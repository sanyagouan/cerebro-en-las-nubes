package com.enlasnubes.restobar.presentation.admin

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AdminUiState(
    val stats: AdminStats? = null,
    val users: List<UserManagement> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val showAddUserDialog: Boolean = false,
    val selectedUser: UserManagement? = null
)

@HiltViewModel
class AdminViewModel @Inject constructor(
    // private val repository: AdminRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AdminUiState())
    val uiState: StateFlow<AdminUiState> = _uiState.asStateFlow()

    init {
        loadStats()
        loadUsers()
    }

    private fun loadStats() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // TODO: Obtener de API
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

    private fun loadUsers() {
        viewModelScope.launch {
            // TODO: Obtener de API
            val mockUsers = listOf(
                UserManagement(
                    id = "1",
                    email = "camarero1@enlasnubes.com",
                    name = "Juan Pérez",
                    role = com.enlasnubes.restobar.data.model.UserRole.WAITER,
                    isActive = true
                ),
                UserManagement(
                    id = "2",
                    email = "cocinero@enlasnubes.com",
                    name = "María García",
                    role = com.enlasnubes.restobar.data.model.UserRole.COOK,
                    isActive = true
                ),
                UserManagement(
                    id = "3",
                    email = "encargada@enlasnubes.com",
                    name = "Ana López",
                    role = com.enlasnubes.restobar.data.model.UserRole.MANAGER,
                    isActive = true
                ),
                UserManagement(
                    id = "4",
                    email = "admin@enlasnubes.com",
                    name = "Carlos Ruiz",
                    role = com.enlasnubes.restobar.data.model.UserRole.ADMIN,
                    isActive = true
                )
            )
            
            _uiState.update { it.copy(users = mockUsers) }
        }
    }

    fun showAddUserDialog() {
        _uiState.update { it.copy(showAddUserDialog = true) }
    }

    fun hideAddUserDialog() {
        _uiState.update { it.copy(showAddUserDialog = false) }
    }

    fun editUser(user: UserManagement) {
        _uiState.update { it.copy(selectedUser = user) }
    }

    fun deleteUser(user: UserManagement) {
        viewModelScope.launch {
            // TODO: Llamar a API para eliminar
            _uiState.update { state ->
                state.copy(users = state.users.filter { it.id != user.id })
            }
        }
    }

    fun addUser(name: String, email: String, role: com.enlasnubes.restobar.data.model.UserRole) {
        viewModelScope.launch {
            // TODO: Llamar a API para crear
            val newUser = UserManagement(
                id = System.currentTimeMillis().toString(),
                email = email,
                name = name,
                role = role,
                isActive = true
            )
            _uiState.update { state ->
                state.copy(
                    users = state.users + newUser,
                    showAddUserDialog = false
                )
            }
        }
    }

    fun updateUser(user: UserManagement) {
        viewModelScope.launch {
            // TODO: Llamar a API para actualizar
            _uiState.update { state ->
                state.copy(
                    users = state.users.map { 
                        if (it.id == user.id) user else it 
                    },
                    selectedUser = null
                )
            }
        }
    }

    fun refreshStats() {
        loadStats()
    }
}
