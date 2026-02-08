package com.enlasnubes.restobar.presentation.admin

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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.AttachMoney
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.Group
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.UserRole

// Modelos para Admin
data class AdminStats(
    val totalReservations: Int,
    val totalRevenue: Double,
    val occupancyRate: Float,
    val totalCustomers: Int,
    val noShowRate: Float,
    val cancellationRate: Float,
    val averagePartySize: Float,
    val peakHours: List<PeakHour>
)

data class PeakHour(
    val hour: String,
    val reservationCount: Int
)

data class UserManagement(
    val id: String,
    val email: String,
    val name: String,
    val role: UserRole,
    val isActive: Boolean
)

enum class AdminTab {
    DASHBOARD, USERS, SETTINGS
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdminScreen(
    viewModel: AdminViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Panel de Administración") },
                actions = {
                    IconButton(onClick = { /* Settings */ }) {
                        Icon(Icons.Default.Settings, contentDescription = "Configuración")
                    }
                }
            )
        },
        floatingActionButton = {
            if (selectedTab == 1) { // Tab de usuarios
                FloatingActionButton(
                    onClick = { viewModel.showAddUserDialog() },
                    containerColor = MaterialTheme.colorScheme.primary
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Agregar usuario")
                }
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Tabs
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Dashboard") },
                    icon = { Icon(Icons.Default.BarChart, contentDescription = null) }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Usuarios") },
                    icon = { Icon(Icons.Default.Group, contentDescription = null) }
                )
                Tab(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    text = { Text("Configuración") },
                    icon = { Icon(Icons.Default.Settings, contentDescription = null) }
                )
            }

            // Contenido según tab
            when (selectedTab) {
                0 -> DashboardTab(stats = uiState.stats)
                1 -> UsersTab(
                    users = uiState.users,
                    onEditUser = { viewModel.editUser(it) },
                    onDeleteUser = { viewModel.deleteUser(it) }
                )
                2 -> SettingsTab()
            }
        }
    }
}

@Composable
private fun DashboardTab(stats: AdminStats?) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // KPIs principales
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                KpiCard(
                    title = "Reservas",
                    value = stats?.totalReservations?.toString() ?: "-",
                    icon = Icons.Default.Event,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.weight(1f)
                )
                KpiCard(
                    title = "Ingresos",
                    value = stats?.let { "€${it.totalRevenue.toInt()}" } ?: "-",
                    icon = Icons.Default.AttachMoney,
                    color = Color(0xFF27AE60),
                    modifier = Modifier.weight(1f)
                )
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                KpiCard(
                    title = "Ocupación",
                    value = stats?.let { "${(it.occupancyRate * 100).toInt()}%" } ?: "-",
                    icon = Icons.Default.TrendingUp,
                    color = Color(0xFFF39C12),
                    modifier = Modifier.weight(1f)
                )
                KpiCard(
                    title = "Clientes",
                    value = stats?.totalCustomers?.toString() ?: "-",
                    icon = Icons.Default.Person,
                    color = MaterialTheme.colorScheme.secondary,
                    modifier = Modifier.weight(1f)
                )
            }
        }

        // Gráfico de horas pico
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Horas Pico",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    stats?.peakHours?.let { hours ->
                        hours.forEach { peak ->
                            PeakHourBar(
                                hour = peak.hour,
                                count = peak.reservationCount,
                                maxCount = hours.maxOf { it.reservationCount }
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    } ?: Text("No hay datos disponibles")
                }
            }
        }

        // Estadísticas adicionales
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Métricas de Rendimiento",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    StatRow(
                        label = "Tasa de No-Show",
                        value = stats?.let { "${(it.noShowRate * 100).toInt()}%" } ?: "-",
                        trend = "+2%"
                    )
                    StatRow(
                        label = "Tasa de Cancelación",
                        value = stats?.let { "${(it.cancellationRate * 100).toInt()}%" } ?: "-",
                        trend = "-1%"
                    )
                    StatRow(
                        label = "Tamaño Medio de Grupo",
                        value = stats?.averagePartySize?.toString() ?: "-",
                        trend = null
                    )
                }
            }
        }
    }
}

@Composable
private fun KpiCard(
    title: String,
    value: String,
    icon: ImageVector,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun PeakHourBar(
    hour: String,
    count: Int,
    maxCount: Int
) {
    val percentage = if (maxCount > 0) count.toFloat() / maxCount else 0f
    
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = hour,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.width(60.dp)
        )
        Box(
            modifier = Modifier.weight(1f)
        ) {
            androidx.compose.foundation.Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(24.dp)
            ) {
                drawRoundRect(
                    color = Color.LightGray,
                    size = androidx.compose.ui.geometry.Size(size.width, size.height),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(4f, 4f)
                )
                drawRoundRect(
                    color = MaterialTheme.colorScheme.primary,
                    size = androidx.compose.ui.geometry.Size(
                        size.width * percentage,
                        size.height
                    ),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(4f, 4f)
                )
            }
        }
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = count.toString(),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun StatRow(
    label: String,
    value: String,
    trend: String?
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = value,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold
            )
            trend?.let {
                Spacer(modifier = Modifier.width(8.dp))
                val trendColor = if (it.startsWith("+")) Color(0xFFE74C3C) else Color(0xFF27AE60)
                Text(
                    text = it,
                    style = MaterialTheme.typography.labelMedium,
                    color = trendColor
                )
            }
        }
    }
}

@Composable
private fun UsersTab(
    users: List<UserManagement>,
    onEditUser: (UserManagement) -> Unit,
    onDeleteUser: (UserManagement) -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(users) { user ->
            UserCard(
                user = user,
                onEdit = { onEditUser(user) },
                onDelete = { onDeleteUser(user) }
            )
        }
    }
}

@Composable
private fun UserCard(
    user: UserManagement,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier.size(40.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = when (user.role) {
                        UserRole.WAITER -> "Camarero"
                        UserRole.COOK -> "Cocinero"
                        UserRole.MANAGER -> "Encargada"
                        UserRole.ADMIN -> "Administrador"
                    },
                    style = MaterialTheme.typography.labelMedium,
                    color = if (user.isActive) MaterialTheme.colorScheme.primary 
                           else MaterialTheme.colorScheme.error
                )
            }
            IconButton(onClick = onEdit) {
                Icon(Icons.Default.Edit, contentDescription = "Editar")
            }
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "Eliminar")
            }
        }
    }
}

@Composable
private fun SettingsTab() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Configuración del Sistema",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.height(16.dp))
        
        // Aquí irían las opciones de configuración
        Text(
            text = "Configuración de horarios, mesas, y preferencias del restaurante.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
