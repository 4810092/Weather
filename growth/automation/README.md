# Optional daily scheduling

[com.nimbo.growth-monitor.plist.example](com.nimbo.growth-monitor.plist.example) is an uninstalled macOS `launchd` template. Replace `__PYTHON_BIN__` and every `__REPO_ROOT__`, confirm the host timezone is `Asia/Tashkent`, then inspect the rendered plist before loading it yourself.

The template runs at 06:15 host-local time and writes operational stdout/stderr to `/tmp`, not the repository. `monitor_public_rank.py` refuses to overwrite an existing day, so duplicate invocations are visible rather than silent.

Do not add store credentials, cookies, API keys, email addresses, or console exports to the plist. Scheduling the public monitor does not authorize outreach, publishing, spend, or provider changes.
