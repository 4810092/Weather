package uz.ganikhodjaev.weather.shared.presentation

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import uz.ganikhodjaev.weather.shared.data.WeatherRepository
import uz.ganikhodjaev.weather.shared.location.DeviceLocationProvider
import uz.ganikhodjaev.weather.shared.location.DeviceLocationResult
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal sealed interface WeatherUiState {
    data object Loading : WeatherUiState

    data class ChooseLocation(
        val query: String = "",
        val results: List<Location> = emptyList(),
        val isSearching: Boolean = false,
        val isLocating: Boolean = false,
        val message: String? = null,
        val canCancel: Boolean = false,
    ) : WeatherUiState

    data class Content(
        val weather: WeatherSnapshot,
        val isRefreshing: Boolean,
        val refreshMessage: String? = null,
    ) : WeatherUiState

    data class EmptyError(val message: String) : WeatherUiState
}

internal class WeatherStateHolder(
    private val repository: WeatherRepository,
    private val locationProvider: DeviceLocationProvider,
    private val scope: CoroutineScope,
) {
    private val mutableState = MutableStateFlow<WeatherUiState>(WeatherUiState.Loading)
    val state: StateFlow<WeatherUiState> = mutableState.asStateFlow()

    private var started = false
    private var observationJob: Job? = null
    private var searchJob: Job? = null
    private var activeLocation: Location? = null
    private var contentBeforeLocationPicker: WeatherUiState.Content? = null

    fun start() {
        if (started) return
        started = true
        val storedLocation = repository.activeLocation()
        if (storedLocation == null) {
            mutableState.value = WeatherUiState.ChooseLocation()
        } else {
            scope.launch { activate(storedLocation, persist = false) }
        }
    }

    fun updateSearchQuery(query: String) {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        searchJob?.cancel()
        val normalized = query.trimStart().take(80)
        mutableState.value = current.copy(
            query = normalized,
            results = if (normalized.length < 2) emptyList() else current.results,
            isSearching = normalized.length >= 2,
            message = null,
        )
        if (normalized.length < 2) return

        searchJob = scope.launch {
            delay(350)
            val before = mutableState.value as? WeatherUiState.ChooseLocation ?: return@launch
            try {
                val results = repository.searchCities(normalized, language = "en")
                val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return@launch
                if (latest.query == normalized) {
                    mutableState.value = latest.copy(
                        results = results,
                        isSearching = false,
                        message = if (results.isEmpty()) "No matching places found." else null,
                    )
                }
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (error: Throwable) {
                logFailure("city search", error)
                val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return@launch
                if (latest.query == before.query) {
                    mutableState.value = latest.copy(
                        isSearching = false,
                        message = "City search is unavailable. Check your connection and try again.",
                    )
                }
            }
        }
    }

    fun chooseLocation(location: Location) {
        searchJob?.cancel()
        scope.launch { activate(location, persist = true) }
    }

    fun showLocationPicker() {
        val current = mutableState.value as? WeatherUiState.Content ?: return
        contentBeforeLocationPicker = current
        mutableState.value = WeatherUiState.ChooseLocation(canCancel = true)
    }

    fun cancelLocationPicker() {
        contentBeforeLocationPicker?.let { mutableState.value = it }
        contentBeforeLocationPicker = null
    }

    fun useDeviceLocation() {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        if (current.isLocating) return
        mutableState.value = current.copy(isLocating = true, message = null)
        scope.launch {
            when (val result = locationProvider.requestCurrentLocation()) {
                is DeviceLocationResult.Success -> {
                    val coordinates = result.coordinates
                    activate(
                        Location(
                            id = "device:${coordinates.latitude}:${coordinates.longitude}",
                            name = "Current location",
                            country = "",
                            latitude = coordinates.latitude,
                            longitude = coordinates.longitude,
                            timezone = coordinates.timezone,
                        ),
                        persist = true,
                    )
                }
                DeviceLocationResult.PermissionDenied -> showLocationMessage(
                    "Location access wasn't granted. Search for a city instead.",
                )
                DeviceLocationResult.ServicesDisabled -> showLocationMessage(
                    "Location services are off. Search for a city or enable them in Settings.",
                )
                is DeviceLocationResult.Failed -> showLocationMessage(
                    result.reason.ifBlank { "Couldn't determine your location. Search for a city instead." },
                )
            }
        }
    }

    fun refresh() {
        activeLocation?.let { location ->
            scope.launch { refreshInternal(location) }
        }
    }

    private suspend fun activate(location: Location, persist: Boolean) {
        if (persist) repository.setActiveLocation(location)
        contentBeforeLocationPicker = null
        activeLocation = location
        observationJob?.cancel()
        mutableState.value = WeatherUiState.Loading
        observationJob = scope.launch {
            repository.observe(location).collect { weather ->
                if (weather != null) {
                    val old = mutableState.value as? WeatherUiState.Content
                    mutableState.value = WeatherUiState.Content(
                        weather = weather,
                        isRefreshing = old?.isRefreshing ?: false,
                        refreshMessage = old?.refreshMessage,
                    )
                }
            }
        }
        refreshInternal(location)
    }

    private fun showLocationMessage(message: String) {
        val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        mutableState.value = latest.copy(isLocating = false, message = message)
    }

    private suspend fun refreshInternal(location: Location) {
        val current = mutableState.value
        if (current is WeatherUiState.Content) {
            mutableState.value = current.copy(isRefreshing = true, refreshMessage = null)
        }
        try {
            repository.refresh(location)
            val updated = mutableState.value
            if (updated is WeatherUiState.Content) {
                mutableState.value = updated.copy(isRefreshing = false, refreshMessage = null)
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            logFailure("weather refresh", error)
            val cached = mutableState.value
            mutableState.value = if (cached is WeatherUiState.Content) {
                cached.copy(
                    isRefreshing = false,
                    refreshMessage = "Couldn't refresh. Showing saved weather.",
                )
            } else {
                WeatherUiState.EmptyError(
                    "Weather is unavailable. Check your connection and try again.",
                )
            }
        }
    }
}

private fun logFailure(operation: String, error: Throwable) {
    println("Nimbo $operation failed: ${error::class.simpleName ?: "unknown error"}")
}
