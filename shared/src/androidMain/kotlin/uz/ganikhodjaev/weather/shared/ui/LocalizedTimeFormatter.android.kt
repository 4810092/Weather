package uz.ganikhodjaev.weather.shared.ui

import java.text.DateFormat
import java.util.Date
import java.util.TimeZone

internal actual fun formatLocalHour(epochSeconds: Long, timezone: String): String =
    DateFormat.getTimeInstance(DateFormat.SHORT).apply {
        timeZone = TimeZone.getTimeZone(timezone)
    }.format(Date(epochSeconds * 1_000L))
