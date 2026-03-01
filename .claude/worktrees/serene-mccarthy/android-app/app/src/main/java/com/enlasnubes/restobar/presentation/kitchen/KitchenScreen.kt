package com.enlasnubes.restobar.presentation.kitchen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.clickable
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessTime
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Group
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Badge
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
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
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.Reservation
import com.enlasnubes.restobar.data.model.ReservationStatus
import com.enlasnubes.restobar.data.model.UserRole
import java.time.LocalTime
import java.time.format.DateTimeFormatter

// Modelo de datos para la vista de cocina
data class KitchenOrder(
    val reservationId: String,
    val tableName: String,
    val customerName: String,
    val pax: Int,
    val time: LocalTime,
    val status: KitchenOrderStatus,
    val items: List<OrderItem>,
    val specialRequests: List<String>,
    val estimatedReadyTime: LocalTime?,
    val actualReadyTime: LocalTime?,
    val alerts: List<KitchenAlert> = emptyList()
)

data class OrderItem(
    val name: String,
    val quantity: Int,
    val category: ItemCategory
)

enum class ItemCategory {
    STARTER, MAIN, DESSERT, SPECIAL
}

data class KitchenAlert(
    val type: AlertType,
    val message: String
)

enum class AlertType {
    URGENT, INFO, ALLERGY, LARGE_GROUP
}

enum class KitchenOrderStatus {
    PENDING, PREPARING, READY, SERVED
}

