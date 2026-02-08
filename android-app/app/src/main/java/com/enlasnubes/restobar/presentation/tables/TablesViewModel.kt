package com.enlasnubes.restobar.presentation.tables

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.enlasnubes.restobar.data.model.Table
import com.enlasnubes.restobar.data.repository.RestobarRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class TablesUiState(
    val tables: List<Table> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class TablesViewModel @Inject constructor(
    private val repository: RestobarRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TablesUiState())
    val uiState: StateFlow<TablesUiState> = _uiState.asStateFlow()

    fun loadTables() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            repository.getTables()
                .onSuccess { tables ->
                    _uiState.update {
                        it.copy(
                            tables = tables,
                            isLoading = false
                        )
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = error.message
                        )
                    }
                }
        }
    }

    fun updateTableStatus(tableId: String, status: String) {
        viewModelScope.launch {
            repository.updateTableStatus(tableId, status)
                .onSuccess {
                    loadTables() // Refresh
                }
        }
    }
}
