package uz.ganikhodjaev.weather.shared

import platform.Foundation.NSBundle
import platform.Foundation.NSNotificationCenter
import platform.Foundation.NSUserDefaults
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal actual fun publishWeatherSnapshot(
    platformContext: PlatformContext,
    snapshot: WeatherSnapshot,
    displayUnits: DisplayUnits,
    allowReview: Boolean
) {
    val defaults = NSUserDefaults(suiteName = APP_GROUP)
    val airQuality = snapshot.airQuality.minByOrNull {
        kotlin.math.abs(it.epochSeconds - snapshot.current.epochSeconds)
    }
    val today = snapshot.dailyForecast.firstOrNull()
    defaults.setObject(
        snapshot.location.name.ifBlank { snapshot.location.country },
        forKey = "location"
    )
    defaults.setInteger(
        displayUnits.temperature(snapshot.current.temperatureC).toLong(),
        forKey = "temperature_c"
    )
    defaults.setObject(displayUnits.temperatureSymbol, forKey = "temperature_unit")
    defaults.setInteger(snapshot.current.weatherCode.toLong(), forKey = "weather_code")
    defaults.setInteger(
        snapshot.current.precipitationProbability.toLong(),
        forKey = "rain_chance"
    )
    defaults.setInteger((airQuality?.usAqi ?: -1).toLong(), forKey = "aqi")
    defaults.setBool(today != null, forKey = "has_daily_range")
    if (today != null) {
        defaults.setInteger(
            displayUnits.temperature(today.temperatureMaxC).toLong(),
            forKey = "temperature_max"
        )
        defaults.setInteger(
            displayUnits.temperature(today.temperatureMinC).toLong(),
            forKey = "temperature_min"
        )
    } else {
        defaults.removeObjectForKey("temperature_max")
        defaults.removeObjectForKey("temperature_min")
    }
    defaults.setInteger(snapshot.fetchedAtEpochSeconds, forKey = "updated_at")
    if (allowReview) maybeRequestReview(defaults, snapshot.fetchedAtEpochSeconds)
    NSNotificationCenter.defaultCenter.postNotificationName(
        aName = "NimboWeatherDidUpdate",
        `object` = null
    )
}

private fun maybeRequestReview(defaults: NSUserDefaults, fetchedAt: Long) {
    if (defaults.integerForKey("last_counted_refresh") == fetchedAt) return
    val completedRefreshes = defaults.integerForKey("completed_refreshes") + 1
    val version = NSBundle.mainBundle.objectForInfoDictionaryKey(
        "CFBundleShortVersionString"
    ) as? String ?: ""
    defaults.setInteger(fetchedAt, forKey = "last_counted_refresh")
    defaults.setInteger(completedRefreshes, forKey = "completed_refreshes")
    if (completedRefreshes >= REVIEW_MILESTONE &&
        defaults.stringForKey("reviewed_version") != version
    ) {
        defaults.setObject(version, forKey = "reviewed_version")
        NSNotificationCenter.defaultCenter.postNotificationName(
            aName = "NimboReviewMilestone",
            `object` = null
        )
    }
}

private const val APP_GROUP = "group.uz.ganikhodjaev.weather"
private const val REVIEW_MILESTONE = 4L
