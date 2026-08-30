# GitHub release-signing environment — 2026-08-30

Status: **CREATED AND BRANCH-RESTRICTED; 4/8 REQUIRED SECRETS
PROVISIONED; NO WORKFLOW RUN**.

At `2026-08-30 09:44 +05:00`, an authenticated, read-only-first inspection of
repository settings showed that `4810092/Weather` had only the existing
`github-pages` environment. A new environment named exactly
`release-signing` was then created for the already-reviewed manual workflow.
Its deployment branch/tag rule was set to **Protected branches only**.

The public GitHub repository API independently reports `master` as
`protected: true`, so the workflow's existing `refs/heads/master` condition is
compatible with that environment rule. No broader branch or tag pattern was
enabled.

At creation, the authenticated environment view showed zero secrets and zero
variables. No signing input was present at that checkpoint.

## Partial-provisioning boundary

At `2026-08-30 12:29 +05:00`, the authenticated environment view confirmed
exactly four required secrets and no variables. Secret values were transferred
directly from local files into the protected environment; they were not
printed, copied into the repository, or sent through chat. The provisioned
names are:

- `NIMBO_ANDROID_UPLOAD_KEYSTORE_B64`
- `NIMBO_APPLE_APP_PROFILE_B64`
- `NIMBO_APPLE_WATCH_PROFILE_B64`
- `NIMBO_APPLE_WIDGET_PROFILE_B64`

The four absent names are:

- `NIMBO_ANDROID_UPLOAD_KEY_PASSWORD`
- `NIMBO_ANDROID_UPLOAD_STORE_PASSWORD`
- `NIMBO_APPLE_DISTRIBUTION_P12_B64`
- `NIMBO_APPLE_DISTRIBUTION_P12_PASSWORD`

The existing local login Keychain still rejects protected Android password
reads and Apple private-key use. The Apple transport password will be generated
only together with a successful disposable P12 export; neither value currently
exists in GitHub.

No required-reviewer or wait-timer rule was added. The default administrator
bypass control remains unchanged; with no reviewer or timer rule this does not
substitute for the protected-branch restriction or make missing secrets
available.

## Decision boundary

Creating and partially provisioning the environment closes only part of the
repository-configuration prerequisite. It does not prove complete credential
access, signing, artifact identity, physical QA, store upload, submission,
review, rollout, or public availability. The manual
`Signed release candidate` workflow has not been dispatched and still has no
runs. The authoritative upload manifest therefore remains fail-closed at
`0/3` byte-verified artifacts.

The next executable release step remains local authorization of the existing
login Keychain, followed by direct provisioning of the four remaining values
without exposing their contents. Only after all eight names are confirmed may
the master-only hosted workflow be dispatched.
