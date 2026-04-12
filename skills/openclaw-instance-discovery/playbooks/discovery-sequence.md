# Discovery Sequence

This playbook is the operational core of the `openclaw-instance-discovery` skill.
It describes the six phases an agent follows to locate, cluster, verify, and confirm
all Gateway instances present on a machine. The ground truth for OpenClaw's service
model, config layout, and env-var contract is at https://docs.openclaw.ai — consult
that reference when any step below produces unexpected output.

Run the phases in order. Do not skip a phase because a previous phase produced
partial results; every phase adds independent evidence that later phases depend on.

---

## Contents

- [Phase 1: native OpenClaw overview](#phase-1-native-openclaw-overview)
- [Phase 2: documented service-manager discovery](#phase-2-documented-service-manager-discovery)
- [Phase 3: candidate clustering](#phase-3-candidate-clustering)
- [Phase 4: explicit per-candidate verification](#phase-4-explicit-per-candidate-verification)
- [Phase 5: human-facing summary](#phase-5-human-facing-summary)
- [Phase 6: minimum confirmation](#phase-6-minimum-confirmation)

---

## Phase 1: native OpenClaw overview

Ask the OpenClaw binary itself what it knows. These commands produce machine-readable
JSON that Phase 3 uses to seed candidate identities.

```sh
# Confirm the binary is present and record the version string.
openclaw --version

# Query the Gateway the CLI considers "current". --deep forces a live probe
# rather than returning a cached status; --json emits a structured object.
openclaw gateway status --deep --json

# Ask the gateway whether it is reachable. Captures port, token, and
# profile name in the JSON envelope.
openclaw gateway probe --json

# Print the absolute path of the config file currently in use.
openclaw config file

# Read the gateway.port key from the active config.
openclaw config get gateway.port
```

**What to capture from each command:**

| Command | Fields to record |
|---|---|
| `openclaw --version` | version string |
| `openclaw gateway status --deep --json` | `port`, `profile`, `state`, `pid`, `token` |
| `openclaw gateway probe --json` | `ok`, `latencyMs`, `port`, `token` |
| `openclaw config file` | absolute config path |
| `openclaw config get gateway.port` | port number (may differ from running instance if config was edited) |

**Relationship to triage:** The triage playbook runs `openclaw gateway probe`
(bare, no flags) and `openclaw status` as quick-health checks. Phase 1 uses
`openclaw gateway status --deep --json` and `openclaw gateway probe --json` instead:
the `--deep` flag forces a live connection test rather than reporting cached state,
and `--json` emits a structured object that Phase 3 can parse without heuristic
text scraping. Phase 1 is therefore a superset of what triage collects about the
gateway, not a duplicate — but if the user already has triage output, you can skip
to Phase 2 after cross-referencing the port and token values.

---

## Phase 2: documented service-manager discovery

The launchd layout is the documented way OpenClaw registers persistent Gateway
processes on macOS (see https://docs.openclaw.ai). Each registered instance has a
`.plist` file under `~/Library/LaunchAgents/` whose label begins with `ai.openclaw`.

### Step 2a — enumerate running services

```sh
launchctl list | grep openclaw
```

Record every service label that begins with `ai.openclaw`. Example output:

```
123   0   ai.openclaw.gateway
456   0   ai.openclaw.gateway.work
```

The first column is the PID (or `-` if not running), the second is the last exit
code, the third is the label.

### Step 2b — list plist files

```sh
ls ~/Library/LaunchAgents/ai.openclaw*.plist
```

Compare the set of plists with the set of running labels from Step 2a. A plist with
no matching running label means the instance is installed but not currently started.
A running label with no plist is unusual; note it but do not discard it.

### Step 2c — inspect each plist for env-var overrides

For every plist file found, extract the `EnvironmentVariables` dictionary. The
canonical env vars that determine instance identity are:

| Variable | Purpose |
|---|---|
| `OPENCLAW_PROFILE` | Selects the named profile from the config file |
| `OPENCLAW_CONFIG_PATH` | Absolute path to the config JSON used by this instance |
| `OPENCLAW_STATE_DIR` | Directory where the Gateway writes its runtime state |
| `OPENCLAW_GATEWAY_PORT` | Port the Gateway listens on (overrides `gateway.port` in config) |

Read each variable with PlistBuddy:

```sh
# Replace <plist> with the absolute path to the file.
/usr/libexec/PlistBuddy \
  -c "Print :EnvironmentVariables:OPENCLAW_PROFILE" \
  -c "Print :EnvironmentVariables:OPENCLAW_CONFIG_PATH" \
  -c "Print :EnvironmentVariables:OPENCLAW_STATE_DIR" \
  -c "Print :EnvironmentVariables:OPENCLAW_GATEWAY_PORT" \
  <plist>
```

If a key is absent, PlistBuddy exits non-zero and prints `Does Not Exist`. That is
not an error — it means the instance inherits the default for that variable.

### Step 2d — read the token from the state directory

Each instance writes an auth token to its state directory. If `OPENCLAW_STATE_DIR`
was found in Step 2c, check for a token file there:

```sh
cat "${OPENCLAW_STATE_DIR}/gateway.token"
# or, if using the default location:
cat ~/.openclaw/state/gateway.token
```

**Relationship to triage:** The triage playbook inspects ONE plist (the default
one) to confirm the service label and gather basic env-var context. Discovery
enumerates ALL plists and reads every env var relevant to multi-instance
differentiation. Triage stops when it has enough to diagnose a single problem;
discovery keeps going until it has a complete picture.

**Future scope — Linux systemd:** On Linux, OpenClaw instances register as systemd
user units (`~/.config/systemd/user/openclaw-gateway*.service`). The equivalent of
Step 2a is `systemctl --user list-units 'openclaw-gateway*'`. Step 2c reads env
overrides from `Environment=` and `EnvironmentFile=` directives in the unit file.
This playbook covers macOS launchd only; Linux support is a future extension.

---

## Phase 3: candidate clustering

A "candidate" is a coherent set of signals that all point to the same Gateway
process. The goal of this phase is to group the raw evidence from Phases 1 and 2
into one candidate per distinct instance.

### What constitutes a candidate identity

Five signals can link evidence to the same instance:

1. **Service label** — the launchd label (e.g. `ai.openclaw.gateway.work`).
2. **Config path** — the absolute path to the config JSON (`OPENCLAW_CONFIG_PATH`
   or the path printed by `openclaw config file`).
3. **State directory** — the directory where the instance stores runtime files
   (`OPENCLAW_STATE_DIR`).
4. **Port** — the TCP port the Gateway listens on (`OPENCLAW_GATEWAY_PORT`,
   `gateway.port` in config, or the port reported by `openclaw gateway probe --json`).
5. **Profile name** — the named profile within a config file (`OPENCLAW_PROFILE`
   or the `profile` field in `openclaw gateway status --deep --json`).

### Clustering procedure

1. Start a new candidate for each plist file found in Phase 2.
2. For each candidate, fill in the five signals from the plist env vars and the
   token file in the state directory.
3. Cross-reference with Phase 1 output. If the port or config path from Phase 1
   matches a candidate, record the Phase 1 token and PID against that candidate.
4. If Phase 1 reported a running gateway whose port does not match any plist,
   create an additional candidate representing that "unknown origin" instance.

### Deduplication rule

A Mac app install (`/Applications/OpenClaw.app`) and its corresponding launchd service (e.g., `ai.openclaw.gateway`) are the **same instance**, not two. The Mac app is packaging; the launchd service is the Gateway. Do not count them separately.

Similarly, an OpenClaw CLI binary is a client that connects to a Gateway — it is not a separate instance. Nodes, plugins, and other client applications are also not instances.

**Only count distinct Gateway processes** — identified by distinct (service label + port + config path) combinations. If two evidence sources point at the same port and config path, they are the same instance.

The number of candidates after clustering MUST equal the number of entries you write to `instances.json`. If you find 2 distinct Gateways, write 2 entries and announce "I found 2 instances." Never inflate the count.

### Neutrality rule

Do not infer human semantics from signal values. A profile named `"personal"` is
not necessarily used for personal tasks; a config path containing `"work"` is not
necessarily a work instance. Record values verbatim. The human-facing summary in
Phase 5 presents the signals; the user decides what they mean.

Do not assume specific profile names, ports, or directory names. Any number of
candidates is valid, including zero (nothing is installed) or one (single instance).

---

## Phase 4: explicit per-candidate verification

For each candidate identified in Phase 3, verify it is actually reachable by
connecting directly to its port with its token. Do not rely on
`openclaw gateway probe --json` without the `--url` flag here — that command asks
whichever instance the CLI considers "current", which may not be the candidate you
intend to test.

### Why `--url` + `--token` instead of `--profile`

`--profile X` routing is empirically unreliable in multi-instance setups. The CLI
uses the profile name to resolve which gateway to contact, but if two instances
share a config file or if the profile routing table is stale, the wrong instance
may respond. The `--url` + `--token` combination bypasses profile resolution
entirely and talks directly to a known address with a known credential.

### Verification command

```sh
openclaw gateway probe --json \
  --url ws://127.0.0.1:<candidate-port> \
  --token <candidate-token>
```

Replace `<candidate-port>` and `<candidate-token>` with the values recorded for
this candidate in Phase 3. If `--token` is not accepted by the installed version,
fall back to `--profile <candidate-profile>` but note the limitation in the summary.

### What to record from the probe response

```jsonc
{
  "ok": true,          // false means the gateway did not respond
  "latencyMs": 12,
  "port": 7700,        // confirm this matches candidate-port
  "profile": "work",   // confirm this matches candidate-profile (if known)
  "version": "1.4.2"   // record for the summary
}
```

If `ok` is `false`: the instance is installed but not running. Record confidence as
`"installed-not-running"` and continue to the next candidate. Do not treat this as
fatal.

If the command itself fails (e.g. unknown flag `--url`): note the installed version
and fall back to `openclaw [--profile <candidate-profile>] gateway probe --json`.
The `--profile` flag routes by name rather than by address, which may give a false
positive in multi-instance setups; record this caveat.

---

## Phase 5: human-facing summary

After verifying all candidates, produce a plain-language summary that the user can
read without knowing OpenClaw internals. No jargon, no raw JSON.

### Single-instance example

```
I found one OpenClaw Gateway on this machine.

  Port:    7700
  Profile: default
  Status:  running (latency 8 ms)
  Config:  ~/.openclaw/config.json
  State:   ~/.openclaw/state/

This is the instance that responds when you run `openclaw` commands without
any flags.
```

### Multi-instance example

```
I found two OpenClaw Gateways on this machine.

  Instance A
    Port:    7700
    Profile: default
    Status:  running (latency 6 ms)
    Config:  ~/.openclaw/config.json
    State:   ~/.openclaw/state/

  Instance B
    Port:    7701
    Profile: work
    Status:  running (latency 9 ms)
    Config:  ~/.openclaw/work/config.json
    State:   ~/.openclaw/work/state/

Instance A appears to be the default (it uses the standard config path).
Instance B has a separate config and state directory.
```

Keep the language neutral. Do not say "your personal instance" or "your work
instance" — use Instance A / Instance B, or the profile names verbatim, until the
user assigns human labels.

---

## Phase 6: minimum confirmation

Save the discovered instances to the registry (see `registry-contract.md`) only
after asking for the minimum confirmation required. Three cases:

### Single-instance, high confidence

Confidence is "high" when at least three of the five signals (label, config path,
state dir, port, profile) are consistent and the Phase 4 probe returned `ok: true`.

Action: auto-save as `default` with no question to the user. Announce:

> Saved one instance as "default". Run `openclaw gateway probe --json` to
> confirm it is reachable at any time.

### Single-instance, medium confidence

Confidence is "medium" when fewer than three signals are consistent, or the Phase 4
probe returned `ok: false` (installed but not running).

Action: ask one yes/no question before saving:

> I found what looks like one OpenClaw instance (port 7700, profile "default").
> Save it as "default" in the registry? [y/N]

### Multi-instance

When there are two or more candidates (regardless of confidence):

Action: present the summary from Phase 5, then ask the user to confirm the
assignment:

> I found 2 instances. Save them as:
>   "default"     → Instance A (port 7700, profile "default")
>   "instance-2"  → Instance B (port 7701, profile "work")
> Confirm? [y/N]

Auto-label as `default` for the instance that matches the default config path (or
the lowest port if ambiguous), and `instance-2`, `instance-3`, … for the rest. Do
not invent human-meaningful names. The user can rename entries in the registry after
confirmation.

After saving, print the absolute path of the registry file so the user knows where
the data lives.
