package uz.ganikhodjaev.weather.shared.ui

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.time.Instant
import kotlinx.datetime.LocalDate
import uz.ganikhodjaev.weather.shared.model.AirQualityHour
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class ForecastPresentationTest {
    @Test
    fun recentDaysRunOldestToCurrentDayWithNoFutureOrDuplicateSamples() {
        val now = Instant.parse("2026-10-04T08:00:00Z").epochSeconds
        val current = hour(now)
        val history = (1..8).map { hour(now - it * 86_400) } + listOf(
            hour(now + 3_600).copy(temperatureC = 80.0),
            hour(now).copy(temperatureC = -90.0),
            hour(now - 3_600).copy(temperatureC = 10.0)
        )
        val days = recentDaySummaries(snapshot(current, history.reversed()))
        assertEquals(
            listOf(
                "2026-09-27",
                "2026-09-28",
                "2026-09-29",
                "2026-09-30",
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
                "2026-10-04"
            ),
            days.map { weatherDate(it.epochSeconds, it.timezone).toString() }
        )
        assertEquals(15.0, days.last().averageC)
        assertEquals(10.0, days.last().lowC)
        assertEquals(20.0, days.last().highC)
    }

    @Test
    fun recentDaysUseCityMidnightAcrossDstAndKeepMissingDaysAbsent() {
        val current = hour(Instant.parse("2026-03-08T08:00:00Z").epochSeconds)
        val history = listOf(
            hour(Instant.parse("2026-03-08T04:30:00Z").epochSeconds).copy(temperatureC = 4.0),
            hour(Instant.parse("2026-03-08T05:30:00Z").epochSeconds).copy(temperatureC = 10.0)
        )
        val days = recentDaySummaries(snapshot(current, history, "America/New_York"))
        assertEquals(
            listOf("2026-03-07", "2026-03-08"),
            days.map { weatherDate(it.epochSeconds, it.timezone).toString() }
        )
        assertEquals(4.0, days.first().averageC)
        assertEquals(15.0, days.last().averageC)
    }

    @Test
    fun savedSnapshotKeepsActualDatesAndDoesNotInventTodaysHistory() {
        val current = hour(Instant.parse("2026-10-03T20:00:00Z").epochSeconds)
        val stale = snapshot(current, emptyList()).copy(
            isStale = true,
            fetchedAtEpochSeconds = current.epochSeconds + 7 * 86_400
        )
        val days = recentDaySummaries(stale)
        assertEquals(1, days.size)
        assertEquals(
            LocalDate(2026, 10, 4),
            weatherDate(days.single().epochSeconds, days.single().timezone)
        )
        assertEquals(20.0, days.single().averageC)
        val fallback =
            recentDaySummaries(stale.copy(location = stale.location.copy(timezone = "invalid")))
        assertEquals(
            LocalDate(2026, 10, 3),
            weatherDate(fallback.single().epochSeconds, fallback.single().timezone)
        )
    }

    @Test
    fun currentSlotUsesHalfOpenHourAndNeverNearbyFutureHour() {
        val hours = listOf(hour(3_600), hour(7_200))
        assertNull(currentHourIndex(hours, 3_599))
        assertEquals(0, currentHourIndex(hours, 3_600))
        assertEquals(0, currentHourIndex(hours, 7_199))
        assertEquals(1, currentHourIndex(hours, 7_200))
        assertNull(currentHourIndex(hours, 10_800))
        assertNull(currentHourIndex(emptyList(), 3_600))
    }

    @Test
    fun missingSelectedTimestampFallsBackToCurrentSlotThenFirstAvailableHour() {
        val hours = listOf(hour(3_600), hour(7_200))
        assertEquals(hours[0], selectedForecastHour(hours, 3_600, 7_500))
        assertEquals(hours[1], selectedForecastHour(hours, 999, 7_500))
        assertEquals(hours[1], selectedForecastHour(hours, null, 7_500))
        assertEquals(hours[0], selectedForecastHour(hours, 999, 20_000))
        assertNull(selectedForecastHour(emptyList(), 999, 7_500))
    }

    @Test
    fun datesUseCityMidnightAndFallbackToUtcForInvalidZone() {
        val epoch = Instant.parse("2026-10-03T20:00:00Z").epochSeconds
        assertEquals(LocalDate(2026, 10, 4), weatherDate(epoch, "Asia/Tashkent"))
        assertEquals(LocalDate(2026, 10, 3), weatherDate(epoch, "America/New_York"))
        assertEquals(LocalDate(2026, 10, 3), weatherDate(epoch, "not/a/timezone"))
    }

    @Test
    fun repeatedDstHourStillUsesDistinctEpochSlotsAndCorrectLocalDate() {
        val first = Instant.parse("2026-11-01T05:00:00Z").epochSeconds
        val second = Instant.parse("2026-11-01T06:00:00Z").epochSeconds
        val hours = listOf(hour(first), hour(second))
        assertEquals(0, currentHourIndex(hours, first + 1_800))
        assertEquals(1, currentHourIndex(hours, second + 1_800))
        assertEquals(LocalDate(2026, 11, 1), weatherDate(first, "America/New_York"))
        assertEquals(LocalDate(2026, 11, 1), weatherDate(second, "America/New_York"))
    }

    @Test
    fun airQualityStalenessUsesFetchAgeCoverageAndFutureClockSkew() {
        val now = 100_000L
        val recent = air(now - 1_800, now - 100)
        assertFalse(isAirQualityStale(recent, now))
        assertFalse(isAirQualityStale(recent.copy(fetchedAtEpochSeconds = now - 21_600), now))
        assertTrue(isAirQualityStale(recent.copy(fetchedAtEpochSeconds = now - 21_601), now))
        assertTrue(isAirQualityStale(recent.copy(epochSeconds = now - 3_601), now))
        assertTrue(isAirQualityStale(recent.copy(epochSeconds = now + 1), now))
        assertFalse(isAirQualityStale(recent.copy(fetchedAtEpochSeconds = now + 300), now))
        assertTrue(isAirQualityStale(recent.copy(fetchedAtEpochSeconds = now + 301), now))
    }

    @Test
    fun serviceUrlsMatchLocalizedPublicRoutes() {
        assertEquals("https://nimbo.uz/", servicePageUrl("uz-UZ"))
        assertEquals("https://nimbo.uz/support/", servicePageUrl("uz", "support"))
        assertEquals("https://nimbo.uz/ru/privacy/", servicePageUrl("RU_ru", "privacy"))
        assertEquals("https://nimbo.uz/en/support/", servicePageUrl("en-US", "support"))
        assertEquals("https://nimbo.uz/en/", servicePageUrl("de"))
        assertFailsWith<IllegalArgumentException> { servicePageUrl("en", "../private") }
    }

    private fun hour(epoch: Long) =
        WeatherHour(epoch, 20.0, 20.0, 0, 0, 0.0, 5.0, 8.0, 40, 1.0, epoch)

    private fun snapshot(
        current: WeatherHour,
        history: List<WeatherHour>,
        timezone: String = "Asia/Tashkent"
    ) = WeatherSnapshot(
        location = Location("test", "Test", "", 0.0, 0.0, timezone),
        current = current,
        timeline = listOf(current),
        recentHistory = history,
        fetchedAtEpochSeconds = current.epochSeconds,
        isStale = false
    )

    private fun air(epoch: Long, fetched: Long) =
        AirQualityHour(epoch, 50, 10.0, 20.0, null, null, null, fetched)
}
