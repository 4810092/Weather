package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeContentPadding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState as rememberVerticalScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedIconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.abs
import kotlin.time.Clock
import kotlin.time.Instant
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import org.jetbrains.compose.resources.painterResource
import org.jetbrains.compose.resources.pluralStringResource
import org.jetbrains.compose.resources.stringResource
import uz.ganikhodjaev.weather.shared.domain.BestTimeOutsideEngine
import uz.ganikhodjaev.weather.shared.domain.OutsideHazard
import uz.ganikhodjaev.weather.shared.domain.OutsideReason
import uz.ganikhodjaev.weather.shared.domain.OutsideRecommendation
import uz.ganikhodjaev.weather.shared.domain.TemperatureComparison
import uz.ganikhodjaev.weather.shared.domain.UpcomingInsight
import uz.ganikhodjaev.weather.shared.domain.WeatherInsightEngine
import uz.ganikhodjaev.weather.shared.domain.WeatherInsights
import uz.ganikhodjaev.weather.shared.domain.localDateDaysAgo
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.weatherCondition
import uz.ganikhodjaev.weather.shared.presentation.UiMessage
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState
import uz.ganikhodjaev.weather.shared.resources.*
import uz.ganikhodjaev.weather.shared.resources.Res

@Composable
internal fun WeatherScreen(
    state: WeatherUiState,
    onRetry: () -> Unit,
    onSearchQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onChangeLocation: () -> Unit,
    onCancelLocationChange: () -> Unit,
    onUnitPreferenceChanged: (UnitPreference) -> Unit,
    themePreference: ThemePreference,
    onThemePreferenceChanged: (ThemePreference) -> Unit
) {
    when (state) {
        WeatherUiState.Loading -> LoadingScreen()
        is WeatherUiState.ChooseLocation -> ChooseLocationScreen(
            state = state,
            onQueryChanged = onSearchQueryChanged,
            onLocationSelected = onLocationSelected,
            onUseDeviceLocation = onUseDeviceLocation,
            onCancel = onCancelLocationChange
        )
        is WeatherUiState.EmptyError -> ErrorScreen(state.message.localized(), onRetry)
        is WeatherUiState.Content -> WeatherContent(
            state,
            onRetry,
            onChangeLocation,
            onUnitPreferenceChanged,
            themePreference,
            onThemePreferenceChanged
        )
    }
}

@Composable
private fun ChooseLocationScreen(
    state: WeatherUiState.ChooseLocation,
    onQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onCancel: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .safeContentPadding()
        ) {
            Column(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .fillMaxWidth()
                    .widthIn(max = 680.dp)
                    .verticalScroll(rememberVerticalScrollState())
                    .padding(horizontal = 24.dp, vertical = 28.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = stringResource(Res.string.brand),
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.SemiBold
                    )
                    if (state.canCancel) {
                        TextButton(onClick = onCancel) {
                            Text(stringResource(Res.string.cancel), fontWeight = FontWeight.Medium)
                        }
                    }
                }
                Spacer(Modifier.height(18.dp))
                Text(
                    text = stringResource(Res.string.onboarding_title),
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(Modifier.height(12.dp))
                Text(
                    text = stringResource(Res.string.onboarding_body),
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.secondary
                )
                Spacer(Modifier.height(28.dp))
                OutlinedTextField(
                    value = state.query,
                    onValueChange = onQueryChanged,
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text(stringResource(Res.string.search_city)) },
                    supportingText = { Text(stringResource(Res.string.change_later)) }
                )

                if (state.isSearching) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 18.dp),
                        horizontalArrangement = Arrangement.Center
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            strokeWidth = 2.dp
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
                            }
                    ) {
                        Text(location.name, fontWeight = FontWeight.SemiBold)
                        if (location.country.isNotBlank()) {
                            Text(
                                location.country,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.secondary
                            )
                        }
                    }
                    HorizontalDivider(color = LocalNimboThemeTokens.current.divider)
                }

                state.message?.let { message ->
                    Spacer(Modifier.height(12.dp))
                    Text(
                        text = message.localized(),
                        color = MaterialTheme.colorScheme.secondary,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }

                Spacer(Modifier.height(24.dp))
                OutlinedButton(
                    onClick = onUseDeviceLocation,
                    enabled = !state.isLocating,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        stringResource(
                            if (state.isLocating) {
                                Res.string.finding_area
                            } else {
                                Res.string.use_location
                            }
                        )
                    )
                }
                Spacer(Modifier.height(12.dp))
                Text(
                    text = stringResource(Res.string.location_privacy),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.secondary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun LoadingScreen() {
    val loadingDescription = stringResource(Res.string.loading_weather)
    Box(
        modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            modifier = Modifier.semantics { contentDescription = loadingDescription }
        )
    }
}

