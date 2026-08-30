package uz.ganikhodjaev.weather.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.headersOf
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFails
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import uz.ganikhodjaev.weather.shared.model.Location

class OpenMeteoServiceTest {
    @Test
    fun forecastHttpFixtureWithoutOptionalArraysKeepsRequiredRows() = runBlocking {
        val response = serviceReturning(FORECAST_WITHOUT_OPTIONAL_ARRAYS).forecast(
            location = LOCATION,
            pastDays = 1,
            forecastDays = 10
        )

        val hourlyRows = response.toWeatherRows(fetchedAt = 99L)
        val dailyRows = response.toDailyRows(fetchedAt = 99L)

        assertEquals(2, hourlyRows.size)
        assertEquals(0, hourlyRows.last().precipitationProbability)
        assertEquals(0.0, hourlyRows.last().precipitationMm)
        assertEquals(0.0, hourlyRows.last().gustKph)
        assertEquals(0.0, hourlyRows.last().uvIndex)
        assertEquals(1, dailyRows.size)
        assertEquals(0, dailyRows.single().precipitationProbabilityMax)
        assertEquals(0.0, dailyRows.single().precipitationMm)
        assertEquals(0.0, dailyRows.single().gustMaxKph)
        assertEquals(0.0, dailyRows.single().uvIndexMax)
    }

    @Test
    fun airQualityHttpFixtureWithoutPollutantArraysKeepsTimeline() = runBlocking {
        val response = serviceReturning(AIR_QUALITY_WITHOUT_OPTIONAL_ARRAYS)
            .airQuality(LOCATION)

        val rows = response.toAirQualityRows(fetchedAt = 99L)

        assertEquals(2, rows.size)
        assertTrue(rows.all { it.usAqi == null })
        assertTrue(rows.all { it.pm25 == null })
        assertTrue(rows.all { it.nitrogenDioxide == null })
    }

    @Test
    fun missingRequiredWeatherOrTimeArrayFailsClosed() = runBlocking {
        listOf(FORECAST_WITHOUT_TIME, FORECAST_WITHOUT_TEMPERATURE).forEach { fixture ->
            assertFails {
                serviceReturning(fixture).forecast(
                    location = LOCATION,
                    pastDays = 1,
                    forecastDays = 10
                )
            }
        }
    }

    @Test
    fun unicodeQueryUsesNormalizedRequestedLanguageAndMapsLocalizedResult() = runBlocking {
        val (service, requests) = recordingService {
            cityResponse(name = "Москва", country = "Россия")
        }

        val results = service.searchCities("  Москва ", "RU")

        assertEquals(listOf(SearchRequest("Москва", "ru")), requests)
        assertEquals("Москва", results.single().name)
        assertEquals("Россия", results.single().country)
    }

    @Test
    fun emptyLocalizedResponseFallsBackToEnglish() = runBlocking {
        val (service, requests) = recordingService { language ->
            if (language == "ru") EMPTY_RESPONSE else cityResponse("Moscow", "Russia")
        }

        val results = service.searchCities("Moscow", "ru")

        assertEquals(
            listOf(SearchRequest("Moscow", "ru"), SearchRequest("Moscow", "en")),
            requests
        )
        assertEquals("Moscow", results.single().name)
    }

    @Test
    fun emptyEnglishResponseDoesNotRetry() = runBlocking {
        val (service, requests) = recordingService { EMPTY_RESPONSE }

        val results = service.searchCities("Nowhere", "en")

        assertTrue(results.isEmpty())
        assertEquals(listOf(SearchRequest("Nowhere", "en")), requests)
    }

    @Test
    fun twoEmptyResponsesReturnNoMatches() = runBlocking {
        val (service, requests) = recordingService { EMPTY_RESPONSE }

        val results = service.searchCities("غير موجود", "ar")

        assertTrue(results.isEmpty())
        assertEquals(
            listOf(SearchRequest("غير موجود", "ar"), SearchRequest("غير موجود", "en")),
            requests
        )
    }

    private fun recordingService(
        responseForLanguage: (String) -> String
    ): Pair<OpenMeteoService, MutableList<SearchRequest>> {
        val requests = mutableListOf<SearchRequest>()
        val engine = MockEngine { request ->
            val language = request.url.parameters["language"].orEmpty()
            requests += SearchRequest(
                query = request.url.parameters["name"].orEmpty(),
                language = language
            )
            respond(
                content = responseForLanguage(language),
                headers = headersOf(
                    HttpHeaders.ContentType,
                    ContentType.Application.Json.toString()
                )
            )
        }
        return OpenMeteoService(HttpClient(engine)) to requests
    }

    private fun serviceReturning(response: String): OpenMeteoService {
        val engine = MockEngine {
            respond(
                content = response,
                headers = headersOf(
                    HttpHeaders.ContentType,
                    ContentType.Application.Json.toString()
                )
            )
        }
        return OpenMeteoService(HttpClient(engine))
    }

    private fun cityResponse(name: String, country: String): String =
        """
        {
          "results": [
            {
              "id": 524901,
              "name": "$name",
              "latitude": 55.75204,
              "longitude": 37.61781,
              "timezone": "Europe/Moscow",
              "country_code": "RU",
              "country": "$country"
            }
          ]
        }
        """.trimIndent()

    private data class SearchRequest(val query: String, val language: String)

    private companion object {
        const val EMPTY_RESPONSE = "{\"results\":[]}"
        val LOCATION = Location(
            id = "tashkent",
            name = "Tashkent",
            country = "Uzbekistan",
            latitude = 41.31,
            longitude = 69.24,
            timezone = "Asia/Tashkent"
        )
        val FORECAST_WITHOUT_OPTIONAL_ARRAYS =
            """
            {
              "latitude": 41.31,
              "longitude": 69.24,
              "timezone": "Asia/Tashkent",
              "utc_offset_seconds": 18000,
              "hourly": {
                "time": [1, 2],
                "temperature_2m": [20.0, 21.0],
                "apparent_temperature": [19.0, 20.0],
                "weather_code": [1, 2],
                "wind_speed_10m": [5.0, 6.0],
                "relative_humidity_2m": [40, 45]
              },
              "daily": {
                "time": [86400],
                "weather_code": [2],
                "temperature_2m_max": [25.0],
                "temperature_2m_min": [15.0],
                "apparent_temperature_max": [24.0],
                "apparent_temperature_min": [14.0],
                "wind_speed_10m_max": [12.0],
                "sunrise": [90000],
                "sunset": [130000]
              }
            }
            """.trimIndent()
        val AIR_QUALITY_WITHOUT_OPTIONAL_ARRAYS =
            """
            {
              "hourly": {
                "time": [1, 2]
              }
            }
            """.trimIndent()
        val FORECAST_WITHOUT_TIME =
            """
            {
              "latitude": 41.31,
              "longitude": 69.24,
              "timezone": "Asia/Tashkent",
              "utc_offset_seconds": 18000,
              "hourly": {
                "temperature_2m": [20.0],
                "apparent_temperature": [19.0],
                "weather_code": [1],
                "wind_speed_10m": [5.0],
                "relative_humidity_2m": [40]
              }
            }
            """.trimIndent()
        val FORECAST_WITHOUT_TEMPERATURE =
            """
            {
              "latitude": 41.31,
              "longitude": 69.24,
              "timezone": "Asia/Tashkent",
              "utc_offset_seconds": 18000,
              "hourly": {
                "time": [1],
                "apparent_temperature": [19.0],
                "weather_code": [1],
                "wind_speed_10m": [5.0],
                "relative_humidity_2m": [40]
              }
            }
            """.trimIndent()
    }
}
