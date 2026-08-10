# Deterministic insight engines

Nimbo does not use an LLM or remote inference for weather guidance. Both engines consume normalized SI weather data and return semantic values; localization happens in presentation code.

## Weather insight

- The current hour is compared with the nearest available hour 24 hours earlier, within a 90-minute tolerance.
- A difference below 2 °C is `Similar`, 2–5 °C is warmer/cooler, and 5 °C or more is much warmer/cooler.
- The next 12 hours are scanned for meaningful change. Likely precipitation is prioritized, followed by a 3 °C apparent-temperature change.
- Missing history produces `Unavailable`; the engine never invents a comparison.

## Best time outside

The engine scores complete, contiguous two-hour windows remaining in the selected location's local day.

Score components total 100 points:

- apparent-temperature comfort: 40;
- precipitation probability and amount: 25;
- sustained wind: 20;
- UV: 15.

A window is excluded when it contains apparent temperature at or above 42 °C or at or below -15 °C, a thunderstorm, heavy precipitation, sustained wind of at least 55 km/h, or gusts of at least 75 km/h. If no safe window remains, Nimbo returns hazards instead of a recommendation.

The output is general weather guidance, not medical or emergency-safety advice. Thresholds are explicit and covered by shared tests so future changes require an intentional review.
