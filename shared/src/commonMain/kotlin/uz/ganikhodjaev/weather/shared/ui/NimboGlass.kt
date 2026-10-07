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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.drawOutline
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.dp
import com.kyant.backdrop.isRenderEffectSupported
import uz.ganikhodjaev.weather.shared.model.WeatherCondition

internal data class GlassStyle(
    val tint: Color,
    val controlTint: Color,
    val selectedTint: Color,
    val highlight: Color,
    val shadow: Color,
    val glow: Color
)

internal val LightGlassStyle = GlassStyle(
    tint = Color(0xBDF8FBFF),
    controlTint = Color(0x66F8FBFF),
    selectedTint = Color(0xE6D2EAF6),
    highlight = Color(0x408796A0),
    shadow = Color(0x08315D78),
    glow = Color(0x28FFFFFF)
)

internal val DarkGlassStyle = GlassStyle(
    tint = Color(0xC21F303B),
    controlTint = Color(0x801F303B),
    selectedTint = Color(0xE6284A5C),
    highlight = Color(0x304D687B),
    shadow = Color(0x18000000),
    glow = Color(0x103C627D)
)

internal val LocalGlassScene = staticCompositionLocalOf { false }
internal val LocalGlassPreferences = staticCompositionLocalOf { GlassPreferences() }

/** Glass rests on this smooth ambience; there is no detailed backdrop to filter. */
@Composable
internal fun NimboGlassScene(
    condition: WeatherCondition,
    daylight: DaylightPhase = DaylightPhase.Unknown,
    content: @Composable () -> Unit
) {
    val tokens = LocalNimboThemeTokens.current
    val style = if (tokens.isDark) DarkGlassStyle else LightGlassStyle
    val preferences = rememberGlassPreferences()
    Box(Modifier.fillMaxSize()) {
        Box(
            Modifier.fillMaxSize()
                .background(tokens.ambience(condition, daylight))
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
            LocalGlassScene provides true,
            LocalGlassPreferences provides preferences,
            content = content
        )
    }
}

@Composable
internal fun Modifier.nimboGlass(
    shape: Shape = RoundedCornerShape(NimboLayout.CardRadius),
    selected: Boolean = false,
    interactive: Boolean = false,
    pressProgress: () -> Float = { 0f }
): Modifier {
    val style = if (LocalNimboThemeTokens.current.isDark) DarkGlassStyle else LightGlassStyle
    val inGlassScene = LocalGlassScene.current
    val preferences = LocalGlassPreferences.current
    val tint = when {
        selected -> style.selectedTint
        interactive -> style.controlTint
        else -> style.tint
    }
    if (!inGlassScene || preferences.reduceTransparency || !isRenderEffectSupported()) {
        return clip(shape).background(tint.copy(alpha = 1f), shape)
            .border(NimboLayout.Hairline, style.highlight, shape)
    }
    // Sampling, blurring and refracting the same low-frequency scene for every
    // scrolling card adds offscreen passes without resolving visible detail.
    // Composite the tint directly and keep depth in a cached edge and native shadow.
    val emphasized = interactive || selected
    return shadow(
        elevation = if (emphasized) 8.dp else 3.dp,
        shape = shape,
        ambientColor = style.shadow,
        spotColor = style.shadow
    ).background(tint, shape).drawWithCache {
        val outline = shape.createOutline(size, layoutDirection, this)
        val highlight = style.highlight.copy(
            alpha = style.highlight.alpha * if (emphasized) 1f else 0.4f
        )
        val edge = Brush.linearGradient(
            0f to highlight,
            0.5f to Color.Transparent,
            1f to highlight.copy(alpha = highlight.alpha * 0.55f),
            start = Offset.Zero,
            end = Offset(size.width, size.height)
        )
        val stroke = Stroke(2 * NimboLayout.Hairline.toPx())
        onDrawWithContent {
            drawContent()
            drawOutline(
                outline = outline,
                brush = edge,
                alpha = 0.8f + pressProgress() * 0.2f,
                style = stroke,
                blendMode = BlendMode.Plus
            )
        }
    }
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
        modifier = modifier.sizeIn(
            minHeight = NimboLayout.ActionSize
        ).glassControl(source, shape, selected),
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
        modifier = modifier.sizeIn(
            minWidth = NimboLayout.ActionSize,
            minHeight = NimboLayout.ActionSize
        )
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
