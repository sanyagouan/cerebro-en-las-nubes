package com.enlasnubes.restobar.data.remote

import com.enlasnubes.restobar.data.model.DashboardStats
import com.enlasnubes.restobar.data.model.LoginRequest
import com.enlasnubes.restobar.data.model.LoginResponse
import com.enlasnubes.restobar.data.model.Reservation
import com.enlasnubes.restobar.data.model.Table
import com.enlasnubes.restobar.data.model.User
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query
import java.time.LocalDate

interface RestobarApi {

    // Auth
    @POST("api/mobile/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("api/mobile/auth/logout")
    suspend fun logout(): Response<Unit>

    @POST("api/mobile/auth/refresh")
    suspend fun refreshToken(@Body request: RefreshRequest): Response<TokenResponse>
    
    @GET("api/mobile/auth/yo")
    suspend fun getCurrentUser(): Response<User>

    @PUT("api/mobile/auth/password")
    suspend fun changeOwnPassword(@Body request: ChangeOwnPasswordRequest): Response<MessageResponse>

    // Reservations
    @GET("api/mobile/reservations")
    suspend fun getReservations(
        @Query("date") date: LocalDate? = null,
        @Query("status") status: String? = null
    ): Response<List<Reservation>>

    @GET("api/mobile/reservations/{id}")
    suspend fun getReservation(@Path("id") id: String): Response<Reservation>

    @PUT("api/mobile/reservations/{id}/status")
    suspend fun updateReservationStatus(
        @Path("id") id: String,
        @Body request: UpdateStatusRequest
    ): Response<StatusUpdateResponse>

    @POST("api/mobile/reservations")
    suspend fun createReservation(@Body reservation: CreateReservationRequest): Response<CreateResponse>

    // Tables
    @GET("api/mobile/tables")
    suspend fun getTables(
        @Query("location") location: String? = null
    ): Response<List<Table>>

    @GET("api/mobile/tables/{id}")
    suspend fun getTable(@Path("id") id: String): Response<Table>

    @PUT("api/mobile/tables/{id}/status")
    suspend fun updateTableStatus(
        @Path("id") id: String,
        @Body request: UpdateStatusRequest
    ): Response<StatusUpdateResponse>

    // Dashboard
    @GET("api/mobile/dashboard/stats")
    suspend fun getDashboardStats(
        @Query("date") date: LocalDate? = null
    ): Response<DashboardStats>

    // Push Notifications
    @POST("api/mobile/notifications/register")
    suspend fun registerDeviceToken(@Body request: DeviceTokenRequest): Response<Unit>

    // Users (Administradora only)
    @GET("api/mobile/usuarios")
    suspend fun getUsers(
        @Query("rol") rol: String? = null,
        @Query("activo") activo: Boolean? = null
    ): Response<List<User>>

    @GET("api/mobile/usuarios/{id}")
    suspend fun getUser(@Path("id") id: String): Response<User>

    @POST("api/mobile/usuarios")
    suspend fun createUser(@Body request: CreateUserRequest): Response<User>

    @PUT("api/mobile/usuarios/{id}")
    suspend fun updateUser(
        @Path("id") id: String,
        @Body request: UpdateUserRequest
    ): Response<User>

    @PUT("api/mobile/usuarios/{id}/password")
    suspend fun changeUserPassword(
        @Path("id") id: String,
        @Body request: ChangePasswordRequest
    ): Response<MessageResponse>

    @DELETE("api/mobile/usuarios/{id}")
    suspend fun deactivateUser(@Path("id") id: String): Response<MessageResponse>
}

data class RefreshRequest(
    val refreshToken: String
)

data class TokenResponse(
    val accessToken: String,
    val tokenType: String
)

data class UpdateStatusRequest(
    val reservationId: String? = null,
    val tableId: String? = null,
    val status: String,
    val notes: String? = null
)

data class StatusUpdateResponse(
    val message: String,
    val reservationId: String? = null,
    val tableId: String? = null,
    val status: String
)

data class CreateReservationRequest(
    val customerName: String,
    val phone: String,
    val date: LocalDate,
    val time: String,
    val pax: Int,
    val tableId: String? = null,
    val notes: String? = null
)

data class CreateResponse(
    val message: String,
    val id: String
)

data class DeviceTokenRequest(
    val deviceToken: String
)

data class CreateUserRequest(
    val usuario: String,
    val nombre: String,
    val password: String,
    val rol: String,
    val telefono: String? = null
)

data class UpdateUserRequest(
    val nombre: String? = null,
    val telefono: String? = null,
    val rol: String? = null
)

data class ChangePasswordRequest(
    val newPassword: String
)

data class ChangeOwnPasswordRequest(
    val currentPassword: String,
    val newPassword: String
)

data class MessageResponse(
    val message: String
)
