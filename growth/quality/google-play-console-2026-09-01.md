# Google Play Console checkpoint — 2026-09-01

Status: **PARTIAL CURRENT EVIDENCE**. The authenticated read-only checkpoint
confirms that the Uzbekistan Custom Store Listing is still under review and
that Android Vitals still exposes no decision-eligible crash or ANR rate. No
Console state was changed.

Observed at `2026-09-01 01:45–01:50` Asia/Tashkent in the `Khasan
Ganikhodjaev` developer account for package `uz.ganikhodjaev.weather`.

## Publishing review

- The app list reports Nimbo as a working app with update status `На
  рассмотрении` and seven currently installed users.
- Publishing overview says the changes are under review, managed publishing is
  off, and the latest publication remains `2026-08-27`.
- The pending change set contains only the Uzbekistan Custom Store Listing
  `Uzbekistan country — Best Time Outside`:
  - `en-US`: `Nimbo: Ob-havo va prognoz` plus the remaining required listing
    information;
  - `ru-RU`: `Nimbo: Погода и прогноз` plus the remaining required listing
    information.

This proves a still-pending review, not approval, publication, public
propagation, or rank impact.

## Dashboard aggregates

The rolling global last-28-days dashboard still reports 25 installs, 18 first
launches by device, and 13 monthly active devices. These are unchanged from the
August 31 checkpoint and are not Uzbekistan-only cohorts. The dashboard exposes
no numeric crash rate, ANR rate, or average rating on its summary cards.

## Android Vitals boundary

The crash and ANR issues page was checked with its default user-perceived
active-mode filter for `2026-08-04..2026-09-01`. The issue-cluster table says
`Нет данных` and the page exposes no numeric user-perceived crash or ANR rate.
The absence of rows is not converted into zero, so every Android stability
guardrail remains `UNKNOWN`.

The Android Vitals overview shows six recommendations against the currently
public phone `1.0.2 (6)` and Wear `1.0.2 (1000007)` releases:

1. outdated `androidx.fragment` on phone;
2. outdated `androidx.fragment` on Wear;
3. outdated `androidx.activity` on Wear;
4. edge-to-edge compatibility on phone;
5. unsupported edge-to-edge APIs or parameters on phone;
6. enable R8 for Wear.

These recommendations are scoped to the old public releases and are not
treated as findings against the unpublished `1.1.0` candidates. The exact
candidate source resolves `androidx.fragment:fragment` to `1.9.0` on phone and
Wear, resolves `androidx.activity` to `1.13.0` on phone, calls
`enableEdgeToEdge`, and enables minification plus resource shrinking for the
phone release. The Wear release does not currently enable minification, so the
R8 recommendation remains a candidate for a later real product update; it does
not justify replacing the already signed and internally delivered `1.1.0`
candidate before its physical store-delivery QA.

## Boundary

No review change, release, rollout, tester assignment, invite acceptance,
notification change, archive action, export, deletion, message, or spend was
performed. Public acquisition remains held by the independent iOS crash,
physical store-delivery, and critical-metric gates.

## 05:55–06:19 follow-up

The review state is unchanged. The listing index identifies
`Uzbekistan country — Best Time Outside` as a 100% Uzbekistan-targeted page,
last updated August 31 and still `На рассмотрении`. A read-only traversal of
its locked review form verified the exact submitted composition:

- separate en-US Uzbek-language and ru-RU Russian-language title, short-copy,
  and full-copy fields;
- one feature graphic, six phone screenshots, and one Wear OS screenshot per
  locale, with distinct object URL sets between the two locales;
- no 7-inch or 10-inch tablet screenshots in either locale.

The form was not edited and its save action remained disabled. The rolling
global dashboard at this later cutoff displayed 1.12 thousand device
impressions, 26 installations, 18 first launches, 13 monthly active devices,
and 34.29% store-listing conversion; D7 retention remained unavailable. These
newer rolling values are recorded here as a separate observation and are not
mixed into the source-windowed August 31 baseline.
