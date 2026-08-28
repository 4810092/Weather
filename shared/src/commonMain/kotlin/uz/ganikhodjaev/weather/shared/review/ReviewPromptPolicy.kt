package uz.ganikhodjaev.weather.shared.review

import kotlin.time.Clock
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.PlatformContext

internal data class ReviewPromptPolicyState(
    val trackedVersion: String = "",
    val successfulForecastCount: Int = 0,
    val successfulLocalDays: Set<String> = emptySet(),
    val lastCountedForecastId: Long? = null,
    val successfullyRequestedVersions: List<String> = emptyList()
)

internal data class ReviewPromptPolicyDecision(
    val state: ReviewPromptPolicyState,
    val shouldRequestReview: Boolean
)

internal interface ReviewPromptPolicyStateStore {
    fun read(): ReviewPromptPolicyState

    fun write(state: ReviewPromptPolicyState)

    fun persistRequestSuccess(state: ReviewPromptPolicyState): Boolean {
        write(state)
        return true
    }
}

internal object ReviewPromptPolicy {
    fun recordSuccessfulForecast(
        currentState: ReviewPromptPolicyState,
        appVersion: String,
        forecastId: Long,
        localDay: String
    ): ReviewPromptPolicyDecision {
        require(appVersion.isNotBlank()) { "App version is required" }
        require(localDay.isNotBlank()) { "Local calendar day is required" }

        val versionState = if (currentState.trackedVersion == appVersion) {
            currentState
        } else {
            ReviewPromptPolicyState(
                trackedVersion = appVersion,
                successfullyRequestedVersions = currentState.successfullyRequestedVersions
            )
        }
        val updatedState = if (versionState.lastCountedForecastId == forecastId) {
            versionState
        } else {
            versionState.copy(
                successfulForecastCount = minOf(
                    versionState.successfulForecastCount + 1,
                    MINIMUM_SUCCESSFUL_FORECASTS
                ),
                successfulLocalDays = (versionState.successfulLocalDays + localDay)
                    .take(MINIMUM_DISTINCT_DAYS)
                    .toSet(),
                lastCountedForecastId = forecastId
            )
        }
        return ReviewPromptPolicyDecision(
            state = updatedState,
            shouldRequestReview = updatedState.successfulForecastCount >=
                MINIMUM_SUCCESSFUL_FORECASTS &&
                updatedState.successfulLocalDays.size >= MINIMUM_DISTINCT_DAYS &&
                appVersion !in updatedState.successfullyRequestedVersions
        )
    }

    fun markRequestSucceeded(
        currentState: ReviewPromptPolicyState,
        appVersion: String
    ): ReviewPromptPolicyState = currentState.copy(
        successfullyRequestedVersions = normalizeSuccessfullyRequestedVersions(
            currentState.successfullyRequestedVersions + appVersion
        )
    )
}

internal fun normalizeSuccessfullyRequestedVersions(
    storedVersions: Iterable<String>,
    legacyVersion: String? = null
): List<String> {
    val ordered = mutableListOf<String>()
    fun append(version: String?) {
        if (version.isNullOrBlank()) return
        ordered.remove(version)
        ordered += version
    }

    storedVersions.forEach(::append)
    append(legacyVersion)
    return ordered
}

internal fun persistSuccessfulReviewRequest(
    stateStore: ReviewPromptPolicyStateStore,
    appVersion: String
): Boolean {
    val updatedState = ReviewPromptPolicy.markRequestSucceeded(
        currentState = stateStore.read(),
        appVersion = appVersion
    )
    return stateStore.persistRequestSuccess(updatedState)
}

internal fun currentLocalCalendarDay(): String = Clock.System.now()
    .toLocalDateTime(TimeZone.currentSystemDefault())
    .date
    .toString()

internal expect fun considerReviewPrompt(
    platformContext: PlatformContext,
    successfulForecastId: Long
)

private const val MINIMUM_SUCCESSFUL_FORECASTS = 3
private const val MINIMUM_DISTINCT_DAYS = 2
