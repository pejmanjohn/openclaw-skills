# Common Signatures

Use this page as a terse signature to next-action map.

## Contents

- Signature table
- Version drift
- Gateway and auth signatures
- Channel and node signatures
- Env and service signatures

| Signature or symptom | Next action |
| --- | --- |
| `Config invalid` / `Legacy config keys detected` | The gateway won't start with invalid config. Run `openclaw [--profile X] doctor --fix`. **Verify the fix persisted** by reading the config file back. If doctor didn't write the changes, migrate manually. |
| `device token mismatch (rotate/reissue device token)` | Use `openclaw [--profile X] dashboard` to get a tokenized URL. Don't connect manually through the bare dashboard page. Verify the URL port matches the actual gateway port. |
| `unauthorized: too many failed authentication attempts` | Auth lockout from accumulated failures (often crash-loop or port mismatch). Stop the gateway, fix root cause, restart fresh. Lockout state is in-memory and clears on restart. |
| `Gateway start blocked: set gateway.mode=local` | Run `openclaw [--profile X] config set gateway.mode local`, then restart. |
| launchctl shows exit code 1 + KeepAlive | Service is crash-looping. **Stop it immediately** (`openclaw [--profile X] gateway stop`) before diagnosing. Each crash may rack up auth failures. |
| CLI config path differs from service config path | Profile mismatch. Check plist env vars (`OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`). Use matching `--profile` flag for all CLI commands. |
| `doctor --fix` claims changes but config unchanged | Doctor may write to a different profile's config. Verify target file. If needed, migrate keys manually with a script. |
| command in docs is missing locally | Run `openclaw --version`, `openclaw help`, and the specific subcommand help. Treat as version drift first. |
| `gateway probe` fails | Open `gateway.md` and verify target, bind, service state, and auth expectations. |
| `doctor` reports blocking config issue | Open `config.md`, confirm `openclaw config file`, then validate the smallest fix. |
| dashboard or Control UI reaches host but gets unauthorized | Open `gateway.md` and `auth-and-pairing.md`; check token drift, device token, and origin policy. |
| channel connected but no replies | Open `channels.md`; separate transport from allowlist, mention, and pairing policy. |
| pairing required or approval pending | Open `auth-and-pairing.md`; resolve approval state before reconnecting. |
| `SYSTEM_RUN_DENIED` or exec suddenly asks for approval | Open `tools-and-nodes.md`; check `openclaw approvals get --gateway` or the node-specific approval state before changing config. |
| browser tool fails but session is otherwise healthy | Open `tools-and-nodes.md`; separate missing tool surface, dependency, approval, and node routing. |
| node feature fails after pairing | Open `tools-and-nodes.md`; check permissions and approvals, not just pairing. |
| camera or screen tool fails on a paired node | Open `tools-and-nodes.md`; verify node approvals and host OS permissions such as Camera or Screen Recording. |
| plugin install or tool registration changed after upgrade | Check local version and plugin compatibility, then inspect `tools-and-nodes.md`. |
| `package.json` missing `openclaw.extensions` | Inspect the plugin `package.json`, confirm the expected metadata is present, and compare plugin packaging against local `openclaw --version`. |
| behavior differs between shell and service | Check env and path overrides in `triage.md` and `auth-and-pairing.md`. |
