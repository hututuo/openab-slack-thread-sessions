# Migration and rollback

The old key `slack:<root timestamp>` does not identify a workspace or channel.
The new key is `slack:<workspace>:<channel>:<root timestamp>`. Timestamps must
remain strings; do not convert them through floating-point values.

1. Confirm each migrated legacy thread's receiving workspace, channel and root
   from verified thread/event evidence. Do not infer ownership from a timestamp.
2. Keep bindings in a private local JSON file, for example:
   `[{"team":"T123","channel":"C123","thread":"123.456"}]`.
3. Run `tools/prepare_thread_migration.py` with the current state directory,
   bindings file and a NEW candidate output directory. Review the candidate
   `thread_map.json`, `session_meta.json` and source hashes. The helper does not
   overwrite live state.
4. Migrate only the verified subset. Preserve unknown legacy records unchanged;
   they do not have to delay every other thread. If an incoming thread matches
   an unresolved legacy root, the runtime guard refuses that thread's ambiguous
   migration rather than silently discard its context.
5. Before replacing a live binary, finish or explicitly reconcile active and
   queued work, confirm downloads are complete, and arrange a brief maintenance
   window. This patch does not make the in-memory queue restart-durable.
6. Stop the service. Back up the existing executable and both state files with
   permissions/ownership retained. Recheck source hashes after stopping; if
   they changed, regenerate and review the candidates.
7. Install the reviewed binary and both matching state files while stopped.
   Verify hashes before restarting. If any replacement fails, restore the
   matching backup set before starting.
8. Start with capacity one and run authorized, harmless two-thread context and
   queue tests. Verify existing native session IDs were preserved, not just that
   the agent replied. Native resume failure retains the mapping for diagnosis.

Do not replace native agent binaries, token sources, browser settings or
unrelated configuration as part of this patch.

## Rollback

Before post-upgrade activity, stop the service, restore the matching old binary
and mapping/metadata backups, verify them, and restart.

After post-upgrade activity, preserve the NEW state before considering rollback.
An old backup may omit new sessions/model progress. Reverse migration must
check whether scoped keys collide on the same legacy timestamp; the old format
cannot represent those conversations safely. Never merge colliding identities
or blindly overwrite new state with an old backup.

## Capacity and connectivity

Capacity one provides isolated conversations with queued execution. Capacity
two can admit two independent turns, but live native text parallelism was not
validated. A shared desktop/browser must have one operator at a time; this
repository does not supply an enforced GUI lock. Do not treat a capacity
increase or a textual instruction to agents as resource isolation.

Socket Mode connection-URL/network errors are separate from an online, full
ACP pool. This patch addresses the latter's dropped batches, not connection
availability. Reconcile messages sent during an outage from actual receive and
reply evidence; restored connectivity is not proof of an empty queue.
