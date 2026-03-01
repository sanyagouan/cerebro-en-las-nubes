import java.util.Properties
import java.io.FileInputStream
import java.io.File

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.ksp)
    alias(libs.plugins.hilt.android)
    alias(libs.plugins.google.services)
}

// Cargar configuración de firma
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("keystore.properties")
if (keystorePropertiesFile.exists()) {
    keystorePropertiesFile.inputStream().use { input ->
        keystoreProperties.load(input)
    }
}

android {
    namespace = "com.enlasnubes.restobar"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.enlasnubes.restobar"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        buildConfigField("String", "API_BASE_URL", "\"https://go84sgscs4ckcs08wog84o0o.app.generaia.site\"")
        buildConfigField("String", "WS_BASE_URL", "\"wss://go84sgscs4ckcs08wog84o0o.app.generaia.site\"")
    }

    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties.getProperty("keyAlias")
            keyPassword = keystoreProperties.getProperty("keyPassword")
            storePassword = keystoreProperties.getProperty("storePassword")
            
            val storeFilePath = keystoreProperties.getProperty("storeFile")
            if (storeFilePath != null) {
                val kFile = rootProject.file(storeFilePath)
                if (kFile.exists()) {
                    storeFile = kFile
                }
            }
        }
    }

    // Fix for Android Studio injected 'externalOverride' config
    // This forces the injected config to use the absolute path relative to project root
    afterEvaluate {
        signingConfigs.findByName("externalOverride")?.let { config ->
            val storeFilePath = keystoreProperties.getProperty("storeFile")
            if (storeFilePath != null) {
                config.storeFile = rootProject.file(storeFilePath)
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            isShrinkResources = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
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
        kotlinCompilerExtensionVersion = "1.5.8"
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
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.activity.compose)
    
    // Compose BOM
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.bundles.compose)
    implementation(libs.androidx.navigation.compose)
    implementation("androidx.compose.material:material:1.6.0") // PullRefresh
    
    // Hilt
    implementation(libs.bundles.hilt)
    ksp(libs.hilt.compiler)
    
    // Networking
    implementation(libs.bundles.retrofit)
    // WebSocket
    implementation(libs.bundles.scarlet)
    
    // Coroutines
    implementation(libs.kotlinx.coroutines)
    
    // Image Loading
    implementation(libs.coil)
    
    // DataStore
    implementation(libs.androidx.datastore)
    
    // Firebase
    implementation(platform(libs.firebase.bom))
    implementation(libs.firebase.messaging)
    implementation(libs.firebase.analytics)
    
    // Testing
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}