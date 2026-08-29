package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class WeatherRepositoryObservationWindowTest {
    @Test
    fun longLivedObservationRebindsTimelineAfterClockCrossesItsWindow() = runBlocking {
        val fixture = ObservationFixture(START)
        try {
            (-2L..49L).forEach { hour ->
                fixture.insertWeatherHour(START + hour * SECONDS_PER_HOUR)
            }

            val emissions = Channel<WeatherSnapshot>(Channel.UNLIMITED)
            val observation = launch {
                fixture.repository.observe(fixture.location)
                    .filterNotNull()
                    .collect(emissions::send)
            }
            try {
                val initial = withTimeout(OBSERVATION_TIMEOUT_MILLIS) { emissions.receive() }
                assertEquals(START, initial.current.epochSeconds)
                assertEquals(START + 24L * SECONDS_PER_HOUR, initial.timeline.last().epochSeconds)
                assertFalse(initial.isStale)

                fixture.clock.value = START + 25L * SECONDS_PER_HOUR

                val advanced = withTimeout(OBSERVATION_TIMEOUT_MILLIS) { emissions.receive() }
                assertEquals(START + 25L * SECONDS_PER_HOUR, advanced.current.epochSeconds)
                assertEquals(START + SECONDS_PER_HOUR, advanced.timeline.first().epochSeconds)
                assertEquals(START + 49L * SECONDS_PER_HOUR, advanced.timeline.last().epochSeconds)
                assertTrue(advanced.isStale)
            } finally {
                observation.cancelAndJoin()
            }
        } finally {
            fixture.close()
        }
    }

    @Test
    fun longLivedObservationRebindsDailyAndAirWindowsAfterDayBoundary() = runBlocking {
        val fixture = ObservationFixture(START)
        try {
            fixture.insertWeatherHour(START)
            fixture.insertWeatherHour(START + 25L * SECONDS_PER_HOUR)
            (-1L..10L).forEach { day ->
                fixture.insertDailyForecast(START + day * SECONDS_PER_DAY)
            }
            listOf(-1L, 0L, 1L, 25L).forEach { hour ->
                fixture.insertAirQualityHour(START + hour * SECONDS_PER_HOUR)
            }

            val emissions = Channel<WeatherSnapshot>(Channel.UNLIMITED)
            val observation = launch {
                fixture.repository.observe(fixture.location)
                    .filterNotNull()
                    .collect(emissions::send)
            }
            try {
                val initial = withTimeout(OBSERVATION_TIMEOUT_MILLIS) { emissions.receive() }
                assertEquals(START - SECONDS_PER_DAY, initial.dailyForecast.first().epochSeconds)
                assertEquals(
                    START + 8L * SECONDS_PER_DAY,
                    initial.dailyForecast.last().epochSeconds
                )
                assertEquals(
                    listOf(-1L, 0L, 1L, 25L).map { START + it * SECONDS_PER_HOUR },
                    initial.airQuality.map { it.epochSeconds }
                )

                fixture.clock.value = START + 25L * SECONDS_PER_HOUR

                val advanced = withTimeout(OBSERVATION_TIMEOUT_MILLIS) { emissions.receive() }
                assertEquals(START + SECONDS_PER_DAY, advanced.dailyForecast.first().epochSeconds)
                assertEquals(
                    START + 10L * SECONDS_PER_DAY,
                    advanced.dailyForecast.last().epochSeconds
                )
                assertEquals(
                    listOf(START + 25L * SECONDS_PER_HOUR),
                    advanced.airQuality.map { it.epochSeconds }
                )
            } finally {
                observation.cancelAndJoin()
            }
        } finally {
            fixture.close()
        }
    }

    private class ObservationFixture(startEpochSeconds: Long) {
        private val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
        private val database: NimboDatabase
        val clock = MutableStateFlow(startEpochSeconds)
        val location = Location(
            id = "tashkent",
            name = "Tashkent",
            country = "Uzbekistan",
            latitude = 41.31,
            longitude = 69.24,
            timezone = "Asia/Tashkent"
        )
        val repository: WeatherRepository

        init {
            NimboDatabase.Schema.create(driver)
            database = NimboDatabase(driver)
            repository = WeatherRepository(database, OpenMeteoService(), clock)
            database.weatherQueries.insertOrReplaceLocation(
                id = location.id,
                name = location.name,
                country = location.country,
                latitude = location.latitude,
                longitude = location.longitude,
                timezone = location.timezone,
                is_active = 1
            )
        }

        fun insertWeatherHour(epochSeconds: Long) {
            database.weatherQueries.insertOrReplaceWeatherHour(
                location_id = location.id,
                epoch_seconds = epochSeconds,
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
                fetched_at_epoch_seconds = START
            )
        }

        fun insertDailyForecast(epochSeconds: Long) {
            database.weatherQueries.insertOrReplaceDailyForecast(
                location_id = location.id,
                epoch_seconds = epochSeconds,
                weather_code = 0,
                temperature_max_c = 25.0,
                temperature_min_c = 15.0,
                apparent_temperature_max_c = 25.0,
                apparent_temperature_min_c = 15.0,
                precipitation_probability_max = 0,
                precipitation_mm = 0.0,
                wind_max_kph = 0.0,
                gust_max_kph = 0.0,
                uv_index_max = 0.0,
                sunrise_epoch_seconds = epochSeconds,
                sunset_epoch_seconds = epochSeconds,
                fetched_at_epoch_seconds = START
            )
        }

        fun insertAirQualityHour(epochSeconds: Long) {
            database.weatherQueries.insertOrReplaceAirQualityHour(
                location_id = location.id,
                epoch_seconds = epochSeconds,
                us_aqi = 25,
                pm25 = 5.0,
                pm10 = 10.0,
                dust = 1.0,
                ozone = 20.0,
                nitrogen_dioxide = 3.0,
                fetched_at_epoch_seconds = START
            )
        }

        fun close() {
            driver.close()
        }
    }

    private companion object {
        const val START = 1_767_225_600L
        const val SECONDS_PER_HOUR = 60L * 60L
        const val SECONDS_PER_DAY = 24L * SECONDS_PER_HOUR
        const val OBSERVATION_TIMEOUT_MILLIS = 5_000L
    }
}
