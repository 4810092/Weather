package uz.ganikhodjaev.weather.shared.review

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ReviewPromptAndroidTest {
    @Test
    fun failedPlayRequestDoesNotMarkVersion() {
        val backing = ReviewStateBacking(eligibleState())
        val stateStore = BackedStateStore(backing)
        val finishResults = mutableListOf<Boolean>()

        requestAndroidReviewPrompt(
            stateStore = stateStore,
            appVersion = APP_VERSION,
            requester = AndroidReviewRequester { onComplete -> onComplete(false) },
            onFinished = { finishResults += it }
        )

        assertTrue(stateStore.read().successfullyRequestedVersions.isEmpty())
        assertEquals(0, backing.durableSuccessWrites)
        assertEquals(listOf(false), finishResults)
    }

    @Test
    fun successfulPlayInvocationSurvivesStateStoreRecreation() {
        val backing = ReviewStateBacking(
            eligibleState().copy(successfullyRequestedVersions = listOf(PREVIOUS_VERSION))
        )
        val firstProcessStore = BackedStateStore(backing)

        requestAndroidReviewPrompt(
            stateStore = firstProcessStore,
            appVersion = APP_VERSION,
            requester = AndroidReviewRequester { onComplete -> onComplete(true) }
        )

        assertEquals(1, backing.durableSuccessWrites)
        val restartedProcessStore = BackedStateStore(backing)
        assertEquals(
            listOf(PREVIOUS_VERSION, APP_VERSION),
            restartedProcessStore.read().successfullyRequestedVersions
        )
        val nextDecision = ReviewPromptPolicy.recordSuccessfulForecast(
            currentState = restartedProcessStore.read(),
            appVersion = APP_VERSION,
            forecastId = 4L,
            localDay = "2026-08-30"
        )
        assertFalse(nextDecision.shouldRequestReview)
    }

    @Test
    fun failedDurableWriteLeavesVersionEligibleAndFinishesCleanly() {
        val backing = ReviewStateBacking(
            state = eligibleState(),
            persistSuccess = false
        )
        val stateStore = BackedStateStore(backing)
        val finishResults = mutableListOf<Boolean>()

        requestAndroidReviewPrompt(
            stateStore = stateStore,
            appVersion = APP_VERSION,
            requester = AndroidReviewRequester { onComplete -> onComplete(true) },
            onFinished = { finishResults += it }
        )

        assertTrue(stateStore.read().successfullyRequestedVersions.isEmpty())
        assertEquals(1, backing.durableSuccessWrites)
        assertEquals(listOf(false), finishResults)
    }

    @Test
    fun persistenceExceptionStillReleasesTheInFlightRequest() {
        val backing = ReviewStateBacking(
            state = eligibleState(),
            throwOnPersistence = true
        )
        val finishResults = mutableListOf<Boolean>()

        requestAndroidReviewPrompt(
            stateStore = BackedStateStore(backing),
            appVersion = APP_VERSION,
            requester = AndroidReviewRequester { onComplete -> onComplete(true) },
            onFinished = { finishResults += it }
        )

        assertTrue(backing.state.successfullyRequestedVersions.isEmpty())
        assertEquals(listOf(false), finishResults)
    }

    @Test
    fun activityMustBeResumedAndNeitherFinishingNorDestroyed() {
        assertTrue(
            isAndroidReviewActivityEligible(
                isFinishing = false,
                isDestroyed = false,
                lifecycleResumed = true
            )
        )
        assertFalse(
            isAndroidReviewActivityEligible(
                isFinishing = true,
                isDestroyed = false,
                lifecycleResumed = true
            )
        )
        assertFalse(
            isAndroidReviewActivityEligible(
                isFinishing = false,
                isDestroyed = true,
                lifecycleResumed = true
            )
        )
        assertFalse(
            isAndroidReviewActivityEligible(
                isFinishing = false,
                isDestroyed = false,
                lifecycleResumed = false
            )
        )
    }

    private class ReviewStateBacking(
        var state: ReviewPromptPolicyState,
        var durableSuccessWrites: Int = 0,
        val persistSuccess: Boolean = true,
        val throwOnPersistence: Boolean = false
    )

    private class BackedStateStore(private val backing: ReviewStateBacking) :
        ReviewPromptPolicyStateStore {
        override fun read(): ReviewPromptPolicyState = backing.state

        override fun write(state: ReviewPromptPolicyState) {
            backing.state = state
        }

        override fun persistRequestSuccess(state: ReviewPromptPolicyState): Boolean {
            backing.durableSuccessWrites += 1
            if (backing.throwOnPersistence) error("persistence failure")
            if (backing.persistSuccess) backing.state = state
            return backing.persistSuccess
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
