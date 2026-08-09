package uz.ganikhodjaev.weather.shared.domain

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue

class BestTimeOutsideEngineTest {
    @Test
    fun selectsTheDryComfortableWindow() {
        val now = 1_704_067_200L
        val hours = listOf(
            hour(now, apparent = 34.0, rainChance = 10, uv = 8.0),
            hour(now + 3_600L, apparent = 31.0, rainChance = 10, uv = 6.0),
            hour(now + 7_200L, apparent = 23.0, rainChance = 5, uv = 2.0),
            hour(now + 10_800L, apparent = 22.0, rainChance = 5, uv = 1.0),
        )

        val result = assertIs<OutsideRecommendation.Recommended>(
            BestTimeOutsideEngine().evaluate(hours, "UTC", now),
        )

        assertEquals(now + 7_200L, result.startEpochSeconds)
        assertTrue(OutsideReason.ComfortableTemperature in result.reasons)
        assertTrue(OutsideReason.Dry in result.reasons)
    }

    @Test
    fun refusesToRecommendAThunderstormWindow() {
        val now = 1_704_067_200L
        val hours = listOf(
            hour(now, code = 95),
            hour(now + 3_600L, code = 95),
        )

        val result = assertIs<OutsideRecommendation.Unsafe>(
            BestTimeOutsideEngine().evaluate(hours, "UTC", now),
        )

        assertTrue(OutsideHazard.Thunderstorm in result.hazards)
    }

    @Test
    fun requiresACompleteTwoHourWindow() {
        val now = 1_704_067_200L
        assertEquals(
            OutsideRecommendation.Unavailable,
            BestTimeOutsideEngine().evaluate(listOf(hour(now)), "UTC", now),
        )
    }
}
