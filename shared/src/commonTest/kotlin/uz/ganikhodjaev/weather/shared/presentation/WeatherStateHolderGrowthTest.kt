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
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
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
import uz.ganikhodjaev.weather.shared.data.SavedLocationLimitReachedException
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.location.DeviceCoordinates
import uz.ganikhodjaev.weather.shared.location.DeviceLocationProvider
import uz.ganikhodjaev.weather.shared.location.DeviceLocationResult
import uz.ganikhodjaev.weather.shared.location.DevicePlace
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
    fun quickCityCompletesOnboardingAndShowsUnacknowledgedTipWithoutDeviceLocation() = runBlocking {
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
                    hasAcknowledgedFirstForecastTip = false
                ),
                onboardingStore.current
            )
            assertEquals(listOf(onboardingStore.current), onboardingStore.writes)
            assertEquals(0, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun unacknowledgedFirstForecastTipRestoresFromFreshCacheOnColdStart() = runBlocking {
        val fetchedAt = 1_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val locationProvider = RecordingLocationProvider()
        val onboardingStore = RecordingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = locationProvider,
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            holder.start()
            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            yield()

            assertEquals(fetchedAt, content.weather.fetchedAtEpochSeconds)
            assertFalse(onboardingStore.current.hasAcknowledgedFirstForecastTip)
            assertTrue(onboardingStore.writes.isEmpty())
            assertEquals(0, repository.refreshCallCount)
            assertEquals(0, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun cachedForecastCompletesInterruptedFirstForecastWithoutAnotherProviderCall() = runBlocking {
        val fetchedAt = 1_500L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val locationProvider = RecordingLocationProvider()
        val onboardingStore = RecordingOnboardingStore()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = locationProvider,
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            holder.start()
            val content = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            yield()

            assertEquals(fetchedAt, content.weather.fetchedAtEpochSeconds)
            assertEquals(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasAcknowledgedFirstForecastTip = false
                ),
                onboardingStore.current
            )
            assertEquals(listOf(onboardingStore.current), onboardingStore.writes)
            assertEquals(0, repository.refreshCallCount)
            assertEquals(0, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun cachedForecastDoesNotCompleteOnboardingWhenContentCannotBeConstructed() = runBlocking {
        val fetchedAt = 1_750L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        repository.failSavedLocationsWith(IllegalStateException("database unavailable"))
        val onboardingStore = RecordingOnboardingStore()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            holder.start()
            val failure = holder.state.filterIsInstance<WeatherUiState.EmptyError>().first()

            assertEquals(UiMessage.WeatherUnavailable, failure.message)
            assertEquals(OnboardingState(), onboardingStore.current)
            assertTrue(onboardingStore.writes.isEmpty())
            assertEquals(0, repository.refreshCallCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun dismissedFirstForecastTipStaysHiddenAfterStateHolderRecreation() = runBlocking {
        val fetchedAt = 2_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val locationProvider = RecordingLocationProvider()
        val onboardingStore = RecordingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val firstScope = CoroutineScope(coroutineContext + SupervisorJob())
        val firstHolder = createStateHolder(
            repository = repository,
            locationProvider = locationProvider,
            onboardingStateStore = onboardingStore,
            scope = firstScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            firstHolder.start()
            firstHolder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            firstHolder.dismissFirstForecastTip()

            val dismissed = assertIs<WeatherUiState.Content>(firstHolder.state.value)
            assertFalse(dismissed.showFirstForecastTip)
            assertTrue(onboardingStore.current.hasAcknowledgedFirstForecastTip)
        } finally {
            firstScope.cancel()
        }

        val secondScope = CoroutineScope(coroutineContext + SupervisorJob())
        val secondHolder = createStateHolder(
            repository = repository,
            locationProvider = locationProvider,
            onboardingStateStore = onboardingStore,
            scope = secondScope,
            currentEpochSeconds = { fetchedAt }
        )
        try {
            secondHolder.start()
            val restored = secondHolder.state.filterIsInstance<WeatherUiState.Content>().first()
            yield()

            assertFalse(restored.showFirstForecastTip)
            assertEquals(0, repository.refreshCallCount)
            assertEquals(0, locationProvider.requestCount)
        } finally {
            secondScope.cancel()
        }
    }

    @Test
    fun failedAcknowledgementWriteHidesTipOnlyForCurrentSession() = runBlocking {
        val fetchedAt = 2_500L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val onboardingStore = ThrowingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val firstScope = CoroutineScope(coroutineContext + SupervisorJob())
        val firstHolder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = onboardingStore,
            scope = firstScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            firstHolder.start()
            firstHolder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            firstHolder.dismissFirstForecastTip()
            assertFalse(
                assertIs<WeatherUiState.Content>(firstHolder.state.value).showFirstForecastTip
            )
            assertEquals(1, onboardingStore.writeCount)
        } finally {
            firstScope.cancel()
        }

        val secondScope = CoroutineScope(coroutineContext + SupervisorJob())
        try {
            val secondHolder = createStateHolder(
                repository = repository,
                locationProvider = RecordingLocationProvider(),
                onboardingStateStore = onboardingStore,
                scope = secondScope,
                currentEpochSeconds = { fetchedAt }
            )
            secondHolder.start()
            val restored = secondHolder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            assertTrue(restored.showFirstForecastTip)
        } finally {
            secondScope.cancel()
        }
    }

    @Test
    fun failedCompletionWriteRetriesFromCacheWithoutAnotherProviderCall() = runBlocking {
        val fetchedAt = 2_750L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val onboardingStore = ThrowingOnboardingStore()

        repeat(2) {
            val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
            try {
                val holder = createStateHolder(
                    repository = repository,
                    locationProvider = RecordingLocationProvider(),
                    onboardingStateStore = onboardingStore,
                    scope = holderScope,
                    currentEpochSeconds = { fetchedAt }
                )
                holder.start()
                holder.state.filterIsInstance<WeatherUiState.Content>().first {
                    it.showFirstForecastTip
                }
                yield()
            } finally {
                holderScope.cancel()
            }
        }

        assertEquals(2, onboardingStore.writeCount)
        assertEquals(0, repository.refreshCallCount)
    }

    @Test
    fun firstForecastTipAddCityOpensCancellablePickerWithoutProviderOrLocationCalls() =
        runBlocking {
            val fetchedAt = 3_000L
            val repository = ScriptedWeatherDataSource(
                initialActiveLocation = TASHKENT,
                initialSnapshot = snapshot(TASHKENT, fetchedAt)
            )
            val locationProvider = RecordingLocationProvider()
            val onboardingStore = RecordingOnboardingStore(
                OnboardingState(
                    hasCompletedFirstForecast = true,
                    hasAcknowledgedFirstForecastTip = false
                )
            )
            val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
            val holder = createStateHolder(
                repository = repository,
                locationProvider = locationProvider,
                onboardingStateStore = onboardingStore,
                scope = holderScope,
                currentEpochSeconds = { fetchedAt }
            )

            try {
                holder.start()
                holder.state.filterIsInstance<WeatherUiState.Content>().first {
                    it.showFirstForecastTip
                }
                holder.addLocationFromFirstForecastTip()

                val picker = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
                assertTrue(picker.canCancel)
                assertEquals(TASHKENT.id, picker.activeLocationId)
                assertEquals(listOf(TASHKENT), picker.savedLocations)
                assertEquals(UzbekistanQuickLocations.all, picker.quickLocations)
                assertTrue(onboardingStore.current.hasAcknowledgedFirstForecastTip)
                assertEquals(0, repository.refreshCallCount)
                assertEquals(0, repository.searchCallCount)
                assertEquals(0, repository.setActiveLocationCallCount)
                assertEquals(0, locationProvider.requestCount)

                val readsBeforeEmission = repository.savedLocationsReadCount
                repository.emitSnapshot(snapshot(TASHKENT, fetchedAt + 1L))
                withTimeout(5_000L) {
                    while (repository.savedLocationsReadCount == readsBeforeEmission) {
                        yield()
                    }
                }
                assertIs<WeatherUiState.ChooseLocation>(holder.state.value)

                holder.cancelLocationPicker()
                val restored = assertIs<WeatherUiState.Content>(holder.state.value)
                assertFalse(restored.showFirstForecastTip)
                assertEquals(fetchedAt + 1L, restored.weather.fetchedAtEpochSeconds)

                val recreatedScope = CoroutineScope(coroutineContext + SupervisorJob())
                try {
                    val recreated = createStateHolder(
                        repository = repository,
                        locationProvider = locationProvider,
                        onboardingStateStore = onboardingStore,
                        scope = recreatedScope,
                        currentEpochSeconds = { fetchedAt + 1L }
                    )
                    recreated.start()
                    val recreatedContent = recreated.state
                        .filterIsInstance<WeatherUiState.Content>()
                        .first()
                    yield()
                    assertFalse(recreatedContent.showFirstForecastTip)
                    assertEquals(0, repository.refreshCallCount)
                    assertEquals(0, locationProvider.requestCount)
                } finally {
                    recreatedScope.cancel()
                }
            } finally {
                holderScope.cancel()
            }
        }

    @Test
    fun firstForecastTipPickerStaysOpenWhenInFlightRefreshSucceeds() = runBlocking {
        val fetchedAt = 3_200L
        val refreshedAt = fetchedAt +
            uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val onboardingStore = RecordingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { refreshedAt }
        )

        try {
            holder.start()
            val refresh = withTimeout(5_000L) { repository.nextRefresh() }
            withTimeout(5_000L) {
                holder.state.filterIsInstance<WeatherUiState.Content>().first {
                    it.showFirstForecastTip
                }
            }

            holder.addLocationFromFirstForecastTip()
            assertIs<WeatherUiState.ChooseLocation>(holder.state.value)

            val savedLocationReadsBeforeSuccess = repository.savedLocationsReadCount
            refresh.succeed(forecastId = refreshedAt)
            withTimeout(5_000L) {
                while (
                    repository.savedLocationsReadCount == savedLocationReadsBeforeSuccess ||
                    repository.refreshHistoryCallCount == 0
                ) {
                    yield()
                }
            }

            assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            holder.cancelLocationPicker()
            val restored = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(refreshedAt, restored.weather.fetchedAtEpochSeconds)
            assertFalse(restored.isRefreshing)
            assertNull(restored.refreshMessage)
            assertFalse(restored.showFirstForecastTip)
            assertEquals(refreshedAt, restored.reviewEligibleForecastId)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun firstForecastTipPickerStaysOpenWhenInFlightRefreshFails() = runBlocking {
        val fetchedAt = 3_300L
        val nowEpochSeconds = fetchedAt +
            uz.ganikhodjaev.weather.shared.AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val onboardingStore = RecordingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { nowEpochSeconds }
        )

        try {
            holder.start()
            val refresh = withTimeout(5_000L) { repository.nextRefresh() }
            withTimeout(5_000L) {
                holder.state.filterIsInstance<WeatherUiState.Content>().first {
                    it.showFirstForecastTip
                }
            }

            holder.addLocationFromFirstForecastTip()
            assertIs<WeatherUiState.ChooseLocation>(holder.state.value)

            refresh.fail(IllegalStateException("offline"))
            yield()

            assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            holder.cancelLocationPicker()
            val restored = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(fetchedAt, restored.weather.fetchedAtEpochSeconds)
            assertFalse(restored.isRefreshing)
            assertEquals(UiMessage.RefreshFailedShowingSaved, restored.refreshMessage)
            assertFalse(restored.showFirstForecastTip)
            assertNull(restored.reviewEligibleForecastId)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun firstForecastTipRemainsUnacknowledgedWhenSavedLocationsCannotBeRead() = runBlocking {
        val fetchedAt = 3_500L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val locationProvider = RecordingLocationProvider()
        val onboardingStore = RecordingOnboardingStore(
            OnboardingState(
                hasCompletedFirstForecast = true,
                hasAcknowledgedFirstForecastTip = false
            )
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = locationProvider,
            onboardingStateStore = onboardingStore,
            scope = holderScope,
            currentEpochSeconds = { fetchedAt }
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.showFirstForecastTip
            }
            repository.failSavedLocationsWith(IllegalStateException("database unavailable"))

            holder.addLocationFromFirstForecastTip()

            val unchanged = assertIs<WeatherUiState.Content>(holder.state.value)
            assertTrue(unchanged.showFirstForecastTip)
            assertFalse(onboardingStore.current.hasAcknowledgedFirstForecastTip)
            assertTrue(onboardingStore.writes.isEmpty())
            assertEquals(0, repository.refreshCallCount)
            assertEquals(0, repository.searchCallCount)
            assertEquals(0, locationProvider.requestCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun failedFirstForecastDoesNotCompleteOnboardingOrShowTip() = runBlocking {
        val repository = ScriptedWeatherDataSource()
        val onboardingStore = RecordingOnboardingStore()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            onboardingStore,
            holderScope
        )

        try {
            holder.start()
            holder.chooseLocation(TASHKENT)
            repository.nextRefresh().fail(IllegalStateException("offline"))
            val failure = holder.state.filterIsInstance<WeatherUiState.EmptyError>().first()

            assertEquals(UiMessage.WeatherUnavailable, failure.message)
            assertEquals(OnboardingState(), onboardingStore.current)
            assertTrue(onboardingStore.writes.isEmpty())
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun startupStorageReadFailureShowsRetryableErrorInsteadOfCrashing() = runBlocking {
        val fetchedAt = Clock.System.now().epochSeconds
        val delegate = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt)
        )
        val repository = FailingFirstStartupReadDataSource(delegate)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            assertEquals(
                WeatherUiState.EmptyError(UiMessage.WeatherUnavailable),
                holder.state.value
            )

            holder.refresh()
            val recovered = holder.state.filterIsInstance<WeatherUiState.Content>().first()
            assertEquals(TASHKENT.id, recovered.weather.location.id)
            assertEquals(2, repository.activeLocationReadCount)
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
    fun failedDevicePlacePersistenceKeepsCoarseLocationWithoutEscaping() = runBlocking {
        val persistenceFailure = IllegalStateException("database unavailable")
        val repository = ScriptedWeatherDataSource(
            updateLocationDetailsFailure = persistenceFailure
        )
        val coordinates = DeviceCoordinates(
            latitude = 41.3111,
            longitude = 69.2797,
            timezone = "Asia/Tashkent"
        )
        val uncaughtFailure = CompletableDeferred<Throwable>()
        val holderScope = CoroutineScope(
            coroutineContext +
                SupervisorJob() +
                CoroutineExceptionHandler { _, error -> uncaughtFailure.complete(error) }
        )
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(
                result = DeviceLocationResult.Success(coordinates),
                place = DevicePlace(name = "Toshkent", country = "Oʻzbekiston")
            ),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope
        )

        try {
            holder.start()
            holder.useDeviceLocation()
            withTimeout(5_000L) { repository.updateLocationDetailsAttempted.await() }
            yield()

            assertFalse(uncaughtFailure.isCompleted)
            val active = requireNotNull(repository.activeLocation())
            assertEquals("", active.name)
            assertEquals("", active.country)
            assertEquals(41.31, active.latitude)
            assertEquals(69.28, active.longitude)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun savedLocationLimitKeepsPickerUsableInsteadOfCrashing() = runBlocking {
        val repository = ScriptedWeatherDataSource(
            setActiveLocationFailure = SavedLocationLimitReachedException()
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            holder.chooseLocation(BUKHARA)

            val picker = holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
                it.message == UiMessage.SavedLocationLimitReached
            }
            assertTrue(picker.isOnboarding)
            assertNull(repository.activeLocation())
            assertEquals(0, repository.refreshCallCount)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun savedLocationLimitStillAllowsReturningToThePreviousForecast() = runBlocking {
        val fetchedAt = Clock.System.now().epochSeconds
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt),
            setActiveLocationFailure = SavedLocationLimitReachedException()
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            holder.showLocationPicker()
            holder.chooseLocation(BUKHARA)

            val picker = holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
                it.message == UiMessage.SavedLocationLimitReached
            }
            assertTrue(picker.canCancel)

            holder.cancelLocationPicker()
            val restored = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(TASHKENT.id, restored.weather.location.id)
            assertEquals(fetchedAt, restored.weather.fetchedAtEpochSeconds)
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
                    hasAcknowledgedFirstForecastTip = true
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
                    hasAcknowledgedFirstForecastTip = true
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
                    hasAcknowledgedFirstForecastTip = true
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
    fun longLivedObservationFailureKeepsCachedContentInsteadOfCrashing() = runBlocking {
        val fetchedAt = Clock.System.now().epochSeconds
        val delegate = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = fetchedAt)
        )
        val repository = FailingLongLivedObservationDataSource(delegate)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository,
            RecordingLocationProvider(),
            RecordingOnboardingStore(),
            holderScope
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            repository.fail(IllegalStateException("database observation failed"))

            val recovered = holder.state.filterIsInstance<WeatherUiState.Content>().first {
                it.refreshMessage == UiMessage.RefreshFailedShowingSaved
            }
            assertFalse(recovered.isRefreshing)
            assertNull(recovered.reviewEligibleForecastId)

            val reattached = withTimeout(5_000) {
                holder.state.filterIsInstance<WeatherUiState.Content>().first {
                    it.weather.fetchedAtEpochSeconds == fetchedAt + 1
                }
            }
            assertEquals(UiMessage.RefreshFailedShowingSaved, reattached.refreshMessage)
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
                    hasAcknowledgedFirstForecastTip = true
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

    @Test
    fun failedSavedLocationDeletionPreservesPickerStateAndShowsMessage() = runBlocking {
        val nowEpochSeconds = 70_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = nowEpochSeconds),
            initialSavedLocations = listOf(TASHKENT, BUKHARA),
            deleteLocationFailure = IllegalStateException("database unavailable")
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { nowEpochSeconds }
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            holder.showLocationPicker()
            holder.deleteSavedLocation(BUKHARA)

            val picker = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            assertEquals(listOf(TASHKENT, BUKHARA), picker.savedLocations)
            assertEquals(UiMessage.ChangesCouldNotBeSaved, picker.message)
            assertEquals(listOf(TASHKENT, BUKHARA), repository.savedLocations())
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun deletedLocationUsesFilteredPickerWhenRereadFailsAndClearsCooldown() = runBlocking {
        val nowEpochSeconds = 75_000L
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
            repository.failSavedLocationsWith(IllegalStateException("database read unavailable"))
            holder.deleteSavedLocation(BUKHARA)

            val picker = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
            assertEquals(listOf(TASHKENT), picker.savedLocations)
            assertNull(picker.message)
            withTimeout(5_000L) {
                while (
                    attemptStore.read(BUKHARA.id) != null ||
                    AutomaticRefreshCoordinator.retainsLocationForTests(BUKHARA.id)
                ) {
                    yield()
                }
            }
            repository.clearSavedLocationsFailure()
            assertEquals(listOf(TASHKENT), repository.savedLocations())
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun failedUnitPreferenceWritePreservesUnitsAndShowsMessage() = runBlocking {
        val nowEpochSeconds = 80_000L
        val repository = ScriptedWeatherDataSource(
            initialActiveLocation = TASHKENT,
            initialSnapshot = snapshot(TASHKENT, fetchedAt = nowEpochSeconds),
            setUnitPreferenceFailure = IllegalStateException("database unavailable")
        )
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(
            repository = repository,
            locationProvider = RecordingLocationProvider(),
            onboardingStateStore = RecordingOnboardingStore(),
            scope = holderScope,
            currentEpochSeconds = { nowEpochSeconds }
        )

        try {
            holder.start()
            holder.state.filterIsInstance<WeatherUiState.Content>().first()
            holder.setUnitPreference(UnitPreference.Imperial)

            val content = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(UnitPreference.Automatic, content.unitPreference)
            assertEquals(UnitSystem.Metric, content.displayUnits.system)
            assertEquals(UiMessage.ChangesCouldNotBeSaved, content.refreshMessage)
            assertEquals(UnitPreference.Automatic, repository.unitPreference())
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
        private val result: DeviceLocationResult = DeviceLocationResult.PermissionDenied,
        private val place: DevicePlace? = null
    ) : DeviceLocationProvider {
        var requestCount = 0
            private set

        override suspend fun requestCurrentLocation(): DeviceLocationResult {
            requestCount += 1
            return result
        }

        override suspend fun resolvePlace(coordinates: DeviceCoordinates): DevicePlace? = place
    }

    private class RecordingOnboardingStore(initialState: OnboardingState = OnboardingState()) :
        OnboardingStateStore {
        var current = initialState
            private set
        val writes = mutableListOf<OnboardingState>()

        override fun read(): OnboardingState = current

        override fun write(state: OnboardingState) {
            current = state
            writes += state
        }
    }

    private class ThrowingOnboardingStore(
        private val initialState: OnboardingState = OnboardingState()
    ) : OnboardingStateStore {
        var writeCount = 0
            private set

        override fun read(): OnboardingState = initialState

        override fun write(state: OnboardingState) {
            writeCount += 1
            throw IllegalStateException("preferences unavailable")
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

    private class FailingFirstStartupReadDataSource(private val delegate: WeatherDataSource) :
        WeatherDataSource by delegate {
        var activeLocationReadCount = 0
            private set

        override fun activeLocation(): Location? {
            activeLocationReadCount += 1
            if (activeLocationReadCount == 1) {
                throw IllegalStateException("database startup read failed")
            }
            return delegate.activeLocation()
        }
    }

    private class FailingLongLivedObservationDataSource(private val delegate: WeatherDataSource) :
        WeatherDataSource by delegate {
        private val failure = CompletableDeferred<Throwable>()
        private var failedOnce = false

        fun fail(error: Throwable) {
            failure.complete(error)
        }

        override fun observe(location: Location): Flow<WeatherSnapshot?> = flow {
            val cached = delegate.observe(location).first()
            if (failedOnce) {
                emit(cached?.copy(fetchedAtEpochSeconds = cached.fetchedAtEpochSeconds + 1))
                awaitCancellation()
            }
            emit(cached)
            val error = failure.await()
            failedOnce = true
            throw error
        }
    }

    private class ScriptedWeatherDataSource(
        initialActiveLocation: Location? = null,
        initialSnapshot: WeatherSnapshot? = null,
        initialSavedLocations: List<Location> = listOfNotNull(initialActiveLocation),
        private val setActiveLocationFailure: Throwable? = null,
        private val updateLocationDetailsFailure: Throwable? = null,
        private val deleteLocationFailure: Throwable? = null,
        private val setUnitPreferenceFailure: Throwable? = null
    ) : WeatherDataSource {
        private val weather = mutableMapOf<String, MutableStateFlow<WeatherSnapshot?>>()
        private val saved = initialSavedLocations.toMutableList()
        private val refreshRequests = Channel<RefreshRequest>(Channel.UNLIMITED)
        private val searchRequests = Channel<SearchRequest>(Channel.UNLIMITED)
        private var active = initialActiveLocation
        private var preference = UnitPreference.Automatic
        private var observeFailure: Throwable? = null
        private var savedLocationsFailure: Throwable? = null
        val observeFailureReached = CompletableDeferred<Unit>()
        val updateLocationDetailsAttempted = CompletableDeferred<Unit>()
        var refreshCallCount = 0
            private set
        var searchCallCount = 0
            private set
        var setActiveLocationCallCount = 0
            private set
        var savedLocationsReadCount = 0
            private set
        var refreshHistoryCallCount = 0
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

        fun failSavedLocationsWith(error: Throwable) {
            savedLocationsFailure = error
        }

        fun clearSavedLocationsFailure() {
            savedLocationsFailure = null
        }

        fun emitSnapshot(snapshot: WeatherSnapshot) {
            weather.getOrPut(snapshot.location.id) { MutableStateFlow(null) }.value = snapshot
        }

        override fun activeLocation(): Location? = active

        override fun savedLocations(): List<Location> {
            savedLocationsReadCount += 1
            savedLocationsFailure?.let { throw it }
            return saved.toList()
        }

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

        override suspend fun refreshHistory(location: Location) {
            refreshHistoryCallCount += 1
        }

        override suspend fun searchCities(query: String, language: String): List<Location> {
            searchCallCount += 1
            return withContext(NonCancellable) {
                val request = SearchRequest(query, language)
                searchRequests.send(request)
                when (val result = request.result.await()) {
                    is SearchResult.Failure -> throw result.error
                    is SearchResult.Success -> result.locations
                }
            }
        }

        override suspend fun setActiveLocation(location: Location) {
            setActiveLocationCallCount += 1
            setActiveLocationFailure?.let { throw it }
            active = location
            saved.removeAll { it.id == location.id }
            saved += location
            weather.getOrPut(location.id) { MutableStateFlow(null) }
        }

        override fun deleteLocation(locationId: String) {
            deleteLocationFailure?.let { throw it }
            saved.removeAll { it.id == locationId }
        }

        override fun updateLocationDetails(location: Location) {
            updateLocationDetailsAttempted.complete(Unit)
            updateLocationDetailsFailure?.let { throw it }
            active = location
            val savedIndex = saved.indexOfFirst { it.id == location.id }
            if (savedIndex >= 0) saved[savedIndex] = location
        }

        override fun unitPreference(): UnitPreference = preference

        override fun setUnitPreference(preference: UnitPreference) {
            setUnitPreferenceFailure?.let { throw it }
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
