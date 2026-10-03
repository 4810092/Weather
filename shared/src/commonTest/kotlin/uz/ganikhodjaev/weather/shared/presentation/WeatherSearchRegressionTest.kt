package uz.ganikhodjaev.weather.shared.presentation

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.filterIsInstance
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
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

class WeatherSearchRegressionTest {
    @Test
    fun editingQueryImmediatelyClearsPreviouslyVisibleResults() = searchTest { holder, source ->
        holder.updateSearchQuery("Alpha", "en")
        source.next().succeed(listOf(ALPHA))
        holder.awaitResults(listOf(ALPHA))

        holder.updateSearchQuery("Bravo", "en")
        val pending = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
        assertEquals("Bravo", pending.query)
        assertTrue(pending.isSearching)
        assertTrue(pending.results.isEmpty())
        assertEquals(null, pending.message)
    }

    @Test
    fun lateNonCooperativeResponseCannotReplaceNewerQueryResults() = searchTest { holder, source ->
        holder.updateSearchQuery("Alpha", "en")
        val old = source.next()
        holder.updateSearchQuery("Bravo", "en")
        val latest = source.next()
        latest.succeed(listOf(BRAVO))
        holder.awaitResults(listOf(BRAVO))

        old.succeed(listOf(ALPHA))
        old.returned.await()
        yield()
        assertEquals(
            listOf(BRAVO),
            assertIs<WeatherUiState.ChooseLocation>(holder.state.value).results
        )
    }

    @Test
    fun returningToSameQueryDoesNotLetFirstRequestOverwriteThirdRequest() = searchTest {
            holder,
            source
        ->
        holder.updateSearchQuery("Alpha", "en")
        val first = source.next()
        holder.updateSearchQuery("Bravo", "en")
        val second = source.next()
        holder.updateSearchQuery("Alpha", "en")
        val third = source.next()
        val newest = ALPHA.copy(id = "new-alpha", name = "Newest Alpha")
        third.succeed(listOf(newest))
        holder.awaitResults(listOf(newest))

        first.succeed(listOf(ALPHA))
        first.returned.await()
        second.fail()
        second.returned.await()
        yield()
        val picker = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
        assertEquals("Alpha", picker.query)
        assertEquals(listOf(newest), picker.results)
        assertEquals(null, picker.message)
        assertFalse(picker.isSearching)
    }

