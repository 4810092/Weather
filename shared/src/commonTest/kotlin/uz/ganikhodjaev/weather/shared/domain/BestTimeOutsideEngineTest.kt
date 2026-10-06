package uz.ganikhodjaev.weather.shared.domain

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue
import kotlin.time.Instant
import uz.ganikhodjaev.weather.shared.model.WeatherHour

class BestTimeOutsideEngineTest {
    private val now = Instant.parse("2026-10-06T06:00:00Z").epochSeconds
    private val engine = BestTimeOutsideEngine()

    private fun forecast(offset: Int = 0, change: (WeatherHour) -> WeatherHour = { it }) =
        change(hour(now + offset * 3_600).copy(fetchedAtEpochSeconds = now))

    private fun pair(change: (WeatherHour) -> WeatherHour) = (0..1).map { forecast(it, change) }

    @Test
    fun precipitationCodesNeverClaimDryEvenWhenNumericFieldsConflict() {
        for (code in listOf(51, 61, 71, 80)) {
            val result = assertIs<OutsideRecommendation.WithCaveats>(
                engine.evaluate(pair { it.copy(weatherCode = code) }, "UTC", now)
            )
            assertTrue(OutsideCaveat.Rain in result.caveats)
            assertTrue(OutsideReason.Dry !in result.window.reasons)
        }
    }

    @Test
    fun knownHazardsRemainVisibleWithMissingOptionalMeasurements() {
        assertIs<OutsideRecommendation.Unsafe>(
            engine.evaluate(
                pair {
                    it.copy(weatherCode = 95, missingFields = WeatherHour.UV)
                },
                "UTC",
                now
            )
        )
    }

    @Test
    fun rainAllDayNeverBecomesTheBestWalk() {
        for (probability in listOf(60, 90, 97, 100)) {
            val result = engine.evaluate(
                (0..12).map {
                    forecast(it) { h ->
                        h.copy(precipitationProbability = probability)
                    }
                },
                "UTC",
                now
            )
            assertTrue(
                OutsideCaveat.Rain in
                    assertIs<OutsideRecommendation.NoSuitableWindow>(result).caveats
            )
        }
    }

    @Test
    fun comfortableWindowWinsOverWarmerRainyHours() {
        val hours = (0..5).map { offset ->
            forecast(offset) {
                it.copy(precipitationProbability = if (offset < 3) 97 else 10)
            }
        }
        val result = assertIs<OutsideRecommendation.Recommended>(engine.evaluate(hours, "UTC", now))
        assertEquals(now + 3 * 3_600, result.startEpochSeconds)
        assertTrue(OutsideReason.Dry in result.reasons)
    }

    @Test
    fun rainThresholdsAreIndependentAndCaveatsCannotBeHiddenByPositiveReasons() {
        for ((probability, amount) in listOf(30 to 0.0, 0 to 0.2, 59 to 0.49)) {
            val result = assertIs<OutsideRecommendation.WithCaveats>(
                engine.evaluate(
                    pair {
                        it.copy(precipitationProbability = probability, precipitationMm = amount)
                    },
                    "UTC",
                    now
                )
            )
            assertTrue(OutsideCaveat.Rain in result.caveats)
            assertTrue(OutsideReason.Dry !in result.window.reasons)
            assertEquals(probability, result.maxRainProbability)
            assertEquals(amount, result.maxRainMm)
        }
        assertIs<OutsideRecommendation.Recommended>(
            engine.evaluate(
                pair {
                    it.copy(precipitationProbability = 29, precipitationMm = 0.19)
                },
                "UTC",
                now
            )
        )
        assertIs<OutsideRecommendation.NoSuitableWindow>(
            engine.evaluate(
                pair {
                    it.copy(precipitationMm = 0.5)
                },
                "UTC",
                now
            )
        )
    }

    @Test
    fun allOriginalHazardBoundariesArePreserved() {
        val cases = listOf<(WeatherHour) -> WeatherHour>(
            { it.copy(apparentTemperatureC = 42.0) },
            { it.copy(apparentTemperatureC = -15.0) },
            { it.copy(weatherCode = 95) },
            { it.copy(precipitationMm = 8.0) },
            { it.copy(precipitationProbability = 90, precipitationMm = 3.0) },
            { it.copy(windKph = 55.0) },
            { it.copy(gustKph = 75.0) }
        )
        cases.forEach { change ->
            assertIs<OutsideRecommendation.Unsafe>(engine.evaluate(pair(change), "UTC", now))
        }
    }

