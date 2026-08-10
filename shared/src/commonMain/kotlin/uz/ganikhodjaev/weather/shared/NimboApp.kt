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
import uz.ganikhodjaev.weather.shared.location.rememberDeviceLocationProvider
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.presentation.WeatherStateHolder
import uz.ganikhodjaev.weather.shared.ui.NimboTheme
import uz.ganikhodjaev.weather.shared.ui.WeatherScreen
import uz.ganikhodjaev.weather.shared.ui.createThemePreferenceStore
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

@Composable
fun NimboApp(platformContext: PlatformContext) {
    val container = remember { NimboContainer(platformContext) }
    val themePreferenceStore = remember { createThemePreferenceStore(platformContext) }
    var themePreference by remember {
        mutableStateOf(themePreferenceStore.read())
    }
    val locationProvider = rememberDeviceLocationProvider(platformContext)
    val automaticUnits = remember { automaticUnitSystem() }
    val scope = rememberCoroutineScope()
    val stateHolder = remember(locationProvider) {
        WeatherStateHolder(container.weatherRepository, locationProvider, automaticUnits, scope)
    }
    val state by stateHolder.state.collectAsState()
    val layoutDirection = if (Locale.current.language in RTL_LANGUAGES) {
        LayoutDirection.Rtl
    } else {
        LayoutDirection.Ltr
    }

    LaunchedEffect(stateHolder) {
        stateHolder.start()
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
                        onSearchQueryChanged = stateHolder::updateSearchQuery,
                        onLocationSelected = stateHolder::chooseLocation,
                        onUseDeviceLocation = stateHolder::useDeviceLocation,
                        onChangeLocation = stateHolder::showLocationPicker,
                        onCancelLocationChange = stateHolder::cancelLocationPicker,
                        onUnitPreferenceChanged = stateHolder::setUnitPreference,
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
