package uz.ganikhodjaev.weather.shared.ui

import kotlin.time.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.domain.localDateDaysAgo
import uz.ganikhodjaev.weather.shared.model.AirQualityHour
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal fun weatherDate(epochSeconds: Long, timezone: String): LocalDate =
    Instant.fromEpochSeconds(epochSeconds).toLocalDateTime(
        runCatching { TimeZone.of(timezone) }.getOrElse { TimeZone.UTC }
    ).date

internal data class RecentDaySummary(
    val epochSeconds: Long,
    val timezone: String,
    val averageC: Double,
    val lowC: Double,
    val highC: Double
)

/** Seven preceding calendar days and the current day, using only data through the snapshot hour. */
internal fun recentDaySummaries(weather: WeatherSnapshot): List<RecentDaySummary> {
    val timezone = weather.location.timezone
    val hoursByDate = (listOf(weather.current) + weather.recentHistory)
        .distinctBy { it.epochSeconds }
        .filter { it.epochSeconds <= weather.current.epochSeconds }
        .groupBy { weatherDate(it.epochSeconds, timezone) }
    return (7 downTo 0).mapNotNull { daysAgo ->
        val date = localDateDaysAgo(weather.current.epochSeconds, timezone, daysAgo)
        val hours = hoursByDate[date] ?: return@mapNotNull null
        RecentDaySummary(
            epochSeconds = hours.minOf { it.epochSeconds },
            timezone = timezone,
            averageC = hours.map { it.temperatureC }.average(),
            lowC = hours.minOf { it.temperatureC },
            highC = hours.maxOf { it.temperatureC }
        )
    }
}

/** A current slot contains now; a nearby future hour is never labelled “now”. */
internal fun currentHourIndex(hours: List<WeatherHour>, now: Long): Int? =
    hours.indexOfLast { now >= it.epochSeconds && now < it.epochSeconds + 3_600 }
        .takeIf { it >= 0 }

internal fun selectedForecastHour(
    hours: List<WeatherHour>,
    selected: Long?,
    now: Long
): WeatherHour? = hours.firstOrNull { it.epochSeconds == selected }
    ?: currentHourIndex(hours, now)?.let(hours::get)
    ?: hours.firstOrNull()

internal fun isAirQualityStale(air: AirQualityHour, now: Long): Boolean =
    now - air.fetchedAtEpochSeconds > 6 * 3_600 ||
        now !in air.epochSeconds..(air.epochSeconds + 3_600) ||
        air.fetchedAtEpochSeconds > now + 300

internal fun servicePageUrl(language: String, page: String = ""): String {
    val prefix = when (language.lowercase().substringBefore('-').substringBefore('_')) {
        "uz" -> ""
        "ru" -> "ru/"
        else -> "en/"
    }
    require(page in setOf("", "support", "privacy"))
    return "https://nimbo.uz/$prefix" + if (page.isBlank()) "" else "$page/"
}
