package uz.ganikhodjaev.weather.shared.ui

import android.os.LocaleList
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertHasClickAction
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.v2.runComposeUiTest
import androidx.compose.ui.text.intl.Locale as ComposeLocale
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import java.util.Locale as JavaLocale
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import uz.ganikhodjaev.weather.shared.layoutDirectionForLanguage
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.ThemePreference
import uz.ganikhodjaev.weather.shared.model.UnitPreference
import uz.ganikhodjaev.weather.shared.model.UnitSystem
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.onboarding.UzbekistanQuickLocations
import uz.ganikhodjaev.weather.shared.presentation.UiMessage
import uz.ganikhodjaev.weather.shared.presentation.WeatherUiState

@OptIn(ExperimentalTestApi::class)
class WeatherScreenAndroidUiTest {
    @Test
    fun onboardingDoesNotRequestLocationUntilTapAndOffersPermissionFreeSearch() =
        withTestLocale("en-US") {
            runComposeUiTest {
                var locationRequests = 0
                var selectedLocation: Location? = null
                var state by mutableStateOf(
                    WeatherUiState.ChooseLocation(
                        isOnboarding = true,
                        quickLocations = UzbekistanQuickLocations.all
                    )
                )

                setContent {
                    TestWeatherScreen(
                        state = state,
                        onSearchQueryChanged = { query ->
                            state = state.copy(
                                query = query,
                                results = if (query.length >= 2) listOf(BUKHARA) else emptyList(),
                                message = null
                            )
                        },
                        onLocationSelected = { selectedLocation = it },
                        onUseDeviceLocation = {
                            locationRequests += 1
                            state = state.copy(message = UiMessage.LocationPermissionDenied)
                        }
                    )
                }

                onNodeWithText("Find the best time to go outside.").assertIsDisplayed()
                onNodeWithText("Tashkent").assertIsDisplayed().assertHasClickAction()
                onNodeWithText("Use my approximate location")
                    .performScrollTo()
                    .assertIsDisplayed()
                    .assertHasClickAction()
                runOnIdle { assertEquals(0, locationRequests) }

                onNodeWithText("Use my approximate location").performClick()
                onNodeWithText("Location access wasn’t granted. Search for a city instead.")
                    .performScrollTo()
                    .assertIsDisplayed()
                runOnIdle { assertEquals(1, locationRequests) }

                onNode(hasSetTextAction()).performScrollTo().performClick().performTextInput("Bu")
                onNodeWithContentDescription("Bukhara, Uzbekistan")
                    .performScrollTo()
                    .assertIsDisplayed()
                    .assertHasClickAction()
                    .performClick()
                runOnIdle { assertEquals(BUKHARA, selectedLocation) }
            }
        }

    @Test
    fun successfulForecastExposesTipAndAccessibleHeaderActions() = withTestLocale("en-US") {
        runComposeUiTest {
            var refreshes = 0
            var changes = 0
            var shares = 0
            var addLocationTips = 0
            var dismissedTips = 0

            setContent {
                TestWeatherScreen(
                    state = contentState(showFirstForecastTip = true),
                    onRetry = { refreshes += 1 },
                    onChangeLocation = { changes += 1 },
                    onShareText = { shares += 1 },
                    onAddLocationFromFirstForecastTip = { addLocationTips += 1 },
                    onDismissFirstForecastTip = { dismissedTips += 1 }
                )
            }

            onNodeWithText("Tashkent").assertIsDisplayed()
            onNodeWithContentDescription("Share weather")
                .assertIsDisplayed()
                .assertHasClickAction()
                .performClick()
            onNodeWithContentDescription("Refresh")
                .assertIsDisplayed()
                .assertHasClickAction()
                .performClick()
            onNodeWithContentDescription("Change place")
                .assertIsDisplayed()
                .assertHasClickAction()
                .performClick()

            onNodeWithText("Your forecast is ready").performScrollTo().assertIsDisplayed()
            onNodeWithText("Add another city")
                .performScrollTo()
                .assertHasClickAction()
                .performClick()
            onNodeWithText("Got it").performScrollTo().assertHasClickAction().performClick()

            runOnIdle {
                assertEquals(1, refreshes)
                assertEquals(1, changes)
                assertEquals(1, shares)
                assertEquals(1, addLocationTips)
                assertEquals(1, dismissedTips)
            }
        }
    }

