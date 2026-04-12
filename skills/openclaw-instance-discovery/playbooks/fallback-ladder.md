# Fallback Ladder

When discovery's native command and launchd phases find nothing, the skill must escalate through documented common locations before asking the user for help. This ladder ensures we never dead-end the user with "not found" and no next action.

The philosophy: **never dead-end the user**. If native discovery fails, we have last resort checks — and if those fail, we ask one tractable question that can move us forward.

## Overview

This escalation ladder walks through 6 steps in order:

1. **PATH checks** — common installation directories
2. **Config location checks** — where configurations typically live
3. **State directory checks** — where OpenClaw stores runtime state
4. **launchd plist files on disk** — check LaunchAgents and LaunchDaemons
5. **Listening ports** — is OpenClaw running but hard to find?
6. **Last resort user question** — one tractable question to help the user help us

## Step 1: Check PATH Issues

When the `openclaw` command is not found in PATH, it may still be installed in a non-standard location. Check these common installation paths:

```bash
ls -l /usr/local/bin/openclaw
ls -l /opt/homebrew/bin/openclaw
ls -l ~/.local/bin/openclaw
ls -l /Applications/OpenClaw.app/Contents/MacOS/openclaw
```

**What to look for:**
- Executables in any of these locations
- Symlinks pointing to the real binary
- Permissions issues (unexecutable files)

**Next action if found:**
- Add the directory to PATH or reference the full path
- Check the binary version: `<path>/openclaw --version`

**Next action if not found:**
- Continue to Step 2

## Step 2: Check Common Config Locations

Configuration files often reveal where OpenClaw expects to find its data or state. Check these locations:

```bash
ls -l ~/.openclaw/openclaw.json
ls -l ~/.openclaw-*/
ls -la ~/Library/Application Support/OpenClaw/
```

**What to look for:**
- JSON config files
- Numbered profile directories (e.g., `~/.openclaw-prod`, `~/.openclaw-staging`)
- Application support directories on macOS

**What to extract:**
- Look inside any config file for:
  - `state_dir` — where runtime state is stored
  - `gateway_port` — what port the gateway is listening on
  - `profile_name` — which profile is active

**Next action if found:**
- Inspect the config to find state directories or port numbers
- Continue to Step 3 to validate state exists

**Next action if not found:**
- Continue to Step 3

## Step 3: Check Common State Dir Locations

OpenClaw stores runtime state (sockets, process info, logs) in predictable directories. Check these locations:

```bash
ls -la ~/.openclaw/
ls -la ~/.openclaw-*/
ls -la ~/Library/Application Support/OpenClaw/state/
```

**What to look for:**
- `gateway.sock` — Unix socket for gateway communication
- `instance-*` directories — multi-instance state
- `logs/` directory — application logs
- `.lock` files or PIDs — signs of a running process

**Next action if found:**
- If you find sockets or logs, the instance exists but may not be running
- Continue to Step 4 to check for launchd configuration

**Next action if not found:**
- Continue to Step 4

## Step 4: Check launchd Plist Files on Disk

Even if `launchctl` doesn't show the service as active, plist files on disk may exist. Check these locations:

```bash
ls -la ~/Library/LaunchAgents/ai.openclaw*.plist
ls -la /Library/LaunchAgents/ai.openclaw*.plist
ls -la /Library/LaunchDaemons/ai.openclaw*.plist
```

**What to look for:**
- Plist files with labels like `ai.openclaw.service` or `ai.openclaw.gateway`
- Multiple profiles (e.g., `ai.openclaw.prod.plist`, `ai.openclaw.staging.plist`)

**What to extract from the plist:**
- `<key>ProgramArguments</key>` — the command being launched
- `<key>WorkingDirectory</key>` — where the process runs
- `<key>EnvironmentVariables</key>` — custom environment for this instance
- `<key>StandardOutPath</key>` / `<key>StandardErrorPath</key>` — log locations

**Next action if found:**
- Load the service manually: `launchctl load ~/Library/LaunchAgents/ai.openclaw.plist`
- Check the environment variables for `OPENCLAW_CONFIG_PATH`, `OPENCLAW_STATE_DIR`, `OPENCLAW_PROFILE`
- Continue to Step 5 to check listening ports

**Next action if not found:**
- Continue to Step 5

## Step 5: Check Listening Ports

OpenClaw may be running but hard to locate via normal means. Check what processes are listening for connections:

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -i openclaw
```

Also check for common gateway ports:

```bash
lsof -nP -iTCP:6000-7000 -sTCP:LISTEN
```

**What to look for:**
- Any process with "openclaw" in the name or command
- OpenClaw gateway typically listens on port 6000 (or higher if multiple instances)
- WebSocket connections on high-numbered ports

**What to do if you find it:**
- Note the port number and PID
- Try connecting to it via the discovered port
- Use `openclaw --url ws://127.0.0.1:<port> --token <token> status --all` to test connectivity

**Next action if found:**
- Confirm the instance by querying it
- Add it to the discovery results with the discovered port

**Next action if not found:**
- Continue to Step 6 (last resort)

## Step 6: Last Resort — Ask One Tractable Question

If all automated checks fail, we have one last resort: ask the user a focused, answerable question that helps us move forward.

**The question to ask:**

> "Do you know roughly where OpenClaw is installed or where you last ran it? This could be:
> - The directory where you ran `openclaw` from
> - A `/opt/` or `/usr/local/` path
> - Or a Homebrew path like `/opt/homebrew/`
>
> Any hint about the installation location will help us find it."

**Why this works:**
- Non-technical users can usually answer "where did I download it" or "where did I run it"
- The answer gives us a new starting point for directory walks
- It's a binary question that moves toward resolution

**What to do with the answer:**
- Walk the provided directory recursively for `openclaw` executables
- Check for state directories or config files relative to that location
- Re-run Steps 1-5 with the new information

## Philosophy: Never Dead-End

The last resort question ensures we never dead-end the user with:

> "OpenClaw not found. Try installing it."

Instead, we say:

> "We couldn't find it automatically, but here's what we've checked and here's what we need from you to keep looking."

This preserves the user's ability to resolve the issue without escalating to support or documentation.

