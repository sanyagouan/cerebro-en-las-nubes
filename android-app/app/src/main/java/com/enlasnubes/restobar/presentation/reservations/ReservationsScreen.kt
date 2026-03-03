package com.enlasnubes.restobar.presentation.reservations

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.ReservationStatus
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReservationsScreen(
    viewModel: ReservationsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedFilter by remember { mutableStateOf(ReservationFilter.ALL) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("Reservas")
                        if (uiState.connectionStatus == ConnectionStatus.CONNECTED) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Surface(
                                color = MaterialTheme.colorScheme.primary,
                                shape = MaterialTheme.shapes.small
                            ) {
                                Text("  En vivo  ", color = MaterialTheme.colorScheme.onPrimary, style = MaterialTheme.typography.labelSmall)
                            }
                        }
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refreshReservations() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Actualizar")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Filters
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ReservationFilter.values().take(4).forEach { filter ->
                    FilterChip(
                        selected = selectedFilter == filter,
                        onClick = {
                            selectedFilter = filter
                            viewModel.setFilter(filter)
                        },
                        label = { Text(filter.name.lowercase().replaceFirstChar { it.uppercase() }) }
                    )
                }
            }

            when {
                uiState.isLoading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
                uiState.error != null -> {
                    Column(
                        Modifier.fillMaxSize().padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { viewModel.dismissError(); viewModel.loadReservations() }) {
                            Text("Reintentar")
                        }
                    }
                }
                else -> {
                    val filteredReservations = viewModel.getFilteredReservations()

                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(filteredReservations) { reservation ->
                            ReservationCard(
                                customerName = reservation.customerName,
                                time = reservation.time.format(DateTimeFormatter.ofPattern("HH:mm")),
                                pax = reservation.pax,
                                status = reservation.status,
                                tableName = reservation.tableName,
                                notes = reservation.notes,
                                specialRequests = reservation.specialRequests,
                                onStatusChange = { newStatus ->
                                    viewModel.updateStatus(
                                        reservation.id,
                                        ReservationStatus.valueOf(newStatus.uppercase())
                                    )
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ReservationCard(
    customerName: String,
    time: String,
    pax: Int,
    status: ReservationStatus,
    tableName: String?,
    notes: String?,
    specialRequests: List<String>,
    onStatusChange: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(customerName, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Schedule, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("$time - $pax personas", style = MaterialTheme.typography.bodyMedium)
                }
                if (tableName != null) {
                    Text("Mesa: $tableName", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary)
                }
                
                if (specialRequests.isNotEmpty() || !notes.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState())
                    ) {
                        specialRequests.forEach { req ->
                            Surface(
                                color = MaterialTheme.colorScheme.errorContainer,
                                shape = MaterialTheme.shapes.small
                            ) {
                                Text(
                                    text = req,
                                    color = MaterialTheme.colorScheme.onErrorContainer,
                                    style = MaterialTheme.typography.labelSmall,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }
                        }
                        if (!notes.isNullOrBlank()) {
                            Surface(
                                color = MaterialTheme.colorScheme.tertiaryContainer,
                                shape = MaterialTheme.shapes.small
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                ) {
                                    Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(12.dp), tint = MaterialTheme.colorScheme.onTertiaryContainer)
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "Notas STAFF",
                                        color = MaterialTheme.colorScheme.onTertiaryContainer,
                                        style = MaterialTheme.typography.labelSmall
                                    )
                                }
                            }
                        }
                    }
                }
            }

            Column(horizontalAlignment = Alignment.End) {
                AssistChip(
                    onClick = { },
                    label = { Text(status.name) },
                    colors = AssistChipDefaults.assistChipColors(
                        containerColor = when (status) {
                            ReservationStatus.CONFIRMED -> MaterialTheme.colorScheme.primaryContainer
                            ReservationStatus.PENDING -> MaterialTheme.colorScheme.secondaryContainer
                            ReservationStatus.SEATED -> MaterialTheme.colorScheme.tertiaryContainer
                            else -> MaterialTheme.colorScheme.surfaceVariant
                        }
                    )
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row {
                    if (status == ReservationStatus.PENDING) {
                        Button(
                            onClick = { onStatusChange("confirmed") },
                            modifier = Modifier.height(36.dp)
                        ) {
                            Text("Confirmar", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                    if (status == ReservationStatus.CONFIRMED) {
                        Button(
                            onClick = { onStatusChange("seated") },
                            modifier = Modifier.height(36.dp)
                        ) {
                            Text("Sentar", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                }
            }
        }
    }
}
