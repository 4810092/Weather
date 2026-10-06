package uz.ganikhodjaev.weather.shared.domain

import kotlin.time.Instant
import kotlinx.datetime.DateTimeUnit
import kotlinx.datetime.TimeZone
import kotlinx.datetime.atStartOfDayIn
import kotlinx.datetime.plus
import kotlinx.datetime.toLocalDateTime
import uz.ganikhodjaev.weather.shared.model.WeatherCondition
import uz.ganikhodjaev.weather.shared.model.WeatherHour
import uz.ganikhodjaev.weather.shared.model.weatherCondition

internal enum class OutsideReason {
    ComfortableTemperature,
    LowerHeat,
    Dry,
    LightWind,
    LowUv
}

internal enum class OutsideCaveat {
    Rain,
    Heat,
    Cold,
    Wind,
    HighUv
}

internal enum class OutsideHazard {
    ExtremeHeat,
    ExtremeCold,
    Thunderstorm,
    HeavyPrecipitation,
    StrongWind
}

internal sealed interface OutsideRecommendation {
    data class Recommended(
        val startEpochSeconds: Long,
        val endEpochSeconds: Long,
        val reasons: List<OutsideReason>,
        val score: Int
    ) : OutsideRecommendation

    data class WithCaveats(
        val window: Recommended,
        val caveats: Set<OutsideCaveat>,
        val maxRainProbability: Int,
        val maxRainMm: Double
    ) : OutsideRecommendation

    data class NoSuitableWindow(val caveats: Set<OutsideCaveat>) : OutsideRecommendation
    data class Unsafe(val hazards: Set<OutsideHazard>) : OutsideRecommendation
    data object Unavailable : OutsideRecommendation
}

/** Product comfort thresholds, not a guarantee of personal safety. See docs/INSIGHT_ENGINE.md. */
internal class BestTimeOutsideEngine {
    fun evaluate(
        timeline: List<WeatherHour>,
        timezone: String,
        nowEpochSeconds: Long
    ): OutsideRecommendation {
        val zone = runCatching { TimeZone.of(timezone) }.getOrNull()
            ?: return OutsideRecommendation.Unavailable
        val localDate = Instant.fromEpochSeconds(nowEpochSeconds).toLocalDateTime(zone).date
        val dayEnd = localDate.plus(1, DateTimeUnit.DAY).atStartOfDayIn(zone).epochSeconds
        // Only complete upcoming hours. A recommendation must never start in the past.
        // Conflicting duplicate timestamps are unknown, not an arbitrary favourable reading.
        val today = timeline.groupBy { it.epochSeconds }.values.mapNotNull { rows ->
            rows.distinct().singleOrNull()
        }.filter { it.epochSeconds >= nowEpochSeconds && it.epochSeconds + HOUR_SECONDS <= dayEnd }
            .sortedBy { it.epochSeconds }
        val windows = today.windowed(WINDOW_HOURS).filter { hours ->
            hours[1].epochSeconds - hours[0].epochSeconds == HOUR_SECONDS &&
                hours.all { isReliable(it, nowEpochSeconds) }
        }
        if (windows.isEmpty()) {
            val knownHazards = today.filter {
                nowEpochSeconds - it.fetchedAtEpochSeconds in
                    -300..MAX_AGE_SECONDS
            }
                .flatMap(::hazards).toSet()
            return if (knownHazards.isEmpty()) {
                OutsideRecommendation.Unavailable
            } else {
                OutsideRecommendation.Unsafe(
                    knownHazards
                )
            }
        }
        val safe = windows.filter { it.flatMap(::hazards).isEmpty() }
        if (safe.isEmpty()) {
            return OutsideRecommendation.Unsafe(windows.flatten().flatMap(::hazards).toSet())
        }
        val comfortable = safe.filter { it.all { hour -> caveats(hour).isEmpty() } }
        val acceptable = comfortable.ifEmpty { safe.filter { it.all(::acceptableWithCaveats) } }
        if (acceptable.isEmpty()) {
            return OutsideRecommendation.NoSuitableWindow(safe.flatten().flatMap(::caveats).toSet())
        }
        // Stable tie break: sorted input and maxBy select the earliest equally good window.
        val best = acceptable.maxBy(::windowScore)
        val window = OutsideRecommendation.Recommended(
            best.first().epochSeconds,
            best.last().epochSeconds + HOUR_SECONDS,
            reasons(best),
            windowScore(best).toInt().coerceIn(0, 100)
        )
        val caveats = best.flatMap(::caveats).toSet()
        return if (caveats.isEmpty()) {
            window
        } else {
            OutsideRecommendation.WithCaveats(
                window,
                caveats,
                best.maxOf {
                    it.precipitationProbability
                },
                best.maxOf { it.precipitationMm }
            )
        }
    }

