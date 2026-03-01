package com.enlasnubes.restobar.presentation.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = PrimaryRed,
    onPrimary = Color.White,
    primaryContainer = PrimaryRed.copy(alpha = 0.1f),
    onPrimaryContainer = PrimaryRed,
    secondary = DarkGray,
    onSecondary = Color.White,
    secondaryContainer = DarkGray.copy(alpha = 0.1f),
    onSecondaryContainer = DarkGray,
    background = LightGray,
    onBackground = DarkGray,
    surface = Color.White,
    onSurface = DarkGray,
    error = ErrorRed,
    onError = Color.White
)

private val DarkColors = darkColorScheme(
    primary = PrimaryRed,
    onPrimary = Color.White,
    primaryContainer = PrimaryRed.copy(alpha = 0.2f),
    onPrimaryContainer = PrimaryRed,
    secondary = Color.LightGray,
    onSecondary = DarkGray,
    secondaryContainer = Color.LightGray.copy(alpha = 0.1f),
    onSecondaryContainer = Color.LightGray,
    background = DarkGray,
    onBackground = Color.LightGray,
    surface = Color(0xFF1E1E1E),
    onSurface = Color.LightGray,
    error = ErrorRed,
    onError = Color.White
)

@Composable
fun EnLasNubesTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
