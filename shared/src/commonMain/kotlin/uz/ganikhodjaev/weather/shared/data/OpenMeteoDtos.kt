package uz.ganikhodjaev.weather.shared.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
internal data class ForecastResponse(
    val latitude: Double,
    val longitude: Double,
    val timezone: String,
    @SerialName("utc_offset_seconds") val utcOffsetSeconds: Int,
    val hourly: HourlyResponse,
    val daily: DailyResponse = DailyResponse()
)

@Serializable
internal data class HourlyResponse(
    val time: List<Long>,
    @SerialName("temperature_2m") val temperature: List<Double>,
    @SerialName("apparent_temperature") val apparentTemperature: List<Double>,
    @SerialName("weather_code") val weatherCode: List<Int>,
    @SerialName("precipitation_probability")
    val precipitationProbability: List<Int?> = emptyList(),
    val precipitation: List<Double?> = emptyList(),
    @SerialName("wind_speed_10m") val windSpeed: List<Double>,
    @SerialName("wind_gusts_10m") val windGusts: List<Double?> = emptyList(),
    @SerialName("relative_humidity_2m") val humidity: List<Int>,
    @SerialName("uv_index") val uvIndex: List<Double?> = emptyList()
)

@Serializable
internal data class DailyResponse(
    val time: List<Long> = emptyList(),
    @SerialName("weather_code") val weatherCode: List<Int> = emptyList(),
    @SerialName("temperature_2m_max") val temperatureMax: List<Double> = emptyList(),
    @SerialName("temperature_2m_min") val temperatureMin: List<Double> = emptyList(),
    @SerialName("apparent_temperature_max") val apparentTemperatureMax: List<Double> = emptyList(),
    @SerialName("apparent_temperature_min") val apparentTemperatureMin: List<Double> = emptyList(),
    @SerialName("precipitation_probability_max")
    val precipitationProbabilityMax: List<Int?> = emptyList(),
    @SerialName("precipitation_sum") val precipitationSum: List<Double?> = emptyList(),
    @SerialName("wind_speed_10m_max") val windSpeedMax: List<Double> = emptyList(),
    @SerialName("wind_gusts_10m_max") val windGustsMax: List<Double?> = emptyList(),
    @SerialName("uv_index_max") val uvIndexMax: List<Double?> = emptyList(),
    val sunrise: List<Long> = emptyList(),
    val sunset: List<Long> = emptyList()
)

@Serializable
internal data class AirQualityResponse(val hourly: AirQualityHourlyResponse)

@Serializable
internal data class AirQualityHourlyResponse(
    val time: List<Long>,
    @SerialName("us_aqi") val usAqi: List<Int?> = emptyList(),
    @SerialName("pm2_5") val pm25: List<Double?> = emptyList(),
    val pm10: List<Double?> = emptyList(),
    val dust: List<Double?> = emptyList(),
    val ozone: List<Double?> = emptyList(),
    @SerialName("nitrogen_dioxide") val nitrogenDioxide: List<Double?> = emptyList()
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
