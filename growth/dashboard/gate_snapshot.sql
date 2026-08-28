-- Scale gates are fail-closed. Unknown is not treated as pass.
SELECT *
FROM (
  VALUES
    ('iOS crash gate', 'blocked', 'App Store Connect shows one iOS 1.0.1 crash on 2026-08-25, but device detail is insufficient and no crash report/stack is exposed for symbolication or root-cause verification.', 'Obtain the Organizer or diagnostic report, symbolicate, reproduce, fix, and re-smoke'),
    ('Open-Meteo promotion clearance', 'pending', 'Clarification email is drafted but has not been sent or answered', 'Send through an authenticated sender and record an unambiguous written response'),
    ('Android device smoke', 'partial', 'Signed phone 1.1.0 (7) passed physical API 25 clean install, live forecast, cold start, denied-location fallback, manual search, share, 150% text, TalkBack, cached-network fallback/recovery, contextual review-prompt dismissal/no immediate repeat, exact APK/signing identity, and cleanup. A scheduled cache refresh passed on the earlier debug candidate; physical tablet, widget, and Wear OS remain incomplete.', 'Run the signed RC on physical tablet, widget, and Wear OS; keep background evidence scoped to its tested artifact'),
    ('iOS physical smoke', 'blocked', 'A locally signed Release passed bounded physical iPad install, provider/cache population, widget-process startup, and cold launch, but the required iPhone is connected without DDI and cannot accept a development build.', 'Unlock and reconnect the iPhone, mount DDI, then run the remaining signed physical matrix')
) AS gates(gate, status, evidence, next_action);
