-- Required goal-surface evidence from the canonical 2026-08-31 UZ capture at
-- 2026-08-31T02:51:00+05:00. Goal evidence is complete. The separately
-- monitored Apple search for `Toshkent ob-havo` returned only one unique app,
-- so overall diagnostic capture is incomplete; that non-goal row is omitted.
SELECT *
FROM (
  VALUES
    ('App Store UZ search', 'all', 'weather', '88', 10, 'fixed_public_capture'),
    ('App Store UZ Weather chart', 'official', 'category', '40', 10, 'fixed_public_capture'),
    ('Google Play UZ Weather category', 'uz-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ Weather category', 'ru-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ Weather category', 'en-UZ', 'category', '>30', 10, 'fixed_logged_out_capture'),
    ('Google Play UZ generic-query quorum', '2-of-3 profiles', 'five configured queries', '0 qualifying queries', 2, 'fixed_logged_out_capture')
) AS ranks(surface, profile, query, observed_rank, target_rank, evidence_class);
