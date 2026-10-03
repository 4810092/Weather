package uz.ganikhodjaev.weather.shared.ui

import android.database.ContentObserver
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext

@Composable
internal actual fun rememberGlassPreferences(): GlassPreferences {
    val resolver = LocalContext.current.contentResolver
    fun read() = GlassPreferences(
        reduceMotion =
        Settings.Global.getFloat(resolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f,
        // Android's high-contrast text preference also needs an opaque backing.
        reduceTransparency = Settings.Secure.getInt(resolver, "high_text_contrast_enabled", 0) == 1
    )
    var preferences by remember(resolver) { mutableStateOf(read()) }
    DisposableEffect(resolver) {
        val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
            override fun onChange(selfChange: Boolean) {
                preferences = read()
            }
        }
        resolver.registerContentObserver(
            Settings.Global.getUriFor(Settings.Global.ANIMATOR_DURATION_SCALE),
            false,
            observer
        )
        resolver.registerContentObserver(
            Settings.Secure.getUriFor("high_text_contrast_enabled"),
            false,
            observer
        )
        preferences = read()
        onDispose { resolver.unregisterContentObserver(observer) }
    }
    return preferences
}
