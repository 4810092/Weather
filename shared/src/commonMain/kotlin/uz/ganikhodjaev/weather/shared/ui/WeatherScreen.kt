package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeContentPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState as rememberVerticalScrollState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.domain.BestTimeOutsideEngine
import uz.ganikhodjaev.weather.shared.domain.OutsideHazard
import uz.ganikhodjaev.weather.shared.domain.OutsideReason
import uz.ganikhodjaev.weather.shared.domain.OutsideRecommendation
import uz.ganikhodjaev.weather.shared.domain.TemperatureComparison
import uz.ganikhodjaev.weather.shared.domain.UpcomingInsight
import uz.ganikhodjaev.weather.shared.domain.WeatherInsightEngine
import uz.ganikhodjaev.weather.shared.model.weatherCondition
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlin.time.Clock
import kotlin.time.Instant

@Composable
internal fun WeatherScreen(
    state: WeatherUiState,
    onRetry: () -> Unit,
    onSearchQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onChangeLocation: () -> Unit,
    onCancelLocationChange: () -> Unit,
) {
    when (state) {
        WeatherUiState.Loading -> LoadingScreen()
        is WeatherUiState.ChooseLocation -> ChooseLocationScreen(
            state = state,
            onQueryChanged = onSearchQueryChanged,
            onLocationSelected = onLocationSelected,
            onUseDeviceLocation = onUseDeviceLocation,
            onCancel = onCancelLocationChange,
        )
        is WeatherUiState.EmptyError -> ErrorScreen(state.message, onRetry)
        is WeatherUiState.Content -> WeatherContent(state, onRetry, onChangeLocation)
    }
}

