package uz.ganikhodjaev.weather.shared

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.intl.Locale
import androidx.compose.ui.unit.LayoutDirection
import uz.ganikhodjaev.weather.shared.location.rememberDeviceLocationProvider
import uz.ganikhodjaev.weather.shared.presentation.WeatherStateHolder
import uz.ganikhodjaev.weather.shared.ui.NimboTheme
import uz.ganikhodjaev.weather.shared.ui.WeatherScreen
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

@Composable
fun NimboApp(platformContext: PlatformContext) {
    val container = remember { NimboContainer(platformContext) }
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
        NimboTheme {
            WeatherScreen(
                state = state,
                onRetry = stateHolder::refresh,
                onSearchQueryChanged = stateHolder::updateSearchQuery,
                onLocationSelected = stateHolder::chooseLocation,
                onUseDeviceLocation = stateHolder::useDeviceLocation,
                onChangeLocation = stateHolder::showLocationPicker,
                onCancelLocationChange = stateHolder::cancelLocationPicker,
                onUnitPreferenceChanged = stateHolder::setUnitPreference
            )
        }
    }
}

private val RTL_LANGUAGES = setOf("ar", "fa", "he", "ur")
