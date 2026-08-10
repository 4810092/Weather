package uz.ganikhodjaev.weather.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.plugins.HttpRequestRetry
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import uz.ganikhodjaev.weather.shared.model.Location

internal class OpenMeteoService(engineClient: HttpClient = createPlatformHttpClient()) {
    private val client = engineClient.config {
        expectSuccess = true
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
        install(HttpTimeout) {
            connectTimeoutMillis = 8_000
            requestTimeoutMillis = 15_000
            socketTimeoutMillis = 15_000
        }
        install(HttpRequestRetry) {
            retryIf(maxRetries = 2) { _, response ->
                response.status.value == 429 || response.status.value >= 500
            }
            retryOnExceptionIf(maxRetries = 2) { _, _ -> true }
            exponentialDelay()
        }
    }

    suspend fun forecast(location: Location, pastDays: Int, forecastDays: Int): ForecastResponse =
        client.get(
            "https://api.open-meteo.com/v1/forecast"
        ) {
            parameter("latitude", location.latitude)
            parameter("longitude", location.longitude)
            parameter("timezone", "auto")
            parameter("timeformat", "unixtime")
            parameter("past_days", pastDays)
            parameter("forecast_days", forecastDays)
            parameter(
                "hourly",
                listOf(
                    "temperature_2m",
                    "apparent_temperature",
                    "weather_code",
                    "precipitation_probability",
                    "precipitation",
                    "wind_speed_10m",
                    "wind_gusts_10m",
                    "relative_humidity_2m",
                    "uv_index"
                ).joinToString(",")
            )
        }.body()

    suspend fun searchCities(query: String, language: String): List<Location> {
        val normalizedQuery = query.trim()
        if (normalizedQuery.length < 2) return emptyList()
        val normalizedLanguage = language.trim().lowercase().ifBlank { ENGLISH_LANGUAGE }
        val localizedResults = requestCities(normalizedQuery, normalizedLanguage)
        if (localizedResults.isNotEmpty() || normalizedLanguage == ENGLISH_LANGUAGE) {
            return localizedResults
        }
        return requestCities(normalizedQuery, ENGLISH_LANGUAGE)
    }

    private suspend fun requestCities(query: String, language: String): List<Location> {
        val response: GeocodingResponse = client.get(
            "https://geocoding-api.open-meteo.com/v1/search"
        ) {
            parameter("name", query)
            parameter("count", 8)
            parameter("language", language)
            parameter("format", "json")
        }.body()
        return response.results.map { result ->
            Location(
                id = result.id.toString(),
                name = result.name,
                country = result.country ?: result.countryCode,
                latitude = result.latitude,
                longitude = result.longitude,
                timezone = result.timezone
            )
        }
    }

    private companion object {
        const val ENGLISH_LANGUAGE = "en"
    }
}
