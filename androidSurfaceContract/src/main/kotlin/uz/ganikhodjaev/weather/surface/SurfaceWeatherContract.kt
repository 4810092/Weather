package uz.ganikhodjaev.weather.surface

const val SURFACE_WEATHER_STALE_AFTER_SECONDS = 6L * 60L * 60L
const val SURFACE_WEATHER_MAX_FUTURE_SKEW_SECONDS = 5L * 60L

private val supportedSurfaceWeatherCodes = setOf(
    0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57,
    61, 63, 65, 66, 67, 71, 73, 75, 77,
    80, 81, 82, 85, 86, 95, 96, 99
)

object SurfaceWeatherKeys {
    const val LOCATION = "location"
    const val TEMPERATURE = "temperature_c"
    const val TEMPERATURE_UNIT = "temperature_unit"
    const val WEATHER_CODE = "weather_code"
    const val RAIN_CHANCE = "rain_chance"
    const val AIR_QUALITY = "aqi"
    const val HAS_DAILY_RANGE = "has_daily_range"
    const val TEMPERATURE_MAX = "temperature_max"
    const val TEMPERATURE_MIN = "temperature_min"
    const val UPDATED_AT = "updated_at"
}

enum class SurfaceWeatherState {
    Empty,
    Fresh,
    Stale
}

data class SurfaceWeatherRenderModel(
    val state: SurfaceWeatherState,
    val location: String? = null,
    val temperature: Int? = null,
    val temperatureUnit: String? = null,
    val weatherCode: Int? = null,
    val rainChance: Int? = null,
    val airQuality: Int? = null,
    val temperatureMaximum: Int? = null,
    val temperatureMinimum: Int? = null,
    val updatedAtEpochSeconds: Long? = null
) {
    val showsOpenAction: Boolean
        get() = state == SurfaceWeatherState.Empty

    val showsWeatherFacts: Boolean
        get() = state != SurfaceWeatherState.Empty

    val showsDailyRange: Boolean
        get() = showsWeatherFacts &&
            temperatureMaximum != null &&
            temperatureMinimum != null

    val showsStaleStatus: Boolean
        get() = state == SurfaceWeatherState.Stale
}

fun buildSurfaceWeatherRenderModel(
    values: Map<String, *>,
    nowEpochSeconds: Long
): SurfaceWeatherRenderModel {
    if (nowEpochSeconds <= 0L) return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)

    val location = (values[SurfaceWeatherKeys.LOCATION] as? String)
        ?.trim()
        ?.takeIf { it.isNotEmpty() && it.length <= 100 }
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val temperature = (values[SurfaceWeatherKeys.TEMPERATURE] as? Int)
        ?.takeIf { it in -200..200 }
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val temperatureUnit = (values[SurfaceWeatherKeys.TEMPERATURE_UNIT] as? String)
        ?.trim()
        ?.takeIf { it.isNotEmpty() && it.length <= 8 }
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val weatherCode = (values[SurfaceWeatherKeys.WEATHER_CODE] as? Int)
        ?.takeIf(supportedSurfaceWeatherCodes::contains)
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val rainChance = (values[SurfaceWeatherKeys.RAIN_CHANCE] as? Int)
        ?.takeIf { it in 0..100 }
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val airQuality = if (values.containsKey(SurfaceWeatherKeys.AIR_QUALITY)) {
        when (val storedAirQuality = values[SurfaceWeatherKeys.AIR_QUALITY]) {
            -1 -> null
            is Int -> storedAirQuality.takeIf { it in 0..1_000 }
                ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
            else -> return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
        }
    } else {
        null
    }
    val hasDailyRange = values[SurfaceWeatherKeys.HAS_DAILY_RANGE] as? Boolean
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    val updatedAt = (values[SurfaceWeatherKeys.UPDATED_AT] as? Long)
        ?.takeIf { it > 0L }
        ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)

    if (
        updatedAt > nowEpochSeconds &&
        updatedAt - nowEpochSeconds > SURFACE_WEATHER_MAX_FUTURE_SKEW_SECONDS
    ) {
        return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    }

    val maximum = if (hasDailyRange) {
        (values[SurfaceWeatherKeys.TEMPERATURE_MAX] as? Int)
            ?.takeIf { it in -200..200 }
            ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    } else {
        null
    }
    val minimum = if (hasDailyRange) {
        (values[SurfaceWeatherKeys.TEMPERATURE_MIN] as? Int)
            ?.takeIf { it in -200..200 }
            ?: return SurfaceWeatherRenderModel(SurfaceWeatherState.Empty)
    } else {
        null
    }
    val ageSeconds = if (updatedAt > nowEpochSeconds) 0L else nowEpochSeconds - updatedAt
    val state = if (ageSeconds > SURFACE_WEATHER_STALE_AFTER_SECONDS) {
        SurfaceWeatherState.Stale
    } else {
        SurfaceWeatherState.Fresh
    }

    return SurfaceWeatherRenderModel(
        state = state,
        location = location,
        temperature = temperature,
        temperatureUnit = temperatureUnit,
        weatherCode = weatherCode,
        rainChance = rainChance,
        airQuality = airQuality,
        temperatureMaximum = maximum,
        temperatureMinimum = minimum,
        updatedAtEpochSeconds = updatedAt
    )
}
