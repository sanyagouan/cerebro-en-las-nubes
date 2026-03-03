package com.enlasnubes.restobar.presentation.waitlist

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.model.WaitlistCreateRequest
import com.enlasnubes.restobar.data.model.WaitlistResponse
import com.enlasnubes.restobar.data.repository.RestobarRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

data class WaitlistUiState(
    val entries: List<WaitlistResponse> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class WaitlistViewModel @Inject constructor(
    private val repository: RestobarRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(WaitlistUiState())
    val uiState: StateFlow<WaitlistUiState> = _uiState.asStateFlow()

    init {
        loadWaitlist()
    }

    fun loadWaitlist() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            val result = repository.getWaitlist(fecha = LocalDate.now(), estado = "waiting")
            result.fold(
                onSuccess = { entries ->
                    _uiState.update { it.copy(entries = entries, isLoading = false) }
                },
                onFailure = { err ->
                    _uiState.update { it.copy(isLoading = false, error = err.message) }
                }
            )
        }
    }

    fun addToWaitlist(request: WaitlistCreateRequest) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            val result = repository.createWaitlistEntry(request)
            result.fold(
                onSuccess = {
                    loadWaitlist() // Reload
                },
                onFailure = { err ->
                    _uiState.update { it.copy(isLoading = false, error = err.message) }
                }
            )
        }
    }

    fun notifyEntry(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            val result = repository.notifyWaitlistEntry(id)
            result.fold(
                onSuccess = {
                    loadWaitlist() // Reload
                },
                onFailure = { err ->
                    _uiState.update { it.copy(isLoading = false, error = err.message) }
                }
            )
        }
    }

    fun removeEntry(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            val result = repository.deleteWaitlistEntry(id)
            result.fold(
                onSuccess = {
                    loadWaitlist() // Reload
                },
                onFailure = { err ->
                    _uiState.update { it.copy(isLoading = false, error = err.message) }
                }
            )
        }
    }

    fun dismissError() {
        _uiState.update { it.copy(error = null) }
    }
}
