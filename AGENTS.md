# Nimbo operator authentication

- Run `scripts/auth-doctor.sh` before store, signing, GitHub Actions, or console work.
- Prefer the protected hosted signing workflow and authenticated `gh`/store APIs. Do not use the local login Keychain when hosted signing can perform the same operation.
- Use App Store Connect JWT and a least-privilege Google Play service account for supported delivery/status operations. Keep credentials outside Git and never print their values.
- Browser-only declarations and provider MFA remain manual. Build/sign, upload, review submission, rollout, and public availability are separate states and permissions.
