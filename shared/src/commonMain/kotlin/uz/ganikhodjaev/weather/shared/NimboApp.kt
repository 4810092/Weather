package uz.ganikhodjaev.weather.shared

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.intl.Locale
import androidx.compose.ui.unit.LayoutDirection
import kotlinx.coroutines.delay
import uz.ganikhodjaev.weather.shared.location.rememberDeviceLocationProvider
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.onboarding.createOnboardingStateStore
import uz.ganikhodjaev.weather.shared.presentation.WeatherStateHolder
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState
import uz.ganikhodjaev.weather.shared.review.considerReviewPrompt
import uz.ganikhodjaev.weather.shared.ui.NimboTheme
import uz.ganikhodjaev.weather.shared.ui.WeatherScreen
import uz.ganikhodjaev.weather.shared.ui.createThemePreferenceStore
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

@Composable
fun NimboApp(platformContext: PlatformContext) {
    val container = remember { NimboContainer(platformContext) }
    val themePreferenceStore = remember { createThemePreferenceStore(platformContext) }
    val onboardingStateStore = remember { createOnboardingStateStore(platformContext) }
    val storeLinkProvider = remember { createStoreLinkProvider(platformContext) }
    var themePreference by remember {
        mutableStateOf(themePreferenceStore.read())
    }
    val locationProvider = rememberDeviceLocationProvider(platformContext)
    val automaticUnits = remember { automaticUnitSystem() }
    val scope = rememberCoroutineScope()
    val stateHolder = remember(locationProvider) {
        WeatherStateHolder(
            container.weatherRepository,
            locationProvider,
            automaticUnits,
            onboardingStateStore,
            scope,
            automaticRefreshAttemptStore = container.automaticRefreshAttemptStore
        )
    }
    val state by stateHolder.state.collectAsState()
    val isForeground by rememberAppIsForeground(platformContext)
    val searchLanguage = Locale.current.language.lowercase()
    val layoutDirection = if (Locale.current.language in RTL_LANGUAGES) {
        LayoutDirection.Rtl
    } else {
        LayoutDirection.Ltr
    }

    LaunchedEffect(stateHolder) {
        stateHolder.start()
    }

    LaunchedEffect(stateHolder, isForeground) {
        if (!isForeground) return@LaunchedEffect
        stateHolder.refreshIfNeeded()
        while (true) {
            delay(FOREGROUND_REFRESH_CHECK_INTERVAL_MILLIS)
            stateHolder.refreshIfNeeded()
        }
    }

    LaunchedEffect(state) {
        (state as? WeatherUiState.Content)?.let { content ->
            publishWeatherSnapshot(platformContext, content.weather, content.displayUnits)
        }
    }

    val reviewEligibleForecastId = (state as? WeatherUiState.Content)
        ?.reviewEligibleForecastId
    LaunchedEffect(reviewEligibleForecastId, isForeground) {
        if (isForeground && reviewEligibleForecastId != null) {
            considerReviewPrompt(platformContext, reviewEligibleForecastId)
        }
    }

    CompositionLocalProvider(LocalLayoutDirection provides layoutDirection) {
        NimboTheme(
            preference = themePreference,
            platformContext = platformContext
        ) {
            CompositionLocalProvider(
                LocalContentColor provides MaterialTheme.colorScheme.onBackground
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.background)
                ) {
                    WeatherScreen(
                        state = state,
                        onRetry = stateHolder::refresh,
                        onSearchQueryChanged = { query ->
                            stateHolder.updateSearchQuery(query, searchLanguage)
                        },
                        onLocationSelected = stateHolder::chooseLocation,
                        onLocationDeleted = stateHolder::deleteSavedLocation,
                        onUseDeviceLocation = stateHolder::useDeviceLocation,
                        onChangeLocation = stateHolder::showLocationPicker,
                        onCancelLocationChange = stateHolder::cancelLocationPicker,
                        onUnitPreferenceChanged = stateHolder::setUnitPreference,
                        onShareText = { text -> shareText(platformContext, text) },
                        storeUrl = storeLinkProvider.storeUrl,
                        onDismissFirstForecastTip = stateHolder::dismissFirstForecastTip,
                        themePreference = themePreference,
                        onThemePreferenceChanged = { preference: ThemePreference ->
                            themePreferenceStore.write(preference)
                            themePreference = preference
                        }
                    )
                }
            }
        }
    }
}

private val RTL_LANGUAGES = setOf("ar", "fa", "he", "ur")
private const val FOREGROUND_REFRESH_CHECK_INTERVAL_MILLIS = 15 * 60 * 1_000L
