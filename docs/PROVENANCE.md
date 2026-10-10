# Provenance

- Upstream: https://github.com/openabdev/openab
- Fixed commit: `6431a1b6991673429f344acb78a58d94658d30fb`
- Upstream license: [MIT at this commit](https://github.com/openabdev/openab/blob/6431a1b6991673429f344acb78a58d94658d30fb/LICENSE), copyright 2026 openabdev.

The reviewed thread-session changes were originally built on a source snapshot
that already contained Slack mention/unlimited-mode changes, bounded network and
media handling, and owner-scoped model controls. Those prerequisites are
included as patch 0001 so this project can be applied to the fixed public
upstream commit without an unavailable private baseline. Patch 0002 contains
the subsequent thread-session/queue change and a portable Unix failure-test
fixture correction.

`source-manifest.json` records the exact upstream and final SHA-256 of every
affected source file. A null upstream hash denotes the new `slack_models.rs`
module. The prerequisite upstream files were read from the official repository
at the fixed commit and checked against the source snapshot's upstream hashes.
The two-patch reconstruction was verified against the reviewed final source.

The publication package does not include private deployment reports, local
service paths, runtime settings, agent session stores or the unverified native
adapter candidate. Synthetic identifiers and intentionally invalid token-like
strings in regression fixtures are test data, not credentials.
