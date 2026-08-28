package uz.ganikhodjaev.weather.shared

import io.ktor.client.network.sockets.ConnectTimeoutException
import io.ktor.client.network.sockets.SocketTimeoutException
import io.ktor.client.plugins.HttpRequestTimeoutException
import io.ktor.client.request.HttpRequestBuilder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.SerializationException
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class BackgroundWeatherUpdaterTest {
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
    fun primaryFailureClassificationSurvivesBackgroundRefreshFlow() = runBlocking {
        listOf(
            HttpRequestTimeoutException(HttpRequestBuilder()) to
                BackgroundRefreshOutcome.TransientFailure,
            SerializationException("invalid primary payload") to
                BackgroundRefreshOutcome.PermanentFailure
        ).forEach { (failure, expected) ->
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

    private class FakeWeatherDataSource(
        private val primaryFailure: Throwable? = null,
        private val airQualityFailure: Throwable? = null
    ) : WeatherDataSource {
        var primaryRefreshCount = 0
            private set
        var airQualityRefreshCount = 0
            private set
        private var unitPreference = UnitPreference.Automatic

        override fun activeLocation(): Location = LOCATION

        override fun savedLocations(): List<Location> = listOf(LOCATION)

        override fun observe(location: Location): Flow<WeatherSnapshot?> = flowOf(SNAPSHOT)

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
