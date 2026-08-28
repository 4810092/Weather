package uz.ganikhodjaev.weather.shared

import java.net.ConnectException
import java.net.SocketException
import java.net.UnknownHostException
import javax.net.ssl.SSLHandshakeException
import kotlin.test.Test
import kotlin.test.assertEquals

class BackgroundRefreshFailureAndroidTest {
    @Test
    fun knownAndroidConnectivityFailuresAreTransient() {
        listOf(
            UnknownHostException("offline"),
            ConnectException("connection refused"),
            SocketException("connection reset")
        ).forEach { error ->
            assertEquals(
                BackgroundRefreshOutcome.TransientFailure,
                classifyBackgroundRefreshFailure(error)
            )
        }
    }

    @Test
    fun certificateFailuresArePermanent() {
        assertEquals(
            BackgroundRefreshOutcome.PermanentFailure,
            classifyBackgroundRefreshFailure(SSLHandshakeException("untrusted certificate"))
        )
    }
}
