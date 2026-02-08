package com.enlasnubes.restobar.presentation.reservations

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.ReservationStatus
import com.enlasnubes.restobar.data.model.UserRole
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.CloudQueue
import androidx.compose.material3.IconButton

@OptIn(ExperimentalMaterial3Api::class, ExperimentalMaterialApi::class)
@Composable
fun ReservationsScreen(
    userRole: UserRole,
    viewModel: ReservationsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    val pullRefreshState = rememberPullRefreshState(
        refreshing = uiState.isRefreshing,
        onRefresh = { viewModel.refreshReservations() }
    )

    LaunchedEffect(Unit) {
        viewModel.loadReservations()
    }

    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.dismissError()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Reservas del Día")
                        Text(
                            text = when (uiState.connectionStatus) {
                                ConnectionStatus.CONNECTED -> "En tiempo real"
                                ConnectionStatus.CONNECTING -> "Conectando..."
                                ConnectionStatus.ERROR -> "Error de conexión"
                                ConnectionStatus.DISCONNECTED -> "Sin conexión"
                            },
                            style = MaterialTheme.typography.labelSmall,
                            color = when (uiState.connectionStatus) {
                                ConnectionStatus.CONNECTED -> Color(0xFF27AE60)
                                else -> MaterialTheme.colorScheme.error
                            }
                        )
                    }
                },
                actions = {
                    // Indicador de conexión
                    IconButton(onClick = { }) {
                        Icon(
                            imageVector = if (uiState.connectionStatus == ConnectionStatus.CONNECTED) 
                                Icons.Default.CloudQueue else Icons.Default.CloudOff,
                            contentDescription = "Estado de conexión",
                            tint = when (uiState.connectionStatus) {
                                ConnectionStatus.CONNECTED -> Color(0xFF27AE60)
                                else -> MaterialTheme.colorScheme.error
                            }
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Filtros
            FilterChipsRow(
                selectedFilter = uiState.selectedFilter,
                onFilterSelected = { viewModel.setFilter(it) }
            )

            // Lista de reservas
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pullRefresh(pullRefreshState)
            ) {
                when {
                    uiState.isLoading -> {
                        CircularProgressIndicator(
                            modifier = Modifier.align(Alignment.Center)
                        )
                    }
                    uiState.reservations.isEmpty() -> {
                        EmptyState()
                    }
                    else -> {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            items(
                                items = viewModel.getFilteredReservations(),
                                key = { it.id }
                            ) { reservation ->
                                ReservationCard(
                                    reservation = reservation,
                                    userRole = userRole,
                                    onStatusUpdate = { status ->
                                        viewModel.updateStatus(reservation.id, status)
                                    },
                                    onEdit = {
                                        // TODO: Navigate to edit screen
                                    },
                                    onViewDetails = {
                                        // TODO: Show detail dialog
                                    }
                                )
                            }
                        }
                    }
                }

                // Indicador de pull-to-refresh
                PullRefreshIndicator(
                    refreshing = uiState.isRefreshing,
                    state = pullRefreshState,
                    modifier = Modifier.align(Alignment.TopCenter)
                )
            }
        }
    }
}

@Composable
private fun FilterChipsRow(
    selectedFilter: ReservationFilter,
    onFilterSelected: (ReservationFilter) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        FilterChip(
            selected = selectedFilter == ReservationFilter.ALL,
            onClick = { onFilterSelected(ReservationFilter.ALL) },
            label = { Text("Todas") }
        )
        FilterChip(
            selected = selectedFilter == ReservationFilter.PENDING,
            onClick = { onFilterSelected(ReservationFilter.PENDING) },
            label = { Text("Pendientes") }
        )
        FilterChip(
            selected = selectedFilter == ReservationFilter.CONFIRMED,
            onClick = { onFilterSelected(ReservationFilter.CONFIRMED) },
            label = { Text("Confirmadas") }
        )
        FilterChip(
            selected = selectedFilter == ReservationFilter.SEATED,
            onClick = { onFilterSelected(ReservationFilter.SEATED) },
            label = { Text("Sentados") }
        )
    }
}

@Composable
private fun EmptyState() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.CloudOff,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Text(
                text = "No hay reservas para mostrar",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "Desliza hacia abajo para actualizar",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
        }
    }
}
