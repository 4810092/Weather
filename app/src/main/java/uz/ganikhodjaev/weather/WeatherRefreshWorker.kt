package uz.ganikhodjaev.weather

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import uz.ganikhodjaev.weather.shared.BackgroundWeatherUpdater
import uz.ganikhodjaev.weather.shared.PlatformContext

class WeatherRefreshWorker(appContext: Context, workerParameters: WorkerParameters) :
    CoroutineWorker(appContext, workerParameters) {
    override suspend fun doWork(): Result {
        BackgroundWeatherUpdater(PlatformContext(applicationContext)).refresh()
        return Result.success()
    }
}
