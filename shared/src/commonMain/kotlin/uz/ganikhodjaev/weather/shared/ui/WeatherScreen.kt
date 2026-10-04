package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeContentPadding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState as rememberVerticalScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.saveable.rememberSaveableStateHolder
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.onClick
import androidx.compose.ui.semantics.paneTitle
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.intl.Locale
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDirection
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.abs
import kotlin.time.Clock
import kotlin.time.Instant
import kotlinx.coroutines.launch
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import org.jetbrains.compose.resources.painterResource
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
import uz.ganikhodjaev.weather.shared.formatShareMessage
import uz.ganikhodjaev.weather.shared.model.AirQualityHour
import uz.ganikhodjaev.weather.shared.model.DailyForecast
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.weatherCondition
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickCity
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickLocation
import uz.ganikhodjaev.weather.shared.presentation.UiMessage
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState
import uz.ganikhodjaev.weather.shared.resources.*
import uz.ganikhodjaev.weather.shared.resources.Res

@OptIn(ExperimentalComposeUiApi::class)
@Composable
internal fun WeatherScreen(
    state: WeatherUiState,
    onRetry: () -> Unit,
    onSearchQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onLocationDeleted: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onChangeLocation: () -> Unit,
    onCancelLocationChange: () -> Unit,
    onUnitPreferenceChanged: (UnitPreference) -> Unit,
    onShareText: (String) -> Unit,
    storeUrl: String,
    reviewUrl: String,
    supportUrl: String,
    onAddLocationFromFirstForecastTip: () -> Unit,
    onDismissFirstForecastTip: () -> Unit,
    themePreference: ThemePreference,
    onThemePreferenceChanged: (ThemePreference) -> Unit
) {
    var page by rememberSaveable { mutableStateOf("forecast") }
    val savedScreens = rememberSaveableStateHolder()
    NimboBackHandler(
        enabled =
        page != "forecast" || (state as? WeatherUiState.ChooseLocation)?.canCancel == true
    ) {
        if (page == "licenses") {
            page = "settings"
        } else if (page == "settings") {
            page = "forecast"
        } else {
            onCancelLocationChange()
        }
    }
    val condition = (state as? WeatherUiState.Content)?.weather?.current?.weatherCode
        ?.let(::weatherCondition) ?: WeatherCondition.Cloudy
    NimboGlassScene(condition) {
        when (state) {
            WeatherUiState.Loading -> LoadingScreen()
            is WeatherUiState.ChooseLocation -> ChooseLocationScreen(
                state = state,
                onQueryChanged = onSearchQueryChanged,
                onLocationSelected = onLocationSelected,
                onLocationDeleted = onLocationDeleted,
                onUseDeviceLocation = onUseDeviceLocation,
                onCancel = onCancelLocationChange
            )
            is WeatherUiState.EmptyError -> ErrorScreen(
                message = state.message.localized(),
                onRetry = onRetry,
                onChangeLocation = onChangeLocation
            )
            is WeatherUiState.Content -> when (page) {
                "settings" -> SettingsScreen(
                    state,
                    themePreference,
                    onUnitPreferenceChanged,
                    onThemePreferenceChanged,
                    reviewUrl,
                    { page = "forecast" },
                    { page = "licenses" }
                )
                "licenses" -> LibraryLicenses { page = "settings" }
                else -> savedScreens.SaveableStateProvider("forecast") {
                    WeatherContent(
                        state,
                        onRetry,
                        onChangeLocation,
                        onShareText,
                        storeUrl,
                        onAddLocationFromFirstForecastTip,
                        onDismissFirstForecastTip,
                        onSettings = { page = "settings" }
                    )
                }
            }
        }
    }
}

