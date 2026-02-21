package com.enlasnubes.restobar.presentation.admin

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdminScreen(
    userRol: String,
    onNavigateToUsers: () -> Unit = {}
) {
    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Panel de Administracion") }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Quick Stats
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                StatCard("Usuarios", "12", Icons.Default.People, MaterialTheme.colorScheme.primary)
                StatCard("Reservas Hoy", "24", Icons.Default.CalendarToday, MaterialTheme.colorScheme.secondary)
                StatCard("Ingresos", "1,250", Icons.Default.AttachMoney, MaterialTheme.colorScheme.tertiary)
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Menu Options
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column {
                    AdminMenuItem(
                        icon = Icons.Default.People,
                        title = "Gestion de Usuarios",
                        subtitle = "Crear y editar usuarios del sistema",
                        onClick = onNavigateToUsers
                    )
                    Divider()
                    AdminMenuItem(
                        icon = Icons.Default.Restaurant,
                        title = "Gestion de Mesas",
                        subtitle = "Configurar mesas y capacidades",
                        onClick = { }
                    )
                    Divider()
                    AdminMenuItem(
                        icon = Icons.Default.Settings,
                        title = "Configuracion",
                        subtitle = "Ajustes del sistema",
                        onClick = { }
                    )
                    Divider()
                    AdminMenuItem(
                        icon = Icons.Default.BarChart,
                        title = "Reportes",
                        subtitle = "Ver estadisticas y reportes",
                        onClick = { }
                    )
                }
            }
        }
    }
}

@Composable
private fun RowScope.StatCard(title: String, value: String, icon: ImageVector, color: Color) {
    Card(
        modifier = Modifier.weight(1f),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(32.dp))
            Spacer(modifier = Modifier.height(8.dp))
            Text(value, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = color)
            Text(title, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
private fun AdminMenuItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.width(16.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(title, fontWeight = FontWeight.Medium)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Icon(Icons.Default.ChevronRight, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
