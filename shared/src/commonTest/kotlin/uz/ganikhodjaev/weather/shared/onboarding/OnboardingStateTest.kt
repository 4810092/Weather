package uz.ganikhodjaev.weather.shared.onboarding

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class OnboardingStateTest {
    @Test
    fun defaultStateDoesNotSkipFirstForecastExperience() {
        val state = OnboardingState()

        assertFalse(state.hasCompletedFirstForecast)
        assertFalse(state.hasShownFirstForecastTip)
    }

    @Test
    fun quickLocationsCoverMajorUzbekistanCitiesWithoutLocationPermission() {
        val locations = UzbekistanQuickLocations.all

        assertEquals("quick:uz:tashkent", locations.first().id)
        assertEquals(7, locations.size)
        assertTrue(locations.all { it.id.startsWith("quick:uz:") })
        assertTrue(locations.all { it.latitude in 37.0..46.0 })
        assertTrue(locations.all { it.longitude in 55.0..74.0 })
        assertEquals(
            "Ташкент",
            locations.first().localized(name = "Ташкент", country = "Узбекистан").name
        )
        assertEquals(
            "Asia/Tashkent",
            locations.first().localized(name = "Toshkent", country = "O‘zbekiston").timezone
        )
    }
}