@Composable
private fun ChooseLocationScreen(
    state: WeatherUiState.ChooseLocation,
    onQueryChanged: (String) -> Unit,
    onLocationSelected: (Location) -> Unit,
    onLocationDeleted: (Location) -> Unit,
    onUseDeviceLocation: () -> Unit,
    onCancel: () -> Unit
) {
    val keyboard = LocalSoftwareKeyboardController.current
    val focus = LocalFocusManager.current
    val selectLocation: (Location) -> Unit = { location ->
        keyboard?.hide()
        focus.clearFocus()
        onLocationSelected(location)
    }
    var pendingDeletion by remember { mutableStateOf<Location?>(null) }
    pendingDeletion?.let { location ->
        // Dialogs have their own window; do not sample the main window's graphics layer.
        CompositionLocalProvider(LocalGlassBackdrop provides null) {
            AlertDialog(
                onDismissRequest = { pendingDeletion = null },
                title = { Text(stringResource(Res.string.remove_saved_place)) },
                text = {
                    Text(
                        stringResource(
                            Res.string.remove_saved_place_message,
                            location.name.ifBlank { stringResource(Res.string.current_location) }
                        )
                    )
                },
                confirmButton = {
                    GlassButton(
                        onClick = {
                            onLocationDeleted(location)
                            pendingDeletion = null
                        }
                    ) {
                        Text(stringResource(Res.string.remove))
                    }
                },
                dismissButton = {
                    GlassButton(onClick = { pendingDeletion = null }) {
                        Text(stringResource(Res.string.cancel))
                    }
                }
            )
        }
    }
    val browsing = state.query.isBlank()
    val searchLabel = stringResource(Res.string.search_city)
    var searchFocused by remember { mutableStateOf(false) }
    val searchShape = RoundedCornerShape(28.dp)
    BoxWithConstraints(Modifier.fillMaxSize().safeContentPadding().imePadding()) {
        val compactHeader = maxHeight < 320.dp
        Column(
            modifier = Modifier.align(Alignment.TopCenter)
                .widthIn(max = 640.dp).fillMaxWidth().fillMaxHeight()
        ) {
            Row(
                Modifier.fillMaxWidth().padding(
                    horizontal = 24.dp,
                    vertical = if (compactHeader) 8.dp else 12.dp
                ),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Column(Modifier.weight(1f)) {
                    if (!compactHeader) {
                        Text(
                            stringResource(Res.string.brand),
                            style = MaterialTheme.typography.labelLarge,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(Modifier.height(4.dp))
                    }
                    Text(
                        stringResource(Res.string.choose_city),
                        style = if (compactHeader) {
                            MaterialTheme.typography.titleLarge
                        } else {
                            MaterialTheme.typography.headlineSmall
                        },
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.semantics { heading() }
                    )
                }
                if (state.canCancel) {
                    GlassIconButton(onClick = {
                        keyboard?.hide()
                        focus.clearFocus()
                        onCancel()
                    }) {
                        Icon(
                            painterResource(Res.drawable.ic_weather_clear_search),
                            stringResource(Res.string.cancel)
                        )
                    }
                }
            }
            Column(
                Modifier.weight(1f).verticalScroll(rememberVerticalScrollState())
                    .padding(horizontal = 24.dp).padding(top = 8.dp, bottom = 24.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    if (state.isOnboarding && browsing) {
                        Text(
                            stringResource(Res.string.onboarding_title),
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.secondary
                        )
                    }
                    TextField(
                        value = state.query,
                        onValueChange = onQueryChanged,
                        modifier = Modifier.fillMaxWidth()
                            .onFocusChanged { searchFocused = it.isFocused }
                            .semantics { contentDescription = searchLabel }
                            .nimboGlass(shape = searchShape)
                            .border(
                                1.dp,
                                if (searchFocused) {
                                    MaterialTheme.colorScheme.primary.copy(alpha = 0.45f)
                                } else {
                                    Color.Transparent
                                },
                                searchShape
                            ),
                        shape = searchShape,
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            focusedPlaceholderColor = MaterialTheme.colorScheme.secondary,
                            unfocusedPlaceholderColor = MaterialTheme.colorScheme.secondary
                        ),
                        singleLine = true,
                        textStyle = MaterialTheme.typography.bodyLarge,
                        placeholder = {
                            Text(
                                searchLabel,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                                modifier = Modifier.clearAndSetSemantics { }
                            )
                        },
                        leadingIcon = {
                            Icon(
                                painterResource(Res.drawable.ic_city_search),
                                null,
                                Modifier.size(22.dp),
                                tint = MaterialTheme.colorScheme.secondary
                            )
                        },
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                        keyboardActions = KeyboardActions(onSearch = {
                            keyboard?.hide()
                            focus.clearFocus()
                        }),
                        trailingIcon = {
                            if (state.query.isNotEmpty()) {
                                IconButton(onClick = { onQueryChanged("") }) {
                                    Icon(
                                        painterResource(Res.drawable.ic_weather_clear_search),
                                        stringResource(Res.string.clear_search),
                                        Modifier.size(20.dp),
                                        tint = MaterialTheme.colorScheme.secondary
                                    )
                                }
                            }
                        }
                    )
                }
                when {
                    state.isSearching -> CitySearchStatus(
                        stringResource(Res.string.searching),
                        true
                    )
                    state.message != null -> CitySearchStatus(state.message.localized())
                    !browsing && state.query.length < 2 ->
                        CitySearchStatus(stringResource(Res.string.search_minimum))
                }
                val results = state.results.takeIf {
                    !state.isSearching && state.message == null
                }.orEmpty()
                if (!browsing && results.isNotEmpty()) {
                    CitySection(title = stringResource(Res.string.search_results)) {
                        CityList {
                            results.forEachIndexed { index, location ->
                                if (index > 0) CityDivider()
                                CityRow(
                                    location = location,
                                    isSelected = location.id == state.activeLocationId,
                                    onClick = { selectLocation(location) }
                                )
                            }
                        }
                    }
                }
                if (browsing) {
                    if (state.savedLocations.isNotEmpty()) {
                        CitySection(title = stringResource(Res.string.saved_places)) {
                            CityList {
                                state.savedLocations.forEachIndexed { index, location ->
                                    if (index > 0) CityDivider()
                                    CityRow(
                                        location = location,
                                        isSelected = location.id == state.activeLocationId,
                                        onClick = { selectLocation(location) },
                                        onDelete = if (location.id == state.activeLocationId) {
                                            null
                                        } else {
                                            { pendingDeletion = location }
                                        }
                                    )
                                }
                            }
                        }
                    }
                    if (state.quickLocations.isNotEmpty()) {
                        CitySection(title = stringResource(Res.string.quick_places)) {
                            FlowRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                state.quickLocations.forEach { quickLocation ->
                                    val location = quickLocation.localized()
                                    GlassButton(onClick = { selectLocation(location) }) {
                                        Text(
                                            location.name,
                                            style = MaterialTheme.typography.bodyMedium
                                        )
                                    }
                                }
                            }
                        }
                    }
                    Column(Modifier.fillMaxWidth().nimboGlass()) {
                        Row(
                            Modifier.fillMaxWidth().sizeIn(minHeight = 56.dp)
                                .clip(RoundedCornerShape(24.dp))
                                .clickable(enabled = !state.isLocating, role = Role.Button) {
                                    keyboard?.hide()
                                    focus.clearFocus()
                                    onUseDeviceLocation()
                                }
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                painterResource(Res.drawable.ic_location),
                                null,
                                Modifier.size(22.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                stringResource(
                                    if (state.isLocating) {
                                        Res.string.finding_area
                                    } else {
                                        Res.string.use_location
                                    }
                                ),
                                modifier = Modifier.weight(1f).semantics {
                                    if (state.isLocating) liveRegion = LiveRegionMode.Polite
                                },
                                style = MaterialTheme.typography.labelLarge
                            )
                        }
                        Text(
                            stringResource(Res.string.location_privacy),
                            modifier = Modifier.padding(start = 16.dp, end = 16.dp, bottom = 16.dp),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.secondary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun CitySection(title: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(
            title,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.secondary,
            modifier = Modifier.semantics { heading() }
        )
        content()
    }
}

@Composable
private fun CityList(content: @Composable () -> Unit) {
    Column(Modifier.fillMaxWidth().nimboGlass().clip(RoundedCornerShape(24.dp))) { content() }
}

@Composable
private fun CityDivider() {
    HorizontalDivider(
        Modifier.padding(horizontal = 16.dp),
        color = LocalNimboThemeTokens.current.divider
    )
}

@Composable
private fun CityRow(
    location: Location,
    isSelected: Boolean,
    onClick: () -> Unit,
    onDelete: (() -> Unit)? = null
) {
    Row(
        modifier = Modifier.fillMaxWidth().background(
            if (isSelected) {
                MaterialTheme.colorScheme.primary.copy(
                    alpha = 0.08f
                )
            } else {
                Color.Transparent
            }
        ),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            Modifier.weight(1f).sizeIn(minHeight = 76.dp)
                .semantics(mergeDescendants = true) { selected = isSelected }
                .clickable(role = Role.Button, onClick = onClick)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                painterResource(
                    if (isSelected) {
                        Res.drawable.ic_city_selected
                    } else {
                        Res.drawable.ic_location
                    }
                ),
                null,
                Modifier.size(22.dp),
                tint = if (isSelected) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.secondary
                }
            )
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(
                    location.name.ifBlank { stringResource(Res.string.current_location) },
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold
                )
                if (location.regionAndCountry().isNotBlank()) {
                    Text(
                        location.regionAndCountry(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }
                if (isSelected) {
                    Text(
                        stringResource(Res.string.active_place),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
        if (onDelete != null) {
            IconButton(onClick = onDelete, modifier = Modifier.padding(end = 8.dp)) {
                Icon(
                    painterResource(Res.drawable.ic_delete),
                    "${location.name}, ${stringResource(Res.string.remove_saved_place)}",
                    tint = MaterialTheme.colorScheme.secondary
                )
            }
        }
    }
}

@Composable
private fun CitySearchStatus(message: String, loading: Boolean = false) {
    Row(
        Modifier.fillMaxWidth().nimboGlass().padding(20.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        if (loading) {
            CircularProgressIndicator(
                Modifier.size(20.dp).clearAndSetSemantics {
                },
                strokeWidth = 2.dp
            )
        }
        Text(
            message,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.secondary,
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }
        )
    }
}

@Composable
private fun UzbekistanQuickLocation.localized(): Location {
    val name = when (city) {
        UzbekistanQuickCity.Tashkent -> stringResource(Res.string.quick_city_tashkent)
        UzbekistanQuickCity.Samarkand -> stringResource(Res.string.quick_city_samarkand)
        UzbekistanQuickCity.Namangan -> stringResource(Res.string.quick_city_namangan)
        UzbekistanQuickCity.Andijan -> stringResource(Res.string.quick_city_andijan)
        UzbekistanQuickCity.Fergana -> stringResource(Res.string.quick_city_fergana)
        UzbekistanQuickCity.Bukhara -> stringResource(Res.string.quick_city_bukhara)
        UzbekistanQuickCity.Nukus -> stringResource(Res.string.quick_city_nukus)
    }
    return localized(
        name = name,
        country = stringResource(Res.string.quick_country_uzbekistan)
    )
}

@Composable
private fun LoadingScreen() {
    val loadingDescription = stringResource(Res.string.loading_weather)
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            modifier = Modifier.nimboGlass(shape = RoundedCornerShape(50)).padding(20.dp)
                .semantics {
                    contentDescription = loadingDescription
                    liveRegion =
                        LiveRegionMode.Polite
                }
        )
    }
}

@Composable
private fun ErrorScreen(message: String, onRetry: () -> Unit, onChangeLocation: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .safeContentPadding(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                modifier = Modifier.widthIn(
                    max = 560.dp
                ).fillMaxWidth().verticalScroll(rememberVerticalScrollState()).padding(24.dp)
                    .nimboGlass().padding(24.dp),
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
                    modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.secondary
                )
                Spacer(Modifier.height(24.dp))
                GlassButton(onClick = onRetry) { Text(stringResource(Res.string.try_again)) }
                Spacer(Modifier.height(8.dp))
                GlassButton(onClick = onChangeLocation) {
                    Text(stringResource(Res.string.change_place))
                }
            }
        }
    }
}

@Composable
private fun WeatherContent(
    state: WeatherUiState.Content,
    onRefresh: () -> Unit,
    onChangeLocation: () -> Unit,
    onShareText: (String) -> Unit,
    storeUrl: String,
    onAddLocationFromFirstForecastTip: () -> Unit,
    onDismissFirstForecastTip: () -> Unit,
    onSettings: () -> Unit
) {
    val weather = state.weather
    var selectedEpoch by rememberSaveable(weather.location.id) { mutableStateOf<Long?>(null) }
    val now = rememberWeatherNow()
    val selected = selectedForecastHour(weather.timeline, selectedEpoch, now) ?: weather.current
    val condition = weatherCondition(weather.current.weatherCode)
    val insights = remember(weather) { WeatherInsightEngine().evaluate(weather) }
    val weatherShareSummary = stringResource(
        Res.string.share_weather_text,
        weather.location.name.ifBlank { stringResource(Res.string.current_location) },
        state.displayUnits.temperature(weather.current.temperatureC),
        weather.current.precipitationProbability
    )
    val shareMessage = formatShareMessage(
        weatherSummary = weatherShareSummary,
        storeCallToAction = stringResource(Res.string.share_store_cta),
        storeUrl = storeUrl
    )
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
    ) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .windowInsetsPadding(WindowInsets.safeDrawing)
        ) {
            val wideLayout = maxWidth >= 840.dp
            val horizontalPadding = if (wideLayout) 36.dp else 24.dp
            val recentDays = remember(weather) { recentDaySummaries(weather) }
            val openPage = rememberWebPageOpener()
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
                        onChangeLocation = onChangeLocation,
                        onShare = { onShareText(shareMessage) },
                        onSettings = onSettings
                    )
                }

                Spacer(Modifier.height(if (wideLayout) 40.dp else 32.dp))
                CenteredSection(horizontalPadding) {
                    CurrentSummary(state = state, condition = condition, insights = insights)
                }
                Spacer(Modifier.height(20.dp))
                CenteredSection(horizontalPadding) {
                    OutsideCard(outside, weather.location.timezone)
                }
                if (state.showFirstForecastTip) {
                    Spacer(Modifier.height(20.dp))
                    CenteredSection(horizontalPadding) {
                        FirstForecastTip(
                            onAddLocation = onAddLocationFromFirstForecastTip,
                            onDismiss = onDismissFirstForecastTip
                        )
                    }
                }
                Spacer(Modifier.height(32.dp))
                WeatherDetails(
                    state = state,
                    selected = selected,
                    recentDays = recentDays,
                    horizontalPadding = horizontalPadding,
                    onSelected = { selectedEpoch = it.epochSeconds },
                    onCurrent = { selectedEpoch = null },
                    now = now
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
                                .clickable { openPage("https://open-meteo.com/") }
                                .padding(vertical = 12.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FirstForecastTip(onAddLocation: () -> Unit, onDismiss: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .nimboGlass(shape = RoundedCornerShape(20.dp))
            .padding(horizontal = 20.dp, vertical = 16.dp)
    ) {
        Text(
            text = stringResource(Res.string.first_forecast_tip_title),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        Spacer(Modifier.height(6.dp))
        Text(
            text = stringResource(Res.string.first_forecast_tip_body),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.secondary
        )
        Spacer(Modifier.height(12.dp))
        GlassButton(
            onClick = onAddLocation,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(stringResource(Res.string.first_forecast_tip_add_city))
        }
        GlassButton(
            onClick = onDismiss,
            modifier = Modifier.align(Alignment.End)
        ) {
            Text(stringResource(Res.string.got_it))
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
    onChangeLocation: () -> Unit,
    onShare: () -> Unit,
    onSettings: () -> Unit
) {
    val weather = state.weather
    val location: @Composable (Modifier) -> Unit = { modifier ->
        Column(modifier = modifier) {
            Text(
                text = weather.location.name.ifBlank {
                    stringResource(Res.string.current_location)
                },
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.SemiBold
            )
            if (weather.location.regionAndCountry().isNotBlank()) {
                Text(
                    text = weather.location.regionAndCountry(),
                    color = MaterialTheme.colorScheme.secondary
                )
            }
        }
    }
    val actions: @Composable () -> Unit = {
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            GlassIconButton(onClick = onSettings) {
                Icon(
                    painterResource(Res.drawable.ic_weather_settings),
                    stringResource(Res.string.settings)
                )
            }
            GlassIconButton(onClick = onShare) {
                Icon(
                    painter = painterResource(Res.drawable.ic_share),
                    contentDescription = stringResource(Res.string.share_weather)
                )
            }
            GlassIconButton(
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
            GlassIconButton(onClick = onChangeLocation, selected = true) {
                Icon(
                    painter = painterResource(Res.drawable.ic_location),
                    contentDescription = stringResource(Res.string.change_place)
                )
            }
        }
    }
    BoxWithConstraints(Modifier.fillMaxWidth()) {
        if (maxWidth < 600.dp || LocalDensity.current.fontScale > 1.3f) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                location(Modifier.fillMaxWidth())
                actions()
            }
        } else {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                location(Modifier.weight(1f).padding(end = 12.dp))
                actions()
            }
        }
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
    WeatherIcon(condition, Modifier.size(48.dp))
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
    Spacer(Modifier.height(12.dp))
    val status = when {
        state.isRefreshing -> stringResource(Res.string.refreshing)
        state.refreshMessage != null -> state.refreshMessage.localized()
        weather.isStale -> stringResource(Res.string.saved_weather)
        else -> stringResource(Res.string.forecast_current)
    }
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        if (state.isRefreshing) {
            CircularProgressIndicator(
                Modifier.size(20.dp).clearAndSetSemantics {},
                strokeWidth = 2.dp
            )
        }
        Text(
            status,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }
        )
    }
    Text(
        stringResource(
            Res.string.last_updated,
            localDateTime(weather.fetchedAtEpochSeconds, weather.location.timezone)
        ),
        color = MaterialTheme.colorScheme.secondary,
        style = MaterialTheme.typography.bodySmall
    )
}

