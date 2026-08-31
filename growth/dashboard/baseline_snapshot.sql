-- Reproducible bounded store-evidence snapshot as of 2026-08-31.
-- Apple overview values are current read-only observations. Google values and
-- Apple ratings are carried forward from 2026-08-28 and explicitly marked.
SELECT *
FROM (
  VALUES
    ('App Store', 'Impressions', '300', 'live_console_2026-08-31'),
    ('App Store', 'First-time downloads', '8', 'live_console_2026-08-31'),
    ('App Store', 'Conversion rate', '4.86%', 'live_console_2026-08-31_reported'),
    ('App Store', 'Ratings', '0', 'carried_forward_2026-08-28_not_revalidated'),
    ('App Store', 'Crashes', '2', 'live_console_2026-08-31'),
    ('Google Play', 'Impressions', '779', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Installations', '21', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'First launches', '14', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Monthly active users', '11', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Conversion rate', '40.82%', 'carried_forward_2026-08-28_not_revalidated'),
    ('Google Play', 'Ratings', '1', 'carried_forward_2026-08-28_not_revalidated')
) AS baseline(platform, metric, value, evidence_class);
