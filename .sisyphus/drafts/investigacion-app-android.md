# Investigación Profunda: App Android - En Las Nubes Restobar

**Fecha:** 2026-02-21
**Fuentes:** NotebookLM (cuadernos del proyecto), Web Search (mejores prácticas 2024-2025)

---

## 1. Autenticación JWT en Android (Jetpack Compose + Kotlin)

### Arquitectura Recomendada
- **Patrón:** MVVM + Clean Architecture
- **State Management:** StateFlow (no LiveData) - thread-safe con `.update {}`
- **Navegación:** Jetpack Navigation 2.8.0+ con type-safe navigation

### Flujo de Autenticación
```
1. Login → Access Token (15-30 min) + Refresh Token (7-30 días)
2. Cada request incluye Access Token en Authorization header
3. Si 401 → usar Refresh Token para obtener nuevo Access Token
4. Si Refresh Token expira → logout automático
```

### Dependencias Recomendadas
```kotlin
// build.gradle.kts
implementation("com.squareup.retrofit2:retrofit:2.9.0")
implementation("com.squareup.retrofit2:converter-gson:2.9.0")
implementation("androidx.security:security-crypto:1.1.0-alpha06") // EncryptedSharedPreferences
```

### Almacenamiento Seguro de Tokens
- **NO usar** SharedPreferences normales
- **USAR** EncryptedSharedPreferences de AndroidX Security
- O SharedPreferences con modo privado + cifrado adicional

### Código Ejemplo - Token Refresh
```kotlin
// AuthInterceptor.kt
class AuthInterceptor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        val token = tokenManager.getAccessToken()
        
        if (token != null) {
            request = request.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        }
        
        val response = chain.proceed(request)
        
        // Si 401, intentar refresh
        if (response.code == 401) {
            synchronized(this) {
                val newToken = refreshToken()
                if (newToken != null) {
                    request = request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    return chain.proceed(request)
                }
            }
        }
        
        return response
    }
}
```

---

## 2. RBAC (Role-Based Access Control) en Android

### Definición de Roles (Kotlin)
```kotlin
enum class UserRole {
    ADMIN,
    MANAGER,
    WAITER,
    COOK;
    
    fun canViewReservations(): Boolean = this != COOK
    fun canEditReservations(): Boolean = this in listOf(ADMIN, MANAGER)
    fun canViewKitchen(): Boolean = this in listOf(ADMIN, MANAGER, COOK)
    fun canManageUsers(): Boolean = this == ADMIN
    fun canViewDashboard(): Boolean = this in listOf(ADMIN, MANAGER)
}
```

### Navegación Dinámica por Rol
```kotlin
// DashboardScreen.kt
@Composable
fun DashboardScreen(
    userRole: UserRole,
    navController: NavController
) {
    val tabs = when (userRole) {
        UserRole.ADMIN -> listOf(
            TabItem.Dashboard,
            TabItem.Reservations,
            TabItem.Tables,
            TabItem.Kitchen,
            TabItem.Admin
        )
        UserRole.MANAGER -> listOf(
            TabItem.Dashboard,
            TabItem.Reservations,
            TabItem.Tables,
            TabItem.Kitchen
        )
        UserRole.WAITER -> listOf(
            TabItem.Reservations,
            TabItem.Tables
        )
        UserRole.COOK -> listOf(
            TabItem.Kitchen
        )
    }
    
    // Renderizar tabs según lista
}
```

### JWT Claims para Permisos
```json
{
  "sub": "user_id",
  "email": "camarero@enlasnubes.com",
  "role": "waiter",
  "permissions": ["reservations.view", "tables.view", "tables.update_status"],
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

## 3. Backend Python (FastAPI + bcrypt + Airtable)

### bcrypt con passlib
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor (default: 12, range: 4-31)
)

# Hash password
hashed = pwd_context.hash("camarero123")

# Verify password
is_valid = pwd_context.verify("camarero123", hashed)
```

### JWT con python-jose
```python
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # Usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Airtable - Rate Limits y Paginación
```
Rate Limits:
- 5 requests/segundo por base
- 50 requests/segundo por personal access token
- Si excedes: HTTP 429, esperar 30 segundos

Paginación:
- Máximo 100 records por página
- Usar parámetro `offset` para siguiente página
- pyairtable maneja automáticamente con `.all()`
```

### pyairtable - CRUD Usuarios
```python
from pyairtable import Api

api = Api(os.environ["AIRTABLE_API_KEY"])
users_table = api.table('appcUoRqLVqxQm7K2', 'tblUsuarios')

# Crear usuario
user = users_table.create({
    "Email": "nuevo@enlasnubes.com",
    "Nombre": "Juan",
    "Password_Hash": pwd_context.hash("password123"),
    "Rol": "waiter",
    "Activo": True
})

# Buscar por email
users = users_table.all(formula="{Email}='camarero@enlasnubes.com'")

# Actualizar
users_table.update(user_id, {"Rol": "manager"})

