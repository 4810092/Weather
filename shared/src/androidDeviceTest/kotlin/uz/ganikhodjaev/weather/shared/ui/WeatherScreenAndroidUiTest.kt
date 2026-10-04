package uz.ganikhodjaev.weather.shared.ui

import android.content.Context
import android.content.res.Configuration
import android.graphics.Bitmap
import android.os.Build
import android.os.LocaleList
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.ComposeUiTest
import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.SemanticsNodeInteraction
import androidx.compose.ui.test.assertHasClickAction
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsSelected
import androidx.compose.ui.test.captureToImage
import androidx.compose.ui.test.hasAnyDescendant
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasContentDescription
import androidx.compose.ui.test.hasScrollToIndexAction
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToIndex
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeDown
import androidx.compose.ui.test.swipeUp
import androidx.compose.ui.test.v2.runAndroidComposeUiTest
import androidx.compose.ui.text.TextLayoutResult
import androidx.compose.ui.text.intl.Locale as ComposeLocale
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.test.platform.app.InstrumentationRegistry
import java.io.File
import java.util.Locale as JavaLocale
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import uz.ganikhodjaev.weather.shared.layoutDirectionForLanguage
import uz.ganikhodjaev.weather.shared.model.DailyForecast
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
    fun savedLocationDialogRemainsOperableOverGlass() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            var removed: Location? = null
            setContent {
                TestWeatherScreen(
                    state = WeatherUiState.ChooseLocation(
                        savedLocations = listOf(TASHKENT, BUKHARA),
                        activeLocationId = TASHKENT.id
                    ),
                    theme = ThemePreference.Dark,
                    onLocationDeleted = { removed = it }
                )
            }
            onNodeWithContentDescription("Bukhara, Remove saved place").performClick()
            onNodeWithText("Cancel").assertIsDisplayed().performClick()
            runOnIdle { assertEquals(null, removed) }
            onNodeWithContentDescription("Bukhara, Remove saved place").performClick()
            onNodeWithText("Remove", useUnmergedTree = true).assertIsDisplayed().performClick()
            runOnIdle { assertEquals(BUKHARA, removed) }
        }
    }

    @Test
    fun glassThemeSwitchKeepsControlsSelectedAndForecastReadable() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            var theme by mutableStateOf(ThemePreference.Light)
            setContent {
                TestWeatherScreen(
                    state = contentState(),
                    theme = theme,
                    onThemePreferenceChanged = { theme = it }
                )
            }
            onNodeWithText("Tashkent").assertIsDisplayed()
            waitForIdle()
            saveGlassScreenshot(
                "light",
                if (Build.VERSION.SDK_INT >=
                    26
                ) {
                    onRoot().captureToImage().asAndroidBitmap()
                } else {
                    null
                }
            )
            onNodeWithContentDescription("Settings").performClick()
            onNodeWithText("Dark", useUnmergedTree = true).performScrollTo().performClick()
            onNodeWithText("Dark").assertIsSelected()
            runOnIdle { assertEquals(ThemePreference.Dark, theme) }
            onNodeWithText("Back").performScrollTo().performClick()
            onNodeWithText("Tashkent").performScrollTo().assertIsDisplayed()
            onNodeWithContentDescription("Refresh").assertHasClickAction()
            waitForIdle()
            saveGlassScreenshot(
                "dark",
                if (Build.VERSION.SDK_INT >=
                    26
                ) {
                    onRoot().captureToImage().asAndroidBitmap()
                } else {
                    null
                }
            )
        }
    }

    @Test
    fun darkGlassForecastRemainsOperableWithLargeTextAndDisabledRefresh() =
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                var refreshes = 0
                setContent {
                    TestWeatherScreen(
                        state = contentState().copy(isRefreshing = true),
                        theme = ThemePreference.Dark,
                        fontScale = 2f,
                        onRetry = { refreshes++ }
                    )
                }
                onNodeWithContentDescription("Refreshing…").performClick()
                runOnIdle { assertEquals(0, refreshes) }
                onNodeWithContentDescription("Settings").performClick()
                onNodeWithText("Dark").performScrollTo().assertIsDisplayed().assertIsSelected()
                onNodeWithText("Back").performScrollTo().performClick()
                onNodeWithText("Tashkent").performScrollTo().assertIsDisplayed()
            }
        }

    @Test
    fun onboardingDoesNotRequestLocationUntilTapAndOffersPermissionFreeSearch() =
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
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
                onNode(hasText("Bukhara") and hasText("Uzbekistan") and hasClickAction())
                    .performScrollTo()
                    .assertIsDisplayed()
                    .assertHasClickAction()
                    .performClick()
                runOnIdle { assertEquals(BUKHARA, selectedLocation) }
            }
        }

    @Test
    fun successfulForecastExposesTipAndAccessibleHeaderActions() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
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
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
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
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
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
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
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
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
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

    @Test
    fun settingsAndOfflineLicensesSupportVisibleAndAndroidBackNavigation() =
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                setContent { TestWeatherScreen(state = contentState()) }
                onNodeWithContentDescription("Settings").performClick()
                onNodeWithText("Open-source licenses").performScrollTo().performClick()
                waitUntil(timeoutMillis = 5_000) {
                    onAllNodes(hasText("Runtime library licenses", substring = true))
                        .fetchSemanticsNodes().isNotEmpty()
                }
                onNodeWithText("Runtime library licenses", substring = true).assertIsDisplayed()
                onNodeWithText("Back").performClick()
                onNodeWithText("Settings").assertIsDisplayed()
                onNodeWithText("Open-source licenses").performScrollTo().performClick()
                runOnUiThread { activity?.onBackPressedDispatcher?.onBackPressed() }
                onNodeWithText("Settings").assertIsDisplayed()
                runOnUiThread { activity?.onBackPressedDispatcher?.onBackPressed() }
                onNodeWithText("Tashkent").assertIsDisplayed()
            }
        }

    @Test
    fun errorRecoveryControlsAreReachableWithLargeText() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            var state: WeatherUiState by mutableStateOf(
                WeatherUiState.EmptyError(UiMessage.WeatherUnavailable)
            )
            var changes = 0
            var retries = 0
            setContent {
                Box(Modifier.height(240.dp).fillMaxWidth()) {
                    TestWeatherScreen(
                        state = state,
                        fontScale = 2f,
                        onRetry = {
                            retries++
                            state = contentState()
                        },
                        onChangeLocation = { changes++ }
                    )
                }
            }
            onNodeWithText("Change place").performScrollTo().assertIsDisplayed().performClick()
            runOnIdle { assertEquals(1, changes) }
            onNodeWithText("Try again").performScrollTo().assertIsDisplayed().performClick()
            runOnIdle { assertEquals(1, retries) }
            onNodeWithText("Tashkent").assertIsDisplayed()
        }
    }

    @Test
    fun searchHidesStaleRowsDuringProgressAndFailureAndClearRemainsOperable() =
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                var state by mutableStateOf(
                    WeatherUiState.ChooseLocation(
                        query = "Bu",
                        results = listOf(BUKHARA),
                        isSearching = true
                    )
                )
                var cancellations = 0
                setContent {
                    TestWeatherScreen(
                        state = state,
                        onSearchQueryChanged = {
                            state =
                                state.copy(query = it, results = emptyList(), message = null)
                        },
                        onCancelLocationChange = { cancellations++ }
                    )
                }
                onNodeWithText("Searching…").performScrollTo().assertIsDisplayed()
                onNodeWithText("Bukhara").assertDoesNotExist()
                runOnIdle {
                    state =
                        state.copy(isSearching = false, message = UiMessage.CitySearchUnavailable)
                }
                onNodeWithText("City search is unavailable. Check your connection and try again.")
                    .performScrollTo().assertIsDisplayed()
                onNodeWithText("Bukhara").assertDoesNotExist()
                onNodeWithContentDescription("Clear search").performScrollTo().performClick()
                runOnIdle {
                    assertEquals("", state.query)
                    assertTrue(state.results.isEmpty())
                    state = state.copy(canCancel = true)
                }
                onNodeWithContentDescription("Clear search").assertDoesNotExist()
                runOnUiThread { activity?.onBackPressedDispatcher?.onBackPressed() }
                runOnIdle { assertEquals(1, cancellations) }
            }
        }

    @Test
    fun oldDailyFixtureUsesActualDateAndDetailsDoNotInventMissingValues() =
        withTestLocale("en-US") {
            runAndroidComposeUiTest<NimboLocaleTestActivity> {
                val base = contentState()
                setContent {
                    TestWeatherScreen(
                        state = base.copy(
                            weather = base.weather.copy(dailyForecast = listOf(testDay()))
                        )
                    )
                }
                val date = formatLocalDay(TEST_EPOCH_SECONDS, TASHKENT.timezone)
                val card = hasText(date) and hasClickAction()
                scrollForecastCardIntoView(card).performClick()
                onNode(card).assertIsSelected()
                onNodeWithText("Today").assertDoesNotExist()
                onNodeWithText("Tomorrow").assertDoesNotExist()
                onNodeWithText("Precipitation").assertDoesNotExist()
                onNodeWithText("Gusts").assertDoesNotExist()
                onNodeWithText("UV index").assertDoesNotExist()
                onNodeWithText("Close details").performScrollTo().assertIsDisplayed()
                waitForIdle()
                saveGlassScreenshot(
                    "daily-details",
                    if (Build.VERSION.SDK_INT >=
                        26
                    ) {
                        onRoot().captureToImage().asAndroidBitmap()
                    } else {
                        null
                    }
                )
                onNodeWithText("Close details").performClick()
                onNodeWithText("Close details").assertDoesNotExist()
                scrollForecastCardIntoView(card).performClick()
                runOnUiThread { activity?.onBackPressedDispatcher?.onBackPressed() }
                onNodeWithText("Close details").assertDoesNotExist()
            }
        }

    @Test
    fun selectedHourSurvivesRefreshAndSettingsRoundTrip() = withTestLocale("en-US") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            val base = contentState()
            val hours = (0 until 24).map { index ->
                base.weather.current.copy(
                    epochSeconds = TEST_EPOCH_SECONDS + index * 3_600,
                    temperatureC = when (index) {
                        1 -> 47.0
                        20 -> 70.0
                        else -> 20.0 + index
                    }
                )
            }
            var state by mutableStateOf(base.copy(weather = base.weather.copy(timeline = hours)))
            setContent { TestWeatherScreen(state = state) }
            val selectedCard = hasContentDescription("47", substring = true) and hasClickAction()
            scrollForecastCardIntoView(selectedCard).performClick().assertIsSelected()
            runOnIdle {
                state = state.copy(
                    weather = state.weather.copy(fetchedAtEpochSeconds = TEST_EPOCH_SECONDS + 100)
                )
            }
            onNode(selectedCard).assertIsSelected()
            // Browse without selecting: this scroll position is independent of the selected hour.
            onNode(
                hasScrollToIndexAction() and hasAnyDescendant(selectedCard)
            ).performScrollToIndex(20)
            waitForIdle()
            val browsedCard = hasContentDescription("70", substring = true) and hasClickAction()
            onNode(browsedCard).assertIsDisplayed()
            val browsedX = onNode(browsedCard).fetchSemanticsNode().positionInRoot.x
            onNodeWithContentDescription("Settings").performScrollTo().performClick()
            onNodeWithText("Back").performClick()
            waitForIdle()
            // Check before any helper can scroll horizontally. Header navigation changes only Y.
            val restoredX = onNode(browsedCard).fetchSemanticsNode().positionInRoot.x
            assertTrue(
                kotlin.math.abs(restoredX - browsedX) <= 1f,
                "Browsing position must survive settings: before=$browsedX after=$restoredX"
            )
            // Scroll back without clicking; the independently selected hour must still be selected.
            onNode(
                hasScrollToIndexAction() and hasAnyDescendant(browsedCard)
            ).performScrollToIndex(1)
            scrollForecastCardIntoView(selectedCard).assertIsSelected()
        }
    }

    @Test
    fun arabicSettingsKeepDegreeSignsBeforeTheirUnitLetters() = withTestLocale("ar") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            setContent {
                TestWeatherScreen(
                    state = contentState().copy(unitPreference = UnitPreference.Automatic),
                    fontScale = 2f
                )
            }
            onNodeWithContentDescription("الإعدادات").performClick()
            listOf("°C · km/h", "°F · mph").forEach { label ->
                onNodeWithText(label, useUnmergedTree = true)
                    .performScrollTo().assertIsDisplayed().assertUnitGlyphOrder(label.take(2))
            }
            onNodeWithText("يستخدم الوضع التلقائي", substring = true, useUnmergedTree = true)
                .performScrollTo().assertIsDisplayed().assertUnitGlyphOrder("°C")
            waitForIdle()
            saveGlassScreenshot(
                "ar-settings-font-200",
                if (Build.VERSION.SDK_INT >=
                    26
                ) {
                    onRoot().captureToImage().asAndroidBitmap()
                } else {
                    null
                }
            )
        }
    }

    @Test
    fun russianSettingsRemainOperableAtTwoHundredPercentText() = withTestLocale("ru-RU") {
        runAndroidComposeUiTest<NimboLocaleTestActivity> {
            setContent { TestWeatherScreen(state = contentState(), fontScale = 2f) }
            onNodeWithContentDescription("Настройки").performClick()
            onNodeWithText("Назад").assertIsDisplayed()
            waitForIdle()
            saveGlassScreenshot(
                "ru-settings-font-200",
                if (Build.VERSION.SDK_INT >=
                    26
                ) {
                    onRoot().captureToImage().asAndroidBitmap()
                } else {
                    null
                }
            )
            onNodeWithText(
                "Лицензии открытого ПО"
            ).performScrollTo().assertIsDisplayed().assertHasClickAction()
            onNodeWithText("Назад").performScrollTo().performClick()
            onNodeWithText("Tashkent").assertIsDisplayed()
        }
    }
}

