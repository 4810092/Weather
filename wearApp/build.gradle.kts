plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.ktlint)
}

android {
    namespace = "uz.ganikhodjaev.weather.wear"
    compileSdk = 36

    defaultConfig {
        applicationId = "uz.ganikhodjaev.weather"
        minSdk = 30
        targetSdk = 36
        // Play requires a version code that is unique across every form factor.
        // Keep Wear OS in a separate range so phone and watch releases can evolve independently.
        versionCode = 1_000_008
        versionName = "1.1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation(libs.androidx.core.splashscreen)
    implementation(libs.androidx.fragment)
    implementation(libs.play.services.wearable)
}
