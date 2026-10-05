# Candidate 13 signed source boundary

Current product source: `44d3f7862b61ef95bf2b686820cfba3fc05a7b25`.

All three distribution artifacts were signed by run37322319203 from workflow head9dcc498 and independently verified locally on October5. Phone13, Wear1000013 and Apple app/widget/watch13 embed the current source and match the exact hashes in [signing evidence](signed-candidate-run-37322319203.md). Source paths match the checkout. Prior build12 bytes are historical and cannot be substituted.

This supersedes the unsigned-artifact boundary in the [October4 source note](release13-recent-days-source-sync-2026-10-04.md). The owner's October5 request authorizes submission to App Store and Google Play. Signing/source verification can pass while exact-distribution runtime and production-health gates remain blocked. Local simulator/emulator acceptance is separately recorded in [runtime evidence](release13-runtime-acceptance-2026-10-05.md); it does not prove signed iOS execution, actual screen-reader speech or store publication.
