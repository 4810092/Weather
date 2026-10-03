package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.test.Test
import kotlin.test.assertTrue

class NimboThemeContrastTest {
    @Test
    fun glassKeepsTextReadableAcrossWeatherThemesAndTransparencyModes() {
        listOf(
            Triple(LightThemeTokens, LightGlassStyle, LightColors),
            Triple(DarkThemeTokens, DarkGlassStyle, DarkColors)
        ).forEach { (tokens, glass, colors) ->
            val stops = listOf(
                tokens.clearBackground,
                tokens.rainBackground,
                tokens.snowBackground,
                tokens.defaultBackground
            ).flatten()
            stops.forEach { stop ->
                // The brightest possible overlapping light spots, plus unlit background.
                val glow = glass.glow.copy(alpha = glass.glow.alpha * 0.5f)
                    .compositeOver(glass.glow.compositeOver(stop))
                listOf(stop, glow).forEach { background ->
                    assertContrastAtLeast(colors.onBackground, background, 4.5)
                    assertContrastAtLeast(colors.secondary, background, 4.5)
                    val pastText = colors.onSurface.copy(alpha = tokens.pastContentAlpha)
                        .compositeOver(background)
                    val pastSurface = glass.tint.compositeOver(background)
                        .copy(alpha = tokens.pastContentAlpha).compositeOver(background)
                    assertContrastAtLeast(pastText, pastSurface, 4.5)
                    listOf(glass.tint, glass.controlTint, glass.selectedTint).forEach { tint ->
                        listOf(
                            tint.compositeOver(background),
                            tint.copy(alpha = 1f)
                        ).forEach { surface ->
                            assertContrastAtLeast(colors.onSurface, surface, 4.5)
                            assertContrastAtLeast(colors.secondary, surface, 4.5)
                        }
                    }
                }
            }
        }
    }

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
