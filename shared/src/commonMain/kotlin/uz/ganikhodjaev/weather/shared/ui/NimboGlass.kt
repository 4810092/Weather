package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.dp
import com.kyant.backdrop.Backdrop
import com.kyant.backdrop.backdrops.layerBackdrop
import com.kyant.backdrop.backdrops.rememberLayerBackdrop
import com.kyant.backdrop.drawBackdrop
import com.kyant.backdrop.effects.blur
import com.kyant.backdrop.effects.lens
import com.kyant.backdrop.highlight.Highlight
import com.kyant.backdrop.highlight.HighlightStyle
import com.kyant.backdrop.isRenderEffectSupported
import com.kyant.backdrop.isRuntimeShaderSupported
import com.kyant.backdrop.shadow.Shadow
import uz.ganikhodjaev.weather.shared.model.WeatherCondition

internal data class GlassStyle(
    val tint: Color,
    val controlTint: Color,
    val selectedTint: Color,
    val highlight: Color,
    val shadow: Color,
    val glow: Color,
    val blurRadius: Float = 8f,
    val lensDepth: Float = 8f
)

internal val LightGlassStyle = GlassStyle(
    tint = Color(0xBDF8FBFF),
    controlTint = Color(0x66F8FBFF),
    selectedTint = Color(0xE6D2EAF6),
    highlight = Color(0xE6FFFFFF),
    shadow = Color(0x14315D78),
    glow = Color(0x99FFFFFF)
)

internal val DarkGlassStyle = GlassStyle(
    tint = Color(0xC21F303B),
    controlTint = Color(0x801F303B),
    selectedTint = Color(0xE6284A5C),
    highlight = Color(0x66E0F4FF),
    shadow = Color(0x33000000),
    glow = Color(0x183C627D)
)

internal val LocalGlassBackdrop = staticCompositionLocalOf<Backdrop?> { null }
private val LocalGlassPreferences = staticCompositionLocalOf { GlassPreferences() }

/** Record only the background, never the glass consuming it (which would recurse). */
@Composable
internal fun NimboGlassScene(condition: WeatherCondition, content: @Composable () -> Unit) {
    val tokens = LocalNimboThemeTokens.current
    val style = if (tokens.isDark) DarkGlassStyle else LightGlassStyle
    val backdrop = rememberLayerBackdrop()
    val preferences = rememberGlassPreferences()
    Box(Modifier.fillMaxSize()) {
        Box(
            Modifier.fillMaxSize()
                .layerBackdrop(backdrop)
                .background(tokens.ambience(condition))
                .drawWithCache {
                    val topLight = Brush.radialGradient(
                        listOf(style.glow, Color.Transparent),
                        center = Offset(size.width * 0.85f, size.height * 0.14f),
                        radius = size.width * 0.85f
                    )
                    val bottomLight = Brush.radialGradient(
                        listOf(style.glow.copy(alpha = style.glow.alpha * 0.5f), Color.Transparent),
                        center = Offset(size.width * 0.05f, size.height * 0.72f),
                        radius = size.width * 0.7f
                    )
                    onDrawBehind {
                        drawRect(topLight)
                        drawRect(bottomLight)
                    }
                }
        )
        CompositionLocalProvider(
            LocalGlassBackdrop provides backdrop,
            LocalGlassPreferences provides preferences,
            content = content
        )
    }
}

@Composable
internal fun Modifier.nimboGlass(
    shape: Shape = RoundedCornerShape(24.dp),
    selected: Boolean = false,
    interactive: Boolean = false,
    pressProgress: () -> Float = { 0f }
): Modifier {
    val style = if (LocalNimboThemeTokens.current.isDark) DarkGlassStyle else LightGlassStyle
    val backdrop = LocalGlassBackdrop.current
    val preferences = LocalGlassPreferences.current
    val tint = when {
        selected -> style.selectedTint
        interactive -> style.controlTint
        else -> style.tint
    }
    if (backdrop == null || preferences.reduceTransparency || !isRenderEffectSupported()) {
        return clip(shape).background(tint.copy(alpha = 1f), shape)
            .border(1.dp, style.highlight, shape)
    }
    return drawBackdrop(
        backdrop = backdrop,
        shape = { shape },
        effects = {
            blur((if (interactive) 2f else style.blurRadius).dp.toPx())
            if (isRuntimeShaderSupported()) {
                lens(
                    refractionHeight = minOf(style.lensDepth.dp.toPx(), size.minDimension / 4f),
                    refractionAmount = (if (interactive || selected) 18.dp else 4.dp).toPx(),
                    depthEffect = true,
                    chromaticAberration = interactive
                )
            }
        },
        highlight = {
            Highlight(
                width = 1.dp,
                style = HighlightStyle.Default(
                    color = if (interactive ||
                        selected
                    ) {
                        style.highlight
                    } else {
                        style.highlight.copy(
                            alpha =
                            style.highlight.alpha * 0.4f
                        )
                    },
                    angle = 40f + pressProgress() * 35f
                )
            )
        },
        shadow = {
            Shadow(
                radius = if (interactive ||
                    selected
                ) {
                    8.dp
                } else {
                    3.dp
                },
                color = style.shadow
            )
        },
        onDrawSurface = { drawRect(tint) }
    )
}

@Composable
private fun Modifier.glassControl(
    source: MutableInteractionSource,
    shape: Shape,
    selected: Boolean
): Modifier {
    val pressed by source.collectIsPressedAsState()
    val reduceMotion = LocalGlassPreferences.current.reduceMotion
    val progress = animateFloatAsState(
        targetValue = if (pressed && !reduceMotion) 1f else 0f,
        animationSpec = spring(dampingRatio = 0.7f, stiffness = 600f),
        label = "glassPress"
    )
    return graphicsLayer {
        val scale = if (reduceMotion) 1f else 1f - progress.value * 0.025f
        scaleX = scale
        scaleY = scale
    }.nimboGlass(shape, selected, interactive = true) { if (reduceMotion) 0f else progress.value }
}

@Composable
internal fun GlassButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    selected: Boolean = false,
    contentPadding: PaddingValues = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
    content: @Composable RowScope.() -> Unit
) {
    val source = remember { MutableInteractionSource() }
    val shape = RoundedCornerShape(50)
    Button(
        onClick = onClick,
        modifier = modifier.sizeIn(minHeight = 48.dp).glassControl(source, shape, selected),
        enabled = enabled,
        shape = shape,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent,
            contentColor = MaterialTheme.colorScheme.onSurface,
            disabledContainerColor = Color.Transparent,
            disabledContentColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
        ),
        elevation = null,
        interactionSource = source,
        contentPadding = contentPadding,
        content = content
    )
}

@Composable
internal fun GlassIconButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    selected: Boolean = false,
    content: @Composable () -> Unit
) {
    val source = remember { MutableInteractionSource() }
    IconButton(
        onClick = onClick,
        modifier = modifier.sizeIn(minWidth = 48.dp, minHeight = 48.dp)
            .glassControl(source, RoundedCornerShape(50), selected),
        enabled = enabled,
        colors = IconButtonDefaults.iconButtonColors(
            contentColor = MaterialTheme.colorScheme.onSurface,
            disabledContentColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
        ),
        interactionSource = source,
        content = content
    )
}
