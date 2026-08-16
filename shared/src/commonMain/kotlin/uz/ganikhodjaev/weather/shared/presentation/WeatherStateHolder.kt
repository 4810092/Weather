package uz.ganikhodjaev.weather.shared.presentation

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import uz.ganikhodjaev.weather.shared.data.WeatherRepository
import uz.ganikhodjaev.weather.shared.domain.timelineWithinHours
import uz.ganikhodjaev.weather.shared.location.DeviceCoordinates
import uz.ganikhodjaev.weather.shared.location.DeviceLocationProvider
import uz.ganikhodjaev.weather.shared.location.DeviceLocationResult
import uz.ganikhodjaev.weather.shared.location.coarsened
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.UnitSystem
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.resolve

internal sealed interface WeatherUiState {
    data object Loading : WeatherUiState

    data class ChooseLocation(
        val query: String = "",
        val results: List<Location> = emptyList(),
        val savedLocations: List<Location> = emptyList(),
        val activeLocationId: String? = null,
        val isSearching: Boolean = false,
        val isLocating: Boolean = false,
        val message: UiMessage? = null,
        val canCancel: Boolean = false
    ) : WeatherUiState

    data class Content(
        val weather: WeatherSnapshot,
        val isRefreshing: Boolean,
        val refreshMessage: UiMessage? = null,
        val unitPreference: UnitPreference,
        val displayUnits: DisplayUnits,
        val savedLocations: List<Location> = emptyList()
    ) : WeatherUiState

    data class EmptyError(val message: UiMessage) : WeatherUiState
}

internal enum class UiMessage {
    NoMatchingPlaces,
    CitySearchUnavailable,
    LocationPermissionDenied,
    LocationServicesDisabled,
    LocationUnavailable,
    RefreshFailedShowingSaved,
    WeatherUnavailable
}

