# Registry: a shared starting point for projects

**Established:** 2026-09-20. Facts checked against shadcn documentation on that date.

## Applies when

Starting a new project, building something reusable in an existing project,
or considering copying code between projects.

## The registry

`~/projects/lib/registry`, GitHub `mazzasaverio/registry`, is private. This is an
optional, access-dependent integration for repositories authorized to use it,
not a prerequisite for consuming these public standards. The `shadcn` CLI treats
it as a registry through its root `registry.json`. It distributes any file, not
only React components: configuration, documents, rules, workflows, agents, and skills.

```bash
pnpm dlx shadcn@latest list mazzasaverio/registry
pnpm dlx shadcn@latest init mazzasaverio/registry
pnpm dlx shadcn@latest add mazzasaverio/registry/<elemento>
pnpm dlx shadcn@latest registry validate mazzasaverio/registry
```

Because it is private, the CLI tries anonymous access, then falls back to
`GH_TOKEN` or `GITHUB_TOKEN`. Without a token, installation fails rather than
degrading. If access is unavailable, record the integration limitation and
continue unrelated implementation without requesting or exposing private context.

## Required

When using this integration:

- **Start new projects from the registry.** Before writing configuration,
  documents, or components from scratch, check existing items with `list`.
- **Reusable work enters the registry in the same session** in which it emerges,
  generalized and stripped of references to its originating project. State this
  in the summary. Follow [shared learning](../reference/03-continuous-learning.md):
  reusable knowledge must not remain buried in one project. If access blocks
  transfer, record the pending canonical update locally.
- **Admit an item only after at least one real use.** A registry full of unused
  items obscures what is active and becomes another place for knowledge to decay.
- **Update `registry.json` and validate** with `registry validate` in the same
  commit that adds or changes an item's files.
- Keep ownership separate: `ops/rules/` owns written standards, `ops/scripts/`
  operational automation, and the registry starter code and files. Do not
  duplicate a procedure between these locations.

## Forbidden

- Treating an installed item as a runtime dependency. Once copied, it becomes
  project-owned code and the copies diverge: the same contract as shadcn/ui in `10-frontend.md`.
- Copying code between projects without going through the registry when using
  this integration. Divergent copies without a declared origin are debt, not reuse.
- Putting secrets, personal context, or project data in items. The repository
  is private today, but items also land in public repositories.

## Verify

- With access, `pnpm dlx shadcn@latest registry validate mazzasaverio/registry` exits without errors.
- A new item has been installed in a real project at least once before being
  declared stable in the registry README.
- The registry README lists its contents and what it deliberately does not yet contain.

## References

- GitHub registry: https://ui.shadcn.com/docs/registry/github
- Overview: https://ui.shadcn.com/docs/registry
- Six document roles: `../strategy/02-project-docs.md`
- [Repository bootstrap](README.md#repository-bootstrap)