    @Test
    fun cachedForecastRemainsUsefulAndRetryRecoversFreshContent() = withTestLocale("en-US") {
        runComposeUiTest {
            var state by mutableStateOf(
                contentState(
                    isStale = true,
                    refreshMessage = UiMessage.RefreshFailedShowingSaved
                )
            )

            setContent {
                TestWeatherScreen(
                    state = state,
                    onRetry = { state = contentState() }
                )
            }

            onNodeWithText("Tashkent").assertIsDisplayed()
            onNodeWithText("Couldn’t refresh. Showing saved weather.")
                .performScrollTo()
                .assertIsDisplayed()
            onNodeWithContentDescription("Refresh").performScrollTo().performClick()
            waitForIdle()
            onNodeWithText("Couldn’t refresh. Showing saved weather.").assertDoesNotExist()
            onNodeWithText("Tashkent").assertIsDisplayed()
        }
    }

    @Test
    fun uzbekAndArabicResourcesFollowLtrAndRtlLayout() {
        withTestLocale("uz-UZ") {
            runComposeUiTest {
                setContent { TestWeatherScreen(state = onboardingState()) }

                onNodeWithText("Tashqariga chiqish uchun eng yaxshi vaqtni toping.")
                    .performScrollTo()
                    .assertIsDisplayed()
                onNodeWithText("O‘zbekistondagi mashhur shaharlar")
                    .performScrollTo()
                    .assertIsDisplayed()
                onNodeWithText("Toshkent").assertIsDisplayed()
                onNodeWithText("Samarqand").assertIsDisplayed()
                val tashkent = onNodeWithText("Toshkent").fetchSemanticsNode().boundsInRoot.center.x
                val samarkand = onNodeWithText("Samarqand")
                    .fetchSemanticsNode()
                    .boundsInRoot
                    .center.x
                assertTrue(tashkent < samarkand, "UZ quick places must start from the left")
                assertEquals(LayoutDirection.Ltr, layoutDirectionForLanguage("uz"))
            }
        }

        withTestLocale("ar") {
            runComposeUiTest {
                setContent { TestWeatherScreen(state = onboardingState()) }

                onNodeWithText("طقس يبدو مألوفًا.").performScrollTo().assertIsDisplayed()
                onNodeWithText("مدن شهيرة في أوزبكستان")
                    .performScrollTo()
                    .assertIsDisplayed()
                onNodeWithText("طشقند").assertIsDisplayed()
                onNodeWithText("سمرقند").assertIsDisplayed()
                val tashkent = onNodeWithText("طشقند").fetchSemanticsNode().boundsInRoot.center.x
                val samarkand = onNodeWithText("سمرقند").fetchSemanticsNode().boundsInRoot.center.x
                assertTrue(tashkent > samarkand, "Arabic quick places must start from the right")
                assertEquals(LayoutDirection.Rtl, layoutDirectionForLanguage("AR"))
            }
        }
    }

    @Test
    fun russianOnboardingRemainsOperableAtTwoHundredPercentFontScale() = withTestLocale("ru-RU") {
        runComposeUiTest {
            setContent {
                TestWeatherScreen(
                    state = onboardingState(),
                    fontScale = 2f
                )
            }

            onNodeWithText("Найдите лучшее время для прогулки.")
                .performScrollTo()
                .assertIsDisplayed()
            onNode(hasSetTextAction()).performScrollTo().assertIsDisplayed()
            onNodeWithText("Использовать приблизительное местоположение")
                .performScrollTo()
                .assertIsDisplayed()
                .assertHasClickAction()
            onNodeWithText("Поиск города работает без разрешения.", substring = true)
                .performScrollTo()
                .assertIsDisplayed()
        }
    }
}

