package uz.ganikhodjaev.weather.shared

import io.ktor.client.network.sockets.ConnectTimeoutException
import io.ktor.client.network.sockets.SocketTimeoutException
import io.ktor.client.plugins.HttpRequestTimeoutException
import io.ktor.client.request.HttpRequestBuilder
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.async
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.yield
import kotlinx.serialization.SerializationException
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class BackgroundWeatherUpdaterTest {
    @BeforeTest
    fun resetAutomaticRefreshCoordinator() = runBlocking {
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
    }

    @Test
    fun futureCacheAndAttemptTimestampsAreRefreshable() {
        val clockBeforeSnapshot = SNAPSHOT.fetchedAtEpochSeconds - 1L

        assertTrue(SNAPSHOT.isAutomaticRefreshDue(clockBeforeSnapshot))
        assertTrue(
            isAutomaticRefreshAttemptDue(
                lastAttemptEpochSeconds = SNAPSHOT.fetchedAtEpochSeconds,
                nowEpochSeconds = clockBeforeSnapshot
            )
        )
    }

    @Test
    fun persistedAttemptSurvivesProcessCoordinatorReset() = runBlocking {
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        val firstAttemptAt = 10_000L

        assertIs<AutomaticRefreshClaimResult.Granted>(
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = firstAttemptAt,
                attemptStore = attemptStore
            )
        )
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()

        assertEquals(
            AutomaticRefreshClaimResult.RetryDeferred,
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = firstAttemptAt + AUTOMATIC_REFRESH_MIN_AGE_SECONDS - 1L,
                attemptStore = attemptStore
            )
        )
        assertIs<AutomaticRefreshClaimResult.Granted>(
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = firstAttemptAt + AUTOMATIC_REFRESH_MIN_AGE_SECONDS,
                attemptStore = attemptStore
            )
        )
        Unit
    }

    @Test
    fun opaquePreferenceKeyDoesNotContainLocationId() {
        val key = automaticRefreshAttemptStorageKey(LOCATION.id)

        assertFalse(key.contains(LOCATION.id))
        assertTrue(key.startsWith("last_attempt_"))
        assertEquals(key, automaticRefreshAttemptStorageKey(LOCATION.id))
    }

    @Test
    fun automaticAttemptFailsClosedWhenDurableWriteFails() = runBlocking {
        val attemptStore = RejectingAutomaticRefreshAttemptStore()
        val nowEpochSeconds = SNAPSHOT.fetchedAtEpochSeconds +
            AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val repository = FakeWeatherDataSource()
        val published = mutableListOf<WeatherSnapshot>()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            nowEpochSeconds = nowEpochSeconds,
            attemptStore = attemptStore,
            publishSnapshot = { published += it }
        )

        assertEquals(BackgroundRefreshOutcome.TransientFailure, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
        assertEquals(listOf(SNAPSHOT), published)
        assertEquals(1, attemptStore.writeCount)
    }

    @Test
    fun automaticAttemptFailsClosedWhenDurableReadFails() = runBlocking {
        val repository = FakeWeatherDataSource()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            nowEpochSeconds = SNAPSHOT.fetchedAtEpochSeconds +
                AUTOMATIC_REFRESH_MIN_AGE_SECONDS,
            attemptStore = ReadFailingAutomaticRefreshAttemptStore,
            publishSnapshot = {}
        )

        assertEquals(BackgroundRefreshOutcome.TransientFailure, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
    }

    @Test
    fun retryDeferredOutcomeSurvivesCachedSnapshotPublishFailure() = runBlocking {
        val firstAttemptAt = SNAPSHOT.fetchedAtEpochSeconds +
            AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        attemptStore.writeDurably(
            LOCATION.id,
            AutomaticRefreshAttemptState(
                token = 1L,
                attemptedAtEpochSeconds = firstAttemptAt,
                phase = AutomaticRefreshAttemptPhase.RetryPending
            )
        )
        val repository = FakeWeatherDataSource()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            nowEpochSeconds = firstAttemptAt + 1L,
            attemptStore = attemptStore,
            publishSnapshot = { error("widget unavailable") }
        )

        assertEquals(BackgroundRefreshOutcome.TransientFailure, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
    }

    @Test
    fun transientFailureStaysDeferredUntilOneRealRetryIsDue() = runBlocking {
        val firstAttemptAt = SNAPSHOT.fetchedAtEpochSeconds +
            AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        val repository = FakeWeatherDataSource(
            primaryFailure = HttpRequestTimeoutException(HttpRequestBuilder())
        )

        assertEquals(
            BackgroundRefreshOutcome.TransientFailure,
            refreshBackgroundWeather(
                repository = repository,
                nowEpochSeconds = firstAttemptAt,
                attemptStore = attemptStore,
                publishSnapshot = {}
            )
        )
        assertEquals(1, repository.primaryRefreshCount)
        assertEquals(
            AutomaticRefreshAttemptPhase.RetryPending,
            attemptStore.read(LOCATION.id)?.phase
        )

        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
        assertEquals(
            BackgroundRefreshOutcome.TransientFailure,
            refreshBackgroundWeather(
                repository = repository,
                nowEpochSeconds = firstAttemptAt + 1L,
                attemptStore = attemptStore,
                publishSnapshot = {}
            )
        )
        assertEquals(1, repository.primaryRefreshCount)

        repository.primaryFailure = null
        assertEquals(
            BackgroundRefreshOutcome.Updated,
            refreshBackgroundWeather(
                repository = repository,
                nowEpochSeconds = firstAttemptAt + AUTOMATIC_REFRESH_MIN_AGE_SECONDS,
                attemptStore = attemptStore,
                publishSnapshot = {}
            )
        )
        assertEquals(2, repository.primaryRefreshCount)
        assertEquals(1, repository.airQualityRefreshCount)
        assertEquals(
            AutomaticRefreshAttemptPhase.Cooldown,
            attemptStore.read(LOCATION.id)?.phase
        )
    }

    @Test
    fun staleAutomaticCompletionCannotOverwriteANewerManualAttempt() = runBlocking {
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        val claim = assertIs<AutomaticRefreshClaimResult.Granted>(
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = 10_000L,
                attemptStore = attemptStore
            )
        )
        AutomaticRefreshCoordinator.recordManualAttempt(
            locationId = LOCATION.id,
            nowEpochSeconds = 10_001L,
            attemptStore = attemptStore
        )

        assertFalse(
            AutomaticRefreshCoordinator.finalizeAutomaticAttempt(
                locationId = LOCATION.id,
                token = claim.token,
                completion = AutomaticRefreshAttemptCompletion.RetryPending,
                attemptStore = attemptStore
            )
        )
        assertEquals(
            AutomaticRefreshAttemptPhase.Cooldown,
            attemptStore.read(LOCATION.id)?.phase
        )
        assertEquals(10_001L, attemptStore.read(LOCATION.id)?.attemptedAtEpochSeconds)
    }

    @Test
    fun manualAttemptUsesBestEffortPersistenceWithoutStrictWrite() = runBlocking {
        val attemptStore = ManualOnlyAutomaticRefreshAttemptStore()

        AutomaticRefreshCoordinator.recordManualAttempt(
            locationId = LOCATION.id,
            nowEpochSeconds = 10_000L,
            attemptStore = attemptStore
        )

        assertEquals(1, attemptStore.bestEffortWriteCount)
        assertEquals(0, attemptStore.strictWriteCount)
    }

    @Test
    fun manualAttemptRemainsInMemoryWhenBestEffortPersistenceFails() = runBlocking {
        val attemptAt = 10_000L

        AutomaticRefreshCoordinator.recordManualAttempt(
            locationId = LOCATION.id,
            nowEpochSeconds = attemptAt,
            attemptStore = BestEffortFailingAutomaticRefreshAttemptStore
        )

        assertEquals(
            AutomaticRefreshClaimResult.Cooldown,
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = attemptAt + 1L,
                attemptStore = BestEffortFailingAutomaticRefreshAttemptStore
            )
        )
    }

    @Test
    fun strictAutomaticWriteForOneLocationDoesNotBlockManualAnotherLocation() = runBlocking {
        val attemptStore = BlockingStrictAutomaticRefreshAttemptStore(LOCATION.id)
        val automaticClaim = async {
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = 10_000L,
                attemptStore = attemptStore
            )
        }
        attemptStore.strictWriteStarted.await()

        withTimeout(1_000L) {
            AutomaticRefreshCoordinator.recordManualAttempt(
                locationId = "quick:uz:samarkand",
                nowEpochSeconds = 10_001L,
                attemptStore = attemptStore
            )
        }

        assertEquals(1, attemptStore.bestEffortWriteCount)
        attemptStore.allowStrictWrite.complete(Unit)
        assertIs<AutomaticRefreshClaimResult.Granted>(automaticClaim.await())
        Unit
    }

    @Test
    fun cooldownStoreCancellationIsNotSwallowed() = runBlocking {
        var cancellationPropagated = false

        try {
            AutomaticRefreshCoordinator.recordManualAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = 10_000L,
                attemptStore = CancellingAutomaticRefreshAttemptStore
            )
        } catch (_: CancellationException) {
            cancellationPropagated = true
        }

        assertTrue(cancellationPropagated)
    }

    @Test
    fun automaticClaimStoreCancellationIsNotSwallowed() = runBlocking {
        var cancellationPropagated = false

        try {
            AutomaticRefreshCoordinator.claimAutomaticAttempt(
                locationId = LOCATION.id,
                nowEpochSeconds = 10_000L,
                attemptStore = CancellingAutomaticRefreshAttemptStore
            )
        } catch (_: CancellationException) {
            cancellationPropagated = true
        }

        assertTrue(cancellationPropagated)
    }

    @Test
    fun durableAttemptStateEncodingRoundTrips() {
        AutomaticRefreshAttemptPhase.entries.forEach { phase ->
            val state = AutomaticRefreshAttemptState(
                token = 42L,
                attemptedAtEpochSeconds = 10_000L,
                phase = phase
            )
            assertEquals(
                state,
                decodeAutomaticRefreshAttemptState(encodeAutomaticRefreshAttemptState(state))
            )
        }
    }

    @Test
    fun unknownRuntimeFailuresArePermanent() {
        assertEquals(
            BackgroundRefreshOutcome.PermanentFailure,
            classifyBackgroundRefreshFailure(IllegalStateException("unexpected state"))
        )
    }

    @Test
    fun databaseAndSerializationFailuresArePermanent() {
        assertEquals(
            BackgroundRefreshOutcome.PermanentFailure,
            classifyBackgroundRefreshFailure(FakeDatabaseException("database write failed"))
        )
        assertEquals(
            BackgroundRefreshOutcome.PermanentFailure,
            classifyBackgroundRefreshFailure(SerializationException("invalid provider payload"))
        )
    }

    @Test
    fun knownKtorTimeoutsAreTransientIncludingWhenWrapped() {
        val requestTimeout = HttpRequestTimeoutException(HttpRequestBuilder())
        val connectTimeout = ConnectTimeoutException("connect timeout")
        val socketTimeout = SocketTimeoutException("socket timeout")

        listOf(
            requestTimeout,
            connectTimeout,
            socketTimeout,
            IllegalStateException("wrapper", requestTimeout)
        ).forEach { error ->
            assertEquals(
                BackgroundRefreshOutcome.TransientFailure,
                classifyBackgroundRefreshFailure(error)
            )
        }
    }

    @Test
    fun onlyExplicitRetryableHttpStatusesAreTransient() {
        listOf(408, 425, 429, 500, 502, 599).forEach { status ->
            assertEquals(true, status.isTransientHttpStatus(), "HTTP $status")
        }
        listOf(400, 401, 403, 404, 409, 422, 499, 600).forEach { status ->
            assertEquals(false, status.isTransientHttpStatus(), "HTTP $status")
        }
    }

    @Test
    fun optionalAirQualityFailureDoesNotDowngradeUpdatedForecast() = runBlocking {
        val repository = FakeWeatherDataSource(
            airQualityFailure = SerializationException("optional AQI payload")
        )
        val published = mutableListOf<WeatherSnapshot>()

        val outcome = refreshBackgroundWeather(repository) { published += it }

        assertEquals(BackgroundRefreshOutcome.Updated, outcome)
        assertEquals(1, repository.primaryRefreshCount)
        assertEquals(1, repository.airQualityRefreshCount)
        assertEquals(listOf(SNAPSHOT), published)
    }

    @Test
    fun freshCachedWeatherSkipsProviderCallsAndStillPublishes() = runBlocking {
        val repository = FakeWeatherDataSource()
        val published = mutableListOf<WeatherSnapshot>()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            publishSnapshot = { published += it },
            nowEpochSeconds = SNAPSHOT.fetchedAtEpochSeconds +
                AUTOMATIC_REFRESH_MIN_AGE_SECONDS - 1L
        )

        assertEquals(BackgroundRefreshOutcome.NothingToRefresh, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
        assertEquals(listOf(SNAPSHOT), published)
    }

    @Test
    fun cachedWeatherAtRefreshBoundaryCallsProvider() = runBlocking {
        val repository = FakeWeatherDataSource()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            publishSnapshot = {},
            nowEpochSeconds = SNAPSHOT.fetchedAtEpochSeconds +
                AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        )

        assertEquals(BackgroundRefreshOutcome.Updated, outcome)
        assertEquals(1, repository.primaryRefreshCount)
        assertEquals(1, repository.airQualityRefreshCount)
    }

    @Test
    fun persistedAttemptSkipsBackgroundProviderCallAfterCoordinatorReset() = runBlocking {
        val attemptStore = InMemoryAutomaticRefreshAttemptStore()
        val recentAttemptAt = SNAPSHOT.fetchedAtEpochSeconds +
            AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        attemptStore.writeDurably(
            LOCATION.id,
            AutomaticRefreshAttemptState(
                token = 1L,
                attemptedAtEpochSeconds = recentAttemptAt,
                phase = AutomaticRefreshAttemptPhase.Cooldown
            )
        )
        AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
        val repository = FakeWeatherDataSource()
        val published = mutableListOf<WeatherSnapshot>()

        val outcome = refreshBackgroundWeather(
            repository = repository,
            nowEpochSeconds = recentAttemptAt + 1L,
            attemptStore = attemptStore,
            publishSnapshot = { published += it }
        )

        assertEquals(BackgroundRefreshOutcome.NothingToRefresh, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
        assertEquals(listOf(SNAPSHOT), published)
    }

    @Test
    fun cacheReadFailureDoesNotCallProvider() = runBlocking {
        val repository = FakeWeatherDataSource(
            observeFailure = FakeDatabaseException("cache unavailable")
        )
        var published = false

        val outcome = refreshBackgroundWeather(repository) { published = true }

        assertEquals(BackgroundRefreshOutcome.PermanentFailure, outcome)
        assertEquals(0, repository.primaryRefreshCount)
        assertEquals(0, repository.airQualityRefreshCount)
        assertFalse(published)
    }

    @Test
    fun concurrentAutomaticPathsCoalescePerLocation() = runBlocking {
        val refreshedAt = SNAPSHOT.fetchedAtEpochSeconds +
            2L * AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        val repository = CoordinatedWeatherDataSource(refreshedAt)
        val published = mutableListOf<WeatherSnapshot>()

        val first = async {
            refreshBackgroundWeather(repository, nowEpochSeconds = refreshedAt) {
                published += it
            }
        }
        repository.primaryStarted.await()
        val second = async {
            refreshBackgroundWeather(repository, nowEpochSeconds = refreshedAt) {
                published += it
            }
        }
        yield()

        assertEquals(1, repository.primaryRefreshCount)
        repository.allowPrimaryToFinish.complete(Unit)

        assertEquals(
            listOf(
                BackgroundRefreshOutcome.Updated,
                BackgroundRefreshOutcome.NothingToRefresh
            ),
            listOf(first.await(), second.await())
        )
        assertEquals(1, repository.primaryRefreshCount)
        assertEquals(1, repository.airQualityRefreshCount)
        assertEquals(2, published.size)
    }

    @Test
    fun queuedAutomaticPathReadsProductionClockAfterAcquiringLocationLock() = runBlocking {
        val refreshedAt = SNAPSHOT.fetchedAtEpochSeconds +
            2L * AUTOMATIC_REFRESH_MIN_AGE_SECONDS
        var currentEpochSeconds = refreshedAt
        val repository = CoordinatedWeatherDataSource(refreshedAt)

        val first = async {
            refreshBackgroundWeather(
                repository = repository,
                currentEpochSeconds = { currentEpochSeconds },
                publishSnapshot = {}
            )
        }
        repository.primaryStarted.await()

        currentEpochSeconds = refreshedAt - 1L
        val queued = async {
            refreshBackgroundWeather(
                repository = repository,
                currentEpochSeconds = { currentEpochSeconds },
                publishSnapshot = {}
            )
        }
        yield()
        assertEquals(1, repository.primaryRefreshCount)

        currentEpochSeconds = refreshedAt + 1L
        repository.allowPrimaryToFinish.complete(Unit)

        assertEquals(BackgroundRefreshOutcome.Updated, first.await())
        assertEquals(BackgroundRefreshOutcome.NothingToRefresh, queued.await())
        assertEquals(1, repository.primaryRefreshCount)
        assertEquals(1, repository.airQualityRefreshCount)
    }

    @Test
    fun primaryFailureClassificationSurvivesBackgroundRefreshFlow() = runBlocking {
        listOf(
            HttpRequestTimeoutException(HttpRequestBuilder()) to
                BackgroundRefreshOutcome.TransientFailure,
            SerializationException("invalid primary payload") to
                BackgroundRefreshOutcome.PermanentFailure
        ).forEach { (failure, expected) ->
            AutomaticRefreshCoordinator.resetAttemptHistoryForTests()
            val repository = FakeWeatherDataSource(primaryFailure = failure)
            var publishedCachedSnapshot = false

            val outcome = refreshBackgroundWeather(repository) {
                publishedCachedSnapshot = true
            }

            assertEquals(expected, outcome)
            assertEquals(1, repository.primaryRefreshCount)
            assertEquals(0, repository.airQualityRefreshCount)
            assertTrue(publishedCachedSnapshot)
        }
    }

    @Test
    fun cancellableRefreshSuppressesCompletionAfterExpiration() = runBlocking {
        val operationStarted = CompletableDeferred<Unit>()
        val operationCanFinish = CompletableDeferred<Unit>()
        val completions = mutableListOf<Boolean>()
        val refreshScope = CoroutineScope(coroutineContext + SupervisorJob())

        try {
            val handle = startCancellableBackgroundRefresh(
                scope = refreshScope,
                refresh = {
                    operationStarted.complete(Unit)
                    operationCanFinish.await()
                    true
                },
                onComplete = completions::add
            )
            operationStarted.await()

            handle.cancel()
            operationCanFinish.complete(Unit)
            handle.join()

            assertTrue(completions.isEmpty())
        } finally {
            refreshScope.cancel()
        }
    }

    @Test
    fun cancellableRefreshReportsExactlyOneTerminalResult() = runBlocking {
        val completions = mutableListOf<Boolean>()
        val refreshScope = CoroutineScope(coroutineContext + SupervisorJob())

        try {
            val handle = startCancellableBackgroundRefresh(
                scope = refreshScope,
                refresh = { true },
                onComplete = completions::add
            )
            handle.join()
            handle.cancel()

            assertEquals(listOf(true), completions)
        } finally {
            refreshScope.cancel()
        }
    }

    private class FakeDatabaseException(message: String) : RuntimeException(message)

    private class RejectingAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
        var writeCount = 0
            private set

        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean {
            writeCount += 1
            return false
        }

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) = Unit

        override suspend fun removeDurably(locationId: String): Boolean = false
    }

    private object CancellingAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean = throw CancellationException("test cancellation")

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) =
            throw CancellationException("test cancellation")

        override suspend fun removeDurably(locationId: String): Boolean =
            throw CancellationException("test cancellation")
    }

    private object ReadFailingAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? =
            error("preferences unavailable")

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean = error("strict write must not run")

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) = Unit

        override suspend fun removeDurably(locationId: String): Boolean = false
    }

    private object BestEffortFailingAutomaticRefreshAttemptStore :
        AutomaticRefreshAttemptStore {
        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean = true

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) =
            error("best-effort persistence unavailable")

        override suspend fun removeDurably(locationId: String): Boolean = true
    }

    private class FakeWeatherDataSource(
        var primaryFailure: Throwable? = null,
        private val airQualityFailure: Throwable? = null,
        private val observeFailure: Throwable? = null
    ) : WeatherDataSource {
        var primaryRefreshCount = 0
            private set
        var airQualityRefreshCount = 0
            private set
        private var unitPreference = UnitPreference.Automatic

        override fun activeLocation(): Location = LOCATION

        override fun savedLocations(): List<Location> = listOf(LOCATION)

        override fun observe(location: Location): Flow<WeatherSnapshot?> {
            observeFailure?.let { throw it }
            return flowOf(SNAPSHOT)
        }

        override suspend fun refreshPrimary(location: Location): Long {
            primaryRefreshCount += 1
            primaryFailure?.let { throw it }
            return SNAPSHOT.fetchedAtEpochSeconds
        }

        override suspend fun refreshAirQuality(location: Location) {
            airQualityRefreshCount += 1
            airQualityFailure?.let { throw it }
        }

        override suspend fun refreshHistory(location: Location) = Unit

        override suspend fun searchCities(query: String, language: String): List<Location> =
            emptyList()

        override suspend fun setActiveLocation(location: Location) = Unit

        override fun deleteLocation(locationId: String) = Unit

        override fun updateLocationDetails(location: Location) = Unit

        override fun unitPreference(): UnitPreference = unitPreference

        override fun setUnitPreference(preference: UnitPreference) {
            unitPreference = preference
        }
    }

    private class ManualOnlyAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
        var strictWriteCount = 0
            private set
        var bestEffortWriteCount = 0
            private set

        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean {
            strictWriteCount += 1
            return true
        }

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
            bestEffortWriteCount += 1
        }

        override suspend fun removeDurably(locationId: String): Boolean = true
    }

    private class BlockingStrictAutomaticRefreshAttemptStore(
        private val blockedLocationId: String
    ) : AutomaticRefreshAttemptStore {
        val strictWriteStarted = CompletableDeferred<Unit>()
        val allowStrictWrite = CompletableDeferred<Unit>()
        var bestEffortWriteCount = 0
            private set

        override suspend fun read(locationId: String): AutomaticRefreshAttemptState? = null

        override suspend fun writeDurably(
            locationId: String,
            state: AutomaticRefreshAttemptState
        ): Boolean {
            if (locationId == blockedLocationId) {
                strictWriteStarted.complete(Unit)
                allowStrictWrite.await()
            }
            return true
        }

        override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
            bestEffortWriteCount += 1
        }

        override suspend fun removeDurably(locationId: String): Boolean = true
    }

    private class CoordinatedWeatherDataSource(private val refreshedAtEpochSeconds: Long) :
        WeatherDataSource {
        private val weather = MutableStateFlow<WeatherSnapshot?>(SNAPSHOT)
        val primaryStarted = CompletableDeferred<Unit>()
        val allowPrimaryToFinish = CompletableDeferred<Unit>()
        var primaryRefreshCount = 0
            private set
        var airQualityRefreshCount = 0
            private set
        private var unitPreference = UnitPreference.Automatic

        override fun activeLocation(): Location = LOCATION

        override fun savedLocations(): List<Location> = listOf(LOCATION)

        override fun observe(location: Location): Flow<WeatherSnapshot?> = weather

        override suspend fun refreshPrimary(location: Location): Long {
            primaryRefreshCount += 1
            primaryStarted.complete(Unit)
            allowPrimaryToFinish.await()
            weather.value = SNAPSHOT.copy(fetchedAtEpochSeconds = refreshedAtEpochSeconds)
            return refreshedAtEpochSeconds
        }

        override suspend fun refreshAirQuality(location: Location) {
            airQualityRefreshCount += 1
        }

        override suspend fun refreshHistory(location: Location) = Unit

        override suspend fun searchCities(query: String, language: String): List<Location> =
            emptyList()

        override suspend fun setActiveLocation(location: Location) = Unit

        override fun deleteLocation(locationId: String) = Unit

        override fun updateLocationDetails(location: Location) = Unit

        override fun unitPreference(): UnitPreference = unitPreference

        override fun setUnitPreference(preference: UnitPreference) {
            unitPreference = preference
        }
    }

    private companion object {
        val LOCATION = Location(
            id = "quick:uz:tashkent",
            name = "Toshkent",
            country = "Oʻzbekiston",
            latitude = 41.2995,
            longitude = 69.2401,
            timezone = "Asia/Tashkent"
        )
        val HOUR = WeatherHour(
            epochSeconds = 100L,
            temperatureC = 25.0,
            apparentTemperatureC = 25.0,
            weatherCode = 0,
            precipitationProbability = 0,
            precipitationMm = 0.0,
            windKph = 5.0,
            gustKph = 8.0,
            humidityPercent = 40,
            uvIndex = 1.0,
            fetchedAtEpochSeconds = 100L
        )
        val SNAPSHOT = WeatherSnapshot(
            location = LOCATION,
            current = HOUR,
            timeline = listOf(HOUR),
            fetchedAtEpochSeconds = 100L,
            isStale = false
        )
    }
}
