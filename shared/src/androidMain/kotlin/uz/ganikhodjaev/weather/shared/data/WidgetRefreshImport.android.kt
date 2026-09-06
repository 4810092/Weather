package uz.ganikhodjaev.weather.shared.data

internal actual suspend fun importPendingWidgetRefreshFromPlatform(
    repository: WeatherRepository
): Boolean = false
