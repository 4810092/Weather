package uz.ganikhodjaev.weather.shared.units

import java.util.Locale
import uz.ganikhodjaev.weather.shared.model.UnitSystem

internal actual fun automaticUnitSystem(): UnitSystem =
    when (Locale.getDefault().country.uppercase()) {
        "US", "LR", "MM" -> UnitSystem.Imperial
        else -> UnitSystem.Metric
    }
