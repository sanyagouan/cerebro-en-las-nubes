package com.enlasnubes.restobar.data.websocket

import android.util.Log
import com.enlasnubes.restobar.BuildConfig
import com.enlasnubes.restobar.data.repository.AuthRepository
import com.tinder.scarlet.Event
import com.tinder.scarlet.Scarlet
import com.tinder.scarlet.WebSocket
import com.tinder.scarlet.messageadapter.gson.GsonMessageAdapter
import com.tinder.scarlet.retry.ExponentialBackoffStrategy
import com.tinder.scarlet.streamadapter.rxjava2.RxJava2StreamAdapterFactory
import com.tinder.scarlet.websocket.okhttp.OkHttpWebSocket
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import javax.inject.Inject
import javax.inject.Singleton

/**
 * WebSocket Manager con Flow reactivo
 * Maneja conexión, reconexión automática y eventos tipados
 */
@Singleton
class WebSocketManager @Inject constructor(
    private val authRepository: AuthRepository
) {
    companion object {
        private const val TAG = "WebSocketManager"
        private const val WS_BASE_URL = BuildConfig.WS_BASE_URL
        private const val RECONNECT_DELAY = 5000L
        private const val PING_INTERVAL = 30000L
        private const val MAX_RECONNECT_ATTEMPTS = 10
    }

    private val serviceScope = CoroutineScope(Dispatchers.IO + Job())
    private val refLock = Mutex()
    private var refCount = 0
    private var reconnectAttempts = 0
    
    private var scarlet: Scarlet? = null
    private var webSocket: WebSocket? = null
    private var pingJob: Job? = null
    
    // Flows públicos
    private val _connectionState = MutableStateFlow<WebSocketConnectionState>(
        WebSocketConnectionState.Disconnected
    )
    val connectionState: StateFlow<WebSocketConnectionState> = _connectionState.asStateFlow()
    
    val eventFlow = WebSocketEventFlow()
    
    // Estado del repositorio
    private val _repositoryState = MutableStateFlow(WebSocketRepositoryState())
    val repositoryState: StateFlow<WebSocketRepositoryState> = _repositoryState.asStateFlow()

    /**
     * Conecta al WebSocket usando Flow
     */
    fun connect(): Flow<WebSocketConnectionState> = flow {
        refLock.withLock {
            refCount++
            Log.d(TAG, "Connect requested, refCount: $refCount")
        }
        
        // Si ya está conectado, emitir estado actual
        if (_connectionState.value is WebSocketConnectionState.Connected) {
            emit(_connectionState.value)
            return@flow
        }
        
        emit(WebSocketConnectionState.Connecting)
        _connectionState.value = WebSocketConnectionState.Connecting
        _repositoryState.value = _repositoryState.value.copy(isConnecting = true)
        
        try {
            val token = authRepository.getAccessToken()
            if (token.isNullOrBlank()) {
                throw IllegalStateException("No auth token available")
            }
            
            val okHttpClient = createOkHttpClient()
            val wsUrl = "$WS_BASE_URL/reservations?token=$token"
            
            scarlet = Scarlet.Builder()
                .webSocketFactory(OkHttpWebSocket.Factory(okHttpClient))
                .addMessageAdapterFactory(GsonMessageAdapter.Factory())
                .addStreamAdapterFactory(RxJava2StreamAdapterFactory())
                .backoffStrategy(ExponentialBackoffStrategy(RECONNECT_DELAY, 60000L))
                .build()
            
            webSocket = scarlet!!.create(WebSocket::class.java, wsUrl)
            
            // Observar eventos de conexión
            observeConnectionEvents()
            
            // Observar mensajes
            observeMessages()
            
            // Iniciar ping
            startPingJob()
            
            emit(WebSocketConnectionState.Connected)
            _connectionState.value = WebSocketConnectionState.Connected
            _repositoryState.value = _repositoryState.value.copy(
                isConnected = true,
                isConnecting = false,
                reconnectAttempts = 0
            )
            reconnectAttempts = 0
            
        } catch (e: Exception) {
            Log.e(TAG, "Connection failed", e)
            emit(WebSocketConnectionState.Error(e))
            _connectionState.value = WebSocketConnectionState.Error(e)
            _repositoryState.value = _repositoryState.value.copy(
                isConnecting = false,
                lastError = e.message
            )
            scheduleReconnect()
        }
    }.catch { e ->
        Log.e(TAG, "Flow error", e)
        emit(WebSocketConnectionState.Error(e))
    }

    /**
     * Desconecta con manejo de referencias
     */
    suspend fun disconnect() {
        val shouldDisconnect = refLock.withLock {
            refCount--
            Log.d(TAG, "Disconnect requested, refCount: $refCount")
            refCount <= 0
        }
        
        if (shouldDisconnect) {
            performDisconnect()
        }
    }

    /**
     * Ejecuta una acción en el WebSocket
     */
    fun sendAction(action: WebSocketAction) {
        if (_connectionState.value !is WebSocketConnectionState.Connected) {
            Log.w(TAG, "Cannot send action, not connected: $action")
            return
        }
        
        val message = when (action) {
            is WebSocketAction.SubscribeTable -> 
                SubscribeTableMessage(tableId = action.tableId)
            is WebSocketAction.UnsubscribeTable -> 
                UnsubscribeTableMessage(tableId = action.tableId)
            is WebSocketAction.UpdateReservationStatus -> 
                StatusUpdateMessage(
                    entityType = "reservation",
                    entityId = action.reservationId,
                    status = action.status,
                    notes = action.notes
                )
            is WebSocketAction.UpdateTableStatus -> 
                StatusUpdateMessage(
                    entityType = "table",
                    entityId = action.tableId,
                    status = action.status
                )
            is WebSocketAction.Ping -> PingMessage()
        }
        
        sendMessage(message)
    }

    // Métodos de conveniencia
    fun markReservationSeated(reservationId: String, notes: String? = null) {
        sendAction(WebSocketAction.UpdateReservationStatus(reservationId, "seated", notes))
    }

    fun markReservationCancelled(reservationId: String, reason: String? = null) {
        sendAction(WebSocketAction.UpdateReservationStatus(reservationId, "cancelled", reason))
    }

    fun markTableFree(tableId: String) {
        sendAction(WebSocketAction.UpdateTableStatus(tableId, "free"))
    }

    private fun observeConnectionEvents() {
        webSocket?.observeEvent()
            ?.onEach { event ->
                when (event) {
                    is Event.OnConnectionOpened -> {
                        Log.d(TAG, "WebSocket opened")
                        _connectionState.value = WebSocketConnectionState.Connected
                        _repositoryState.value = _repositoryState.value.copy(
                            isConnected = true,
                            isConnecting = false
                        )
                    }
                    is Event.OnConnectionClosed -> {
                        Log.d(TAG, "WebSocket closed")
                        _connectionState.value = WebSocketConnectionState.Disconnected
                        _repositoryState.value = _repositoryState.value.copy(isConnected = false)
                        scheduleReconnect()
                    }
                    is Event.OnConnectionFailed -> {
                        Log.e(TAG, "WebSocket failed", event.throwable)
                        _connectionState.value = WebSocketConnectionState.Error(event.throwable)
                        _repositoryState.value = _repositoryState.value.copy(
                            isConnected = false,
                            lastError = event.throwable?.message
                        )
                        scheduleReconnect()
                    }
                    else -> {}
                }
            }
            ?.launchIn(serviceScope)
    }

    private fun observeMessages() {
        webSocket?.observeText()
            ?.onEach { message ->
                try {
                    val event = parseEvent(message)
                    eventFlow.emit(event)
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing message: $message", e)
                }
            }
            ?.launchIn(serviceScope)
    }

    private fun sendMessage(message: WebSocketMessage) {
        try {
            val json = when (message) {
                is PingMessage -> "{\"type\":\"ping\"}"
                is SubscribeTableMessage -> "{\"type\":\"subscribe_table\",\"table_id\":\"${message.tableId}\"}"
                is UnsubscribeTableMessage -> "{\"type\":\"unsubscribe_table\",\"table_id\":\"${message.tableId}\"}"
                is StatusUpdateMessage -> buildStatusUpdateJson(message)
            }
            webSocket?.send(json)
            Log.d(TAG, "Sent: ${message.type}")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending message", e)
        }
    }

    private fun buildStatusUpdateJson(message: StatusUpdateMessage): String {
        return """{"type":"status_update","entity_type":"${message.entityType}","entity_id":"${message.entityId}","status":"${message.status}"${message.notes?.let { ",\"notes\":\"$it\"" } ?: ""}}"""
    }

    private fun parseEvent(json: String): WebSocketEvent {
        return when {
            json.contains("\"type\":\"reservation_update\"") -> 
                com.google.gson.Gson().fromJson(json, ReservationUpdateEvent::class.java)
            json.contains("\"type\":\"table_update\"") -> 
                com.google.gson.Gson().fromJson(json, TableUpdateEvent::class.java)
            json.contains("\"type\":\"connection\"") -> 
                com.google.gson.Gson().fromJson(json, ConnectionEvent::class.java)
            json.contains("\"type\":\"pong\"") -> 
                com.google.gson.Gson().fromJson(json, PongEvent::class.java)
            json.contains("\"type\":\"error\"") -> 
                com.google.gson.Gson().fromJson(json, ErrorEvent::class.java)
            else -> throw IllegalArgumentException("Unknown event type in: $json")
        }
    }

    private fun startPingJob() {
        pingJob?.cancel()
        pingJob = serviceScope.launch {
            while (true) {
                delay(PING_INTERVAL)
                if (_connectionState.value is WebSocketConnectionState.Connected) {
                    sendAction(WebSocketAction.Ping)
                }
            }
        }
    }

    private fun scheduleReconnect() {
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            Log.e(TAG, "Max reconnect attempts reached")
            return
        }
        
        reconnectAttempts++
        _repositoryState.value = _repositoryState.value.copy(reconnectAttempts = reconnectAttempts)
        
        serviceScope.launch {
            delay(RECONNECT_DELAY * reconnectAttempts)
            if (_connectionState.value !is WebSocketConnectionState.Connected) {
                Log.d(TAG, "Attempting reconnect #$reconnectAttempts")
                connect().launchIn(serviceScope)
            }
        }
    }

    private fun performDisconnect() {
        pingJob?.cancel()
        pingJob = null
        scarlet = null
        webSocket = null
        _connectionState.value = WebSocketConnectionState.Disconnected
        _repositoryState.value = WebSocketRepositoryState()
        Log.d(TAG, "WebSocket fully disconnected")
    }

    private fun createOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BASIC
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            })
            .build()
    }
}
