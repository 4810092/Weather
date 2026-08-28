-- Scale gates are fail-closed. Unknown is not treated as pass.
SELECT *
FROM (
  VALUES
    ('iOS crash gate', 'blocked', 'App Store Connect shows one iOS 1.0.1 crash on 2026-08-25, but device detail is insufficient and no crash report/stack is exposed for symbolication or root-cause verification.', 'Obtain the Organizer or diagnostic report, symbolicate, reproduce, fix, and re-smoke'),
    ('Open-Meteo promotion clearance', 'pending', 'Clarification email is drafted but has not been sent or answered', 'Send through an authenticated sender and record an unambiguous written response'),
    ('Android device smoke', 'partial', 'Signed phone 1.1.0 (7) passed physical API 25 clean install, live forecast, cold start, denied-location fallback, manual search, share, 150% text, TalkBack, cached-network fallback/recovery, contextual review-prompt dismissal/no immediate repeat, exact APK/signing identity, and cleanup. A scheduled cache refresh passed on the earlier debug candidate; physical tablet, widget, and Wear OS remain incomplete.', 'Run the signed RC on physical tablet, widget, and Wear OS; keep background evidence scoped to its tested artifact'),
    ('iOS physical smoke', 'blocked', 'The exact Apple 1.1.0 (5) archive installed on a physical iPad but launch was blocked by the device lock and the app was removed; the earlier 1.0.1 (4) Release passed bounded physical iPad provider/cache/widget/cold-launch paths. The required iPhone is currently unavailable; its previous connection had no mountable DDI.', 'Unlock the iPad and reconnect the iPhone, mount DDI, then run the remaining signed physical matrix')
) AS gates(gate, status, evidence, next_action);
