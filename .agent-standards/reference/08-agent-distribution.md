# Portable agent standards

## Architecture

Ops is the only authoring source. Product repositories commit generated snapshots
so cloud and mobile sessions can start from their Git clone without local paths,
network bootstrap, or a second repository. Only the shared runtime is inlined in
root `AGENTS.md`; rules and references load on demand. Skills expose short safe
entry points and keep upstream material under `upstream/`.

- `reference/07-agent-runtime.md`: canonical always-loaded policy.
- `scripts/agent-bundle.json`: explicit public-safe file allowlist and profiles.
- `.agent-standards/`: generated rules, references, manifest, offline verifier.
- `.agents/skills/ops-*`: Codex adapter.
- `.claude/skills/ops-*`: Claude adapter with the same reference payload.

The entire ops `context/` tree is private, including nested references, not only
`context/01-preferences.md`. Never publish it to public repositories or distribute
it in product bundles, even private ones. The distributor rejects context paths
even if accidentally added to its explicit allowlist. Do not bypass this by
renaming files or copying their contents into rules, skills, logs, or commits.
Promote only reviewed, non-personal operational decisions and reusable lessons;
never personal circumstances, private evidence, or identifying details.
Keep the ops repository private. Path checks do not detect paraphrased personal
information, so content review remains required before publication.

No personal context, production inventory, credentials, or recursive platform
copy belongs in the bundle. Unbundled Markdown links become revision-pinned ops
links; code-formatted paths remain literal. Missing restricted references block
only operations that need them, not unrelated frontend work.

## Installation and updates

Commit reviewed source changes before distribution. From an ops checkout:

```bash
bash scripts/rules-sync.sh --list
bash scripts/rules-sync.sh --install ../products/example --ci
bash scripts/rules-sync.sh --check ../products/example
```

Replace the example with the actual repository path. `--write` aliases install;
`--install-all` targets discovered immediate Git repositories under sibling
products, labs, lib, and services. Prefer individual installs after reviewing
repository status. Installation is not publication and does not choose a branch.

In a product clone, without ops or network:

```bash
python3 .agent-standards/verify.py
```

`--ci` installs an optional pinned-checkout workflow that runs this verifier.
Integrity checks detect edits and missing files, not whether a model obeyed rules
or whether the snapshot is the latest ops release. Source freshness requires
`--check` from ops. Unrelated ops commits do not invalidate bundles.

Automatic profiles inspect root dependencies and `components.json`. `base` has
rules only; `web` adds frontend-design, shadcn, and accessibility; `prisma` adds
Prisma Client. For monorepos or missed stacks, commit `.agent-profile.json`:

```json
{"profiles": ["web", "prisma"], "skills": []}
```

Profiles are additive. Add only skills with reviewed redistribution rights.
Updates preserve local text outside the managed AGENTS markers and refuse edited
generated files, collisions, unsafe paths, and uncommitted source inputs.
Handled failures attempt rollback; this is not crash-safe transactional storage
or a concurrent-writer lock. Run one synchronizer per repository.

## Agent discovery

Do not create a new `CLAUDE.md`. Modern Claude supports `AGENTS.md`; existing
Claude instruction files can change discovery precedence, so the installer
preserves them and adds relative AGENTS imports. Older clients may need upgrading.
Codex discovers repository `.agents/skills`; Claude uses `.claude/skills`.
Zed native first-match instruction files can shadow AGENTS; resolve reported
conflicts rather than assuming all agent loaders behave identically.

The runtime routes relevant tasks to namespaced skills explicitly. Discovery and
following instructions remain model/client behavior, not an enforcement boundary.
Keep tests, CI, permissions, secret isolation, and deployment controls independent.

Official references:

- [Claude cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web)
- [Claude memory](https://code.claude.com/docs/en/memory)
- [Claude skills](https://code.claude.com/docs/en/skills)
- [Codex instructions](https://developers.openai.com/codex/guides/agents-md)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Zed instructions](https://zed.dev/docs/ai/instructions.md)
- [Agent Skills specification](https://agentskills.io/specification)

## Migration and publication

Legacy `STANDARDS.lock` and `.claude/rules/` are not silently deleted. An old
snapshot may include local rules or edited generated files. Compare each file to
its recorded source, preserve unknown or modified content, move valid local rules
to their intended location, and remove only proven obsolete generated material.
Until resolved, the verifier reports the legacy lock as a conflict.

Inspect status, staged changes, remote ownership, publication branch, and existing
commits before rollout. Never include unrelated changes, force-push, or publish a
third-party clone just because discovery found it. Dirty repositories require an
isolated reviewed increment or a reported blocker. A local installation does not
help mobile sessions until its commit reaches the branch they clone.

Test each increment with fixtures and offline verification. Then start a fresh
Claude cloud session and a fresh Codex session against the published branch. Ask
them to identify the policy, choose the relevant UI skill, and perform a small
change with appropriate checks. Local checksum tests cannot prove cloud discovery.
Record client versions and results; do not describe this acceptance test as passed
until those sessions actually run.

When ops is unavailable, record reusable lessons in existing project documentation
as pending promotion. Review them into the canonical source and redistribute;
never turn generated snapshots into independently maintained rule sets.
