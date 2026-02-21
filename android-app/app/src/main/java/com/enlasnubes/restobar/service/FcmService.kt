package com.enlasnubes.restobar.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.enlasnubes.restobar.MainActivity
import com.enlasnubes.restobar.R
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

private val Context.fcmDataStore: DataStore<Preferences> by preferencesDataStore(name = "fcm_prefs")

@AndroidEntryPoint
class FcmService : FirebaseMessagingService() {

    companion object {
        const val CHANNEL_ID = "restobar_notifications"
        const val CHANNEL_NAME = "En Las Nubes Notificaciones"
        const val TAG = "FcmService"
        val FCM_TOKEN = stringPreferencesKey("fcm_token")
        
        // Token accesible globalmente para registrar en login
        var currentToken: String? = null
            private set
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        loadSavedToken()
    }

    private fun loadSavedToken() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val prefs = applicationContext.fcmDataStore.data.first()
                currentToken = prefs[FCM_TOKEN]
                currentToken?.let { Log.d(TAG, "Token loaded: ${it.take(20)}...") }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading token", e)
            }
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d(TAG, "New FCM token received: ${token.take(20)}...")
        currentToken = token
        
        // Guardar token localmente
        CoroutineScope(Dispatchers.IO).launch {
            try {
                applicationContext.fcmDataStore.edit { prefs ->
                    prefs[FCM_TOKEN] = token
                }
                Log.d(TAG, "Token saved locally")
            } catch (e: Exception) {
                Log.e(TAG, "Error saving token", e)
            }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)

        val title = message.notification?.title ?: message.data["title"] ?: "En Las Nubes"
        val body = message.notification?.body ?: message.data["body"] ?: ""
        val eventType = message.data["event_type"] ?: ""

        Log.d(TAG, "Message received: title=$title, body=$body, event=$eventType")
        showNotification(title, body, eventType)
    }

    private fun showNotification(title: String, body: String, eventType: String) {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra("event_type", eventType)
        }

        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val notificationBuilder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent)

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Notificaciones de reservas y eventos del restaurante"
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
}
