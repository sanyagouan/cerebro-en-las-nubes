package com.enlasnubes.restobar

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.enlasnubes.restobar.presentation.auth.LoginScreen
import com.enlasnubes.restobar.presentation.auth.LoginViewModel
import com.enlasnubes.restobar.presentation.dashboard.DashboardScreen
import com.enlasnubes.restobar.presentation.navigation.Screen
import com.enlasnubes.restobar.presentation.theme.EnLasNubesTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val loginViewModel: LoginViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EnLasNubesTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    RestobarApp(loginViewModel = loginViewModel)
                }
            }
        }
    }
}

@Composable
fun RestobarApp(
    loginViewModel: LoginViewModel
) {
    val navController = rememberNavController()
    val authState by loginViewModel.authState.collectAsStateWithLifecycle()

    NavHost(
        navController = navController,
        startDestination = if (authState.isAuthenticated) Screen.Dashboard.route else Screen.Login.route
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                viewModel = loginViewModel,
                onLoginSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Dashboard.route) {
            DashboardScreen(
                userRol = authState.userRol,
                userName = authState.userName,
                onLogout = {
                    loginViewModel.logout()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Dashboard.route) { inclusive = true }
                    }
                }
            )
        }
    }
}
