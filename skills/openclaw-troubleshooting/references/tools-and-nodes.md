# Tools And Nodes

Use this page when exec, browser, plugin-backed tools, or node capabilities fail after the session otherwise appears healthy.

## Contents

- Separate the failure class
- Core checks
- Exec approvals
- Browser issues
- Nodes
- Plugins

## Separate the failure class

- Tool approval or policy problem
- Local executable or browser dependency problem
- Node is unpaired or offline
- Node is paired but lacks the required permission or capability
- Plugin or tool registration mismatch after install or upgrade

## Core checks

```bash
openclaw --version
openclaw help
openclaw logs --follow
openclaw doctor
openclaw approvals get --gateway
```

Then inspect the specific local help for the tool, node, or plugin surface that is failing.

## Exec approvals

If `exec` is denied, determine whether the failure is:

- gateway-side approval policy
- node-side approval policy
- missing local executable
- sandbox or permission restriction

Check the effective approval state before changing config:

```bash
openclaw approvals get --gateway
openclaw approvals get --node <id-or-name-or-ip>
```

Local approval state can also drift if `~/.openclaw/exec-approvals.json` differs from what the operator expects.

Do not treat an approval denial as a transport or pairing error.

## Browser issues

Browser failures often split into:

- browser tool not available in the installed version
- missing local browser dependency
- auth or secure-context problem in the target page
- node-hosted browser mismatch versus gateway-hosted browser execution

Use logs and local help output to identify where the browser action was supposed to run.

## Nodes

For node-backed features, separate:

- pairing state
- permission grant
- runtime reachability
- approval policy

A node can be paired but still unable to run a capability because permissions or approvals are narrower than pairing alone.

For camera or screen failures after pairing, verify both node approvals and OS-level permissions. On macOS, Screen Recording or Camera permission can block the capability even when pairing is healthy.

## Plugins

If a plugin exposes tools or nodes and install or runtime fails, confirm the installed plugin shape matches the local OpenClaw version. Version drift between plugin packaging and current runtime expectations is a common source of missing tools.

Start with the package metadata:

- inspect the plugin `package.json`
- confirm it includes the `openclaw.extensions` field expected by the installed runtime
- compare the plugin version and README against local `openclaw --version`

If the install error specifically says `missing openclaw.extensions`, treat that as a plugin metadata issue first, then rerun the same install or load step and verify the error disappears.
