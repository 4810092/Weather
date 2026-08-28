package uz.ganikhodjaev.weather.shared

import io.ktor.client.engine.darwin.DarwinHttpRequestException
import platform.Foundation.NSURLErrorDomain

internal actual fun isTransientPlatformNetworkFailure(error: Throwable): Boolean {
    val visited = mutableSetOf<Throwable>()
    var current: Throwable? = error
    while (current != null && visited.add(current)) {
        val origin = (current as? DarwinHttpRequestException)?.origin
        if (
            origin != null &&
            origin.domain == NSURLErrorDomain &&
            origin.code in TRANSIENT_NS_URL_ERROR_CODES
        ) {
            return true
        }
        current = current.cause
    }
    return false
}

private val TRANSIENT_NS_URL_ERROR_CODES = setOf(
    -1001L, // timed out
    -1003L, // cannot find host
    -1004L, // cannot connect to host
    -1005L, // network connection lost
    -1006L, // DNS lookup failed
    -1009L, // not connected to the Internet
    -1018L, // international roaming is disabled
    -1019L, // call is active
    -1020L // cellular data is not allowed
)
