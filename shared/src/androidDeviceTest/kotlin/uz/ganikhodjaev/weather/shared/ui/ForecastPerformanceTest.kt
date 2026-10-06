package uz.ganikhodjaev.weather.shared.ui

import android.os.Build
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.captureToImage
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeLeft
import androidx.compose.ui.test.swipeRight
import androidx.compose.ui.test.v2.runAndroidComposeUiTest
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import kotlin.test.Test

/** Fixed-data rendering benchmark; deliberately excludes provider latency and process startup. */
@OptIn(ExperimentalTestApi::class)
class ForecastPerformanceTest {
    @Test
    fun fixedForecastRenderScrollAndRefresh() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            val base = contentState()
            val current = base.weather.current
            var state by mutableStateOf(
                base.copy(
                    weather = base.weather.copy(
                        timeline = (-24..24).map { offset ->
                            current.copy(
                                epochSeconds = current.epochSeconds + offset * 3_600,
                                temperatureC = 24.0 + (offset % 6),
                                precipitationProbability = if (offset in 3..6) 70 else 10,
                                precipitationMm = if (offset in 3..6) 0.6 else 0.0
                            )
                        }
                    )
                )
            )
            val start = System.nanoTime()
            setContent {
                TestWeatherScreen(state = state, onRetry = {
                    state = state.copy(isRefreshing = true)
                })
            }
            waitForIdle()
            val firstRenderMs = (System.nanoTime() - start) / 1_000_000.0
            val context = InstrumentationRegistry.getInstrumentation().targetContext
            val directory = File(
                context.externalMediaDirs.first(),
                "additional_test_output"
            ).apply { mkdirs() }
            saveGlassScreenshot(
                "performance-first-screen",
                if (Build.VERSION.SDK_INT >=
                    26
                ) {
                    onRoot().captureToImage().asAndroidBitmap()
                } else {
                    null
                }
            )
            val refreshMs = (1..5).map {
                val refreshStart = System.nanoTime()
                onNodeWithContentDescription("Refresh").performClick()
                waitForIdle()
                runOnIdle { state = state.copy(isRefreshing = false) }
                waitForIdle()
                (System.nanoTime() - refreshStart) / 1_000_000.0
            }
            onNodeWithTag("hourly-forecast").performScrollTo()
            waitForIdle()
            val instrumentation = InstrumentationRegistry.getInstrumentation()
            fun shell(command: String): String =
                android.os.ParcelFileDescriptor.AutoCloseInputStream(
                    instrumentation.uiAutomation.executeShellCommand(command)
                ).bufferedReader().use { it.readText() }
            val packageName = instrumentation.targetContext.packageName
            shell("dumpsys gfxinfo $packageName reset")
            repeat(8) { index ->
                onNodeWithTag("hourly-forecast").performTouchInput {
                    if (index % 2 ==
                        0
                    ) {
                        swipeLeft(durationMillis = 400)
                    } else {
                        swipeRight(durationMillis = 400)
                    }
                }
                waitForIdle()
            }
            File(
                directory,
                "performance-frames.txt"
            ).writeText(shell("dumpsys gfxinfo $packageName framestats"))
            File(directory, "performance-render.json").writeText(
                """{"clock":$TEST_EPOCH_SECONDS,"locale":"en-US","fontScale":1,"theme":"light","api":${Build.VERSION.SDK_INT},"model":"${Build.MODEL}","firstComposeRenderMs":$firstRenderMs,"refreshRenderMs":${refreshMs.joinToString(
                    prefix = "[",
                    postfix = "]"
                )}}"""
            )
        }
    }
}
