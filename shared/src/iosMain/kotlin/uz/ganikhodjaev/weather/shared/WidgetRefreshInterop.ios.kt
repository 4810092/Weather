package uz.ganikhodjaev.weather.shared

import kotlin.native.concurrent.ThreadLocal

/** Synchronous JSON RPC implemented by the iOS App Group store. */
public interface WidgetRefreshBridge {
    public fun exchange(request: String): String
}

/**
 * Installed by AppDelegate before NimboContainer is created.  Keeping this
 * bridge in Kotlin makes the widget store the single authority for values that
 * must be atomic across the app and WidgetKit extension.
 */
@ThreadLocal
public object WidgetRefreshInterop {
    private var bridge: WidgetRefreshBridge? = null

    public fun install(bridge: WidgetRefreshBridge) {
        this.bridge = bridge
    }

    internal fun exchange(request: String): String? = bridge?.exchange(request)
}