@Composable
private fun ErrorScreen(message: String, onRetry: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .safeContentPadding(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().widthIn(max = 560.dp).padding(32.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    stringResource(Res.string.error_title),
                    style = MaterialTheme.typography.headlineMedium
                )
                Spacer(Modifier.height(12.dp))
                Text(
                    message,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.secondary
                )
                Spacer(Modifier.height(24.dp))
                Button(onClick = onRetry) { Text(stringResource(Res.string.try_again)) }
            }
        }
    }
}

@Composable
private fun WeatherContent(
    state: WeatherUiState.Content,
    onRefresh: () -> Unit,
    onChangeLocation: () -> Unit,
    onUnitPreferenceChanged: (UnitPreference) -> Unit,
    themePreference: ThemePreference,
    onThemePreferenceChanged: (ThemePreference) -> Unit
) {
    val weather = state.weather
    var selected by remember(weather.fetchedAtEpochSeconds) { mutableStateOf(weather.current) }
    val condition = weatherCondition(weather.current.weatherCode)
    val background = LocalNimboThemeTokens.current.ambience(condition)
    val insights = remember(weather) { WeatherInsightEngine().evaluate(weather) }
    val outside = remember(weather) {
        BestTimeOutsideEngine().evaluate(
            timeline = weather.timeline,
            timezone = weather.location.timezone,
            nowEpochSeconds = weather.current.epochSeconds
        )
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(background)
    ) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Vertical))
        ) {
            val wideLayout = maxWidth >= 840.dp
            val horizontalPadding = if (wideLayout) 36.dp else 24.dp
            val recentDays = remember(weather) { recentDaySummaries(weather) }
            val uriHandler = LocalUriHandler.current
            Column(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .fillMaxWidth()
                    .verticalScroll(rememberVerticalScrollState())
                    .padding(vertical = 16.dp)
            ) {
                CenteredSection(horizontalPadding) {
                    WeatherHeader(
                        state = state,
                        onRefresh = onRefresh,
                        onChangeLocation = onChangeLocation
                    )
                }

                Spacer(Modifier.height(if (wideLayout) 40.dp else 32.dp))
                CenteredSection(horizontalPadding) {
                    CurrentSummary(state = state, condition = condition, insights = insights)
                }
                Spacer(Modifier.height(32.dp))
                WeatherDetails(
                    state = state,
                    selected = selected,
                    outside = outside,
                    recentDays = recentDays,
                    horizontalPadding = horizontalPadding,
                    onSelected = { selected = it },
                    onUnitPreferenceChanged = onUnitPreferenceChanged,
                    themePreference = themePreference,
                    onThemePreferenceChanged = onThemePreferenceChanged
                )

                Spacer(Modifier.height(24.dp))
                CenteredSection(horizontalPadding) {
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = stringResource(Res.string.attribution),
                            color = MaterialTheme.colorScheme.secondary,
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier
                                .clickable { uriHandler.openUri("https://open-meteo.com/") }
                                .padding(vertical = 12.dp)
                        )
                        TextButton(
                            onClick = {
                                uriHandler.openUri("https://github.com/4810092/Weather")
                            }
                        ) {
                            Text(stringResource(Res.string.about_nimbo))
                        }
                        TextButton(
                            onClick = {
                                uriHandler.openUri(
                                    "https://github.com/4810092/Weather/blob/master/docs/PRIVACY.md"
                                )
                            }
                        ) {
                            Text(stringResource(Res.string.privacy_policy))
                        }
                        TextButton(
                            onClick = {
                                uriHandler.openUri(
                                    "https://github.com/4810092/Weather/blob/master/LICENSE"
                                )
                            }
                        ) {
                            Text(stringResource(Res.string.open_source_licenses))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CenteredSection(horizontalPadding: Dp, content: @Composable () -> Unit) {
    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = Alignment.TopCenter
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 1120.dp)
                .fillMaxWidth()
                .padding(horizontal = horizontalPadding),
            content = { content() }
        )
    }
}

