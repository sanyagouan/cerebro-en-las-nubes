package com.enlasnubes.restobar.presentation.dashboard

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.TableBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import com.enlasnubes.restobar.data.model.UserRole
import com.enlasnubes.restobar.presentation.kitchen.KitchenScreen
import com.enlasnubes.restobar.presentation.reservations.ReservationsScreen
import com.enlasnubes.restobar.presentation.tables.TablesScreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    userRole: UserRole,
    userName: String,
    onLogout: () -> Unit
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }

    // Define tabs based on role
    val tabs = when (userRole) {
        UserRole.WAITER -> listOf(
            TabItem.Reservations,
            TabItem.Tables
        )
        UserRole.COOK -> listOf(
            TabItem.Kitchen
        )
        UserRole.MANAGER -> listOf(
            TabItem.Reservations,
            TabItem.Tables,
            TabItem.Kitchen
        )
        UserRole.ADMIN -> listOf(
            TabItem.Reservations,
            TabItem.Tables,
            TabItem.Kitchen,
            TabItem.Admin
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text("En Las Nubes - ${getRoleName(userRole)}")
                },
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ExitToApp,
                            contentDescription = "Cerrar sesión"
                        )
                    }
                }
            )
        },
        bottomBar = {
            if (tabs.size > 1) {
                NavigationBar {
                    tabs.forEachIndexed { index, tab ->
                        NavigationBarItem(
                            icon = { Icon(tab.icon, contentDescription = tab.title) },
                            label = { Text(tab.title) },
                            selected = selectedTab == index,
                            onClick = { selectedTab = index }
                        )
                    }
                }
            }
        }
    ) { padding ->
        // Content based on selected tab
        when (tabs.getOrNull(selectedTab)) {
            TabItem.Reservations -> ReservationsScreen(
                modifier = Modifier.padding(padding),
                userRole = userRole
            )
            TabItem.Tables -> TablesScreen(
                modifier = Modifier.padding(padding),
                userRole = userRole
            )
            TabItem.Kitchen -> KitchenScreen(
                userRole = userRole
            )
            TabItem.Admin -> Text(
                text = "Panel Admin (Próximamente)",
                modifier = Modifier.padding(padding)
            )
            else -> {}
        }
    }
}

private fun getRoleName(role: UserRole): String {
    return when (role) {
        UserRole.WAITER -> "Camarero"
        UserRole.COOK -> "Cocinero"
        UserRole.MANAGER -> "Encargada"
        UserRole.ADMIN -> "Admin"
    }
}

sealed class TabItem(
    val title: String,
    val icon: ImageVector
) {
    data object Reservations : TabItem("Reservas", Icons.Default.Event)
    data object Tables : TabItem("Mesas", Icons.Default.TableBar)
    data object Kitchen : TabItem("Cocina", Icons.Default.Restaurant)
    data object Admin : TabItem("Admin", Icons.Default.AdminPanelSettings)
}
