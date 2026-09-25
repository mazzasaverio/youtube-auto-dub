# Git publication workflow

## Applies when

All repositories. Publication authorization is defined in `../AGENTS.md`.

## Required

- Publish related fixes, checks, and docs together. Split only independent
  outcomes or real risks; close regressions before publishing.
- Inspect worktree and branch. Exclude unrelated changes and preserve other
  sessions' work.
- Complete required tests, builds, migrations, and deployment checks before push.
- Push directly to the configured deployment branch, for example
  `git push origin <branch>:main`. A stale local deployment ref is not authoritative.
- On non-fast-forward rejection, fetch the deployment branch, confirm compatible
  intent and authorization, rebase, resolve conflicts, rerun affected checks, and
  push in order. Stop if intent conflicts or fast-forward remains impossible.
- Require CI for tests, lint, type checks, and builds on pull requests and the
  deployment branch. CI must work without production secrets; investigate
  unexpected credential requests before adding secrets.
- Verify shared services from outside their host. Use one release command to
  own push, deployment wait, and external verification when available.
- Record release notes, roadmap status, and relevant decisions before commit.
  Mark an increment deployed only after verifying the public deployment and the
  changed critical path.
- Use focused development checks and required candidate checks. Reuse only valid
  evidence; do not skip CI, security, or migrations.
- Keep one publication session per branch. Isolate authorized concurrent work;
  do not change another session's branch, index, or stash.
- Use versioned isolated fixtures. Parallelize independent checks only. Simulated
  AI responses test the UI, not the real model; do not claim token savings without
  measurements.
- When two local processes consume the same scheduled jobs, isolate their queue
  backend or namespace as well as their network ports. Prove the test process
  handled the job before attributing a missing event to application code.

## Forbidden

- Leave verified work uncommitted or unpushed without reporting a concrete block.
- Infer standing publication authorization when none was given.
- Force-push a deployment branch or bypass non-fast-forward rejection.
- Publish unrelated work or merge from an unrelated local branch.
- Open a pull request when direct publication was requested.

## Verify

- Complete [shared learning](../reference/03-continuous-learning.md) in the same session.
- Confirm the worktree contains only intended publication changes.
- Confirm the designated branch contains the current remote deployment branch.
- Confirm the final push succeeded as a fast-forward.
- Check deployment and application state when access is available; report missing
  access instead of claiming an unverified deployment.

## Reference

- [Efficient development cycle](../reference/02-efficient-development.md).
- [Observability](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/07-observability.md).
