package uz.ganikhodjaev.weather.shared.ui

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.time.Instant
import uz.ganikhodjaev.weather.shared.model.DailyForecast
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class DaylightAndTimelineTest {
    private val dawn = Instant.parse("2026-10-06T01:00:00Z").epochSeconds
    private val dusk = dawn + 12 * 3_600
    private val hour = WeatherHour(dawn, -5.0, -7.0, 0, 0, 0.0, 5.0, 8.0, 50, 1.0, dawn)
    private val weather = WeatherSnapshot(
        Location("test", "Tashkent", "UZ", 41.0, 69.0, "Asia/Tashkent"),
        hour,
        listOf(hour),
        dailyForecast = listOf(
            DailyForecast(
                dawn - 6 * 3_600, 0, 25.0, 10.0, 25.0, 10.0, 0, 0.0, 5.0, 8.0, 1.0,
                dawn, dusk, dawn
            )
        ),
        fetchedAtEpochSeconds = dawn,
        isStale = false
    )

    @Test
    fun sunriseIsDaySunsetIsNightRegardlessOfDeviceOrTheme() {
        assertEquals(DaylightPhase.Night, daylightAt(weather, dawn - 1, dawn))
        assertEquals(DaylightPhase.Day, daylightAt(weather, dawn, dawn))
        assertEquals(DaylightPhase.Day, daylightAt(weather, dusk - 1, dawn))
        assertEquals(DaylightPhase.Night, daylightAt(weather, dusk, dawn))
    }

    @Test
    fun missingStaleInvalidOrWrongDaySunDataUsesNeutralFallback() {
        assertEquals(
            DaylightPhase.Unknown,
            daylightAt(weather.copy(dailyForecast = emptyList()), dawn, dawn)
        )
        assertEquals(DaylightPhase.Unknown, daylightAt(weather, dawn, dawn + 86_401))
        assertEquals(DaylightPhase.Unknown, daylightAt(weather, dawn, dawn - 301))
        assertEquals(DaylightPhase.Unknown, daylightAt(weather, dawn + 86_400, dawn))
        assertEquals(
            DaylightPhase.Unknown,
            daylightAt(weather.copy(location = weather.location.copy(timezone = "bad")), dawn, dawn)
        )
        assertEquals(
            DaylightPhase.Unknown,
            daylightAt(
                weather.copy(
                    dailyForecast = listOf(
                        weather.dailyForecast.single().copy(sunriseEpochSeconds = 0)
                    )
                ),
                dawn,
                dawn
            )
        )
    }

    @Test
    fun curvePreservesNegativeValuesConstantRangesAndMissingHours() {
        assertEquals(0f, temperatureFraction(-15.0, -15.0, -5.0))
        assertEquals(1f, temperatureFraction(-5.0, -15.0, -5.0))
        assertEquals(0.5f, temperatureFraction(-5.0, -5.0, -5.0))
        val slots = timelineSlots(listOf(hour.copy(epochSeconds = dawn + 7_200), hour))
        assertEquals(listOf(dawn, dawn + 3_600, dawn + 7_200), slots.map { it.epochSeconds })
        assertNull(slots[1].hour)
        assertNull(timelineSlots(listOf(hour.copy(temperatureC = Double.NaN))).single().hour)
    }

    @Test
    fun repeatedDstWallClockHoursKeepDistinctSelectableInstants() {
        val start = Instant.parse("2026-11-01T05:00:00Z").epochSeconds
        val slots = timelineSlots((0..2).map { hour.copy(epochSeconds = start + it * 3_600) })
        assertEquals(3, slots.map { it.epochSeconds }.distinct().size)
        assertEquals(2 * 3_600, slots.last().epochSeconds - slots.first().epochSeconds)
    }
}
