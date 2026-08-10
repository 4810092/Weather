package uz.ganikhodjaev.weather.shared.domain

import kotlin.time.Instant
import kotlinx.datetime.DateTimeUnit
import kotlinx.datetime.LocalDate
import kotlinx.datetime.LocalDateTime
import kotlinx.datetime.TimeZone
import kotlinx.datetime.minus
import kotlinx.datetime.toInstant
import kotlinx.datetime.toLocalDateTime

internal fun localDateDaysAgo(epochSeconds: Long, timezone: String, daysAgo: Int): LocalDate {
    val zone = safeTimeZone(timezone)
    return Instant.fromEpochSeconds(epochSeconds)
        .toLocalDateTime(zone)
        .date
        .minus(daysAgo, DateTimeUnit.DAY)
}

internal fun sameLocalTimeDaysAgo(epochSeconds: Long, timezone: String, daysAgo: Int): Long {
    val zone = safeTimeZone(timezone)
    val current = Instant.fromEpochSeconds(epochSeconds).toLocalDateTime(zone)
    return LocalDateTime(
        date = current.date.minus(daysAgo, DateTimeUnit.DAY),
        time = current.time
    ).toInstant(zone).epochSeconds
}

internal fun <T> timelineWithinHours(
    values: List<T>,
    currentEpochSeconds: Long,
    hours: Int,
    epochSeconds: (T) -> Long
): List<T> {
    val radius = hours * 60L * 60L
    return values.filter { value ->
        epochSeconds(value) in (currentEpochSeconds - radius)..(currentEpochSeconds + radius)
    }
}

private fun safeTimeZone(timezone: String): TimeZone =
    runCatching { TimeZone.of(timezone) }.getOrElse { TimeZone.UTC }
