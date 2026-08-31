-- Reproducible bounded store-evidence snapshot based on the 2026-08-31 console
-- reads and the 2026-09-01 public Apple UZ rating/version lookup.
-- Apple overview values and selected Google global last-28-days dashboard
-- values are current read-only observations. Stale listing values are marked.
SELECT *
FROM (
  VALUES
    ('App Store', 'Impressions', '300', 'live_console_2026-08-31'),
    ('App Store', 'First-time downloads', '8', 'live_console_2026-08-31'),
    ('App Store', 'Conversion rate', '4.86%', 'live_console_2026-08-31_reported'),
    ('App Store', 'Ratings', '1', 'public_itunes_lookup_uz_2026-09-01'),
    ('App Store', 'Crashes', '2', 'live_console_2026-08-31'),
    ('Google Play', 'Impressions', '779', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Installations', '25', 'live_global_last_28_days_2026-08-31'),
    ('Google Play', 'First launches', '18', 'live_global_last_28_days_2026-08-31'),
    ('Google Play', 'Monthly active devices', '13', 'live_global_last_28_days_2026-08-31'),
    ('Google Play', 'Conversion rate', '40.82%', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Ratings', '1', 'carried_forward_2026-08-28_not_revalidated')
) AS baseline(platform, metric, value, evidence_class);
