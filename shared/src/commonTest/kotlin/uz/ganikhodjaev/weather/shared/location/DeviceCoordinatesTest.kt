package uz.ganikhodjaev.weather.shared.location

import kotlin.test.Test
import kotlin.test.assertEquals

class DeviceCoordinatesTest {
    @Test
    fun deviceCoordinatesAreReducedBeforeStorageOrNetworkUse() {
        val coordinates = DeviceCoordinates(41.311081, 69.240562, "Asia/Tashkent")

        assertEquals(
            DeviceCoordinates(41.31, 69.24, "Asia/Tashkent"),
            coordinates.coarsened()
        )
    }

    @Test
    fun negativeCoordinatesRoundSymmetrically() {
        val coordinates = DeviceCoordinates(-33.868820, -70.669265, "America/Santiago")

        assertEquals(-33.87, coordinates.coarsened().latitude)
        assertEquals(-70.67, coordinates.coarsened().longitude)
    }
}