@Composable
private fun ChooseLocationScreen(
    state: WeatherUiState.ChooseLocation,
    onQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onCancel: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .safeContentPadding()
            .verticalScroll(rememberVerticalScrollState())
            .padding(horizontal = 24.dp, vertical = 28.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Nimbo",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
            )
            if (state.canCancel) {
                Text(
                    text = "Cancel",
                    modifier = Modifier.clickable(onClick = onCancel).padding(8.dp),
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
        Spacer(Modifier.height(18.dp))
        Text(
            text = "Weather that feels familiar.",
            style = MaterialTheme.typography.displaySmall,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(Modifier.height(12.dp))
        Text(
            text = "Choose a place to see the next 24 hours alongside weather you've just experienced.",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.secondary,
        )
        Spacer(Modifier.height(28.dp))
        OutlinedTextField(
            value = state.query,
            onValueChange = onQueryChanged,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            label = { Text("Search for a city") },
            supportingText = { Text("You can change this later.") },
        )

        if (state.isSearching) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 18.dp),
                horizontalArrangement = Arrangement.Center,
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    strokeWidth = 2.dp,
                )
            }
        }

        state.results.forEach { location ->
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onLocationSelected(location) }
                    .padding(vertical = 14.dp)
                    .semantics {
                        contentDescription = "${location.name}, ${location.country}"
                    },
            ) {
                Text(location.name, fontWeight = FontWeight.SemiBold)
                if (location.country.isNotBlank()) {
                    Text(
                        location.country,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.secondary,
                    )
                }
            }
            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))
        }

        state.message?.let { message ->
            Spacer(Modifier.height(12.dp))
            Text(
                text = message,
                color = MaterialTheme.colorScheme.secondary,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        Spacer(Modifier.height(24.dp))
        OutlinedButton(
            onClick = onUseDeviceLocation,
            enabled = !state.isLocating,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(if (state.isLocating) "Finding your area…" else "Use my approximate location")
        }
        Spacer(Modifier.height(12.dp))
        Text(
            text = "Nimbo only requests location after you tap this button. City search works without permission.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.secondary,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun LoadingScreen() {
    Box(
        modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background),
        contentAlignment = Alignment.Center,
    ) {
        CircularProgressIndicator(
            modifier = Modifier.semantics { contentDescription = "Loading weather" },
        )
    }
}

@Composable
private fun ErrorScreen(message: String, onRetry: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().safeContentPadding().padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("Weather is out of reach", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        Text(message, textAlign = TextAlign.Center, color = MaterialTheme.colorScheme.secondary)
        Spacer(Modifier.height(24.dp))
        Button(onClick = onRetry) { Text("Try again") }
    }
}

@Composable
private fun WeatherContent(
    state: WeatherUiState.Content,
    onRefresh: () -> Unit,
    onChangeLocation: () -> Unit,
) {
    val weather = state.weather
    var selected by remember(weather.fetchedAtEpochSeconds) { mutableStateOf(weather.current) }
    val condition = weatherCondition(weather.current.weatherCode)
    val background = ambience(condition)
    val insights = remember(weather) { WeatherInsightEngine().evaluate(weather) }
    val outside = remember(weather) {
        BestTimeOutsideEngine().evaluate(
            timeline = weather.timeline,
            timezone = weather.location.timezone,
            nowEpochSeconds = weather.current.epochSeconds,
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(background)
            .safeContentPadding()
            .verticalScroll(rememberVerticalScrollState())
            .padding(horizontal = 24.dp, vertical = 16.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column {
                Text(
                    text = weather.location.name,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = weather.location.country,
                    color = MaterialTheme.colorScheme.secondary,
                )
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = if (state.isRefreshing) "Refreshing…" else "Refresh",
                    modifier = Modifier.clickable(enabled = !state.isRefreshing, onClick = onRefresh),
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Medium,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Change place",
                    modifier = Modifier.clickable(onClick = onChangeLocation),
                    color = MaterialTheme.colorScheme.secondary,
                    style = MaterialTheme.typography.labelLarge,
                )
            }
        }

        Spacer(Modifier.height(32.dp))
        Text(
            text = "${weather.current.temperatureC.roundToInt()}°",
            fontSize = 88.sp,
            lineHeight = 88.sp,
            fontWeight = FontWeight.Light,
        )
        Text(
            text = condition.label(),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Medium,
        )
        Text(
            text = "Feels like ${weather.current.apparentTemperatureC.roundToInt()}°",
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.titleMedium,
        )
        Spacer(Modifier.height(18.dp))
        Text(
            text = comparisonInsight(insights.comparison),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Medium,
        )
        insights.upcoming?.let { upcoming ->
            Spacer(Modifier.height(6.dp))
            Text(
                text = upcomingInsight(upcoming, weather.location.timezone),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.secondary,
            )
        }
        if (weather.isStale || state.refreshMessage != null) {
            Spacer(Modifier.height(12.dp))
            Text(
                text = state.refreshMessage ?: "Saved weather · update needed",
                modifier = Modifier
                    .background(
                        MaterialTheme.colorScheme.surface.copy(alpha = 0.72f),
                        RoundedCornerShape(12.dp),
                    )
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                color = MaterialTheme.colorScheme.secondary,
            )
        }

        Spacer(Modifier.height(32.dp))
        Text("24 hours before · now · 24 hours ahead", fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(12.dp))
        Timeline(
            weather = weather,
            selected = selected,
            onSelected = { selected = it },
        )
        Spacer(Modifier.height(18.dp))
        SelectedHour(selected, weather.location.timezone)
        Spacer(Modifier.height(18.dp))
        OutsideCard(outside, weather.location.timezone)
        val recentDays = remember(weather) { recentDaySummaries(weather) }
        if (recentDays.isNotEmpty()) {
            Spacer(Modifier.height(18.dp))
            RecentDays(recentDays)
        }
        Spacer(Modifier.height(24.dp))
        Text(
            text = "Weather data by Open-Meteo · Location data by GeoNames",
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(bottom = 4.dp),
        )
    }
}

private data class RecentDaySummary(
    val daysAgo: Int,
    val averageC: Int,
    val lowC: Int,
    val highC: Int,
)

@Composable
private fun RecentDays(days: List<RecentDaySummary>) {
    Column {
        Text("Recent days", fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(10.dp))
        Row(
            modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            days.forEach { day ->
                Column(
                    modifier = Modifier
                        .width(116.dp)
                        .background(
                            MaterialTheme.colorScheme.surface.copy(alpha = 0.68f),
                            RoundedCornerShape(18.dp),
                        )
                        .padding(14.dp),
                ) {
                    Text(
                        if (day.daysAgo == 1) "Yesterday" else "${day.daysAgo} days ago",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.secondary,
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "${day.averageC}° avg",
                        fontWeight = FontWeight.SemiBold,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        "${day.lowC}°–${day.highC}°",
                        color = MaterialTheme.colorScheme.secondary,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
    }
}

private fun recentDaySummaries(weather: WeatherSnapshot): List<RecentDaySummary> {
    val zone = runCatching { TimeZone.of(weather.location.timezone) }.getOrElse { TimeZone.UTC }
    return (1..7).mapNotNull { daysAgo ->
        val targetDate = Instant.fromEpochSeconds(
            weather.current.epochSeconds - daysAgo * 24L * 60L * 60L,
        ).toLocalDateTime(zone).date
        val hours = weather.recentHistory.filter { hour ->
            Instant.fromEpochSeconds(hour.epochSeconds).toLocalDateTime(zone).date == targetDate
        }
        if (hours.isEmpty()) return@mapNotNull null
        RecentDaySummary(
            daysAgo = daysAgo,
            averageC = hours.map { it.temperatureC }.average().roundToInt(),
            lowC = hours.minOf { it.temperatureC }.roundToInt(),
            highC = hours.maxOf { it.temperatureC }.roundToInt(),
        )
    }
}

@Composable
private fun OutsideCard(recommendation: OutsideRecommendation, timezone: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.74f), RoundedCornerShape(24.dp))
            .padding(18.dp),
    ) {
        Text("Best time to go outside", fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(8.dp))
        when (recommendation) {
            is OutsideRecommendation.Recommended -> {
                Text(
                    text = "${formatHour(recommendation.startEpochSeconds, timezone)}–" +
                        formatHour(recommendation.endEpochSeconds, timezone),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold,
                )
                if (recommendation.reasons.isNotEmpty()) {
                    Text(
                        recommendation.reasons.joinToString(" · ") { it.label() },
                        color = MaterialTheme.colorScheme.secondary,
                    )
                }
            }
            is OutsideRecommendation.Unsafe -> {
                Text(
                    "No safe window to recommend today",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    recommendation.hazards.joinToString(" · ") { it.label() },
                    color = MaterialTheme.colorScheme.secondary,
                )
            }
            OutsideRecommendation.Unavailable -> Text(
                "Not enough hourly data yet.",
                color = MaterialTheme.colorScheme.secondary,
            )
        }
    }
}

@Composable
private fun Timeline(
    weather: WeatherSnapshot,
    selected: WeatherHour,
    onSelected: (WeatherHour) -> Unit,
) {
    val now = Clock.System.now().epochSeconds
    val nowIndex = weather.timeline.indices.minByOrNull { index ->
        abs(weather.timeline[index].epochSeconds - now)
    } ?: 0
    val density = LocalDensity.current
    val initialOffset = with(density) { (68.dp * (nowIndex - 2).coerceAtLeast(0)).roundToPx() }
    val timelineScroll = rememberScrollState(initial = initialOffset)
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(timelineScroll),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        weather.timeline.forEach { hour ->
            val past = hour.epochSeconds < now - 1_800
            val isNow = abs(hour.epochSeconds - now) < 1_800
            val isSelected = hour.epochSeconds == selected.epochSeconds
            val hourLabel = formatHour(hour.epochSeconds, weather.location.timezone)
            Column(
                modifier = Modifier
                    .width(64.dp)
                    .alpha(if (past) 0.55f else 1f)
                    .background(
                        if (isSelected) MaterialTheme.colorScheme.surface.copy(alpha = 0.9f)
                        else Color.Transparent,
                        RoundedCornerShape(18.dp),
                    )
                    .clickable { onSelected(hour) }
                    .semantics {
                        contentDescription = "$hourLabel, ${hour.temperatureC.roundToInt()} degrees, " +
                            "${hour.precipitationProbability} percent chance of precipitation"
                    }
                    .padding(vertical = 10.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(if (isNow) "NOW" else hourLabel, style = MaterialTheme.typography.labelSmall)
                Spacer(Modifier.height(8.dp))
                Text(weatherCondition(hour.weatherCode).symbol(), fontSize = 20.sp)
                Spacer(Modifier.height(8.dp))
                Text("${hour.temperatureC.roundToInt()}°", fontWeight = FontWeight.SemiBold)
                if (hour.precipitationProbability > 0) {
                    Text(
                        "${hour.precipitationProbability}%",
                        color = MaterialTheme.colorScheme.primary,
                        style = MaterialTheme.typography.labelSmall,
                    )
                } else {
                    Spacer(Modifier.height(16.dp))
                }
                if (isNow) {
                    Spacer(Modifier.height(6.dp))
                    Box(
                        Modifier.size(6.dp).background(MaterialTheme.colorScheme.primary, CircleShape),
                    )
                }
            }
        }
    }
}

@Composable
private fun SelectedHour(hour: WeatherHour, timezone: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.74f), RoundedCornerShape(24.dp))
            .padding(18.dp),
    ) {
        Text(formatHour(hour.epochSeconds, timezone), fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(10.dp))
        HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.24f))
        Spacer(Modifier.height(12.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Detail("Feels like", "${hour.apparentTemperatureC.roundToInt()}°")
            Detail("Rain", "${hour.precipitationProbability}%")
            Detail("Wind", "${hour.windKph.roundToInt()} km/h")
        }
    }
}

