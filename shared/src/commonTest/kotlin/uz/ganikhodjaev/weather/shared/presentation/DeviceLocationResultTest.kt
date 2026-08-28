package uz.ganikhodjaev.weather.shared.presentation

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import uz.ganikhodjaev.weather.shared.location.DeviceLocationResult
import uz.ganikhodjaev.weather.shared.model.Location

class DeviceLocationResultTest {
    @Test
    fun deniedLocationKeepsTheUserInTheRecoverableCitySelectionFlow() {
        assertEquals(
            UiMessage.LocationPermissionDenied,
            DeviceLocationResult.PermissionDenied.locationFailureMessage()
        )
    }

    @Test
    fun disabledServicesAndUnavailableFixMapToDistinctMessages() {
        assertEquals(
            UiMessage.LocationServicesDisabled,
            DeviceLocationResult.ServicesDisabled.locationFailureMessage()
        )
        assertEquals(
            UiMessage.LocationUnavailable,
            DeviceLocationResult.Failed("timeout").locationFailureMessage()
        )
    }

    @Test
    fun emptyForecastErrorCanRecoverToANonCancellableLocationPicker() {
        val active = Location(
            id = "quick:tashkent",
            name = "Toshkent",
            country = "Uzbekistan",
            latitude = 41.2995,
            longitude = 69.2401,
            timezone = "Asia/Tashkent"
        )

        val picker = WeatherUiState.EmptyError(UiMessage.WeatherUnavailable)
            .toLocationPicker(savedLocations = listOf(active), activeLocationId = active.id)

        requireNotNull(picker)
        assertEquals(active.id, picker.activeLocationId)
        assertEquals(listOf(active), picker.savedLocations)
        assertTrue(picker.quickLocations.isNotEmpty())
        assertFalse(picker.canCancel)
    }

    @Test
    fun loadingDoesNotExposeLocationPickerRecovery() {
        assertNull(
            WeatherUiState.Loading.toLocationPicker(
                savedLocations = emptyList(),
                activeLocationId = null
            )
        )
    }
}
