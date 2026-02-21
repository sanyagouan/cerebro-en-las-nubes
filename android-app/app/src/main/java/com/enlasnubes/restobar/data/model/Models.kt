package com.enlasnubes.restobar.data.model

import com.google.gson.annotations.SerializedName
import java.time.LocalDate
import java.time.LocalTime
import java.time.Instant

enum class UserRole {
    @SerializedName("administradora") ADMINISTRADORA,
    @SerializedName("encargada") ENCARGADA,
    @SerializedName("camarero") CAMARERO,
    @SerializedName("cocina") COCINA
}

enum class ReservationStatus {
    @SerializedName("pending") PENDING,
    @SerializedName("confirmed") CONFIRMED,
    @SerializedName("seated") SEATED,
    @SerializedName("paying") PAYING,
    @SerializedName("completed") COMPLETED,
    @SerializedName("cancelled") CANCELLED,
    @SerializedName("no_show") NO_SHOW
}

enum class TableLocation {
    @SerializedName("interior") INTERIOR,
    @SerializedName("terrace") TERRACE
}

enum class TableStatus {
    @SerializedName("free") FREE,
    @SerializedName("occupied") OCCUPIED,
    @SerializedName("reserved") RESERVED,
    @SerializedName("maintenance") MAINTENANCE
}

data class User(
    val id: String,
    val usuario: String,
    val nombre: String,
    val rol: String,
    val telefono: String? = null,
    val activo: Boolean = true
)

data class Reservation(
    val id: String,
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("customer_phone") val phone: String,
    val date: LocalDate,
    val time: LocalTime,
    val pax: Int,
    val status: ReservationStatus,
    @SerializedName("table_id") val tableId: String? = null,
    @SerializedName("table_name") val tableName: String? = null,
    val location: TableLocation? = null,
    val notes: String? = null,
    @SerializedName("special_requests") val specialRequests: List<String> = emptyList(),
    @SerializedName("created_at") val createdAt: Instant,
    @SerializedName("updated_at") val updatedAt: Instant? = null
)

data class Table(
    val id: String,
    val number: String,
    val capacity: Int,
    @SerializedName("max_capacity") val maxCapacity: Int,
    val location: TableLocation,
    val status: TableStatus,
    @SerializedName("is_active") val isActive: Boolean = true,
    @SerializedName("current_reservation") val currentReservation: Reservation? = null
)

data class DashboardStats(
    @SerializedName("total_reservations") val totalReservations: Int,
    val confirmed: Int,
    val pending: Int,
    val seated: Int,
    val cancelled: Int,
    @SerializedName("occupancy_rate") val occupancyRate: Float,
    @SerializedName("pax_total") val paxTotal: Int
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type") val tokenType: String = "bearer",
    val user: User
)

data class LoginRequest(
    val usuario: String,
    val password: String,
    @SerializedName("device_token") val deviceToken: String? = null
)
