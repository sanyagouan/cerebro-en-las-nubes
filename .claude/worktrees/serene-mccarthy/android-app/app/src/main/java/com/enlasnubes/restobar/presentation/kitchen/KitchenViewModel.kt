package com.enlasnubes.restobar.presentation.kitchen

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
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
import java.time.LocalTime
import javax.inject.Inject

data class KitchenUiState(
    val orders: List<KitchenOrder> = emptyList(),
    val alerts: List<KitchenAlert> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val showAlertsDialog: Boolean = false
)

@HiltViewModel
class KitchenViewModel @Inject constructor(
    private val repository: RestobarRepository,
    private val webSocketService: WebSocketService
) : ViewModel() {

    private val _uiState = MutableStateFlow(KitchenUiState())
    val uiState: StateFlow<KitchenUiState> = _uiState.asStateFlow()

    init {
        // Escuchar actualizaciones de reservas
        viewModelScope.launch {
            webSocketService.reservationUpdates.collect { event ->
                handleReservationUpdate(event)
            }
        }

        loadOrders()
    }

    private fun loadOrders() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            // Obtener reservas del día y convertir a órdenes de cocina
            repository.getReservations(date = LocalDate.now())
                .onSuccess { reservations ->
                    val orders = reservations
                        .filter { it.status.name == "CONFIRMED" || it.status.name == "SEATED" }
                        .map { reservation ->
                            KitchenOrder(
                                reservationId = reservation.id,
                                tableName = reservation.tableName ?: "Sin mesa",
                                customerName = reservation.customerName,
                                pax = reservation.pax,
                                time = reservation.time,
                                status = when (reservation.status.name) {
                                    "SEATED" -> KitchenOrderStatus.PREPARING
                                    else -> KitchenOrderStatus.PENDING
                                },
                                items = emptyList(), // TODO: Obtener de API
                                specialRequests = reservation.specialRequests,
                                estimatedReadyTime = null,
                                actualReadyTime = null,
                                alerts = generateAlerts(reservation.pax, reservation.specialRequests)
                            )
                        }
                        .sortedBy { it.time }

                    _uiState.update {
                        it.copy(
                            orders = orders,
                            isLoading = false,
                            alerts = orders.flatMap { it.alerts }
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

    private fun generateAlerts(pax: Int, specialRequests: List<String>): List<KitchenAlert> {
        val alerts = mutableListOf<KitchenAlert>()

        if (pax >= 10) {
            alerts.add(
                KitchenAlert(
                    AlertType.LARGE_GROUP,
                    "Grupo grande: $pax pax"
                )
            )
        }

        specialRequests.forEach { request ->
            when {
                request.contains("gluten", ignoreCase = true) -> {
                    alerts.add(
                        KitchenAlert(
                            AlertType.ALLERGY,
                            "Sin gluten: $request"
                        )
                    )
                }
                request.contains("alergia", ignoreCase = true) || 
                request.contains("alérgico", ignoreCase = true) -> {
                    alerts.add(
                        KitchenAlert(
                            AlertType.ALLERGY,
                            "⚠️ Alergia: $request"
                        )
                    )
                }
                request.contains("trona", ignoreCase = true) -> {
                    alerts.add(
                        KitchenAlert(
                            AlertType.INFO,
                            "Niño con trona"
                        )
                    )
                }
            }
        }

        return alerts
    }

    fun getFilteredOrders(filter: KitchenTimeFilter): List<KitchenOrder> {
        val now = LocalTime.now()
        return when (filter) {
            KitchenTimeFilter.ALL -> _uiState.value.orders
            KitchenTimeFilter.NEXT_HOUR -> {
                _uiState.value.orders.filter {
                    val diff = java.time.Duration.between(now, it.time).toMinutes()
                    diff in -30..60
                }
            }
            KitchenTimeFilter.NEXT_2_HOURS -> {
                _uiState.value.orders.filter {
                    val diff = java.time.Duration.between(now, it.time).toMinutes()
                    diff in -30..120
                }
            }
            KitchenTimeFilter.OVERDUE -> {
                _uiState.value.orders.filter {
                    it.time.isBefore(now) && it.status != KitchenOrderStatus.SERVED
                }
            }
        }
    }

    fun updateOrderStatus(orderId: String, newStatus: KitchenOrderStatus) {
        viewModelScope.launch {
            _uiState.update { state ->
                state.copy(
                    orders = state.orders.map { order ->
                        if (order.reservationId == orderId) {
                            order.copy(status = newStatus)
                        } else {
                            order
                        }
                    }
                )
            }

            // Notificar vía WebSocket
            when (newStatus) {
                KitchenOrderStatus.PREPARING -> {
                    // Notificar que cocina inició preparación
                }
                KitchenOrderStatus.READY -> {
                    // Notificar a camareros que orden está lista
                }
                else -> {}
            }
        }
    }

    fun markOrderReady(orderId: String) {
        updateOrderStatus(orderId, KitchenOrderStatus.READY)

        // Enviar notificación push a camareros
        viewModelScope.launch {
            // TODO: Implementar notificación push
        }
    }

    fun showAlerts() {
        _uiState.update { it.copy(showAlertsDialog = true) }
    }

    fun dismissAlerts() {
        _uiState.update { it.copy(showAlertsDialog = false) }
    }

    private fun handleReservationUpdate(event: ReservationUpdateEvent) {
        when (event.event) {
            "created", "updated" -> {
                // Recargar órdenes
                loadOrders()
            }
            "seated" -> {
                // Marcar orden como en preparación
                event.data.id?.let { id ->
                    updateOrderStatus(id, KitchenOrderStatus.PREPARING)
                }
            }
        }
    }
}
