-- Rank evidence available in the initial 2026-08-28 baseline.
-- Google category/search rows are deliberately unknown until the fixed
-- three-profile monitor writes a comparable capture.
SELECT *
FROM (
  VALUES
    ('App Store UZ search', 'all', 'weather', '81', 10, 'fixed_public_capture'),
    ('App Store UZ Weather chart', 'official', 'category', '>100', 10, 'fixed_public_capture'),
    ('Google Play UZ Weather category', 'uz-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ Weather category', 'ru-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ Weather category', 'en-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ generic-query quorum', '2-of-3 profiles', 'five configured queries', '0 qualifying queries', 2, 'fixed_logged_out_capture')
) AS ranks(surface, profile, query, observed_rank, target_rank, evidence_class);
