package uz.ganikhodjaev.weather.shared.onboarding

import android.content.Context
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual fun createOnboardingStateStore(
    platformContext: PlatformContext
): OnboardingStateStore {
    val preferences = platformContext.applicationContext.getSharedPreferences(
        PREFERENCES_NAME,
        Context.MODE_PRIVATE
    )
    return object : OnboardingStateStore {
        override fun read(): OnboardingState = OnboardingState(
            hasCompletedFirstForecast = preferences.getBoolean(
                KEY_COMPLETED_FIRST_FORECAST,
                false
            ),
            // The legacy "shown" bit was written before UI render and cannot prove an action.
            hasAcknowledgedFirstForecastTip = preferences.getBoolean(
                KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP,
                false
            )
        )

        override fun write(state: OnboardingState) {
            // apply() updates the in-process value immediately and schedules disk I/O,
            // avoiding a synchronous preferences commit on the UI callback path.
            preferences.edit()
                .putBoolean(KEY_COMPLETED_FIRST_FORECAST, state.hasCompletedFirstForecast)
                .putBoolean(
                    KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP,
                    state.hasAcknowledgedFirstForecastTip
                )
                .apply()
        }
    }
}

private const val PREFERENCES_NAME = "nimbo_preferences"
private const val KEY_COMPLETED_FIRST_FORECAST = "onboarding_completed_first_forecast"
private const val KEY_ACKNOWLEDGED_FIRST_FORECAST_TIP =
    "onboarding_acknowledged_first_forecast_tip"
