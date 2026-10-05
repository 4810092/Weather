plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.ktlint)
}

android {
    namespace = "uz.ganikhodjaev.weather.wear"
    compileSdk = 37

    defaultConfig {
        applicationId = "uz.ganikhodjaev.weather"
        minSdk = 30
        targetSdk = 36
        // Play requires a version code that is unique across every form factor.
        // Keep Wear OS in a separate range so phone and watch releases can evolve independently.
        versionCode = 1_000_013
        versionName = "1.1.0"
    }

    buildTypes {
        debug {
            // Data Layer requires the same package and signing identity as the phone.
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-dev"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    sourceSets {
        getByName("main").kotlin.directories.add(
            rootProject.layout.projectDirectory
                .dir("androidSurfaceContract/src/main/kotlin")
                .asFile.path
        )
        getByName("test").kotlin.directories.add(
            rootProject.layout.projectDirectory
                .dir("androidSurfaceContract/src/test/kotlin")
                .asFile.path
        )
    }
}

dependencies {
    implementation(libs.androidx.core.splashscreen)
    implementation(libs.androidx.fragment)
    implementation(libs.play.services.wearable)
    testImplementation(kotlin("test-junit"))
}