private fun SemanticsNodeInteraction.assertUnitGlyphOrder(unit: String) {
    val layouts = mutableListOf<TextLayoutResult>()
    performSemanticsAction(SemanticsActions.GetTextLayoutResult) { it(layouts) }
    val layout = layouts.single()
    val offset = layout.layoutInput.text.text.indexOf(unit)
    assertTrue(offset >= 0)
    assertTrue(
        layout.getBoundingBox(offset).center.x < layout.getBoundingBox(offset + 1).center.x,
        "The degree sign must render before its Latin unit letter in RTL text"
    )
}

@Composable
private fun TestWeatherScreen(
    state: WeatherUiState,
    fontScale: Float = 1f,
    theme: ThemePreference = ThemePreference.Light,
    onThemePreferenceChanged: (ThemePreference) -> Unit = {},
    onRetry: () -> Unit = {},
    onSearchQueryChanged: (String) -> Unit = {},
    onLocationSelected: (Location) -> Unit = {},
    onLocationDeleted: (Location) -> Unit = {},
    onUseDeviceLocation: () -> Unit = {},
    onChangeLocation: () -> Unit = {},
    onCancelLocationChange: () -> Unit = {},
    onShareText: (String) -> Unit = {},
    onAddLocationFromFirstForecastTip: () -> Unit = {},
    onDismissFirstForecastTip: () -> Unit = {}
) {
    val currentDensity = LocalDensity.current
    val injectedLanguage = AndroidUiTestLocale.locale.language
    val composeLanguage = ComposeLocale.current.language
    check(composeLanguage == injectedLanguage) {
        "Compose locale $composeLanguage does not match injected locale $injectedLanguage"
    }
    CompositionLocalProvider(
        LocalContentColor provides
            if (theme ==
                ThemePreference.Dark
            ) {
                DarkColors.onBackground
            } else {
                LightColors.onBackground
            },
        LocalDensity provides Density(currentDensity.density, fontScale),
        LocalLayoutDirection provides layoutDirectionForLanguage(injectedLanguage),
        LocalNimboThemeTokens provides
            if (theme == ThemePreference.Dark) DarkThemeTokens else LightThemeTokens
    ) {
        MaterialTheme(
            colorScheme = if (theme ==
                ThemePreference.Dark
            ) {
                DarkColors
            } else {
                LightColors
            }
        ) {
            WeatherScreen(
                state = state,
                onRetry = onRetry,
                onSearchQueryChanged = onSearchQueryChanged,
                onLocationSelected = onLocationSelected,
                onLocationDeleted = onLocationDeleted,
                onUseDeviceLocation = onUseDeviceLocation,
                onChangeLocation = onChangeLocation,
                onCancelLocationChange = onCancelLocationChange,
                onUnitPreferenceChanged = {},
                onShareText = onShareText,
                storeUrl = "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather",
                reviewUrl = "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather",
                supportUrl = "https://nimbo.uz/support/",
                onAddLocationFromFirstForecastTip = onAddLocationFromFirstForecastTip,
                onDismissFirstForecastTip = onDismissFirstForecastTip,
                themePreference = theme,
                onThemePreferenceChanged = onThemePreferenceChanged
            )
        }
    }
}

