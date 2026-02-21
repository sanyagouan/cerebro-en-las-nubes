package com.enlasnubes.restobar.presentation.admin

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.model.User
import com.enlasnubes.restobar.data.repository.RestobarRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

// Data classes for Admin screen
data class PeakHour(val hour: String, val reservations: Int)

data class AdminStats(
    val totalReservations: Int,
    val totalRevenue: Double,
    val occupancyRate: Float,
    val totalCustomers: Int,
    val noShowRate: Float,
    val cancellationRate: Float,
    val averagePartySize: Float,
    val peakHours: List<PeakHour>
)

data class AdminUiState(
    val stats: AdminStats? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

data class UserManagementState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
    val showCreateDialog: Boolean = false,
    val showEditDialog: User? = null,
    val showPasswordDialog: User? = null,
    val showDeleteConfirm: User? = null
)

@HiltViewModel
class AdminViewModel @Inject constructor(
    private val repository: RestobarRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AdminUiState())
    val uiState: StateFlow<AdminUiState> = _uiState.asStateFlow()

    private val _userManagementState = MutableStateFlow(UserManagementState())
    val userManagementState: StateFlow<UserManagementState> = _userManagementState.asStateFlow()

    init {
        loadStats()
    }

    private fun loadStats() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // TODO: Obtener de API cuando esté disponible
            val mockStats = AdminStats(
                totalReservations = 156,
                totalRevenue = 8750.50,
                occupancyRate = 0.78f,
                totalCustomers = 423,
                noShowRate = 0.05f,
                cancellationRate = 0.08f,
                averagePartySize = 4.2f,
                peakHours = listOf(
                    PeakHour("13:00", 25),
                    PeakHour("14:00", 35),
                    PeakHour("15:00", 20),
                    PeakHour("20:00", 30),
                    PeakHour("21:00", 40),
                    PeakHour("22:00", 28)
                )
            )
            
            _uiState.update {
                it.copy(
                    stats = mockStats,
                    isLoading = false
                )
            }
        }
    }

    fun refreshStats() {
        loadStats()
    }

    // ============ GESTIÓN DE USUARIOS ============

    fun refreshUsers() {
        viewModelScope.launch {
            _userManagementState.update { it.copy(isLoading = true, error = null) }
            
            val result = repository.getUsuarios()
            
            result.fold(
                onSuccess = { users ->
                    _userManagementState.update { 
                        it.copy(users = users, isLoading = false) 
                    }
                },
                onFailure = { error ->
                    _userManagementState.update { 
                        it.copy(error = error.message, isLoading = false) 
                    }
                }
            )
        }
    }

    fun showCreateUserDialog() {
        _userManagementState.update { it.copy(showCreateDialog = true) }
    }

    fun hideCreateUserDialog() {
        _userManagementState.update { it.copy(showCreateDialog = false) }
    }

    fun createUser(usuario: String, nombre: String, password: String, rol: String, telefono: String?) {
        viewModelScope.launch {
            _userManagementState.update { it.copy(isLoading = true, error = null) }
            
            val result = repository.createUsuario(usuario, nombre, password, rol, telefono)
            
            result.fold(
                onSuccess = { newUser ->
                    _userManagementState.update { 
                        it.copy(
                            users = it.users + newUser,
                            showCreateDialog = false,
                            isLoading = false,
                            successMessage = "Usuario creado correctamente"
                        ) 
                    }
                },
                onFailure = { error ->
                    _userManagementState.update { 
                        it.copy(error = error.message, isLoading = false) 
                    }
                }
            )
        }
    }

    fun showEditUserDialog(user: User) {
        _userManagementState.update { it.copy(showEditDialog = user) }
    }

    fun hideEditUserDialog() {
        _userManagementState.update { it.copy(showEditDialog = null) }
    }

    fun updateUser(id: String, nombre: String, telefono: String?, rol: String) {
        viewModelScope.launch {
            _userManagementState.update { it.copy(isLoading = true, error = null) }
            
            val result = repository.updateUsuario(id, nombre, telefono, rol)
            
            result.fold(
                onSuccess = { updatedUser ->
                    _userManagementState.update { state ->
                        state.copy(
                            users = state.users.map { if (it.id == id) updatedUser else it },
                            showEditDialog = null,
                            isLoading = false,
                            successMessage = "Usuario actualizado correctamente"
                        )
                    }
                },
                onFailure = { error ->
                    _userManagementState.update { 
                        it.copy(error = error.message, isLoading = false) 
                    }
                }
            )
        }
    }

    fun showPasswordDialog(user: User) {
        _userManagementState.update { it.copy(showPasswordDialog = user) }
    }

    fun hidePasswordDialog() {
        _userManagementState.update { it.copy(showPasswordDialog = null) }
    }

    fun changeUserPassword(id: String, newPassword: String) {
        viewModelScope.launch {
            _userManagementState.update { it.copy(isLoading = true, error = null) }
            
            val result = repository.changeUserPassword(id, newPassword)
            
            result.fold(
                onSuccess = {
                    _userManagementState.update { 
                        it.copy(
                            showPasswordDialog = null,
                            isLoading = false,
                            successMessage = "Contraseña actualizada correctamente"
                        ) 
                    }
                },
                onFailure = { error ->
                    _userManagementState.update { 
                        it.copy(error = error.message, isLoading = false) 
                    }
                }
            )
        }
    }

    fun showDeleteConfirm(user: User) {
        _userManagementState.update { it.copy(showDeleteConfirm = user) }
    }

    fun hideDeleteConfirm() {
        _userManagementState.update { it.copy(showDeleteConfirm = null) }
    }

    fun deactivateUser(id: String) {
        viewModelScope.launch {
            _userManagementState.update { it.copy(isLoading = true, error = null) }
            
            val result = repository.deactivateUser(id)
            
            result.fold(
                onSuccess = {
                    _userManagementState.update { state ->
                        state.copy(
                            users = state.users.map { 
                                if (it.id == id) it.copy(activo = false) else it 
                            },
                            showDeleteConfirm = null,
                            isLoading = false,
                            successMessage = "Usuario desactivado correctamente"
                        )
                    }
                },
                onFailure = { error ->
                    _userManagementState.update { 
                        it.copy(error = error.message, isLoading = false) 
                    }
                }
            )
        }
    }

    fun clearSuccessMessage() {
        _userManagementState.update { it.copy(successMessage = null) }
    }

    fun clearError() {
        _userManagementState.update { it.copy(error = null) }
    }
}
