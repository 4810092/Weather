package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import kotlin.test.Test
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location

class LocationRetentionTest {
    @Test
    fun changingPlaceRemovesPreviousLocationAndItsCachedWeather() = runBlocking {
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

            assertNull(database.weatherQueries.selectLocationById(previous.id).executeAsOneOrNull())
            assertTrue(
                database.weatherQueries.selectTimeline(previous.id, 0, Long.MAX_VALUE)
                    .executeAsList()
                    .isEmpty()
            )
        } finally {
            driver.close()
        }
    }
}
