package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.ui.graphics.Color
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.test.Test
import kotlin.test.assertTrue

class NimboThemeContrastTest {
    @Test
    fun darkWeatherBackgroundsKeepTextReadable() {
        val backgroundStops = listOf(
            DarkThemeTokens.clearBackground,
            DarkThemeTokens.rainBackground,
            DarkThemeTokens.snowBackground,
            DarkThemeTokens.defaultBackground
        ).flatten()

        backgroundStops.forEach { background ->
            assertContrastAtLeast(DarkColors.onBackground, background, 4.5)
            assertContrastAtLeast(DarkColors.secondary, background, 4.5)
            assertContrastAtLeast(DarkColors.primary, background, 3.0)
        }
    }

    @Test
    fun darkMaterialSurfacesKeepTextAndOutlinesReadable() {
        assertContrastAtLeast(DarkColors.onSurface, DarkColors.surface, 4.5)
        assertContrastAtLeast(DarkColors.onSurfaceVariant, DarkColors.surfaceVariant, 4.5)
        assertContrastAtLeast(DarkColors.outline, Color(0xFF1F303B), 3.0)
    }

    private fun assertContrastAtLeast(foreground: Color, background: Color, minimum: Double) {
        val contrast = contrastRatio(foreground, background)
        assertTrue(
            contrast >= minimum,
            "Expected contrast >= $minimum, got $contrast for $foreground on $background"
        )
    }

    private fun contrastRatio(first: Color, second: Color): Double {
        val firstLuminance = first.relativeLuminance()
        val secondLuminance = second.relativeLuminance()
        return (max(firstLuminance, secondLuminance) + 0.05) /
            (min(firstLuminance, secondLuminance) + 0.05)
    }

    private fun Color.relativeLuminance(): Double = 0.2126 * red.linearChannel() +
        0.7152 * green.linearChannel() +
        0.0722 * blue.linearChannel()

    private fun Float.linearChannel(): Double {
        val channel = toDouble()
        return if (channel <= 0.04045) {
            channel / 12.92
        } else {
            ((channel + 0.055) / 1.055).pow(2.4)
        }
    }
}
