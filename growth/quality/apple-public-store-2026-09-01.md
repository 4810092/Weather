# Apple public UZ store checkpoint — 2026-09-01

Status: **one public UZ rating is now observable; public release remains
1.0.1**.

At `2026-09-01T00:55:34+05:00`, a logged-out request to Apple's public lookup
endpoint for app `6799886897` and country `uz` returned:

- name `Nimbo Weather`;
- public version `1.0.1`, released at `2026-08-24T05:16:14Z`;
- `userRatingCount=1` and `averageUserRating=5.0`;
- `userRatingCountForCurrentVersion=1` and
  `averageUserRatingForCurrentVersion=5.0`;
- minimum OS version `15.0`.

Source:
<https://itunes.apple.com/lookup?id=6799886897&country=uz>. The complete JSON
response was 7,209 bytes with SHA-256
`ab8d71c169fe51db71e6440e3efa1d0df529e438a7cefb2e9dcb466bd52f5efd`.
The HTTP response date was `Mon, 31 Aug 2026 19:55:34 GMT`.

This is a point-in-time public storefront aggregate. It does not expose review
text, reviewer identity, acquisition source, sessions, retention, crash-free
sessions, or the App Store Connect review inbox. It also proves that build 6 is
not public: the storefront still serves `1.0.1`. No reply action is possible or
claimed from this source.
