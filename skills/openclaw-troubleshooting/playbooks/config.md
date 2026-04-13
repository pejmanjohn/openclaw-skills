# Config

Use this page when behavior suggests OpenClaw is reading a different config than expected, the config is invalid, or changes are not taking effect.

## Contents

- Active config path
- Validation flow
- Safe edits
- Schema and get workflow
- Env override confusion

## Active config path

Start with:

```bash
openclaw config file
openclaw config --help
openclaw doctor
```

The active path is the first fact to anchor. Do not edit `~/.openclaw/openclaw.json` blindly if `openclaw config file` points elsewhere.

## Validation flow

Use local help to confirm available verbs, then prefer the narrowest inspection commands the installed binary supports:

```bash
openclaw config get <path>
openclaw config schema
openclaw config validate
openclaw doctor
```

If `config validate` is unavailable locally, fall back to `openclaw help`, the specific `config --help` surface, and `openclaw doctor` for schema and startup failures.

## Safe edits

Before proposing or applying a config change, read `playbooks/config-writing.md` and follow it strictly.

Short version:
- confirm the active file path first
- propose the exact narrow change first
- back up before writing
- prefer one small change at a time
- run `openclaw config validate` immediately after the change
- revert immediately if validation fails
- verify the intended file and value actually changed

## Schema and get workflow

Suggested order:

1. `openclaw config file`
2. `openclaw config get <specific.path>`
3. `openclaw config schema`
4. edit the file or use supported set or unset commands
5. `openclaw config validate`
6. `openclaw doctor`
7. `openclaw gateway status` or the failing feature command

## Env override confusion

Config may look correct while runtime behavior still follows environment overrides. Check:

- `OPENCLAW_HOME`
- `OPENCLAW_STATE_DIR`
- `OPENCLAW_CONFIG_PATH`
- `.env` files in the working directory or state directory
- service-manager environment such as `launchctl` or systemd

If the current shell and the background service do not share the same environment, treat that as the primary bug.
