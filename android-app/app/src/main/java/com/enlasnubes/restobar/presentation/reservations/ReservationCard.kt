package com.enlasnubes.restobar.presentation.reservations

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccessTime
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.EventSeat
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.enlasnubes.restobar.data.model.Reservation
import com.enlasnubes.restobar.data.model.ReservationStatus
import com.enlasnubes.restobar.data.model.UserRole
import java.time.format.DateTimeFormatter

@Composable
fun ReservationCard(
    reservation: Reservation,
    userRole: UserRole,
    onStatusUpdate: (ReservationStatus) -> Unit,
    onEdit: () -> Unit,
    onViewDetails: () -> Unit,
    modifier: Modifier = Modifier
) {
    val statusColor = when (reservation.status) {
        ReservationStatus.PENDING -> MaterialTheme.colorScheme.tertiary
        ReservationStatus.CONFIRMED -> MaterialTheme.colorScheme.primary
        ReservationStatus.SEATED -> Color(0xFF27AE60)
        ReservationStatus.PAYING -> Color(0xFFF39C12)
        ReservationStatus.COMPLETED -> Color(0xFF2C3E50)
        ReservationStatus.CANCELLED -> MaterialTheme.colorScheme.error
        ReservationStatus.NO_SHOW -> Color(0xFF95A5A6)
    }

    val statusText = when (reservation.status) {
        ReservationStatus.PENDING -> "Pendiente"
        ReservationStatus.CONFIRMED -> "Confirmada"
        ReservationStatus.SEATED -> "Sentado"
        ReservationStatus.PAYING -> "Pagando"
        ReservationStatus.COMPLETED -> "Completada"
        ReservationStatus.CANCELLED -> "Cancelada"
        ReservationStatus.NO_SHOW -> "No Show"
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onViewDetails),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header: Hora + Status
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.AccessTime,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = reservation.time.format(DateTimeFormatter.ofPattern("HH:mm")),
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }

                StatusChip(status = statusText, color = statusColor)
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Nombre del cliente
            Text(
                text = reservation.customerName,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Detalles
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Pax
                InfoChip(
                    icon = Icons.Default.Person,
                    text = "${reservation.pax} pax",
                    highlight = reservation.pax >= 7
                )

                // Mesa
                reservation.tableName?.let {
                    InfoChip(
                        icon = Icons.Default.EventSeat,
                        text = it
                    )
                }

                // Ubicación
                reservation.location?.let { loc ->
                    InfoChip(
                        icon = Icons.Default.Place,
                        text = if (loc.name == "TERRACE") "Terraza" else "Interior"
                    )
                }
            }

            // Notas
            if (!reservation.notes.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Notas: ${reservation.notes}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }

            // Peticiones especiales
            if (reservation.specialRequests.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row {
                    reservation.specialRequests.forEach { request ->
                        SpecialRequestChip(request = request)
                        Spacer(modifier = Modifier.width(4.dp))
                    }
                }
            }

            HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))

            // Acciones rápidas
            QuickActionsRow(
                reservation = reservation,
                userRole = userRole,
                onStatusUpdate = onStatusUpdate,
                onEdit = onEdit
            )
        }
    }
}

@Composable
private fun StatusChip(status: String, color: Color) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = color.copy(alpha = 0.15f)
    ) {
        Text(
            text = status,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelMedium,
            color = color,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun InfoChip(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String,
    highlight: Boolean = false
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(16.dp),
            tint = if (highlight) MaterialTheme.colorScheme.error 
                   else MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = if (highlight) MaterialTheme.colorScheme.error 
                    else MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = if (highlight) FontWeight.Bold else FontWeight.Normal
        )
    }
}

@Composable
private fun SpecialRequestChip(request: String) {
    val (icon, label) = when {
        request.contains("trona", ignoreCase = true) -> Icons.Default.Person to "Trona"
        request.contains("gluten", ignoreCase = true) -> Icons.Default.Cancel to "Sin Gluten"
        request.contains("mascota", ignoreCase = true) -> Icons.Default.Person to "Mascota"
        else -> Icons.Default.Place to request.take(10)
    }

    Surface(
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.secondaryContainer
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(14.dp)
            )
            Spacer(modifier = Modifier.width(2.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall
            )
        }
    }
}

@Composable
private fun QuickActionsRow(
    reservation: Reservation,
    userRole: UserRole,
    onStatusUpdate: (ReservationStatus) -> Unit,
    onEdit: () -> Unit
) {
    var showMoreOptions by remember { mutableStateOf(false) }

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Acciones según estado y rol
        when (reservation.status) {
            ReservationStatus.PENDING, ReservationStatus.CONFIRMED -> {
                // Botón Sentado (Camarero, Encargada, Admin)
                if (userRole != UserRole.COCINA) {
                    QuickActionButton(
                        icon = Icons.Default.EventSeat,
                        label = "Sentado",
                        color = Color(0xFF27AE60),
                        onClick = { onStatusUpdate(ReservationStatus.SEATED) },
                        modifier = Modifier.weight(1f)
                    )
                }

                // Botón Cancelar (Encargada, Admin)
                if (userRole == UserRole.ENCARGADA || userRole == UserRole.ADMINISTRADORA) {
                    QuickActionButton(
                        icon = Icons.Default.Cancel,
                        label = "Cancelar",
                        color = MaterialTheme.colorScheme.error,
                        onClick = { onStatusUpdate(ReservationStatus.CANCELLED) },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            ReservationStatus.SEATED -> {
                // Botón Mesa Libre
                QuickActionButton(
                    icon = Icons.Default.CheckCircle,
                    label = "Liberar",
                    color = MaterialTheme.colorScheme.primary,
                    onClick = { onStatusUpdate(ReservationStatus.COMPLETED) },
                    modifier = Modifier.weight(1f)
                )

                // No-show
                if (userRole == UserRole.ENCARGADA || userRole == UserRole.ADMINISTRADORA) {
                    QuickActionButton(
                        icon = Icons.Default.Delete,
                        label = "No Show",
                        color = Color(0xFF95A5A6),
                        onClick = { onStatusUpdate(ReservationStatus.NO_SHOW) },
                        modifier = Modifier.weight(1f)
                    )
                }
            }
            else -> {}
        }

        // Menú de más opciones (Editar, etc)
        if (userRole == UserRole.ENCARGADA || userRole == UserRole.ADMINISTRADORA) {
            Box {
                IconButton(onClick = { showMoreOptions = true }) {
                    Icon(Icons.Default.Edit, contentDescription = "Más opciones")
                }

                DropdownMenu(
                    expanded = showMoreOptions,
                    onDismissRequest = { showMoreOptions = false }
                ) {
                    DropdownMenuItem(
                        text = { Text("Editar reserva") },
                        onClick = {
                            showMoreOptions = false
                            onEdit()
                        },
                        leadingIcon = {
                            Icon(Icons.Default.Edit, contentDescription = null)
                        }
                    )

                    if (reservation.status == ReservationStatus.PENDING) {
                        DropdownMenuItem(
                            text = { Text("Confirmar") },
                            onClick = {
                                showMoreOptions = false
                                onStatusUpdate(ReservationStatus.CONFIRMED)
                            },
                            leadingIcon = {
                                Icon(Icons.Default.CheckCircle, contentDescription = null)
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun QuickActionButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
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
                tint = color,
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = label,
                color = color,
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
