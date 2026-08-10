package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF315D78),
    onPrimary = Color.White,
    background = Color(0xFFF3F7FC),
    onBackground = Color(0xFF15212A),
    surface = Color(0xFFF8FBFF),
    onSurface = Color(0xFF15212A),
    secondary = Color(0xFF5B7282),
    outline = Color(0xFF8796A0)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFA8D8F0),
    onPrimary = Color(0xFF0D3448),
    background = Color(0xFF101820),
    onBackground = Color(0xFFE6F0F5),
    surface = Color(0xFF16232D),
    onSurface = Color(0xFFE6F0F5),
    secondary = Color(0xFFB7C9D4),
    outline = Color(0xFF7E919D)
)

@Composable
internal fun NimboTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) DarkColors else LightColors,
        content = content
    )
}
