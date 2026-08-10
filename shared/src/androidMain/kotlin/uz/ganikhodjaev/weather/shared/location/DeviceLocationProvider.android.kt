package uz.ganikhodjaev.weather.shared.location

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import android.os.Build
import android.os.CancellationSignal
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.core.content.ContextCompat
import java.util.TimeZone
import kotlin.coroutines.resume
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import uz.ganikhodjaev.weather.shared.PlatformContext

@Composable
internal actual fun rememberDeviceLocationProvider(
    platformContext: PlatformContext
): DeviceLocationProvider {
    val activity = platformContext.activity
    val permissionResult = remember { PermissionResult() }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> permissionResult.complete(granted) }

    return remember(activity, permissionLauncher) {
        DeviceLocationProvider {
            val alreadyGranted = ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.ACCESS_COARSE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
            val granted = alreadyGranted ||
                permissionResult.request {
                    permissionLauncher.launch(Manifest.permission.ACCESS_COARSE_LOCATION)
                }
            if (!granted) {
                DeviceLocationResult.PermissionDenied
            } else {
                val manager = activity.getSystemService(Context.LOCATION_SERVICE) as LocationManager
                if (!manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) &&
                    !manager.isProviderEnabled(LocationManager.GPS_PROVIDER)
                ) {
                    DeviceLocationResult.ServicesDisabled
                } else {
                    withTimeoutOrNull(12_000) { manager.currentCoarseLocation() }?.let { location ->
                        DeviceLocationResult.Success(
                            DeviceCoordinates(
                                latitude = location.latitude,
                                longitude = location.longitude,
                                timezone = TimeZone.getDefault().id
                            )
                        )
                    } ?: DeviceLocationResult.Failed("A current location was not available.")
                }
            }
        }
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
