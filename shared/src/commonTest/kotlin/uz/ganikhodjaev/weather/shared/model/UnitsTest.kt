package uz.ganikhodjaev.weather.shared.model

import kotlin.test.Test
import kotlin.test.assertEquals

class UnitsTest {
    @Test
    fun convertsSiValuesAtTheDisplayBoundary() {
        val imperial = DisplayUnits(UnitSystem.Imperial)

        assertEquals(68, imperial.temperature(20.0))
        assertEquals(62, imperial.wind(100.0))
        assertEquals(1.0, imperial.precipitation(25.4), absoluteTolerance = 0.0001)
    }

    @Test
    fun resolvesAutomaticWithoutChangingStoredPreference() {
        assertEquals(UnitSystem.Imperial, UnitPreference.Automatic.resolve(UnitSystem.Imperial).system)
        assertEquals(UnitSystem.Metric, UnitPreference.Metric.resolve(UnitSystem.Imperial).system)
    }
}
