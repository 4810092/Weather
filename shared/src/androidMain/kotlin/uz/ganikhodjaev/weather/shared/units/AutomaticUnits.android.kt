package uz.ganikhodjaev.weather.shared.units

import uz.ganikhodjaev.weather.shared.model.UnitSystem
import java.util.Locale

internal actual fun automaticUnitSystem(): UnitSystem = when (Locale.getDefault().country.uppercase()) {
    "US", "LR", "MM" -> UnitSystem.Imperial
    else -> UnitSystem.Metric
}
