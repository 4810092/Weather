package uz.ganikhodjaev.weather.shared.location

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.useContents
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.datetime.TimeZone
import platform.CoreLocation.CLLocation
import platform.CoreLocation.CLLocationManager
import platform.CoreLocation.CLLocationManagerDelegateProtocol
import platform.CoreLocation.kCLAuthorizationStatusAuthorizedAlways
import platform.CoreLocation.kCLAuthorizationStatusAuthorizedWhenInUse
import platform.CoreLocation.kCLAuthorizationStatusDenied
import platform.CoreLocation.kCLAuthorizationStatusNotDetermined
import platform.CoreLocation.kCLAuthorizationStatusRestricted
import platform.Foundation.NSError
import platform.darwin.NSObject
import uz.ganikhodjaev.weather.shared.PlatformContext
import kotlin.coroutines.Continuation
import kotlin.coroutines.resume

@Composable
internal actual fun rememberDeviceLocationProvider(
    platformContext: PlatformContext,
): DeviceLocationProvider = remember(platformContext) { IosDeviceLocationProvider() }

@OptIn(ExperimentalForeignApi::class)
private class IosDeviceLocationProvider : DeviceLocationProvider {
    private val manager = CLLocationManager()
    private var continuation: Continuation<DeviceLocationResult>? = null
    private val delegate = LocationDelegate(
        onAuthorizationChanged = ::authorizationChanged,
        onLocations = ::locationsUpdated,
        onError = ::locationFailed,
    )

    init {
        manager.delegate = delegate
        manager.desiredAccuracy = 3_000.0
    }

    override suspend fun requestCurrentLocation(): DeviceLocationResult =
        withTimeoutOrNull(12_000) {
            suspendCancellableCoroutine { next ->
            continuation?.resume(DeviceLocationResult.Failed("A newer location request replaced this one."))
            continuation = next
            next.invokeOnCancellation { continuation = null }
            when (manager.authorizationStatus) {
                kCLAuthorizationStatusDenied,
                kCLAuthorizationStatusRestricted -> finish(
                    DeviceLocationResult.PermissionDenied,
                )
                kCLAuthorizationStatusNotDetermined ->
                    manager.requestWhenInUseAuthorization()
                else -> requestIfAvailable()
            }
            }
        } ?: DeviceLocationResult.Failed("A current location wasn't available in time.")

    private fun authorizationChanged(manager: CLLocationManager) {
        if (continuation == null) return
        when (manager.authorizationStatus) {
            kCLAuthorizationStatusDenied,
            kCLAuthorizationStatusRestricted -> finish(
                DeviceLocationResult.PermissionDenied,
            )
            kCLAuthorizationStatusAuthorizedAlways,
            kCLAuthorizationStatusAuthorizedWhenInUse -> requestIfAvailable()
            else -> Unit
        }
    }

    private fun locationsUpdated(didUpdateLocations: List<*>) {
        val location = didUpdateLocations.lastOrNull() as? CLLocation ?: return
        finish(
            DeviceLocationResult.Success(
                DeviceCoordinates(
                    latitude = location.coordinate.useContents { latitude },
                    longitude = location.coordinate.useContents { longitude },
                    timezone = TimeZone.currentSystemDefault().id,
                ),
            ),
        )
    }

    private fun locationFailed(didFailWithError: NSError) {
        finish(DeviceLocationResult.Failed(didFailWithError.localizedDescription))
    }

    private fun requestIfAvailable() {
        if (!CLLocationManager.locationServicesEnabled()) {
            finish(DeviceLocationResult.ServicesDisabled)
        } else {
            manager.requestLocation()
        }
    }

    private fun finish(result: DeviceLocationResult) {
        continuation?.resume(result)
        continuation = null
    }
}

@OptIn(ExperimentalForeignApi::class)
private class LocationDelegate(
    private val onAuthorizationChanged: (CLLocationManager) -> Unit,
    private val onLocations: (List<*>) -> Unit,
    private val onError: (NSError) -> Unit,
) : NSObject(), CLLocationManagerDelegateProtocol {
    override fun locationManagerDidChangeAuthorization(manager: CLLocationManager) {
        onAuthorizationChanged(manager)
    }

    override fun locationManager(manager: CLLocationManager, didUpdateLocations: List<*>) {
        onLocations(didUpdateLocations)
    }

    override fun locationManager(manager: CLLocationManager, didFailWithError: NSError) {
        onError(didFailWithError)
    }
}
