package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import kotlin.time.Clock
import kotlinx.coroutines.runBlocking
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location

class WidgetRefreshImportTest {
    @Test
    fun preservesWidgetOriginalFetchTimestamp() = fixture { repository, database ->
        assertTrue(repository.importWidgetRefresh(payload(fetchedAt = HOUR)))

        assertEquals(
            HOUR,
            database.weatherQueries.selectWeatherFetchedAt(LOCATION.id, HOUR).executeAsOne()
        )
    }

    @Test
    fun neverOverwritesNewerCachedRows() = fixture { repository, database ->
        database.weatherQueries.insertOrReplaceWeatherHour(
            LOCATION.id, HOUR, 99.0, 99.0, 0, 0, 0.0, 0.0, 0.0, 0, 0.0, "test", HOUR + 100
        )

        assertTrue(repository.importWidgetRefresh(payload(fetchedAt = HOUR)))

        val row = database.weatherQueries.selectTimeline(LOCATION.id, HOUR, HOUR)
            .executeAsOne()
        assertEquals(99.0, row.temperature_c)
        assertEquals(HOUR + 100, row.fetched_at_epoch_seconds)
    }

    @Test
    fun malformedPrimaryPreservesExistingCache() = fixture { repository, database ->
        database.weatherQueries.insertOrReplaceWeatherHour(
            LOCATION.id, HOUR, 99.0, 99.0, 0, 0, 0.0, 0.0, 0.0, 0, 0.0, "test", HOUR + 100
        )

        assertFalse(repository.importWidgetRefresh(payload(forecast = "{bad")))

        assertEquals(
            99.0,
            database.weatherQueries.selectTimeline(LOCATION.id, HOUR, HOUR)
                .executeAsOne().temperature_c
        )
    }

    @Test
    fun malformedOptionalAqiDoesNotBlockPrimaryImport() = fixture { repository, database ->
        assertTrue(repository.importWidgetRefresh(payload(airQuality = "{bad")))

        assertEquals(
            21.0,
            database.weatherQueries.selectTimeline(LOCATION.id, HOUR, HOUR)
                .executeAsOne().temperature_c
        )
        assertEquals(
            0,
            database.weatherQueries.selectAirQuality(LOCATION.id, 0).executeAsList().size
        )
    }

    private fun fixture(block: (WeatherRepository, NimboDatabase) -> Unit) {
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        try {
            NimboDatabase.Schema.create(driver)
            val database = NimboDatabase(driver)
            val repository = WeatherRepository(database, OpenMeteoService())
            runBlocking { repository.setActiveLocation(LOCATION) }
            block(repository, database)
        } finally {
            driver.close()
        }
    }

    private fun payload(
        fetchedAt: Long = HOUR,
        forecast: String = FORECAST,
        airQuality: String? = null
    ) = WidgetRefreshImportPayload(
        deliveryId = "delivery-1",
        locationId = LOCATION.id,
        latitude = LOCATION.latitude,
        longitude = LOCATION.longitude,
        fetchedAtEpochSeconds = fetchedAt,
        forecast = forecast,
        airQuality = airQuality,
        airQualityFetchedAtEpochSeconds = null
    )

    private companion object {
        val HOUR = Clock.System.now().epochSeconds
        val LOCATION = Location("tashkent", "Tashkent", "Uzbekistan", 41.31, 69.24, "Asia/Tashkent")
        val FORECAST = """
            {"latitude":41.31,"longitude":69.24,"timezone":"Asia/Tashkent","utc_offset_seconds":0,
             "hourly":{"time":[$HOUR],"temperature_2m":[21.0],"apparent_temperature":[20.0],
             "weather_code":[2],"wind_speed_10m":[6.0],"relative_humidity_2m":[45]},"daily":{}}
        """.trimIndent()
    }
}
