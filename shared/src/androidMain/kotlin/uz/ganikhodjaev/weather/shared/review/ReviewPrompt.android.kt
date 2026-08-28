package uz.ganikhodjaev.weather.shared.review

import android.content.Context
import android.content.SharedPreferences
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import com.google.android.play.core.review.ReviewManagerFactory
import java.util.concurrent.atomic.AtomicBoolean
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun considerReviewPrompt(
    platformContext: PlatformContext,
    successfulForecastId: Long
) {
    val context = platformContext.applicationContext
    val appVersion = runCatching {
        context.packageManager.getPackageInfo(context.packageName, 0).versionName
    }.getOrNull().orEmpty()
    if (appVersion.isBlank()) return

    val preferences = context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
    val stateStore = AndroidReviewPromptPolicyStateStore(preferences)
    val decision = ReviewPromptPolicy.recordSuccessfulForecast(
        currentState = stateStore.read(),
        appVersion = appVersion,
        forecastId = successfulForecastId,
        localDay = currentLocalCalendarDay()
    )
    stateStore.write(decision.state)
    if (!decision.shouldRequestReview || !reviewRequestInFlight.compareAndSet(false, true)) return

    requestAndroidReviewPrompt(
        stateStore = stateStore,
        appVersion = appVersion,
        requester = PlayReviewRequester(platformContext),
        onFinished = { reviewRequestInFlight.set(false) }
    )
}

internal fun interface AndroidReviewRequester {
    fun requestReview(onComplete: (Boolean) -> Unit)
}

internal fun requestAndroidReviewPrompt(
    stateStore: ReviewPromptPolicyStateStore,
    appVersion: String,
    requester: AndroidReviewRequester,
    onFinished: (Boolean) -> Unit = {}
) {
    val completionHandled = AtomicBoolean(false)
    fun finish(requestSucceeded: Boolean) {
        if (!completionHandled.compareAndSet(false, true)) return
        val successPersisted = try {
            requestSucceeded && persistSuccessfulReviewRequest(stateStore, appVersion)
        } catch (_: Throwable) {
            false
        }
        onFinished(successPersisted)
    }

    try {
        requester.requestReview(::finish)
    } catch (_: Throwable) {
        finish(false)
    }
}

private class PlayReviewRequester(private val platformContext: PlatformContext) :
    AndroidReviewRequester {
    override fun requestReview(onComplete: (Boolean) -> Unit) {
        val activity = platformContext.activity ?: run {
            onComplete(false)
            return
        }
        if (!activity.isEligibleForReviewLaunch()) {
            onComplete(false)
            return
        }
        val manager = runCatching { ReviewManagerFactory.create(activity) }.getOrElse {
            onComplete(false)
            return
        }
        val requestTask = runCatching { manager.requestReviewFlow() }.getOrElse {
            onComplete(false)
            return
        }
        requestTask.addOnCompleteListener { completedRequest ->
            if (!completedRequest.isSuccessful) {
                onComplete(false)
                return@addOnCompleteListener
            }
            if (!activity.isEligibleForReviewLaunch()) {
                onComplete(false)
                return@addOnCompleteListener
            }
            val launchTask = runCatching {
                manager.launchReviewFlow(activity, completedRequest.result)
            }.getOrElse {
                onComplete(false)
                return@addOnCompleteListener
            }
            launchTask.addOnCompleteListener { completedLaunch ->
                // A successful task proves only that Play accepted the invocation.
                // Google still controls whether any review dialog is displayed.
                onComplete(completedLaunch.isSuccessful)
            }
        }
    }
}

private fun android.app.Activity.isEligibleForReviewLaunch(): Boolean {
    val lifecycleResumed = (this as? LifecycleOwner)
        ?.lifecycle
        ?.currentState
        ?.isAtLeast(Lifecycle.State.RESUMED) == true
    return isAndroidReviewActivityEligible(
        isFinishing = isFinishing,
        isDestroyed = isDestroyed,
        lifecycleResumed = lifecycleResumed
    )
}

