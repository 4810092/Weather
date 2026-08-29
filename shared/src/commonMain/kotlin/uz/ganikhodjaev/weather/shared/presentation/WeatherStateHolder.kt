package uz.ganikhodjaev.weather.shared.presentation

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withTimeoutOrNull
import uz.ganikhodjaev.weather.shared.AutomaticRefreshAttemptCompletion
import uz.ganikhodjaev.weather.shared.AutomaticRefreshAttemptStore
import uz.ganikhodjaev.weather.shared.AutomaticRefreshClaimResult
import uz.ganikhodjaev.weather.shared.AutomaticRefreshCoordinator
import uz.ganikhodjaev.weather.shared.BackgroundRefreshOutcome
import uz.ganikhodjaev.weather.shared.InMemoryAutomaticRefreshAttemptStore
import uz.ganikhodjaev.weather.shared.classifyBackgroundRefreshFailure
import uz.ganikhodjaev.weather.shared.data.SavedLocationLimitReachedException
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.domain.timelineWithinHours
import uz.ganikhodjaev.weather.shared.isAutomaticRefreshDue
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
import uz.ganikhodjaev.weather.shared.onboarding.OnboardingState
import uz.ganikhodjaev.weather.shared.onboarding.OnboardingStateStore
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickLocation
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickLocations

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
        val canCancel: Boolean = false,
        val isOnboarding: Boolean = false,
        val quickLocations: List<UzbekistanQuickLocation> = emptyList()
    ) : WeatherUiState

    data class Content(
        val weather: WeatherSnapshot,
        val isRefreshing: Boolean,
        val refreshMessage: UiMessage? = null,
        val unitPreference: UnitPreference,
        val displayUnits: DisplayUnits,
        val savedLocations: List<Location> = emptyList(),
        val showFirstForecastTip: Boolean = false,
        val reviewEligibleForecastId: Long? = null
    ) : WeatherUiState

    data class EmptyError(val message: UiMessage) : WeatherUiState
}

internal enum class UiMessage {
    NoMatchingPlaces,
    CitySearchUnavailable,
    LocationPermissionDenied,
    LocationServicesDisabled,
    LocationUnavailable,
    SavedLocationLimitReached,
    ChangesCouldNotBeSaved,
    RefreshFailedShowingSaved,
    WeatherUnavailable
}

