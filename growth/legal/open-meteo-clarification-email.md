# Open-Meteo promotion clarification — sent 2026-08-29

Status: sent at `2026-08-29 06:05:07 +05:00`; a read-only authenticated Gmail
thread and broad Open-Meteo search recheck at
`2026-08-29 12:35:12 +05:00` found no inbound response. The provider gate
remains `pending` until an unambiguous written answer is recorded.
To: `info@open-meteo.com`
Address verification: published on [Open-Meteo Terms & Privacy](https://open-meteo.com/en/terms), re-checked immediately before sending on 2026-08-29.
Subject: Clarification on non-commercial organic promotion for Nimbo

Hello Open-Meteo team,

I maintain Nimbo, an open-source weather app for iOS and Android:
https://github.com/4810092/Weather

The public project site is being activated at https://nimbo.uz/. The app is free and currently has no subscriptions, advertising, paid features, affiliate links, accounts, analytics SDK, or sale of user data. It uses Open-Meteo's public forecast, historical forecast, air-quality, and geocoding endpoints and displays the required Open-Meteo/GeoNames attribution.

Before doing any public promotion, I would like written clarification on the “promotional activities” example in your commercial-use terms.

Our proposed activity is entirely unpaid and non-monetized:

- publishing Uzbek- and Russian-language educational/product posts;
- contacting relevant journalists and local communities once, with at most one follow-up;
- submitting a genuine product update for editorial consideration by Apple or Google;
- using ordinary links to the free app, with no paid ads, sponsorships, referral fees, or affiliate revenue.

Would those activities make Nimbo's API use commercial under your current terms even though the app and promotion generate no revenue? If the answer depends on ownership, intent, distribution channel, download volume, or another fact, please tell us which condition controls.

We will monitor usage and keep it below the published Free API limits of 600 calls per minute, 5,000 per hour, 10,000 per day, and 300,000 per month. We understand that staying below the limits does not by itself authorize commercial use.

Please confirm one of the following in writing:

1. the described unpaid organic promotion remains permitted on the Free non-commercial API; or
2. it requires a paid subscription/customer endpoint or self-hosting before promotion begins.

If option 2 applies, please recommend the appropriate plan and confirm whether a customer API key may be protected behind a server-side proxy rather than embedded in the public mobile clients.

Thank you,

Khasan Ganikhodjaev
Nimbo maintainer
https://github.com/4810092/Weather

## Send gate

- The 2026-08-29 terms still list apps without subscriptions or advertising as
  non-commercial examples, but separately classify integration into
  promotional activities as commercial. That ambiguity is why silence or the
  absence of monetization cannot close this gate.
- The terms and official contact address were re-checked on the send date.
- The Gmail provider returned a successful sent-message result from the
  authenticated maintainer account. A pre-send search found no earlier thread
  to or from the provider contact, so no duplicate was sent.
- At the dated recheck, the sent clarification remained the only indexed
  matching message and had label `SENT`. Exact sender, domain, subject, and
  broad `Open-Meteo` searches returned no inbound message. This covers only
  Gmail-indexed state in the authenticated maintainer account and does not
  prove delivery or exclude another account or a future/not-yet-indexed reply.
- Save the sent timestamp and full written reply; do not mark the provider gate `pass` based on silence or an ambiguous answer.
