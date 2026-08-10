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
