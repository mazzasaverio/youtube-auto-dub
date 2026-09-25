---
paths: scripts/**/*.sh
---

# Shell script conventions

## Applies when

Creating or changing Bash scripts in `scripts/`.

## Required

- Start with `#!/bin/bash` and `set -euo pipefail`.
- Set `export DEBIAN_FRONTEND=noninteractive` for unattended package operations.
- Make reruns safe. Guard installations and one-time changes with checks such
  as `command -v`, directory tests, or current-state comparisons.
- Keep configurable values near the top, for example `SSH_PORT=2222` and `USERNAME=deploy`.
- Quote variable expansions as `"$VAR"` unless intentional splitting is documented and verified.
- Clone Oh My Zsh directly with Git instead of running its remote installer.
  Redirect stdin from `/dev/null` when a command might consume pipeline or terminal input.
- On Ubuntu 24.04, account for `ssh.socket`. To change the SSH port, override it
  with both `ListenStream=0.0.0.0:PORT` and `ListenStream=[::]:PORT`, for IPv4 and IPv6.
- Keep scripts non-interactive and fail with useful error messages.

## Forbidden

- Unbounded prompts or commands waiting for input during automation.
- Unquoted expansions of paths, secrets, or user-controlled values.
- Remote installation scripts executed directly from the network.
- Changes that fail or duplicate configuration on the second run.
- SSH socket changes binding only IPv4 or only IPv6 unless explicitly requested.

## Verify

- Run `bash -n <script>`.
- Run ShellCheck when available and review every suppression.
- Run the script twice in a disposable or staging environment: the second run
  must succeed without duplicating state.
- For SSH changes, keep the current session open, verify both listeners, and
  test a new connection before disconnecting.

## References

None.
