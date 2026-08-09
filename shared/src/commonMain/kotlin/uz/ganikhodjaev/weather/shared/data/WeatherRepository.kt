package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import kotlin.math.abs
import kotlin.time.Clock

internal class WeatherRepository(
    private val database: NimboDatabase,
    private val service: OpenMeteoService,
) {
    private val queries = database.weatherQueries

    fun activeLocation(): Location? {
        val stored = queries.selectActiveLocation().executeAsOneOrNull()
        return stored?.let {
            Location(
                id = stored.id,
                name = stored.name,
                country = stored.country,
                latitude = stored.latitude,
                longitude = stored.longitude,
                timezone = stored.timezone,
            )
        }
    }

    fun observe(location: Location): Flow<WeatherSnapshot?> {
        val now = Clock.System.now().epochSeconds
        return queries.selectTimeline(
            location_id = location.id,
            epoch_seconds = now - HISTORY_SECONDS,
            epoch_seconds_ = now + TIMELINE_SECONDS,
        ) { _, epoch, temperature, apparent, code, rainChance, rainMm, wind, gust, humidity, uv, _, fetchedAt ->
            WeatherHour(
                epochSeconds = epoch,
                temperatureC = temperature,
                apparentTemperatureC = apparent,
                weatherCode = code.toInt(),
                precipitationProbability = rainChance.toInt(),
                precipitationMm = rainMm,
                windKph = wind,
                gustKph = gust,
                humidityPercent = humidity.toInt(),
                uvIndex = uv,
                fetchedAtEpochSeconds = fetchedAt,
            )
        }.asFlow().mapToList(Dispatchers.Default).map { allHours ->
            if (allHours.isEmpty()) return@map null
            val current = allHours.minBy { abs(it.epochSeconds - Clock.System.now().epochSeconds) }
            val fetchedAt = allHours.maxOf { it.fetchedAtEpochSeconds }
            WeatherSnapshot(
                location = location,
                current = current,
                timeline = allHours.filter {
                    it.epochSeconds >= current.epochSeconds - TIMELINE_SECONDS &&
                        it.epochSeconds <= current.epochSeconds + TIMELINE_SECONDS
                },
                recentHistory = allHours.filter { it.epochSeconds < current.epochSeconds },
                fetchedAtEpochSeconds = fetchedAt,
                isStale = Clock.System.now().epochSeconds - fetchedAt > STALE_AFTER_SECONDS,
            )
        }
    }

    suspend fun refresh(location: Location) {
        val response = service.forecast(location)
        val fetchedAt = Clock.System.now().epochSeconds
        val size = listOf(
            response.hourly.time.size,
            response.hourly.temperature.size,
            response.hourly.apparentTemperature.size,
            response.hourly.weatherCode.size,
            response.hourly.windSpeed.size,
            response.hourly.humidity.size,
        ).min()

        database.transaction {
            queries.deleteWeatherForLocation(location.id)
            repeat(size) { index ->
                val epoch = response.hourly.time[index]
                val temperature = response.hourly.temperature[index]
                val code = response.hourly.weatherCode[index]
                val rainChance = response.hourly.precipitationProbability.getOrNull(index) ?: 0
                queries.insertOrReplaceWeatherHour(
                    location_id = location.id,
                    epoch_seconds = epoch,
                    temperature_c = temperature,
                    apparent_temperature_c = response.hourly.apparentTemperature[index],
                    weather_code = code.toLong(),
                    precipitation_probability = rainChance.toLong(),
                    precipitation_mm = response.hourly.precipitation.getOrNull(index) ?: 0.0,
                    wind_kph = response.hourly.windSpeed[index],
                    gust_kph = response.hourly.windGusts.getOrNull(index) ?: 0.0,
                    humidity_percent = response.hourly.humidity[index].toLong(),
                    uv_index = response.hourly.uvIndex.getOrNull(index) ?: 0.0,
                    source = "open-meteo",
                    fetched_at_epoch_seconds = fetchedAt,
                )
                queries.insertForecastSnapshot(
                    location_id = location.id,
                    issued_at_epoch_seconds = fetchedAt,
                    valid_at_epoch_seconds = epoch,
                    temperature_c = temperature,
                    weather_code = code.toLong(),
                    precipitation_probability = rainChance.toLong(),
                )
            }
            queries.deleteOldForecastSnapshots(fetchedAt - SNAPSHOT_RETENTION_SECONDS)
        }
    }

    suspend fun searchCities(query: String, language: String): List<Location> =
        service.searchCities(query, language)

    suspend fun setActiveLocation(location: Location) {
        database.transaction {
            queries.deactivateLocations()
            queries.insertOrReplaceLocation(
                id = location.id,
                name = location.name,
                country = location.country,
                latitude = location.latitude,
                longitude = location.longitude,
                timezone = location.timezone,
                is_active = 1,
            )
        }
    }

    private companion object {
        const val TIMELINE_SECONDS = 24L * 60L * 60L
        const val HISTORY_SECONDS = 7L * 24L * 60L * 60L
        const val STALE_AFTER_SECONDS = 6L * 60L * 60L
        const val SNAPSHOT_RETENTION_SECONDS = 14L * 24L * 60L * 60L
    }
}
