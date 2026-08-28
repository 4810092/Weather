package uz.ganikhodjaev.weather.shared.presentation

import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.yield
import uz.ganikhodjaev.weather.shared.AutomaticRefreshCoordinator
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

class WeatherStateHolderRaceTest {
    @BeforeTest
    fun resetAutomaticRefreshCoordinator() = runBlocking {
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
    }

    @Test
    fun staleNonCooperativeRefreshCannotReplaceTheLatestForecastOrReviewCandidate() = runBlocking {
        val repository = ControllableWeatherDataSource()
        val onboarding = RecordingOnboardingStore()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(repository, onboarding, holderScope)

        try {
            holder.start()
            holder.chooseLocation(LOCATION_A)
            repository.refreshStarted(LOCATION_A).await()

            holder.chooseLocation(LOCATION_B)
            repository.refreshStarted(LOCATION_B).await()
            repository.completeRefresh(LOCATION_B, RefreshResult.Success(200L))
            val latest = holder.state.filterIsInstance<WeatherUiState.Content>().first { content ->
                content.weather.location.id == LOCATION_B.id &&
                    content.reviewEligibleForecastId == 200L
            }
            assertEquals(LOCATION_B.id, latest.weather.location.id)
            assertEquals(200L, latest.reviewEligibleForecastId)
            assertEquals(1, onboarding.writes.size)

            // Simulate an engine that ignores cancellation and returns A after B won.
            repository.completeRefresh(LOCATION_A, RefreshResult.Success(300L))
            yield()

            val afterStaleSuccess = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(LOCATION_B.id, afterStaleSuccess.weather.location.id)
            assertEquals(200L, afterStaleSuccess.reviewEligibleForecastId)
            assertEquals(1, onboarding.writes.size)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun staleNonCooperativeFailureCannotReplaceTheLatestForecastWithAnError() = runBlocking {
        val repository = ControllableWeatherDataSource()
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(repository, RecordingOnboardingStore(), holderScope)

        try {
            holder.start()
            holder.chooseLocation(LOCATION_A)
            repository.refreshStarted(LOCATION_A).await()

            holder.chooseLocation(LOCATION_B)
            repository.refreshStarted(LOCATION_B).await()
            repository.completeRefresh(LOCATION_B, RefreshResult.Success(200L))
            yield()

            repository.completeRefresh(
                LOCATION_A,
                RefreshResult.Failure(IllegalStateException("late A failure"))
            )
            yield()

            val latest = assertIs<WeatherUiState.Content>(holder.state.value)
            assertEquals(LOCATION_B.id, latest.weather.location.id)
            assertEquals(200L, latest.reviewEligibleForecastId)
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun activeLocationPersistenceIsSerializedSoTheLatestChoiceWins() = runBlocking {
        val repository = ControllableWeatherDataSource(blockedPersistenceLocation = LOCATION_A)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(repository, RecordingOnboardingStore(), holderScope)

        try {
            holder.start()
            holder.chooseLocation(LOCATION_A)
            repository.persistenceStarted.await()

            holder.chooseLocation(LOCATION_B)
            repository.releasePersistence.complete(Unit)
            repository.refreshStarted(LOCATION_B).await()

            assertEquals(LOCATION_B, repository.activeLocation())
            assertEquals(listOf(LOCATION_A.id, LOCATION_B.id), repository.persistedLocationIds)

            repository.completeRefresh(LOCATION_B, RefreshResult.Success(200L))
        } finally {
            holderScope.cancel()
        }
    }

    @Test
    fun cachedContentCannotStartASecondRefreshWhileActivationRefreshIsRunning() = runBlocking {
        val repository = ControllableWeatherDataSource()
        repository.seedSnapshot(LOCATION_A, fetchedAt = 50L)
        val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
        val holder = createStateHolder(repository, RecordingOnboardingStore(), holderScope)

        try {
            holder.start()
            holder.chooseLocation(LOCATION_A)
            repository.refreshStarted(LOCATION_A).await()
            holder.state.filterIsInstance<WeatherUiState.Content>().first { content ->
                content.weather.location.id == LOCATION_A.id
            }

            holder.refresh()
            yield()

            assertEquals(1, repository.refreshCallCount(LOCATION_A))
            repository.completeRefresh(LOCATION_A, RefreshResult.Success(100L))
        } finally {
            holderScope.cancel()
        }
    }

    private fun createStateHolder(
        repository: WeatherDataSource,
        onboarding: OnboardingStateStore,
        scope: CoroutineScope
    ) = WeatherStateHolder(
        repository = repository,
        locationProvider = DeviceLocationProvider { DeviceLocationResult.PermissionDenied },
        automaticUnitSystem = UnitSystem.Metric,
        onboardingStateStore = onboarding,
        scope = scope
    )

    private class RecordingOnboardingStore : OnboardingStateStore {
        private var state = OnboardingState()
        val writes = mutableListOf<OnboardingState>()

        override fun read(): OnboardingState = state

        override fun write(state: OnboardingState) {
            this.state = state
            writes += state
        }
    }

    private class ControllableWeatherDataSource(
        private val blockedPersistenceLocation: Location? = null
    ) : WeatherDataSource {
        private val weather = mutableMapOf<String, MutableStateFlow<WeatherSnapshot?>>()
        private val refreshStarts = mutableMapOf<String, CompletableDeferred<Unit>>()
        private val refreshResults = mutableMapOf<String, CompletableDeferred<RefreshResult>>()
        private val refreshCallCounts = mutableMapOf<String, Int>()
        private var active: Location? = null
        private var preference = UnitPreference.Automatic

        val persistenceStarted = CompletableDeferred<Unit>()
        val releasePersistence = CompletableDeferred<Unit>()
        val persistedLocationIds = mutableListOf<String>()

        fun refreshStarted(location: Location): CompletableDeferred<Unit> =
            refreshStarts.getOrPut(location.id) { CompletableDeferred() }

        fun completeRefresh(location: Location, result: RefreshResult) {
            refreshResults.getOrPut(location.id) { CompletableDeferred() }.complete(result)
        }

        fun seedSnapshot(location: Location, fetchedAt: Long) {
            weather.getOrPut(location.id) { MutableStateFlow(null) }.value =
                snapshot(location, fetchedAt)
        }

        fun refreshCallCount(location: Location): Int = refreshCallCounts[location.id] ?: 0

        override fun activeLocation(): Location? = active

        override fun savedLocations(): List<Location> = listOfNotNull(active)

        override fun observe(location: Location): Flow<WeatherSnapshot?> =
            weather.getOrPut(location.id) { MutableStateFlow(null) }

        override suspend fun refreshPrimary(location: Location): Long =
            withContext(NonCancellable) {
                refreshCallCounts[location.id] = refreshCallCount(location) + 1
                refreshStarts.getOrPut(location.id) { CompletableDeferred() }.complete(Unit)
                when (
                    val result = refreshResults
                        .getOrPut(location.id) { CompletableDeferred() }
                        .await()
                ) {
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

        override suspend fun searchCities(query: String, language: String) = emptyList<Location>()

        override suspend fun setActiveLocation(location: Location) {
            if (location == blockedPersistenceLocation) {
                withContext(NonCancellable) {
                    persistenceStarted.complete(Unit)
                    releasePersistence.await()
                }
            }
            persistedLocationIds += location.id
            active = location
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

    private sealed interface RefreshResult {
        data class Success(val forecastId: Long) : RefreshResult
        data class Failure(val error: Throwable) : RefreshResult
    }

    private companion object {
        val LOCATION_A = Location(
            id = "A",
            name = "A",
            country = "UZ",
            latitude = 41.0,
            longitude = 69.0,
            timezone = "Asia/Tashkent"
        )
        val LOCATION_B = LOCATION_A.copy(id = "B", name = "B")

        fun snapshot(location: Location, fetchedAt: Long): WeatherSnapshot {
            val hour = WeatherHour(
                epochSeconds = fetchedAt,
                temperatureC = 20.0,
                apparentTemperatureC = 20.0,
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
