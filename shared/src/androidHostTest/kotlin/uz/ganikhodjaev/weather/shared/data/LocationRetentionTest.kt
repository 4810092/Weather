package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location

class LocationRetentionTest {
    @Test
    fun changingPlaceRetainsPreviousLocationAndItsCachedWeatherUntilDeletion() = runBlocking {
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        NimboDatabase.Schema.create(driver)
        val database = NimboDatabase(driver)
        val repository = WeatherRepository(database, OpenMeteoService())
        val previous = Location("previous", "Previous", "Test", 41.31, 69.24, "Asia/Tashkent")
        val next = Location("next", "Next", "Test", 48.86, 2.35, "Europe/Paris")

        try {
            repository.setActiveLocation(previous)
            database.weatherQueries.insertOrReplaceWeatherHour(
                location_id = previous.id,
                epoch_seconds = 1,
                temperature_c = 20.0,
                apparent_temperature_c = 20.0,
                weather_code = 0,
                precipitation_probability = 0,
                precipitation_mm = 0.0,
                wind_kph = 0.0,
                gust_kph = 0.0,
                humidity_percent = 50,
                uv_index = 0.0,
                source = "test",
                fetched_at_epoch_seconds = 1
            )

            repository.setActiveLocation(next)

            assertNotNull(
                database.weatherQueries.selectLocationById(previous.id).executeAsOneOrNull()
            )
            assertEquals(2, repository.savedLocations().size)
            assertTrue(
                database.weatherQueries.selectTimeline(previous.id, 0, Long.MAX_VALUE)
                    .executeAsList()
                    .isNotEmpty()
            )

            repository.deleteLocation(previous.id)

            assertTrue(repository.savedLocations().none { it.id == previous.id })
            assertTrue(
                database.weatherQueries.selectTimeline(previous.id, 0, Long.MAX_VALUE)
                    .executeAsList()
                    .isEmpty()
            )
        } finally {
            driver.close()
        }
    }

    @Test
    fun eleventhLocationRollsBackWithoutClearingTheActiveLocation() = runBlocking {
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        NimboDatabase.Schema.create(driver)
        val repository = WeatherRepository(NimboDatabase(driver), OpenMeteoService())

        try {
            repeat(MAX_SAVED_LOCATIONS) { index ->
                repository.setActiveLocation(
                    Location(
                        id = "saved-$index",
                        name = "Saved $index",
                        country = "Test",
                        latitude = 40.0 + index,
                        longitude = 60.0 + index,
                        timezone = "Asia/Tashkent"
                    )
                )
            }
            val activeBeforeOverflow = assertNotNull(repository.activeLocation())
            val failure = try {
                repository.setActiveLocation(
                    Location(
                        id = "overflow",
                        name = "Overflow",
                        country = "Test",
                        latitude = 0.0,
                        longitude = 0.0,
                        timezone = "UTC"
                    )
                )
                null
            } catch (error: Throwable) {
                error
            }

            assertIs<SavedLocationLimitReachedException>(failure)
            assertEquals(MAX_SAVED_LOCATIONS, repository.savedLocations().size)
            assertEquals(activeBeforeOverflow, repository.activeLocation())
        } finally {
            driver.close()
        }
    }
}
