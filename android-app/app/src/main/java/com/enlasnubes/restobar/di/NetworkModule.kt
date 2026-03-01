package com.enlasnubes.restobar.di

import com.enlasnubes.restobar.BuildConfig
import com.enlasnubes.restobar.data.remote.RestobarApi
import com.enlasnubes.restobar.data.websocket.WebSocketService
import com.enlasnubes.restobar.data.websocket.WebSocketManager
import com.enlasnubes.restobar.data.repository.AuthRepository
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import dagger.Lazy
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .registerTypeAdapter(LocalDate::class.java, object : com.google.gson.JsonDeserializer<LocalDate> {
                override fun deserialize(json: com.google.gson.JsonElement, type: java.lang.reflect.Type, context: com.google.gson.JsonDeserializationContext): LocalDate {
                    return LocalDate.parse(json.asString)
                }
            })
            .registerTypeAdapter(LocalDate::class.java, object : com.google.gson.JsonSerializer<LocalDate> {
                override fun serialize(src: LocalDate, typeOfSrc: java.lang.reflect.Type, context: com.google.gson.JsonSerializationContext): com.google.gson.JsonElement {
                    return com.google.gson.JsonPrimitive(src.format(DateTimeFormatter.ISO_LOCAL_DATE))
                }
            })
            .registerTypeAdapter(LocalTime::class.java, object : com.google.gson.JsonDeserializer<LocalTime> {
                override fun deserialize(json: com.google.gson.JsonElement, type: java.lang.reflect.Type, context: com.google.gson.JsonDeserializationContext): LocalTime {
                    return LocalTime.parse(json.asString)
                }
            })
            .registerTypeAdapter(LocalTime::class.java, object : com.google.gson.JsonSerializer<LocalTime> {
                override fun serialize(src: LocalTime, typeOfSrc: java.lang.reflect.Type, context: com.google.gson.JsonSerializationContext): com.google.gson.JsonElement {
                    return com.google.gson.JsonPrimitive(src.format(DateTimeFormatter.ISO_LOCAL_TIME))
                }
            })
            .registerTypeAdapter(Instant::class.java, object : com.google.gson.JsonDeserializer<Instant> {
                override fun deserialize(json: com.google.gson.JsonElement, type: java.lang.reflect.Type, context: com.google.gson.JsonDeserializationContext): Instant {
                    return Instant.parse(json.asString)
                }
            })
            .registerTypeAdapter(Instant::class.java, object : com.google.gson.JsonSerializer<Instant> {
                override fun serialize(src: Instant, typeOfSrc: java.lang.reflect.Type, context: com.google.gson.JsonSerializationContext): com.google.gson.JsonElement {
                    return com.google.gson.JsonPrimitive(src.toString())
                }
            })
            .create()
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(authRepository: Lazy<AuthRepository>): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BODY
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            })
            .addInterceptor { chain ->
                val token = authRepository.get().getAccessTokenBlocking()
                val requestBuilder = chain.request().newBuilder()
                if (!token.isNullOrBlank()) {
                    requestBuilder.addHeader("Authorization", "Bearer $token")
                }
                chain.proceed(requestBuilder.build())
            }
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, gson: Gson): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }

    @Provides
    @Singleton
    fun provideRestobarApi(retrofit: Retrofit): RestobarApi {
        return retrofit.create(RestobarApi::class.java)
    }

    @Provides
    @Singleton
    fun provideWebSocketService(manager: WebSocketManager): WebSocketService {
        return manager
    }
}