internal class WeatherStateHolder(
    private val repository: WeatherDataSource,
    private val locationProvider: DeviceLocationProvider,
    private val automaticUnitSystem: UnitSystem,
    private val onboardingStateStore: OnboardingStateStore,
    private val scope: CoroutineScope,
    private val automaticRefreshAttemptStore: AutomaticRefreshAttemptStore =
        InMemoryAutomaticRefreshAttemptStore(),
    private val currentEpochSeconds: () -> Long = {
        kotlin.time.Clock.System.now().epochSeconds
    }
) {
    private val mutableState = MutableStateFlow<WeatherUiState>(WeatherUiState.Loading)
    val state: StateFlow<WeatherUiState> = mutableState.asStateFlow()

    private var started = false
    private var searchJob: Job? = null
    private var placeResolutionJob: Job? = null
    private var deviceLocationJob: Job? = null
    private var activationJob: Job? = null
    private var refreshJob: Job? = null
    private val activationMutex = Mutex()
    private var activationGeneration = 0L
    private var refreshGate = RefreshGate(activationGeneration)
    private var deviceLocationRequestGeneration = 0L
    private var activeLocation: Location? = null
    private var unitPreference = UnitPreference.Automatic
    private var contentBeforeLocationPicker: WeatherUiState.Content? = null
    private var onboardingState = onboardingStateStore.read()
    private var pendingSuccessfulForecast: PendingSuccessfulForecast? = null

    fun start() {
        if (started) return
        val storedLocation = try {
            unitPreference = repository.unitPreference()
            repository.activeLocation()
        } catch (error: Throwable) {
            logFailure("startup storage read", error)
            mutableState.value = WeatherUiState.EmptyError(UiMessage.WeatherUnavailable)
            return
        }
        started = true
        if (storedLocation == null) {
            mutableState.value = WeatherUiState.ChooseLocation(
                isOnboarding = !onboardingState.hasCompletedFirstForecast,
                quickLocations = UzbekistanQuickLocations.all
            )
        } else {
            launchActivation(storedLocation, persist = false)
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
        cancelDeviceLocationRequest()
        launchActivation(location, persist = true)
    }

    fun deleteSavedLocation(location: Location) {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        if (location.id == activeLocation?.id) return
        try {
            repository.deleteLocation(location.id)
        } catch (error: Throwable) {
            logFailure("saved location deletion", error)
            mutableState.value = current.copy(message = UiMessage.ChangesCouldNotBeSaved)
            return
        }
        val savedLocations = try {
            repository.savedLocations()
        } catch (error: Throwable) {
            // The delete already succeeded. Keep the picker accurate from its
            // current snapshot and still clear per-location refresh bookkeeping.
            logFailure("saved locations read after deletion", error)
            current.savedLocations.filterNot { it.id == location.id }
        }
        mutableState.value = current.copy(savedLocations = savedLocations, message = null)
        scope.launch {
            AutomaticRefreshCoordinator.removeAttemptState(
                locationId = location.id,
                attemptStore = automaticRefreshAttemptStore
            )
        }
    }

    fun showLocationPicker() {
        val current = mutableState.value
        val picker = createLocationPicker(current) ?: return
        contentBeforeLocationPicker = current as? WeatherUiState.Content
        mutableState.value = picker
    }

    fun cancelLocationPicker() {
        cancelDeviceLocationRequest()
        contentBeforeLocationPicker?.let { mutableState.value = it }
        contentBeforeLocationPicker = null
    }

    fun useDeviceLocation() {
        val current = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        if (current.isLocating) return
        deviceLocationJob?.cancel()
        val requestGeneration = ++deviceLocationRequestGeneration
        mutableState.value = current.copy(isLocating = true, message = null)
        deviceLocationJob = scope.launch {
            when (val result = locationProvider.requestCurrentLocation()) {
                is DeviceLocationResult.Success -> {
                    if (!isCurrentDeviceLocationRequest(requestGeneration)) return@launch
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
                    launchActivation(
                        location = location,
                        persist = true,
                        deviceCoordinates = coordinates
                    )
                }
                else -> {
                    if (isCurrentDeviceLocationRequest(requestGeneration)) {
                        showLocationMessage(result.locationFailureMessage())
                    }
                }
            }
        }
    }

    fun refresh() {
        if (!started) {
            start()
            return
        }
        launchRefresh(forceRefresh = true, nowEpochSeconds = null)
    }

    fun refreshIfNeeded(nowEpochSeconds: Long? = null) {
        val freshnessCheckEpochSeconds = nowEpochSeconds ?: currentEpochSeconds()
        when (val current = mutableState.value) {
            is WeatherUiState.Content -> {
                if (!current.weather.isAutomaticRefreshDue(freshnessCheckEpochSeconds)) return
            }
            is WeatherUiState.EmptyError -> activeLocation?.id ?: return
            WeatherUiState.Loading,
            is WeatherUiState.ChooseLocation -> return
        }
        launchRefresh(forceRefresh = false, nowEpochSeconds = nowEpochSeconds)
    }

    private fun launchRefresh(forceRefresh: Boolean, nowEpochSeconds: Long?) {
        if (refreshJob?.isActive == true) return
        if (mutableState.value is WeatherUiState.Loading ||
            mutableState.value is WeatherUiState.ChooseLocation
        ) {
            return
        }
        activeLocation?.let { location ->
            val generation = activationGeneration
            refreshJob = scope.launch {
                refreshInternal(location, generation, forceRefresh, nowEpochSeconds)
            }
        }
    }

    fun setUnitPreference(preference: UnitPreference) {
        val current = mutableState.value as? WeatherUiState.Content
        try {
            repository.setUnitPreference(preference)
        } catch (error: Throwable) {
            logFailure("unit preference write", error)
            if (current != null) {
                mutableState.value = current.copy(
                    refreshMessage = UiMessage.ChangesCouldNotBeSaved
                )
            }
            return
        }
        unitPreference = preference
        if (current == null) return
        mutableState.value = current.copy(
            unitPreference = preference,
            displayUnits = preference.resolve(automaticUnitSystem)
        )
    }

    fun dismissFirstForecastTip() {
        acknowledgeFirstForecastTip()
    }

    fun addLocationFromFirstForecastTip() {
        val current = mutableState.value as? WeatherUiState.Content ?: return
        val picker = createLocationPicker(current) ?: return
        acknowledgeFirstForecastTip()
        contentBeforeLocationPicker = mutableState.value as? WeatherUiState.Content
        mutableState.value = picker
    }

    private fun acknowledgeFirstForecastTip() {
        val current = mutableState.value as? WeatherUiState.Content ?: return
        if (!onboardingState.hasAcknowledgedFirstForecastTip) {
            persistOnboardingState(
                onboardingState.copy(hasAcknowledgedFirstForecastTip = true)
            )
        }
        mutableState.value = current.copy(showFirstForecastTip = false)
    }

    private fun createLocationPicker(current: WeatherUiState): WeatherUiState.ChooseLocation? {
        val savedLocations = try {
            repository.savedLocations()
        } catch (error: Throwable) {
            logFailure("saved locations read", error)
            return null
        }
        return current.toLocationPicker(
            savedLocations = savedLocations,
            activeLocationId = activeLocation?.id
        )
    }

    private fun launchActivation(
        location: Location,
        persist: Boolean,
        deviceCoordinates: DeviceCoordinates? = null
    ) {
        val generation = ++activationGeneration
        refreshGate = RefreshGate(generation)
        activationJob?.cancel()
        refreshJob?.cancel()
        refreshJob = null
        placeResolutionJob?.cancel()
        placeResolutionJob = null
        pendingSuccessfulForecast = null
        activationJob = scope.launch {
            activate(location, persist, generation, deviceCoordinates)
        }
    }

    private suspend fun activate(
        location: Location,
        persist: Boolean,
        generation: Long,
        deviceCoordinates: DeviceCoordinates?
    ) {
        val activated = try {
            activationMutex.withLock {
                if (!isCurrentActivation(generation)) return@withLock false
                if (persist) repository.setActiveLocation(location)
                if (!isCurrentActivation(generation)) return@withLock false

                activeLocation = location
                contentBeforeLocationPicker = null
                mutableState.value = WeatherUiState.Loading
                true
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: SavedLocationLimitReachedException) {
            if (isCurrentActivation(generation)) {
                showLocationMessage(UiMessage.SavedLocationLimitReached)
            }
            false
        } catch (error: Throwable) {
            logFailure("location activation", error)
            if (isCurrentActivation(generation)) {
                showLocationMessage(UiMessage.LocationUnavailable)
            }
            false
        }
        if (!activated || !isCurrentActivation(generation, location)) return

        if (deviceCoordinates != null) {
            placeResolutionJob = scope.launch {
                resolveDevicePlace(location, deviceCoordinates, generation)
            }
        }

        coroutineScope {
            launch {
                var retryDelayMillis = WEATHER_OBSERVATION_INITIAL_RETRY_MILLIS
                while (isCurrentActivation(generation, location)) {
                    var failed = false
                    try {
                        repository.observe(location).collect { weather ->
                            if (weather == null || !isCurrentActivation(generation, location)) {
                                return@collect
                            }
                            val visibleState = mutableState.value
                            val old = (visibleState as? WeatherUiState.Content)
                                ?: contentBeforeLocationPicker
                            val savedLocations = repository.savedLocations()
                            if (!isCurrentActivation(generation, location)) return@collect
                            if (visibleState is WeatherUiState.ChooseLocation && old == null) {
                                return@collect
                            }
                            completeFirstForecastIfNeeded()
                            val content = WeatherUiState.Content(
                                weather = weather,
                                savedLocations = savedLocations,
                                isRefreshing = old?.isRefreshing ?: false,
                                refreshMessage = old?.refreshMessage,
                                unitPreference = unitPreference,
                                displayUnits = unitPreference.resolve(automaticUnitSystem),
                                showFirstForecastTip = old?.showFirstForecastTip
                                    ?: shouldShowFirstForecastTip(),
                                reviewEligibleForecastId = old?.reviewEligibleForecastId
                            )
                            val updatedContent = applyPendingSuccessfulForecast(
                                content = content,
                                generation = generation,
                                location = location
                            )
                            if (!isCurrentActivation(generation, location)) return@collect
                            if (mutableState.value is WeatherUiState.ChooseLocation) {
                                if (contentBeforeLocationPicker != null) {
                                    contentBeforeLocationPicker = updatedContent
                                }
                            } else {
                                mutableState.value = updatedContent
                            }
                        }
                    } catch (cancelled: CancellationException) {
                        throw cancelled
                    } catch (error: Throwable) {
                        failed = true
                        logFailure("weather observation", error)
                        handleObservationFailure(generation, location)
                    }
                    if (isCurrentActivation(generation, location)) {
                        delay(retryDelayMillis)
                        retryDelayMillis = if (failed) {
                            (retryDelayMillis * 2).coerceAtMost(
                                WEATHER_OBSERVATION_MAX_RETRY_MILLIS
                            )
                        } else {
                            WEATHER_OBSERVATION_INITIAL_RETRY_MILLIS
                        }
                    }
                }
            }
            refreshInternal(
                location,
                generation,
                forceRefresh = false,
                nowEpochSeconds = null
            )
            awaitCancellation()
        }
    }

    private fun showLocationMessage(message: UiMessage) {
        val latest = mutableState.value as? WeatherUiState.ChooseLocation ?: return
        mutableState.value = latest.copy(isLocating = false, message = message)
    }

    private fun handleObservationFailure(generation: Long, location: Location) {
        if (!isCurrentActivation(generation, location)) return
        val cached = updateContentPreservingLocationPicker { current ->
            current.copy(
                isRefreshing = false,
                refreshMessage = UiMessage.RefreshFailedShowingSaved,
                reviewEligibleForecastId = null
            )
        }
        if (cached == null && mutableState.value is WeatherUiState.Loading) {
            mutableState.value = WeatherUiState.EmptyError(UiMessage.WeatherUnavailable)
        }
    }

    private suspend fun resolveDevicePlace(
        location: Location,
        coordinates: DeviceCoordinates,
        generation: Long
    ) {
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
        if (!isCurrentActivation(generation, location)) return

        try {
            repository.updateLocationDetails(resolvedLocation)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            // Reverse-geocoding is optional enrichment. Keep the already persisted
            // coarse-coordinate location usable when its label cannot be stored.
            logFailure("device place persistence", error)
            return
        }
        if (!isCurrentActivation(generation, location)) return
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

    private suspend fun refreshInternal(
        location: Location,
        generation: Long,
        forceRefresh: Boolean,
        nowEpochSeconds: Long?
    ) {
        AutomaticRefreshCoordinator.withLocationLock(location.id) {
            refreshInternalSingleFlight(
                location,
                generation,
                forceRefresh = forceRefresh,
                nowEpochSeconds = nowEpochSeconds ?: currentEpochSeconds()
            )
        }
    }

    private suspend fun refreshInternalSingleFlight(
        location: Location,
        generation: Long,
        forceRefresh: Boolean,
        nowEpochSeconds: Long
    ) {
        if (!isCurrentActivation(generation, location)) return
        val gate = refreshGate
        if (gate.generation != generation || !gate.mutex.tryLock()) return
        try {
            val automaticAttemptToken = if (!forceRefresh) {
                val cachedSnapshot = try {
                    repository.observe(location).first()
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (error: Throwable) {
                    logFailure("cached weather freshness check", error)
                    return
                }
                val refreshDue = cachedSnapshot?.isAutomaticRefreshDue(
                    nowEpochSeconds
                ) ?: true
                if (!refreshDue) return
                when (
                    val claim = AutomaticRefreshCoordinator.claimAutomaticAttempt(
                        location.id,
                        nowEpochSeconds,
                        automaticRefreshAttemptStore
                    )
                ) {
                    is AutomaticRefreshClaimResult.Granted -> claim.token
                    AutomaticRefreshClaimResult.Cooldown,
                    AutomaticRefreshClaimResult.RetryDeferred,
                    AutomaticRefreshClaimResult.StoreUnavailable -> return
                }
            } else {
                null
            }
            updateContentPreservingLocationPicker { current ->
                current.copy(
                    weather = current.weather.advancedToNow(),
                    isRefreshing = true,
                    refreshMessage = null,
                    reviewEligibleForecastId = null
                )
            }
            try {
                if (forceRefresh) {
                    AutomaticRefreshCoordinator.recordManualAttempt(
                        location.id,
                        nowEpochSeconds,
                        automaticRefreshAttemptStore
                    )
                }
                val successfulForecastId = try {
                    repository.refreshPrimary(location)
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (error: Throwable) {
                    automaticAttemptToken?.let { token ->
                        AutomaticRefreshCoordinator.finalizeAutomaticAttempt(
                            locationId = location.id,
                            token = token,
                            completion = if (
                                classifyBackgroundRefreshFailure(error) ==
                                BackgroundRefreshOutcome.TransientFailure
                            ) {
                                AutomaticRefreshAttemptCompletion.RetryPending
                            } else {
                                AutomaticRefreshAttemptCompletion.Cooldown
                            },
                            attemptStore = automaticRefreshAttemptStore
                        )
                    }
                    throw error
                }
                automaticAttemptToken?.let { token ->
                    AutomaticRefreshCoordinator.finalizeAutomaticAttempt(
                        locationId = location.id,
                        token = token,
                        completion = AutomaticRefreshAttemptCompletion.Cooldown,
                        attemptStore = automaticRefreshAttemptStore
                    )
                }
                if (!isCurrentActivation(generation, location)) return
                pendingSuccessfulForecast = PendingSuccessfulForecast(
                    generation = generation,
                    locationId = location.id,
                    forecastId = successfulForecastId
                )
                updateContentPreservingLocationPicker { contentAfterRefresh ->
                    applyPendingSuccessfulForecast(
                        content = contentAfterRefresh,
                        generation = generation,
                        location = location
                    ).copy(
                        isRefreshing = false,
                        refreshMessage = null
                    )
                }
                if (!isCurrentActivation(generation, location)) return
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
                if (!isCurrentActivation(generation, location)) return
                val cached = updateContentPreservingLocationPicker { content ->
                    content.copy(
                        isRefreshing = false,
                        refreshMessage = UiMessage.RefreshFailedShowingSaved
                    )
                }
                if (cached == null && mutableState.value !is WeatherUiState.ChooseLocation) {
                    mutableState.value = WeatherUiState.EmptyError(
                        UiMessage.WeatherUnavailable
                    )
                }
            }
        } finally {
            gate.mutex.unlock()
        }
    }

    private fun applyPendingSuccessfulForecast(
        content: WeatherUiState.Content,
        generation: Long,
        location: Location
    ): WeatherUiState.Content {
        val pending = pendingSuccessfulForecast ?: return content
        if (
            pending.generation != generation ||
            pending.locationId != location.id ||
            content.weather.location.id != location.id ||
            !isCurrentActivation(generation, location)
        ) {
            return content
        }
        val successfulForecastId = pending.forecastId
        if (content.weather.fetchedAtEpochSeconds < successfulForecastId) return content

        val shouldShowTip = !onboardingState.hasAcknowledgedFirstForecastTip
        completeFirstForecastIfNeeded()
        pendingSuccessfulForecast = null
        return content.copy(
            showFirstForecastTip = content.showFirstForecastTip || shouldShowTip,
            reviewEligibleForecastId = successfulForecastId
        )
    }

    private fun shouldShowFirstForecastTip(): Boolean = onboardingState.hasCompletedFirstForecast &&
        !onboardingState.hasAcknowledgedFirstForecastTip

    private fun completeFirstForecastIfNeeded() {
        if (!onboardingState.hasCompletedFirstForecast) {
            persistOnboardingState(onboardingState.copy(hasCompletedFirstForecast = true))
        }
    }

    private fun persistOnboardingState(state: OnboardingState) {
        // Keep this session responsive. If durable storage fails, the unchanged store
        // safely retries the completion or acknowledgement on the next launch.
        onboardingState = state
        try {
            onboardingStateStore.write(state)
        } catch (error: Throwable) {
            logFailure("onboarding state write", error)
        }
    }

    private inline fun updateContentPreservingLocationPicker(
        update: (WeatherUiState.Content) -> WeatherUiState.Content
    ): WeatherUiState.Content? {
        val visibleState = mutableState.value
        val content = (visibleState as? WeatherUiState.Content)
            ?: contentBeforeLocationPicker?.takeIf {
                visibleState is WeatherUiState.ChooseLocation
            }
            ?: return null
        val updated = update(content)
        if (visibleState is WeatherUiState.ChooseLocation) {
            contentBeforeLocationPicker = updated
        } else {
            mutableState.value = updated
        }
        return updated
    }

    private fun cancelDeviceLocationRequest() {
        deviceLocationRequestGeneration += 1
        deviceLocationJob?.cancel()
        deviceLocationJob = null
    }

    private fun isCurrentDeviceLocationRequest(generation: Long): Boolean =
        generation == deviceLocationRequestGeneration &&
            mutableState.value is WeatherUiState.ChooseLocation

    private fun isCurrentActivation(generation: Long, location: Location? = null): Boolean =
        generation == activationGeneration &&
            (location == null || activeLocation?.id == location.id)

    private data class PendingSuccessfulForecast(
        val generation: Long,
        val locationId: String,
        val forecastId: Long
    )

    private data class RefreshGate(val generation: Long, val mutex: Mutex = Mutex())
}

internal fun DeviceLocationResult.locationFailureMessage(): UiMessage = when (this) {
    DeviceLocationResult.PermissionDenied -> UiMessage.LocationPermissionDenied
    DeviceLocationResult.ServicesDisabled -> UiMessage.LocationServicesDisabled
    is DeviceLocationResult.Failed -> UiMessage.LocationUnavailable
    is DeviceLocationResult.Success -> error("A successful location has no failure message")
}

internal fun WeatherUiState.toLocationPicker(
    savedLocations: List<Location>,
    activeLocationId: String?
): WeatherUiState.ChooseLocation? = when (this) {
    is WeatherUiState.Content -> WeatherUiState.ChooseLocation(
        savedLocations = savedLocations,
        activeLocationId = weather.location.id,
        canCancel = true,
        quickLocations = UzbekistanQuickLocations.all
    )
    is WeatherUiState.EmptyError -> WeatherUiState.ChooseLocation(
        savedLocations = savedLocations,
        activeLocationId = activeLocationId,
        canCancel = false,
        quickLocations = UzbekistanQuickLocations.all
    )
    WeatherUiState.Loading,
    is WeatherUiState.ChooseLocation -> null
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

private const val WEATHER_OBSERVATION_INITIAL_RETRY_MILLIS = 2_000L
private const val WEATHER_OBSERVATION_MAX_RETRY_MILLIS = 60_000L
