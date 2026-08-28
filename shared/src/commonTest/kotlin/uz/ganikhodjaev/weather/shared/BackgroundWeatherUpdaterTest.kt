package uz.ganikhodjaev.weather.shared

import io.ktor.client.network.sockets.ConnectTimeoutException
import io.ktor.client.network.sockets.SocketTimeoutException
import io.ktor.client.plugins.HttpRequestTimeoutException
import io.ktor.client.request.HttpRequestBuilder
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlinx.serialization.SerializationException

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

    private class FakeDatabaseException(message: String) : RuntimeException(message)
}
