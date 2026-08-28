-- Reproducible bounded snapshot of the reported store-console baseline.
-- Values preserve each console metric as reported; they are not recomputed
-- across incompatible denominators.
SELECT *
FROM (
  VALUES
    ('App Store', 'Impressions', '206', 'reported_console_readout'),
    ('App Store', 'First-time downloads', '5', 'reported_console_readout'),
    ('App Store', 'Conversion rate', '4.05%', 'reported_console_readout'),
    ('App Store', 'Ratings', '0', 'reported_console_readout'),
    ('App Store', 'Crashes', '1', 'live_console_2026-08-28'),
    ('Google Play', 'Impressions', '779', 'reported_console_readout'),
    ('Google Play', 'Installations', '21', 'live_console_2026-08-28'),
    ('Google Play', 'First launches', '14', 'live_console_2026-08-28'),
    ('Google Play', 'Monthly active users', '11', 'live_console_2026-08-28'),
    ('Google Play', 'Conversion rate', '40.82%', 'reported_console_readout'),
    ('Google Play', 'Ratings', '1', 'reported_console_readout')
) AS baseline(platform, metric, value, evidence_class);
