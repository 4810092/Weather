package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import platform.Foundation.NSUserDefaults
import platform.UIKit.UIUserInterfaceStyle
import uz.ganikhodjaev.weather.shared.PlatformContext
import uz.ganikhodjaev.weather.shared.activeIosWindow
import uz.ganikhodjaev.weather.shared.model.ThemePreference

private const val THEME_PREFERENCE_KEY = "theme_preference"

internal actual fun createThemePreferenceStore(context: PlatformContext): ThemePreferenceStore {
    val preferences = NSUserDefaults.standardUserDefaults
    return object : ThemePreferenceStore {
        override fun read(): ThemePreference = ThemePreference.fromStoredValue(
            preferences.stringForKey(THEME_PREFERENCE_KEY)
        )

        override fun write(preference: ThemePreference) {
            preferences.setObject(preference.name, forKey = THEME_PREFERENCE_KEY)
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
        val style = when (preference) {
            ThemePreference.System -> UIUserInterfaceStyle.UIUserInterfaceStyleUnspecified
            ThemePreference.Light -> UIUserInterfaceStyle.UIUserInterfaceStyleLight
            ThemePreference.Dark -> UIUserInterfaceStyle.UIUserInterfaceStyleDark
        }
        activeIosWindow()?.let { window ->
            window.overrideUserInterfaceStyle = style
            window.rootViewController?.overrideUserInterfaceStyle = style
            window.rootViewController?.setNeedsStatusBarAppearanceUpdate()
        }
    }
}
