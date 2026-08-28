package uz.ganikhodjaev.weather.shared

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class StoreLinkProviderTest {
    @Test
    fun storeLinksAreCanonicalAndContainNoTrackingParameters() {
        val links = listOf(NimboStoreLinks.GOOGLE_PLAY, NimboStoreLinks.APP_STORE)

        assertTrue(links.all { it.startsWith("https://") })
        assertTrue(links.none { "utm_" in it })
        assertTrue(links.none { "referrer=" in it })
    }

    @Test
    fun shareMessageAddsLocalizedCallToActionAndPlatformLinkOnSeparateLines() {
        val message = formatShareMessage(
            weatherSummary = "Toshkent: 28°, 10% chance of rain — Nimbo",
            storeCallToAction = "Get Nimbo for your next walk:",
            storeUrl = NimboStoreLinks.GOOGLE_PLAY
        )

        assertEquals(3, message.lines().size)
        assertEquals(NimboStoreLinks.GOOGLE_PLAY, message.lines().last())
        assertFalse("41.2995" in message)
        assertFalse("69.2401" in message)
    }
}