@Composable
private fun WeatherDetails(
    state: WeatherUiState.Content,
    selected: WeatherHour,
    recentDays: List<RecentDaySummary>,
    horizontalPadding: Dp,
    onSelected: (WeatherHour) -> Unit,
    onCurrent: () -> Unit,
    now: Long
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
        onSelected = onSelected,
        onCurrent = onCurrent,
        now = now
    )
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        SelectedHour(selected, weather.location.timezone, state.displayUnits)
    }
    Spacer(Modifier.height(18.dp))
    CenteredSection(horizontalPadding) {
        AirQualityCard(
            weather.airQuality.minByOrNull { abs(it.epochSeconds - now) },
            weather.location.timezone,
            now
        )
    }
    if (weather.dailyForecast.isNotEmpty()) {
        Spacer(Modifier.height(18.dp))
        TenDayForecast(
            days = weather.dailyForecast,
            timezone = weather.location.timezone,
            units = state.displayUnits,
            contentPadding = horizontalPadding
        )
    }
    if (recentDays.isNotEmpty()) {
        Spacer(Modifier.height(18.dp))
        RecentDays(recentDays, state.displayUnits, horizontalPadding)
    }
}

@Composable
private fun AirQualityCard(air: AirQualityHour?, timezone: String, now: Long) {
    val aqi = air?.usAqi
    val label = when {
        aqi == null || aqi < 0 -> stringResource(Res.string.aqi_unavailable)
        aqi <= 50 -> stringResource(Res.string.aqi_good)
        aqi <= 100 -> stringResource(Res.string.aqi_moderate)
        aqi <= 150 -> stringResource(Res.string.aqi_unhealthy_sensitive)
        aqi <= 200 -> stringResource(Res.string.aqi_unhealthy)
        aqi <= 300 -> stringResource(Res.string.aqi_very_unhealthy)
        else -> stringResource(Res.string.aqi_hazardous)
    }
    Column(
        Modifier.fillMaxWidth().nimboGlass().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("${stringResource(Res.string.air_quality)} · US AQI", fontWeight = FontWeight.SemiBold)
        if (aqi != null &&
            aqi >= 0
        ) {
            Text(aqi.toString(), style = MaterialTheme.typography.headlineLarge)
        }
        Text(label, color = MaterialTheme.colorScheme.secondary)
        if (air != null) {
            Text(
                stringResource(Res.string.aqi_time, localDateTime(air.epochSeconds, timezone)),
                style = MaterialTheme.typography.bodySmall
            )
            if (isAirQualityStale(
                    air,
                    now
                )
            ) {
                Text(
                    stringResource(Res.string.aqi_stale),
                    style = MaterialTheme.typography.bodySmall
                )
            }
            listOfNotNull(
                air.pm25?.let { "PM2.5 ${it.toInt()} μg/m³" },
                air.pm10?.let { "PM10 ${it.toInt()} μg/m³" }
            ).forEach { Text(it, style = MaterialTheme.typography.bodySmall) }
        }
        Text(
            stringResource(Res.string.aqi_scale_description),
            style = MaterialTheme.typography.bodySmall
        )
        Text(
            stringResource(Res.string.air_quality_attribution),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.secondary
        )
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
private fun TenDayForecast(
    days: List<DailyForecast>,
    timezone: String,
    units: DisplayUnits,
    contentPadding: Dp
) {
    var selectedDay by rememberSaveable { mutableStateOf<Long?>(null) }
    val selected = days.firstOrNull { it.epochSeconds == selectedDay }
    NimboBackHandler(enabled = selected != null) { selectedDay = null }
    Column {
        CenteredSection(contentPadding) {
            Text(stringResource(Res.string.ten_day_forecast), fontWeight = FontWeight.SemiBold)
        }
        Spacer(Modifier.height(10.dp))
        LazyRow(
            contentPadding = PaddingValues(horizontal = contentPadding),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(days.size, key = { days[it].epochSeconds }) { index ->
                val day = days[index]
                val title = formatLocalDay(day.epochSeconds, timezone)
                val condition = weatherCondition(day.weatherCode).label()
                val range =
                    stringResource(
                        Res.string.temperature_range,
                        units.temperature(day.temperatureMinC),
                        units.temperature(day.temperatureMaxC)
                    )
                Column(
                    Modifier.width((152 * LocalDensity.current.fontScale.coerceAtMost(2f)).dp)
                        .nimboGlass(
                            shape = RoundedCornerShape(18.dp),
                            selected =
                            selectedDay == day.epochSeconds
                        )
                        .clickable {
                            selectedDay =
                                if (selectedDay == day.epochSeconds) null else day.epochSeconds
                        }
                        .semantics(mergeDescendants = true) {
                            this.selected =
                                selectedDay == day.epochSeconds
                            role = Role.Button
                        }
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(title, style = MaterialTheme.typography.labelMedium)
                    WeatherIcon(weatherCondition(day.weatherCode), Modifier.size(28.dp))
                    Text(condition, style = MaterialTheme.typography.bodySmall)
                    Text(range, fontWeight = FontWeight.SemiBold)
                    day.precipitationProbabilityMax?.let {
                        Text("$it%", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        if (selected != null) {
            Spacer(Modifier.height(12.dp))
            CenteredSection(contentPadding) {
                Column(
                    Modifier.fillMaxWidth().nimboGlass().padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        formatLocalDay(selected.epochSeconds, timezone),
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.semantics {
                            heading()
                        }
                    )
                    Text(weatherCondition(selected.weatherCode).label())
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Detail(
                            stringResource(Res.string.detail_feels_like),
                            stringResource(
                                Res.string.temperature_range,
                                units.temperature(selected.apparentTemperatureMinC),
                                units.temperature(selected.apparentTemperatureMaxC)
                            )
                        )
                        selected.precipitationProbabilityMax?.let {
                            Detail(stringResource(Res.string.detail_rain), "$it%")
                        }
                        selected.precipitationMm?.let {
                            Detail(
                                stringResource(Res.string.detail_precipitation),
                                "${kotlin.math.round(
                                    units.precipitation(it) * 100
                                ) / 100} ${units.precipitationSymbol}"
                            )
                        }
                        Detail(
                            stringResource(Res.string.detail_wind),
                            "${units.wind(selected.windMaxKph)} ${units.windSymbol}"
                        )
                        selected.gustMaxKph?.let {
                            Detail(
                                stringResource(Res.string.detail_gust),
                                "${units.wind(it)} ${units.windSymbol}"
                            )
                        }
                        selected.uvIndexMax?.let {
                            Detail(stringResource(Res.string.detail_uv), it.toString())
                        }
                        selected.sunriseEpochSeconds.takeIf {
                            it > 0
                        }?.let {
                            Detail(
                                stringResource(Res.string.detail_sunrise),
                                isolatedLocalHour(it, timezone)
                            )
                        }
                        selected.sunsetEpochSeconds.takeIf {
                            it > 0
                        }?.let {
                            Detail(
                                stringResource(Res.string.detail_sunset),
                                isolatedLocalHour(it, timezone)
                            )
                        }
                    }
                    GlassButton(onClick = {
                        selectedDay = null
                    }) { Text(stringResource(Res.string.close_details)) }
                }
            }
        }
    }
}

private data class RecentDaySummary(
    val epochSeconds: Long,
    val timezone: String,
    val averageC: Double,
    val lowC: Double,
    val highC: Double
)

@Composable
private fun RecentDays(days: List<RecentDaySummary>, units: DisplayUnits, contentPadding: Dp) {
    val recentDaysScroll = rememberLazyListState()
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
                key = { index -> days[index].epochSeconds }
            ) { index ->
                val day = days[index]
                Column(
                    modifier = Modifier
                        .width((156 * LocalDensity.current.fontScale.coerceAtMost(2f)).dp)
                        .nimboGlass(shape = RoundedCornerShape(18.dp))
                        .padding(14.dp)
                ) {
                    Text(
                        formatLocalDay(day.epochSeconds, day.timezone),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.secondary
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        stringResource(Res.string.average_label),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.secondary
                    )
                    Text(
                        "${units.temperature(day.averageC)}°",
                        fontWeight = FontWeight.SemiBold,
                        style = MaterialTheme.typography.titleLarge
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
            epochSeconds = hours.first().epochSeconds,
            timezone = weather.location.timezone,
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
    val direction = LocalLayoutDirection.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .nimboGlass(shape = RoundedCornerShape(24.dp))
            .padding(18.dp)
    ) {
        Text(stringResource(Res.string.units), fontWeight = FontWeight.SemiBold)
        Text(
            stringResource(
                if (preference ==
                    UnitPreference.Automatic
                ) {
                    Res.string.automatic_units_description
                } else {
                    Res.string.selected_units_description
                },
                isolatedUnitSymbol(units.temperatureSymbol, direction),
                isolatedUnitSymbol(units.windSymbol, direction)
            ),
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(12.dp))
        FlowRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            UnitPreference.entries.forEach { option ->
                UnitButton(option, preference, onPreferenceChanged, Modifier.widthIn(min = 100.dp))
            }
        }
    }
}

private fun isolatedUnitSymbol(symbol: String, direction: LayoutDirection): String =
    if (direction == LayoutDirection.Rtl) "\u2066$symbol\u2069" else symbol

@Composable
private fun ThemeCard(preference: ThemePreference, onPreferenceChanged: (ThemePreference) -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .nimboGlass(shape = RoundedCornerShape(24.dp))
            .padding(18.dp)
    ) {
        Text(stringResource(Res.string.theme), fontWeight = FontWeight.SemiBold)
        Text(
            stringResource(Res.string.theme_description),
            color = MaterialTheme.colorScheme.secondary,
            style = MaterialTheme.typography.bodySmall
        )
        Spacer(Modifier.height(12.dp))
        FlowRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            ThemePreference.entries.forEach { option ->
                ThemeButton(option, preference, onPreferenceChanged, Modifier.widthIn(min = 100.dp))
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
            style = MaterialTheme.typography.labelLarge
        )
    }
    if (selectedOption) {
        GlassButton(
            onClick = {},
            selected = true,
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
            content = { content() }
        )
    } else {
        GlassButton(
            onClick = { onPreferenceChanged(option) },
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
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
                UnitPreference.Metric -> "°C · km/h"
                UnitPreference.Imperial -> "°F · mph"
            },
            style = MaterialTheme.typography.labelLarge.copy(
                textDirection = if (option == UnitPreference.Automatic) {
                    TextDirection.Content
                } else {
                    TextDirection.Ltr
                }
            )
        )
    }
    if (selectedOption) {
        GlassButton(
            onClick = {},
            selected = true,
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
            content = { content() }
        )
    } else {
        GlassButton(
            onClick = { onPreferenceChanged(option) },
            modifier = buttonModifier,
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
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
            .nimboGlass(shape = RoundedCornerShape(24.dp))
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
    onSelected: (WeatherHour) -> Unit,
    onCurrent: () -> Unit,
    now: Long
) {
    val nowIndex = currentHourIndex(weather.timeline, now)
    val selectedIndex = weather.timeline.indexOfFirst {
        it.epochSeconds == selected.epochSeconds
    }.coerceAtLeast(0)
    val timelineScroll = rememberLazyListState(initialFirstVisibleItemIndex = selectedIndex)
    var scrolledSelection by rememberSaveable(weather.location.id) { mutableStateOf<Long?>(null) }
    val scope = rememberCoroutineScope()
    LaunchedEffect(weather.location.id, selected.epochSeconds) {
        if (scrolledSelection != selected.epochSeconds) {
            timelineScroll.scrollToItem(selectedIndex)
            scrolledSelection = selected.epochSeconds
        }
    }
    if (nowIndex != null) {
        CenteredSection(contentPadding) {
            GlassButton(onClick = {
                onCurrent()
                scope.launch { timelineScroll.scrollToItem(nowIndex) }
            }) { Text(stringResource(Res.string.return_current_hour)) }
        }
    }
    Spacer(Modifier.height(8.dp))
    val appDirection = LocalLayoutDirection.current
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            state = timelineScroll,
            contentPadding = PaddingValues(horizontal = contentPadding),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(weather.timeline.size, key = { weather.timeline[it].epochSeconds }) { index ->
                val hour = weather.timeline[index]
                val isNow = index == nowIndex
                val isSelected = hour.epochSeconds == selected.epochSeconds
                val timezone = weather.location.timezone
                val dayStart =
                    index == 0 ||
                        weatherDate(hour.epochSeconds, timezone) !=
                        weatherDate(weather.timeline[index - 1].epochSeconds, timezone)
                val date = formatLocalDay(hour.epochSeconds, timezone)
                val hourLabel = isolatedLocalHour(hour.epochSeconds, timezone)
                val description = stringResource(
                    Res.string.hour_accessibility_full,
                    "$date, $hourLabel",
                    units.temperature(hour.temperatureC),
                    weatherCondition(hour.weatherCode).label(),
                    units.temperature(hour.apparentTemperatureC),
                    hour.precipitationProbability,
                    units.wind(hour.windKph),
                    units.windSymbol
                ) + if (isNow) ", ${stringResource(Res.string.now)}" else ""
                CompositionLocalProvider(LocalLayoutDirection provides appDirection) {
                    Column(
                        Modifier.width((108 * LocalDensity.current.fontScale.coerceAtMost(2f)).dp)
                            .nimboGlass(shape = RoundedCornerShape(18.dp), selected = isSelected)
                            .clickable { onSelected(hour) }
                            .clearAndSetSemantics {
                                contentDescription = description
                                this.selected =
                                    isSelected
                                role = Role.Button
                                onClick {
                                    onSelected(hour)
                                    true
                                }
                            }
                            .padding(horizontal = 10.dp, vertical = 12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            date,
                            style = MaterialTheme.typography.labelSmall,
                            color = if (dayStart) {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.secondary
                            },
                            fontWeight = if (dayStart) FontWeight.Bold else FontWeight.Normal
                        )
                        Text(
                            if (isNow) stringResource(Res.string.now) else hourLabel,
                            style = MaterialTheme.typography.labelMedium
                        )
                        WeatherIcon(weatherCondition(hour.weatherCode), Modifier.size(28.dp))
                        Text(
                            "${units.temperature(hour.temperatureC)}°",
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            "${hour.precipitationProbability}%",
                            style = MaterialTheme.typography.labelSmall
                        )
                        Box(
                            Modifier.size(
                                6.dp
                            ).background(
                                if (isNow) MaterialTheme.colorScheme.primary else Color.Transparent,
                                CircleShape
                            )
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SelectedHour(hour: WeatherHour, timezone: String, units: DisplayUnits) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .nimboGlass(shape = RoundedCornerShape(24.dp))
            .padding(18.dp)
    ) {
        Text(localDateTime(hour.epochSeconds, timezone), fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(10.dp))
        HorizontalDivider(color = LocalNimboThemeTokens.current.divider)
        Spacer(Modifier.height(12.dp))
        FlowRow(
            Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(24.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            HourDetails(hour, units)
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
        UiMessage.SavedLocationLimitReached -> Res.string.saved_location_limit_reached
        UiMessage.ChangesCouldNotBeSaved -> Res.string.changes_could_not_be_saved
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

@Composable
private fun WeatherIcon(condition: WeatherCondition, modifier: Modifier = Modifier) {
    val drawable = when (condition) {
        WeatherCondition.Clear -> Res.drawable.ic_weather_clear
        WeatherCondition.MainlyClear -> Res.drawable.ic_weather_mainly_clear
        WeatherCondition.Cloudy -> Res.drawable.ic_weather_cloudy
        WeatherCondition.Fog -> Res.drawable.ic_weather_fog
        WeatherCondition.Drizzle -> Res.drawable.ic_weather_drizzle
        WeatherCondition.Rain -> Res.drawable.ic_weather_rain
        WeatherCondition.Snow -> Res.drawable.ic_weather_snow
        WeatherCondition.Showers -> Res.drawable.ic_weather_showers
        WeatherCondition.Thunderstorm -> Res.drawable.ic_weather_storm
        WeatherCondition.Unknown -> Res.drawable.ic_weather_unknown
    }
    Icon(painterResource(drawable), contentDescription = null, modifier = modifier)
}

private fun Location.regionAndCountry(): String =
    listOf(region, country).filter(String::isNotBlank).distinct().joinToString(", ")

private fun localDateTime(epoch: Long, timezone: String): String =
    "${formatLocalDay(epoch, timezone)}, ${isolatedLocalHour(epoch, timezone)}"

@Composable
private fun rememberWeatherNow(): Long {
    var now by remember { mutableStateOf(Clock.System.now().epochSeconds) }
    LaunchedEffect(Unit) {
        while (true) {
            now = Clock.System.now().epochSeconds
            kotlinx.coroutines.delay(30_000)
        }
    }
    return now
}

@Composable
private fun SettingsScreen(
    state: WeatherUiState.Content,
    theme: ThemePreference,
    onUnits: (UnitPreference) -> Unit,
    onTheme: (ThemePreference) -> Unit,
    reviewUrl: String,
    onBack: () -> Unit,
    onLicenses: () -> Unit
) {
    val uri = LocalUriHandler.current
    val openPage = rememberWebPageOpener()
    val language = Locale.current.language
    val title = stringResource(Res.string.settings)
    Column(
        Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing)
            .semantics { paneTitle = title }
            .verticalScroll(rememberVerticalScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {
        GlassButton(onClick = onBack) { Text(stringResource(Res.string.back)) }
        Text(
            title,
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.semantics {
                heading()
            }
        )
        UnitsCard(state.unitPreference, state.displayUnits, onUnits)
        ThemeCard(theme, onTheme)
        listOf(
            Res.string.about_nimbo to servicePageUrl(language),
            Res.string.help_and_feedback to servicePageUrl(language, "support"),
            Res.string.privacy_policy to servicePageUrl(language, "privacy"),
            Res.string.rate_nimbo to reviewUrl
        ).forEach { (label, url) ->
            GlassButton(onClick = {
                if (label == Res.string.rate_nimbo) uri.openUri(url) else openPage(url)
            }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(label)) }
        }
        GlassButton(onClick = onLicenses, modifier = Modifier.fillMaxWidth()) {
            Text(stringResource(Res.string.open_source_licenses))
        }
    }
}
