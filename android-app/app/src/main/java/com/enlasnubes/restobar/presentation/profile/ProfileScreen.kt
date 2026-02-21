package com.enlasnubes.restobar.presentation.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    userRol: String,
    userName: String,
    onBack: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var showChangePasswordDialog by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        viewModel.loadProfile()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mi Perfil") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Volver")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Avatar
            Surface(
                modifier = Modifier.size(100.dp),
                shape = CircleShape,
                color = MaterialTheme.colorScheme.primaryContainer
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        modifier = Modifier.size(50.dp),
                        tint = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Nombre
            Text(
                text = uiState.user?.nombre ?: userName,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(4.dp))

            // Rol
            Surface(
                shape = MaterialTheme.shapes.small,
                color = when (userRol) {
                    "administradora" -> MaterialTheme.colorScheme.errorContainer
                    "encargada" -> MaterialTheme.colorScheme.tertiaryContainer
                    "camarero" -> MaterialTheme.colorScheme.primaryContainer
                    "cocina" -> MaterialTheme.colorScheme.secondaryContainer
                    else -> MaterialTheme.colorScheme.surfaceVariant
                }
            ) {
                Text(
                    text = getRoleDisplayName(userRol),
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.labelLarge
                )
            }

            Spacer(modifier = Modifier.height(32.dp))

            // Información del usuario
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Informacion",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(16.dp))

                    ProfileInfoRow(
                        icon = Icons.Default.Person,
                        label = "Usuario",
                        value = uiState.user?.usuario ?: "-"
                    )

                    if (!uiState.user?.telefono.isNullOrBlank()) {
                        ProfileInfoRow(
                            icon = Icons.Default.Phone,
                            label = "Telefono",
                            value = uiState.user?.telefono ?: ""
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Acciones
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column {
                    ProfileActionItem(
                        icon = Icons.Default.Lock,
                        title = "Cambiar contrasena",
                        subtitle = "Actualiza tu contrasena de acceso",
                        onClick = { showChangePasswordDialog = true }
                    )
                }
            }

            // Mensaje de éxito
            if (uiState.successMessage != null) {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = uiState.successMessage!!,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }
            }

            // Error
            if (uiState.error != null) {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Error,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = uiState.error!!,
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }
        }
    }

    // Dialog para cambiar contraseña
    if (showChangePasswordDialog) {
        ChangePasswordDialog(
            isLoading = uiState.isLoading,
            onDismiss = { 
                showChangePasswordDialog = false
                viewModel.clearMessages()
            },
            onConfirm = { currentPassword, newPassword ->
                viewModel.changePassword(currentPassword, newPassword)
            }
        )
    }
}

@Composable
private fun ProfileInfoRow(
    icon: ImageVector,
    label: String,
    value: String
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
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

@Composable
private fun ProfileActionItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ChangePasswordDialog(
    isLoading: Boolean,
    onDismiss: () -> Unit,
    onConfirm: (currentPassword: String, newPassword: String) -> Unit
) {
    var currentPassword by remember { mutableStateOf("") }
    var newPassword by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var passwordMismatch by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Cambiar contrasena") },
        text = {
            Column {
                OutlinedTextField(
                    value = currentPassword,
                    onValueChange = { currentPassword = it },
                    label = { Text("Contrasena actual") },
                    singleLine = true,
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = newPassword,
                    onValueChange = { 
                        newPassword = it
                        passwordMismatch = confirmPassword.isNotBlank() && it != confirmPassword
                    },
                    label = { Text("Nueva contrasena") },
                    singleLine = true,
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = confirmPassword,
                    onValueChange = { 
                        confirmPassword = it
                        passwordMismatch = newPassword.isNotBlank() && it != newPassword
                    },
                    label = { Text("Confirmar nueva contrasena") },
                    singleLine = true,
                    isError = passwordMismatch,
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
                    supportingText = if (passwordMismatch) {
                        { Text("Las contrasenas no coinciden") }
                    } else null,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    if (!passwordMismatch && newPassword.isNotBlank()) {
                        onConfirm(currentPassword, newPassword)
                    }
                },
                enabled = !isLoading && currentPassword.isNotBlank() && newPassword.isNotBlank() && !passwordMismatch
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Guardar")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}

private fun getRoleDisplayName(rol: String): String {
    return when (rol) {
        "administradora" -> "Administradora"
        "encargada" -> "Encargada"
        "camarero" -> "Camarero"
        "cocina" -> "Cocina"
        else -> rol.replaceFirstChar { it.uppercase() }
    }
}
