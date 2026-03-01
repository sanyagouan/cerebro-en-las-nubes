package com.enlasnubes.restobar.presentation.admin

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.enlasnubes.restobar.data.model.User

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserManagementScreen(
    userRol: String,
    viewModel: AdminViewModel = androidx.hilt.navigation.compose.hiltViewModel()
) {
    val uiState by viewModel.userManagementState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Gestion de Usuarios") },
                actions = {
                    IconButton(onClick = { viewModel.refreshUsers() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Actualizar")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { viewModel.showCreateUserDialog() },
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Nuevo usuario")
            }
        }
    ) { padding ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (uiState.error != null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(uiState.error!!, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { viewModel.refreshUsers() }) {
                        Text("Reintentar")
                    }
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(uiState.users) { user ->
                    UserCard(
                        user = user,
                        onEdit = { viewModel.showEditUserDialog(user) },
                        onChangePassword = { viewModel.showPasswordDialog(user) },
                        onDeactivate = { viewModel.showDeleteConfirm(user) }
                    )
                }
            }
        }

        // Dialogs
        if (uiState.showCreateDialog) {
            CreateUserDialog(
                onDismiss = { viewModel.hideCreateUserDialog() },
                onCreate = { usuario, nombre, password, rol, telefono ->
                    viewModel.createUser(usuario, nombre, password, rol, telefono)
                }
            )
        }

        uiState.showEditDialog?.let { user ->
            EditUserDialog(
                user = user,
                onDismiss = { viewModel.hideEditUserDialog() },
                onSave = { nombre, telefono, rol ->
                    viewModel.updateUser(user.id, nombre, telefono, rol)
                }
            )
        }

        uiState.showPasswordDialog?.let { user ->
            ChangePasswordDialog(
                userName = user.nombre,
                onDismiss = { viewModel.hidePasswordDialog() },
                onChange = { newPassword ->
                    viewModel.changeUserPassword(user.id, newPassword)
                }
            )
        }

        uiState.showDeleteConfirm?.let { user ->
            AlertDialog(
                onDismissRequest = { viewModel.hideDeleteConfirm() },
                title = { Text("Desactivar Usuario") },
                text = { Text("¿Seguro que quieres desactivar a ${user.nombre}? El usuario no podra acceder al sistema.") },
                confirmButton = {
                    TextButton(
                        onClick = { viewModel.deactivateUser(user.id) },
                        colors = ButtonDefaults.textButtonColors(
                            contentColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Text("Desactivar")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { viewModel.hideDeleteConfirm() }) {
                        Text("Cancelar")
                    }
                }
            )
        }
    }
}

