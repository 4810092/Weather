# Signed-candidate run 33368227872: Apple export diagnosis

Date: 2026-08-31  
Workflow head: `2ddea098372160c3d6990d5c7eef9e710a792bf5`  
Product source authority: `2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`

## Hosted result

GitHub Actions run
[`33368227872`](https://github.com/4810092/Weather/actions/runs/33368227872)
was triggered with `workflow_dispatch` on `master`.

- `build-unsigned` (`99413297925`) passed in 31m09s. It rebuilt the exact
  Android phone, Wear OS, and unsigned Apple archive, rechecked the sealed
  source inputs, and published the one-day unsigned handoff.
- `sign-verify` (`99420344274`) passed protected-secret decoding, Android phone
  and Wear upload signing, Apple identity installation, and all three profile
  installation steps.
- `Export and retain distribution-signed Apple build 6` failed with
  `xcodebuild` exit 70. Xcode rejected the app, widget, and watch profiles
  because they are Xcode-managed while the retained export options requested
  `signingStyle=manual`.
- The final cleanup step passed. The hosted runner destroyed its ephemeral
  signing directory and keychain.

The run produced only unsigned handoff artifact `9749831056`, named
`nimbo-unsigned-inputs-2cdd4387fc2b8b0f4cd3e3a873f019a6ca8a3652`, with
expiry `2026-09-01T07:54:39Z`. There is no signed-candidate tar or receipt from
this failed run, so it is not promotable release evidence.

## Bounded reproduction

The unsigned handoff was downloaded to a mode-700 temporary directory and its
embedded checksum was verified before extraction:

```text
c45b511f7b7c0a1a039f001219b6c9d02bbbbecec2c39f11292f08397345b678  nimbo-unsigned-inputs.tar.gz
```

No rebuild was performed. A temporary copy of the exact export options changed
only `signingStyle` from `manual` to `automatic`; its SHA-256 was
`d913719a273e731d81e8cd2d545fa084f5ecae0960cb89648b7ad51b044aded4`.
Running `xcodebuild -exportArchive` against the downloaded exact-source archive
then completed with `** EXPORT SUCCEEDED **` using the already installed
Xcode-managed app, widget, and watch distribution profiles.

The locally exported IPA was diagnostic only. It was not uploaded, submitted,
used to promote the manifest, or accepted as hosted provenance. The temporary
export is removed after this diagnosis.

## Remediation and boundary

The product source and `iosApp/ExportOptions.plist` remain unchanged. The
protected hosted workflow now validates the committed non-upload manual base
before secrets are available, deterministically normalizes the retained copy to
`signingStyle=automatic`, and then re-reads it before any signing step. The
workflow security policy pins the changed bytes, run-block digest, required
automatic-normalization markers, and a regression test.

`store/upload-manifest-1.1.0.json` remains `draft-blocked`. A new successful
hosted run must still produce and byte-verify the complete three-platform
candidate, retain the exact bytes, pass matching physical QA, and preserve the
no-upload boundary before any release-ready claim.
