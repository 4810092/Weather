# Forecast interaction feedback — candidate 13 source boundary

Source: `59a0ad381aeee892dfac51a85ccd15c2fb294773`. Prepared October 4, 2026.

First-forecast actions have a 12dp gap. The Current hour action centers the card, including at either end of the timeline. Hourly, daily and history rows measure the full set of localized text before layout and use one card height per row, including large fonts and optional missing daily values. The complete geolocation panel is a single accessible button; tapping its explanatory text invokes the same action. Shared weather includes the localized Nimbo website landing page, while platform review links remain unchanged.

Regression coverage now requires 19 instrumented tests per Android device, including centering at first/middle/last positions, equal heights after scrolling with Russian large text, both geolocation hit areas, first-tip button spacing, and the share URL. Targeted host tests, formatting and Android test compilation passed. API24 and API36 phones passed all 19 tests. The initial API36 tablet run passed 18; the sole failure was Compose WindowCapture.forceRedraw timing out after 2000ms while saving the existing Russian-onboarding screenshot. No assertion was removed, timeout increased or test skipped. Full CI will repeat the matrix. Logs: `/tmp/nimbo-feedback-compile.log`, `/tmp/nimbo-feedback-ui.log`.

Live HTTPS checks returned 200 for `https://nimbo.uz/`, `/ru/` and `/en/`. All three HTML pages link to Apple app6799886897 and Google Play packageuz.ganikhodjaev.weather, with localized Play language parameters. No website publication was required or performed.

Full CI, fresh native simulator review and Samsung debug update are pending. Current candidates remain phone1.1.0(13), Wear1.1.0(1000013), Apple1.1.0(13). The canonical registry atomically marks Apple, phone, and Wear artifacts blocked until new signing and independent byte/runtime verification. Distribution hashes and evidence remain null; build12 records are historical. No push, hosted CI, store upload or publication is authorized by this local change. Physical-iPhone settings and Mac network configuration remain untouched.
