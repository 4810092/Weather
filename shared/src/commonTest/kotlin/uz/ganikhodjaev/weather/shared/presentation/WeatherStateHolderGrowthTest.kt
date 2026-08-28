package uz.ganikhodjaev.weather.shared.presentation

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue
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
import kotlinx.coroutines.yield
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

    private fun createStateHolder(
        repository: WeatherDataSource,
        locationProvider: DeviceLocationProvider,
        onboardingStateStore: OnboardingStateStore,
        scope: CoroutineScope
    ) = WeatherStateHolder(
        repository = repository,
        locationProvider = locationProvider,
        automaticUnitSystem = UnitSystem.Metric,
        onboardingStateStore = onboardingStateStore,
        scope = scope
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

    private class ScriptedWeatherDataSource(
        initialActiveLocation: Location? = null,
        initialSnapshot: WeatherSnapshot? = null
    ) : WeatherDataSource {
        private val weather = mutableMapOf<String, MutableStateFlow<WeatherSnapshot?>>()
        private val refreshRequests = Channel<RefreshRequest>(Channel.UNLIMITED)
        private val searchRequests = Channel<SearchRequest>(Channel.UNLIMITED)
        private var active = initialActiveLocation
        private var preference = UnitPreference.Automatic

        init {
            if (initialActiveLocation != null) {
                weather[initialActiveLocation.id] = MutableStateFlow(initialSnapshot)
            }
        }

        suspend fun nextRefresh(): RefreshRequest = refreshRequests.receive()

        suspend fun nextSearch(): SearchRequest = searchRequests.receive()

        override fun activeLocation(): Location? = active

        override fun savedLocations(): List<Location> = listOfNotNull(active)

        override fun observe(location: Location): Flow<WeatherSnapshot?> =
            weather.getOrPut(location.id) { MutableStateFlow(null) }

        override suspend fun refreshPrimary(location: Location): Long {
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
            weather.getOrPut(location.id) { MutableStateFlow(null) }
        }

        override fun deleteLocation(locationId: String) = Unit

        override fun updateLocationDetails(location: Location) {
            active = location
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