@Composable
private fun Detail(label: String, value: String) {
    Column {
        Text(label, color = MaterialTheme.colorScheme.secondary, style = MaterialTheme.typography.labelMedium)
        Text(value, fontWeight = FontWeight.SemiBold)
    }
}

private fun comparisonInsight(comparison: TemperatureComparison): String = when (comparison) {
    TemperatureComparison.MuchWarmer -> "Noticeably warmer than yesterday at this time."
    TemperatureComparison.Warmer -> "A little warmer than yesterday at this time."
    TemperatureComparison.Similar -> "About the same as yesterday at this time."
    TemperatureComparison.Cooler -> "A little cooler than yesterday at this time."
    TemperatureComparison.MuchCooler -> "Noticeably cooler than yesterday at this time."
    TemperatureComparison.Unavailable -> "A clear view of the hours ahead."
}

private fun upcomingInsight(insight: UpcomingInsight, timezone: String): String = when (insight) {
    is UpcomingInsight.RainLikely -> "Rain is likely around ${formatHour(insight.epochSeconds, timezone)}."
    is UpcomingInsight.TurningCooler -> "It turns cooler around ${formatHour(insight.epochSeconds, timezone)}."
    is UpcomingInsight.TurningWarmer -> "It turns warmer around ${formatHour(insight.epochSeconds, timezone)}."
}

