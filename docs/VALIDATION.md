# Validation scope

The reviewed final OpenAB source snapshot was validated in an isolated macOS
source checkout on 2026-10-10:

- 588 core Rust tests passed, including 17 new thread/session regressions.
- Root `cargo check`: exit 0.
- Core and root Clippy: exit 0.
- Migration helper: five Python unit tests passed.

Rust checks used the pinned lockfile, offline dependencies, no default
features, and the `slack` feature. Local listeners were enabled for mock
transport fixtures. An existing `/bin/false` assumption failed on that host;
the final patch uses `/bin/sh -c false` in that test only. No production
secret-execution behavior was changed by that fixture correction.

Publication preparation additionally checked the ordered patches against the
fixed upstream files and compared all 11 reconstructed file hashes with the
reviewed source. The Python migration tests were rerun on the publication copy.

These are source/fixture results, not a promise of live Slack or native-agent
behavior. This package does not claim a completed production rollout. Native
Antigravity resume and simultaneous real-agent text execution remain outside
the reported acceptance. GUI/browser mutual exclusion is not implemented.

Covered by the new tests: scoped Slack keys/reply coordinates, retry dedupe,
ingress order including cancellation, independent thread admission, capacity-one
queueing, reservation release, persisted mapping reload with a mock ACP agent,
legacy-key refusal, corrupt-store preservation, and zero-capacity failure.
Existing model/reset tests also remain in the full suite.

No Windows build or cross-platform matrix was run. Tests containing Unix shell
and Python fixture paths require corresponding host tools. No full upstream
workspace/all-features or native `agy-acp` suite is claimed.
