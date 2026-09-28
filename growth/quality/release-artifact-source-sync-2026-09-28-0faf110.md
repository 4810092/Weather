# Release source transition — September 28, 2026

Status: **PASS — signed artifact source identity only**.

Product/build-input authority `0faf1105cc5da072e4e9ee043c46e2e9de4f4ada` retains the latest widget/background-refresh
fixes and advances phone to `1.1.0 (12)`, Wear OS to `1.1.0 (1000012)`,
and Apple app/widget/watch to `1.1.0 (12)`. Fresh Android version codes are
required because the older vc11/vc1000011 artifacts are already in Google Play.
The coordinated source contract also requires a successor Apple build.

All three current manifest entries are now verified-current with exact signed
hashes. Runtime evidence remains null. Protected signing run `36361077488`,
materialization `36363383305`, and independent trusted verification
`36363527493` passed for this exact source. The former source `fcffe13be1cc15e83a0609751f696e48c9301444`
and its verified build-11 artifacts remain historical-superseded in their dated
receipt and evidence records. No old
runtime, upload, or review result is transferred to these bytes.

The owner requested publication of the latest fixes. Local CI, protected
signing, durable materialization, independent byte verification, runtime QA,
store delivery, review, and public availability must each be verified.

See [independent byte verification](release-artifact-full-verification-2026-09-28-build12-hosted.md). This pass does not close runtime, store delivery, review, or publication gates.
