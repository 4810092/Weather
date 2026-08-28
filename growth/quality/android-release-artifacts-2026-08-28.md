# Android 1.1.0 internal release artifacts — 2026-08-28

Status: **SIGNED AND LOCALLY VALIDATED; NOT UPLOADED**. These are internal
release candidates, not proof of Google Play submission or availability.

## Artifact identity

All artifacts are stored outside the repository at
`/Users/khasan/work/ganikhodjaev/.nimbo-release/android/1.1.0-internal/` and
have mode `0600`.

| Artifact | Identity | SHA-256 |
|---|---|---|
| `nimbo-phone-1.1.0-vc7.aab` | phone `1.1.0 (7)` | `e476a124c33854873add9061140f68f1720ff098202b52e7758038bb50f5a77c` |
| `nimbo-wear-1.1.0-vc1000008.aab` | Wear OS `1.1.0 (1000008)` | `ac19a0eab1a60554db309166f135e754c97205b79c4f5182164a8b21594e7dc6` |
| `nimbo-phone-1.1.0-vc7-universal.apk` | phone universal APK | `2067f4b06b3c857f2aa86b5284447b3db7a1f1d91c58a9f1d666573e84be48d6` |
| `nimbo-wear-1.1.0-vc1000008-universal.apk` | Wear OS universal APK | `88445c1ea472ec7677499fb8bb7f93e081cf540171ba7a7bbd8e1e6c826696bf` |
| `nimbo-phone-1.1.0-vc7-mapping.txt` | phone R8 mapping | `06ab3656d5a67428388dcfd4f6f60a44db294d1da9e0d7300ef0bdd005a7bb1c` |

The generated APK-set containers are also retained beside the artifacts:

- `nimbo-phone-1.1.0-vc7-universal.apks` —
  `f5fa3a743539f321c1aa3c1e4b5583869c80028f5441be15dabd4c5f778b7275`
- `nimbo-wear-1.1.0-vc1000008-universal.apks` —
  `3d095cd9af6e6719964d6233cd54b8147f20c9a5e90747288df0a9f3a61dd508`

## Validation

- `bundletool 1.18.3 validate` exited successfully for both signed AABs.
  The checked bundletool JAR SHA-256 was
  `a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29`.
- Both AABs and both universal APKs use the expected Google Play upload
  certificate SHA-256 fingerprint:
  `43:15:48:A4:87:1C:9C:09:0E:EE:80:8A:C3:A3:48:98:F5:D7:86:02:D9:E7:47:DF:E8:1E:22:84:15:AA:C2:52`.
- `apksigner verify --verbose --print-certs` passed for both universal APKs.
  The phone APK is signed with v2 and v3, reports package
  `uz.ganikhodjaev.weather`, version `1.1.0 (7)`, min SDK 24, and target SDK
  36. The Wear OS APK is signed with v3 and reports the same package, version
  `1.1.0 (1000008)`, min SDK 30, and target SDK 36.
- Ordinary `jarsigner -verify` returned exit `0` and `jar verified` for both
  AABs. `jarsigner -verify -strict` returned exit `4` only because the upload
  certificate is self-signed, therefore has no public trust chain, and the
  signatures have no timestamp. This is a trust/timestamp warning for the
  expected private upload certificate, not a signature-integrity failure.

## Boundary

These checks prove local artifact identity, signing, and bundle/APK structure.
The phone universal APK's exact physical install/live/cold-start result is
recorded separately in `android-physical-smoke-2026-08-28.md`; Wear installation
is not proven. Neither report proves acceptance by Google Play, track assignment,
review completion, or public availability; those remain separate release gates.
