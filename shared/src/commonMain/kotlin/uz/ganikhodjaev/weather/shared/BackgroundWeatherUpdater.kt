package uz.ganikhodjaev.weather.shared

import kotlinx.coroutines.flow.filterNotNull
import kotlinx.coroutines.flow.first
import uz.ganikhodjaev.weather.shared.model.resolve
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

class BackgroundWeatherUpdater(platformContext: PlatformContext) {
    private val context = platformContext
    private val repository = NimboContainer(platformContext).weatherRepository

    suspend fun refresh(): Boolean = runCatching {
        val location = repository.activeLocation() ?: return false
        val refreshedFromNetwork = runCatching {
            repository.refreshPrimary(location)
            true
        }.getOrDefault(false)
        if (refreshedFromNetwork) runCatching { repository.refreshAirQuality(location) }
        val snapshot = repository.observe(location).filterNotNull().first()
        val units = repository.unitPreference().resolve(automaticUnitSystem())
        publishWeatherSnapshot(
            platformContext = context,
            snapshot = snapshot,
            displayUnits = units,
            allowReview = false
        )
        refreshedFromNetwork
    }.getOrDefault(false)
}
