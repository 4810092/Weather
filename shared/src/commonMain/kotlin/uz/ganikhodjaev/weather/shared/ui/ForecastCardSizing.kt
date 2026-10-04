package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.Dp

internal data class ForecastCardText(val text: String, val style: TextStyle)

/** Size the whole row before scrolling; an offscreen long translation must not resize it later. */
@Composable
internal fun uniformForecastCardHeight(
    rows: List<List<ForecastCardText>>,
    contentWidth: Dp,
    fixedHeights: List<Dp>
): Dp {
    val density = LocalDensity.current
    val direction = LocalLayoutDirection.current
    val measurer = rememberTextMeasurer(cacheSize = 128)
    return remember(rows, contentWidth, fixedHeights, density, direction, measurer) {
        val constraints = Constraints(maxWidth = with(density) { contentWidth.roundToPx() })
        val maxTextHeight = rows.maxOfOrNull { row ->
            row.sumOf { item ->
                measurer.measure(
                    text = item.text,
                    style = item.style,
                    constraints = constraints,
                    layoutDirection = direction
                ).size.height
            }
        } ?: 0
        with(density) {
            (maxTextHeight + fixedHeights.sumOf { it.roundToPx() }).toDp()
        }
    }
}