private fun OutsideReason.label(): String = when (this) {
    OutsideReason.ComfortableTemperature -> "comfortable"
    OutsideReason.LowerHeat -> "milder"
    OutsideReason.Dry -> "dry"
    OutsideReason.LightWind -> "light wind"
    OutsideReason.LowUv -> "low UV"
}

private fun OutsideHazard.label(): String = when (this) {
    OutsideHazard.ExtremeHeat -> "extreme heat"
    OutsideHazard.ExtremeCold -> "extreme cold"
    OutsideHazard.Thunderstorm -> "thunderstorm"
    OutsideHazard.HeavyPrecipitation -> "heavy precipitation"
    OutsideHazard.StrongWind -> "strong wind"
}

private fun formatHour(epochSeconds: Long, timezone: String): String {
    val local = Instant.fromEpochSeconds(epochSeconds).toLocalDateTime(TimeZone.of(timezone))
    return local.hour.toString().padStart(2, '0') + ":00"
}

private fun ambience(condition: WeatherCondition): Brush {
    val colors = when (condition) {
        WeatherCondition.Clear, WeatherCondition.MainlyClear -> listOf(Color(0xFFDDEEFF), Color(0xFFF8F3E8))
        WeatherCondition.Rain, WeatherCondition.Showers, WeatherCondition.Thunderstorm -> listOf(Color(0xFFD8E1E8), Color(0xFFF2F5F7))
        WeatherCondition.Snow -> listOf(Color(0xFFEAF4F7), Color(0xFFF7FAFB))
        else -> listOf(Color(0xFFE2EAF0), Color(0xFFF6F8FA))
    }
    return Brush.verticalGradient(colors)
}

private fun WeatherCondition.label(): String = when (this) {
    WeatherCondition.Clear -> "Clear"
    WeatherCondition.MainlyClear -> "Mostly clear"
    WeatherCondition.Cloudy -> "Cloudy"
    WeatherCondition.Fog -> "Foggy"
    WeatherCondition.Drizzle -> "Drizzle"
    WeatherCondition.Rain -> "Rain"
    WeatherCondition.Snow -> "Snow"
    WeatherCondition.Showers -> "Showers"
    WeatherCondition.Thunderstorm -> "Thunderstorm"
    WeatherCondition.Unknown -> "Weather"
}

private fun WeatherCondition.symbol(): String = when (this) {
    WeatherCondition.Clear -> "☀"
    WeatherCondition.MainlyClear -> "◒"
    WeatherCondition.Cloudy -> "●"
    WeatherCondition.Fog -> "≋"
    WeatherCondition.Drizzle -> "⋮"
    WeatherCondition.Rain, WeatherCondition.Showers -> "☂"
    WeatherCondition.Snow -> "✣"
    WeatherCondition.Thunderstorm -> "ϟ"
    WeatherCondition.Unknown -> "·"
}
