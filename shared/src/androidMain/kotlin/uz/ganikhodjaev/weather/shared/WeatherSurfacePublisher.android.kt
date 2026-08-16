package uz.ganikhodjaev.weather.shared

import android.content.Intent
import com.google.android.gms.wearable.PutDataMapRequest
import com.google.android.gms.wearable.Wearable
import com.google.android.play.core.review.ReviewManagerFactory
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal actual fun publishWeatherSnapshot(
    platformContext: PlatformContext,
    snapshot: WeatherSnapshot,
    displayUnits: DisplayUnits,
    allowReview: Boolean
) {
    val context = platformContext.applicationContext
    val airQuality = snapshot.airQuality.minByOrNull {
        kotlin.math.abs(it.epochSeconds - snapshot.current.epochSeconds)
    }
    val today = snapshot.dailyForecast.firstOrNull()
    val preferences = context.getSharedPreferences(PREFERENCES_NAME, 0)
    val editor = preferences.edit()
        .putString(KEY_LOCATION, snapshot.location.name.ifBlank { snapshot.location.country })
        .putInt(KEY_TEMPERATURE, displayUnits.temperature(snapshot.current.temperatureC))
        .putString(KEY_TEMPERATURE_UNIT, displayUnits.temperatureSymbol)
        .putInt(KEY_WEATHER_CODE, snapshot.current.weatherCode)
        .putInt(KEY_RAIN_CHANCE, snapshot.current.precipitationProbability)
        .putInt(KEY_AQI, airQuality?.usAqi ?: -1)
        .putBoolean(KEY_HAS_DAILY_RANGE, today != null)
        .putLong(KEY_UPDATED_AT, snapshot.fetchedAtEpochSeconds)
    if (today != null) {
        editor
            .putInt(KEY_TEMPERATURE_MAX, displayUnits.temperature(today.temperatureMaxC))
            .putInt(KEY_TEMPERATURE_MIN, displayUnits.temperature(today.temperatureMinC))
    } else {
        editor.remove(KEY_TEMPERATURE_MAX).remove(KEY_TEMPERATURE_MIN)
    }
    editor.apply()

    val watchRequest = PutDataMapRequest.create(WEATHER_DATA_PATH).apply {
        dataMap.putString(
            KEY_LOCATION,
            snapshot.location.name.ifBlank { snapshot.location.country }
        )
        dataMap.putInt(KEY_TEMPERATURE, displayUnits.temperature(snapshot.current.temperatureC))
        dataMap.putString(KEY_TEMPERATURE_UNIT, displayUnits.temperatureSymbol)
        dataMap.putInt(KEY_WEATHER_CODE, snapshot.current.weatherCode)
        dataMap.putInt(KEY_RAIN_CHANCE, snapshot.current.precipitationProbability)
        dataMap.putInt(KEY_AQI, airQuality?.usAqi ?: -1)
        dataMap.putBoolean(KEY_HAS_DAILY_RANGE, today != null)
        if (today != null) {
            dataMap.putInt(KEY_TEMPERATURE_MAX, displayUnits.temperature(today.temperatureMaxC))
            dataMap.putInt(KEY_TEMPERATURE_MIN, displayUnits.temperature(today.temperatureMinC))
        }
        dataMap.putLong(KEY_UPDATED_AT, snapshot.fetchedAtEpochSeconds)
    }.asPutDataRequest().setUrgent()
    Wearable.getDataClient(context).putDataItem(watchRequest)

    if (allowReview) maybeRequestReview(platformContext, snapshot.fetchedAtEpochSeconds)

    context.sendBroadcast(
        Intent(ACTION_WIDGET_DATA_CHANGED).setPackage(context.packageName)
    )
}

private fun maybeRequestReview(platformContext: PlatformContext, fetchedAt: Long) {
    val activity = platformContext.requireActivity()
    val context = platformContext.applicationContext
    val preferences = context.getSharedPreferences(PREFERENCES_NAME, 0)
    if (preferences.getLong(KEY_LAST_COUNTED_REFRESH, -1L) == fetchedAt) return
    val completedRefreshes = preferences.getInt(KEY_COMPLETED_REFRESHES, 0) + 1
    val version = runCatching {
        context.packageManager.getPackageInfo(context.packageName, 0).versionName
    }.getOrNull().orEmpty()
    preferences.edit()
        .putLong(KEY_LAST_COUNTED_REFRESH, fetchedAt)
        .putInt(KEY_COMPLETED_REFRESHES, completedRefreshes)
        .apply()
    if (completedRefreshes < REVIEW_MILESTONE ||
        preferences.getString(KEY_REVIEWED_VERSION, "") == version
    ) {
        return
    }
    preferences.edit().putString(KEY_REVIEWED_VERSION, version).apply()
    val manager = ReviewManagerFactory.create(activity)
    manager.requestReviewFlow().addOnCompleteListener { task ->
        if (task.isSuccessful) {
            manager.launchReviewFlow(activity, task.result)
        }
    }
}

private const val PREFERENCES_NAME = "nimbo_surface_weather"
private const val KEY_LOCATION = "location"
private const val KEY_TEMPERATURE = "temperature_c"
private const val KEY_TEMPERATURE_UNIT = "temperature_unit"
private const val KEY_WEATHER_CODE = "weather_code"
private const val KEY_RAIN_CHANCE = "rain_chance"
private const val KEY_AQI = "aqi"
private const val KEY_HAS_DAILY_RANGE = "has_daily_range"
private const val KEY_TEMPERATURE_MAX = "temperature_max"
private const val KEY_TEMPERATURE_MIN = "temperature_min"
private const val KEY_UPDATED_AT = "updated_at"
private const val KEY_LAST_COUNTED_REFRESH = "last_counted_refresh"
private const val KEY_COMPLETED_REFRESHES = "completed_refreshes"
private const val KEY_REVIEWED_VERSION = "reviewed_version"
private const val REVIEW_MILESTONE = 4
private const val WEATHER_DATA_PATH = "/nimbo/weather"
private const val ACTION_WIDGET_DATA_CHANGED =
    "uz.ganikhodjaev.weather.action.WIDGET_DATA_CHANGED"
