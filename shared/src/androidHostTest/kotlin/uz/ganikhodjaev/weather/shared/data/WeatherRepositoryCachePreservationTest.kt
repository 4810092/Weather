package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.headersOf
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFails
import kotlinx.coroutines.runBlocking
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location

class WeatherRepositoryCachePreservationTest {
    @Test
    fun missingRequiredProviderArrayPreservesCachedWeather() {
        assertFailedRefreshPreservesCache(FORECAST_WITHOUT_TIME)
    }

    @Test
    fun emptyRequiredProviderArrayPreservesCachedWeather() {
        assertFailedRefreshPreservesCache(FORECAST_WITH_EMPTY_TIME)
    }

    private fun assertFailedRefreshPreservesCache(response: String) = runBlocking {
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        NimboDatabase.Schema.create(driver)
        val database = NimboDatabase(driver)
        val engine = MockEngine {
            respond(
                content = response,
                headers = headersOf(
                    HttpHeaders.ContentType,
                    ContentType.Application.Json.toString()
                )
            )
        }
        val repository = WeatherRepository(
            database = database,
            service = OpenMeteoService(HttpClient(engine))
        )

        try {
            repository.setActiveLocation(LOCATION)
            database.weatherQueries.insertOrReplaceWeatherHour(
                location_id = LOCATION.id,
                epoch_seconds = 1,
                temperature_c = 20.0,
                apparent_temperature_c = 19.0,
                weather_code = 1,
                precipitation_probability = 25,
                precipitation_mm = 0.5,
                wind_kph = 5.0,
                gust_kph = 8.0,
                humidity_percent = 40,
                uv_index = 2.0,
                source = "open-meteo",
                fetched_at_epoch_seconds = 1
            )
            val cachedBefore = database.weatherQueries
                .selectTimeline(LOCATION.id, 0, Long.MAX_VALUE)
                .executeAsList()
            val locationBefore = repository.activeLocation()

            assertFails { repository.refreshPrimary(LOCATION) }

            assertEquals(
                cachedBefore,
                database.weatherQueries.selectTimeline(LOCATION.id, 0, Long.MAX_VALUE)
                    .executeAsList()
            )
            assertEquals(locationBefore, repository.activeLocation())
        } finally {
            driver.close()
        }
    }

    private companion object {
        val LOCATION = Location(
            id = "tashkent",
            name = "Tashkent",
            country = "Uzbekistan",
            latitude = 41.31,
            longitude = 69.24,
            timezone = "Asia/Tashkent"
        )
        val FORECAST_WITHOUT_TIME = forecastResponse(hourlyTime = null)
        val FORECAST_WITH_EMPTY_TIME = forecastResponse(hourlyTime = "[]")

        fun forecastResponse(hourlyTime: String?): String =
            """
            {
              "latitude": 41.31,
              "longitude": 69.24,
              "timezone": "UTC",
              "utc_offset_seconds": 0,
              "hourly": {
                ${hourlyTime?.let { "\"time\": $it," }.orEmpty()}
                "temperature_2m": [21.0],
                "apparent_temperature": [20.0],
                "weather_code": [2],
                "wind_speed_10m": [6.0],
                "relative_humidity_2m": [45]
              }
            }
            """.trimIndent()
    }
}
