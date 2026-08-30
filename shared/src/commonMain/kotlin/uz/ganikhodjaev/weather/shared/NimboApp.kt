package uz.ganikhodjaev.weather.shared

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.intl.Locale
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import org.jetbrains.compose.resources.stringResource
import uz.ganikhodjaev.weather.shared.location.rememberDeviceLocationProvider
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.onboarding.createOnboardingStateStore
import uz.ganikhodjaev.weather.shared.presentation.WeatherStateHolder
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState
import uz.ganikhodjaev.weather.shared.resources.Res
import uz.ganikhodjaev.weather.shared.resources.app_start_unavailable
import uz.ganikhodjaev.weather.shared.resources.try_again
import uz.ganikhodjaev.weather.shared.review.considerReviewPrompt
import uz.ganikhodjaev.weather.shared.ui.NimboTheme
import uz.ganikhodjaev.weather.shared.ui.WeatherScreen
import uz.ganikhodjaev.weather.shared.ui.createThemePreferenceStore
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

@Composable
fun NimboApp(platformContext: PlatformContext) {
    var containerAttempt by remember { mutableIntStateOf(0) }
    val containerResult = remember(containerAttempt) {
        runCatching { NimboContainer(platformContext) }.onFailure { error ->
            println(
                "Nimbo storage initialization failed: " +
                    (error::class.simpleName ?: "unknown error")
            )
        }
    }
    val container = containerResult.getOrNull()
    if (container == null) {
        NimboStartupFailure(
            platformContext = platformContext,
            onRetry = { containerAttempt += 1 }
        )
        return
    }
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
    val layoutDirection = layoutDirectionForLanguage(Locale.current.language)

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
                        reviewUrl = storeLinkProvider.reviewUrl,
                        supportUrl = NimboPublicLinks.SUPPORT,
                        onAddLocationFromFirstForecastTip = {
                            stateHolder.addLocationFromFirstForecastTip()
                        },
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

@Composable
private fun NimboStartupFailure(platformContext: PlatformContext, onRetry: () -> Unit) {
    NimboTheme(
        preference = ThemePreference.System,
        platformContext = platformContext
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
        ) {
            Column(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = stringResource(Res.string.app_start_unavailable),
                    color = MaterialTheme.colorScheme.onBackground,
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center
                )
                Button(onClick = onRetry) {
                    Text(stringResource(Res.string.try_again))
                }
            }
        }
    }
}

internal fun layoutDirectionForLanguage(language: String): LayoutDirection =
    if (language.lowercase() in RTL_LANGUAGES) LayoutDirection.Rtl else LayoutDirection.Ltr

private val RTL_LANGUAGES = setOf("ar", "fa", "he", "ur")
private const val FOREGROUND_REFRESH_CHECK_INTERVAL_MILLIS = 15 * 60 * 1_000L
