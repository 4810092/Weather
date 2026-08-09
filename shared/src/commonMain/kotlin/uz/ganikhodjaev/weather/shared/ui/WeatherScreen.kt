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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
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
) {
    when (state) {
        WeatherUiState.Loading -> LoadingScreen()
        is WeatherUiState.EmptyError -> ErrorScreen(state.message, onRetry)
        is WeatherUiState.Content -> WeatherContent(state, onRetry)
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
private fun WeatherContent(state: WeatherUiState.Content, onRefresh: () -> Unit) {
    val weather = state.weather
    var selected by remember(weather.fetchedAtEpochSeconds) { mutableStateOf(weather.current) }
    val condition = weatherCondition(weather.current.weatherCode)
    val background = ambience(condition)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(background)
            .safeContentPadding()
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
            Text(
                text = if (state.isRefreshing) "Refreshing…" else "Refresh",
                modifier = Modifier.clickable(enabled = !state.isRefreshing, onClick = onRefresh),
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Medium,
            )
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
            text = comparisonInsight(weather),
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Medium,
        )
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
        Spacer(Modifier.weight(1f))
        Text(
            text = "Weather data by Open-Meteo · Location data by GeoNames",
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.padding(bottom = 4.dp),
        )
    }
}

@Composable
private fun Timeline(
    weather: WeatherSnapshot,
    selected: WeatherHour,
    onSelected: (WeatherHour) -> Unit,
) {
    val now = Clock.System.now().epochSeconds
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .horizontalScroll(rememberScrollState()),
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

private fun comparisonInsight(weather: WeatherSnapshot): String {
    val yesterdayEpoch = weather.current.epochSeconds - 24L * 60L * 60L
    val yesterday = weather.timeline.minByOrNull { abs(it.epochSeconds - yesterdayEpoch) }
        ?: return "A clear view of the hours ahead."
    val difference = weather.current.temperatureC - yesterday.temperatureC
    return when {
        difference >= 5.0 -> "Noticeably warmer than yesterday at this time."
        difference >= 2.0 -> "A little warmer than yesterday at this time."
        difference <= -5.0 -> "Noticeably cooler than yesterday at this time."
        difference <= -2.0 -> "A little cooler than yesterday at this time."
        else -> "About the same as yesterday at this time."
    }
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
