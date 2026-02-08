package com.enlasnubes.restobar.data.websocket

import com.google.gson.annotations.SerializedName

/**
 * Eventos WebSocket recibidos del servidor
 */
sealed class WebSocketEvent {
    abstract val type: String
    abstract val timestamp: String
}

data class ReservationUpdateEvent(
    @SerializedName("type") override val type: String = "reservation_update",
    @SerializedName("event") val event: String, // created, updated, cancelled, seated
    @SerializedName("data") val data: ReservationEventData,
    @SerializedName("timestamp") override val timestamp: String
) : WebSocketEvent()

data class TableUpdateEvent(
    @SerializedName("type") override val type: String = "table_update",
    @SerializedName("table_id") val tableId: String,
    @SerializedName("status") val status: String, // free, occupied, reserved
    @SerializedName("reservation_id") val reservationId: String?,
    @SerializedName("timestamp") override val timestamp: String
) : WebSocketEvent()

data class ConnectionEvent(
    @SerializedName("type") override val type: String = "connection",
    @SerializedName("status") val status: String,
    @SerializedName("role") val role: String,
    @SerializedName("timestamp") override val timestamp: String
) : WebSocketEvent()

data class PongEvent(
    @SerializedName("type") override val type: String = "pong",
    @SerializedName("timestamp") override val timestamp: String
) : WebSocketEvent()

data class ErrorEvent(
    @SerializedName("type") override val type: String = "error",
    @SerializedName("message") val message: String,
    @SerializedName("timestamp") override val timestamp: String
) : WebSocketEvent()

data class ReservationEventData(
    @SerializedName("id") val id: String,
    @SerializedName("customer_name") val customerName: String?,
    @SerializedName("status") val status: String,
    @SerializedName("pax") val pax: Int?,
    @SerializedName("time") val time: String?,
    @SerializedName("table_id") val tableId: String?,
    @SerializedName("table_name") val tableName: String?,
    @SerializedName("updated_by") val updatedBy: String?
)

/**
 * Mensajes enviados al servidor
 */
sealed class WebSocketMessage {
    abstract val type: String
}

data class PingMessage(
    @SerializedName("type") override val type: String = "ping"
) : WebSocketMessage()

data class SubscribeTableMessage(
    @SerializedName("type") override val type: String = "subscribe_table",
    @SerializedName("table_id") val tableId: String
) : WebSocketMessage()

data class UnsubscribeTableMessage(
    @SerializedName("type") override val type: String = "unsubscribe_table",
    @SerializedName("table_id") val tableId: String
) : WebSocketMessage()

data class StatusUpdateMessage(
    @SerializedName("type") override val type: String = "status_update",
    @SerializedName("entity_type") val entityType: String, // reservation, table
    @SerializedName("entity_id") val entityId: String,
    @SerializedName("status") val status: String,
    @SerializedName("notes") val notes: String? = null
) : WebSocketMessage()
