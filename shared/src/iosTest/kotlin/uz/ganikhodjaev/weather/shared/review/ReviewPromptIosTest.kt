package uz.ganikhodjaev.weather.shared.review

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ReviewPromptIosTest {
    @Test
    fun unavailableForegroundPresentationDoesNotMarkVersion() {
        val stateStore = RecordingStateStore(eligibleState())
        val requester = RecordingRequester(requestInvoked = false)

        val invoked = requestIosReviewPrompt(stateStore, APP_VERSION, requester)

        assertFalse(invoked)
        assertEquals(0, requester.storeKitInvocationCount)
        assertTrue(stateStore.read().successfullyRequestedVersions.isEmpty())
        assertEquals(0, stateStore.successfulPersistenceCount)
    }

    @Test
    fun storeKitFailureDoesNotConsumeTheVersion() {
        val stateStore = RecordingStateStore(eligibleState())

        val invoked = requestIosReviewPrompt(
            stateStore = stateStore,
            appVersion = APP_VERSION,
            requester = IosReviewRequester { error("StoreKit unavailable") }
        )

        assertFalse(invoked)
        assertTrue(stateStore.read().successfullyRequestedVersions.isEmpty())
        assertEquals(0, stateStore.successfulPersistenceCount)
    }

    @Test
    fun foregroundStoreKitInvocationMarksVersionWithoutClaimingDialogDisplay() {
        val stateStore = RecordingStateStore(
            eligibleState().copy(successfullyRequestedVersions = listOf(PREVIOUS_VERSION))
        )
        val requester = RecordingRequester(requestInvoked = true)

        val invoked = requestIosReviewPrompt(stateStore, APP_VERSION, requester)

        assertTrue(invoked)
        assertEquals(1, requester.storeKitInvocationCount)
        assertEquals(
            listOf(PREVIOUS_VERSION, APP_VERSION),
            stateStore.read().successfullyRequestedVersions
        )
        assertEquals(1, stateStore.successfulPersistenceCount)
    }

    @Test
    fun foregroundSceneTakesPriorityOverLegacyWindow() {
        assertEquals(
            IosReviewRequestPath.ForegroundWindowScene,
            selectIosReviewRequestPath(
                isApplicationActive = true,
                hasForegroundWindowScene = true,
                hasLegacyKeyWindow = true
            )
        )
    }

    @Test
    fun activeLegacyWindowIsAReviewFallbackWhenNoSceneExists() {
        assertEquals(
            IosReviewRequestPath.LegacyKeyWindow,
            selectIosReviewRequestPath(
                isApplicationActive = true,
                hasForegroundWindowScene = false,
                hasLegacyKeyWindow = true
            )
        )
    }

    @Test
    fun inactiveApplicationNeverRequestsReview() {
        assertEquals(
            null,
            selectIosReviewRequestPath(
                isApplicationActive = false,
                hasForegroundWindowScene = true,
                hasLegacyKeyWindow = true
            )
        )
        assertEquals(
            null,
            selectIosReviewRequestPath(
                isApplicationActive = false,
                hasForegroundWindowScene = false,
                hasLegacyKeyWindow = true
            )
        )
    }

    @Test
    fun activeApplicationWithoutAReviewSurfaceRemainsRetryable() {
        assertEquals(
            null,
            selectIosReviewRequestPath(
                isApplicationActive = true,
                hasForegroundWindowScene = false,
                hasLegacyKeyWindow = false
            )
        )
    }

    private class RecordingRequester(private val requestInvoked: Boolean) : IosReviewRequester {
        var storeKitInvocationCount = 0
            private set

        override fun requestReviewWhenForeground(): Boolean {
            if (!requestInvoked) return false
            storeKitInvocationCount += 1
            return true
        }
    }

    private class RecordingStateStore(private var state: ReviewPromptPolicyState) :
        ReviewPromptPolicyStateStore {
        var successfulPersistenceCount = 0
            private set

        override fun read(): ReviewPromptPolicyState = state

        override fun write(state: ReviewPromptPolicyState) {
            this.state = state
        }

        override fun persistRequestSuccess(state: ReviewPromptPolicyState): Boolean {
            this.state = state
            successfulPersistenceCount += 1
            return true
        }
    }

    private companion object {
        const val PREVIOUS_VERSION = "1.0.2"
        const val APP_VERSION = "1.1.0"

        fun eligibleState() = ReviewPromptPolicyState(
            trackedVersion = APP_VERSION,
            successfulForecastCount = 3,
            successfulLocalDays = setOf("2026-08-28", "2026-08-29"),
            lastCountedForecastId = 3L
        )
    }
}
