package uz.ganikhodjaev.weather.shared.review

import platform.Foundation.NSBundle
import platform.Foundation.NSUserDefaults
import platform.StoreKit.SKStoreReviewController
import platform.UIKit.UIApplication
import platform.UIKit.UIApplicationState
import platform.UIKit.UISceneActivationStateForegroundActive
import platform.UIKit.UIWindowScene
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun considerReviewPrompt(
    platformContext: PlatformContext,
    successfulForecastId: Long
) {
    val appVersion = NSBundle.mainBundle.objectForInfoDictionaryKey(
        "CFBundleShortVersionString"
    ) as? String ?: return
    val stateStore = IosReviewPromptPolicyStateStore(NSUserDefaults(suiteName = APP_GROUP))
    val decision = ReviewPromptPolicy.recordSuccessfulForecast(
        currentState = stateStore.read(),
        appVersion = appVersion,
        forecastId = successfulForecastId,
        localDay = currentLocalCalendarDay()
    )
    stateStore.write(decision.state)
    if (decision.shouldRequestReview) {
        requestIosReviewPrompt(
            stateStore = stateStore,
            appVersion = appVersion,
            requester = StoreKitReviewRequester
        )
    }
}

internal fun interface IosReviewRequester {
    fun requestReviewWhenForeground(): Boolean
}

internal fun requestIosReviewPrompt(
    stateStore: ReviewPromptPolicyStateStore,
    appVersion: String,
    requester: IosReviewRequester
): Boolean {
    val requestInvoked = runCatching {
        requester.requestReviewWhenForeground()
    }.getOrDefault(false)
    if (!requestInvoked) return false

    // StoreKit decides whether a dialog is displayed. A true result records only
    // that a platform review request was invoked while the app was foreground-active.
    return persistSuccessfulReviewRequest(stateStore, appVersion)
}

private object StoreKitReviewRequester : IosReviewRequester {
    @Suppress("DEPRECATION")
    override fun requestReviewWhenForeground(): Boolean {
        val application = UIApplication.sharedApplication
        val foregroundScene = application.connectedScenes
            .asSequence()
            .filterIsInstance<UIWindowScene>()
            .firstOrNull { it.activationState == UISceneActivationStateForegroundActive }
        return when (
            selectIosReviewRequestPath(
                isApplicationActive = application.applicationState ==
                    UIApplicationState.UIApplicationStateActive,
                hasForegroundWindowScene = foregroundScene != null,
                hasLegacyKeyWindow = application.keyWindow != null
            )
        ) {
            IosReviewRequestPath.ForegroundWindowScene -> {
                SKStoreReviewController.requestReviewInScene(requireNotNull(foregroundScene))
                true
            }
            IosReviewRequestPath.LegacyKeyWindow -> {
                // Nimbo intentionally uses the legacy AppDelegate window lifecycle on iOS 15+.
                // That lifecycle has no UIWindowScene, so StoreKit's legacy request API is the
                // only in-app review path that can present without a scene migration.
                SKStoreReviewController.requestReview()
                true
            }
            null -> false
        }
    }
}

internal enum class IosReviewRequestPath {
    ForegroundWindowScene,
    LegacyKeyWindow
}

internal fun selectIosReviewRequestPath(
    isApplicationActive: Boolean,
    hasForegroundWindowScene: Boolean,
    hasLegacyKeyWindow: Boolean
): IosReviewRequestPath? {
    if (!isApplicationActive) return null
    if (hasForegroundWindowScene) return IosReviewRequestPath.ForegroundWindowScene
    if (hasLegacyKeyWindow) return IosReviewRequestPath.LegacyKeyWindow
    return null
}

private class IosReviewPromptPolicyStateStore(private val preferences: NSUserDefaults) :
    ReviewPromptPolicyStateStore {
    override fun read() = ReviewPromptPolicyState(
        trackedVersion = preferences.stringForKey(KEY_TRACKED_VERSION).orEmpty(),
        successfulForecastCount = preferences.integerForKey(KEY_SUCCESSFUL_FORECAST_COUNT).toInt(),
        successfulLocalDays = preferences.stringForKey(KEY_SUCCESSFUL_LOCAL_DAYS)
            .orEmpty()
            .split(DAY_SEPARATOR)
            .filter(String::isNotBlank)
            .toSet(),
        lastCountedForecastId = preferences.objectForKey(KEY_LAST_COUNTED_FORECAST_ID)?.let {
            preferences.integerForKey(KEY_LAST_COUNTED_FORECAST_ID)
        },
        successfullyRequestedVersions = normalizeSuccessfullyRequestedVersions(
            storedVersions = preferences.stringForKey(KEY_REVIEWED_VERSION_HISTORY)
                .orEmpty()
                .split(VERSION_SEPARATOR),
            legacyVersion = preferences.stringForKey(KEY_REVIEWED_VERSION)
        )
    )

    override fun write(state: ReviewPromptPolicyState) {
        preferences.writeReviewPromptPolicyState(state)
    }
}

private fun NSUserDefaults.writeReviewPromptPolicyState(state: ReviewPromptPolicyState) {
    setObject(state.trackedVersion, forKey = KEY_TRACKED_VERSION)
    setInteger(state.successfulForecastCount.toLong(), forKey = KEY_SUCCESSFUL_FORECAST_COUNT)
    setObject(
        state.successfulLocalDays.joinToString(DAY_SEPARATOR),
        forKey = KEY_SUCCESSFUL_LOCAL_DAYS
    )
    state.lastCountedForecastId?.let {
        setInteger(it, forKey = KEY_LAST_COUNTED_FORECAST_ID)
    } ?: removeObjectForKey(KEY_LAST_COUNTED_FORECAST_ID)
    state.successfullyRequestedVersions.takeIf { it.isNotEmpty() }?.let { versions ->
        setObject(versions.joinToString(VERSION_SEPARATOR), forKey = KEY_REVIEWED_VERSION_HISTORY)
        // Keep the legacy key synchronized so rollback to an older binary still
        // blocks the most recently invoked version.
        setObject(versions.last(), forKey = KEY_REVIEWED_VERSION)
    } ?: removeObjectForKey(KEY_REVIEWED_VERSION)
    if (state.successfullyRequestedVersions.isEmpty()) {
        removeObjectForKey(KEY_REVIEWED_VERSION_HISTORY)
    }
}

private const val APP_GROUP = "group.uz.ganikhodjaev.weather"
private const val KEY_TRACKED_VERSION = "tracked_version"
private const val KEY_SUCCESSFUL_FORECAST_COUNT = "successful_forecast_count"
private const val KEY_SUCCESSFUL_LOCAL_DAYS = "successful_local_days"
private const val KEY_LAST_COUNTED_FORECAST_ID = "last_counted_forecast_id"
private const val KEY_REVIEWED_VERSION = "reviewed_version"
private const val KEY_REVIEWED_VERSION_HISTORY = "reviewed_version_history"
private const val DAY_SEPARATOR = "|"
private const val VERSION_SEPARATOR = "\u001F"