@Composable
fun UserCard(
    user: User,
    onEdit: () -> Unit,
    onChangePassword: () -> Unit,
    onDeactivate: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = user.nombre,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    if (!user.activo) {
                        Spacer(modifier = Modifier.width(8.dp))
                        Surface(
                            color = MaterialTheme.colorScheme.errorContainer,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                text = "Inactivo",
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onErrorContainer
                            )
                        }
                    }
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "@${user.usuario}",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        color = getRolColor(user.rol),
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            text = user.rol.replaceFirstChar { it.uppercase() },
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }
            }

            Box {
                IconButton(onClick = { expanded = true }) {
                    Icon(Icons.Default.MoreVert, contentDescription = "Opciones")
                }
                DropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false }
                ) {
                    DropdownMenuItem(
                        text = { Text("Editar") },
                        onClick = {
                            expanded = false
                            onEdit()
                        },
                        leadingIcon = { Icon(Icons.Default.Edit, contentDescription = null) }
                    )
                    DropdownMenuItem(
                        text = { Text("Cambiar contrasena") },
                        onClick = {
                            expanded = false
                            onChangePassword()
                        },
                        leadingIcon = { Icon(Icons.Default.Key, contentDescription = null) }
                    )
                    if (user.activo) {
                        DropdownMenuItem(
                            text = { Text("Desactivar") },
                            onClick = {
                                expanded = false
                                onDeactivate()
                            },
                            leadingIcon = {
                                Icon(
                                    Icons.Default.Block,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.error
                                )
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun getRolColor(rol: String): androidx.compose.ui.graphics.Color {
    return when (rol) {
        "administradora" -> MaterialTheme.colorScheme.errorContainer
        "encargada" -> MaterialTheme.colorScheme.primaryContainer
        "camarero" -> MaterialTheme.colorScheme.secondaryContainer
        "cocina" -> MaterialTheme.colorScheme.tertiaryContainer
        else -> MaterialTheme.colorScheme.surfaceVariant
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateUserDialog(
    onDismiss: () -> Unit,
    onCreate: (usuario: String, nombre: String, password: String, rol: String, telefono: String?) -> Unit
) {
    var usuario by remember { mutableStateOf("") }
    var nombre by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var rol by remember { mutableStateOf("camarero") }
    var telefono by remember { mutableStateOf("") }
    var passwordError by remember { mutableStateOf<String?>(null) }
    var expanded by remember { mutableStateOf(false) }

    val roles = listOf("administradora", "encargada", "camarero", "cocina")

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Nuevo Usuario") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = usuario,
                    onValueChange = { usuario = it },
                    label = { Text("Usuario") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                OutlinedTextField(
                    value = nombre,
                    onValueChange = { nombre = it },
                    label = { Text("Nombre completo") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                OutlinedTextField(
                    value = password,
                    onValueChange = { 
                        password = it
                        passwordError = null
                    },
                    label = { Text("Contrasena") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    isError = passwordError != null,
                    supportingText = passwordError?.let { { Text(it) } },
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
                )
                OutlinedTextField(
                    value = confirmPassword,
                    onValueChange = { 
                        confirmPassword = it
                        passwordError = null
                    },
                    label = { Text("Confirmar contrasena") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    isError = passwordError != null,
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
                )
                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { expanded = it }
                ) {
                    OutlinedTextField(
                        value = rol.replaceFirstChar { it.uppercase() },
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Rol") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        roles.forEach { role ->
                            DropdownMenuItem(
                                text = { Text(role.replaceFirstChar { it.uppercase() }) },
                                onClick = {
                                    rol = role
                                    expanded = false
                                }
                            )
                        }
                    }
                }
                OutlinedTextField(
                    value = telefono,
                    onValueChange = { telefono = it },
                    label = { Text("Telefono (opcional)") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    when {
                        password.length < 6 -> passwordError = "Minimo 6 caracteres"
                        password != confirmPassword -> passwordError = "Las contrasenas no coinciden"
                        usuario.isNotBlank() && nombre.isNotBlank() && password.isNotBlank() -> {
                            onCreate(usuario, nombre, password, rol, telefono.ifBlank { null })
                        }
                    }
                },
                enabled = usuario.isNotBlank() && nombre.isNotBlank() && password.isNotBlank()
            ) {
                Text("Crear")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EditUserDialog(
    user: User,
    onDismiss: () -> Unit,
    onSave: (nombre: String, telefono: String?, rol: String) -> Unit
) {
    var nombre by remember { mutableStateOf(user.nombre) }
    var telefono by remember { mutableStateOf(user.telefono ?: "") }
    var rol by remember { mutableStateOf(user.rol) }
    var expanded by remember { mutableStateOf(false) }

    val roles = listOf("administradora", "encargada", "camarero", "cocina")

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Editar Usuario") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = nombre,
                    onValueChange = { nombre = it },
                    label = { Text("Nombre completo") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                OutlinedTextField(
                    value = telefono,
                    onValueChange = { telefono = it },
                    label = { Text("Telefono") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { expanded = it }
                ) {
                    OutlinedTextField(
                        value = rol.replaceFirstChar { it.uppercase() },
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Rol") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        roles.forEach { role ->
                            DropdownMenuItem(
                                text = { Text(role.replaceFirstChar { it.uppercase() }) },
                                onClick = {
                                    rol = role
                                    expanded = false
                                }
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onSave(nombre, telefono.ifBlank { null }, rol) },
                enabled = nombre.isNotBlank()
            ) {
                Text("Guardar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}

@Composable
fun ChangePasswordDialog(
    userName: String,
    onDismiss: () -> Unit,
    onChange: (newPassword: String) -> Unit
) {
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Cambiar Contrasena") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Nueva contrasena para: $userName")
                OutlinedTextField(
                    value = password,
                    onValueChange = { 
                        password = it
                        error = null
                    },
                    label = { Text("Nueva contrasena") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    isError = error != null,
                    supportingText = error?.let { { Text(it) } },
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
                )
                OutlinedTextField(
                    value = confirmPassword,
                    onValueChange = { 
                        confirmPassword = it
                        error = null
                    },
                    label = { Text("Confirmar contrasena") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    isError = error != null,
                    visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    when {
                        password.length < 6 -> error = "Minimo 6 caracteres"
                        password != confirmPassword -> error = "Las contrasenas no coinciden"
                        else -> onChange(password)
                    }
                },
                enabled = password.isNotBlank()
            ) {
                Text("Cambiar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}