/** Nested LazyRow scroll semantics do not bring the row into the vertical viewport. */
@OptIn(ExperimentalTestApi::class)
private fun ComposeUiTest.scrollForecastCardIntoView(
    matcher: SemanticsMatcher
): SemanticsNodeInteraction {
    val card = onNode(matcher)
    card.performScrollTo()
    repeat(8) {
        waitForIdle()
        val node = card.fetchSemanticsNode()
        val top = node.positionInRoot.y
        val bottom = top + node.size.height
        val viewport = onRoot().fetchSemanticsNode().boundsInRoot
        val margin = 32f
        if (top >= viewport.top + margin && bottom <= viewport.bottom - margin) {
            return card.assertIsDisplayed()
        }
        onRoot().performTouchInput {
            if (top < viewport.top + margin) {
                swipeDown(startY = height * 0.3f, endY = height * 0.7f)
            } else {
                swipeUp(startY = height * 0.8f, endY = height * 0.4f)
            }
        }
    }
    val node = card.fetchSemanticsNode()
    val top = node.positionInRoot.y
    val bottom = top + node.size.height
    val viewport = onRoot().fetchSemanticsNode().boundsInRoot
    assertTrue(
        top >= viewport.top + 32f && bottom <= viewport.bottom - 32f,
        "Forecast card must fit in viewport before clicking: top=$top bottom=$bottom viewport=$viewport"
    )
    return card.assertIsDisplayed()
}

