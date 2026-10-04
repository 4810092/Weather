package uz.ganikhodjaev.weather.shared.model

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.time.Instant

class WeatherModelsTest {
    @Test
    fun currentHourDoesNotAdvanceAfterHalfPastOrBeforeLocalMidnight() {
        // Tashkent 23:00 and the following midnight, expressed as absolute instants.
        val beforeMidnight = hour("2026-10-04T18:00:00Z")
        val midnight = hour("2026-10-04T19:00:00Z")
        val hours = listOf(midnight, beforeMidnight)
        assertEquals(beforeMidnight, hours.weatherHourAt(beforeMidnight.epochSeconds + 37 * 60))
        assertEquals(beforeMidnight, hours.weatherHourAt(midnight.epochSeconds - 1))
        assertEquals(midnight, hours.weatherHourAt(midnight.epochSeconds))
    }

    @Test
    fun repeatedDstHourIsSelectedByInstantInsteadOfWallClockOrNearestDistance() {
        // Both hours read 01:00 in New York when daylight saving ends.
        val first = hour("2026-11-01T05:00:00Z")
        val repeated = hour("2026-11-01T06:00:00Z")
        val hours = listOf(repeated, first)
        assertEquals(first, hours.weatherHourAt(first.epochSeconds + 59 * 60))
        assertEquals(repeated, hours.weatherHourAt(repeated.epochSeconds + 37 * 60))
    }

    @Test
    fun incompleteCacheUsesAvailableBoundaryWithoutRequiringSortedInput() {
        val first = hour("2026-10-04T08:00:00Z")
        val last = hour("2026-10-04T09:00:00Z")
        assertEquals(first, listOf(last, first).weatherHourAt(first.epochSeconds - 3600))
        assertEquals(last, listOf(last, first).weatherHourAt(last.epochSeconds + 86_400))
        assertNull(emptyList<WeatherHour>().weatherHourAt(first.epochSeconds))
    }

    private fun hour(instant: String) = WeatherHour(
        epochSeconds = Instant.parse(instant).epochSeconds,
        temperatureC = 20.0,
        apparentTemperatureC = 20.0,
        weatherCode = 0,
        precipitationProbability = 0,
        precipitationMm = 0.0,
        windKph = 0.0,
        gustKph = 0.0,
        humidityPercent = 50,
        uvIndex = 0.0,
        fetchedAtEpochSeconds = 0L
    )

    @Test
    fun mapsRepresentativeWmoCodesToNormalizedConditions() {
        val expected = mapOf(
            0 to WeatherCondition.Clear,
            2 to WeatherCondition.MainlyClear,
            3 to WeatherCondition.Cloudy,
            45 to WeatherCondition.Fog,
            55 to WeatherCondition.Drizzle,
            65 to WeatherCondition.Rain,
            75 to WeatherCondition.Snow,
            82 to WeatherCondition.Showers,
            99 to WeatherCondition.Thunderstorm,
            1000 to WeatherCondition.Unknown
        )

        expected.forEach { (code, condition) ->
            assertEquals(condition, weatherCondition(code), "WMO code $code")
        }
    }
}
