package com.enlasnubes.restobar.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.model.User
import com.enlasnubes.restobar.data.repository.AuthRepository
import com.enlasnubes.restobar.data.repository.RestobarRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProfileUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null
)

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val restobarRepository: RestobarRepository,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Intentar obtener datos del usuario del servidor
            val result = restobarRepository.getCurrentUser()
            
            result.fold(
                onSuccess = { user ->
                    _uiState.update { 
                        it.copy(user = user, isLoading = false) 
                    }
                },
                onFailure = { error ->
                    // Si falla, usar datos del repositorio local
                    val localUser = authRepository.getCurrentUser()
                    _uiState.update { 
                        it.copy(
                            user = localUser,
                            isLoading = false,
                            error = "No se pudo actualizar el perfil: ${error.message}"
                        )
                    }
                }
            )
        }
    }

    fun changePassword(currentPassword: String, newPassword: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, successMessage = null) }
            
            val result = restobarRepository.changeOwnPassword(currentPassword, newPassword)
            
            result.fold(
                onSuccess = {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            successMessage = "Contrasena actualizada correctamente"
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = error.message ?: "Error al cambiar la contrasena"
                        )
                    }
                }
            )
        }
    }

    fun clearMessages() {
        _uiState.update { it.copy(error = null, successMessage = null) }
    }
}
