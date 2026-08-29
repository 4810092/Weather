package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import kotlin.math.abs
import kotlin.time.Clock
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.flow
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.domain.timelineWithinHours
import uz.ganikhodjaev.weather.shared.model.AirQualityHour
import uz.ganikhodjaev.weather.shared.model.DailyForecast
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal interface WeatherDataSource {
    fun activeLocation(): Location?

    fun savedLocations(): List<Location>

    fun observe(location: Location): Flow<WeatherSnapshot?>

    suspend fun refreshPrimary(location: Location): Long

    suspend fun refreshAirQuality(location: Location)

    suspend fun refreshHistory(location: Location)

    suspend fun searchCities(query: String, language: String): List<Location>

    suspend fun setActiveLocation(location: Location)

    fun deleteLocation(locationId: String)

    fun updateLocationDetails(location: Location)

    fun unitPreference(): UnitPreference

    fun setUnitPreference(preference: UnitPreference)
}

internal class WeatherRepository(
    private val database: NimboDatabase,
    private val service: OpenMeteoService,
    private val observationEpochSeconds: Flow<Long> = weatherObservationEpochSeconds()
) : WeatherDataSource {
    private val queries = database.weatherQueries

    override fun activeLocation(): Location? {
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

    override fun savedLocations(): List<Location> = queries.selectAllLocations {
            id,
            name,
            country,
            latitude,
            longitude,
            timezone,
            _
        ->
        Location(id, name, country, latitude, longitude, timezone)
    }.executeAsList()

    @OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
    override fun observe(location: Location): Flow<WeatherSnapshot?> =
        observationEpochSeconds.flatMapLatest { now ->
            val timelineFlow = queries.selectTimeline(
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
            }.asFlow().mapToList(Dispatchers.Default)
            val dailyFlow = queries.selectDailyForecast(location.id, now - SECONDS_PER_DAY) {
                    _,
                    epoch,
                    code,
                    max,
                    min,
                    apparentMax,
                    apparentMin,
                    rainChance,
                    rain,
                    wind,
                    gust,
                    uv,
                    sunrise,
                    sunset,
                    fetchedAt
                ->
                DailyForecast(
                    epoch,
                    code.toInt(),
                    max,
                    min,
                    apparentMax,
                    apparentMin,
                    rainChance.toInt(),
                    rain,
                    wind,
                    gust,
                    uv,
                    sunrise,
                    sunset,
                    fetchedAt
                )
            }.asFlow().mapToList(Dispatchers.Default)
            val airFlow = queries.selectAirQuality(location.id, now - SECONDS_PER_HOUR) {
                    _,
                    epoch,
                    aqi,
                    pm25,
                    pm10,
                    dust,
                    ozone,
                    nitrogenDioxide,
                    fetchedAt
                ->
                AirQualityHour(
                    epoch,
                    aqi?.toInt(),
                    pm25,
                    pm10,
                    dust,
                    ozone,
                    nitrogenDioxide,
                    fetchedAt
                )
            }.asFlow().mapToList(Dispatchers.Default)

            combine(timelineFlow, dailyFlow, airFlow) { allHours, daily, airQuality ->
                if (allHours.isEmpty()) return@combine null
                val resolvedLocation = activeLocation()?.takeIf { it.id == location.id } ?: location
                val current = allHours.minBy { abs(it.epochSeconds - now) }
                val fetchedAt = allHours.maxOf { it.fetchedAtEpochSeconds }
                WeatherSnapshot(
                    location = resolvedLocation,
                    current = current,
                    timeline = timelineWithinHours(allHours, current.epochSeconds, hours = 24) {
                        it.epochSeconds
                    },
                    recentHistory = allHours.filter { it.epochSeconds < current.epochSeconds },
                    dailyForecast = daily,
                    airQuality = airQuality,
                    fetchedAtEpochSeconds = fetchedAt,
                    isStale = now - fetchedAt > STALE_AFTER_SECONDS
                )
            }
        }

    override suspend fun refreshPrimary(location: Location): Long {
        val response = service.forecast(location, pastDays = 1, forecastDays = 10)
        return persistResponse(location, response, recordForecast = true)
    }

    override suspend fun refreshAirQuality(location: Location) {
        val fetchedAt = Clock.System.now().epochSeconds
        val rows = service.airQuality(location).toAirQualityRows(fetchedAt)
        database.transaction {
            rows.forEach { row ->
                queries.insertOrReplaceAirQualityHour(
                    location_id = location.id,
                    epoch_seconds = row.epochSeconds,
                    us_aqi = row.usAqi?.toLong(),
                    pm25 = row.pm25,
                    pm10 = row.pm10,
                    dust = row.dust,
                    ozone = row.ozone,
                    nitrogen_dioxide = row.nitrogenDioxide,
                    fetched_at_epoch_seconds = fetchedAt
                )
            }
            queries.deleteAirQualityBefore(fetchedAt - AIR_QUALITY_RETENTION_SECONDS)
        }
    }

    override suspend fun refreshHistory(location: Location) {
        val response = service.forecast(location, pastDays = 7, forecastDays = 1)
        persistResponse(location, response, recordForecast = false)
    }

    private fun persistResponse(
        location: Location,
        response: ForecastResponse,
        recordForecast: Boolean
    ): Long {
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
            response.toDailyRows(fetchedAt).forEach { day ->
                queries.insertOrReplaceDailyForecast(
                    location_id = location.id,
                    epoch_seconds = day.epochSeconds,
                    weather_code = day.weatherCode.toLong(),
                    temperature_max_c = day.temperatureMaxC,
                    temperature_min_c = day.temperatureMinC,
                    apparent_temperature_max_c = day.apparentTemperatureMaxC,
                    apparent_temperature_min_c = day.apparentTemperatureMinC,
                    precipitation_probability_max = day.precipitationProbabilityMax.toLong(),
                    precipitation_mm = day.precipitationMm,
                    wind_max_kph = day.windMaxKph,
                    gust_max_kph = day.gustMaxKph,
                    uv_index_max = day.uvIndexMax,
                    sunrise_epoch_seconds = day.sunriseEpochSeconds,
                    sunset_epoch_seconds = day.sunsetEpochSeconds,
                    fetched_at_epoch_seconds = fetchedAt
                )
            }
            queries.deleteWeatherOutsideWindow(
                location_id = location.id,
                epoch_seconds = fetchedAt - WEATHER_RETENTION_SECONDS,
                epoch_seconds_ = fetchedAt + WEATHER_FUTURE_RETENTION_SECONDS
            )
            queries.deleteOldForecastSnapshots(fetchedAt - SNAPSHOT_RETENTION_SECONDS)
        }
        return fetchedAt
    }

    override suspend fun searchCities(query: String, language: String): List<Location> =
        service.searchCities(query, language)

    override suspend fun setActiveLocation(location: Location) {
        val alreadySaved = queries.selectLocationById(location.id).executeAsOneOrNull() != null
        database.transaction {
            queries.deactivateLocations()
            if (alreadySaved) {
                queries.updateLocation(
                    name = location.name,
                    country = location.country,
                    latitude = location.latitude,
                    longitude = location.longitude,
                    timezone = location.timezone,
                    is_active = 1,
                    id = location.id
                )
            } else {
                require(savedLocations().size < MAX_SAVED_LOCATIONS) {
                    "Saved location limit reached"
                }
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
    }

    override fun deleteLocation(locationId: String) {
        database.transaction {
            queries.deleteWeatherForLocation(locationId)
            queries.deleteDailyForecastForLocation(locationId)
            queries.deleteAirQualityForLocation(locationId)
            queries.deleteLocationById(locationId)
        }
    }

    override fun updateLocationDetails(location: Location) {
        queries.updateLocationDetails(
            name = location.name,
            country = location.country,
            id = location.id
        )
    }

    override fun unitPreference(): UnitPreference = queries.selectSetting(UNIT_PREFERENCE_KEY)
        .executeAsOneOrNull()
        ?.let { stored -> UnitPreference.entries.firstOrNull { it.name == stored } }
        ?: UnitPreference.Automatic

    override fun setUnitPreference(preference: UnitPreference) {
        queries.upsertSetting(UNIT_PREFERENCE_KEY, preference.name)
    }

    private companion object {
        const val TIMELINE_SECONDS = 24L * 60L * 60L
        const val HISTORY_SECONDS = 7L * 24L * 60L * 60L
        const val STALE_AFTER_SECONDS = 6L * 60L * 60L
        const val SNAPSHOT_RETENTION_SECONDS = 14L * 24L * 60L * 60L
        const val FORECAST_SNAPSHOT_HORIZON_SECONDS = 48L * 60L * 60L
        const val WEATHER_RETENTION_SECONDS = 8L * 24L * 60L * 60L
        const val WEATHER_FUTURE_RETENTION_SECONDS = 11L * 24L * 60L * 60L
        const val SECONDS_PER_HOUR = 60L * 60L
        const val SECONDS_PER_DAY = 24L * SECONDS_PER_HOUR
        const val AIR_QUALITY_RETENTION_SECONDS = 7L * SECONDS_PER_DAY
        const val UNIT_PREFERENCE_KEY = "unit_preference"
        const val MAX_SAVED_LOCATIONS = 10
    }
}

private fun weatherObservationEpochSeconds(): Flow<Long> = flow {
    while (true) {
        val now = Clock.System.now().epochSeconds
        emit(now)
        val secondsIntoInterval = now % OBSERVATION_REEVALUATION_SECONDS
        val secondsUntilNextInterval = OBSERVATION_REEVALUATION_SECONDS - secondsIntoInterval
        delay(secondsUntilNextInterval * 1_000L)
    }
}

private const val OBSERVATION_REEVALUATION_SECONDS = 15L * 60L

internal fun ForecastResponse.toDailyRows(fetchedAt: Long): List<DailyForecast> {
    val requiredSize = listOf(
        daily.time.size,
        daily.weatherCode.size,
        daily.temperatureMax.size,
        daily.temperatureMin.size,
        daily.apparentTemperatureMax.size,
        daily.apparentTemperatureMin.size,
        daily.windSpeedMax.size,
        daily.sunrise.size,
        daily.sunset.size
    ).min()
    return List(requiredSize) { index ->
        DailyForecast(
            epochSeconds = daily.time[index],
            weatherCode = daily.weatherCode[index],
            temperatureMaxC = daily.temperatureMax[index],
            temperatureMinC = daily.temperatureMin[index],
            apparentTemperatureMaxC = daily.apparentTemperatureMax[index],
            apparentTemperatureMinC = daily.apparentTemperatureMin[index],
            precipitationProbabilityMax = daily.precipitationProbabilityMax.getOrNull(index) ?: 0,
            precipitationMm = daily.precipitationSum.getOrNull(index) ?: 0.0,
            windMaxKph = daily.windSpeedMax[index],
            gustMaxKph = daily.windGustsMax.getOrNull(index) ?: 0.0,
            uvIndexMax = daily.uvIndexMax.getOrNull(index) ?: 0.0,
            sunriseEpochSeconds = daily.sunrise[index],
            sunsetEpochSeconds = daily.sunset[index],
            fetchedAtEpochSeconds = fetchedAt
        )
    }
}

internal fun AirQualityResponse.toAirQualityRows(fetchedAt: Long): List<AirQualityHour> =
    hourly.time.mapIndexed { index, epoch ->
        AirQualityHour(
            epochSeconds = epoch,
            usAqi = hourly.usAqi.getOrNull(index),
            pm25 = hourly.pm25.getOrNull(index),
            pm10 = hourly.pm10.getOrNull(index),
            dust = hourly.dust.getOrNull(index),
            ozone = hourly.ozone.getOrNull(index),
            nitrogenDioxide = hourly.nitrogenDioxide.getOrNull(index),
            fetchedAtEpochSeconds = fetchedAt
        )
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
