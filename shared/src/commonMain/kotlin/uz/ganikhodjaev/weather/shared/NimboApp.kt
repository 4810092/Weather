package uz.ganikhodjaev.weather.shared

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import uz.ganikhodjaev.weather.shared.location.rememberDeviceLocationProvider
import uz.ganikhodjaev.weather.shared.presentation.WeatherStateHolder
import uz.ganikhodjaev.weather.shared.ui.NimboTheme
import uz.ganikhodjaev.weather.shared.ui.WeatherScreen

@Composable
fun NimboApp(platformContext: PlatformContext) {
    val container = remember { NimboContainer(platformContext) }
    val locationProvider = rememberDeviceLocationProvider(platformContext)
    val scope = rememberCoroutineScope()
    val stateHolder = remember(locationProvider) {
        WeatherStateHolder(container.weatherRepository, locationProvider, scope)
    }
    val state by stateHolder.state.collectAsState()

    LaunchedEffect(stateHolder) {
        stateHolder.start()
    }

    NimboTheme {
        WeatherScreen(
            state = state,
            onRetry = stateHolder::refresh,
            onSearchQueryChanged = stateHolder::updateSearchQuery,
            onLocationSelected = stateHolder::chooseLocation,
            onUseDeviceLocation = stateHolder::useDeviceLocation,
            onChangeLocation = stateHolder::showLocationPicker,
            onCancelLocationChange = stateHolder::cancelLocationPicker,
        )
    }
}
