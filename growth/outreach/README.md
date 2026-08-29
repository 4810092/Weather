# Outreach operating rules

The 15 rows in [contact-research.csv](contact-research.csv) are a dated research shortlist, not permission to contact anyone. `verified_public_channel` means only that the outlet/community, its organizational submission route, and the linked editorial/activity hook were checked on public first-party pages on `verified_on`. It does **not** mean the outlet has agreed to receive or publish the pitch. Re-check every mutable channel and hook immediately before any owner-approved send; never enrich the list from private data brokers.

Before contact:

1. Confirm every scale gate in [../quality/gates.json](../quality/gates.json) is `pass`.
2. Re-verify the public contact route on the organization's official site or official social profile and update `verified_on`.
3. Open `hook_source_url` and confirm that the personalization sentence still accurately describes the public work or activity.
4. Select the Uzbek or Russian draft, re-check every factual claim, and replace every placeholder.
5. Obtain explicit approval to send. Send one message and at most one follow-up after 5–7 days; honor silence after that.

Never buy a list, scrape private addresses, mass-send, promise coverage/rank, offer an incentive for installs or reviews, or present an unverified address as confirmed.

The list deliberately uses editorial desks, organizational inboxes, official forms, or public community accounts. It excludes private contact details and personal journalist addresses even when an article byline exposes one.

## Personalized draft pack

[draft-manifest.csv](draft-manifest.csv) maps every verified shortlist row to
one concise, copy-ready first message and exactly one follow-up. The individual
files are indexed in [drafts/README.md](drafts/README.md). They are drafts only:
creating the files does not change `contact_status`, `last_contacted`, or
`follow_up_due`, and no message has been sent or staged in an external system.

The language in the manifest is selected from each row's
`preferred_language`. Every draft keeps the row's public organizational route
and `hook_source_url`; no private person, inferred address, or additional
contact detail has been added.
