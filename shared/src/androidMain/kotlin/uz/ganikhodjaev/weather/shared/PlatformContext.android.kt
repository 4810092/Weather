package uz.ganikhodjaev.weather.shared

import android.app.Activity
import android.content.Context

actual class PlatformContext {
    internal val applicationContext: Context
    internal val activity: Activity?

    constructor(activity: Activity) {
        applicationContext = activity.applicationContext
        this.activity = activity
    }

    constructor(context: Context) {
        applicationContext = context.applicationContext
        activity = null
    }

    internal fun requireActivity(): Activity = requireNotNull(activity) {
        "This operation requires a foreground activity"
    }
}
