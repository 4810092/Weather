package uz.ganikhodjaev.weather.shared.review

import android.content.Context
import com.google.android.play.core.review.ReviewManagerFactory
import java.util.concurrent.atomic.AtomicBoolean
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun considerReviewPrompt(
    platformContext: PlatformContext,
    successfulForecastId: Long
) {
    val context = platformContext.applicationContext
    val appVersion = runCatching {
        context.packageManager.getPackageInfo(context.packageName, 0).versionName
    }.getOrNull().orEmpty()
    if (appVersion.isBlank()) return

    val preferences = context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
    val decision = ReviewPromptPolicy.recordSuccessfulForecast(
        currentState = preferences.readReviewPromptPolicyState(),
        appVersion = appVersion,
        forecastId = successfulForecastId,
        localDay = currentLocalCalendarDay()
    )
    preferences.writeReviewPromptPolicyState(decision.state)
    if (!decision.shouldRequestReview || !reviewRequestInFlight.compareAndSet(false, true)) return

    val manager = ReviewManagerFactory.create(platformContext.requireActivity())
    manager.requestReviewFlow().addOnCompleteListener { requestTask ->
        if (!requestTask.isSuccessful) {
            reviewRequestInFlight.set(false)
            return@addOnCompleteListener
        }
        manager.launchReviewFlow(platformContext.requireActivity(), requestTask.result)
            .addOnCompleteListener { launchTask ->
                if (launchTask.isSuccessful) {
                    val latest = preferences.readReviewPromptPolicyState()
                    preferences.writeReviewPromptPolicyState(
                        ReviewPromptPolicy.markRequestSucceeded(latest, appVersion)
                    )
                }
                reviewRequestInFlight.set(false)
            }
    }
}

private fun android.content.SharedPreferences.readReviewPromptPolicyState() =
    ReviewPromptPolicyState(
        trackedVersion = getString(KEY_TRACKED_VERSION, "").orEmpty(),
        successfulForecastCount = getInt(KEY_SUCCESSFUL_FORECAST_COUNT, 0),
        successfulLocalDays = getString(KEY_SUCCESSFUL_LOCAL_DAYS, "")
            .orEmpty()
            .split(DAY_SEPARATOR)
            .filter(String::isNotBlank)
            .toSet(),
        lastCountedForecastId = getLong(KEY_LAST_COUNTED_FORECAST_ID, NO_FORECAST_ID)
            .takeUnless { it == NO_FORECAST_ID },
        successfullyRequestedVersion = getString(KEY_REVIEWED_VERSION, null)
    )

private fun android.content.SharedPreferences.writeReviewPromptPolicyState(
    state: ReviewPromptPolicyState
) {
    edit()
        .putString(KEY_TRACKED_VERSION, state.trackedVersion)
        .putInt(KEY_SUCCESSFUL_FORECAST_COUNT, state.successfulForecastCount)
        .putString(KEY_SUCCESSFUL_LOCAL_DAYS, state.successfulLocalDays.joinToString(DAY_SEPARATOR))
        .putLong(KEY_LAST_COUNTED_FORECAST_ID, state.lastCountedForecastId ?: NO_FORECAST_ID)
        .putString(KEY_REVIEWED_VERSION, state.successfullyRequestedVersion)
        .apply()
}

private val reviewRequestInFlight = AtomicBoolean(false)
private const val PREFERENCES_NAME = "nimbo_review_policy"
private const val KEY_TRACKED_VERSION = "tracked_version"
private const val KEY_SUCCESSFUL_FORECAST_COUNT = "successful_forecast_count"
private const val KEY_SUCCESSFUL_LOCAL_DAYS = "successful_local_days"
private const val KEY_LAST_COUNTED_FORECAST_ID = "last_counted_forecast_id"
private const val KEY_REVIEWED_VERSION = "reviewed_version"
private const val DAY_SEPARATOR = "|"
private const val NO_FORECAST_ID = Long.MIN_VALUE
