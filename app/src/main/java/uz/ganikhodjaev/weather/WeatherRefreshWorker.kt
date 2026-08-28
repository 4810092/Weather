package uz.ganikhodjaev.weather

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import uz.ganikhodjaev.weather.shared.BackgroundRefreshOutcome
import uz.ganikhodjaev.weather.shared.BackgroundWeatherUpdater
import uz.ganikhodjaev.weather.shared.PlatformContext

class WeatherRefreshWorker(appContext: Context, workerParameters: WorkerParameters) :
    CoroutineWorker(appContext, workerParameters) {
    override suspend fun doWork(): Result =
        when (BackgroundWeatherUpdater(PlatformContext(applicationContext)).refreshOutcome()) {
            BackgroundRefreshOutcome.Updated,
            BackgroundRefreshOutcome.NothingToRefresh -> Result.success()
            BackgroundRefreshOutcome.TransientFailure -> Result.retry()
            BackgroundRefreshOutcome.PermanentFailure -> Result.failure()
        }
}
