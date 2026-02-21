package com.enlasnubes.restobar.data.repository

import com.enlasnubes.restobar.data.model.DashboardStats
import com.enlasnubes.restobar.data.model.LoginRequest
import com.enlasnubes.restobar.data.model.LoginResponse
import com.enlasnubes.restobar.data.model.Reservation
import com.enlasnubes.restobar.data.model.Table
import com.enlasnubes.restobar.data.model.User
import com.enlasnubes.restobar.data.remote.ChangeOwnPasswordRequest
import com.enlasnubes.restobar.data.remote.ChangePasswordRequest
import com.enlasnubes.restobar.data.remote.CreateReservationRequest
import com.enlasnubes.restobar.data.remote.CreateUserRequest
import com.enlasnubes.restobar.data.remote.DeviceTokenRequest
import com.enlasnubes.restobar.data.remote.RestobarApi
import com.enlasnubes.restobar.data.remote.UpdateStatusRequest
import com.enlasnubes.restobar.data.remote.UpdateUserRequest
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.LocalDate
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RestobarRepository @Inject constructor(
    private val api: RestobarApi
) {
    // Auth
    suspend fun login(usuario: String, password: String, deviceToken: String?): Result<LoginResponse> {
        return try {
            val response = api.login(LoginRequest(usuario, password, deviceToken))
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Login fallido: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout(): Result<Unit> {
        return try {
            api.logout()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun registerDeviceToken(token: String): Result<Unit> {
        return try {
            api.registerDeviceToken(DeviceTokenRequest(token))
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCurrentUser(): Result<User> {
        return try {
            val response = api.getCurrentUser()
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error al obtener usuario: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun changeOwnPassword(currentPassword: String, newPassword: String): Result<String> {
        return try {
            val response = api.changeOwnPassword(ChangeOwnPasswordRequest(currentPassword, newPassword))
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Contrasena actualizada")
            } else {
                Result.failure(Exception("Error al cambiar contrasena: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Reservations
    suspend fun getReservations(date: LocalDate? = null, status: String? = null): Result<List<Reservation>> {
        return try {
            val response = api.getReservations(date, status)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Failed to get reservations: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getReservation(id: String): Result<Reservation> {
        return try {
            val response = api.getReservation(id)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get reservation: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateReservationStatus(
        reservationId: String,
        status: String,
        notes: String? = null
    ): Result<String> {
        return try {
            val response = api.updateReservationStatus(
                reservationId,
                UpdateStatusRequest(reservationId = reservationId, status = status, notes = notes)
            )
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Updated")
            } else {
                Result.failure(Exception("Failed to update status: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createReservation(request: CreateReservationRequest): Result<String> {
        return try {
            val response = api.createReservation(request)
            if (response.isSuccessful) {
                Result.success(response.body()?.id ?: "")
            } else {
                Result.failure(Exception("Failed to create reservation: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Tables
    suspend fun getTables(location: String? = null): Result<List<Table>> {
        return try {
            val response = api.getTables(location)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Failed to get tables: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateTableStatus(tableId: String, status: String): Result<String> {
        return try {
            val response = api.updateTableStatus(
                tableId,
                UpdateStatusRequest(tableId = tableId, status = status)
            )
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Updated")
            } else {
                Result.failure(Exception("Failed to update table: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Dashboard
    suspend fun getDashboardStats(date: LocalDate? = null): Result<DashboardStats> {
        return try {
            val response = api.getDashboardStats(date)
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to get stats: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Users (Administradora only)
    suspend fun getUsuarios(rol: String? = null, activo: Boolean? = null): Result<List<User>> {
        return try {
            val response = api.getUsers(rol, activo)
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Error al obtener usuarios: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createUsuario(usuario: String, nombre: String, password: String, rol: String, telefono: String?): Result<User> {
        return try {
            val response = api.createUser(CreateUserRequest(usuario, nombre, password, rol, telefono))
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error al crear usuario: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateUsuario(id: String, nombre: String?, telefono: String?, rol: String?): Result<User> {
        return try {
            val response = api.updateUser(id, UpdateUserRequest(nombre, telefono, rol))
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error al actualizar usuario: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun changeUserPassword(id: String, newPassword: String): Result<String> {
        return try {
            val response = api.changeUserPassword(id, ChangePasswordRequest(newPassword))
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Contraseña actualizada")
            } else {
                Result.failure(Exception("Error al cambiar contraseña: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deactivateUser(id: String): Result<String> {
        return try {
            val response = api.deactivateUser(id)
            if (response.isSuccessful) {
                Result.success(response.body()?.message ?: "Usuario desactivado")
            } else {
                Result.failure(Exception("Error al desactivar usuario: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
