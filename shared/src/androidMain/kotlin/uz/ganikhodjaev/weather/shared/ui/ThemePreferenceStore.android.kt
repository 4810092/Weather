package uz.ganikhodjaev.weather.shared.ui

import android.content.Context
import android.graphics.drawable.ColorDrawable
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.core.view.WindowCompat
import uz.ganikhodjaev.weather.shared.PlatformContext
import uz.ganikhodjaev.weather.shared.model.ThemePreference

private const val PREFERENCES_NAME = "nimbo_preferences"
private const val THEME_PREFERENCE_KEY = "theme_preference"
private const val LIGHT_BACKGROUND = 0xFFF3F7FC.toInt()
private const val DARK_BACKGROUND = 0xFF101820.toInt()

internal actual fun createThemePreferenceStore(context: PlatformContext): ThemePreferenceStore {
    val preferences = context.activity.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
    return object : ThemePreferenceStore {
        override fun read(): ThemePreference = ThemePreference.fromStoredValue(
            preferences.getString(THEME_PREFERENCE_KEY, null)
        )

        override fun write(preference: ThemePreference) {
            preferences.edit().putString(THEME_PREFERENCE_KEY, preference.name).apply()
        }
    }
}

@Composable
internal actual fun ApplyPlatformThemeAppearance(
    context: PlatformContext,
    preference: ThemePreference,
    darkTheme: Boolean
) {
    SideEffect {
        val window = context.activity.window
        window.setBackgroundDrawable(
            ColorDrawable(if (darkTheme) DARK_BACKGROUND else LIGHT_BACKGROUND)
        )
        val controller = WindowCompat.getInsetsController(window, window.decorView)
        controller.isAppearanceLightStatusBars = !darkTheme
        controller.isAppearanceLightNavigationBars = !darkTheme
    }
}
