# Common Signatures

Use this page as a terse signature to next-action map.

| Signature or symptom | Next action |
| --- | --- |
| command in docs is missing locally | Run `openclaw --version`, `openclaw help`, and the specific subcommand help. Treat as version drift first. |
| `gateway probe` fails | Open `gateway.md` and verify target, bind, service state, and auth expectations. |
| `doctor` reports blocking config issue | Open `config.md`, confirm `openclaw config file`, then validate the smallest fix. |
| dashboard or Control UI reaches host but gets unauthorized | Open `gateway.md` and `auth-and-pairing.md`; check token drift, device token, and origin policy. |
| channel connected but no replies | Open `channels.md`; separate transport from allowlist, mention, and pairing policy. |
| pairing required or approval pending | Open `auth-and-pairing.md`; resolve approval state before reconnecting. |
| browser tool fails but session is otherwise healthy | Open `tools-and-nodes.md`; separate missing tool surface, dependency, approval, and node routing. |
| node feature fails after pairing | Open `tools-and-nodes.md`; check permissions and approvals, not just pairing. |
| plugin install or tool registration changed after upgrade | Check local version and plugin compatibility, then inspect `tools-and-nodes.md`. |
| behavior differs between shell and service | Check env and path overrides in `triage.md` and `auth-and-pairing.md`. |
