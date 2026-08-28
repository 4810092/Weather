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
    val successfullyRequestedVersion: String? = null
)

internal data class ReviewPromptPolicyDecision(
    val state: ReviewPromptPolicyState,
    val shouldRequestReview: Boolean
)

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
                successfullyRequestedVersion = currentState.successfullyRequestedVersion
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
                updatedState.successfullyRequestedVersion != appVersion
        )
    }

    fun markRequestSucceeded(
        currentState: ReviewPromptPolicyState,
        appVersion: String
    ): ReviewPromptPolicyState = currentState.copy(
        successfullyRequestedVersion = appVersion
    )
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
