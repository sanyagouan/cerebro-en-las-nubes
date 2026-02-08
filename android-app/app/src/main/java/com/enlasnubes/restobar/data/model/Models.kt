package com.enlasnubes.restobar.data.model

import java.time.LocalDate
import java.time.LocalTime
import java.time.Instant

enum class UserRole {
    WAITER,      // Camarero
    COOK,        // Cocinero
    MANAGER,     // Encargada
    ADMIN        // Administrador
}

enum class ReservationStatus {
    PENDING,     // Pendiente
    CONFIRMED,   // Confirmada
    SEATED,      // Sentado
    PAYING,      // Pagando
    COMPLETED,   // Completada
    CANCELLED,   // Cancelada
    NO_SHOW      // No apareció
}

enum class TableLocation {
    INTERIOR,    // Interior
    TERRACE      // Terraza
}

enum class TableStatus {
    FREE,        // Libre
    OCCUPIED,    // Ocupada
    RESERVED,    // Reservada
    MAINTENANCE  // Mantenimiento
}

data class User(
    val id: String,
    val email: String,
    val name: String,
    val role: UserRole,
    val isActive: Boolean = true
)

data class Reservation(
    val id: String,
    val customerName: String,
    val phone: String,
    val date: LocalDate,
    val time: LocalTime,
    val pax: Int,
    val status: ReservationStatus,
    val tableId: String? = null,
    val tableName: String? = null,
    val location: TableLocation? = null,
    val notes: String? = null,
    val specialRequests: List<String> = emptyList(),
    val createdAt: Instant,
    val updatedAt: Instant? = null
)

data class Table(
    val id: String,
    val name: String,
    val capacity: Int,
    val maxCapacity: Int,
    val location: TableLocation,
    val status: TableStatus,
    val isActive: Boolean = true,
    val currentReservation: Reservation? = null
)

data class DashboardStats(
    val totalReservations: Int,
    val confirmed: Int,
    val pending: Int,
    val seated: Int,
    val cancelled: Int,
    val occupancyRate: Float,
    val paxTotal: Int
)

data class LoginResponse(
    val accessToken: String,
    val refreshToken: String,
    val user: User
)
