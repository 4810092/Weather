package uz.ganikhodjaev.weather.shared.ui

import platform.Foundation.NSDate
import platform.Foundation.NSDateFormatter
import platform.Foundation.NSLocale
import platform.Foundation.NSTimeZone
import platform.Foundation.currentLocale
import platform.Foundation.dateWithTimeIntervalSince1970
import platform.Foundation.timeZoneWithName

internal actual fun formatLocalHour(epochSeconds: Long, timezone: String): String {
    val formatter = NSDateFormatter().apply {
        locale = NSLocale.currentLocale
        dateStyle = 0u
        timeStyle = 1u
        NSTimeZone.timeZoneWithName(timezone)?.let { timeZone = it }
    }
    return formatter.stringFromDate(NSDate.dateWithTimeIntervalSince1970(epochSeconds.toDouble()))
}

internal actual fun formatLocalDay(epochSeconds: Long, timezone: String): String {
    val formatter = NSDateFormatter().apply {
        locale = NSLocale.currentLocale
        dateStyle = 2u
        timeStyle = 0u
        NSTimeZone.timeZoneWithName(timezone)?.let { timeZone = it }
    }
    return formatter.stringFromDate(NSDate.dateWithTimeIntervalSince1970(epochSeconds.toDouble()))
}
