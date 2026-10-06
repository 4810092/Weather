package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.click
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeDown
import androidx.compose.ui.test.swipeLeft
import androidx.compose.ui.test.v2.runAndroidComposeUiTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertTrue
import uz.ganikhodjaev.weather.shared.model.DailyForecast
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.presentation.UiMessage
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState

@OptIn(ExperimentalTestApi::class)
class PremiumForecastUiTest {
    @Test
    fun deterministicVisualMatrix() {
        val cases = listOf(
            Triple("ru", ThemePreference.Light, 1f),
            Triple("uz", ThemePreference.Dark, 1f),
            Triple("ar", ThemePreference.Light, 1f),
            Triple("ru", ThemePreference.Dark, 2f)
        )
        cases.forEach { (locale, theme, scale) ->
            withTestLocale(locale) {
                runAndroidComposeUiTest<NimboLocaleTestActivity> {
                    var state by mutableStateOf(
                        premiumState().let { base ->
                            if (scale > 1f) {
                                base.copy(
                                    weather = base.weather.copy(
                                        location =
                                        base.weather.location.copy(
                                            name = "Санкт-Петербург — Василеостровский район"
                                        )
                                    )
                                )
                            } else {
                                base
                            }
                        }
                    )
                    setContent { TestWeatherScreen(state, scale, theme) }
                    onNodeWithTag("current-temperature").assertIsDisplayed()
                    if (scale == 1f) {
                        onNodeWithTag("hourly-forecast").assertIsDisplayed()
                        val plot = onNodeWithTag(
                            "hourly-forecast"
                        ).fetchSemanticsNode().boundsInRoot
                        val viewport = onRoot().fetchSemanticsNode().boundsInRoot
                        assertTrue(
                            plot.top < viewport.bottom - 100,
                            "Hourly plot must begin on first screen"
                        )
                    }
                    captureFeedbackScreenshot(
                        "premium-$locale-${theme.name.lowercase()}-${scale.toInt()}"
                    )
                    runOnIdle {
                        state = state.copy(
                            weather = state.weather.copy(
                                isStale = true,
                                fetchedAtEpochSeconds = TEST_EPOCH_SECONDS - 86_400
                            ),
                            refreshMessage = UiMessage.RefreshFailedShowingSaved
                        )
                    }
                    captureFeedbackScreenshot("premium-$locale-offline-${scale.toInt()}")
                }
            }
        }
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                var state: WeatherUiState by mutableStateOf(premiumState(rain = true))
                setContent { TestWeatherScreen(state) }
                onNodeWithTag("outside-guidance").performScrollTo()
                onNodeWithText("No suitable two-hour window today").assertIsDisplayed()
                captureFeedbackScreenshot("premium-rain-all-day")
                runOnIdle { state = WeatherUiState.EmptyError(UiMessage.WeatherUnavailable) }
                captureFeedbackScreenshot("premium-error")
                runOnIdle { state = WeatherUiState.ChooseLocation(isOnboarding = true) }
                captureFeedbackScreenshot("premium-first-launch")
                mainClock.autoAdvance = false
                runOnIdle { state = WeatherUiState.Loading }
                mainClock.advanceTimeBy(32)
                captureFeedbackScreenshot("premium-loading")
                mainClock.autoAdvance = true
            }
        }
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                val night = TEST_EPOCH_SECONDS + 10 * 3_600
                setContent {
                    TestWeatherScreen(
                        premiumState(now = night),
                        theme = ThemePreference.Dark,
                        nowEpochSeconds = night
                    )
                }
                captureFeedbackScreenshot("premium-night")
            }
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                val base = premiumState()
                val partial = base.copy(
                    weather = base.weather.copy(
                        current = base.weather.current.copy(
                            temperatureC = -5.0,
                            apparentTemperatureC = -8.0
                        ),
                        timeline = base.weather.timeline
                            .filterIndexed { index, _ -> index != 25 }
                            .map { it.copy(temperatureC = -5.0, apparentTemperatureC = -8.0) }
                    )
                )
                setContent { TestWeatherScreen(partial) }
                captureFeedbackScreenshot("premium-negative-gap")
            }
        }
    }

    @Test
    fun swipeBrowsesWhileTapAndHoldDragChooseHours() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            setContent { TestWeatherScreen(premiumState()) }
            fun selectedTime() = onNodeWithTag("selected-hour-time").fetchSemanticsNode()
                .config[SemanticsProperties.Text].single().text
            val initial = selectedTime()
            onNodeWithTag("hourly-forecast").performScrollTo().performTouchInput {
                swipeLeft(durationMillis = 400)
            }
            waitForIdle()
            assertEquals(initial, selectedTime(), "Scrolling must not change the chosen hour")
            onNodeWithTag("hourly-forecast").performTouchInput { click(center) }
            waitForIdle()
            val tapped = selectedTime()
            assertNotEquals(initial, tapped)
            onNodeWithTag("hourly-forecast").performTouchInput {
                down(center)
                advanceEventTime(700)
                repeat(12) { step ->
                    moveTo(Offset(width * (0.5f + (step + 1) * 0.025f), center.y), delayMillis = 25)
                }
                up()
            }
            waitForIdle()
            assertNotEquals(tapped, selectedTime(), "Holding and dragging must select another hour")
            onNodeWithText("Current hour").performScrollTo().performClick()
            waitForIdle()
            assertEquals(initial, selectedTime())
        }
    }

    @Test
    fun refreshAndSettingsKeepUsefulContentAndVerticalPosition() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            var state by mutableStateOf(premiumState())
            var refreshes = 0
            setContent {
                TestWeatherScreen(state, onRetry = {
                    refreshes++
                    state = state.copy(isRefreshing = true)
                })
            }
            onNodeWithTag("forecast-scroll").performTouchInput {
                swipeDown(startY = 30f, endY = height * 0.7f, durationMillis = 500)
            }
            waitForIdle()
            runOnIdle { assertEquals(1, refreshes) }
            onNodeWithTag("current-temperature").assertIsDisplayed()
            runOnIdle { state = state.copy(isRefreshing = false) }
            onNodeWithTag("outside-guidance").performScrollTo()
            val before = onNodeWithTag("outside-guidance").fetchSemanticsNode().positionInRoot.y
            onNodeWithContentDescription("Settings").performClick()
            onNodeWithText("Back").performClick()
            waitForIdle()
            val after = onNodeWithTag("outside-guidance").fetchSemanticsNode().positionInRoot.y
            assertEquals(before, after, "Returning from settings must restore vertical scroll")
        }
    }
}

