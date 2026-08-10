package uz.ganikhodjaev.weather.shared.location

import androidx.compose.runtime.Composable
import kotlin.math.round
import uz.ganikhodjaev.weather.shared.PlatformContext

internal data class DeviceCoordinates(
    val latitude: Double,
    val longitude: Double,
    val timezone: String
)

internal fun DeviceCoordinates.coarsened(): DeviceCoordinates = copy(
    latitude = latitude.coarseCoordinate(),
    longitude = longitude.coarseCoordinate()
)

private fun Double.coarseCoordinate(): Double = round(this * 100.0) / 100.0

internal sealed interface DeviceLocationResult {
    data class Success(val coordinates: DeviceCoordinates) : DeviceLocationResult
    data object PermissionDenied : DeviceLocationResult
    data object ServicesDisabled : DeviceLocationResult
    data class Failed(val reason: String) : DeviceLocationResult
}

internal fun interface DeviceLocationProvider {
    suspend fun requestCurrentLocation(): DeviceLocationResult
}

@Composable
internal expect fun rememberDeviceLocationProvider(
    platformContext: PlatformContext
): DeviceLocationProvider
