-- Baseline-versus-target percentages used in the growth control room.
-- The Play conversion and launch-rate reads remain directional until their
-- source populations and time windows are reconciled.
SELECT *
FROM (
  VALUES
    ('Apple conversion', 'Baseline', 0.0405),
    ('Apple conversion', 'Target', 0.1500),
    ('Play conversion', 'Baseline', 0.4082),
    ('Play conversion', 'Target', 0.3500),
    ('First launch / install', 'Baseline', 0.6667),
    ('First launch / install', 'Target', 0.8000)
) AS drivers(metric, series, rate);
