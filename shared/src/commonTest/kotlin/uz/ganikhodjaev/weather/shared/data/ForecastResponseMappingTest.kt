package uz.ganikhodjaev.weather.shared.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ForecastResponseMappingTest {
    @Test
    fun partialOptionalArraysKeepUsableRequiredRows() {
        val rows = response(
            times = listOf(1L, 2L),
            temperatures = listOf(10.0, 11.0),
            rainProbability = listOf(75)
        ).toWeatherRows(fetchedAt = 99L)

        assertEquals(2, rows.size)
        assertEquals(75, rows[0].precipitationProbability)
        assertEquals(0, rows[1].precipitationProbability)
        assertEquals(0.0, rows[1].uvIndex)
    }

    @Test
    fun truncatedRequiredArrayOnlyMapsCompleteRows() {
        val rows = response(
            times = listOf(1L, 2L),
            temperatures = listOf(10.0)
        ).toWeatherRows(fetchedAt = 99L)

        assertEquals(1, rows.size)
        assertEquals(1L, rows.single().epochSeconds)
    }

    @Test
    fun missingRequiredArrayProducesNoRowsSoRepositoryCanPreserveCache() {
        val rows = response(
            times = listOf(1L),
            temperatures = emptyList()
        ).toWeatherRows(fetchedAt = 99L)

        assertTrue(rows.isEmpty())
    }

    @Test
    fun dailyForecastUsesSafeDefaultsForOptionalProviderValues() {
        val response = response(times = emptyList(), temperatures = emptyList()).copy(
            daily = DailyResponse(
                time = listOf(86_400L),
                weatherCode = listOf(2),
                temperatureMax = listOf(20.0),
                temperatureMin = listOf(8.0),
                apparentTemperatureMax = listOf(19.0),
                apparentTemperatureMin = listOf(7.0),
                windSpeedMax = listOf(12.0),
                sunrise = listOf(90_000L),
                sunset = listOf(130_000L)
            )
        )

        val day = response.toDailyRows(fetchedAt = 99L).single()

        assertEquals(0, day.precipitationProbabilityMax)
        assertEquals(0.0, day.precipitationMm)
        assertEquals(0.0, day.uvIndexMax)
    }

    @Test
    fun airQualityKeepsTimelineWhenPollutantArraysArePartial() {
        val rows = AirQualityResponse(
            hourly = AirQualityHourlyResponse(
                time = listOf(1L, 2L),
                usAqi = listOf(42),
                pm25 = emptyList(),
                pm10 = emptyList(),
                dust = emptyList(),
                ozone = emptyList(),
                nitrogenDioxide = emptyList()
            )
        ).toAirQualityRows(fetchedAt = 99L)

        assertEquals(2, rows.size)
        assertEquals(42, rows.first().usAqi)
        assertEquals(null, rows.last().usAqi)
    }

    private fun response(
        times: List<Long>,
        temperatures: List<Double>,
        rainProbability: List<Int?> = emptyList()
    ) = ForecastResponse(
        latitude = 0.0,
        longitude = 0.0,
        timezone = "Asia/Tashkent",
        utcOffsetSeconds = 18_000,
        hourly = HourlyResponse(
            time = times,
            temperature = temperatures,
            apparentTemperature = times.map { 9.0 },
            weatherCode = times.map { 1 },
            precipitationProbability = rainProbability,
            precipitation = emptyList(),
            windSpeed = times.map { 5.0 },
            windGusts = emptyList(),
            humidity = times.map { 50 },
            uvIndex = emptyList()
        )
    )
}
