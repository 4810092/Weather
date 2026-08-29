package uz.ganikhodjaev.weather.shared.presentation

import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.time.Clock
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.yield
import uz.ganikhodjaev.weather.shared.AutomaticRefreshAttemptPhase
import uz.ganikhodjaev.weather.shared.AutomaticRefreshAttemptState
import uz.ganikhodjaev.weather.shared.AutomaticRefreshAttemptStore
import uz.ganikhodjaev.weather.shared.AutomaticRefreshClaimResult
import uz.ganikhodjaev.weather.shared.AutomaticRefreshCoordinator
import uz.ganikhodjaev.weather.shared.InMemoryAutomaticRefreshAttemptStore
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.location.DeviceLocationProvider
import uz.ganikhodjaev.weather.shared.location.DeviceLocationResult
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.UnitSystem
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.onboarding.OnboardingState
import uz.ganikhodjaev.weather.shared.onboarding.OnboardingStateStore
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickLocations

class WeatherStateHolderGrowthTest {
    @BeforeTest
    fun resetAutomaticRefreshCoordinator() = runBlocking {
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
    }

    @Test
    fun quickCityCompletesOnboardingWithoutRequestingDeviceLocation() = runBlocking {
        val repository = ScriptedWeatherDataSource()
        val locationProvider = RecordingLocationProvider()
        val onboardingStore = RecordingOnboardingStore()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(repository, locationProvider, onboardingStore, holderScope)

        try {
            holder.start()
            val picker = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            assertTrue(picker.isOnboarding)
            assertEquals(UzbekistanQuickLocations.all, picker.quickLocations)

            val quickLocation = UzbekistanQuickLocations.all.first().localized(
                name = "Toshkent",
                country = "Oʻzbekiston"
            )
            holder.chooseLocation(quickLocation)
            val refresh = repository.nextRefresh()
            assertEquals(quickLocation, repository.activeLocation())
            refresh.succeed(forecastId = 100L)

            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.reviewEligibleForecastId == 100L
            }
            assertEquals(quickLocation.id, content.weather.location.id)
            assertTrue(content.showFirstForecastTip)
            assertEquals(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasShownFirstForecastTip = true
                ),
                onboardingStore.current
            )
            assertEquals(0, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun deniedLocationKeepsManualCitySearchAndSelectionAvailable() = runBlocking {
        val repository = ScriptedWeatherDataSource()
        val locationProvider = RecordingLocationProvider(DeviceLocationResult.PermissionDenied)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            locationProvider,
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            holder.useDeviceLocation()
            val denied = holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
                it.message == UiMessage.LocationPermissionDenied
            }
            assertFalse(denied.isLocating)
            assertTrue(denied.isOnboarding)
            assertEquals(1, locationProvider.requestCount)

            holder.updateSearchQuery("Bukhara", language = "uz")
            val search = repository.nextSearch()
            assertEquals("Bukhara", search.query)
            assertEquals("uz", search.language)
            search.succeed(listOf(BUKHARA))

            val results = holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
                it.results == listOf(BUKHARA) && !it.isSearching
            }
            assertNull(results.message)

