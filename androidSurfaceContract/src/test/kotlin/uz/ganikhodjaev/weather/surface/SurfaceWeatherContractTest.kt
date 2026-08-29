package uz.ganikhodjaev.weather.surface

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class SurfaceWeatherContractTest {
    @Test
    fun emptyPayloadShowsOnlyTheOpenAction() {
        val model = buildSurfaceWeatherRenderModel(emptyMap<String, Any?>(), NOW)

        assertEquals(SurfaceWeatherState.Empty, model.state)
        assertTrue(model.showsOpenAction)
        assertFalse(model.showsWeatherFacts)
        assertFalse(model.showsDailyRange)
        assertFalse(model.showsStaleStatus)
        assertNull(model.temperature)
        assertNull(model.rainChance)
        assertNull(model.airQuality)
    }

    @Test
    fun everyRequiredKeyFailsClosedWhenMissing() {
        val requiredKeys = listOf(
            SurfaceWeatherKeys.LOCATION,
            SurfaceWeatherKeys.TEMPERATURE,
            SurfaceWeatherKeys.TEMPERATURE_UNIT,
            SurfaceWeatherKeys.WEATHER_CODE,
            SurfaceWeatherKeys.RAIN_CHANCE,
            SurfaceWeatherKeys.HAS_DAILY_RANGE,
            SurfaceWeatherKeys.UPDATED_AT
        )

        requiredKeys.forEach { missingKey ->
            val model = buildSurfaceWeatherRenderModel(
                completePayload().minus(missingKey),
                NOW
            )

            assertEquals(
                SurfaceWeatherState.Empty,
                model.state,
                "Payload without $missingKey must fail closed"
            )
        }
    }

    @Test
    fun incompleteDailyRangeFailsClosed() {
        val withoutMaximum = completePayload().minus(SurfaceWeatherKeys.TEMPERATURE_MAX)
        val withoutMinimum = completePayload().minus(SurfaceWeatherKeys.TEMPERATURE_MIN)

        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(withoutMaximum, NOW).state
        )
        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(withoutMinimum, NOW).state
        )
    }

    @Test
    fun realZeroValuesRemainVisibleWeatherFacts() {
        val model = buildSurfaceWeatherRenderModel(
            completePayload().toMutableMap().apply {
                this[SurfaceWeatherKeys.TEMPERATURE] = 0
                this[SurfaceWeatherKeys.WEATHER_CODE] = 0
                this[SurfaceWeatherKeys.RAIN_CHANCE] = 0
                this[SurfaceWeatherKeys.AIR_QUALITY] = 0
                this[SurfaceWeatherKeys.TEMPERATURE_MAX] = 0
                this[SurfaceWeatherKeys.TEMPERATURE_MIN] = 0
            },
            NOW
        )

        assertEquals(SurfaceWeatherState.Fresh, model.state)
        assertFalse(model.showsOpenAction)
        assertTrue(model.showsWeatherFacts)
        assertTrue(model.showsDailyRange)
        assertEquals(0, model.temperature)
        assertEquals(0, model.weatherCode)
        assertEquals(0, model.rainChance)
        assertEquals(0, model.airQuality)
        assertEquals(0, model.temperatureMaximum)
        assertEquals(0, model.temperatureMinimum)
    }

    @Test
    fun sixHourBoundaryIsFreshAndOneSecondAfterIsStale() {
        val atBoundary = completePayload(
            updatedAt = NOW - SURFACE_WEATHER_STALE_AFTER_SECONDS
        )
        val afterBoundary = completePayload(
            updatedAt = NOW - SURFACE_WEATHER_STALE_AFTER_SECONDS - 1L
        )

        val fresh = buildSurfaceWeatherRenderModel(atBoundary, NOW)
        val stale = buildSurfaceWeatherRenderModel(afterBoundary, NOW)

        assertEquals(SurfaceWeatherState.Fresh, fresh.state)
        assertFalse(fresh.showsStaleStatus)
        assertEquals(SurfaceWeatherState.Stale, stale.state)
        assertTrue(stale.showsStaleStatus)
        assertTrue(stale.showsWeatherFacts)
        assertEquals(24, stale.temperature)
        assertEquals(10, stale.rainChance)
    }

    @Test
    fun smallClockSkewIsAcceptedButFarFutureTimestampFailsClosed() {
        val maximumAcceptedFuture = completePayload(
            updatedAt = NOW + SURFACE_WEATHER_MAX_FUTURE_SKEW_SECONDS
        )
        val firstRejectedFuture = completePayload(
            updatedAt = NOW + SURFACE_WEATHER_MAX_FUTURE_SKEW_SECONDS + 1L
        )
        val corruptFuture = completePayload(updatedAt = Long.MAX_VALUE)

        assertEquals(
            SurfaceWeatherState.Fresh,
            buildSurfaceWeatherRenderModel(maximumAcceptedFuture, NOW).state
        )
        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(firstRejectedFuture, NOW).state
        )
        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(corruptFuture, NOW).state
        )
    }

    @Test
    fun malformedTimestampAndWeatherValuesFailClosed() {
        val intTimestamp = completePayload().toMutableMap().apply {
            this[SurfaceWeatherKeys.UPDATED_AT] = NOW.toInt()
        }
        val zeroTimestamp = completePayload(updatedAt = 0L)
        val invalidRain = completePayload().toMutableMap().apply {
            this[SurfaceWeatherKeys.RAIN_CHANCE] = 101
        }

        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(intTimestamp, NOW).state
        )
        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(zeroTimestamp, NOW).state
        )
        assertEquals(
            SurfaceWeatherState.Empty,
            buildSurfaceWeatherRenderModel(invalidRain, NOW).state
        )
    }

    @Test
    fun malformedCoreFactsAndDailyBoundsFailClosed() {
        val invalidPayloads = listOf(
            SurfaceWeatherKeys.LOCATION to "x".repeat(101),
            SurfaceWeatherKeys.TEMPERATURE to 201,
            SurfaceWeatherKeys.TEMPERATURE to -201,
            SurfaceWeatherKeys.TEMPERATURE_UNIT to "x".repeat(9),
            SurfaceWeatherKeys.WEATHER_CODE to 4,
            SurfaceWeatherKeys.AIR_QUALITY to 1_001,
            SurfaceWeatherKeys.AIR_QUALITY to -2,
            SurfaceWeatherKeys.TEMPERATURE_MAX to 201,
            SurfaceWeatherKeys.TEMPERATURE_MIN to -201
        )

        invalidPayloads.forEach { (key, value) ->
            val payload = completePayload().toMutableMap().apply { this[key] = value }
            assertEquals(
                SurfaceWeatherState.Empty,
                buildSurfaceWeatherRenderModel(payload, NOW).state,
                "Malformed $key must fail closed"
            )
        }
    }

    @Test
    fun absentOptionalFactsDoNotBecomeFakeZeroes() {
        val model = buildSurfaceWeatherRenderModel(
            completePayload().toMutableMap().apply {
                this[SurfaceWeatherKeys.AIR_QUALITY] = -1
                this[SurfaceWeatherKeys.HAS_DAILY_RANGE] = false
                remove(SurfaceWeatherKeys.TEMPERATURE_MAX)
                remove(SurfaceWeatherKeys.TEMPERATURE_MIN)
            },
            NOW
        )

        assertEquals(SurfaceWeatherState.Fresh, model.state)
        assertTrue(model.showsWeatherFacts)
        assertFalse(model.showsDailyRange)
        assertNull(model.airQuality)
        assertNull(model.temperatureMaximum)
        assertNull(model.temperatureMinimum)
    }

    @Test
    fun missingAirQualityIsAnAbsentOptionalFact() {
        val model = buildSurfaceWeatherRenderModel(
            completePayload().minus(SurfaceWeatherKeys.AIR_QUALITY),
            NOW
        )

        assertEquals(SurfaceWeatherState.Fresh, model.state)
        assertTrue(model.showsWeatherFacts)
        assertNull(model.airQuality)
    }

    private fun completePayload(updatedAt: Long = NOW): Map<String, Any> = mapOf(
        SurfaceWeatherKeys.LOCATION to "Tashkent",
        SurfaceWeatherKeys.TEMPERATURE to 24,
        SurfaceWeatherKeys.TEMPERATURE_UNIT to "°C",
        SurfaceWeatherKeys.WEATHER_CODE to 1,
        SurfaceWeatherKeys.RAIN_CHANCE to 10,
        SurfaceWeatherKeys.AIR_QUALITY to 42,
        SurfaceWeatherKeys.HAS_DAILY_RANGE to true,
        SurfaceWeatherKeys.TEMPERATURE_MAX to 27,
        SurfaceWeatherKeys.TEMPERATURE_MIN to 18,
        SurfaceWeatherKeys.UPDATED_AT to updatedAt
    )

    private companion object {
        const val NOW = 2_000_000_000L
    }
}
