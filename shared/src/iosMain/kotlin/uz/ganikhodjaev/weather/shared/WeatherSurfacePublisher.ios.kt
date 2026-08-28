package uz.ganikhodjaev.weather.shared

import platform.Foundation.NSNotificationCenter
import platform.Foundation.NSUserDefaults
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal actual fun publishWeatherSnapshot(
    platformContext: PlatformContext,
    snapshot: WeatherSnapshot,
    displayUnits: DisplayUnits
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
    NSNotificationCenter.defaultCenter.postNotificationName(
        aName = "NimboWeatherDidUpdate",
        `object` = null
    )
}

private const val APP_GROUP = "group.uz.ganikhodjaev.weather"
