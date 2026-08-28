package uz.ganikhodjaev.weather.shared.review

import platform.Foundation.NSBundle
import platform.Foundation.NSNotificationCenter
import platform.Foundation.NSUserDefaults
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun considerReviewPrompt(
    platformContext: PlatformContext,
    successfulForecastId: Long
) {
    val appVersion = NSBundle.mainBundle.objectForInfoDictionaryKey(
        "CFBundleShortVersionString"
    ) as? String ?: return
    val preferences = NSUserDefaults(suiteName = APP_GROUP)
    val decision = ReviewPromptPolicy.recordSuccessfulForecast(
        currentState = preferences.readReviewPromptPolicyState(),
        appVersion = appVersion,
        forecastId = successfulForecastId,
        localDay = currentLocalCalendarDay()
    )
    preferences.writeReviewPromptPolicyState(decision.state)
    if (decision.shouldRequestReview) {
        NSNotificationCenter.defaultCenter.postNotificationName(
            aName = REVIEW_MILESTONE_NOTIFICATION,
            `object` = null
        )
    }
}

private fun NSUserDefaults.readReviewPromptPolicyState() = ReviewPromptPolicyState(
    trackedVersion = stringForKey(KEY_TRACKED_VERSION).orEmpty(),
    successfulForecastCount = integerForKey(KEY_SUCCESSFUL_FORECAST_COUNT).toInt(),
    successfulLocalDays = stringForKey(KEY_SUCCESSFUL_LOCAL_DAYS)
        .orEmpty()
        .split(DAY_SEPARATOR)
        .filter(String::isNotBlank)
        .toSet(),
    lastCountedForecastId = objectForKey(KEY_LAST_COUNTED_FORECAST_ID)?.let {
        integerForKey(KEY_LAST_COUNTED_FORECAST_ID)
    },
    successfullyRequestedVersion = stringForKey(KEY_REVIEWED_VERSION)
)

private fun NSUserDefaults.writeReviewPromptPolicyState(state: ReviewPromptPolicyState) {
    setObject(state.trackedVersion, forKey = KEY_TRACKED_VERSION)
    setInteger(state.successfulForecastCount.toLong(), forKey = KEY_SUCCESSFUL_FORECAST_COUNT)
    setObject(
        state.successfulLocalDays.joinToString(DAY_SEPARATOR),
        forKey = KEY_SUCCESSFUL_LOCAL_DAYS
    )
    state.lastCountedForecastId?.let {
        setInteger(it, forKey = KEY_LAST_COUNTED_FORECAST_ID)
    } ?: removeObjectForKey(KEY_LAST_COUNTED_FORECAST_ID)
    state.successfullyRequestedVersion?.let {
        setObject(it, forKey = KEY_REVIEWED_VERSION)
    } ?: removeObjectForKey(KEY_REVIEWED_VERSION)
}

private const val APP_GROUP = "group.uz.ganikhodjaev.weather"
private const val REVIEW_MILESTONE_NOTIFICATION = "NimboReviewMilestone"
private const val KEY_TRACKED_VERSION = "tracked_version"
private const val KEY_SUCCESSFUL_FORECAST_COUNT = "successful_forecast_count"
private const val KEY_SUCCESSFUL_LOCAL_DAYS = "successful_local_days"
private const val KEY_LAST_COUNTED_FORECAST_ID = "last_counted_forecast_id"
private const val KEY_REVIEWED_VERSION = "reviewed_version"
private const val DAY_SEPARATOR = "|"
