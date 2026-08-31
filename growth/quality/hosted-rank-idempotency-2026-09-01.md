# Hosted rank idempotency — 2026-09-01

Status: **canonical evidence preserved; workflow no-op fix pending hosted
verification**.

Scheduled run `33449407626` started at `2026-09-01 04:08 +05:00` after the
canonical `2026-09-01` observation had already been captured. The read-only
capture job stopped in `prepare-history` with exit code 2 and the message
`canonical day already exists on the default branch: 2026-09-01`; the write
job was skipped. No snapshot, receipt, evaluation, branch, or store state was
overwritten.

The default `master` snapshot and the `growth-observations` snapshot resolve to
the same Git blob `4132a1687bc58f5459ee2992debf2b7896540667` (73,282 bytes). The
existing day therefore remains the immutable canonical record and the Top-10
streak remains `0/7`.

The workflow now requests an explicit idempotent mode from the history
validator. When the requested day is already in the validated authoritative
history, capture, bundle upload, and persistence are skipped and the run ends as
a no-op success. The default strict API continues to reject an existing day.
If the default branch contains the day but the observation branch is missing it
or differs byte-for-byte, history preparation still fails before any write.

Repository unit and static-security tests cover the allowed no-op, the default
strict rejection, the divergent-history rejection, the required step guards,
and the persist-job guard. A manual hosted dispatch against the already
canonical September 1 day is still required to prove the workflow behavior
after the fix reaches `master`.
