package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import uz.ganikhodjaev.weather.shared.PlatformContext
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.model.WeatherCondition

internal val LightColors = lightColorScheme(
    primary = Color(0xFF315D78),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD2EAF6),
    onPrimaryContainer = Color(0xFF153F54),
    inversePrimary = Color(0xFFA8D8F0),
    secondary = Color(0xFF5B7282),
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFDDE8EE),
    onSecondaryContainer = Color(0xFF263B47),
    tertiary = Color(0xFF5F607A),
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFE5E4FF),
    onTertiaryContainer = Color(0xFF2C2D48),
    background = Color(0xFFF3F7FC),
    onBackground = Color(0xFF15212A),
    surface = Color(0xFFF8FBFF),
    onSurface = Color(0xFF15212A),
    surfaceVariant = Color(0xFFDDE5EA),
    onSurfaceVariant = Color(0xFF3F4B53),
    surfaceTint = Color(0xFF315D78),
    inverseSurface = Color(0xFF2A353C),
    inverseOnSurface = Color(0xFFEDF2F5),
    error = Color(0xFFBA1A1A),
    onError = Color.White,
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF410002),
    outline = Color(0xFF8796A0),
    outlineVariant = Color(0xFFC3CDD3),
    scrim = Color.Black,
    surfaceBright = Color(0xFFF8FBFF),
    surfaceContainer = Color(0xFFEDF2F6),
    surfaceContainerHigh = Color(0xFFE7EDF1),
    surfaceContainerHighest = Color(0xFFE1E8EC),
    surfaceContainerLow = Color(0xFFF2F6FA),
    surfaceContainerLowest = Color.White,
    surfaceDim = Color(0xFFD5DCE1)
)

internal val DarkColors = darkColorScheme(
    primary = Color(0xFFA8D8F0),
    onPrimary = Color(0xFF0D3448),
    primaryContainer = Color(0xFF214A60),
    onPrimaryContainer = Color(0xFFD0EEFA),
    inversePrimary = Color(0xFF315D78),
    secondary = Color(0xFFB7C9D4),
    onSecondary = Color(0xFF23333D),
    secondaryContainer = Color(0xFF354650),
    onSecondaryContainer = Color(0xFFD6E6EE),
    tertiary = Color(0xFFC4C8EA),
    onTertiary = Color(0xFF2D304C),
    tertiaryContainer = Color(0xFF444766),
    onTertiaryContainer = Color(0xFFE4E5FF),
    background = Color(0xFF101820),
    onBackground = Color(0xFFE6F0F5),
    surface = Color(0xFF16232D),
    onSurface = Color(0xFFE6F0F5),
    surfaceVariant = Color(0xFF2B3943),
    onSurfaceVariant = Color(0xFFC5D3DC),
    surfaceTint = Color(0xFFA8D8F0),
    inverseSurface = Color(0xFFE6F0F5),
    inverseOnSurface = Color(0xFF25323B),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005),
    errorContainer = Color(0xFF93000A),
    onErrorContainer = Color(0xFFFFDAD6),
    outline = Color(0xFF899AA5),
    outlineVariant = Color(0xFF3D4B55),
    scrim = Color.Black,
    surfaceBright = Color(0xFF35434D),
    surfaceContainer = Color(0xFF19242D),
    surfaceContainerHigh = Color(0xFF23303A),
    surfaceContainerHighest = Color(0xFF2E3B45),
    surfaceContainerLow = Color(0xFF151E26),
    surfaceContainerLowest = Color(0xFF0B1117),
    surfaceDim = Color(0xFF101820)
)

internal data class NimboThemeTokens(
    val isDark: Boolean,
    val clearBackground: List<Color>,
    val rainBackground: List<Color>,
    val snowBackground: List<Color>,
    val defaultBackground: List<Color>,
    val subtleSurface: Color,
    val cardSurface: Color,
    val selectedSurface: Color,
    val statusSurface: Color,
    val divider: Color,
    val pastContentAlpha: Float
) {
    fun ambience(condition: WeatherCondition): Brush = Brush.verticalGradient(
        when (condition) {
            WeatherCondition.Clear, WeatherCondition.MainlyClear -> clearBackground
            WeatherCondition.Rain,
            WeatherCondition.Showers,
            WeatherCondition.Thunderstorm -> rainBackground
            WeatherCondition.Snow -> snowBackground
            else -> defaultBackground
        }
    )
}

internal val LightThemeTokens = NimboThemeTokens(
    isDark = false,
    clearBackground = listOf(Color(0xFFDDEEFF), Color(0xFFF8F3E8)),
    rainBackground = listOf(Color(0xFFD8E1E8), Color(0xFFF2F5F7)),
    snowBackground = listOf(Color(0xFFEAF4F7), Color(0xFFF7FAFB)),
    defaultBackground = listOf(Color(0xFFE2EAF0), Color(0xFFF6F8FA)),
    subtleSurface = Color(0xADF8FBFF),
    cardSurface = Color(0xBDF8FBFF),
    selectedSurface = Color(0xE6F8FBFF),
    statusSurface = Color(0xB8F8FBFF),
    divider = Color(0x3D8796A0),
    pastContentAlpha = 0.55f
)

internal val DarkThemeTokens = NimboThemeTokens(
    isDark = true,
    clearBackground = listOf(Color(0xFF0C2133), Color(0xFF28231D)),
    rainBackground = listOf(Color(0xFF101B26), Color(0xFF192831)),
    snowBackground = listOf(Color(0xFF172934), Color(0xFF24343C)),
    defaultBackground = listOf(Color(0xFF13222C), Color(0xFF1D2B33)),
    subtleSurface = Color(0xD91F303B),
    cardSurface = Color(0xE61F303B),
    selectedSurface = Color(0xF2284A5C),
    statusSurface = Color(0xE61F303B),
    divider = Color(0xFF3D4B55),
    pastContentAlpha = 0.72f
)

internal val LocalNimboThemeTokens = staticCompositionLocalOf { LightThemeTokens }

@Composable
internal fun NimboTheme(
    preference: ThemePreference,
    platformContext: PlatformContext,
    content: @Composable () -> Unit
) {
    val darkTheme = preference.resolve(isSystemInDarkTheme())
    val colors = if (darkTheme) DarkColors else LightColors
    val tokens = if (darkTheme) DarkThemeTokens else LightThemeTokens

    ApplyPlatformThemeAppearance(platformContext, preference, darkTheme)
    androidx.compose.runtime.CompositionLocalProvider(LocalNimboThemeTokens provides tokens) {
        MaterialTheme(
            colorScheme = colors,
            content = content
        )
    }
}
