# Retired local fallback scheduling

[com.nimbo.growth-monitor.plist.example](com.nimbo.growth-monitor.plist.example)
is an uninstalled macOS `launchd` fallback. The canonical unattended path is
the GitHub-hosted `Nimbo UZ daily rank monitor`; do not load this plist while
that workflow is active because two schedulers would race for the same day.
If hosted execution is intentionally retired, replace `__PYTHON_BIN__` and
every `__REPO_ROOT__`, confirm the host timezone is `Asia/Tashkent`, then
inspect the rendered plist before loading it yourself.

The template runs at 06:15 host-local time and writes operational stdout/stderr
to `/tmp`, not the repository. `monitor_public_rank.py` refuses to overwrite an
existing day, so duplicate invocations are visible rather than silent. It does
not share the hosted branch's parent-CAS, receipt, or non-force-push proof and
is therefore not an equivalent concurrent writer.

Do not add store credentials, cookies, API keys, email addresses, or console exports to the plist. Scheduling the public monitor does not authorize outreach, publishing, spend, or provider changes.