    @Test
    fun comfortAndCautionBoundariesApplyToEveryHourNotJustAverage() {
        val caution = listOf<(WeatherHour) -> WeatherHour>(
            { it.copy(apparentTemperatureC = 9.99) },
            { it.copy(apparentTemperatureC = 30.01) },
            { it.copy(windKph = 20.0) },
            { it.copy(gustKph = 30.0) },
            { it.copy(uvIndex = 6.0) }
        )
        caution.forEach { change ->
            assertIs<OutsideRecommendation.WithCaveats>(
                engine.evaluate(listOf(forecast(), forecast(1, change)), "UTC", now)
            )
        }
        val poor = listOf<(WeatherHour) -> WeatherHour>(
            { it.copy(apparentTemperatureC = 4.99) },
            { it.copy(apparentTemperatureC = 35.01) },
            { it.copy(windKph = 35.0) },
            { it.copy(gustKph = 50.0) },
            { it.copy(uvIndex = 8.0) }
        )
        poor.forEach { change ->
            assertIs<OutsideRecommendation.NoSuitableWindow>(
                engine.evaluate(listOf(forecast(), forecast(1, change)), "UTC", now)
            )
        }
    }

    @Test
    fun gapsDuplicatesInvalidFieldsAndUnknownZonesCannotCreateConfidence() {
        val unavailable = listOf(
            listOf(forecast()), listOf(forecast(), forecast(2)),
            listOf(forecast(), forecast { it.copy(temperatureC = 40.0) }, forecast(1)),
            pair { it.copy(missingFields = WeatherHour.RAIN_PROBABILITY) },
            pair {
                it.copy(precipitationProbability = -1)
            },
            pair { it.copy(precipitationProbability = 101) },
            pair {
                it.copy(apparentTemperatureC = Double.NaN)
            },
            pair { it.copy(uvIndex = Double.POSITIVE_INFINITY) },
            pair { it.copy(weatherCode = -1) }
        )
        unavailable.forEach {
            assertEquals(OutsideRecommendation.Unavailable, engine.evaluate(it, "UTC", now))
        }
        assertEquals(
            OutsideRecommendation.Unavailable,
            engine.evaluate(
                pair {
                    it
                },
                "invalid",
                now
            )
        )
    }

    @Test
    fun freshnessAndClockSkewBoundariesAreExplicit() {
        for (age in listOf(0L, 21_600L, -300L)) {
            assertIs<OutsideRecommendation.Recommended>(
                engine.evaluate(
                    pair {
                        it.copy(
                            fetchedAtEpochSeconds =
                            now - age
                        )
                    },
                    "UTC",
                    now
                )
            )
        }
        for (age in listOf(21_601L, -301L)) {
            assertEquals(
                OutsideRecommendation.Unavailable,
                engine.evaluate(
                    pair {
                        it.copy(
                            fetchedAtEpochSeconds =
                            now - age
                        )
                    },
                    "UTC",
                    now
                )
            )
        }
    }

    @Test
    fun advancingClockDropsStartedWindowAndDateRolloverUsesCityTime() {
        val hours = (0..12).map { forecast(it) }
        assertEquals(
            now + 3_600,
            assertIs<OutsideRecommendation.Recommended>(
                engine.evaluate(
                    hours,
                    "UTC",
                    now + 1
                )
            ).startEpochSeconds
        )
        // 23:00 in Tashkent leaves only one complete hour; tomorrow is not today's guidance.
        val late = Instant.parse("2026-10-06T18:00:00Z").epochSeconds
        val lateHours = (0..4).map { hour(late + it * 3_600).copy(fetchedAtEpochSeconds = late) }
        assertEquals(
            OutsideRecommendation.Unavailable,
            engine.evaluate(lateHours, "Asia/Tashkent", late)
        )
        assertEquals(
            late + 3_600,
            assertIs<OutsideRecommendation.Recommended>(
                engine.evaluate(
                    lateHours,
                    "Asia/Tashkent",
                    late + 3_600
                )
            ).startEpochSeconds
        )
    }

    @Test
    fun shuffledInputAndEqualScoresChooseEarliestAndDstUsesElapsedHours() {
        assertEquals(
            now,
            assertIs<OutsideRecommendation.Recommended>(
                engine.evaluate(
                    (0..3).map {
                        forecast(it)
                    }.reversed(),
                    "UTC",
                    now
                )
            ).startEpochSeconds
        )
        val dst = Instant.parse("2026-11-01T05:00:00Z").epochSeconds
        val hours = (0..2).map { hour(dst + it * 3_600).copy(fetchedAtEpochSeconds = dst) }
        assertEquals(
            dst + 7_200,
            assertIs<OutsideRecommendation.Recommended>(
                engine.evaluate(hours, "America/New_York", dst)
            ).endEpochSeconds
        )
    }
}
