package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.awaitLongPressOrCancellation
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.onClick
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import kotlin.math.abs
import kotlin.math.round
import kotlinx.coroutines.launch
import org.jetbrains.compose.resources.stringResource
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.weatherCondition
import uz.ganikhodjaev.weather.shared.resources.*

@Composable
internal fun Timeline(
    weather: WeatherSnapshot,
    selected: WeatherHour,
    units: DisplayUnits,
    contentPadding: Dp,
    onSelected: (WeatherHour) -> Unit,
    onCurrent: () -> Unit,
    now: Long
) {
    val slots = remember(weather.timeline) { timelineSlots(weather.timeline) }
    if (slots.isEmpty()) return
    val selectedIndex = slots.indexOfFirst {
        it.epochSeconds == selected.epochSeconds
    }.coerceAtLeast(0)
    val nowIndex = slots.indexOfLast {
        now in it.epochSeconds until it.epochSeconds + 3_600 &&
            it.hour != null
    }
    val scroll = rememberLazyListState(initialFirstVisibleItemIndex = selectedIndex)
    var positionedCity by rememberSaveable { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    val reduceMotion = LocalGlassPreferences.current.reduceMotion
    val haptic = LocalHapticFeedback.current
    val selection by rememberUpdatedState(selected.epochSeconds)
    val choose by rememberUpdatedState(onSelected)
    val width = (80 * LocalDensity.current.fontScale.coerceIn(1f, 2f)).dp
    val scale = LocalDensity.current.fontScale.coerceAtLeast(1f)
    val chartTop = (26 * scale).dp
    val chartRange = 52.dp
    val chartHeight = chartTop + chartRange + 12.dp
    val rowText = slots.mapIndexed { index, slot ->
        listOf(
            ForecastCardText(
                formatLocalDay(slot.epochSeconds, weather.location.timezone),
                MaterialTheme.typography.labelSmall
            ),
            ForecastCardText(
                if (index ==
                    nowIndex
                ) {
                    stringResource(Res.string.now)
                } else {
                    formatLocalHour(slot.epochSeconds, weather.location.timezone)
                },
                MaterialTheme.typography.labelMedium
            ),
            ForecastCardText("100%", MaterialTheme.typography.labelMedium),
            ForecastCardText(
                "100.0 ${units.precipitationSymbol}",
                MaterialTheme.typography.labelSmall
            )
        )
    }
    val rowHeight =
        uniformForecastCardHeight(
            rowText,
            width,
            listOf(chartHeight, 2.dp, 8.dp, 8.dp, 24.dp, 16.dp, 19.dp)
        )
    val minimum = slots.mapNotNull { it.hour?.temperatureC }.minOrNull() ?: 0.0
    val maximum = slots.mapNotNull { it.hour?.temperatureC }.maxOrNull() ?: 0.0
    fun y(index: Int): Dp? = slots.getOrNull(index)?.hour?.let {
        chartTop + chartRange * (1 - temperatureFraction(it.temperatureC, minimum, maximum))
    }
    fun center(index: Int) {
        scope.launch {
            if (reduceMotion) scroll.scrollToItem(index) else scroll.animateScrollToItem(index)
        }
    }
    fun select(index: Int, center: Boolean) {
        val hour = slots.getOrNull(index)?.hour ?: return
        if (hour.epochSeconds != selection) {
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            choose(hour)
        }
        if (center) center(index)
    }
    LaunchedEffect(weather.location.id) {
        if (positionedCity != weather.location.id) {
            scroll.scrollToItem(selectedIndex)
            positionedCity = weather.location.id
        }
    }
    FlowRow(
        Modifier.fillMaxWidth().padding(horizontal = contentPadding),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(
            stringResource(Res.string.timeline_title),
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(top = 12.dp)
        )
        if (nowIndex >= 0) {
            TextButton(onClick = {
                onCurrent()
                center(nowIndex)
            }) {
                Text(stringResource(Res.string.return_current_hour))
            }
        }
    }
    val appDirection = LocalLayoutDirection.current
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
        BoxWithConstraints(Modifier.fillMaxWidth()) {
            val edge = maxOf(contentPadding, (maxWidth - width) / 2)
            LazyRow(
                Modifier.fillMaxWidth().testTag("hourly-forecast")
                    .pointerInput(slots, reduceMotion) {
                        var scrubIndex: Int? = null
                        fun explore(x: Float) {
                            val info = scroll.layoutInfo
                            val item = info.visibleItemsInfo.minByOrNull {
                                // Item offsets exclude content padding; pointer coordinates do not.
                                abs(it.offset + info.beforeContentPadding + it.size / 2f - x)
                            } ?: return
                            scrubIndex = item.index
                            select(item.index, center = false)
                        }
                        awaitEachGesture {
                            val down = awaitFirstDown(requireUnconsumed = false)
                            val held =
                                awaitLongPressOrCancellation(down.id) ?: return@awaitEachGesture
                            explore(held.position.x)
                            // Win the gesture before LazyRow sees movement, but only after a hold.
                            // Ordinary taps and swipes retain the standard clickable/scroll behaviour.
                            while (true) {
                                val event = awaitPointerEvent(PointerEventPass.Initial)
                                val change = event.changes.firstOrNull { it.id == held.id } ?: break
                                if (!change.pressed) {
                                    change.consume()
                                    scrubIndex?.let { center(it) }
                                    break
                                }
                                explore(change.position.x)
                                change.consume()
                            }
                            scrubIndex = null
                        }
                    },
                state = scroll,
                contentPadding = PaddingValues(horizontal = edge)
            ) {
                items(slots.size, key = { slots[it].epochSeconds }) { index ->
                    val slot = slots[index]
                    val hour = slot.hour
                    val isSelected = slot.epochSeconds == selected.epochSeconds
                    val isNow = index == nowIndex
                    val isPast = slot.epochSeconds + 3_600 <= now
                    val date = formatLocalDay(slot.epochSeconds, weather.location.timezone)
                    val time = formatLocalHour(slot.epochSeconds, weather.location.timezone)
                    val newDay =
                        index == 0 ||
                            weatherDate(slot.epochSeconds, weather.location.timezone) !=
                            weatherDate(slots[index - 1].epochSeconds, weather.location.timezone)
                    val rain = hour?.takeIf { it.hasField(WeatherHour.RAIN_PROBABILITY) }
                        ?.precipitationProbability?.toString() ?: "—"
                    val missingLabel = stringResource(Res.string.hour_missing_data)
                    val description = if (hour == null) {
                        "$date, $time, $missingLabel"
                    } else {
                        stringResource(
                            Res.string.hour_accessibility_full,
                            "$date, $time",
                            units.temperature(hour.temperatureC),
                            weatherCondition(hour.weatherCode).label(),
                            units.temperature(hour.apparentTemperatureC),
                            rain,
                            units.wind(hour.windKph),
                            units.windSymbol
                        ) +
                            (if (isNow) ", ${stringResource(Res.string.now)}" else "") +
                            (
                                if (hour.missingFields !=
                                    0
                                ) {
                                    ", $missingLabel"
                                } else {
                                    ""
                                }
                                )
                    }
                    val selectedColor by animateColorAsState(
                        if (isSelected) {
                            MaterialTheme.colorScheme.primary.copy(
                                alpha = 0.1f
                            )
                        } else {
                            Color.Transparent
                        },
                        tween(if (reduceMotion) 0 else NimboLayout.TRANSITION_MILLIS)
                    )
                    val primary = MaterialTheme.colorScheme.primary
                    val curveColor = if (isPast) MaterialTheme.colorScheme.secondary else primary
                    val divider = LocalNimboThemeTokens.current.divider
                    CompositionLocalProvider(LocalLayoutDirection provides appDirection) {
                        Column(
                            Modifier.width(
                                width
                            ).background(
                                selectedColor,
                                RoundedCornerShape(NimboLayout.CompactRadius)
                            )
                                .clickable(enabled = hour != null) { select(index, center = true) }
                                .clearAndSetSemantics {
                                    contentDescription = description
                                    this.selected = isSelected
                                    if (hour != null) {
                                        role = Role.Button
                                        onClick {
                                            select(index, center = true)
                                            true
                                        }
                                    }
                                },
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Box(
                                Modifier.fillMaxWidth().height(
                                    2.dp
                                ).background(if (newDay) divider else Color.Transparent)
                            )
                            Text(
                                date,
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = if (newDay) FontWeight.Bold else FontWeight.Normal,
                                color = MaterialTheme.colorScheme.secondary,
                                modifier = Modifier.padding(top = 8.dp)
                            )
                            Text(
                                if (isNow) stringResource(Res.string.now) else "\u2066$time\u2069",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = if (isNow) FontWeight.Bold else FontWeight.Normal
                            )
                            Spacer(Modifier.height(8.dp))
                            WeatherIcon(
                                hour?.let { weatherCondition(it.weatherCode) }
                                    ?: WeatherCondition.Unknown,
                                Modifier.size(24.dp),
                                daylightAt(weather, slot.epochSeconds, now)
                            )
                            Box(Modifier.fillMaxWidth().height(chartHeight)) {
                                val currentY = y(index)
                                val previousY = y(index - 1)
                                val nextY = y(index + 1)
                                Canvas(Modifier.fillMaxSize()) {
                                    if (currentY != null) {
                                        val cy = currentY.toPx()
                                        val middle = size.width / 2
                                        val path = Path()
                                        if (previousY != null) {
                                            path.moveTo(0f, (previousY.toPx() + cy) / 2)
                                            path.cubicTo(middle / 2, cy, middle / 2, cy, middle, cy)
                                        } else {
                                            path.moveTo(middle, cy)
                                        }
                                        if (nextY != null) {
                                            path.cubicTo(
                                                middle * 1.5f,
                                                cy,
                                                middle * 1.5f,
                                                cy,
                                                size.width,
                                                (nextY.toPx() + cy) / 2
                                            )
                                        }
                                        drawPath(path, curveColor, style = Stroke(2.dp.toPx()))
                                        if (isSelected) {
                                            drawLine(
                                                primary.copy(alpha = 0.4f),
                                                Offset(middle, cy),
                                                Offset(middle, size.height),
                                                1.dp.toPx()
                                            )
                                        }
                                        drawCircle(
                                            curveColor,
                                            (if (isSelected) 4.dp else 2.5.dp).toPx(),
                                            Offset(middle, cy)
                                        )
                                    }
                                }
                                Text(
                                    hour?.let { "${units.temperature(it.temperatureC)}°" } ?: "—",
                                    Modifier.align(Alignment.TopCenter).offset(
                                        y =
                                        (currentY ?: chartTop) - (24 * scale).dp
                                    ),
                                    style = MaterialTheme.typography.bodyMedium,
                                    fontWeight = if (isSelected) {
                                        FontWeight.Bold
                                    } else {
                                        FontWeight.Medium
                                    }
                                )
                            }
                            Box(
                                Modifier.height(16.dp).width(24.dp),
                                contentAlignment = Alignment.BottomCenter
                            ) {
                                if (hour != null && hour.hasField(WeatherHour.RAIN_PROBABILITY)) {
                                    Box(
                                        Modifier.fillMaxWidth().height(
                                            (
                                                hour.precipitationProbability *
                                                    0.14f +
                                                    2
                                                ).dp
                                        )
                                            .background(
                                                primary.copy(alpha = if (isPast) 0.25f else 0.5f),
                                                RoundedCornerShape(3.dp)
                                            )
                                    )
                                }
                            }
                            Text(
                                if (rain ==
                                    "—"
                                ) {
                                    rain
                                } else {
                                    "$rain%"
                                },
                                style = MaterialTheme.typography.labelMedium
                            )
                            Text(
                                hour?.takeIf { it.hasField(WeatherHour.RAIN_AMOUNT) }?.let {
                                    "${round(
                                        units.precipitation(it.precipitationMm) * 100
                                    ) / 100} ${units.precipitationSymbol}"
                                } ?: "—",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.secondary
                            )
                            Box(
                                Modifier.padding(top = 6.dp, bottom = 8.dp).size(5.dp)
                                    .background(
                                        if (isNow) primary else Color.Transparent,
                                        RoundedCornerShape(50)
                                    )
                            )
                        }
                    }
                }
            }
        }
    }
    Text(
        stringResource(Res.string.timeline_explore),
        Modifier.padding(horizontal = contentPadding, vertical = 8.dp),
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.secondary
    )
}
