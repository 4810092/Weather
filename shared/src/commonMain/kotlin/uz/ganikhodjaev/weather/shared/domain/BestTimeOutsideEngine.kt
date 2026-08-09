package uz.ganikhodjaev.weather.shared.domain

import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.weatherCondition
import kotlin.time.Instant

internal enum class OutsideReason {
    ComfortableTemperature,
    LowerHeat,
    Dry,
    LightWind,
    LowUv,
}

internal enum class OutsideHazard {
    ExtremeHeat,
    ExtremeCold,
    Thunderstorm,
    HeavyPrecipitation,
    StrongWind,
}

internal sealed interface OutsideRecommendation {
    data class Recommended(
        val startEpochSeconds: Long,
        val endEpochSeconds: Long,
        val reasons: List<OutsideReason>,
        val score: Int,
    ) : OutsideRecommendation

    data class Unsafe(val hazards: Set<OutsideHazard>) : OutsideRecommendation
    data object Unavailable : OutsideRecommendation
}

internal class BestTimeOutsideEngine {
    fun evaluate(
        timeline: List<WeatherHour>,
        timezone: String,
        nowEpochSeconds: Long,
    ): OutsideRecommendation {
        val zone = runCatching { TimeZone.of(timezone) }.getOrElse { TimeZone.UTC }
        val localDate = Instant.fromEpochSeconds(nowEpochSeconds).toLocalDateTime(zone).date
        val today = timeline.filter { hour ->
            hour.epochSeconds >= nowEpochSeconds - 30L * 60L &&
                Instant.fromEpochSeconds(hour.epochSeconds).toLocalDateTime(zone).date == localDate
        }
        if (today.size < WINDOW_HOURS) return OutsideRecommendation.Unavailable

        val windows = today.windowed(WINDOW_HOURS, step = 1).filter { hours ->
            hours.zipWithNext().all { (first, second) ->
                second.epochSeconds - first.epochSeconds in 3_000L..4_200L
            }
        }
        val safeWindows = windows.filter { window -> window.flatMap(::hazards).isEmpty() }
        if (safeWindows.isEmpty()) {
            val detected = today.flatMap(::hazards).toSet()
            return if (detected.isEmpty()) OutsideRecommendation.Unavailable
            else OutsideRecommendation.Unsafe(detected)
        }

        val best = safeWindows.maxBy(::windowScore)
        val reasons = reasons(best)
        return OutsideRecommendation.Recommended(
            startEpochSeconds = best.first().epochSeconds,
            endEpochSeconds = best.last().epochSeconds + HOUR_SECONDS,
            reasons = reasons,
            score = windowScore(best).toInt().coerceIn(0, 100),
        )
    }

    private fun windowScore(hours: List<WeatherHour>): Double = hours.sumOf { hour ->
        val feels = hour.apparentTemperatureC
        val temperatureScore = when {
            feels in 16.0..25.0 -> 40.0
            feels in 10.0..<16.0 || feels in 25.0..30.0 -> 30.0
            feels in 5.0..<10.0 || feels in 30.0..35.0 -> 18.0
            else -> 5.0
        }
        val rainScore = (25.0 - hour.precipitationProbability * 0.25 - hour.precipitationMm * 8.0)
            .coerceIn(0.0, 25.0)
        val windScore = (20.0 - (hour.windKph - 10.0).coerceAtLeast(0.0) * 0.8)
            .coerceIn(0.0, 20.0)
        val uvScore = (15.0 - (hour.uvIndex - 2.0).coerceAtLeast(0.0) * 2.0)
            .coerceIn(0.0, 15.0)
        temperatureScore + rainScore + windScore + uvScore
    } / hours.size

    private fun hazards(hour: WeatherHour): List<OutsideHazard> = buildList {
        if (hour.apparentTemperatureC >= 42.0) add(OutsideHazard.ExtremeHeat)
        if (hour.apparentTemperatureC <= -15.0) add(OutsideHazard.ExtremeCold)
        if (weatherCondition(hour.weatherCode) == WeatherCondition.Thunderstorm) {
            add(OutsideHazard.Thunderstorm)
        }
        if (hour.precipitationMm >= 8.0 ||
            (hour.precipitationProbability >= 90 && hour.precipitationMm >= 3.0)
        ) {
            add(OutsideHazard.HeavyPrecipitation)
        }
        if (hour.windKph >= 55.0 || hour.gustKph >= 75.0) add(OutsideHazard.StrongWind)
    }

    private fun reasons(hours: List<WeatherHour>): List<OutsideReason> = buildList {
        val averageFeels = hours.map { it.apparentTemperatureC }.average()
        if (averageFeels in 16.0..25.0) add(OutsideReason.ComfortableTemperature)
        else if (averageFeels < 32.0) add(OutsideReason.LowerHeat)
        if (hours.all { it.precipitationProbability < 30 && it.precipitationMm < 0.2 }) {
            add(OutsideReason.Dry)
        }
        if (hours.all { it.windKph < 20.0 && it.gustKph < 30.0 }) add(OutsideReason.LightWind)
        if (hours.all { it.uvIndex < 3.0 }) add(OutsideReason.LowUv)
    }.take(3)

    private companion object {
        const val WINDOW_HOURS = 2
        const val HOUR_SECONDS = 60L * 60L
    }
}
