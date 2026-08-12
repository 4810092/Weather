package uz.ganikhodjaev.weather.shared

import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal expect fun publishWeatherSnapshot(
    platformContext: PlatformContext,
    snapshot: WeatherSnapshot,
    displayUnits: DisplayUnits,
    allowReview: Boolean = true
)
