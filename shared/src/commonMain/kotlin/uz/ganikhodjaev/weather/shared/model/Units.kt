package uz.ganikhodjaev.weather.shared.model

import kotlin.math.roundToInt

internal enum class UnitPreference {
    Automatic,
    Metric,
    Imperial,
}

internal enum class UnitSystem {
    Metric,
    Imperial,
}

internal data class DisplayUnits(
    val system: UnitSystem,
) {
    fun temperature(celsius: Double): Int = when (system) {
        UnitSystem.Metric -> celsius.roundToInt()
        UnitSystem.Imperial -> (celsius * 9.0 / 5.0 + 32.0).roundToInt()
    }

    fun wind(kilometresPerHour: Double): Int = when (system) {
        UnitSystem.Metric -> kilometresPerHour.roundToInt()
        UnitSystem.Imperial -> (kilometresPerHour * 0.621371).roundToInt()
    }

    fun precipitation(millimetres: Double): Double = when (system) {
        UnitSystem.Metric -> millimetres
        UnitSystem.Imperial -> millimetres / 25.4
    }

    val temperatureSymbol: String get() = when (system) {
        UnitSystem.Metric -> "°C"
        UnitSystem.Imperial -> "°F"
    }

    val windSymbol: String get() = when (system) {
        UnitSystem.Metric -> "km/h"
        UnitSystem.Imperial -> "mph"
    }
}

internal fun UnitPreference.resolve(automatic: UnitSystem): DisplayUnits = DisplayUnits(
    when (this) {
        UnitPreference.Automatic -> automatic
        UnitPreference.Metric -> UnitSystem.Metric
        UnitPreference.Imperial -> UnitSystem.Imperial
    },
)