private fun saveGlassScreenshot(name: String, captured: Bitmap?) {
    val bitmap =
        captured
            ?: requireNotNull(
                InstrumentationRegistry.getInstrumentation().uiAutomation.takeScreenshot()
            )
    val sampledColors = (1..16).flatMap { x ->
        (1..16).map { y -> bitmap.getPixel(bitmap.width * x / 17, bitmap.height * y / 17) }
    }.toSet()
    assertTrue(
        sampledColors.size > 16,
        "Screenshot must contain rendered content, not a blank window"
    )
    val context = InstrumentationRegistry.getInstrumentation().targetContext
    val directory = File(context.externalMediaDirs.first(), "additional_test_output").apply {
        mkdirs()
    }
    File(directory, "$name.png").outputStream().use {
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)
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
    val originalTestLocale = AndroidUiTestLocale.locale
    AndroidUiTestLocale.locale = JavaLocale.forLanguageTag(languageTag)
    LocaleList.setDefault(LocaleList(AndroidUiTestLocale.locale))
    return try {
        block()
    } finally {
        AndroidUiTestLocale.locale = originalTestLocale
        LocaleList.setDefault(originalLocales)
    }
}

class NimboLocaleTestActivity : ComponentActivity() {
    override fun attachBaseContext(newBase: Context) {
        val locale = AndroidUiTestLocale.locale
        val locales = LocaleList(locale)
        LocaleList.setDefault(locales)
        val configuration = Configuration(newBase.resources.configuration).apply {
            setLocales(locales)
            setLayoutDirection(locale)
        }
        super.attachBaseContext(newBase.createConfigurationContext(configuration))
    }
}

private object AndroidUiTestLocale {
    @Volatile
    var locale: JavaLocale = JavaLocale.forLanguageTag("en-US")
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

private fun testDay() = DailyForecast(
    epochSeconds = TEST_EPOCH_SECONDS,
    weatherCode = 0,
    temperatureMaxC = 28.0,
    temperatureMinC = 18.0,
    apparentTemperatureMaxC = 27.0,
    apparentTemperatureMinC = 17.0,
    precipitationProbabilityMax = null,
    precipitationMm = null,
    windMaxKph = 12.0,
    gustMaxKph = null,
    uvIndexMax = null,
    sunriseEpochSeconds = TEST_EPOCH_SECONDS - 3_600,
    sunsetEpochSeconds = TEST_EPOCH_SECONDS + 3_600,
    fetchedAtEpochSeconds = TEST_EPOCH_SECONDS
)
