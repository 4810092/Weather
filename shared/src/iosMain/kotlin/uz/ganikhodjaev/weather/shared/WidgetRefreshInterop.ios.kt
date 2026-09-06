package uz.ganikhodjaev.weather.shared

import platform.Foundation.NSLock

/** Synchronous JSON RPC implemented by the iOS App Group store. */
public interface WidgetRefreshBridge {
    public fun exchange(request: String): String
}

/**
 * Installed by AppDelegate before NimboContainer is created.  Keeping this
 * bridge in Kotlin makes the widget store the single authority for values that
 * must be atomic across the app and WidgetKit extension.
 */
public object WidgetRefreshInterop {
    private val lock = NSLock()
    private var bridge: WidgetRefreshBridge? = null

    public fun install(bridge: WidgetRefreshBridge) {
        lock.lock()
        try {
            this.bridge = bridge
        } finally {
            lock.unlock()
        }
    }

    internal fun exchange(request: String): String? {
        lock.lock()
        val installed = try { bridge } finally { lock.unlock() }
        return installed?.exchange(request)
    }
}
