package uz.ganikhodjaev.weather.shared.units

import platform.Foundation.NSLocale
import platform.Foundation.countryCode
import platform.Foundation.currentLocale
import uz.ganikhodjaev.weather.shared.model.UnitSystem

internal actual fun automaticUnitSystem(): UnitSystem = when (
    NSLocale.currentLocale.countryCode?.uppercase()
) {
    "US", "LR", "MM" -> UnitSystem.Imperial
    else -> UnitSystem.Metric
}