internal fun premiumState(
    rain: Boolean = false,
    now: Long = TEST_EPOCH_SECONDS
): WeatherUiState.Content {
    val base = contentState()
    val current = base.weather.current.copy(
        epochSeconds = now,
        fetchedAtEpochSeconds = now,
        weatherCode = if (rain) 61 else 0,
        precipitationProbability = if (rain) 97 else 10,
        precipitationMm = if (rain) 1.0 else 0.0
    )
    val midnight = (now + 18_000) / 86_400 * 86_400 - 18_000
    return base.copy(
        weather = base.weather.copy(
            current = current,
            fetchedAtEpochSeconds = now,
            timeline = (-24..24).map { offset ->
                current.copy(
                    epochSeconds = current.epochSeconds + offset * 3_600,
                    temperatureC = 24.0 + (offset % 8),
                    apparentTemperatureC = 24.0 + (offset % 8),
                    weatherCode = if (rain || offset in 3..6) 61 else 0,
                    precipitationProbability = if (rain) {
                        97
                    } else if (offset in 3..6) {
                        70
                    } else {
                        10
                    },
                    precipitationMm = if (rain) {
                        1.0
                    } else if (offset in 3..6) {
                        0.6
                    } else {
                        0.0
                    }
                )
            },
            dailyForecast = (-1..1).map { day ->
                val start = midnight + day * 86_400
                DailyForecast(
                    start, 0, 28.0, 16.0, 28.0, 16.0, 10, 0.0, 8.0, 12.0, 2.0,
                    start + 6 * 3_600, start + 18 * 3_600, now
                )
            }
        )
    )
}
