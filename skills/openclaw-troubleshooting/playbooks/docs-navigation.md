# Docs Navigation

Use this playbook when local CLI output, logs, or config inspection tell you **what** is happening, but you still need the right OpenClaw doc page to understand intended product behavior, platform model, or the latest workflow.

## Core rule

OpenClaw docs are easier to navigate than they look because most pages include useful frontmatter near the top:

- `title` -> the page name
- `summary` -> one-line description of what the page is for
- `read_when` -> concrete situations that should trigger that page

Do not browse by filename guesswork alone when the docs corpus is large. Skim the frontmatter and use it to choose the right page quickly.

## Search strategy

### 1. Start local

Prefer the local docs tree first:

- `/opt/homebrew/lib/node_modules/openclaw/docs`

Use local docs when you want:
- the current installed docs set on this machine
- fast searching without browser noise
- a page path you can cite or open immediately

### 2. Match the symptom to a doc family

Rough map:

- Gateway runtime, service manager, reachability -> `docs/gateway/*`, `docs/cli/gateway.md`, `docs/platforms/*`
- Config keys, validation, schema, mutation -> `docs/cli/config.md`, `docs/gateway/configuration.md`
- Pairing, devices, channel approval -> `docs/channels/*`, `docs/cli/pairing.md`, `docs/cli/devices.md`
- Discovery, Bonjour, remote access, SSH, tailnet -> `docs/gateway/discovery.md`, `docs/gateway/bonjour.md`, `docs/gateway/remote.md`, `docs/network.md`
- Skills, plugins, load rules -> `docs/tools/skills.md`, `docs/tools/plugin.md`, `docs/tools/clawhub.md`
- Platform-specific service layout -> `docs/platforms/mac*`, `docs/platforms/linux.md`, `docs/platforms/windows.md`

### 3. Use frontmatter before full-body reading

When you find candidate files, inspect the first ~20 lines first.

You are looking for:
- whether the `summary` matches the problem class
- whether `read_when` explicitly matches the user’s situation
- whether the page is conceptual, CLI-oriented, or platform-specific

If a page’s `read_when` matches exactly, that page is usually the right one.

### 4. Only then read deeply

Once you have the right page:
- read the relevant section
- extract the intended behavior or workflow
- then return to local runtime truth (`openclaw help`, logs, config, running services)

Docs are for intended behavior. The installed CLI and machine state are still runtime truth.

## Practical search patterns

If you are using shell search over the docs tree, prefer searching for:
- the symptom class (`pairing`, `discovery`, `control ui`, `launchd`, `systemd`, `trusted-proxy`)
- the command family (`gateway`, `config`, `devices`, `pairing`)
- frontmatter keys (`summary:`, `read_when:`, `title:`)

Good workflow:
1. search by symptom or command family
2. inspect frontmatter in top matches
3. choose the page whose `read_when` best matches
4. read only the relevant section

## When docs are especially worth it

Open the docs early when:
- the platform/service-manager model matters
- a feature has multiple transports or modes (for example discovery, SSH, tailnet, direct WS)
- you need the canonical conceptual model (Gateway, pairing, node, control UI)
- local behavior might be version-drifted and you want the latest intended workflow

## Avoid these mistakes

- Do not use docs as proof that the installed CLI must support a command or flag.
- Do not read many pages deeply before checking their frontmatter fit.
- Do not let docs override local runtime truth when the local binary, logs, or config disagree.
- Do not search only by filename when the frontmatter already tells you which page to read.

## Mental model

Think of the docs corpus like a catalog with embedded routing hints.

The frontmatter tells you:
- what the page is about
- when to read it
- whether it is likely to answer this exact question

Use that routing metadata first, then dive into the page content.
