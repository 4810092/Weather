package uz.ganikhodjaev.weather.shared.domain

import kotlin.math.abs
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal enum class TemperatureComparison {
    MuchWarmer,
    Warmer,
    Similar,
    Cooler,
    MuchCooler,
    Unavailable
}

internal sealed interface UpcomingInsight {
    data class RainLikely(val epochSeconds: Long) : UpcomingInsight
    data class TurningCooler(val epochSeconds: Long) : UpcomingInsight
    data class TurningWarmer(val epochSeconds: Long) : UpcomingInsight
}

internal data class WeatherInsights(
    val comparison: TemperatureComparison,
    val upcoming: UpcomingInsight?
)

internal class WeatherInsightEngine {
    fun evaluate(weather: WeatherSnapshot): WeatherInsights = WeatherInsights(
        comparison = compareWithYesterday(weather),
        upcoming = findUpcomingChange(weather)
    )

    private fun compareWithYesterday(weather: WeatherSnapshot): TemperatureComparison {
        val target = sameLocalTimeDaysAgo(
            epochSeconds = weather.current.epochSeconds,
            timezone = weather.location.timezone,
            daysAgo = 1
        )
        val yesterday = (weather.recentHistory + weather.timeline)
            .filter { abs(it.epochSeconds - target) <= MATCH_WINDOW_SECONDS }
            .minByOrNull { abs(it.epochSeconds - target) }
            ?: return TemperatureComparison.Unavailable
        val difference = weather.current.temperatureC - yesterday.temperatureC
        return when {
            difference >= 5.0 -> TemperatureComparison.MuchWarmer
            difference >= 2.0 -> TemperatureComparison.Warmer
            difference <= -5.0 -> TemperatureComparison.MuchCooler
            difference <= -2.0 -> TemperatureComparison.Cooler
            else -> TemperatureComparison.Similar
        }
    }

    private fun findUpcomingChange(weather: WeatherSnapshot): UpcomingInsight? {
        val future = weather.timeline.filter {
            it.epochSeconds > weather.current.epochSeconds &&
                it.epochSeconds <= weather.current.epochSeconds + LOOK_AHEAD_SECONDS
        }
        future.firstOrNull { it.precipitationProbability >= 60 || it.precipitationMm >= 0.5 }
            ?.let { return UpcomingInsight.RainLikely(it.epochSeconds) }

        val baseline = weather.current.apparentTemperatureC
        future.firstOrNull { it.apparentTemperatureC <= baseline - 3.0 }
            ?.let { return UpcomingInsight.TurningCooler(it.epochSeconds) }
        future.firstOrNull { it.apparentTemperatureC >= baseline + 3.0 }
            ?.let { return UpcomingInsight.TurningWarmer(it.epochSeconds) }
        return null
    }

    private companion object {
        const val MATCH_WINDOW_SECONDS = 90L * 60L
        const val LOOK_AHEAD_SECONDS = 12L * 60L * 60L
    }
}
