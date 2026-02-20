package com.enlasnubes.restobar.data.websocket

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/**
 * Interfaz del servicio WebSocket para inyección de dependencias
 */
interface WebSocketService {
    val connectionState: StateFlow<ConnectionState>
    val reservationUpdates: Flow<ReservationUpdateEvent>
    
    fun connect(token: String)
    fun disconnect()
    fun markReservationSeated(reservationId: String, notes: String? = null)
    fun markReservationCancelled(reservationId: String, reason: String? = null)
    fun sendMessage(message: WebSocketMessage)
    
    enum class ConnectionState {
        CONNECTED,
        CONNECTING,
        DISCONNECTED,
        ERROR
    }
}