enum class KitchenTimeFilter {
    ALL, NEXT_HOUR, NEXT_2_HOURS, OVERDUE
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KitchenScreen(
    userRole: UserRole,
    viewModel: KitchenViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedFilter by remember { mutableStateOf(KitchenTimeFilter.ALL) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Restaurant,
                            contentDescription = null,
                            modifier = Modifier.size(28.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Cocina")
                    }
                },
                actions = {
                    // Contador de alertas
                    if (uiState.alerts.isNotEmpty()) {
                        BadgedBox(
                            badge = { Badge { Text(uiState.alerts.size.toString()) } }
                        ) {
                            IconButton(onClick = { viewModel.showAlerts() }) {
                                Icon(Icons.Default.Notifications, contentDescription = "Alertas")
                            }
                        }
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
            // Filtros de tiempo
            TimeFilterChips(
                selectedFilter = selectedFilter,
                onFilterSelected = { selectedFilter = it }
            )

            // Resumen del flujo
            KitchenFlowSummary(orders = uiState.orders)

            // Timeline de órdenes
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(
                    items = viewModel.getFilteredOrders(selectedFilter),
                    key = { it.reservationId }
                ) { order ->
                    KitchenOrderCard(
                        order = order,
                        onStatusChange = { status ->
                            viewModel.updateOrderStatus(order.reservationId, status)
                        },
                        onReady = {
                            viewModel.markOrderReady(order.reservationId)
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun TimeFilterChips(
    selectedFilter: KitchenTimeFilter,
    onFilterSelected: (KitchenTimeFilter) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        FilterChip(
            selected = selectedFilter == KitchenTimeFilter.ALL,
            onClick = { onFilterSelected(KitchenTimeFilter.ALL) },
            label = { Text("Todas") }
        )
        FilterChip(
            selected = selectedFilter == KitchenTimeFilter.NEXT_HOUR,
            onClick = { onFilterSelected(KitchenTimeFilter.NEXT_HOUR) },
            label = { Text("Próx. hora") },
            leadingIcon = {
                Icon(Icons.Default.Timer, contentDescription = null)
            }
        )
        FilterChip(
            selected = selectedFilter == KitchenTimeFilter.NEXT_2_HOURS,
            onClick = { onFilterSelected(KitchenTimeFilter.NEXT_2_HOURS) },
            label = { Text("2 horas") },
            leadingIcon = {
                Icon(Icons.Default.AccessTime, contentDescription = null)
            }
        )
        FilterChip(
            selected = selectedFilter == KitchenTimeFilter.OVERDUE,
            onClick = { onFilterSelected(KitchenTimeFilter.OVERDUE) },
            label = { Text("Urgentes") },
            leadingIcon = {
                Icon(Icons.Default.Warning, contentDescription = null)
            }
        )
    }
}

@Composable
private fun KitchenFlowSummary(orders: List<KitchenOrder>) {
    val pending = orders.count { it.status == KitchenOrderStatus.PENDING }
    val preparing = orders.count { it.status == KitchenOrderStatus.PREPARING }
    val ready = orders.count { it.status == KitchenOrderStatus.READY }
    val totalPax = orders.sumOf { it.pax }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            FlowStatItem(label = "Pendientes", value = pending, color = MaterialTheme.colorScheme.tertiary)
            FlowStatItem(label = "En cocina", value = preparing, color = Color(0xFFF39C12))
            FlowStatItem(label = "Listos", value = ready, color = Color(0xFF27AE60))
            FlowStatItem(label = "Total pax", value = totalPax, color = MaterialTheme.colorScheme.primary)
        }
    }
}

@Composable
private fun FlowStatItem(label: String, value: Int, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value.toString(),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun KitchenOrderCard(
    order: KitchenOrder,
    onStatusChange: (KitchenOrderStatus) -> Unit,
    onReady: () -> Unit
) {
    val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")
    val isUrgent = order.alerts.any { it.type == AlertType.URGENT }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when (order.status) {
                KitchenOrderStatus.READY -> Color(0xFF27AE60).copy(alpha = 0.1f)
                KitchenOrderStatus.PREPARING -> Color(0xFFF39C12).copy(alpha = 0.1f)
                else -> MaterialTheme.colorScheme.surface
            }
        ),
        border = if (isUrgent) {
            androidx.compose.foundation.BorderStroke(2.dp, MaterialTheme.colorScheme.error)
        } else null
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header: Hora, Mesa, Pax
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Indicador de urgencia
                    if (isUrgent) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.error,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                    }

                    Text(
                        text = order.time.format(timeFormatter),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = if (isUrgent) MaterialTheme.colorScheme.error 
                               else MaterialTheme.colorScheme.primary
                    )

                    Spacer(modifier = Modifier.width(16.dp))

                    Icon(
                        imageVector = Icons.Default.Restaurant,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = order.tableName,
                        style = MaterialTheme.typography.bodyLarge
                    )
                }

                // Pax
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (order.pax >= 7) MaterialTheme.colorScheme.error.copy(alpha = 0.15f)
                            else MaterialTheme.colorScheme.primary.copy(alpha = 0.15f)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Group,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = if (order.pax >= 7) MaterialTheme.colorScheme.error
                                   else MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "${order.pax}",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.Bold,
                            color = if (order.pax >= 7) MaterialTheme.colorScheme.error
                                   else MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Alertas
            order.alerts.forEach { alert ->
                AlertChip(alert = alert)
                Spacer(modifier = Modifier.height(4.dp))
            }

            // Peticiones especiales
            if (order.specialRequests.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                order.specialRequests.forEach { request ->
                    SpecialRequestRow(request = request)
                }
            }

            Divider(modifier = Modifier.padding(vertical = 12.dp))

            // Acciones
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                when (order.status) {
                    KitchenOrderStatus.PENDING -> {
                        ActionButton(
                            text = "Iniciar",
                            icon = Icons.Default.Restaurant,
                            color = Color(0xFF3498DB),
                            onClick = { onStatusChange(KitchenOrderStatus.PREPARING) },
                            modifier = Modifier.weight(1f)
                        )
                    }
                    KitchenOrderStatus.PREPARING -> {
                        ActionButton(
                            text = "Listo",
                            icon = Icons.Default.CheckCircle,
                            color = Color(0xFF27AE60),
                            onClick = onReady,
                            modifier = Modifier.weight(1f)
                        )
                    }
                    KitchenOrderStatus.READY -> {
                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            color = Color(0xFF27AE60).copy(alpha = 0.2f)
                        ) {
                            Row(
                                modifier = Modifier
                                    .padding(vertical = 10.dp)
                                    .fillMaxWidth(),
                                horizontalArrangement = Arrangement.Center,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = Color(0xFF27AE60)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = "¡Listo para servir!",
                                    color = Color(0xFF27AE60),
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                    else -> {}
                }
            }
        }
    }
}

@Composable
private fun AlertChip(alert: KitchenAlert) {
    val (icon, color) = when (alert.type) {
        AlertType.URGENT -> Icons.Default.Warning to MaterialTheme.colorScheme.error
        AlertType.ALLERGY -> Icons.Default.Error to Color(0xFFF39C12)
        AlertType.LARGE_GROUP -> Icons.Default.Group to MaterialTheme.colorScheme.primary
        AlertType.INFO -> Icons.Default.AccessTime to MaterialTheme.colorScheme.secondary
    }

    Surface(
        shape = RoundedCornerShape(8.dp),
        color = color.copy(alpha = 0.15f)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = color
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = alert.message,
                style = MaterialTheme.typography.labelMedium,
                color = color,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun SpecialRequestRow(request: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = Icons.Default.Edit,
            contentDescription = null,
            modifier = Modifier.size(14.dp),
            tint = MaterialTheme.colorScheme.tertiary
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = request,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.tertiary
        )
    }
}

@Composable
private fun ActionButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(8.dp),
        color = color.copy(alpha = 0.1f)
    ) {
        Row(
            modifier = Modifier
                .padding(vertical = 10.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = text,
                color = color,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

// Placeholder para BadgedBox (simplificado)
@Composable
fun BadgedBox(
    badge: @Composable () -> Unit,
    content: @Composable () -> Unit
) {
    Box {
        content()
        Box(
            modifier = Modifier.align(Alignment.TopEnd)
        ) {
            badge()
        }
    }
}