@Composable
private fun TestWeatherScreen(
    state: WeatherUiState,
    fontScale: Float = 1f,
    onRetry: () -> Unit = {},
    onSearchQueryChanged: (String) -> Unit = {},
    onLocationSelected: (Location) -> Unit = {},
    onUseDeviceLocation: () -> Unit = {},
    onChangeLocation: () -> Unit = {},
    onShareText: (String) -> Unit = {},
    onAddLocationFromFirstForecastTip: () -> Unit = {},
    onDismissFirstForecastTip: () -> Unit = {}
) {
    val currentDensity = LocalDensity.current
    CompositionLocalProvider(
        LocalDensity provides Density(currentDensity.density, fontScale),
        LocalLayoutDirection provides layoutDirectionForLanguage(ComposeLocale.current.language),
        LocalNimboThemeTokens provides LightThemeTokens
    ) {
        MaterialTheme(colorScheme = LightColors) {
            WeatherScreen(
                state = state,
                onRetry = onRetry,
                onSearchQueryChanged = onSearchQueryChanged,
                onLocationSelected = onLocationSelected,
                onLocationDeleted = {},
                onUseDeviceLocation = onUseDeviceLocation,
                onChangeLocation = onChangeLocation,
                onCancelLocationChange = {},
                onUnitPreferenceChanged = {},
                onShareText = onShareText,
                storeUrl = "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather",
                reviewUrl = "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather",
                supportUrl = "https://nimbo.uz/support/",
                onAddLocationFromFirstForecastTip = onAddLocationFromFirstForecastTip,
                onDismissFirstForecastTip = onDismissFirstForecastTip,
                themePreference = ThemePreference.Light,
                onThemePreferenceChanged = {}
            )
        }
    }
}

private fun onboardingState() = WeatherUiState.ChooseLocation(
    isOnboarding = true,
    quickLocations = UzbekistanQuickLocations.all
)

private fun contentState(
    isStale: Boolean = false,
    refreshMessage: UiMessage? = null,
    showFirstForecastTip: Boolean = false
): WeatherUiState.Content {
    val hour = WeatherHour(
        epochSeconds = TEST_EPOCH_SECONDS,
        temperatureC = 24.0,
        apparentTemperatureC = 24.0,
        weatherCode = 0,
        precipitationProbability = 10,
        precipitationMm = 0.0,
        windKph = 7.0,
        gustKph = 11.0,
        humidityPercent = 38,
        uvIndex = 1.0,
        fetchedAtEpochSeconds = TEST_EPOCH_SECONDS
    )
    return WeatherUiState.Content(
        weather = WeatherSnapshot(
            location = TASHKENT,
            current = hour,
            timeline = listOf(hour),
            fetchedAtEpochSeconds = TEST_EPOCH_SECONDS,
            isStale = isStale
        ),
        isRefreshing = false,
        refreshMessage = refreshMessage,
        unitPreference = UnitPreference.Metric,
        displayUnits = DisplayUnits(UnitSystem.Metric),
        showFirstForecastTip = showFirstForecastTip
    )
}

private inline fun <T> withTestLocale(languageTag: String, block: () -> T): T {
    val originalLocales = LocaleList.getDefault()
    LocaleList.setDefault(LocaleList(JavaLocale.forLanguageTag(languageTag)))
    return try {
        block()
    } finally {
        LocaleList.setDefault(originalLocales)
    }
}

private val TASHKENT = Location(
    id = "quick:uz:tashkent",
    name = "Tashkent",
    country = "Uzbekistan",
    latitude = 41.2995,
    longitude = 69.2401,
    timezone = "Asia/Tashkent"
)

private val BUKHARA = Location(
    id = "search:uz:bukhara",
    name = "Bukhara",
    country = "Uzbekistan",
    latitude = 39.7747,
    longitude = 64.4286,
    timezone = "Asia/Tashkent"
)

private const val TEST_EPOCH_SECONDS = 1_725_000_000L
