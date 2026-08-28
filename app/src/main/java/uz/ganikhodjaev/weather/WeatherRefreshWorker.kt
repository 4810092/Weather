package uz.ganikhodjaev.weather

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.ListenableWorker
import androidx.work.WorkerParameters
import uz.ganikhodjaev.weather.shared.BackgroundRefreshOutcome
import uz.ganikhodjaev.weather.shared.BackgroundWeatherUpdater
import uz.ganikhodjaev.weather.shared.PlatformContext

class WeatherRefreshWorker(appContext: Context, workerParameters: WorkerParameters) :
    CoroutineWorker(appContext, workerParameters) {
    override suspend fun doWork(): Result {
        val updater = BackgroundWeatherUpdater(PlatformContext(applicationContext))
        return updater.refreshOutcome().toWorkerResult()
    }
}

internal fun BackgroundRefreshOutcome.toWorkerResult(): ListenableWorker.Result = when (this) {
    BackgroundRefreshOutcome.Updated,
    BackgroundRefreshOutcome.NothingToRefresh -> ListenableWorker.Result.success()
    BackgroundRefreshOutcome.TransientFailure -> ListenableWorker.Result.retry()
    BackgroundRefreshOutcome.PermanentFailure -> ListenableWorker.Result.failure()
}
