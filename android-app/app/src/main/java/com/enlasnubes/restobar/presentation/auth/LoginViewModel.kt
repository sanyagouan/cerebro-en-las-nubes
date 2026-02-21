package com.enlasnubes.restobar.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.repository.AuthRepository
import com.enlasnubes.restobar.data.repository.RestobarRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthState(
    val isAuthenticated: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null,
    val userId: String = "",
    val userName: String = "",
    val userUsuario: String = "",
    val userRol: String = ""
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val restobarRepository: RestobarRepository,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _authState = MutableStateFlow(AuthState())
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    init {
        viewModelScope.launch {
            authRepository.currentUser.collect { user ->
                if (user != null) {
                    _authState.update {
                        it.copy(
                            isAuthenticated = true,
                            userId = user.id,
                            userName = user.nombre,
                            userUsuario = user.usuario,
                            userRol = user.rol
                        )
                    }
                }
            }
        }
    }

    fun login(usuario: String, password: String, deviceToken: String? = null) {
        viewModelScope.launch {
            _authState.update { it.copy(isLoading = true, error = null) }

            restobarRepository.login(usuario, password, deviceToken)
                .onSuccess { response ->
                    authRepository.saveAuthData(
                        accessToken = response.accessToken,
                        refreshToken = response.refreshToken,
                        user = response.user
                    )
                    _authState.update {
                        it.copy(
                            isAuthenticated = true,
                            isLoading = false,
                            userId = response.user.id,
                            userName = response.user.nombre,
                            userUsuario = response.user.usuario,
                            userRol = response.user.rol
                        )
                    }
                }
                .onFailure { error ->
                    _authState.update {
                        it.copy(
                            isLoading = false,
                            error = error.message ?: "Error de autenticación"
                        )
                    }
                }
        }
    }

    fun logout() {
        viewModelScope.launch {
            restobarRepository.logout()
            authRepository.clearAuthData()
            _authState.update {
                AuthState() // Reset to default
            }
        }
    }

    fun clearError() {
        _authState.update { it.copy(error = null) }
    }
}