    @Test
    fun activeFailureLeavesNoOldResultsAndExplainsSearchFailure() = searchTest { holder, source ->
        holder.updateSearchQuery("Alpha", "en")
        source.next().succeed(listOf(ALPHA))
        holder.awaitResults(listOf(ALPHA))
        holder.updateSearchQuery("Bravo", "en")
        source.next().fail()
        val failed = holder.state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
            it.message == UiMessage.CitySearchUnavailable
        }
        assertTrue(failed.results.isEmpty())
        assertFalse(failed.isSearching)
    }

    @Test
    fun cancelAndReopenDiscardsResponseFromPreviousPicker() = searchTest(
        activeLocation = ALPHA
    ) { holder, source ->
        holder.state.filterIsInstance<WeatherUiState.Content>().first()
        holder.showLocationPicker()
        holder.updateSearchQuery("Alpha", "en")
        val old = source.next()
        holder.cancelLocationPicker()
        assertIs<WeatherUiState.Content>(holder.state.value)
        holder.showLocationPicker()
        holder.updateSearchQuery("Alpha", "en")
        val newest = source.next()
        val replacement = ALPHA.copy(id = "replacement")
        newest.succeed(listOf(replacement))
        holder.awaitResults(listOf(replacement))
        old.succeed(listOf(ALPHA))
        old.returned.await()
        yield()
        assertEquals(
            listOf(replacement),
            assertIs<WeatherUiState.ChooseLocation>(holder.state.value).results
        )
    }

    @Test
    fun emptyQueryCancelsPendingSearchAndDoesNotRequestEmptyResults() = searchTest {
            holder,
            source
        ->
        holder.updateSearchQuery("Alpha", "en")
        val old = source.next()
        holder.updateSearchQuery("   ", "en")
        val cleared = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
        assertEquals("", cleared.query)
        assertFalse(cleared.isSearching)
        assertTrue(cleared.results.isEmpty())
        old.succeed(listOf(ALPHA))
        old.returned.await()
        delay(400)
        val latest = assertIs<WeatherUiState.ChooseLocation>(holder.state.value)
        assertTrue(latest.results.isEmpty())
        assertEquals(null, latest.message)
        assertEquals(1, source.requests.size)
    }

    private fun searchTest(
        activeLocation: Location? = null,
        block: suspend (WeatherStateHolder, SearchSource) -> Unit
    ) = runBlocking {
        withTimeout(5_000) {
            val source = SearchSource(activeLocation)
            val holderScope = CoroutineScope(coroutineContext + SupervisorJob())
            val holder = WeatherStateHolder(
                repository = source,
                locationProvider = DeviceLocationProvider { DeviceLocationResult.PermissionDenied },
                automaticUnitSystem = UnitSystem.Metric,
                onboardingStateStore = object : OnboardingStateStore {
                    override fun read() = OnboardingState(hasCompletedFirstForecast = true)
                    override fun write(state: OnboardingState) = Unit
                },
                scope = holderScope,
                currentEpochSeconds = { 100L }
            )
            try {
                holder.start()
                block(holder, source)
            } finally {
                source.requests.forEach { it.succeed(emptyList()) }
                holderScope.cancel()
            }
        }
    }

    private suspend fun WeatherStateHolder.awaitResults(expected: List<Location>) {
        state.filterIsInstance<WeatherUiState.ChooseLocation>().first {
            !it.isSearching && it.results == expected
        }
    }

    private class Request {
        val result = CompletableDeferred<Result<List<Location>>>()
        val returned = CompletableDeferred<Unit>()

        fun succeed(locations: List<Location>) {
            result.complete(Result.success(locations))
        }

        fun fail() {
            result.complete(Result.failure(IllegalStateException("search unavailable")))
        }
    }

    private class SearchSource(private var active: Location?) : WeatherDataSource {
        val requests = mutableListOf<Request>()
        private val starts = Channel<Request>(Channel.UNLIMITED)

        suspend fun next(): Request = starts.receive()

        override suspend fun searchCities(query: String, language: String): List<Location> =
            withContext(NonCancellable) {
                val request = Request()
                requests += request
                starts.send(request)
                try {
                    request.result.await().getOrThrow()
                } finally {
                    request.returned.complete(Unit)
                }
            }

        override fun activeLocation(): Location? = active
        override fun savedLocations(): List<Location> = listOfNotNull(active)
        override fun observe(location: Location): Flow<WeatherSnapshot?> =
            MutableStateFlow(snapshot(location))
        override suspend fun refreshPrimary(location: Location): Long = 100L
        override suspend fun refreshAirQuality(location: Location) = Unit
        override suspend fun refreshHistory(location: Location) = Unit
        override suspend fun setActiveLocation(location: Location) {
            active = location
        }
        override fun deleteLocation(locationId: String) = Unit
        override fun updateLocationDetails(location: Location) = Unit
        override fun unitPreference(): UnitPreference = UnitPreference.Automatic
        override fun setUnitPreference(preference: UnitPreference) = Unit
    }

    private companion object {
        val ALPHA = Location("alpha", "Alpha", "UZ", 41.0, 69.0, "Asia/Tashkent")
        val BRAVO = ALPHA.copy(id = "bravo", name = "Bravo")

        fun snapshot(location: Location): WeatherSnapshot {
            val hour = WeatherHour(100L, 20.0, 20.0, 0, 0, 0.0, 5.0, 8.0, 40, 1.0, 100L)
            return WeatherSnapshot(
                location,
                hour,
                listOf(hour),
                fetchedAtEpochSeconds = 100L,
                isStale = false
            )
        }
    }
}
