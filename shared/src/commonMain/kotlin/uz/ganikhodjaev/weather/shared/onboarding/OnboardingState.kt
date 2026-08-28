package uz.ganikhodjaev.weather.shared.onboarding

import uz.ganikhodjaev.weather.shared.PlatformContext
import uz.ganikhodjaev.weather.shared.model.Location

internal data class OnboardingState(
    val hasCompletedFirstForecast: Boolean = false,
    val hasShownFirstForecastTip: Boolean = false
)

internal interface OnboardingStateStore {
    fun read(): OnboardingState

    fun write(state: OnboardingState)
}

internal expect fun createOnboardingStateStore(
    platformContext: PlatformContext
): OnboardingStateStore

internal enum class UzbekistanQuickCity {
    Tashkent,
    Samarkand,
    Namangan,
    Andijan,
    Fergana,
    Bukhara,
    Nukus
}

internal data class UzbekistanQuickLocation(
    val city: UzbekistanQuickCity,
    val id: String,
    val latitude: Double,
    val longitude: Double
) {
    fun localized(name: String, country: String): Location = Location(
        id = id,
        name = name,
        country = country,
        latitude = latitude,
        longitude = longitude,
        timezone = UZBEKISTAN_TIMEZONE
    )
}

internal object UzbekistanQuickLocations {
    val all: List<UzbekistanQuickLocation> = listOf(
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Tashkent,
            id = "quick:uz:tashkent",
            latitude = 41.2995,
            longitude = 69.2401
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Samarkand,
            id = "quick:uz:samarkand",
            latitude = 39.6542,
            longitude = 66.9597
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Namangan,
            id = "quick:uz:namangan",
            latitude = 40.9983,
            longitude = 71.6726
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Andijan,
            id = "quick:uz:andijan",
            latitude = 40.7821,
            longitude = 72.3442
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Fergana,
            id = "quick:uz:fergana",
            latitude = 40.3894,
            longitude = 71.7870
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Bukhara,
            id = "quick:uz:bukhara",
            latitude = 39.7747,
            longitude = 64.4286
        ),
        UzbekistanQuickLocation(
            city = UzbekistanQuickCity.Nukus,
            id = "quick:uz:nukus",
            latitude = 42.4600,
            longitude = 59.6166
        )
    )
}

private const val UZBEKISTAN_TIMEZONE = "Asia/Tashkent"
