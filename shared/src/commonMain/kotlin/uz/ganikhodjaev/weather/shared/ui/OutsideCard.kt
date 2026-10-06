package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import kotlin.math.round
import org.jetbrains.compose.resources.stringResource
import uz.ganikhodjaev.weather.shared.domain.OutsideCaveat
import uz.ganikhodjaev.weather.shared.domain.OutsideHazard
import uz.ganikhodjaev.weather.shared.domain.OutsideReason
import uz.ganikhodjaev.weather.shared.domain.OutsideRecommendation
import uz.ganikhodjaev.weather.shared.model.DisplayUnits
import uz.ganikhodjaev.weather.shared.resources.*

@Composable
internal fun OutsideCard(
    recommendation: OutsideRecommendation,
    timezone: String,
    units: DisplayUnits
) {
    val reasonLabels = mapOf(
        OutsideReason.ComfortableTemperature to stringResource(Res.string.reason_comfortable),
        OutsideReason.LowerHeat to stringResource(Res.string.reason_milder),
        OutsideReason.Dry to stringResource(Res.string.reason_dry),
        OutsideReason.LightWind to stringResource(Res.string.reason_light_wind),
        OutsideReason.LowUv to stringResource(Res.string.reason_low_uv)
    )
    val hazardLabels = mapOf(
        OutsideHazard.ExtremeHeat to stringResource(Res.string.hazard_extreme_heat),
        OutsideHazard.ExtremeCold to stringResource(Res.string.hazard_extreme_cold),
        OutsideHazard.Thunderstorm to stringResource(Res.string.hazard_thunderstorm),
        OutsideHazard.HeavyPrecipitation to stringResource(Res.string.hazard_heavy_precipitation),
        OutsideHazard.StrongWind to stringResource(Res.string.hazard_strong_wind)
    )
    val caveatLabels = mapOf(
        OutsideCaveat.Rain to stringResource(Res.string.caveat_rain),
        OutsideCaveat.Heat to stringResource(Res.string.caveat_heat),
        OutsideCaveat.Cold to stringResource(Res.string.caveat_cold),
        OutsideCaveat.Wind to stringResource(Res.string.caveat_wind),
        OutsideCaveat.HighUv to stringResource(Res.string.caveat_uv)
    )
    val window = when (recommendation) {
        is OutsideRecommendation.Recommended -> recommendation
        is OutsideRecommendation.WithCaveats -> recommendation.window
        else -> null
    }
    Column(
        Modifier.fillMaxWidth().testTag("outside-guidance").nimboGlass().padding(18.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(stringResource(Res.string.outside_title), style = MaterialTheme.typography.labelLarge)
        Text(
            stringResource(
                when (recommendation) {
                    is OutsideRecommendation.Recommended -> Res.string.best_time_outside
                    is OutsideRecommendation.WithCaveats -> Res.string.outside_caution
                    is OutsideRecommendation.NoSuitableWindow -> Res.string.outside_no_window
                    is OutsideRecommendation.Unsafe -> Res.string.no_safe_window
                    OutsideRecommendation.Unavailable -> Res.string.not_enough_data
                }
            ),
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        if (window != null) {
            Text(
                stringResource(
                    Res.string.time_range,
                    "\u2066${formatLocalHour(window.startEpochSeconds, timezone)}\u2069",
                    "\u2066${formatLocalHour(window.endEpochSeconds, timezone)}\u2069"
                ),
                style = MaterialTheme.typography.headlineSmall
            )
        }
        // Reservations precede favourable reasons and are never truncated to a positive-only list.
        when (recommendation) {
            is OutsideRecommendation.WithCaveats -> {
                Text(recommendation.caveats.joinToString(" · ") { caveatLabels.getValue(it) })
                if (OutsideCaveat.Rain in recommendation.caveats) {
                    Text(
                        "${recommendation.maxRainProbability}% · ${round(
                            units.precipitation(recommendation.maxRainMm) * 100
                        ) / 100} ${units.precipitationSymbol}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
            is OutsideRecommendation.NoSuitableWindow -> Text(
                recommendation.caveats.joinToString(" · ") { caveatLabels.getValue(it) }
            )
            is OutsideRecommendation.Unsafe -> Text(
                recommendation.hazards.joinToString(" · ") { hazardLabels.getValue(it) },
                color = MaterialTheme.colorScheme.error
            )
            else -> Unit
        }
        if (window != null && window.reasons.isNotEmpty()) {
            Text(
                window.reasons.joinToString(" · ") { reasonLabels.getValue(it) },
                color = MaterialTheme.colorScheme.secondary,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
