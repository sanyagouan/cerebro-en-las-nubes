package com.enlasnubes.restobar.presentation.reservations

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.model.Reservation
import com.enlasnubes.restobar.data.model.ReservationStatus
import com.enlasnubes.restobar.data.model.UserRole
import com.enlasnubes.restobar.data.repository.AuthRepository
import com.enlasnubes.restobar.data.repository.RestobarRepository
import com.enlasnubes.restobar.data.websocket.ReservationUpdateEvent
import com.enlasnubes.restobar.data.websocket.WebSocketService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

data class ReservationsUiState(
    val reservations: List<Reservation> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null,
    val selectedFilter: ReservationFilter = ReservationFilter.ALL,
    val connectionStatus: ConnectionStatus = ConnectionStatus.DISCONNECTED
)

enum class ReservationFilter {
    ALL, PENDING, CONFIRMED, SEATED, COMPLETED, CANCELLED
}

enum class ConnectionStatus {
    CONNECTED, DISCONNECTED, CONNECTING, ERROR
}

@HiltViewModel
class ReservationsViewModel @Inject constructor(
    private val repository: RestobarRepository,
    private val webSocketService: WebSocketService,
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ReservationsUiState())
    val uiState: StateFlow<ReservationsUiState> = _uiState.asStateFlow()

    init {
        // Escuchar eventos de conexión WebSocket
        viewModelScope.launch {
            webSocketService.connectionState.collect { state ->
                val connectionStatus = when (state) {
                    WebSocketService.ConnectionState.CONNECTED -> ConnectionStatus.CONNECTED
                    WebSocketService.ConnectionState.CONNECTING -> ConnectionStatus.CONNECTING
                    WebSocketService.ConnectionState.DISCONNECTED -> ConnectionStatus.DISCONNECTED
                    WebSocketService.ConnectionState.ERROR -> ConnectionStatus.ERROR
                }
                _uiState.update { it.copy(connectionStatus = connectionStatus) }
            }
        }

        // Escuchar actualizaciones de reservas vía WebSocket
        viewModelScope.launch {
            webSocketService.reservationUpdates.collect { event ->
                handleReservationUpdate(event)
            }
        }

        // Conectar WebSocket
        viewModelScope.launch {
            authRepository.authToken.collect { token ->
                if (!token.isNullOrBlank()) {
                    webSocketService.connect(token)
                }
            }
        }
    }

    fun loadReservations(date: LocalDate = LocalDate.now()) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            repository.getReservations(date = date)
                .onSuccess { reservations ->
                    _uiState.update {
                        it.copy(
                            reservations = reservations.sortedBy { r -> r.time },
                            isLoading = false
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = error.message
                        )
                    }
                }
        }
    }

    fun refreshReservations() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            loadReservations()
            _uiState.update { it.copy(isRefreshing = false) }
        }
    }

    fun setFilter(filter: ReservationFilter) {
        _uiState.update { it.copy(selectedFilter = filter) }
    }

    fun getFilteredReservations(): List<Reservation> {
        val filter = _uiState.value.selectedFilter
        return if (filter == ReservationFilter.ALL) {
            _uiState.value.reservations
        } else {
            _uiState.value.reservations.filter { 
                it.status.name == filter.name 
            }
        }
    }

    fun updateStatus(reservationId: String, newStatus: ReservationStatus, notes: String? = null) {
        viewModelScope.launch {
            // Optimistic update
            updateLocalReservation(reservationId, newStatus)

            // Enviar vía WebSocket para tiempo real
            when (newStatus) {
                ReservationStatus.SEATED -> webSocketService.markReservationSeated(reservationId, notes)
                ReservationStatus.CANCELLED -> webSocketService.markReservationCancelled(reservationId, notes)
                ReservationStatus.COMPLETED -> webSocketService.sendMessage(
                    com.enlasnubes.restobar.data.websocket.StatusUpdateMessage(
                        entityType = "reservation",
                        entityId = reservationId,
                        status = "completed",
                        notes = notes
                    )
                )
                else -> {}
            }

            // También enviar vía HTTP como backup
            repository.updateReservationStatus(reservationId, newStatus.name.lowercase())
                .onFailure { error ->
                    Log.e("ReservationsViewModel", "Error updating status", error)
                    // Revert optimistic update on failure
                    loadReservations()
                }
        }
    }

    private fun handleReservationUpdate(event: ReservationUpdateEvent) {
        when (event.event) {
            "created" -> {
                // Agregar nueva reserva
                loadReservations() // Recargar para obtener datos completos
            }
            "updated", "seated", "cancelled", "completed" -> {
                // Actualizar reserva existente
                event.data.id.let { id ->
                    val status = try {
                        ReservationStatus.valueOf(event.data.status.uppercase())
                    } catch (e: IllegalArgumentException) {
                        // Estado desconocido, mantener el actual
                        return@let
                    }
                    updateLocalReservation(id, status)
                }
            }
        }
    }

    private fun updateLocalReservation(id: String, newStatus: ReservationStatus) {
        _uiState.update { state ->
            state.copy(
                reservations = state.reservations.map { reservation ->
                    if (reservation.id == id) {
                        reservation.copy(status = newStatus)
                    } else {
                        reservation
                    }
                }
            )
        }
    }

    fun dismissError() {
        _uiState.update { it.copy(error = null) }
    }
}