    private fun isReliable(hour: WeatherHour, now: Long): Boolean = hour.missingFields == 0 &&
        now - hour.fetchedAtEpochSeconds in -300..MAX_AGE_SECONDS &&
        hour.temperatureC.isFinite() &&
        hour.apparentTemperatureC.isFinite() &&
        hour.precipitationProbability in 0..100 &&
        hour.precipitationMm.isFinite() &&
        hour.precipitationMm >= 0 &&
        hour.windKph.isFinite() &&
        hour.windKph >= 0 &&
        hour.gustKph.isFinite() &&
        hour.gustKph >= 0 &&
        hour.uvIndex.isFinite() &&
        hour.uvIndex >= 0 &&
        weatherCondition(hour.weatherCode) != WeatherCondition.Unknown

    private fun acceptableWithCaveats(hour: WeatherHour): Boolean =
        hour.precipitationProbability < MAX_ACCEPTABLE_RAIN_PROBABILITY &&
            hour.precipitationMm < MAX_ACCEPTABLE_RAIN_MM &&
            hour.apparentTemperatureC in MIN_ACCEPTABLE_FEELS..MAX_ACCEPTABLE_FEELS &&
            hour.windKph < MAX_ACCEPTABLE_WIND &&
            hour.gustKph < MAX_ACCEPTABLE_GUST &&
            hour.uvIndex < MAX_ACCEPTABLE_UV

    private fun caveats(hour: WeatherHour): List<OutsideCaveat> = buildList {
        if (hour.precipitationProbability >= COMFORT_RAIN_PROBABILITY ||
            hour.precipitationMm >= COMFORT_RAIN_MM ||
            weatherCondition(hour.weatherCode) in PRECIPITATION_CONDITIONS
        ) {
            add(OutsideCaveat.Rain)
        }
        if (hour.apparentTemperatureC > COMFORT_MAX_FEELS) add(OutsideCaveat.Heat)
        if (hour.apparentTemperatureC < COMFORT_MIN_FEELS) add(OutsideCaveat.Cold)
        if (hour.windKph >= COMFORT_WIND || hour.gustKph >= COMFORT_GUST) add(OutsideCaveat.Wind)
        if (hour.uvIndex >= COMFORT_UV) add(OutsideCaveat.HighUv)
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
        val windScore = (20.0 - (hour.windKph - 10.0).coerceAtLeast(0.0) * 0.8).coerceIn(0.0, 20.0)
        val uvScore = (15.0 - (hour.uvIndex - 2.0).coerceAtLeast(0.0) * 2.0).coerceIn(0.0, 15.0)
        temperatureScore + rainScore + windScore + uvScore
    } / hours.size

    private fun hazards(hour: WeatherHour): List<OutsideHazard> = buildList {
        if (hour.apparentTemperatureC >= 42.0) add(OutsideHazard.ExtremeHeat)
        if (hour.apparentTemperatureC <= -15.0) add(OutsideHazard.ExtremeCold)
        if (weatherCondition(hour.weatherCode) ==
            WeatherCondition.Thunderstorm
        ) {
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
        if (hours.all {
                it.precipitationProbability < COMFORT_RAIN_PROBABILITY &&
                    it.precipitationMm < COMFORT_RAIN_MM &&
                    weatherCondition(it.weatherCode) !in PRECIPITATION_CONDITIONS
            }
        ) {
            add(OutsideReason.Dry)
        }
        if (hours.all { it.windKph < 20.0 && it.gustKph < 30.0 }) add(OutsideReason.LightWind)
        if (hours.all { it.uvIndex < 3.0 }) add(OutsideReason.LowUv)
    }.take(3)

    internal companion object {
        val PRECIPITATION_CONDITIONS = setOf(
            WeatherCondition.Drizzle,
            WeatherCondition.Rain,
            WeatherCondition.Snow,
            WeatherCondition.Showers,
            WeatherCondition.Thunderstorm
        )
        const val WINDOW_HOURS = 2
        const val HOUR_SECONDS = 3_600L
        const val MAX_AGE_SECONDS = 6 * HOUR_SECONDS
        const val COMFORT_RAIN_PROBABILITY = 30
        const val COMFORT_RAIN_MM = 0.2
        const val COMFORT_MIN_FEELS = 10.0
        const val COMFORT_MAX_FEELS = 30.0
        const val COMFORT_WIND = 20.0
        const val COMFORT_GUST = 30.0
        const val COMFORT_UV = 6.0
        const val MAX_ACCEPTABLE_RAIN_PROBABILITY = 60
        const val MAX_ACCEPTABLE_RAIN_MM = 0.5
        const val MIN_ACCEPTABLE_FEELS = 5.0
        const val MAX_ACCEPTABLE_FEELS = 35.0
        const val MAX_ACCEPTABLE_WIND = 35.0
        const val MAX_ACCEPTABLE_GUST = 50.0
        const val MAX_ACCEPTABLE_UV = 8.0
    }
}
