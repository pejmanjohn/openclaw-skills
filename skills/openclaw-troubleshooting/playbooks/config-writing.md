# Config Writing

Use this playbook before proposing or applying any OpenClaw config change.

The goal is not just to change config. The goal is to change the **right** config, in the **smallest** safe way, with a clean rollback path if validation fails.

## Core rule

Never batch-write the entire `openclaw.json`.

Do not overwrite the whole config file when a narrow key-level change will do. Prefer `openclaw config set` / `openclaw config unset` when possible. If file editing is unavoidable, change the smallest possible part of the active config file.

## Required sequence

### 1. Resolve the active target first

Before any config mutation:
- identify the active profile if one exists
- identify the active config file with `openclaw config file`
- do not assume `~/.openclaw/openclaw.json` is the file that matters

If the machine has multiple profiles or services, verify you are editing the config actually used by the runtime you are troubleshooting.

### 2. Read before writing

Before changing anything:
- read the current value
- confirm the key path exists or that creating it is intended
- understand whether the change is meant to affect runtime behavior, validation, or service startup

### 3. Propose the exact narrow change first

Before writing, state exactly:
- the key path to change
- the old value when known
- the new value
- why this change is needed

For broad or behavior-changing edits, get explicit user approval before writing.

### 4. Back up before mutation

Before applying the change:
- create a backup of the active config file

The backup should be simple and local so you can restore it immediately if validation fails.

### 5. Make the smallest reversible edit

Rules:
- one change at a time
- avoid opportunistic cleanup during incident response
- prefer `config set` / `config unset` over manual file editing
- do not mix multiple speculative fixes into one mutation

### 6. Validate immediately

After every config change, run:

```bash
openclaw config validate
```

If the runtime uses a non-default profile, use the matching profile on the validation command too.

If `config validate` is unavailable on the installed binary, use the narrowest local validation surface available (`openclaw config --help`, `openclaw doctor`, or the exact failing command), but `config validate` is the preferred path.

### 7. Revert immediately on validation failure

If validation fails:
- restore the backup immediately
- do not continue with more edits
- do not restart the gateway on a known-invalid config

### 8. Verify persistence

After validation succeeds:
- read the changed key back
- confirm the intended file actually changed
- confirm you did not accidentally edit the wrong profile's config

### 9. Then continue to runtime checks

Only after the config is valid and confirmed should you move on to:
- `openclaw doctor`
- `openclaw gateway status`
- `openclaw gateway probe`
- the exact failing feature path

Restart or reload only if the changed setting actually requires it.

## Do / Don't

### Do
- use the active config path, not assumptions
- propose exact key-level changes
- back up before mutation
- validate immediately
- revert on failure
- verify the value persisted

### Don't
- rewrite the whole config file
- edit first and inspect later
- mutate multiple unrelated settings in one step
- keep going after validation failure
- assume the default profile is the one in use

## Mental model

A config change is successful only when all of these are true:
1. you changed the right file
2. you changed the right key
3. the config still validates
4. the intended runtime now sees that change

Anything less is just moving risk around.