internal fun isAndroidReviewActivityEligible(
    isFinishing: Boolean,
    isDestroyed: Boolean,
    lifecycleResumed: Boolean
): Boolean = !isFinishing && !isDestroyed && lifecycleResumed

private class AndroidReviewPromptPolicyStateStore(private val preferences: SharedPreferences) :
    ReviewPromptPolicyStateStore {
    override fun read() = ReviewPromptPolicyState(
        trackedVersion = preferences.getString(KEY_TRACKED_VERSION, "").orEmpty(),
        successfulForecastCount = preferences.getInt(KEY_SUCCESSFUL_FORECAST_COUNT, 0),
        successfulLocalDays = preferences.getString(KEY_SUCCESSFUL_LOCAL_DAYS, "")
            .orEmpty()
            .split(DAY_SEPARATOR)
            .filter(String::isNotBlank)
            .toSet(),
        lastCountedForecastId = preferences
            .getLong(KEY_LAST_COUNTED_FORECAST_ID, NO_FORECAST_ID)
            .takeUnless { it == NO_FORECAST_ID },
        successfullyRequestedVersions = normalizeSuccessfullyRequestedVersions(
            storedVersions = preferences.getString(KEY_REVIEWED_VERSION_HISTORY, "")
                .orEmpty()
                .split(VERSION_SEPARATOR),
            legacyVersion = preferences.getString(KEY_REVIEWED_VERSION, null)
        )
    )

    override fun write(state: ReviewPromptPolicyState) {
        preferences.edit().putReviewPromptPolicyState(state).apply()
    }

    override fun persistRequestSuccess(state: ReviewPromptPolicyState): Boolean {
        val previousState = read()
        val persisted = preferences.edit().putReviewPromptPolicyState(state).commit()
        if (!persisted) {
            // SharedPreferences may update its in-memory map even when the disk
            // write fails. Restore eligibility so this version can retry.
            preferences.edit().putReviewPromptPolicyState(previousState).apply()
        }
        return persisted
    }
}

private fun SharedPreferences.Editor.putReviewPromptPolicyState(
    state: ReviewPromptPolicyState
): SharedPreferences.Editor = putString(KEY_TRACKED_VERSION, state.trackedVersion)
    .putInt(KEY_SUCCESSFUL_FORECAST_COUNT, state.successfulForecastCount)
    .putString(KEY_SUCCESSFUL_LOCAL_DAYS, state.successfulLocalDays.joinToString(DAY_SEPARATOR))
    .putLong(KEY_LAST_COUNTED_FORECAST_ID, state.lastCountedForecastId ?: NO_FORECAST_ID)
    .putString(
        KEY_REVIEWED_VERSION_HISTORY,
        state.successfullyRequestedVersions.joinToString(VERSION_SEPARATOR)
    )
    // Keep the legacy key synchronized so rollback to an older binary still
    // blocks the most recently invoked version.
    .putString(KEY_REVIEWED_VERSION, state.successfullyRequestedVersions.lastOrNull())

private val reviewRequestInFlight = AtomicBoolean(false)
private const val PREFERENCES_NAME = "nimbo_review_policy"
private const val KEY_TRACKED_VERSION = "tracked_version"
private const val KEY_SUCCESSFUL_FORECAST_COUNT = "successful_forecast_count"
private const val KEY_SUCCESSFUL_LOCAL_DAYS = "successful_local_days"
private const val KEY_LAST_COUNTED_FORECAST_ID = "last_counted_forecast_id"
private const val KEY_REVIEWED_VERSION = "reviewed_version"
private const val KEY_REVIEWED_VERSION_HISTORY = "reviewed_version_history"
private const val DAY_SEPARATOR = "|"
private const val VERSION_SEPARATOR = "\u001F"
private const val NO_FORECAST_ID = Long.MIN_VALUE
