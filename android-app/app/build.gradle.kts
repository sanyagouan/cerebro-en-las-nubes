plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt.android)
}

android {
    namespace = "com.enlasnubes.restobar"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.enlasnubes.restobar"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        // API Base URL - ACTUALIZAR con URL real del servidor Coolify
        // Ejemplo: "https://api.enlasnubes.com"
        buildConfigField("String", "API_BASE_URL", "\"https://UPDATE_WITH_YOUR_COOLIFY_DOMAIN.com\"")
        buildConfigField("String", "WS_BASE_URL", "\"wss://UPDATE_WITH_YOUR_COOLIFY_DOMAIN.com\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")
            buildConfigField("String", "WS_BASE_URL", "\"ws://10.0.2.2:8000\"")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.7"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Core
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    
    // Compose BOM
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.bundles.compose)
    implementation(libs.androidx.navigation.compose)
    implementation("androidx.compose.material:material:1.6.0") // PullRefresh
    
    // Hilt
    implementation(libs.bundles.hilt)
    kapt(libs.hilt.compiler)
    
    // Networking
    implementation(libs.bundles.retrofit)
    implementation(libs.scarlet)
    implementation(libs.scarlet.websocket)
    implementation(libs.scarlet.gson)
    
    // Coroutines
    implementation(libs.kotlinx.coroutines)
    
    // Image Loading
    implementation(libs.coil)
    
    // DataStore
    implementation(libs.androidx.datastore)
    
    // Firebase
    implementation(libs.firebase.messaging)
    
    // Testing
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
