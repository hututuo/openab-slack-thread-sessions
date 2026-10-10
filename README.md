# OpenAB Slack thread sessions

A small, independently maintained **patch project for [OpenAB](https://github.com/openabdev/openab)**. It is not a standalone Slack bot, an official OpenAB release, or an original replacement for OpenAB.

The patch improves persistent Slack-thread conversation routing and queues accepted work when all ACP execution slots are busy. The underlying OpenAB project provides the Slack transport, ACP harness, agent integrations and most of the implementation.

## What changes

- Conversation keys include the receiving workspace, channel and exact root message timestamp. Replies in one thread share its conversation; different threads remain isolated.
- FIFO admission keeps busy-capacity requests queued instead of dropping a batch with `pool exhausted`.
- Same-thread preprocessing preserves receive order in per-thread mode. Existing per-lane batching semantics are retained.
- Session reservations prevent idle eviction between setup and prompting.
- Failed native resume preserves the old Slack mapping rather than silently starting another conversation.
- Scoped model controls, bounded reconnect-event deduplication, persistence safeguards and regression tests are included.
- Explicit-mention routing and the existing unlimited-turn option are preserved. No new conversation-round cap is introduced.

## Status and limits

This is a reviewed source patch, not a deployment service or packaged binary. The tested source passed 588 core Rust tests, root `cargo check`, core/root Clippy and five Python migration tests. See [validation](docs/VALIDATION.md) for the exact scope.

With `pool.max_sessions = 1`, independent conversations **take turns**. This is not simultaneous execution. Capacity-two admission tests passed, but simultaneous real Antigravity text tasks have not been validated end to end. There is no enforced cross-process GUI/browser lock; raising capacity does not make sharing a desktop or browser profile safe.

Queued prompts and the bounded dedupe cache are in memory. Conversation mappings persist, but queued work is not a durable broker. Drain work before restart; do not blindly replay prompts with uncertain side effects. This patch does not repair Socket Mode connection-URL/network failures, and it does not promise exactly-once execution.

No `agy-acp` candidate, native agent binary, deployment-specific configuration or user data is distributed. Native agent resume support must be validated separately.

## Reproduce

Requirements: Git, Python 3, and the Rust/system dependencies required by upstream. Use a disposable source checkout, not a live installation. Run the following
commands from the parent directory containing this cloned patch repository.

```sh
git clone https://github.com/openabdev/openab.git openab-work
cd openab-work
git checkout --detach 6431a1b6991673429f344acb78a58d94658d30fb
cd ..
python3 openab-slack-thread-sessions/tools/apply_patches.py openab-work
python3 openab-slack-thread-sessions/tools/apply_patches.py openab-work --apply
cd openab-work
cargo test --locked -p openab-core --no-default-features --features slack
cargo check --locked --no-default-features --features slack
cargo clippy --locked -p openab-core --no-default-features --features slack --all-targets
```

The verifier stages and hash-checks both patches without changing the checkout by default. `--apply` copies only the 11 verified affected files. An unexpected baseline is rejected. For another upstream revision, rebase and retest instead of bypassing the checks.

Patch order:

1. `0001-slack-prerequisites.patch`: the earlier Slack/model-control/media-safety changes required by the reviewed baseline.
2. `0002-thread-session-queue.patch`: thread identity, admission, ordering, persistence/recovery safeguards and tests.

[Provenance](docs/PROVENANCE.md) explains the two-stage baseline. The second patch alone is not meant for a clean upstream checkout.

## Migration and safe rollout

[Migration guide](docs/MIGRATION.md) covers explicit legacy-key binding, backups, partial migration, restart and rollback. Never guess the channel owning a timestamp-only legacy key. The helper prepares candidates; it never installs them.

```sh
python3 tools/prepare_thread_migration.py STATE_DIRECTORY VERIFIED_BINDINGS_JSON NEW_CANDIDATE_DIRECTORY
python3 -m unittest discover -s tools -v
```

Bindings are local input, not repository content. Keep mapping files, session IDs, credentials, logs, browser profiles and downloaded documents private.

## License and attribution

[MIT License](LICENSE). Upstream copyright **Copyright (c) 2026 openabdev** is retained verbatim. See [NOTICE](NOTICE) for attribution and the scope of this derivative project.
