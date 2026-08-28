package uz.ganikhodjaev.weather.shared

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class StoreLinkProviderTest {
    @Test
    fun platformStoreLinksMatchPublishedCanonicalUrlsExactly() {
        assertEquals(
            "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather",
            NimboStoreLinks.GOOGLE_PLAY
        )
        assertEquals(
            "https://apps.apple.com/app/id6799886897",
            NimboStoreLinks.APP_STORE
        )
    }

    @Test
    fun storeLinksContainNoOptionalQueryTrackingOrFragment() {
        val googlePlay = NimboStoreLinks.GOOGLE_PLAY
        val appStore = NimboStoreLinks.APP_STORE
        val links = listOf(googlePlay, appStore)

        assertTrue(links.all { it.startsWith("https://") })
        assertTrue(links.none { "utm_" in it })
        assertTrue(links.none { "referrer=" in it })
        assertFalse("#" in googlePlay)
        assertEquals("id=uz.ganikhodjaev.weather", googlePlay.substringAfter('?'))
        assertFalse("&" in googlePlay)
        assertFalse("?" in appStore)
        assertFalse("#" in appStore)
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
