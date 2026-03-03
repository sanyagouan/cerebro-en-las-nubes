package com.enlasnubes.restobar.presentation.tables

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.Table
import com.enlasnubes.restobar.data.model.TableLocation
import com.enlasnubes.restobar.data.model.TableStatus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TablesScreen(
    userRol: String,
    viewModel: TablesViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedLocation by remember { mutableStateOf<TableLocation?>(null) }
    var selectedTable by remember { mutableStateOf<Table?>(null) }
    
    val canEdit = userRol == "encargada" || userRol == "administradora"

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mapa de Mesas") },
                actions = {
                    if (canEdit) {
                        IconButton(onClick = { }) {
                            Icon(Icons.Default.Edit, contentDescription = "Editar")
                        }
                    }
                }
            )
        },
        floatingActionButton = {
            if (canEdit) {
                FloatingActionButton(
                    onClick = { },
                    containerColor = MaterialTheme.colorScheme.primary
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Nueva reserva")
                }
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Filter chips
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedLocation == null,
                    onClick = { selectedLocation = null },
                    label = { Text("Todas") }
                )
                FilterChip(
                    selected = selectedLocation == TableLocation.TERRACE,
                    onClick = { selectedLocation = TableLocation.TERRACE },
                    label = { Text("Terraza") },
                    leadingIcon = { Icon(Icons.Default.Restaurant, contentDescription = null, modifier = Modifier.size(16.dp)) }
                )
                FilterChip(
                    selected = selectedLocation == TableLocation.INTERIOR,
                    onClick = { selectedLocation = TableLocation.INTERIOR },
                    label = { Text("Interior") },
                    leadingIcon = { Icon(Icons.Default.EventSeat, contentDescription = null, modifier = Modifier.size(16.dp)) }
                )
            }

            // Stats row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                StatBox(label = "Libres", value = uiState.tables.count { it.status == TableStatus.FREE }, color = Color(0xFF27AE60))
                StatBox(label = "Ocupadas", value = uiState.tables.count { it.status == TableStatus.OCCUPIED }, color = MaterialTheme.colorScheme.error)
                StatBox(label = "Reservadas", value = uiState.tables.count { it.status == TableStatus.RESERVED }, color = MaterialTheme.colorScheme.primary)
            }

            when {
                uiState.isLoading -> {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
                uiState.error != null -> {
                    Box(Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.Center) {
                        Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
                    }
                }
                else -> {
                    val filteredTables = selectedLocation?.let { loc ->
                        uiState.tables.filter { it.location == loc }
                    } ?: uiState.tables

                    LazyVerticalGrid(
                        columns = GridCells.Adaptive(120.dp),
                        contentPadding = PaddingValues(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(filteredTables) { table ->
                            TableCard(
                                table = table,
                                onClick = { selectedTable = table },
                                onStatusChange = { viewModel.updateTableStatus(table.id, it) }
                            )
                        }
                    }
                }
            }
        }
    }

    if (selectedTable != null) {
        TableQuickActionsDialog(
            table = selectedTable!!,
            onDismiss = { selectedTable = null },
            onStatusChange = { status ->
                viewModel.updateTableStatus(selectedTable!!.id, status)
                selectedTable = null
            },
            onAddWalkIn = {
                viewModel.updateTableStatus(selectedTable!!.id, "occupied")
                selectedTable = null
            },
            onReportIssue = {
                viewModel.updateTableStatus(selectedTable!!.id, "maintenance")
                selectedTable = null
            }
        )
    }
}

@Composable
private fun RowScope.StatBox(label: String, value: Int, color: Color) {
    Card(
        modifier = Modifier.weight(1f),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(value.toString(), style = MaterialTheme.typography.titleLarge, color = color, fontWeight = FontWeight.Bold)
            Text(label, style = MaterialTheme.typography.bodySmall, color = color)
        }
    }
}

@Composable
private fun TableCard(
    table: Table,
    onClick: () -> Unit,
    onStatusChange: (String) -> Unit
) {
    val statusColor = when (table.status) {
        TableStatus.FREE -> Color(0xFF27AE60)
        TableStatus.OCCUPIED -> Color(0xFFE74C3C)
        TableStatus.RESERVED -> Color(0xFFF39C12)
        TableStatus.MAINTENANCE -> Color(0xFF95A5A6)
    }

    val shape = if (table.capacity <= 2) CircleShape else RoundedCornerShape(16.dp)

    Card(
        modifier = Modifier
            .aspectRatio(1f)
            .border(2.dp, statusColor, shape)
            .clickable(onClick = onClick),
        shape = shape,
        colors = CardDefaults.cardColors(containerColor = statusColor.copy(alpha = 0.15f))
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = table.number,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = statusColor
            )
            Text(
                text = "${table.capacity} pax",
                style = MaterialTheme.typography.bodySmall,
                color = statusColor.copy(alpha = 0.8f)
            )
            if (table.status == TableStatus.RESERVED) {
                Spacer(modifier = Modifier.height(4.dp))
                Surface(
                    color = statusColor,
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        "Reserva",
                        color = Color.White,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TableQuickActionsDialog(
    table: Table,
    onDismiss: () -> Unit,
    onStatusChange: (String) -> Unit,
    onAddWalkIn: () -> Unit,
    onReportIssue: () -> Unit
) {
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
            Text("Gestión rápida - Mesa ${table.number}", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(16.dp))
            
            ListItem(
                headlineContent = { Text("Walk-in (Sentar sin reserva)") },
                leadingContent = { Icon(Icons.Default.PersonAdd, contentDescription = null, tint = MaterialTheme.colorScheme.primary) },
                modifier = Modifier.clickable { onAddWalkIn() }
            )
            ListItem(
                headlineContent = { Text(if (table.status == TableStatus.FREE) "Marcar como Ocupada" else "Liberar Mesa") },
                leadingContent = { 
                    Icon(
                        if (table.status == TableStatus.FREE) Icons.Default.EventSeat else Icons.Default.CheckCircle, 
                        contentDescription = null,
                        tint = if (table.status == TableStatus.FREE) MaterialTheme.colorScheme.error else Color(0xFF27AE60)
                    ) 
                },
                modifier = Modifier.clickable { onStatusChange(if (table.status == TableStatus.FREE) "occupied" else "free") }
            )
            ListItem(
                headlineContent = { Text("Reportar Incidencia (Mantenimiento)") },
                leadingContent = { Icon(Icons.Default.Warning, contentDescription = null, tint = Color(0xFF95A5A6)) },
                modifier = Modifier.clickable { onReportIssue() }
            )
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
