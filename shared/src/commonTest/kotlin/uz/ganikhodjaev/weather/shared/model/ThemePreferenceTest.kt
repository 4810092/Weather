package uz.ganikhodjaev.weather.shared.model

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ThemePreferenceTest {
    @Test
    fun storedValuesRoundTrip() {
        ThemePreference.entries.forEach { preference ->
            assertEquals(preference, ThemePreference.fromStoredValue(preference.name))
        }
    }

    @Test
    fun missingOrInvalidStoredValueFallsBackToSystem() {
        assertEquals(ThemePreference.System, ThemePreference.fromStoredValue(null))
        assertEquals(ThemePreference.System, ThemePreference.fromStoredValue("dark"))
        assertEquals(ThemePreference.System, ThemePreference.fromStoredValue("Unknown"))
    }

    @Test
    fun resolvesAgainstSystemAppearance() {
        assertTrue(ThemePreference.System.resolve(systemIsDark = true))
        assertFalse(ThemePreference.System.resolve(systemIsDark = false))
        assertFalse(ThemePreference.Light.resolve(systemIsDark = true))
        assertTrue(ThemePreference.Dark.resolve(systemIsDark = false))
    }
}
