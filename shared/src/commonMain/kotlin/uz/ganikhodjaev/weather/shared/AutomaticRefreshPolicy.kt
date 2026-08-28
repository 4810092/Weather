package uz.ganikhodjaev.weather.shared

import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal const val AUTOMATIC_REFRESH_MIN_AGE_SECONDS = 60L * 60L

internal fun WeatherSnapshot.isAutomaticRefreshDue(nowEpochSeconds: Long): Boolean {
    if (fetchedAtEpochSeconds <= 0L) return true
    if (nowEpochSeconds < fetchedAtEpochSeconds) return true
    return nowEpochSeconds - fetchedAtEpochSeconds >= AUTOMATIC_REFRESH_MIN_AGE_SECONDS
}

internal fun isAutomaticRefreshAttemptDue(
    lastAttemptEpochSeconds: Long?,
    nowEpochSeconds: Long
): Boolean {
    if (lastAttemptEpochSeconds == null || lastAttemptEpochSeconds <= 0L) return true
    if (nowEpochSeconds < lastAttemptEpochSeconds) return true
    return nowEpochSeconds - lastAttemptEpochSeconds >= AUTOMATIC_REFRESH_MIN_AGE_SECONDS
}
