package com.enlasnubes.restobar.presentation.tables

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.enlasnubes.restobar.data.model.Table
import com.enlasnubes.restobar.data.model.TableLocation
import com.enlasnubes.restobar.data.model.TableStatus
import com.enlasnubes.restobar.data.model.UserRole
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TablesScreen(
    userRole: UserRole,
    viewModel: TablesViewModel = androidx.hilt.navigation.compose.hiltViewModel()
) {
    val uiState by androidx.lifecycle.compose.collectAsStateWithLifecycle(viewModel.uiState)
    var selectedLocation by remember { mutableStateOf<TableLocation?>(null) }
    var selectedTable by remember { mutableStateOf<Table?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mapa de Mesas") },
                actions = {
                    if (userRole == UserRole.MANAGER || userRole == UserRole.ADMIN) {
                        IconButton(onClick = { /* Edit mode */ }) {
                            Icon(Icons.Default.Edit, contentDescription = "Editar")
                        }
                    }
                }
            )
        },
        floatingActionButton = {
            if (userRole == UserRole.MANAGER || userRole == UserRole.ADMIN) {
                FloatingActionButton(
                    onClick = { /* Add reservation */ },
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
            // Filtros de ubicación
            LocationFilterChips(
                selectedLocation = selectedLocation,
                onLocationSelected = { selectedLocation = it }
            )

            // Estadísticas rápidas
            TablesStatsRow(tables = uiState.tables)

            // Grid de mesas
            LazyVerticalGrid(
                columns = GridCells.Fixed(3),
                contentPadding = PaddingValues(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                // Header Terraza
                item(span = { GridItemSpan(3) }) {
                    SectionHeader(
                        title = "Terraza",
                        icon = Icons.Default.LocationOn,
                        color = Color(0xFF3498DB)
                    )
                }

                items(
                    items = uiState.tables.filter { 
                        it.location == TableLocation.TERRACE && (selectedLocation == null || selectedLocation == TableLocation.TERRACE)
                    },
                    key = { it.id }
                ) { table ->
                    TableCard(
                        table = table,
                        userRole = userRole,
                        onClick = { selectedTable = table },
                        onStatusChange = { status ->
                            viewModel.updateTableStatus(table.id, status.name.lowercase())
                        }
                    )
                }

                // Header Interior
                item(span = { GridItemSpan(3) }) {
                    SectionHeader(
                        title = "Interior",
                        icon = Icons.Default.Restaurant,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }

                items(
                    items = uiState.tables.filter { 
                        it.location == TableLocation.INTERIOR && (selectedLocation == null || selectedLocation == TableLocation.INTERIOR)
                    },
                    key = { it.id }
                ) { table ->
                    TableCard(
                        table = table,
                        userRole = userRole,
                        onClick = { selectedTable = table },
                        onStatusChange = { status ->
                            viewModel.updateTableStatus(table.id, status.name.lowercase())
                        }
                    )
                }
            }
        }
    }

    // Dialog de detalle/acciones
    selectedTable?.let { table ->
        TableDetailDialog(
            table = table,
            userRole = userRole,
            onDismiss = { selectedTable = null },
            onStatusChange = { status ->
                viewModel.updateTableStatus(table.id, status.name.lowercase())
                selectedTable = null
            }
        )
    }
}

@Composable
private fun SectionHeader(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            color = color,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun LocationFilterChips(
    selectedLocation: TableLocation?,
    onLocationSelected: (TableLocation?) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        FilterChip(
            selected = selectedLocation == null,
            onClick = { onLocationSelected(null) },
            label = { Text("Todas") }
        )
        FilterChip(
            selected = selectedLocation == TableLocation.TERRACE,
            onClick = { onLocationSelected(TableLocation.TERRACE) },
            label = { Text("Terraza") },
            leadingIcon = {
                Icon(Icons.Default.LocationOn, contentDescription = null)
            }
        )
        FilterChip(
            selected = selectedLocation == TableLocation.INTERIOR,
            onClick = { onLocationSelected(TableLocation.INTERIOR) },
            label = { Text("Interior") },
            leadingIcon = {
                Icon(Icons.Default.Restaurant, contentDescription = null)
            }
        )
    }
}

@Composable
private fun TablesStatsRow(tables: List<Table>) {
    val total = tables.size
    val occupied = tables.count { it.status == TableStatus.OCCUPIED }
    val reserved = tables.count { it.status == TableStatus.RESERVED }
    val free = tables.count { it.status == TableStatus.FREE }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatBox(label = "Libres", value = free, color = Color(0xFF27AE60))
        StatBox(label = "Ocupadas", value = occupied, color = MaterialTheme.colorScheme.error)
        StatBox(label = "Reservadas", value = reserved, color = MaterialTheme.colorScheme.primary)
        StatBox(label = "Total", value = total, color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
private fun StatBox(label: String, value: Int, color: Color) {
    Card(
        modifier = Modifier.weight(1f),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = value.toString(),
                style = MaterialTheme.typography.titleLarge,
                color = color,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = color
            )
        }
    }
}

@Composable
fun TableCard(
    table: Table,
    userRole: UserRole,
    onClick: () -> Unit,
    onStatusChange: (TableStatus) -> Unit
) {
    val (backgroundColor, borderColor) = when (table.status) {
        TableStatus.FREE -> Color(0xFF27AE60).copy(alpha = 0.15f) to Color(0xFF27AE60)
        TableStatus.OCCUPIED -> MaterialTheme.colorScheme.error.copy(alpha = 0.15f) to MaterialTheme.colorScheme.error
        TableStatus.RESERVED -> MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) to MaterialTheme.colorScheme.primary
        TableStatus.MAINTENANCE -> Color(0xFFF39C12).copy(alpha = 0.15f) to Color(0xFFF39C12)
    }

    Card(
        modifier = Modifier
            .aspectRatio(1f)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        ),
        border = androidx.compose.foundation.BorderStroke(2.dp, borderColor)
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Número de mesa
                Text(
                    text = table.name.replace("Mesa ", ""),
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = borderColor
                )

                // Capacidad
                Text(
                    text = "${table.capacity}p",
                    style = MaterialTheme.typography.bodySmall,
                    color = borderColor.copy(alpha = 0.7f)
                )

                // Indicador de reserva actual
                if (table.currentReservation != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Icon(
                        imageVector = Icons.Default.EventSeat,
                        contentDescription = null,
                        tint = borderColor,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = table.currentReservation.time.format(
                            DateTimeFormatter.ofPattern("HH:mm")
                        ),
                        style = MaterialTheme.typography.labelSmall,
                        color = borderColor
                    )
                }
            }
        }
    }
}

