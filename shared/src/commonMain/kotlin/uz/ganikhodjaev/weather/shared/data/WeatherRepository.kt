package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import kotlin.math.abs
import kotlin.time.Clock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.domain.timelineWithinHours
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal class WeatherRepository(
    private val database: NimboDatabase,
    private val service: OpenMeteoService
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
                timezone = stored.timezone
            )
        }
    }

    fun observe(location: Location): Flow<WeatherSnapshot?> {
        val now = Clock.System.now().epochSeconds
        return queries.selectTimeline(
            location_id = location.id,
            epoch_seconds = now - HISTORY_SECONDS,
            epoch_seconds_ = now + TIMELINE_SECONDS
        ) {
                _,
                epoch,
                temperature,
                apparent,
                code,
                rainChance,
                rainMm,
                wind,
                gust,
                humidity,
                uv,
                _,
                fetchedAt
            ->
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
                fetchedAtEpochSeconds = fetchedAt
            )
        }.asFlow().mapToList(Dispatchers.Default).map { allHours ->
            if (allHours.isEmpty()) return@map null
            val resolvedLocation = activeLocation()?.takeIf { it.id == location.id } ?: location
            val current = allHours.minBy { abs(it.epochSeconds - Clock.System.now().epochSeconds) }
            val fetchedAt = allHours.maxOf { it.fetchedAtEpochSeconds }
            WeatherSnapshot(
                location = resolvedLocation,
                current = current,
                timeline = timelineWithinHours(allHours, current.epochSeconds, hours = 24) {
                    it.epochSeconds
                },
                recentHistory = allHours.filter { it.epochSeconds < current.epochSeconds },
                fetchedAtEpochSeconds = fetchedAt,
                isStale = Clock.System.now().epochSeconds - fetchedAt > STALE_AFTER_SECONDS
            )
        }
    }

    suspend fun refreshPrimary(location: Location) {
        val response = service.forecast(location, pastDays = 1, forecastDays = 2)
        persistResponse(location, response, recordForecast = true)
    }

    suspend fun refreshHistory(location: Location) {
        val response = service.forecast(location, pastDays = 7, forecastDays = 1)
        persistResponse(location, response, recordForecast = false)
    }

    private fun persistResponse(
        location: Location,
        response: ForecastResponse,
        recordForecast: Boolean
    ) {
        val fetchedAt = Clock.System.now().epochSeconds
        val rows = response.toWeatherRows(fetchedAt)
        require(rows.isNotEmpty()) { "Provider response contained no usable hourly weather rows" }
        val issuedAt = fetchedAt - fetchedAt % SECONDS_PER_HOUR

        database.transaction {
            if (response.timezone.isNotBlank() && response.timezone != location.timezone) {
                queries.updateLocationTimezone(response.timezone, location.id)
            }
            rows.forEach { row ->
                queries.insertOrReplaceWeatherHour(
                    location_id = location.id,
                    epoch_seconds = row.epochSeconds,
                    temperature_c = row.temperatureC,
                    apparent_temperature_c = row.apparentTemperatureC,
                    weather_code = row.weatherCode.toLong(),
                    precipitation_probability = row.precipitationProbability.toLong(),
                    precipitation_mm = row.precipitationMm,
                    wind_kph = row.windKph,
                    gust_kph = row.gustKph,
                    humidity_percent = row.humidityPercent.toLong(),
                    uv_index = row.uvIndex,
                    source = "open-meteo",
                    fetched_at_epoch_seconds = fetchedAt
                )
                if (
                    recordForecast &&
                    row.epochSeconds >= fetchedAt &&
                    row.epochSeconds <= fetchedAt + FORECAST_SNAPSHOT_HORIZON_SECONDS
                ) {
                    queries.insertForecastSnapshot(
                        location_id = location.id,
                        issued_at_epoch_seconds = issuedAt,
                        valid_at_epoch_seconds = row.epochSeconds,
                        temperature_c = row.temperatureC,
                        weather_code = row.weatherCode.toLong(),
                        precipitation_probability = row.precipitationProbability.toLong()
                    )
                }
            }
            queries.deleteWeatherOutsideWindow(
                location_id = location.id,
                epoch_seconds = fetchedAt - WEATHER_RETENTION_SECONDS,
                epoch_seconds_ = fetchedAt + WEATHER_FUTURE_RETENTION_SECONDS
            )
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
                is_active = 1
            )
        }
    }

    fun unitPreference(): UnitPreference = queries.selectSetting(UNIT_PREFERENCE_KEY)
        .executeAsOneOrNull()
        ?.let { stored -> UnitPreference.entries.firstOrNull { it.name == stored } }
        ?: UnitPreference.Automatic

    fun setUnitPreference(preference: UnitPreference) {
        queries.upsertSetting(UNIT_PREFERENCE_KEY, preference.name)
    }

    private companion object {
        const val TIMELINE_SECONDS = 24L * 60L * 60L
        const val HISTORY_SECONDS = 7L * 24L * 60L * 60L
        const val STALE_AFTER_SECONDS = 6L * 60L * 60L
        const val SNAPSHOT_RETENTION_SECONDS = 14L * 24L * 60L * 60L
        const val FORECAST_SNAPSHOT_HORIZON_SECONDS = 48L * 60L * 60L
        const val WEATHER_RETENTION_SECONDS = 8L * 24L * 60L * 60L
        const val WEATHER_FUTURE_RETENTION_SECONDS = 3L * 24L * 60L * 60L
        const val SECONDS_PER_HOUR = 60L * 60L
        const val UNIT_PREFERENCE_KEY = "unit_preference"
    }
}

internal fun ForecastResponse.toWeatherRows(fetchedAt: Long): List<WeatherHour> {
    val requiredSize = listOf(
        hourly.time.size,
        hourly.temperature.size,
        hourly.apparentTemperature.size,
        hourly.weatherCode.size,
        hourly.windSpeed.size,
        hourly.humidity.size
    ).min()
    return List(requiredSize) { index ->
        WeatherHour(
            epochSeconds = hourly.time[index],
            temperatureC = hourly.temperature[index],
            apparentTemperatureC = hourly.apparentTemperature[index],
            weatherCode = hourly.weatherCode[index],
            precipitationProbability = hourly.precipitationProbability.getOrNull(index) ?: 0,
            precipitationMm = hourly.precipitation.getOrNull(index) ?: 0.0,
            windKph = hourly.windSpeed[index],
            gustKph = hourly.windGusts.getOrNull(index) ?: 0.0,
            humidityPercent = hourly.humidity[index],
            uvIndex = hourly.uvIndex.getOrNull(index) ?: 0.0,
            fetchedAtEpochSeconds = fetchedAt
        )
    }
}
