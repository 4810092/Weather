# Recent days — candidate 13 source boundary

Source: `32c8f315bb84286424d4a62b6e88064dba55f720`. Prepared October 4, 2026.

Recent days now run from the oldest of the preceding seven calendar days through the current snapshot day. The current day includes available history plus the current hour, with duplicate timestamps and future hours excluded. Missing days remain absent. Saved forecasts retain their actual local dates and end at the last available date, without inventing today’s data. Initial scrolling reveals the last card; a new city or calendar day returns to the end, while same-day refresh and a round trip through Settings preserve manual browsing. Cards keep uniform height.

Targeted formatting, shared Android host tests and Android instrumented-test compilation passed (`/tmp/nimbo-recent-days-targeted.log`). New pure tests cover ascending dates, the partial current day, duplicate/future exclusion, city midnight/DST, missing days, stale snapshots and invalid timezones. The instrumented suite now requires20 tests per device, including initial position, chronological placement, refresh/Settings restoration and city/day changes. Full CI and fresh device checks are pending.

The canonical registry atomically marks Apple, phone, and Wear artifacts blocked until new signing and independent byte/runtime verification. Candidates remain phone1.1.0(13), Wear1.1.0(1000013) and Apple1.1.0(13); distribution hashes remain null and build12 records remain historical. Earlier forecast-feedback source59a0ad3 evidence does not validate this change. No publication or hosted CI is authorized by this local task.