@Composable
fun TableDetailDialog(
    table: Table,
    userRole: UserRole,
    onDismiss: () -> Unit,
    onStatusChange: (TableStatus) -> Unit
) {
    var showStatusMenu by remember { mutableStateOf(false) }

    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.EventSeat,
                    contentDescription = null,
                    modifier = Modifier.size(32.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(table.name)
            }
        },
        text = {
            Column {
                Text(
                    text = "Capacidad: ${table.capacity} personas",
                    style = MaterialTheme.typography.bodyMedium
                )
                if (table.maxCapacity > table.capacity) {
                    Text(
                        text = "Max: ${table.maxCapacity} con sillas extra",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Ubicación: ${if (table.location == TableLocation.TERRACE) "Terraza" else "Interior"}",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Estado: ${getStatusText(table.status)}",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )

                // Reserva actual
                table.currentReservation?.let { reservation ->
                    Spacer(modifier = Modifier.height(16.dp))
                    androidx.compose.material3.Divider()
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Reserva actual:",
                        style = MaterialTheme.typography.labelMedium
                    )
                    Text(
                        text = "${reservation.customerName} - ${reservation.pax} pax",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "${reservation.time.format(DateTimeFormatter.ofPattern("HH:mm"))}",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        },
        confirmButton = {
            if (userRole != UserRole.COOK) {
                Box {
                    IconButton(onClick = { showStatusMenu = true }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "Cambiar estado")
                    }

                    DropdownMenu(
                        expanded = showStatusMenu,
                        onDismissRequest = { showStatusMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Marcar Libre") },
                            onClick = {
                                onStatusChange(TableStatus.FREE)
                                showStatusMenu = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("Marcar Ocupada") },
                            onClick = {
                                onStatusChange(TableStatus.OCCUPIED)
                                showStatusMenu = false
                            }
                        )
                        if (userRole == UserRole.MANAGER || userRole == UserRole.ADMIN) {
                            DropdownMenuItem(
                                text = { Text("Mantenimiento") },
                                onClick = {
                                    onStatusChange(TableStatus.MAINTENANCE)
                                    showStatusMenu = false
                                }
                            )
                        }
                    }
                }
            }
        },
        dismissButton = {
            androidx.compose.material3.TextButton(onClick = onDismiss) {
                Text("Cerrar")
            }
        }
    )
}

private fun getStatusText(status: TableStatus): String {
    return when (status) {
        TableStatus.FREE -> "Libre"
        TableStatus.OCCUPIED -> "Ocupada"
        TableStatus.RESERVED -> "Reservada"
        TableStatus.MAINTENANCE -> "Mantenimiento"
    }
}
