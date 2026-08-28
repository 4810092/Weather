package uz.ganikhodjaev.weather.shared

import java.net.ConnectException
import java.net.NoRouteToHostException
import java.net.SocketException
import java.net.UnknownHostException

internal actual fun isTransientPlatformNetworkFailure(error: Throwable): Boolean {
    val visited = mutableSetOf<Throwable>()
    var current: Throwable? = error
    while (current != null && visited.add(current)) {
        if (
            current is UnknownHostException ||
            current is ConnectException ||
            current is NoRouteToHostException ||
            current is SocketException
        ) {
            return true
        }
        current = current.cause
    }
    return false
}
