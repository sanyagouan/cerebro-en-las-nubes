package com.enlasnubes.restobar.presentation.waitlist

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.enlasnubes.restobar.data.model.WaitlistCreateRequest
import com.enlasnubes.restobar.data.model.WaitlistResponse
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WaitlistScreen(
    viewModel: WaitlistViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var showAddDialog by remember { mutableStateOf(false) }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(onClick = { showAddDialog = true }) {
                Icon(Icons.Default.Add, contentDescription = "Añadir a lista")
            }
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading && uiState.entries.isEmpty() -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                uiState.error != null -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { viewModel.dismissError(); viewModel.loadWaitlist() }) {
                            Text("Reintentar")
                        }
                    }
                }
                uiState.entries.isEmpty() -> {
                    Text(
                        "No hay nadie en la lista de espera.",
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                else -> {
                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(uiState.entries) { entry ->
                            WaitlistCard(
                                entry = entry,
                                onNotify = { viewModel.notifyEntry(entry.id) },
                                onRemove = { viewModel.removeEntry(entry.id) }
                            )
                        }
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        WaitlistAddDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { request ->
                viewModel.addToWaitlist(request)
                showAddDialog = false
            }
        )
    }
}

@Composable
private fun WaitlistCard(
    entry: WaitlistResponse,
    onNotify: () -> Unit,
    onRemove: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "${entry.posicion ?: "?"} - ${entry.nombreCliente}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${entry.numPersonas} pax • Llega: ${entry.hora}",
                    style = MaterialTheme.typography.bodyMedium
                )
                if (!entry.notas.isNullOrBlank()) {
                    Text(
                        text = "Notas: ${entry.notas}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }

            Column(horizontalAlignment = Alignment.End) {
                Button(
                    onClick = onNotify,
                    modifier = Modifier.height(36.dp)
                ) {
                    Icon(Icons.Default.NotificationsActive, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Avisar", style = MaterialTheme.typography.labelMedium)
                }
                TextButton(
                    onClick = onRemove,
                    modifier = Modifier.height(36.dp),
                    colors = ButtonDefaults.textButtonColors(contentColor = MaterialTheme.colorScheme.error)
                ) {
                    Text("Sentar/Quitar", style = MaterialTheme.typography.labelMedium)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun WaitlistAddDialog(
    onDismiss: () -> Unit,
    onConfirm: (WaitlistCreateRequest) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var pax by remember { mutableStateOf("2") }
    var notes by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Añadir a Espera") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Nombre") },
                    singleLine = true
                )
                OutlinedTextField(
                    value = phone,
                    onValueChange = { phone = it },
                    label = { Text("Teléfono") },
                    singleLine = true
                )
                OutlinedTextField(
                    value = pax,
                    onValueChange = { pax = it },
                    label = { Text("Pax (Personas)") },
                    singleLine = true
                )
                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text("Notas / Alergias") },
                    maxLines = 2
                )
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    onConfirm(
                        WaitlistCreateRequest(
                            nombreCliente = name,
                            telefonoCliente = phone,
                            fecha = LocalDate.now().toString(),
                            hora = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm")),
                            numPersonas = pax.toIntOrNull() ?: 2,
                            notas = notes.takeIf { it.isNotBlank() }
                        )
                    )
                },
                enabled = name.isNotBlank() && phone.isNotBlank()
            ) {
                Text("Añadir")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}