@Composable
private fun WeatherHeader(
    state: WeatherUiState.Content,
    onRefresh: () -> Unit,
    onChangeLocation: () -> Unit
) {
    val weather = state.weather
    val location: @Composable (Modifier) -> Unit = { modifier ->
        Column(modifier = modifier) {
            Text(
                text = weather.location.name.ifBlank {
                    stringResource(Res.string.current_location)
                },
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.SemiBold,
                maxLines = 2
            )
            if (weather.location.country.isNotBlank()) {
                Text(
                    text = weather.location.country,
                    color = MaterialTheme.colorScheme.secondary
                )
            }
        }
    }
    val actions: @Composable () -> Unit = {
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp),
            horizontalAlignment = Alignment.End
        ) {
            OutlinedIconButton(
                onClick = onRefresh,
                enabled = !state.isRefreshing
            ) {
                Icon(
                    painter = painterResource(Res.drawable.ic_refresh),
                    contentDescription = stringResource(
                        if (state.isRefreshing) Res.string.refreshing else Res.string.refresh
                    )
                )
            }
            FilledIconButton(onClick = onChangeLocation) {
                Icon(
                    painter = painterResource(Res.drawable.ic_location),
                    contentDescription = stringResource(Res.string.change_place)
                )
            }
        }
    }
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.Top
    ) {
        location(Modifier.weight(1f).padding(end = 12.dp))
        actions()
    }
}

@Composable
private fun CurrentSummary(
    state: WeatherUiState.Content,
    condition: WeatherCondition,
    insights: WeatherInsights
) {
    val weather = state.weather
    val fontScale = LocalDensity.current.fontScale.coerceAtLeast(1f)
    val heroSize = 88f * minOf(fontScale, 1.25f) / fontScale
    Text(
        text = "${state.displayUnits.temperature(weather.current.temperatureC)}°",
        fontSize = heroSize.sp,
        lineHeight = heroSize.sp,
        fontWeight = FontWeight.Light,
        maxLines = 1
    )
    Text(
        text = condition.label(),
        style = MaterialTheme.typography.headlineMedium,
        fontWeight = FontWeight.Medium
    )
    Text(
        text = stringResource(
            Res.string.feels_like,
            state.displayUnits.temperature(weather.current.apparentTemperatureC)
        ),
        color = MaterialTheme.colorScheme.secondary,
        style = MaterialTheme.typography.titleMedium
    )
    Spacer(Modifier.height(18.dp))
    Text(
        text = comparisonInsight(insights.comparison),
        style = MaterialTheme.typography.titleLarge,
        fontWeight = FontWeight.Medium
    )
    insights.upcoming?.let { upcoming ->
        Spacer(Modifier.height(6.dp))
        Text(
            text = upcomingInsight(upcoming, weather.location.timezone),
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.secondary
        )
    }
    if (weather.isStale || state.refreshMessage != null) {
        Spacer(Modifier.height(12.dp))
        Text(
            text = state.refreshMessage?.localized() ?: stringResource(Res.string.saved_weather),
            modifier = Modifier
                .background(
                    LocalNimboThemeTokens.current.statusSurface,
                    RoundedCornerShape(12.dp)
                )
                .padding(horizontal = 12.dp, vertical = 8.dp),
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
private fun WeatherDetails(
    state: WeatherUiState.Content,
    selected: WeatherHour,
    outside: OutsideRecommendation,
    recentDays: List<RecentDaySummary>,
    horizontalPadding: Dp,
    onSelected: (WeatherHour) -> Unit,
    onUnitPreferenceChanged: (UnitPreference) -> Unit,
    themePreference: ThemePreference,
    onThemePreferenceChanged: (ThemePreference) -> Unit
) {
    val weather = state.weather
    CenteredSection(horizontalPadding) {
        Text(
            stringResource(Res.string.timeline_title),
            fontWeight = FontWeight.SemiBold
        )
    }
    Spacer(Modifier.height(12.dp))
    Timeline(
        weather = weather,
        selected = selected,
        units = state.displayUnits,
        contentPadding = horizontalPadding,
        onSelected = onSelected
    )
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        SelectedHour(selected, weather.location.timezone, state.displayUnits)
    }
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        OutsideCard(outside, weather.location.timezone)
    }
    if (recentDays.isNotEmpty()) {
        Spacer(Modifier.height(18.dp))
        RecentDays(recentDays, state.displayUnits, horizontalPadding)
    }
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        UnitsCard(state.unitPreference, state.displayUnits, onUnitPreferenceChanged)
    }
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        ThemeCard(themePreference, onThemePreferenceChanged)
    }
}

