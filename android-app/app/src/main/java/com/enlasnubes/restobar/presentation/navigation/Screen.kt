package com.enlasnubes.restobar.presentation.navigation

sealed class Screen(val route: String) {
    data object Login : Screen("login")
    data object Dashboard : Screen("dashboard")
    data object Reservations : Screen("reservations")
    data object Tables : Screen("tables")
    data object Kitchen : Screen("kitchen")
    data object Admin : Screen("admin")
}

sealed class BottomNavItem(
    val route: String,
    val title: String,
    val icon: String
) {
    data object Reservations : BottomNavItem("reservations", "Reservas", "event")
    data object Tables : BottomNavItem("tables", "Mesas", "table_bar")
    data object Kitchen : BottomNavItem("kitchen", "Cocina", "restaurant")
    data object Admin : BottomNavItem("admin", "Admin", "admin_panel_settings")
}
