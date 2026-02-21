package com.enlasnubes.restobar.data.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.enlasnubes.restobar.data.model.User
import com.enlasnubes.restobar.data.model.UserRole
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

@Singleton
class AuthRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val dataStore = context.dataStore

    companion object {
        val ACCESS_TOKEN = stringPreferencesKey("access_token")
        val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
        val USER_ID = stringPreferencesKey("user_id")
        val USER_USUARIO = stringPreferencesKey("user_usuario")
        val USER_NAME = stringPreferencesKey("user_name")
        val USER_ROLE = stringPreferencesKey("user_role")
    }

    val authToken: Flow<String?> = dataStore.data.map { it[ACCESS_TOKEN] }
    val refreshToken: Flow<String?> = dataStore.data.map { it[REFRESH_TOKEN] }
    
    val currentUser: Flow<User?> = dataStore.data.map { prefs ->
        val userId = prefs[USER_ID] ?: return@map null
        val usuario = prefs[USER_USUARIO] ?: return@map null
        val nombre = prefs[USER_NAME] ?: return@map null
        val rol = prefs[USER_ROLE] ?: return@map null
        
        User(
            id = userId,
            usuario = usuario,
            nombre = nombre,
            rol = rol
        )
    }

    suspend fun saveAuthData(
        accessToken: String,
        refreshToken: String,
        user: User
    ) {
        dataStore.edit { prefs ->
            prefs[ACCESS_TOKEN] = accessToken
            prefs[REFRESH_TOKEN] = refreshToken
            prefs[USER_ID] = user.id
            prefs[USER_USUARIO] = user.usuario
            prefs[USER_NAME] = user.nombre
            prefs[USER_ROLE] = user.rol
        }
    }

    suspend fun clearAuthData() {
        dataStore.edit { it.clear() }
    }

    suspend fun getAccessToken(): String? {
        return dataStore.data.first()[ACCESS_TOKEN]
    }

    suspend fun getCurrentUser(): User? {
        return currentUser.first()
    }

    fun getAccessTokenBlocking(): String? {
        return runBlocking { getAccessToken() }
    }
}
