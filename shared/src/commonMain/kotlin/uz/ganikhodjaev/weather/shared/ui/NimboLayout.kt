package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.dp

internal object NimboLayout {
    val Gutter = 20.dp
    val SectionGap = 16.dp
    val CardRadius = 20.dp
    val CompactRadius = 12.dp
    val ActionSize = 48.dp
    val Hairline = 1.dp
    const val TRANSITION_MILLIS = 140
}

/** Brief state-change feedback without moving content, deferring input or animating at rest. */
@Composable
internal fun Modifier.quietTransition(key: Any): Modifier {
    val reduceMotion = LocalGlassPreferences.current.reduceMotion
    val opacity = remember { Animatable(1f) }
    val previous = remember { arrayOf(key) }
    LaunchedEffect(key, reduceMotion) {
        if (reduceMotion) {
            opacity.snapTo(1f)
        } else if (previous[0] != key) {
            opacity.snapTo(0.9f)
            opacity.animateTo(1f, tween(NimboLayout.TRANSITION_MILLIS))
        }
        previous[0] = key
    }
    return graphicsLayer { alpha = if (reduceMotion) 1f else opacity.value }
}