private data class RecentDaySummary(
    val daysAgo: Int,
    val averageC: Double,
    val lowC: Double,
    val highC: Double
)

@Composable
private fun RecentDays(days: List<RecentDaySummary>, units: DisplayUnits, contentPadding: Dp) {
    val recentDaysScroll = rememberLazyListState(
        initialFirstVisibleItemIndex = days.lastIndex
    )
    Column {
        CenteredSection(contentPadding) {
            Text(
                stringResource(Res.string.recent_days),
                fontWeight = FontWeight.SemiBold
            )
        }
        Spacer(Modifier.height(10.dp))
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            state = recentDaysScroll,
            contentPadding = PaddingValues(horizontal = contentPadding),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(
                count = days.size,
                key = { index -> days[days.lastIndex - index].daysAgo }
            ) { index ->
                val day = days[days.lastIndex - index]
                Column(
                    modifier = Modifier
                        .width(116.dp)
                        .background(
                            LocalNimboThemeTokens.current.subtleSurface,
                            RoundedCornerShape(18.dp)
                        )
                        .padding(14.dp)
                ) {
                    Text(
                        if (day.daysAgo == 1) {
                            stringResource(Res.string.yesterday)
                        } else {
                            pluralStringResource(Res.plurals.days_ago, day.daysAgo, day.daysAgo)
                        },
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.secondary
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        stringResource(
                            Res.string.average_temperature,
                            units.temperature(day.averageC)
                        ),
                        fontWeight = FontWeight.SemiBold,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        stringResource(
                            Res.string.temperature_range,
                            units.temperature(day.lowC),
                            units.temperature(day.highC)
                        ),
                        color = MaterialTheme.colorScheme.secondary,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}

private fun recentDaySummaries(weather: WeatherSnapshot): List<RecentDaySummary> {
    val zone = runCatching { TimeZone.of(weather.location.timezone) }.getOrElse { TimeZone.UTC }
    return (1..7).mapNotNull { daysAgo ->
        val targetDate = localDateDaysAgo(
            epochSeconds = weather.current.epochSeconds,
            timezone = weather.location.timezone,
            daysAgo = daysAgo
        )
        val hours = weather.recentHistory.filter { hour ->
            Instant.fromEpochSeconds(hour.epochSeconds).toLocalDateTime(zone).date == targetDate
        }
        if (hours.isEmpty()) return@mapNotNull null
        RecentDaySummary(
            daysAgo = daysAgo,
            averageC = hours.map { it.temperatureC }.average(),
            lowC = hours.minOf { it.temperatureC },
            highC = hours.maxOf { it.temperatureC }
        )
    }
}

@Composable
private fun UnitsCard(
    preference: UnitPreference,
    units: DisplayUnits,
    onPreferenceChanged: (UnitPreference) -> Unit
) {
    val accessibilityLayout = LocalDensity.current.fontScale >= 1.5f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                LocalNimboThemeTokens.current.subtleSurface,
                RoundedCornerShape(24.dp)
            )
            .padding(18.dp)
    ) {
        Text(stringResource(Res.string.units), fontWeight = FontWeight.SemiBold)
        Text(
            stringResource(
                Res.string.automatic_units_description,
                units.temperatureSymbol,
                units.windSymbol
            ),
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(12.dp))
        if (accessibilityLayout) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                UnitPreference.entries.forEach { option ->
                    UnitButton(option, preference, onPreferenceChanged, Modifier.fillMaxWidth())
                }
            }
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                UnitPreference.entries.forEach { option ->
                    UnitButton(option, preference, onPreferenceChanged, Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun ThemeCard(preference: ThemePreference, onPreferenceChanged: (ThemePreference) -> Unit) {
    val accessibilityLayout = LocalDensity.current.fontScale >= 1.5f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                LocalNimboThemeTokens.current.subtleSurface,
                RoundedCornerShape(24.dp)
            )
            .padding(18.dp)
    ) {
        Text(stringResource(Res.string.theme), fontWeight = FontWeight.SemiBold)
        Text(
            stringResource(Res.string.theme_description),
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(12.dp))
        if (accessibilityLayout) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                ThemePreference.entries.forEach { option ->
                    ThemeButton(option, preference, onPreferenceChanged, Modifier.fillMaxWidth())
                }
            }
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ThemePreference.entries.forEach { option ->
                    ThemeButton(option, preference, onPreferenceChanged, Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun ThemeButton(
    option: ThemePreference,
    preference: ThemePreference,
    onPreferenceChanged: (ThemePreference) -> Unit,
    modifier: Modifier
) {
    val selectedOption = option == preference
    val buttonModifier = modifier.semantics {
        selected = selectedOption
        role = Role.RadioButton
    }
    val content: @Composable () -> Unit = {
        Text(
            when (option) {
                ThemePreference.System -> stringResource(Res.string.theme_system)
                ThemePreference.Light -> stringResource(Res.string.theme_light)
                ThemePreference.Dark -> stringResource(Res.string.theme_dark)
            },
            maxLines = 1,
            style = MaterialTheme.typography.labelLarge
        )
    }
    if (selectedOption) {
        Button(
            onClick = {},
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 6.dp),
            content = { content() }
        )
    } else {
        OutlinedButton(
            onClick = { onPreferenceChanged(option) },
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 6.dp),
            content = { content() }
        )
    }
}

@Composable
private fun UnitButton(
    option: UnitPreference,
    preference: UnitPreference,
    onPreferenceChanged: (UnitPreference) -> Unit,
    modifier: Modifier
) {
    val selectedOption = option == preference
    val buttonModifier = modifier.semantics {
        selected = selectedOption
        role = Role.RadioButton
    }
    val content: @Composable () -> Unit = {
        Text(
            when (option) {
                UnitPreference.Automatic -> stringResource(Res.string.unit_auto)
                UnitPreference.Metric -> stringResource(Res.string.unit_metric)
                UnitPreference.Imperial -> stringResource(Res.string.unit_imperial)
            },
            maxLines = 1,
            style = MaterialTheme.typography.labelLarge
        )
    }
    if (selectedOption) {
        Button(
            onClick = {},
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 6.dp),
            content = { content() }
        )
    } else {
        OutlinedButton(
            onClick = { onPreferenceChanged(option) },
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 6.dp),
            content = { content() }
        )
    }
}

@Composable
private fun OutsideCard(recommendation: OutsideRecommendation, timezone: String) {
    val reasonLabels = mapOf(
        OutsideReason.ComfortableTemperature to stringResource(Res.string.reason_comfortable),
        OutsideReason.LowerHeat to stringResource(Res.string.reason_milder),
        OutsideReason.Dry to stringResource(Res.string.reason_dry),
        OutsideReason.LightWind to stringResource(Res.string.reason_light_wind),
        OutsideReason.LowUv to stringResource(Res.string.reason_low_uv)
    )
    val hazardLabels = mapOf(
        OutsideHazard.ExtremeHeat to stringResource(Res.string.hazard_extreme_heat),
        OutsideHazard.ExtremeCold to stringResource(Res.string.hazard_extreme_cold),
        OutsideHazard.Thunderstorm to stringResource(Res.string.hazard_thunderstorm),
        OutsideHazard.HeavyPrecipitation to stringResource(Res.string.hazard_heavy_precipitation),
        OutsideHazard.StrongWind to stringResource(Res.string.hazard_strong_wind)
    )
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                LocalNimboThemeTokens.current.cardSurface,
                RoundedCornerShape(24.dp)
            )
            .padding(18.dp)
    ) {
        Text(stringResource(Res.string.best_time_outside), fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(8.dp))
        when (recommendation) {
            is OutsideRecommendation.Recommended -> {
                Text(
                    text = stringResource(
                        Res.string.time_range,
                        isolatedLocalHour(recommendation.startEpochSeconds, timezone),
                        isolatedLocalHour(recommendation.endEpochSeconds, timezone)
                    ),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold
                )
                if (recommendation.reasons.isNotEmpty()) {
                    Text(
                        recommendation.reasons.joinToString(" · ") { reasonLabels.getValue(it) },
                        color = MaterialTheme.colorScheme.secondary
                    )
                }
            }
            is OutsideRecommendation.Unsafe -> {
                Text(
                    stringResource(Res.string.no_safe_window),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    recommendation.hazards.joinToString(" · ") { hazardLabels.getValue(it) },
                    color = MaterialTheme.colorScheme.secondary
                )
            }
            OutsideRecommendation.Unavailable -> Text(
                stringResource(Res.string.not_enough_data),
                color = MaterialTheme.colorScheme.secondary
            )
        }
    }
}