            holder.chooseLocation(BUKHARA)
            val refresh = repository.nextRefresh()
            refresh.succeed(forecastId = 200L)
            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.weather.location.id == BUKHARA.id
            }
            assertEquals(BUKHARA.id, content.weather.location.id)
            assertEquals(1, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun staleNonCooperativeSearchCannotReplaceLatestResults() = runBlocking {
        val repository = ScriptedWeatherDataSource()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            holder.updateSearchQuery("Ta", language = "en")
            val staleSearch = repository.nextSearch()

            holder.updateSearchQuery("Bu", language = "en")
            val latestSearch = repository.nextSearch()
            latestSearch.succeed(listOf(BUKHARA))
            holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
                it.query == "Bu" && it.results == listOf(BUKHARA) && !it.isSearching
            }

            staleSearch.succeed(listOf(TASHKENT))
            yield()

            val final = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            assertEquals("Bu", final.query)
            assertEquals(listOf(BUKHARA), final.results)
            assertFalse(final.isSearching)
            assertNull(final.message)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun failedRefreshKeepsCachedContentAndRetryClearsWarning() = runBlocking {
        val cached = snapshot(TASHKENT, fetchedAt = 50L)
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = cached
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasShownFirstForecastTip = true
                )
            ),
            holderScope
        )

        try {
            holder.start()
            val failedRefresh = repository.nextRefresh()
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.weather.fetchedAtEpochSeconds == cached.fetchedAtEpochSeconds
            }
            failedRefresh.fail(IllegalStateException("offline"))

            val savedContent = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.refreshMessage == UiMessage.RefreshFailedShowingSaved
            }
            assertEquals(cached, savedContent.weather)
            assertFalse(savedContent.isRefreshing)

            holder.refresh()
            val retry = repository.nextRefresh()
            val retrying = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.isRefreshing
            }
            assertNull(retrying.refreshMessage)
            assertEquals(cached.fetchedAtEpochSeconds, retrying.weather.fetchedAtEpochSeconds)

            retry.succeed(forecastId = 300L)
            val recovered = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.weather.fetchedAtEpochSeconds == 300L && !it.isRefreshing
            }
            assertNull(recovered.refreshMessage)
            assertEquals(TASHKENT.id, recovered.weather.location.id)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun freshCacheSkipsAutomaticActivationRefresh() = runBlocking {
        val cached = snapshot(TASHKENT, fetchedAt = Clock.System.now().epochSeconds)
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = cached
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasShownFirstForecastTip = true
                )
            ),
            holderScope
        )

        try {
            holder.start()
            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first()
            yield()

            assertEquals(cached.fetchedAtEpochSeconds, content.weather.fetchedAtEpochSeconds)
            assertEquals(0, repository.refreshCallCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun foregroundCacheReadFailureDoesNotCallProvider() = runBlocking {
        var nowEpochSeconds = 40_000L
        val cached = snapshot(TASHKENT, fetchedAt = nowEpochSeconds)
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = cached
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasShownFirstForecastTip = true
                )
            ),
            holderScope,
            currentEpochSeconds = { nowEpochSeconds }
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            yield()
            assertEquals(0, repository.refreshCallCount)

            repository.failObserveWith(IllegalStateException("cache unavailable"))
            nowEpochSeconds += uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
            holder.refreshIfNeeded()
            repository.observeFailureReached.await()
            yield()

            assertEquals(0, repository.refreshCallCount)
            assertTrue(holder.state.value is WeatherUiState.Content)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun automaticRefreshWaitsForHourlyBoundaryWhileManualRefreshRemainsAvailable() = runBlocking {
        val firstForecastId = 3_700L
        val secondForecastId = firstForecastId +
            uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val cached = snapshot(TASHKENT, fetchedAt = 100L)
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = cached
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasShownFirstForecastTip = true
                )
            ),
            holderScope,
            currentEpochSeconds = { firstForecastId }
        )

        try {
            holder.start()
            val activationRefresh = repository.nextRefresh()
            activationRefresh.succeed(forecastId = firstForecastId)
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == firstForecastId
            }
            assertEquals(1, repository.refreshCallCount)

            holder.refreshIfNeeded(
                nowEpochSeconds = firstForecastId +
                    uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS - 1L
            )
            yield()
            assertEquals(1, repository.refreshCallCount)

            holder.refreshIfNeeded(
                nowEpochSeconds = secondForecastId
            )
            val automaticRefresh = repository.nextRefresh()
            assertEquals(2, repository.refreshCallCount)
            automaticRefresh.succeed(forecastId = secondForecastId)
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == secondForecastId
            }

            holder.refresh()
            val manualRefresh = repository.nextRefresh()
            assertEquals(3, repository.refreshCallCount)
            manualRefresh.succeed(forecastId = secondForecastId + 1L)
            val manuallyRefreshed = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == secondForecastId + 1L
            }
            assertEquals(secondForecastId + 1L, manuallyRefreshed.weather.fetchedAtEpochSeconds)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun emptyErrorAutomaticRetryRespectsHourlyAttemptGate() = runBlocking {
        val firstAttemptAt = 10_000L
        val repository = ScriptedWeatherDataSource(initialActiveLocation = TASHKENT)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope,
            currentEpochSeconds = { firstAttemptAt }
        )

        try {
            holder.start()
            repository.nextRefresh().fail(IllegalStateException("offline"))
            holder.state.first { it is WeatherUiState.EmptyError }
            assertEquals(1, repository.refreshCallCount)

            holder.refreshIfNeeded(
                firstAttemptAt +
                    uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS - 1L
            )
            yield()
            assertEquals(1, repository.refreshCallCount)

            val retryAt = firstAttemptAt +
                uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
            holder.refreshIfNeeded(retryAt)
            val retry = repository.nextRefresh()
            assertEquals(2, repository.refreshCallCount)
            retry.succeed(forecastId = retryAt)
            val recovered = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == retryAt
            }
            assertEquals(retryAt, recovered.weather.fetchedAtEpochSeconds)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun providerCooldownForOneLocationDoesNotBlockAnotherLocation() = runBlocking {
        val attemptAt = 20_000L
        val repository = ScriptedWeatherDataSource(initialActiveLocation = TASHKENT)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope,
            currentEpochSeconds = { attemptAt }
        )

        try {
            holder.start()
            repository.nextRefresh().fail(IllegalStateException("offline"))
            holder.state.first { it is WeatherUiState.EmptyError }

            holder.chooseLocation(BUKHARA)
            val bukharaRefresh = repository.nextRefresh()
            assertEquals(BUKHARA.id, bukharaRefresh.location.id)
            assertEquals(2, repository.refreshCallCount)
            bukharaRefresh.succeed(forecastId = attemptAt)
            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.weather.location.id == BUKHARA.id && !it.isRefreshing
            }
            assertEquals(BUKHARA.id, content.weather.location.id)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun failedManualRefreshUpdatesAutoCooldownButDoesNotBlockAnotherManualRetry() = runBlocking {
        var nowEpochSeconds = 30_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = 1L)
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope,
            currentEpochSeconds = { nowEpochSeconds }
        )

        try {
            holder.start()
            repository.nextRefresh().succeed(forecastId = nowEpochSeconds)
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == nowEpochSeconds
            }

            nowEpochSeconds += uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
            holder.refresh()
            repository.nextRefresh().fail(IllegalStateException("offline"))
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.refreshMessage == UiMessage.RefreshFailedShowingSaved
            }
            assertEquals(2, repository.refreshCallCount)

            holder.refreshIfNeeded(nowEpochSeconds + 15L * 60L)
            yield()
            assertEquals(2, repository.refreshCallCount)

            holder.refresh()
            val manualRetry = repository.nextRefresh()
            assertEquals(3, repository.refreshCallCount)
            manualRetry.succeed(forecastId = nowEpochSeconds + 1L)
            val recovered = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == nowEpochSeconds + 1L
            }
            assertEquals(nowEpochSeconds + 1L, recovered.weather.fetchedAtEpochSeconds)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun failedRefreshClearsStaleReviewEligibility() = runBlocking {
        val initialForecastId = 35_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = 1L)
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { initialForecastId }
        )

        try {
            holder.start()
            repository.nextRefresh().succeed(forecastId = initialForecastId)
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.reviewEligibleForecastId == initialForecastId && !it.isRefreshing
            }

            holder.refresh()
            val failedRefresh = repository.nextRefresh()
            val refreshing = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.isRefreshing
            }
            assertNull(refreshing.reviewEligibleForecastId)

            failedRefresh.fail(IllegalStateException("offline"))
            val failed = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.refreshMessage == UiMessage.RefreshFailedShowingSaved
            }
            assertNull(failed.reviewEligibleForecastId)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun persistedAutomaticCooldownDoesNotBlockManualRefreshAfterColdStart() = runBlocking {
        val recentAttemptAt = 40_000L
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        attemptStore.writeDurably(
            TASHKENT.id,
            AutomaticRefreshAttemptState(
                token = 1L,
                attemptedAtEpochSeconds = recentAttemptAt,
                phase = AutomaticRefreshAttemptPhase.Cooldown
            )
        )
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = 1L)
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { recentAttemptAt + 1L },
            automaticRefreshAttemptStore = attemptStore
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            yield()
            assertEquals(0, repository.refreshCallCount)

            holder.refresh()
            val manualRefresh = repository.nextRefresh()
            assertEquals(1, repository.refreshCallCount)
            manualRefresh.succeed(forecastId = recentAttemptAt + 2L)
            val refreshed = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == recentAttemptAt + 2L
            }
            assertEquals(recentAttemptAt + 2L, refreshed.weather.fetchedAtEpochSeconds)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun automaticStoreFailureDoesNotBlockManualRefresh() = runBlocking {
        val nowEpochSeconds = 50_000L
        val attemptStore = ThrowingAutomaticRefreshAttemptStore()
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = 1L)
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { nowEpochSeconds },
            automaticRefreshAttemptStore = attemptStore
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            yield()
            assertEquals(0, repository.refreshCallCount)

            holder.refresh()
            val manualRefresh = repository.nextRefresh()
            assertEquals(1, repository.refreshCallCount)
            manualRefresh.succeed(forecastId = nowEpochSeconds)
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                !it.isRefreshing && it.weather.fetchedAtEpochSeconds == nowEpochSeconds
            }
            assertTrue(attemptStore.writeCount >= 1)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun deletingSavedLocationRemovesItsAutomaticRefreshCooldown() = runBlocking {
        val nowEpochSeconds = 60_000L
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        AutomaticRefreshCoordinator.recordManualAttempt(
            locationId = BUKHARA.id,
            nowEpochSeconds = nowEpochSeconds,
            attemptStore = attemptStore
        )
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = nowEpochSeconds),
            initialSavedLocations = listOf(TASHKENT, BUKHARA)
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { nowEpochSeconds },
            automaticRefreshAttemptStore = attemptStore
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            holder.showLocationPicker()
            holder.deleteSavedLocation(BUKHARA)

            withTimeout(5_000L) {
                while (
                    attemptStore.read(BUKHARA.id) != null ||
                    AutomaticRefreshCoordinator.retainsLocationForTests(BUKHARA.id)
                ) {
                    yield()
                }
            }
            assertFalse(BUKHARA in repository.savedLocations())
            assertIs<AutomaticRefreshClaimResult.Granted>(
                AutomaticRefreshCoordinator.claimAutomaticAttempt(
                    locationId = BUKHARA.id,
                    nowEpochSeconds = nowEpochSeconds + 1L,
                    attemptStore = attemptStore
                )
            )
            Unit
        } finally {
            holderScope.cancel()
        }
    }

    private fun createStateHolder(
        repository: WeatherDataSource,
        locationProvider: DeviceLocationProvider,
        onboardingStateStore: OnboardingStateStore,
        scope: CoroutineScope,
        currentEpochSeconds: () -> Long = { Clock.System.now().epochSeconds },
        automaticRefreshAttemptStore: AutomaticRefreshAttemptStore =
            InMemoryAutomaticRefreshAttemptStore()
    ) = WeatherStateHolder(
        repository = repository,
        locationProvider = locationProvider,
        automaticUnitSystem = UnitSystem.Metric,
        onboardingStateStore = onboardingStateStore,
        scope = scope,
        automaticRefreshAttemptStore = automaticRefreshAttemptStore,
        currentEpochSeconds = currentEpochSeconds
    )

    private class RecordingLocationProvider(
        private val result: DeviceLocationResult = DeviceLocationResult.PermissionDenied
    ) : DeviceLocationProvider {
        var requestCount = 0
            private set

        override suspend fun requestCurrentLocation(): DeviceLocationResult {
            requestCount += 1
            return result
        }
    }

    private class RecordingOnboardingStore(initialState: OnboardingState = OnboardingState()) :
        OnboardingStateStore {
        var current = initialState
            private set

        override fun read(): OnboardingState = current

        override fun write(state: OnboardingState) {
            current = state
        }
    }

    private class ThrowingAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
        var writeCount = 0
            private set

        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean {
            writeCount += 1
            throw IllegalStateException("preferences unavailable")
        }

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
            writeCount += 1
            throw IllegalStateException("preferences unavailable")
        }

        override suspend fun removeDurably(locationId: String): Boolean = false
    }

    private class ScriptedWeatherDataSource(
        initialActiveLocation: Location? = null,
        initialSnapshot: WeatherSnapshot? = null,
        initialSavedLocations: List<Location> = listOfNotNull(initialActiveLocation)
    ) : WeatherDataSource {
        private val weather = mutableMapOf<String, MutableStateFlow<WeatherSnapshot?>>()
        private val saved = initialSavedLocations.toMutableList()
        private val refreshRequests = Channel<RefreshRequest>(Channel.UNLIMITED)
        private val searchRequests = Channel<SearchRequest>(Channel.UNLIMITED)
        private var active = initialActiveLocation
        private var preference = UnitPreference.Automatic
        private var observeFailure: Throwable? = null
        val observeFailureReached = CompletableDeferred<Unit>()
        var refreshCallCount = 0
            private set

        init {
            if (initialActiveLocation != null) {
                weather[initialActiveLocation.id] = MutableStateFlow(initialSnapshot)
            }
        }

        suspend fun nextRefresh(): RefreshRequest = refreshRequests.receive()

        suspend fun nextSearch(): SearchRequest = searchRequests.receive()

        fun failObserveWith(error: Throwable) {
            observeFailure = error
        }

        override fun activeLocation(): Location? = active

        override fun savedLocations(): List<Location> = saved.toList()

        override fun observe(location: Location): Flow<WeatherSnapshot?> {
            observeFailure?.let { error ->
                observeFailureReached.complete(Unit)
                throw error
            }
            return weather.getOrPut(location.id) { MutableStateFlow(null) }
        }

        override suspend fun refreshPrimary(location: Location): Long {
            refreshCallCount += 1
            val request = RefreshRequest(location)
            refreshRequests.send(request)
            return when (val result = request.result.await()) {
                is RefreshResult.Failure -> throw result.error
                is RefreshResult.Success -> {
                    weather.getOrPut(location.id) { MutableStateFlow(null) }.value =
                        snapshot(location, result.forecastId)
                    result.forecastId
                }
            }
        }

        override suspend fun refreshAirQuality(location: Location) = Unit

        override suspend fun refreshHistory(location: Location) = Unit

        override suspend fun searchCities(query: String, language: String): List<Location> =
            withContext(NonCancellable) {
                val request = SearchRequest(query, language)
                searchRequests.send(request)
                when (val result = request.result.await()) {
                    is SearchResult.Failure -> throw result.error
                    is SearchResult.Success -> result.locations
                }
            }

        override suspend fun setActiveLocation(location: Location) {
            active = location
            saved.removeAll { it.id == location.id }
            saved += location
            weather.getOrPut(location.id) { MutableStateFlow(null) }
        }

        override fun deleteLocation(locationId: String) {
            saved.removeAll { it.id == locationId }
        }

        override fun updateLocationDetails(location: Location) {
            active = location
            val savedIndex = saved.indexOfFirst { it.id == location.id }
            if (savedIndex >= 0) saved[savedIndex] = location
        }

        override fun unitPreference(): UnitPreference = preference

        override fun setUnitPreference(preference: UnitPreference) {
            this.preference = preference
        }
    }

    private class RefreshRequest(val location: Location) {
        val result = CompletableDeferred<RefreshResult>()

        fun succeed(forecastId: Long) {
            result.complete(RefreshResult.Success(forecastId))
        }

        fun fail(error: Throwable) {
            result.complete(RefreshResult.Failure(error))
        }
    }

    private class SearchRequest(val query: String, val language: String) {
        val result = CompletableDeferred<SearchResult>()

        fun succeed(locations: List<Location>) {
            result.complete(SearchResult.Success(locations))
        }
    }

    private sealed interface RefreshResult {
        data class Success(val forecastId: Long) : RefreshResult
        data class Failure(val error: Throwable) : RefreshResult
    }

    private sealed interface SearchResult {
        data class Success(val locations: List<Location>) : SearchResult
        data class Failure(val error: Throwable) : SearchResult
    }

    private companion object {
        val TASHKENT = Location(
            id = "quick:uz:tashkent",
            name = "Toshkent",
            country = "Oʻzbekiston",
            latitude = 41.2995,
            longitude = 69.2401,
            timezone = "Asia/Tashkent"
        )
        val BUKHARA = Location(
            id = "search:uz:bukhara",
            name = "Bukhara",
            country = "Uzbekistan",
            latitude = 39.7747,
            longitude = 64.4286,
            timezone = "Asia/Tashkent"
        )

        fun snapshot(location: Location, fetchedAt: Long): WeatherSnapshot {
            val hour = WeatherHour(
                epochSeconds = fetchedAt,
                temperatureC = 24.0,
                apparentTemperatureC = 24.0,
                weatherCode = 0,
                precipitationProbability = 0,
                precipitationMm = 0.0,
                windKph = 5.0,
                gustKph = 8.0,
                humidityPercent = 40,
                uvIndex = 1.0,
                fetchedAtEpochSeconds = fetchedAt
            )
            return WeatherSnapshot(
                location = location,
                current = hour,
                timeline = listOf(hour),
                fetchedAtEpochSeconds = fetchedAt,
                isStale = false
            )
        }
    }
}
