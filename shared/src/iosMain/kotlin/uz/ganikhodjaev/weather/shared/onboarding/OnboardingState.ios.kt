package uz.ganikhodjaev.weather.shared.onboarding

import platform.Foundation.NSUserDefaults
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun createOnboardingStateStore(
    platformContext: PlatformContext
): OnboardingStateStore {
    val preferences = NSUserDefaults.standardUserDefaults
    return object : OnboardingStateStore {
        override fun read(): OnboardingState = OnboardingState(
            hasCompletedFirstForecast = preferences.boolForKey(KEY_COMPLETED_FIRST_FORECAST),
            // The legacy "shown" bit was written before UI render and cannot prove an action.
            hasAcknowledgedFirstForecastTip = preferences.boolForKey(
                KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP
            )
        )

        override fun write(state: OnboardingState) {
            preferences.setBool(
                state.hasCompletedFirstForecast,
                forKey = KEY_COMPLETED_FIRST_FORECAST
            )
            preferences.setBool(
                state.hasAcknowledgedFirstForecastTip,
                forKey = KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP
            )
        }
    }
}

private const val KEY_COMPLETED_FIRST_FORECAST = "onboarding_completed_first_forecast"
private const val KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP =
    "onboarding_acknowledged_first_forecast_tip"