@Composable
private fun Timeline(
    weather: WeatherSnapshot,
    selected: WeatherHour,
    units: DisplayUnits,
    contentPadding: Dp,
    onSelected: (WeatherHour) -> Unit
) {
    val now = Clock.System.now().epochSeconds
    val nowIndex = weather.timeline.indices.minByOrNull { index ->
        abs(weather.timeline[index].epochSeconds - now)
    } ?: 0
    val timelineScroll = rememberLazyListState(
        initialFirstVisibleItemIndex = (nowIndex - 2).coerceAtLeast(0)
    )
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            state = timelineScroll,
            contentPadding = PaddingValues(horizontal = contentPadding),
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            items(
                count = weather.timeline.size,
                key = { index -> weather.timeline[index].epochSeconds }
            ) { index ->
                val hour = weather.timeline[index]
                val past = hour.epochSeconds < now - 1_800
                val isNow = abs(hour.epochSeconds - now) < 1_800
                val isSelected = hour.epochSeconds == selected.epochSeconds
                val hourLabel = isolatedLocalHour(hour.epochSeconds, weather.location.timezone)
                val hourDescription = stringResource(
                    Res.string.hour_accessibility_full,
                    hourLabel,
                    units.temperature(hour.temperatureC),
                    weatherCondition(hour.weatherCode).label(),
                    units.temperature(hour.apparentTemperatureC),
                    hour.precipitationProbability,
                    units.wind(hour.windKph),
                    units.windSymbol
                )
                Column(
                    modifier = Modifier
                        .width(64.dp)
                        .alpha(
                            if (past) {
                                LocalNimboThemeTokens.current.pastContentAlpha
                            } else {
                                1f
                            }
                        )
                        .clip(RoundedCornerShape(18.dp))
                        .background(
                            if (isSelected) {
                                LocalNimboThemeTokens.current.selectedSurface
                            } else {
                                Color.Transparent
                            }
                        )
                        .clickable { onSelected(hour) }
                        .semantics {
                            contentDescription = hourDescription
                            this.selected = isSelected
                            role = Role.Button
                        }
                        .padding(vertical = 10.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        if (isNow) stringResource(Res.string.now) else hourLabel,
                        style = MaterialTheme.typography.labelSmall
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        weatherCondition(hour.weatherCode).symbol(),
                        fontSize = 20.sp
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "${units.temperature(hour.temperatureC)}°",
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        if (hour.precipitationProbability > 0) {
                            "${hour.precipitationProbability}%"
                        } else {
                            " "
                        },
                        color = if (hour.precipitationProbability > 0) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            Color.Transparent
                        },
                        style = MaterialTheme.typography.labelSmall
                    )
                    Spacer(Modifier.height(6.dp))
                    Box(
                        Modifier.size(6.dp).background(
                            if (isNow) MaterialTheme.colorScheme.primary else Color.Transparent,
                            CircleShape
                        )
                    )
                }
            }
        }
    }
}

