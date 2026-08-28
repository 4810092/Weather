-- Required goal-surface evidence from the fixed 2026-08-29 UZ capture.
-- The goal surfaces are complete. The separately monitored Apple search for
-- `Toshkent ob-havo` returned only one unique app and is not represented here.
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
