package uz.ganikhodjaev.weather.shared.review

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ReviewPromptPolicyTest {
    @Test
    fun requiresThreeSuccessfulForecastsAcrossTwoLocalDays() {
        var state = ReviewPromptPolicyState()

        state = record(state, 1, "2026-08-28").also {
            assertFalse(it.shouldRequestReview)
        }.state
        state = record(state, 2, "2026-08-28").also {
            assertFalse(it.shouldRequestReview)
        }.state
        state = record(state, 3, "2026-08-28").also {
            assertFalse(it.shouldRequestReview)
        }.state
        val eligible = record(state, 4, "2026-08-29")

        assertTrue(eligible.shouldRequestReview)
        assertEquals(3, eligible.state.successfulForecastCount)
        assertEquals(setOf("2026-08-28", "2026-08-29"), eligible.state.successfulLocalDays)
    }

    @Test
    fun sameForecastIsCountedOnce() {
        val first = record(ReviewPromptPolicyState(), 7, "2026-08-28")
        val duplicate = record(first.state, 7, "2026-08-29")

        assertEquals(1, duplicate.state.successfulForecastCount)
        assertEquals(setOf("2026-08-28"), duplicate.state.successfulLocalDays)
        assertFalse(duplicate.shouldRequestReview)
    }

    @Test
    fun failedPlatformFlowRemainsEligibleForRetry() {
        var state = ReviewPromptPolicyState()
        state = record(state, 1, "2026-08-28").state
        state = record(state, 2, "2026-08-28").state
        val eligible = record(state, 3, "2026-08-29")

        val retry = record(eligible.state, 3, "2026-08-29")

        assertTrue(retry.shouldRequestReview)
        assertEquals(eligible.state, retry.state)
    }

    @Test
    fun successfulPlatformFlowBlocksAnotherRequestForVersion() {
        var state = ReviewPromptPolicyState()
        state = record(state, 1, "2026-08-28").state
        state = record(state, 2, "2026-08-28").state
        state = record(state, 3, "2026-08-29").state
        state = ReviewPromptPolicy.markRequestSucceeded(state, APP_VERSION)

        val nextForecast = record(state, 4, "2026-08-30")

        assertFalse(nextForecast.shouldRequestReview)
        assertEquals(APP_VERSION, nextForecast.state.successfullyRequestedVersion)
    }

    @Test
    fun newVersionMustEarnItsOwnMilestone() {
        var state = ReviewPromptPolicyState()
        state = record(state, 1, "2026-08-28").state
        state = record(state, 2, "2026-08-28").state
        state = record(state, 3, "2026-08-29").state
        state = ReviewPromptPolicy.markRequestSucceeded(state, APP_VERSION)

        val nextVersion = ReviewPromptPolicy.recordSuccessfulForecast(
            currentState = state,
            appVersion = "1.0.3",
            forecastId = 4,
            localDay = "2026-08-30"
        )

        assertFalse(nextVersion.shouldRequestReview)
        assertEquals(1, nextVersion.state.successfulForecastCount)
        assertEquals("1.0.3", nextVersion.state.trackedVersion)
    }

    private fun record(
        state: ReviewPromptPolicyState,
        forecastId: Long,
        localDay: String
    ): ReviewPromptPolicyDecision = ReviewPromptPolicy.recordSuccessfulForecast(
        currentState = state,
        appVersion = APP_VERSION,
        forecastId = forecastId,
        localDay = localDay
    )

    private companion object {
        const val APP_VERSION = "1.0.2"
    }
}
