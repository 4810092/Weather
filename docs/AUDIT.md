# Repository audit

Date: 2026-08-09  
Baseline commit: `8fcefb8`  
Recovery tag: `legacy-android-v1.0.1`

## Production identity

- Android application ID: `uz.ganikhodjaev.weather` (immutable).
- Android namespace: `uz.ganikhodjaev.weather`.
- Legacy version: version code 2, version name 1.0.1.
- Tracked release artifact: `app/release/app-release.aab`.
- AAB signing certificate subject: `CN=Khasan Ganikhodjaev, OU=Android Developer, O=no, L=Tashkent, ST=Tashkent, C=UZ`.
- Certificate SHA-256: `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.
- Certificate validity: 2024-03-27 through 2049-03-21.
- The signing keystore, upload key configuration, Play App Signing status, and Play publishing credentials are not present in the repository. They must be recovered or verified in Play Console before a production upload.
- The iOS bundle identifier is reserved by product decision as `uz.ganikhodjaev.weather`; its Apple Developer availability has not yet been verified.

## Repository and history

- One commit exists on `master`; no prior tags or release branches existed.
- Remote: `https://github.com/4810092/Weather.git`.
- The worktree contained pre-existing Android Studio `.idea` changes before Nimbo work. They are not part of the migration and must not be overwritten accidentally.
- A recovery tag and a `codex/nimbo-1.0` implementation branch were created before migration.

## Build and architecture

- Single Android application module (`:app`), no iOS project and no CI.
- AGP 8.3.1, Gradle 8.4, Kotlin 1.9.0, Java 17.
- Android compile/target SDK 34; min SDK 26.
- XML layouts, one `Activity`, one `Fragment`, RecyclerView, ViewBinding.
- Dagger 2, Retrofit/Gson, OkHttp, AndroidX ViewModel and a `SharedFlow` event.
- The app fetches a hard-coded Tashkent forecast and displays DTO-derived objects as rows. There is no current-weather UX, location flow, offline cache, settings, localization, accessibility treatment, or adaptive layout.
- Baseline `./gradlew test assembleDebug` succeeds.
- Release minification is disabled and ProGuard configuration is the default template.

## Data, permissions, and migration

- Declared permission: `INTERNET` only.
- No Room/SQLite database, SharedPreferences, DataStore, files, or persisted settings are used by legacy code.
- No user data migration is required from version code 2. Nimbo must still pass an install-over-production test to validate signing, startup, backup restoration, permissions, and package continuity.
- Android backup is enabled with template rules. Nimbo will replace these with explicit policy.

## Networking and security

- A live-looking OpenWeather API key is hard-coded in source and present in Git history.
- OkHttp BODY logging is enabled for all builds.
- Network errors are collapsed into an uninformative exception and then silently ignored in the ViewModel.
- Required remediation: remove the key from HEAD, stop using a client secret for the v1 provider, disable sensitive release logging, and rotate/revoke the exposed key outside this repository. Removing it from HEAD does not remove it from public Git history.
- No keystores, certificates, provisioning profiles, service-account JSON, or publishing tokens were found in the working tree.

## Delivery gaps

- No GitHub Actions, lint/static analysis policy, release automation, store metadata, privacy policy, screenshots, or open-source governance files.
- No iOS shell, signing configuration, App Store privacy manifest, or App Store Connect metadata.
- The legacy AAB is intentionally retained until upgrade testing is complete; new release artifacts must not be committed.

## External verification still required

- Play Console: current production version, Play App Signing/enrollment, upload certificate, listing access, and highest accepted version code.
- Apple Developer: team access and whether App ID `uz.ganikhodjaev.weather` already exists.
- Real devices and store-managed production APK for final upgrade testing.

