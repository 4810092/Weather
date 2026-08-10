package uz.ganikhodjaev.weather.shared.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
internal data class ForecastResponse(
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    @SerialName("utc_offset_seconds") val utcOffsetSeconds: Int,
    val hourly: HourlyResponse
)

@Serializable
internal data class HourlyResponse(
    val time: List<Long>,
    @SerialName("temperature_2m") val temperature: List<Double>,
    @SerialName("apparent_temperature") val apparentTemperature: List<Double>,
    @SerialName("weather_code") val weatherCode: List<Int>,
    @SerialName("precipitation_probability") val precipitationProbability: List<Int?>,
    val precipitation: List<Double?>,
    @SerialName("wind_speed_10m") val windSpeed: List<Double>,
    @SerialName("wind_gusts_10m") val windGusts: List<Double?>,
    @SerialName("relative_humidity_2m") val humidity: List<Int>,
    @SerialName("uv_index") val uvIndex: List<Double?>
)

@Serializable
internal data class GeocodingResponse(val results: List<GeocodingResult> = emptyList())

@Serializable
internal data class GeocodingResult(
    val id: Long,
    val name: String,
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    @SerialName("country_code") val countryCode: String,
    val country: String? = null,
    val admin1: String? = null
)
