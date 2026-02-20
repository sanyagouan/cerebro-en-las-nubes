package com.enlasnubes.restobar.data.websocket

import android.util.Log
import com.enlasnubes.restobar.BuildConfig
import com.google.gson.Gson
import dagger.hilt.android.scopes.ActivityRetainedScoped
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit
import javax.inject.Inject

/**
 * Implementación de WebSocketService usando OkHttp nativo
 */
@ActivityRetainedScoped
class WebSocketManager @Inject constructor() : WebSocketService {

    companion object {
        private const val TAG = "WebSocketManager"
        private const val RECONNECT_DELAY = 5000L
        private const val MAX_RECONNECT_ATTEMPTS = 10
        private const val WS_BASE_URL = BuildConfig.WS_BASE_URL
    }

    private val serviceScope = CoroutineScope(Dispatchers.IO + Job())
    private val gson = Gson()

    private var webSocket: WebSocket? = null
    private var okHttpClient: OkHttpClient? = null
    private var reconnectAttempts = 0

    private val _connectionState = MutableStateFlow<WebSocketService.ConnectionState>(
        WebSocketService.ConnectionState.DISCONNECTED
    )
    override val connectionState: StateFlow<WebSocketService.ConnectionState> = _connectionState.asStateFlow()

    private val _reservationUpdatesFlow = MutableSharedFlow<ReservationUpdateEvent>()
    override val reservationUpdates: Flow<ReservationUpdateEvent> = _reservationUpdatesFlow

    init {
        okHttpClient = OkHttpClient.Builder()
            .pingInterval(30, TimeUnit.SECONDS)
            .build()
    }

    override fun connect(token: String) {
        if (_connectionState.value == WebSocketService.ConnectionState.CONNECTED ||
            _connectionState.value == WebSocketService.ConnectionState.CONNECTING) {
            return
        }

        _connectionState.value = WebSocketService.ConnectionState.CONNECTING
        val wsUrl = buildWsUrl(token)
        val request = Request.Builder().url(wsUrl).build()

        webSocket = okHttpClient?.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _connectionState.value = WebSocketService.ConnectionState.CONNECTED
                reconnectAttempts = 0
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(text)
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _connectionState.value = WebSocketService.ConnectionState.DISCONNECTED
                scheduleReconnect()
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = WebSocketService.ConnectionState.ERROR
                scheduleReconnect()
            }
        })
    }

    private fun buildWsUrl(token: String): String {
        return "${WS_BASE_URL.replace("https://", "wss://").replace("http://", "ws://")}/ws/reservations?token=$token"
    }

    override fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        webSocket = null
        _connectionState.value = WebSocketService.ConnectionState.DISCONNECTED
    }

    override fun markReservationSeated(reservationId: String, notes: String?) {
        sendMessage(StatusUpdateMessage("reservation", reservationId, "seated", notes))
    }

    override fun markReservationCancelled(reservationId: String, reason: String?) {
        sendMessage(StatusUpdateMessage("reservation", reservationId, "cancelled", reason))
    }

    override fun sendMessage(message: WebSocketMessage) {
        if (_connectionState.value != WebSocketService.ConnectionState.CONNECTED) return
        val json = when (message) {
            is PingMessage -> "{\"type\":\"ping\"}"
            is StatusUpdateMessage -> {
                val notes = message.notes?.let { ",\"notes\":\"$it\"" } ?: ""
                "{\"type\":\"status_update\",\"entity_type\":\"${message.entityType}\",\"entity_id\":\"${message.entityId}\",\"status\":\"${message.status}\"$notes}"
            }
            else -> gson.toJson(message)
        }
        webSocket?.send(json)
    }

    private fun handleMessage(text: String) {
        try {
            val map = gson.fromJson(text, Map::class.java)
            when (map["type"]) {
                "reservation_update" -> {
                    val event = gson.fromJson(text, ReservationUpdateEvent::class.java)
                    serviceScope.launch { _reservationUpdatesFlow.emit(event) }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Parse error", e)
        }
    }

    private fun scheduleReconnect() {
        if (reconnectAttempts++ >= MAX_RECONNECT_ATTEMPTS) return
        serviceScope.launch {
            delay(RECONNECT_DELAY * reconnectAttempts)
        }
    }
}
