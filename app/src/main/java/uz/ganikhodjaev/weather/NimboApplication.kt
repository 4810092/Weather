package uz.ganikhodjaev.weather

import android.app.Application
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

class NimboApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
        val request = PeriodicWorkRequestBuilder<WeatherRefreshWorker>(
            BACKGROUND_REFRESH_INTERVAL_MINUTES,
            TimeUnit.MINUTES
        ).setConstraints(constraints).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            BACKGROUND_REFRESH_WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }

    private companion object {
        const val BACKGROUND_REFRESH_INTERVAL_MINUTES = 30L
        const val BACKGROUND_REFRESH_WORK_NAME = "nimbo_weather_refresh"
    }
}
