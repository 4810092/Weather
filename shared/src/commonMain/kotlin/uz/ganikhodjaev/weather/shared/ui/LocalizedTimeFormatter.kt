package uz.ganikhodjaev.weather.shared.ui

internal expect fun formatLocalHour(epochSeconds: Long, timezone: String): String
