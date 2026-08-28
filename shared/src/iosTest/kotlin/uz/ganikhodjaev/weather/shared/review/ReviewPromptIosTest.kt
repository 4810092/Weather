package uz.ganikhodjaev.weather.shared.review

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ReviewPromptIosTest {
    @Test
    fun missingForegroundWindowSceneDoesNotMarkVersion() {
        val stateStore = RecordingStateStore(eligibleState())
        val requester = SceneAwareRequester(foregroundWindowSceneAvailable = false)

        val invoked = requestIosReviewPrompt(stateStore, APP_VERSION, requester)

        assertFalse(invoked)
        assertEquals(0, requester.storeKitInvocationCount)
        assertTrue(stateStore.read().successfullyRequestedVersions.isEmpty())
        assertEquals(0, stateStore.successfulPersistenceCount)
    }

    @Test
    fun foregroundStoreKitInvocationMarksVersionWithoutClaimingDialogDisplay() {
        val stateStore = RecordingStateStore(
            eligibleState().copy(successfullyRequestedVersions = listOf(PREVIOUS_VERSION))
        )
        val requester = SceneAwareRequester(foregroundWindowSceneAvailable = true)

        val invoked = requestIosReviewPrompt(stateStore, APP_VERSION, requester)

        assertTrue(invoked)
        assertEquals(1, requester.storeKitInvocationCount)
        assertEquals(
            listOf(PREVIOUS_VERSION, APP_VERSION),
            stateStore.read().successfullyRequestedVersions
        )
        assertEquals(1, stateStore.successfulPersistenceCount)
    }

    private class SceneAwareRequester(private val foregroundWindowSceneAvailable: Boolean) :
        IosReviewRequester {
        var storeKitInvocationCount = 0
            private set

        override fun requestReviewInForegroundWindowScene(): Boolean {
            if (!foregroundWindowSceneAvailable) return false
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
