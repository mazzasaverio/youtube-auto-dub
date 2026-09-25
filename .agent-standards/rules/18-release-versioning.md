# Release versioning

## Applies when

Planning, publishing, or presenting a release in `ROADMAP.md`, `CHANGELOG.md`,
or Console.

## Required

- Use semantic versions `MAJOR.MINOR.PATCH`.
- Increment **Major** for breaking changes, mandatory migrations, removals,
  or fundamental product transformations.
- Increment **Minor** for a useful new capability compatible with existing behavior.
- Increment **Patch** for fixes, reliability, performance, accessibility, copy,
  or data changes that introduce no new core capability.
- If a release contains multiple change types, apply the highest increment.
- Assign versions by impact, not date, commit count, or number of changed files.
- Treat a release as a coherent user outcome. A single commit does not
  automatically require a new version.
- Show planned version, increment type, and expected outcome in the Roadmap.
- Record published version, ISO 8601 timestamp with timezone, name, useful change,
  impact, and acceptance evidence in the Changelog.

## Forbidden

- Using CalVer or dates as version numbers.
- Retroactively changing a communicated version without recording the migration
  and previous mapping.
- Calling a release Major just because it is large, or a breaking change Patch
  just because it contains little code.

## Verify

- Versions match `v?\d+\.\d+\.\d+` and increase in order.
- Roadmap and Changelog use the same next version.
- The type shown in Console matches the incremented component.
- The latest Changelog release has a verifiable date and time.

## References

- Document contract: [project documentation](https://github.com/mazzasaverio/ops/blob/a001ba70ab91bffa7143bf1f955107b17a1254fc/strategy/02-project-docs.md).
- SemVer specification: https://semver.org/lang/it/
