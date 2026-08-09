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
        val insights = WeatherInsightEngine().evaluate(snapshot(current, listOf(yesterday, current, rain)))

        assertEquals(TemperatureComparison.Warmer, insights.comparison)
        assertEquals(rain.epochSeconds, assertIs<UpcomingInsight.RainLikely>(insights.upcoming).epochSeconds)
    }

    @Test
    fun reportsUnavailableWhenYesterdayIsMissing() {
        val current = hour(200_000L, temperature = 20.0)
        val insights = WeatherInsightEngine().evaluate(snapshot(current, listOf(current)))

        assertEquals(TemperatureComparison.Unavailable, insights.comparison)
        assertEquals(null, insights.upcoming)
    }

    private fun snapshot(current: WeatherHour, timeline: List<WeatherHour>) = WeatherSnapshot(
        location = Location("test", "Test", "Test", 0.0, 0.0, "UTC"),
        current = current,
        timeline = timeline,
        fetchedAtEpochSeconds = current.fetchedAtEpochSeconds,
        isStale = false,
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
    uv: Double = 1.0,
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
    fetchedAtEpochSeconds = epoch,
)
