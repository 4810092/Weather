package uz.ganikhodjaev.weather.shared

import kotlin.time.Clock
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import platform.Foundation.NSNumber
import platform.Foundation.NSUserDefaults
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal actual fun configureWidgetRefresh(
    platformContext: PlatformContext,
    location: Location?,
    displayUnits: DisplayUnits?
) {
    val config = location?.let { configuredLocation(it, displayUnits ?: return) }
    val legacy = location?.let { legacyAttempt(automaticRefreshAttemptStorageKey(it.id)) }
    widgetExchange(
        buildJsonObject {
            put("op", "configure")
            put("config", config ?: JsonNull)
            legacy?.let { put("legacy", it) }
        }
    )
}

internal actual fun publishWeatherSnapshot(
    platformContext: PlatformContext,
    snapshot: WeatherSnapshot,
    displayUnits: DisplayUnits
) {
    // A delayed observation must not reconfigure the selected widget city.
    val now = Clock.System.now().epochSeconds
    val airQuality = snapshot.airQuality.filter {
        now - it.fetchedAtEpochSeconds in 0..(6 * 60 * 60L)
    }.minByOrNull {
        kotlin.math.abs(it.epochSeconds - snapshot.current.epochSeconds)
    }
    val today = snapshot.dailyForecast.firstOrNull()
    widgetExchange(
        buildJsonObject {
            put("op", "publish")
            put("config", configuredLocation(snapshot.location, displayUnits))
            put(
                "snapshot",
                buildJsonObject {
                    put("location", snapshot.location.name.ifBlank { snapshot.location.country })
                    put("temperature_c", displayUnits.temperature(snapshot.current.temperatureC))
                    put("temperature_unit", displayUnits.temperatureSymbol)
                    put("weather_code", snapshot.current.weatherCode)
                    put("rain_chance", snapshot.current.precipitationProbability)
                    put("aqi", airQuality?.usAqi ?: -1)
                    put("has_daily_range", today != null)
                    if (today != null) {
                        put("temperature_max", displayUnits.temperature(today.temperatureMaxC))
                        put("temperature_min", displayUnits.temperature(today.temperatureMinC))
                    }
                    put("updated_at", snapshot.fetchedAtEpochSeconds)
                }
            )
        }
    )
}

private fun configuredLocation(location: Location, displayUnits: DisplayUnits): JsonObject =
    buildJsonObject {
        put("id", location.id)
        put("name", location.name)
        put("country", location.country)
        put("latitude", location.latitude)
        put("longitude", location.longitude)
        put("timezone", location.timezone)
        put("temperatureUnit", displayUnits.temperatureSymbol)
        put("attemptKey", automaticRefreshAttemptStorageKey(location.id))
    }

private fun widgetExchange(request: JsonObject) {
    try {
        WidgetRefreshInterop.exchange(
            WIDGET_RPC_JSON.encodeToString(JsonObject.serializer(), request)
        )
    } catch (_: Throwable) {
        // Widget presentation is best effort; foreground weather remains usable.
    }
}

private fun legacyAttempt(key: String): String? = when (
    val stored =
        NSUserDefaults.standardUserDefaults.objectForKey(key)
) {
    is NSNumber -> encodeAutomaticRefreshAttemptState(
        legacyAutomaticRefreshAttemptState(stored.longLongValue)
    )
    else -> NSUserDefaults.standardUserDefaults.stringForKey(key)
}

private val WIDGET_RPC_JSON = Json { }