# Eliminar (soft delete recomendado)
users_table.update(user_id, {"Activo": False})
```

### Estructura Tabla Usuarios en Airtable
| Campo | Tipo | Notas |
|-------|------|-------|
| Email | Email | Único, obligatorio |
| Nombre | Single line text | Obligatorio |
| Password_Hash | Single line text | bcrypt, obligatorio |
| Rol | Single select | admin, manager, waiter, cook |
| Activo | Checkbox | Default: true |
| Telefono | Phone | Opcional |
| Device_Token | Single line text | FCM token para push |
| Ultimo_Login | DateTime | Auto-update |
| Creado | Created time | Auto |
| Modificado | Last modified | Auto |

---

## 4. Hilt - Inyección de Dependencias

### Configuración
```kotlin
// build.gradle.kts (project)
plugins {
    id("com.google.dagger.hilt.android") version "2.51" apply false
}

// build.gradle.kts (app)
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp") // Para Hilt
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.51")
    ksp("com.google.dagger:hilt-compiler:2.51")
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")
}
```

### NetworkModule
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.enlasnubes.com/api/mobile/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRestobarApi(retrofit: Retrofit): RestobarApi {
        return retrofit.create(RestobarApi::class.java)
    }
}
```

### Repository Pattern con Hilt
```kotlin
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun logout()
    suspend fun getCurrentUser(): User?
}

class AuthRepositoryImpl @Inject constructor(
    private val api: RestobarApi,
    private val tokenManager: TokenManager
) : AuthRepository {
    override suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = api.login(LoginRequest(email, password))
            tokenManager.saveTokens(response.access_token, response.refresh_token)
            Result.success(response.user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    // ... otros métodos
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        authRepositoryImpl: AuthRepositoryImpl
    ): AuthRepository
}
```

---

## 5. Casos de Éxito - Apps de Restaurantes

### FoodClick (Aggregator)
- **Usuarios:** 660 restaurantes conectados
- **Rating:** 4.7 estrellas
- **Features:** Reservas, pre-ordering, pagos contactless, propinas
- **Lecciones:**
  - Automatizar reduces errores de staff
  - Confirmaciones automáticas reducen no-shows
  - Integración POS es crítica

### SwiftServe (POS + Ordering)
- **Problema resuelto:** Colas largas, pedidos perdidos, staff overflow
- **Features:** Mobile ordering, integración POS, loyalty programs
- **Lecciones:**
  - Mobile ordering elimina necesidad de hardware caro
  - Notificaciones de estado de pedido mejoran CX
  - Inventario en tiempo real reduce desperdicio

### Patrones Comunes Exitosos
1. **Autenticación robusta:** JWT + refresh tokens
2. **Permisos granulares:** RBAC con verificación en cada request
3. **Navegación adaptativa:** UI cambia según rol
4. **Sincronización tiempo real:** WebSocket para actualizaciones
5. **Offline-first:** Caché local con Room para datos críticos
6. **Notificaciones push:** FCM para alertas de cocina y reservas

---

## 6. Recomendaciones para En Las Nubes

### Prioridad 1: Backend
1. Crear tabla Usuarios en Airtable con campos documentados
2. Implementar bcrypt con passlib (work factor 12)
3. Añadir refresh tokens al sistema JWT existente
4. Crear endpoints CRUD de usuarios (solo admin)
5. Implementar matriz de permisos RBAC en Python

### Prioridad 2: Android - Autenticación
1. Usar EncryptedSharedPreferences para tokens
2. Implementar AuthInterceptor con refresh automático
3. Crear AuthRepository con Hilt
4. StateFlow en LoginViewModel

### Prioridad 3: Android - Navegación por Rol
1. Leer rol del JWT y guardarlo en sesión
2. DashboardScreen con tabs dinámicos
3. Ocultar tabs según rol (cook solo ve cocina)
4. Verificar permisos antes de cada navegación

### Prioridad 4: Android - Gestión Usuarios
1. UserManagementScreen solo visible para admin
2. Formulario crear/editar usuario
3. Soft delete (marcar Activo=false)
4. Validar no eliminar último admin

---

## 7. Bibliotecas Recomendadas (Versiones 2024-2025)

### Android
| Biblioteca | Versión | Uso |
|------------|---------|-----|
| Hilt | 2.51 | DI |
| Retrofit | 2.9.0 | API calls |
| OkHttp | 4.12 | HTTP client |
| Security Crypto | 1.1.0-alpha06 | Token storage |
| Navigation Compose | 2.8.0+ | Type-safe nav |
| Lifecycle | 2.7.0 | ViewModel, StateFlow |
| Coroutines | 1.8.0 | Async |
| Gson | 2.10.1 | JSON |

### Python Backend
| Biblioteca | Versión | Uso |
|------------|---------|-----|
| FastAPI | 0.115+ | API framework |
| python-jose | 3.3+ | JWT |
| passlib[bcrypt] | 1.7+ | Password hashing |
| pyairtable | 2.3+ | Airtable client |
| pydantic | 2.0+ | Validation |

---

**Próximos pasos:**
1. Actualizar plan con estos hallazgos
2. Ejecutar Wave 1: Backend - Usuarios en Airtable
3. Ejecutar con Atlas (no Sisyphus) para orquestación completa
