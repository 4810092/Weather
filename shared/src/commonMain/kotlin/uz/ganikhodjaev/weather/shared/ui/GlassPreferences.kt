package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable

internal data class GlassPreferences(
    val reduceMotion: Boolean = false,
    val reduceTransparency: Boolean = false
)

@Composable
internal expect fun rememberGlassPreferences(): GlassPreferences
