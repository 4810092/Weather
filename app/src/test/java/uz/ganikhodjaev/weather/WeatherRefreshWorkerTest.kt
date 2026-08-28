package uz.ganikhodjaev.weather

import androidx.work.ListenableWorker
import kotlin.test.Test
import kotlin.test.assertEquals
import uz.ganikhodjaev.weather.shared.BackgroundRefreshOutcome

class WeatherRefreshWorkerTest {
    @Test
    fun transientFailureRequestsWorkManagerRetry() {
        assertEquals(
            ListenableWorker.Result.retry(),
            BackgroundRefreshOutcome.TransientFailure.toWorkerResult()
        )
    }

    @Test
    fun permanentFailureStopsWithFailure() {
        assertEquals(
            ListenableWorker.Result.failure(),
            BackgroundRefreshOutcome.PermanentFailure.toWorkerResult()
        )
    }

    @Test
    fun updatedAndNothingToRefreshBothCompleteSuccessfully() {
        listOf(
            BackgroundRefreshOutcome.Updated,
            BackgroundRefreshOutcome.NothingToRefresh
        ).forEach { outcome ->
            assertEquals(ListenableWorker.Result.success(), outcome.toWorkerResult())
        }
    }
}
