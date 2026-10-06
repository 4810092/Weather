package uz.ganikhodjaev.weather.shared.domain

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

class WeatherInsightEngineTest {
    @Test
    fun reportsWarmerAndPrioritizesIncomingRain() {
        val now = 200_000L
        val yesterday = hour(now - 86_400L, temperature = 24.0)
        val current = hour(now, temperature = 28.0)
        val rain = hour(now + 3_600L, temperature = 27.0, rainChance = 70)
            .copy(fetchedAtEpochSeconds = now)
        val insights = WeatherInsightEngine().evaluate(
            snapshot(current, listOf(yesterday, current, rain))
        )

        assertEquals(TemperatureComparison.Warmer, insights.comparison)
        assertEquals(
            rain.epochSeconds,
            assertIs<UpcomingInsight.RainLikely>(insights.upcoming).epochSeconds
        )
    }

    @Test
    fun reportsUnavailableWhenYesterdayIsMissing() {
        val current = hour(200_000L, temperature = 20.0)
        val insights = WeatherInsightEngine().evaluate(snapshot(current, listOf(current)))

        assertEquals(TemperatureComparison.Unavailable, insights.comparison)
        assertEquals(null, insights.upcoming)
    }

    @Test
    fun upcomingChangeAdvancesWithClockAndDoesNotReuseExpiredHours() {
        val now = 200_000L
        val hours = (0..3).map { offset ->
            hour(now + offset * 3_600, rainChance = if (offset == 1) 80 else 0)
                .copy(fetchedAtEpochSeconds = now)
        }
        val weather = snapshot(hours[0], hours)
        assertIs<UpcomingInsight.RainLikely>(WeatherInsightEngine().evaluate(weather, now).upcoming)
        assertEquals(null, WeatherInsightEngine().evaluate(weather, now + 7_200).upcoming)
        assertEquals(null, WeatherInsightEngine().evaluate(weather, now + 21_601).upcoming)
        assertEquals(
            null,
            WeatherInsightEngine().evaluate(weather.copy(isStale = true), now).upcoming
        )
        val staleFuture = weather.copy(
            timeline = listOf(
                hours[0],
                hours[1].copy(
                    fetchedAtEpochSeconds =
                    now - 86_400
                )
            )
        )
        assertEquals(null, WeatherInsightEngine().evaluate(staleFuture, now).upcoming)
    }

    @Test
    fun ongoingRainIsNotAnnouncedAsANewChange() {
        val now = 200_000L
        val current = hour(now, code = 61, rainChance = 97, rainMm = 1.0)
        val rain = current.copy(epochSeconds = now + 3_600)
        assertEquals(
            null,
            WeatherInsightEngine().evaluate(snapshot(current, listOf(current, rain))).upcoming
        )
        val wetCodeWithZeroAmount = current.copy(
            precipitationProbability = 0,
            precipitationMm = 0.0
        )
        assertEquals(
            null,
            WeatherInsightEngine().evaluate(
                snapshot(wetCodeWithZeroAmount, listOf(wetCodeWithZeroAmount, rain))
            ).upcoming
        )
    }

    @Test
    fun nearestChangeWinsAndRainCanReturnAfterADryHour() {
        val now = 200_000L
        val current = hour(now)
        val cooler = current.copy(epochSeconds = now + 3_600, apparentTemperatureC = 16.0)
        val rain = current.copy(epochSeconds = now + 7_200, precipitationProbability = 80)
        assertIs<UpcomingInsight.TurningCooler>(
            WeatherInsightEngine().evaluate(
                snapshot(current, listOf(rain, current, cooler))
            ).upcoming
        )
        val coolerAndRain = cooler.copy(precipitationProbability = 80)
        assertEquals(
            UpcomingInsight.RainLikely(cooler.epochSeconds),
            WeatherInsightEngine().evaluate(
                snapshot(current, listOf(current, coolerAndRain))
            ).upcoming
        )
        val wetCurrent = current.copy(weatherCode = 61, precipitationProbability = 80)
        val dry = current.copy(epochSeconds = now + 3_600)
        assertEquals(
            UpcomingInsight.RainLikely(rain.epochSeconds),
            WeatherInsightEngine().evaluate(
                snapshot(wetCurrent, listOf(wetCurrent, dry, rain))
            ).upcoming
        )
        assertEquals(
            null,
            WeatherInsightEngine().evaluate(snapshot(current, listOf(current, rain))).upcoming
        )
        val unknown = current.copy(missingFields = WeatherHour.RAIN_PROBABILITY)
        assertEquals(
            null,
            WeatherInsightEngine().evaluate(
                snapshot(unknown, listOf(unknown, rain.copy(epochSeconds = now + 3_600)))
            ).upcoming
        )
    }

    private fun snapshot(current: WeatherHour, timeline: List<WeatherHour>) = WeatherSnapshot(
        location = Location("test", "Test", "Test", 0.0, 0.0, "UTC"),
        current = current,
        timeline = timeline,
        fetchedAtEpochSeconds = current.fetchedAtEpochSeconds,
        isStale = false
    )
}

internal fun hour(
    epoch: Long,
    temperature: Double = 20.0,
    apparent: Double = temperature,
    code: Int = 0,
    rainChance: Int = 0,
    rainMm: Double = 0.0,
    wind: Double = 8.0,
    gust: Double = 12.0,
    uv: Double = 1.0
) = WeatherHour(
    epochSeconds = epoch,
    temperatureC = temperature,
    apparentTemperatureC = apparent,
    weatherCode = code,
    precipitationProbability = rainChance,
    precipitationMm = rainMm,
    windKph = wind,
    gustKph = gust,
    humidityPercent = 50,
    uvIndex = uv,
    fetchedAtEpochSeconds = epoch
)