internal class WeatherStateHolder(
    private val repository: WeatherRepository,
    private val locationProvider: DeviceLocationProvider,
    private val automaticUnitSystem: UnitSystem,
    private val scope: CoroutineScope
) {
    private val mutableState = MutableStateFlow<WeatherUiState>(WeatherUiState.Loading)
    val state: StateFlow<WeatherUiState> = mutableState.asStateFlow()

    private var started = false
    private var observationJob: Job? = null
    private var searchJob: Job? = null
    private var placeResolutionJob: Job? = null
    private var refreshJob: Job? = null
    private var activeLocation: Location? = null
    private var unitPreference = UnitPreference.Automatic
    private var contentBeforeLocationPicker: WeatherUiState.Content? = null

    fun start() {
        if (started) return
        started = true
        unitPreference = repository.unitPreference()
        val storedLocation = repository.activeLocation()
        if (storedLocation == null) {
            mutableState.value = WeatherUiState.ChooseLocation()
        } else {
            scope.launch { activate(storedLocation, persist = false) }
        }
    }

    fun updateSearchQuery(query: String, language: String) {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        searchJob?.cancel()
        val normalized = query.trimStart().take(80)
        mutableState.value = current.copy(
            query = normalized,
            results = if (normalized.length < 2) emptyList() else current.results,
            isSearching = normalized.length >= 2,
            message = null
        )
        if (normalized.length < 2) return

        searchJob = scope.launch {
            delay(350)
            val before = mutableState.value as? WeatherUiState.ChooseLocation ?: return@launch
            try {
                val results = repository.searchCities(normalized, language)
                val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return@launch
                if (latest.query == normalized) {
                    mutableState.value = latest.copy(
                        results = results,
                        isSearching = false,
                        message = if (results.isEmpty()) UiMessage.NoMatchingPlaces else null
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
                        message = UiMessage.CitySearchUnavailable
                    )
                }
            }
        }
    }

    fun chooseLocation(location: Location) {
        searchJob?.cancel()
        placeResolutionJob?.cancel()
        scope.launch { activate(location, persist = true) }
    }

    fun deleteSavedLocation(location: Location) {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        if (location.id == activeLocation?.id) return
        repository.deleteLocation(location.id)
        mutableState.value = current.copy(savedLocations = repository.savedLocations())
    }

    fun showLocationPicker() {
        val current = mutableState.value as? WeatherUiState.Content ?: return
        contentBeforeLocationPicker = current
        mutableState.value = WeatherUiState.ChooseLocation(
            savedLocations = repository.savedLocations(),
            activeLocationId = current.weather.location.id,
            canCancel = true
        )
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
                    // Always reduce device coordinates before persistence or network use.
                    // Two decimal places are roughly kilometre-scale and cannot represent
                    // a precise street-level location even when iOS grants Precise Location.
                    val coordinates = result.coordinates.coarsened()
                    val location = Location(
                        id = "device:${coordinates.latitude}:${coordinates.longitude}",
                        name = "",
                        country = "",
                        latitude = coordinates.latitude,
                        longitude = coordinates.longitude,
                        timezone = coordinates.timezone
                    )
                    repository.setActiveLocation(location)
                    activeLocation = location
                    placeResolutionJob?.cancel()
                    placeResolutionJob = scope.launch {
                        resolveDevicePlace(location, coordinates)
                    }
                    activate(location, persist = false)
                }
                DeviceLocationResult.PermissionDenied -> showLocationMessage(
                    UiMessage.LocationPermissionDenied
                )
                DeviceLocationResult.ServicesDisabled -> showLocationMessage(
                    UiMessage.LocationServicesDisabled
                )
                is DeviceLocationResult.Failed -> showLocationMessage(
                    UiMessage.LocationUnavailable
                )
            }
        }
    }

    fun refresh() {
        if (refreshJob?.isActive == true) return
        if (mutableState.value is WeatherUiState.Loading ||
            mutableState.value is WeatherUiState.ChooseLocation
        ) {
            return
        }
        activeLocation?.let { location ->
            refreshJob = scope.launch { refreshInternal(location) }
        }
    }

    fun setUnitPreference(preference: UnitPreference) {
        unitPreference = preference
        repository.setUnitPreference(preference)
        val current = mutableState.value as? WeatherUiState.Content ?: return
        mutableState.value = current.copy(
            unitPreference = preference,
            displayUnits = preference.resolve(automaticUnitSystem)
        )
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
                        savedLocations = repository.savedLocations(),
                        isRefreshing = old?.isRefreshing ?: false,
                        refreshMessage = old?.refreshMessage,
                        unitPreference = unitPreference,
                        displayUnits = unitPreference.resolve(automaticUnitSystem)
                    )
                }
            }
        }
        refreshInternal(location)
    }

    private fun showLocationMessage(message: UiMessage) {
        val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        mutableState.value = latest.copy(isLocating = false, message = message)
    }

    private suspend fun resolveDevicePlace(location: Location, coordinates: DeviceCoordinates) {
        val place = try {
            withTimeoutOrNull(8_000) {
                locationProvider.resolvePlace(coordinates)
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            logFailure("device place lookup", error)
            null
        } ?: return
        val resolvedLocation = location.copy(
            name = place.name.trim(),
            country = place.country.trim()
        )
        if (resolvedLocation.name.isBlank() && resolvedLocation.country.isBlank()) return
        if (activeLocation?.id != location.id) return

        repository.updateLocationDetails(resolvedLocation)
        activeLocation = resolvedLocation
        val current = mutableState.value as? WeatherUiState.Content
        if (current?.weather?.location?.id == location.id) {
            mutableState.value = current.copy(
                weather = current.weather.copy(location = resolvedLocation)
            )
        }
        contentBeforeLocationPicker = contentBeforeLocationPicker?.let { content ->
            if (content.weather.location.id == location.id) {
                content.copy(weather = content.weather.copy(location = resolvedLocation))
            } else {
                content
            }
        }
    }

    private suspend fun refreshInternal(location: Location) {
        val current = mutableState.value
        if (current is WeatherUiState.Content) {
            mutableState.value = current.copy(
                weather = current.weather.advancedToNow(),
                isRefreshing = true,
                refreshMessage = null
            )
        }
        try {
            repository.refreshPrimary(location)
            val updated = mutableState.value
            if (updated is WeatherUiState.Content) {
                mutableState.value = updated.copy(isRefreshing = false, refreshMessage = null)
            }
            scope.launch {
                try {
                    repository.refreshHistory(location)
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (error: Throwable) {
                    logFailure("historical weather refresh", error)
                }
            }
            scope.launch {
                try {
                    repository.refreshAirQuality(location)
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (error: Throwable) {
                    logFailure("air-quality refresh", error)
                }
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            logFailure("weather refresh", error)
            val cached = mutableState.value
            mutableState.value = if (cached is WeatherUiState.Content) {
                cached.copy(
                    isRefreshing = false,
                    refreshMessage = UiMessage.RefreshFailedShowingSaved
                )
            } else {
                WeatherUiState.EmptyError(
                    UiMessage.WeatherUnavailable
                )
            }
        }
    }
}

private fun WeatherSnapshot.advancedToNow(): WeatherSnapshot {
    val hours = (recentHistory + timeline).distinctBy { it.epochSeconds }
    if (hours.isEmpty()) return this
    val now = kotlin.time.Clock.System.now().epochSeconds
    val currentHour = hours.minBy { kotlin.math.abs(it.epochSeconds - now) }
    return copy(
        current = currentHour,
        timeline = timelineWithinHours(hours, currentHour.epochSeconds, hours = 24) {
            it.epochSeconds
        },
        recentHistory = hours.filter { it.epochSeconds < currentHour.epochSeconds }
    )
}

private fun logFailure(operation: String, error: Throwable) {
    println("Nimbo $operation failed: ${error::class.simpleName ?: "unknown error"}")
}