@Composable
private fun SelectedHour(hour: WeatherHour, timezone: String, units: DisplayUnits) {
    val accessibilityLayout = LocalDensity.current.fontScale >= 1.5f
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                LocalNimboThemeTokens.current.cardSurface,
                RoundedCornerShape(24.dp)
            )
            .padding(18.dp)
    ) {
        Text(isolatedLocalHour(hour.epochSeconds, timezone), fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(10.dp))
        HorizontalDivider(color = LocalNimboThemeTokens.current.divider)
        Spacer(Modifier.height(12.dp))
        if (accessibilityLayout) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                HourDetails(hour, units)
            }
        } else {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                HourDetails(hour, units)
            }
        }
    }
}

@Composable
private fun HourDetails(hour: WeatherHour, units: DisplayUnits) {
    Detail(
        stringResource(Res.string.detail_feels_like),
        "${units.temperature(hour.apparentTemperatureC)}°"
    )
    Detail(stringResource(Res.string.detail_rain), "${hour.precipitationProbability}%")
    Detail(
        stringResource(Res.string.detail_wind),
        stringResource(Res.string.wind_value, units.wind(hour.windKph), units.windSymbol)
    )
}

@Composable
private fun Detail(label: String, value: String) {
    Column {
        Text(
            label,
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.labelMedium
        )
        Text(value, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun comparisonInsight(comparison: TemperatureComparison): String = when (comparison) {
    TemperatureComparison.MuchWarmer -> stringResource(Res.string.comparison_much_warmer)
    TemperatureComparison.Warmer -> stringResource(Res.string.comparison_warmer)
    TemperatureComparison.Similar -> stringResource(Res.string.comparison_similar)
    TemperatureComparison.Cooler -> stringResource(Res.string.comparison_cooler)
    TemperatureComparison.MuchCooler -> stringResource(Res.string.comparison_much_cooler)
    TemperatureComparison.Unavailable -> stringResource(Res.string.comparison_unavailable)
}

@Composable
private fun upcomingInsight(insight: UpcomingInsight, timezone: String): String = when (insight) {
    is UpcomingInsight.RainLikely -> stringResource(
        Res.string.upcoming_rain,
        isolatedLocalHour(insight.epochSeconds, timezone)
    )
    is UpcomingInsight.TurningCooler -> stringResource(
        Res.string.upcoming_cooler,
        isolatedLocalHour(insight.epochSeconds, timezone)
    )
    is UpcomingInsight.TurningWarmer -> stringResource(
        Res.string.upcoming_warmer,
        isolatedLocalHour(insight.epochSeconds, timezone)
    )
}

private fun isolatedLocalHour(epochSeconds: Long, timezone: String): String =
    "\u2066${formatLocalHour(epochSeconds, timezone)}\u2069"

@Composable
private fun UiMessage.localized(): String = stringResource(
    when (this) {
        UiMessage.NoMatchingPlaces -> Res.string.no_matching_places
        UiMessage.CitySearchUnavailable -> Res.string.city_search_unavailable
        UiMessage.LocationPermissionDenied -> Res.string.location_permission_denied
        UiMessage.LocationServicesDisabled -> Res.string.location_services_disabled
        UiMessage.LocationUnavailable -> Res.string.location_unavailable
        UiMessage.RefreshFailedShowingSaved -> Res.string.refresh_failed_saved
        UiMessage.WeatherUnavailable -> Res.string.weather_unavailable
    }
)

@Composable
private fun WeatherCondition.label(): String = when (this) {
    WeatherCondition.Clear -> stringResource(Res.string.condition_clear)
    WeatherCondition.MainlyClear -> stringResource(Res.string.condition_mostly_clear)
    WeatherCondition.Cloudy -> stringResource(Res.string.condition_cloudy)
    WeatherCondition.Fog -> stringResource(Res.string.condition_foggy)
    WeatherCondition.Drizzle -> stringResource(Res.string.condition_drizzle)
    WeatherCondition.Rain -> stringResource(Res.string.condition_rain)
    WeatherCondition.Snow -> stringResource(Res.string.condition_snow)
    WeatherCondition.Showers -> stringResource(Res.string.condition_showers)
    WeatherCondition.Thunderstorm -> stringResource(Res.string.condition_thunderstorm)
    WeatherCondition.Unknown -> stringResource(Res.string.condition_unknown)
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
