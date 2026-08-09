package uz.ganikhodjaev.weather.shared.model

import kotlin.test.Test
import kotlin.test.assertEquals

class WeatherModelsTest {
    @Test
    fun mapsRepresentativeWmoCodesToNormalizedConditions() {
        val expected = mapOf(
            0 to WeatherCondition.Clear,
            2 to WeatherCondition.MainlyClear,
            3 to WeatherCondition.Cloudy,
            45 to WeatherCondition.Fog,
            55 to WeatherCondition.Drizzle,
            65 to WeatherCondition.Rain,
            75 to WeatherCondition.Snow,
            82 to WeatherCondition.Showers,
            99 to WeatherCondition.Thunderstorm,
            1000 to WeatherCondition.Unknown,
        )

        expected.forEach { (code, condition) ->
            assertEquals(condition, weatherCondition(code), "WMO code $code")
        }
    }
}
