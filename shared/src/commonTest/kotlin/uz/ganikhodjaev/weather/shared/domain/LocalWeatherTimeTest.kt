package uz.ganikhodjaev.weather.shared.domain

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.time.Instant
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toInstant
import kotlinx.datetime.toLocalDateTime

class LocalWeatherTimeTest {
    private val newYork = TimeZone.of("America/New_York")

    @Test
    fun sameLocalTimeUsesCalendarDayAcrossSpringDst() {
        val current = LocalDateTime(2026, 3, 8, 12, 0).toInstant(newYork)
        val prior = sameLocalTimeDaysAgo(current.epochSeconds, newYork.id, daysAgo = 1)
        val localPrior = Instant.fromEpochSeconds(prior).toLocalDateTime(newYork)

        assertEquals(LocalDateTime(2026, 3, 7, 12, 0), localPrior)
        assertEquals(23L * 60L * 60L, current.epochSeconds - prior)
    }

    @Test
    fun sameLocalTimeUsesCalendarDayAcrossFallDst() {
        val current = LocalDateTime(2026, 11, 1, 12, 0).toInstant(newYork)
        val prior = sameLocalTimeDaysAgo(current.epochSeconds, newYork.id, daysAgo = 1)
        val localPrior = Instant.fromEpochSeconds(prior).toLocalDateTime(newYork)

        assertEquals(LocalDateTime(2026, 10, 31, 12, 0), localPrior)
        assertEquals(25L * 60L * 60L, current.epochSeconds - prior)
    }

    @Test
    fun timelineIsAnExactPlusMinus24HourInstantWindowAcrossDst() {
        val current = LocalDateTime(2026, 11, 1, 1, 30).toInstant(newYork).epochSeconds
        val values = listOf(
            current - 24L * 60L * 60L - 1L,
            current - 24L * 60L * 60L,
            current,
            current + 24L * 60L * 60L,
            current + 24L * 60L * 60L + 1L
        )

        assertEquals(values.subList(1, 4), timelineWithinHours(values, current, 24) { it })
    }

    @Test
    fun localDateDaysAgoUsesCalendarDateNearMidnight() {
        val current = LocalDateTime(2026, 1, 1, 0, 15).toInstant(newYork)

        assertEquals(
            kotlinx.datetime.LocalDate(2025, 12, 31),
            localDateDaysAgo(current.epochSeconds, newYork.id, daysAgo = 1)
        )
    }
}
