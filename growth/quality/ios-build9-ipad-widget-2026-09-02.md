# iPad build-9 widget render — 2026-09-02

Status: **PASS for one visible medium-widget render on the connected physical
iPad; NOT A COMPLETE iOS PHYSICAL OR TESTFLIGHT PASS**.

## Bounded observation

At `2026-09-02 20:05:54 +05:00`, Xcode's physical-device screenshot action
captured the Home Screen of the connected iPad mini (5th generation), iPadOS
26.6.1. The Nimbo medium widget was visibly rendered for Tashkent and showed
current temperature, daily high/low, precipitation, and AQI rather than an
empty, placeholder, or error surface.

The repository retains only a deterministic pixel crop of the Nimbo widget so
that unrelated Home Screen content is not published. No pixels inside the crop
were retouched or generated.

| Artifact | SHA-256 |
| --- | --- |
| `growth/quality/evidence/ios-physical-2026-09-02-build9-widget.png` | `4f735e0bb09655c7ae45513cb9138316a5b497c97f273b9907a97e72942ff092` |

The uncropped local screenshot remains outside Git. Its SHA-256 is
`c0945633f5951d6c1208e43a1ba4b9d35b7b75a3fe34df4`, which binds the crop to
the operator's original local evidence without publishing unrelated device
content.

## Identity and fail-closed boundary

The installed Nimbo bundle reported version `1.1.0 (9)` and used the freshly
changed bundle path
`27709EF4-03C5-466E-AD67-8BF8BE8BC7D1/Nimbo.app`. Both the app and widget
processes were alive immediately before this capture, and the system crash-log
domain contained zero current `Nimbo-*` files. CoreDevice still classified the
bundle as `builtByDeveloper=true`, so this observation is not relabelled as a
TestFlight or distribution-signed result.

This evidence proves only the visible render. It does not prove widget tap/open,
share-sheet presentation, TestFlight identity, iOS 15 compatibility, physical
watch behavior, post-delivery crash-free sessions, review, rollout, or public
availability. The iOS physical and crash gates remain blocked.
