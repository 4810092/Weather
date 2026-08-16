package uz.ganikhodjaev.weather.shared.location

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Address
import android.location.Geocoder
import android.location.Location
import android.location.LocationManager
import android.os.Build
import android.os.CancellationSignal
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.core.content.ContextCompat
import java.util.Locale
import java.util.TimeZone
import kotlin.coroutines.resume
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import uz.ganikhodjaev.weather.shared.PlatformContext

@Composable
internal actual fun rememberDeviceLocationProvider(
    platformContext: PlatformContext
): DeviceLocationProvider {
    val activity = platformContext.requireActivity()
    val permissionResult = remember { PermissionResult() }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> permissionResult.complete(granted) }

    return remember(activity, permissionLauncher) {
        object : DeviceLocationProvider {
            override suspend fun requestCurrentLocation(): DeviceLocationResult {
                val alreadyGranted = ContextCompat.checkSelfPermission(
                    activity,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                ) == PackageManager.PERMISSION_GRANTED
                val granted = alreadyGranted ||
                    permissionResult.request {
                        permissionLauncher.launch(Manifest.permission.ACCESS_COARSE_LOCATION)
                    }
                return if (!granted) {
                    DeviceLocationResult.PermissionDenied
                } else {
                    val manager = activity.getSystemService(
                        Context.LOCATION_SERVICE
                    ) as LocationManager
                    if (!manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) &&
                        !manager.isProviderEnabled(LocationManager.GPS_PROVIDER)
                    ) {
                        DeviceLocationResult.ServicesDisabled
                    } else {
                        withTimeoutOrNull(12_000) {
                            manager.currentCoarseLocation()
                        }?.let { location ->
                            DeviceLocationResult.Success(
                                DeviceCoordinates(
                                    latitude = location.latitude,
                                    longitude = location.longitude,
                                    timezone = TimeZone.getDefault().id
                                )
                            )
                        } ?: DeviceLocationResult.Failed(
                            "A current location was not available."
                        )
                    }
                }
            }

            override suspend fun resolvePlace(coordinates: DeviceCoordinates): DevicePlace? =
                activity.reverseGeocode(coordinates)
        }
    }
}

private suspend fun Context.reverseGeocode(coordinates: DeviceCoordinates): DevicePlace? {
    if (!Geocoder.isPresent()) return null
    val geocoder = Geocoder(this, Locale.getDefault())
    val addresses = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        geocoder.reverseGeocodeAsync(coordinates)
    } else {
        withContext(Dispatchers.IO) {
            @Suppress("DEPRECATION")
            runCatching {
                geocoder.getFromLocation(coordinates.latitude, coordinates.longitude, 1)
            }.getOrNull().orEmpty()
        }
    }
    val address = addresses.firstOrNull() ?: return null
    val name = sequenceOf(address.locality, address.subAdminArea, address.adminArea)
        .firstOrNull { !it.isNullOrBlank() }
        .orEmpty()
    return DevicePlace(name = name, country = address.countryName.orEmpty())
        .takeIf { it.name.isNotBlank() || it.country.isNotBlank() }
}

private suspend fun Geocoder.reverseGeocodeAsync(coordinates: DeviceCoordinates): List<Address> =
    suspendCancellableCoroutine { continuation ->
        try {
            getFromLocation(
                coordinates.latitude,
                coordinates.longitude,
                1,
                object : Geocoder.GeocodeListener {
                    override fun onGeocode(addresses: MutableList<Address>) {
                        if (continuation.isActive) continuation.resume(addresses)
                    }

                    override fun onError(errorMessage: String?) {
                        if (continuation.isActive) continuation.resume(emptyList())
                    }
                }
            )
        } catch (_: Throwable) {
            if (continuation.isActive) continuation.resume(emptyList())
        }
    }

private class PermissionResult {
    private var pending: CompletableDeferred<Boolean>? = null

    suspend fun request(launch: () -> Unit): Boolean {
        val deferred = CompletableDeferred<Boolean>()
        pending?.cancel()
        pending = deferred
        launch()
        return deferred.await()
    }

    fun complete(granted: Boolean) {
        pending?.complete(granted)
        pending = null
    }
}

private suspend fun LocationManager.currentCoarseLocation(): Location? =
    suspendCancellableCoroutine { continuation ->
        val provider = when {
            isProviderEnabled(LocationManager.NETWORK_PROVIDER) -> LocationManager.NETWORK_PROVIDER
            isProviderEnabled(LocationManager.GPS_PROVIDER) -> LocationManager.GPS_PROVIDER
            else -> {
                continuation.resume(null)
                return@suspendCancellableCoroutine
            }
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val signal = CancellationSignal()
            continuation.invokeOnCancellation { signal.cancel() }
            getCurrentLocation(provider, signal, { runnable -> runnable.run() }) { location ->
                if (continuation.isActive) continuation.resume(location)
            }
        } else {
            @Suppress("DEPRECATION")
            requestSingleUpdate(provider, { location ->
                if (continuation.isActive) continuation.resume(location)
            }, null)
        }
    }
