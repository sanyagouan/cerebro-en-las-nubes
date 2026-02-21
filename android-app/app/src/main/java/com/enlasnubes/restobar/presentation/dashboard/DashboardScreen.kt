package com.enlasnubes.restobar.presentation.dashboard

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.AdminPanelSettings
import androidx.compose.material.icons.filled.ArrowBack
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import com.enlasnubes.restobar.presentation.admin.AdminScreen
import com.enlasnubes.restobar.presentation.admin.UserManagementScreen
import com.enlasnubes.restobar.presentation.kitchen.KitchenScreen
import com.enlasnubes.restobar.presentation.reservations.ReservationsScreen
import com.enlasnubes.restobar.presentation.tables.TablesScreen

sealed class TabItem(
    val title: String,
    val icon: ImageVector
) {
    data object Reservations : TabItem("Reservas", Icons.Default.Event)
    data object Tables : TabItem("Mesas", Icons.Default.TableBar)
    data object Kitchen : TabItem("Cocina", Icons.Default.Restaurant)
    data object Admin : TabItem("Admin", Icons.Default.AdminPanelSettings)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    userRol: String,
    userName: String,
    onLogout: () -> Unit
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
    var showUserManagement by rememberSaveable { mutableStateOf(false) }

    val tabs = when (userRol) {
        "camarero" -> listOf(TabItem.Reservations, TabItem.Tables)
        "cocina" -> listOf(TabItem.Kitchen)
        "encargada" -> listOf(TabItem.Reservations, TabItem.Tables, TabItem.Kitchen)
        "administradora" -> listOf(TabItem.Reservations, TabItem.Tables, TabItem.Kitchen, TabItem.Admin)
        else -> listOf(TabItem.Reservations) // Default fallback
    }

    // Si estamos en UserManagement, mostrar esa pantalla
    if (showUserManagement) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text("Gestion de Usuarios") },
                    navigationIcon = {
                        IconButton(onClick = { showUserManagement = false }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Volver")
                        }
                    },
                    actions = {
                        IconButton(onClick = onLogout) {
                            Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Cerrar sesion")
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
                UserManagementScreen(userRol = userRol)
            }
        }
        return
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("En Las Nubes - ${getRoleName(userRol)}") },
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Cerrar sesion")
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (tabs.getOrNull(selectedTab)) {
                TabItem.Reservations -> ReservationsScreen(userRol = userRol)
                TabItem.Tables -> TablesScreen(userRol = userRol)
                TabItem.Kitchen -> KitchenScreen(userRol = userRol)
                TabItem.Admin -> AdminScreen(
                    userRol = userRol,
                    onNavigateToUsers = { showUserManagement = true }
                )
                else -> {}
            }
        }
    }
}

private fun getRoleName(rol: String): String {
    return when (rol) {
        "camarero" -> "Camarero"
        "cocina" -> "Cocina"
        "encargada" -> "Encargada"
        "administradora" -> "Administradora"
        else -> rol.replaceFirstChar { it.uppercase() }
    }
}
