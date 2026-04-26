# Auto-fix Allowlist

This file defines the bounded set of fixes that may be applied **without user approval** when this skill is invoked in authorized mode (`OPENCLAW_TROUBLESHOOTING_AUTHORIZED=1`, typically by `/openclaw-babysit --auto-fix`).

If a diagnosis does not match an entry below with high confidence, the skill must exit and alert without modifying anything.

## Inclusion criteria

A fix may be added to this allowlist only if all of the following hold:

1. **Unambiguous signature.** The live evidence pattern uniquely identifies one root cause. No other documented incident shares the same surface signature without a distinguishing secondary signal.
2. **Reversible.** The fix can be undone by re-running the same kind of operation (e.g. another restart) — it does not delete config, mutate persistent state, or rewrite user data.
3. **Idempotent or safely-repeatable.** Re-running the fix when the system is already healthy is a no-op or a benign cycle.
4. **No config edits.** Auto-fix never writes to `openclaw.json` or any persistent config file. Config-shaped signatures are the most prone to misclassification — they always go to the alert path.
5. **No privilege escalation.** No `sudo`, no `--no-verify`, no bypassing of safety checks.

## High-confidence rule

If two entries in the local incident log or shipped incident log share the same surface error string, **the signature is not high-confidence**. Exit and alert. Distinguishing them requires secondary evidence (file mtimes, process start time, runs counter delta, etc.) that the skill must check explicitly before deciding.

## Allowlist (current)

Each entry: signature, distinguishing check, fix block, verification.

### A1. Cached ESM module-load failure across multiple channels

**Signature:** `channel exited: The requested module 'openclaw/plugin-sdk/<X>' does not provide an export named '<Y>'` repeating across two or more channels with `auto-restart attempt N/10` ticking up; gateway pid alive; `gateway probe` returns `ok`.

**Distinguishing check (REQUIRED):** verify that the on-disk file at `<install-root>/dist/extensions/node_modules/openclaw/plugin-sdk/<X>.js` parses cleanly and that a fresh `node --input-type=module -e "import('openclaw/plugin-sdk/<X>')..."` from the extension directory succeeds. The disk file must be healthy *and* the running gateway must still error — otherwise this is not the cached-ESM pattern.

**Fix:**
```bash
openclaw gateway stop
launchctl print-disabled gui/$(id -u) | grep -q '"ai.openclaw.gateway" => disabled' \
  && launchctl enable gui/$(id -u)/ai.openclaw.gateway
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
sleep 12
openclaw gateway probe
```

**Verification:** `openclaw doctor` reports all enabled channels as `ok`, no `channel exited` log lines in the 30 seconds following the restart.

---

### A2. errno-5 trap: service stuck in launchd disabled list

**Signature:** `Bootstrap failed: 5: Input/output error` from `launchctl bootstrap` immediately after a successful `openclaw gateway stop`. `launchctl print-disabled gui/$(id -u) | grep openclaw` shows the service as `disabled`.

**Distinguishing check:** the `print-disabled` query must show the service as disabled. If not, this is a different bootstrap failure mode and must not be auto-fixed.

**Fix:**
```bash
launchctl enable gui/$(id -u)/ai.openclaw.gateway
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
sleep 12
openclaw gateway probe
```

**Verification:** `launchctl list ai.openclaw.gateway` returns a record with a numeric PID and `LastExitStatus = 0`; `gateway probe` returns `ok`.

---

### A3. Stale gateway lock files preventing start

**Signature:** Gateway fails to start after an in-session restart with lock-related errors; `$TMPDIR/openclaw-$UID/gateway.*.lock` files exist with a recent mtime but no matching live process.

**Distinguishing check:** `lsof` on the lock file shows no holder, AND `pgrep -f 'openclaw.*gateway'` returns no PID. If a live gateway is holding the lock, this is not the stale-lock pattern.

**Fix:**
```bash
rm -f "${TMPDIR%/}/openclaw-$(id -u)/gateway."*.lock
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist 2>/dev/null \
  || openclaw gateway start
sleep 12
openclaw gateway probe
```

**Verification:** `gateway probe` returns `ok` and no new lock-related errors in the next 30 seconds of logs.

## Explicitly NOT allowlisted

These patterns from the incident log are **not** auto-applicable:

- **Channel SecretRef crash loops driven by out-of-sync `channels.<name>.enabled` and `plugins.entries.<name>.enabled` flags** — applies to any channel. The documented fix is a config edit (`config set channels.<name>.enabled true` or the corresponding plugin disable), and config edits are never auto-applied in this skill. Additionally, the `unresolved SecretRef "file:..."` surface error is shared with the cached-ESM pattern (A1) and other plugin-load failures: an auto-fix that picked the wrong root cause would move a bad install to a worse one. Always exit and alert for SecretRef-shaped errors regardless of which channel produced them.
- **Bundled-plugin `node_modules` not staged after `openclaw update`.** The fix involves running `pnpm install --prod` inside extension directories. Network-dependent, version-sensitive, and the per-extension enumeration logic should be run with human eyes on the output.
- **Anything requiring `sudo`** (LaunchDaemon migration, system-level reconfig).

## Adding entries

Auto-fix allowlist additions belong in PRs to this repo, not in `local/memory/`. The local incident log can record the signature and the manual fix; promotion to the allowlist requires verifying the inclusion criteria above against multiple incidents and cannot be done from a single user's environment.
