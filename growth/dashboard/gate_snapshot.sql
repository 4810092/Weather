-- Scale gates are fail-closed. Unknown is not treated as pass.
SELECT *
FROM (
  VALUES
    ('iOS crash gate', 'blocked', '1 crash on iOS 1.0.1 on 2026-08-25; no stack trace available', 'Obtain the Organizer/diagnostic report, symbolicate, reproduce, fix, and re-smoke'),
    ('Open-Meteo promotion clearance', 'pending', 'Free endpoint is documented for non-commercial use; no written promotion clearance attached', 'Obtain written clearance or approve a separately costed licensed endpoint'),
    ('Android device smoke', 'partial', 'Final debug APK passed localized quick-city selection, live forecast, and cold start on API 24/36 emulators and physical API 25, plus physical search. The immediately preceding runtime-identical candidate passed API 24 offline recovery; signed tablet, share, background, and accessibility coverage remains incomplete', 'Run the versioned signed RC on the remaining tablet, share, background, and accessibility matrix'),
    ('iOS physical smoke', 'blocked', 'Release passed iOS 18.1 simulator and bounded physical iPad live-provider/cold-launch paths; the required iPhone is connected without a mountable Developer Disk Image', 'Unlock/reconnect the iPhone, mount DDI, then run denied-location, search, offline, share, VoiceOver, widget, and cold-start paths')
) AS gates(gate, status, evidence, next_action);
