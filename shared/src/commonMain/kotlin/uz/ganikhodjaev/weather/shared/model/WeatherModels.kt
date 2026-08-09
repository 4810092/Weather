package uz.ganikhodjaev.weather.shared.model

data class Location(
    val id: String,
    val name: String,
    val country: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
)

data class WeatherHour(
    val epochSeconds: Long,
    val temperatureC: Double,
    val apparentTemperatureC: Double,
    val weatherCode: Int,
    val precipitationProbability: Int,
    val precipitationMm: Double,
    val windKph: Double,
    val gustKph: Double,
    val humidityPercent: Int,
    val uvIndex: Double,
    val fetchedAtEpochSeconds: Long,
)

data class WeatherSnapshot(
    val location: Location,
    val current: WeatherHour,
    val timeline: List<WeatherHour>,
    val fetchedAtEpochSeconds: Long,
    val isStale: Boolean,
)

enum class WeatherCondition {
    Clear,
    MainlyClear,
    Cloudy,
    Fog,
    Drizzle,
    Rain,
    Snow,
    Showers,
    Thunderstorm,
    Unknown,
}

fun weatherCondition(code: Int): WeatherCondition = when (code) {
    0 -> WeatherCondition.Clear
    1, 2 -> WeatherCondition.MainlyClear
    3 -> WeatherCondition.Cloudy
    45, 48 -> WeatherCondition.Fog
    51, 53, 55, 56, 57 -> WeatherCondition.Drizzle
    61, 63, 65, 66, 67 -> WeatherCondition.Rain
    71, 73, 75, 77, 85, 86 -> WeatherCondition.Snow
    80, 81, 82 -> WeatherCondition.Showers
    95, 96, 99 -> WeatherCondition.Thunderstorm
    else -> WeatherCondition.Unknown
}
