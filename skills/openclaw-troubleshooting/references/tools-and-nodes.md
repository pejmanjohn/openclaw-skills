# Tools And Nodes

Use this page when exec, browser, plugin-backed tools, or node capabilities fail after the session otherwise appears healthy.

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
```

Then inspect the specific local help for the tool, node, or plugin surface that is failing.

## Exec approvals

If `exec` is denied, determine whether the failure is:

- gateway-side approval policy
- node-side approval policy
- missing local executable
- sandbox or permission restriction

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

## Plugins

If a plugin exposes tools or nodes and install or runtime fails, confirm the installed plugin shape matches the local OpenClaw version. Version drift between plugin packaging and current runtime expectations is a common source of missing tools.
