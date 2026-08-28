-- Critical metric guardrails from the 2026-08-29 growth evaluation.
-- Unknown remains blocking until decision-eligible weekly console evidence exists.
SELECT *
FROM (
  VALUES
    ('ios_crash_free_sessions_pct', 'iOS crash-free sessions', 'unknown', TRUE, '>= 99.8%', 'block_scale', 'Attach the source-defined App Store crash-free-session metric for the same UZ evidence window'),
    ('android_user_perceived_crash_rate_pct', 'Android user-perceived crash rate', 'unknown', TRUE, '< 1.09%', 'block_scale', 'Import the Play Console UZ user-perceived crash rate for the same seven complete days'),
    ('android_user_perceived_anr_rate_pct', 'Android user-perceived ANR rate', 'unknown', TRUE, '< 0.47%', 'block_scale', 'Import the Play Console UZ user-perceived ANR rate for the same seven complete days'),
    ('android_phone_model_crash_rate_pct', 'Android phone-model crash rate', 'unknown', TRUE, '< 8%', 'review_required', 'Import decision-eligible concrete phone-model crash evidence and review the worst observed model'),
    ('android_phone_model_anr_rate_pct', 'Android phone-model ANR rate', 'unknown', TRUE, '< 8%', 'review_required', 'Import decision-eligible concrete phone-model ANR evidence and review the worst observed model'),
    ('wear_model_crash_rate_pct', 'Wear OS model crash rate', 'unknown', TRUE, '< 4%', 'review_required', 'Import decision-eligible concrete Wear OS model crash evidence and review the worst observed model'),
    ('wear_model_anr_rate_pct', 'Wear OS model ANR rate', 'unknown', TRUE, '< 5%', 'review_required', 'Import decision-eligible concrete Wear OS model ANR evidence and review the worst observed model'),
    ('open_policy_issues', 'Weekly store policy issues', 'unknown', TRUE, '= 0', 'block_scale', 'Import Apple and Google policy-issue counts for the same weekly UZ evidence window')
) AS guardrails(guardrail_id, guardrail, status, critical, threshold, unknown_policy, next_action);
