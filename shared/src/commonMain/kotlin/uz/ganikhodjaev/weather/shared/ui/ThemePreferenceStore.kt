package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import uz.ganikhodjaev.weather.shared.PlatformContext
import uz.ganikhodjaev.weather.shared.model.ThemePreference

internal interface ThemePreferenceStore {
    fun read(): ThemePreference

    fun write(preference: ThemePreference)
}

internal expect fun createThemePreferenceStore(context: PlatformContext): ThemePreferenceStore

@Composable
internal expect fun ApplyPlatformThemeAppearance(
    context: PlatformContext,
    preference: ThemePreference,
    darkTheme: Boolean
)
