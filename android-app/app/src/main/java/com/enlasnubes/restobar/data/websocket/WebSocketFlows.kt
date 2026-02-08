package com.enlasnubes.restobar.data.websocket

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach

/**
 * Estado de conexión WebSocket como Flow
 */
sealed class WebSocketConnectionState {
    data object Disconnected : WebSocketConnectionState()
    data object Connecting : WebSocketConnectionState()
    data object Connected : WebSocketConnectionState()
    data class Error(val throwable: Throwable?) : WebSocketConnectionState()
}

/**
 * Wrapper tipado para eventos WebSocket como Flow
 */
class WebSocketEventFlow {
    private val _events = MutableSharedFlow<WebSocketEvent>()
    val events: Flow<WebSocketEvent> = _events.asSharedFlow()
    
    // Flujos específicos por tipo de evento
    val reservationUpdates: Flow<ReservationUpdateEvent> = events.filterIsInstance()
    val tableUpdates: Flow<TableUpdateEvent> = events.filterIsInstance()
    val connectionEvents: Flow<ConnectionEvent> = events.filterIsInstance()
    val errors: Flow<ErrorEvent> = events.filterIsInstance()
    
    // Flujo de reservas creadas
    val reservationsCreated = reservationUpdates
        .filter { it.event == "created" }
        .map { it.data }
    
    // Flujo de reservas actualizadas
    val reservationsUpdated = reservationUpdates
        .filter { it.event in listOf("updated", "seated", "cancelled", "completed") }
        .map { it.data }
    
    suspend fun emit(event: WebSocketEvent) {
        _events.emit(event)
    }
}

/**
 * Estado del repositorio de WebSocket con Flow
 */
data class WebSocketRepositoryState(
    val isConnected: Boolean = false,
    val isConnecting: Boolean = false,
    val lastError: String? = null,
    val reconnectAttempts: Int = 0
)

/**
 * Actions que pueden ser enviadas al WebSocket
 */
sealed class WebSocketAction {
    data class SubscribeTable(val tableId: String) : WebSocketAction()
    data class UnsubscribeTable(val tableId: String) : WebSocketAction()
    data class UpdateReservationStatus(
        val reservationId: String,
        val status: String,
        val notes: String? = null
    ) : WebSocketAction()
    data class UpdateTableStatus(
        val tableId: String,
        val status: String
    ) : WebSocketAction()
    data object Ping : WebSocketAction()
}
