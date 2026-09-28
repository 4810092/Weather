# Build 12 hosted byte verification — September 28, 2026

Status: **PASS — signed artifact identity only**.

[Trusted verification run 36363527493](https://github.com/4810092/Weather/actions/runs/36363527493)
passed at workflow head `968a6793f390c586a7fa56721b05a483a48ce4df`. It independently
reopened draft `397876280`, validated its exact assets and absent tag, and
verified all three complete signed artifacts from source
`0faf1105cc5da072e4e9ee043c46e2e9de4f4ada`. Protected signing run `36361077488` and materialization run
`36363383305` supply the separate provenance and retained-byte chain.

| Artifact | Version | SHA-256 |
| --- | --- | --- |
| Phone AAB | `1.1.0 (12)` | `5fdc866094226d7cde09696e6fd2de27683af0ee6955674b3a1d29a7c203a2cd` |
| Wear AAB | `1.1.0 (1000012)` | `51a1d4f0a8e5b8cfa6cb6d752e1a3aad56de36749eaa6fb551039a1f429b23e4` |
| Apple IPA | `1.1.0 (12)` | `b42d0bf6a218ba1b5ed3d607a18611fbf700fadef856b02861f618411585474d` |

The [machine receipt](receipts/trusted-release-verification-36363527493.json)
returns `verified-current` and `byte_verified=true` for all three artifacts.
Its Actions artifact `10945639847` is 1,741 bytes with ZIP SHA-256
`c83a6f69d1eb6a8201a4c7b4b7d826ee8d4c9709c3be36f815b168167678c674`;
the local download matched size/hash and its source/run/draft/artifact identities.
The 21 security mutation tests passed and independent review found no changed
safety logic or Pages deployment. Current runtime fields remain null.

This evidence establishes signed-byte authority only. It does not establish
store upload, TestFlight/Internal delivery, natural widget/background refresh,
fresh crash close-out, review, rollout, or public availability. The retained
draft is mutable and requires protected revalidation before later use.
