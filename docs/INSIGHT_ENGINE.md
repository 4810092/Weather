# Deterministic insight engines

Nimbo does not use an LLM or remote inference for weather guidance. Both engines consume normalized SI weather data and return semantic values; localization happens in presentation code.

## Weather insight

- The current hour is compared with the nearest available hour 24 hours earlier, within a 90-minute tolerance.
- A difference below 2 °C is `Similar`, 2–5 °C is warmer/cooler, and 5 °C or more is much warmer/cooler.
- The next 12 hours are sorted and scanned for the earliest meaningful change: likely precipitation or a 3 °C apparent-temperature change, with precipitation winning a same-hour tie. An ongoing wet spell is not announced as newly arriving. A rain transition requires a known dry adjacent hour; a gap or unknown rain fields cannot establish onset.
- Missing history produces `Unavailable`; the engine never invents a comparison.

## Best time outside

The engine considers complete, exactly contiguous two-hour windows starting at or after the actual clock time and ending within the selected city's local day. It sorts input, rejects conflicting duplicate timestamps, and breaks score ties in favour of the earliest window. Local midnight is calculated in the city's IANA timezone (including DST); an invalid timezone gives insufficient data. A started window is removed, even when a cached snapshot still calls it current.

Five outcomes are distinct: comfortable; usable with explicit reservations; no suitable window; dangerous conditions; insufficient/reliably fresh data. A relative score can only rank eligible windows, never make poor weather suitable.

| Criterion (every hour in the window) | Comfortable | With reservations | Otherwise |
| --- | --- | --- | --- |
| Rain probability | <30% | <60% | No suitable window |
| Precipitation intensity | <0.2 mm/h | <0.5 mm/h | No suitable window |
| Apparent temperature | 10–30 °C inclusive | 5–35 °C inclusive | No suitable window |
| Wind / gust | <20 / <30 km/h | <35 / <50 km/h | No suitable window |
| UV | <6 | <8 | No suitable window |

These are deliberately conservative product comfort cutoffs for an ordinary two-hour walk, not clinical or meteorological safety standards. Probability and amount are independent: even a small expected amount with 97% probability is not promoted as a good walk. The caution band accommodates a possible brief light shower or less comfortable temperature/wind, and always displays **all** reservations before positive reasons. Rain reservations include maximum hourly probability and intensity. Comfortable windows are preferred to caution windows regardless of aggregate score. Rain at/above 60% or 0.5 mm/h is too likely/disruptive for the product to propose a walk. Temperature, wind and UV limits prevent one favourable component masking another unfavourable one.

Within each class, score weights remain apparent temperature 40, rain 25, wind 20 and UV 15. A window is excluded when it contains apparent temperature ≥42 °C or ≤−15 °C, a thunderstorm, ≥8 mm/h precipitation (or ≥90% probability with ≥3 mm/h), wind ≥55 km/h or gust ≥75 km/h. These existing hazard thresholds are unchanged. Known fresh hazards are retained even when another field is unavailable.

Each candidate hour must have valid finite measurements, known weather code and all rain/gust/UV fields supplied by the provider; fetch age must be at most six hours with at most five minutes of future clock skew. Optional-field absence is persisted as a mask in schema v5. Older cache rows migrate to unknown completeness, so fabricated historical zero defaults cannot create new confidence. Useful temperatures can still be displayed. Missing hours and stale data return insufficient data. When fresh remaining observations exist but less than two hours remain before local midnight, the outcome is no suitable window today; it never borrows tomorrow’s window. Known hazards in the remaining portion of the current hour still take priority.

Boundary and regression tests cover both rain thresholds, all original hazard cutoffs, freshness/skew, invalid and partial data, time advancement, midnight, shuffled/duplicate input and DST. Guidance is local and deterministic and is general weather guidance, not medical or emergency-safety advice.
