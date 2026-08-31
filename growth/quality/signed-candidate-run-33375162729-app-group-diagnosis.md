# Signed candidate run 33375162729: App Group diagnosis

Status: failed closed; no signed candidate was uploaded or promoted.

## Hosted evidence

- GitHub Actions run: `33375162729`
- Workflow head: `b15e071979bffb681bf9666131441a81ba11b0d5`
- Product source authority: `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`
- Unsigned build job `99434889770`: succeeded in 18m38s.
- Protected sign/verify job `99439518709`: failed in 1m02s.
- `xcodebuild -exportArchive`: `** EXPORT SUCCEEDED **`.
- Android phone and Wear upload signing completed before the Apple export.
- Signing-material destruction completed after the verifier stopped the job.

The byte verifier rejected both the exported IPA and the retained archive copy:

```text
upload manifest artifact apple exported IPA app: signed app-group entitlement is missing
upload manifest artifact apple exported IPA widget: signed app-group entitlement is missing
upload manifest artifact apple xcarchive app: signed app-group entitlement is missing
upload manifest artifact apple xcarchive widget: signed app-group entitlement is missing
```

The final `actions/upload-artifact` step was skipped, so this run produced no
signed-candidate package or receipt. The only retained run artifact is the
inert unsigned handoff:

- artifact id: `9752092151`
- artifact name: `nimbo-unsigned-inputs-2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`
- GitHub artifact digest: `sha256:ec2e234d0f6ef68ed3fad3c60621accb1fae59e58b37c507ca53e589963a2e2f`
- inner unsigned tar SHA-256 after download: `ada16e124cc8f824e2980240dc425f5ef2c6b56d0f14277027a1a77c855d7789`
- expiry reported by GitHub: `2026-09-01T09:13:29Z`

## Diagnosis

The checked-in app and widget entitlement files both request exactly
`group.uz.ganikhodjaev.weather`. The distribution provisioning profiles
embedded by Xcode authorize that group: otherwise the same verifier pass would
also have emitted a provisioning-profile app-group failure. Instead, Xcode's
export from the deliberately unsigned archive signed app and widget with only
the four base distribution entitlements and omitted the requested App Group.

The unsigned archive contains no signed entitlement blob or retained `.xcent`
file. This makes the `CODE_SIGNING_ALLOWED=NO` handoff the cause of the lost
entitlement context, not a product-source change and not an invalid profile.

## Bounded local reproduction

The exact downloaded unsigned handoff was exported locally with the effective
`signingStyle=automatic` copy. The export reproduced the missing App Group.
Starting from that exported IPA, only the app and widget signatures were
replaced with the pinned Apple Distribution identity after adding the one
profile-authorized App Group to the otherwise exact Xcode-generated
entitlements. The app then passed:

```text
codesign --verify --strict --deep --verbose=4
valid on disk
satisfies its Designated Requirement
```

The re-packed diagnostic IPA passed `unzip -tq` and retained the App Group in
both signed entitlement blobs. Its temporary SHA-256 was
`9c781ae073456c173c19334cccc0283a25c42bed31ae542e2c7b82c416a8d02a`.
It was not uploaded, retained as a release candidate, or used for promotion.

## Required next gate

The hosted workflow must perform the same bounded nested-first re-sign, then:

1. byte-verify the repacked IPA and retained archive copy;
2. compare the UUID and raw SHA-256 of every embedded profile with the protected
   app/widget/watch profile inputs;
3. bind the workflow head, workflow digest, verifier digests, run id and attempt
   into a schema-3 receipt;
4. upload only after all checks close successfully.

Until that new hosted run succeeds, release `1.1.0` remains blocked and this
record is diagnostic evidence only.
