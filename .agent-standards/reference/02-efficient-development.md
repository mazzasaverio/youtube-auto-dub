# Efficient development and operational context

Updated on 2026-09-09 at the user's request: reduce redundant preparation,
repeated documentation attempts, and scope changes while preserving checks and
quality. Applies through the [Git workflow](../rules/15-git-merge-workflow.md).
It does not expand authorization or reduce mandatory controls.

## Default workflow

1. Define one outcome with a few observable behaviors to verify. For a focused
   fix, three to five criteria usually suffice without requiring a formal plan.
2. Load relevant context and reproduce the reported case. Make the first change
   once the cause and boundaries are sufficiently clear.
3. Implement and immediately test that behavior. Expand investigation only when
   the result, dependencies, or risk require it.
4. Run required checks once on the final candidate. Repeat checks invalidated
   by changes or failures; do not rerun green checks without a reason.
5. Update relevant documentation in one pass, then commit and push the complete
   increment when authorized. Reuse check results that remain valid.
6. Verify CI and deployment for the exact commit. While waiting, complete only
   useful, independent, already-authorized work, without concurrent writes to
   the publication branch or scripts deployment can interrupt. Conclude by
   distinguishing verified outcomes from remaining limitations.

Record a separate defect discovered during work with evidence and a next step,
while honoring authorized commitments. Finish the current increment first unless
the defect makes it incorrect or creates an urgent data, security, or payment
risk. Do not start a platform-wide audit for a UI change.

## Avoid unnecessary cycles

Origin of the September 9 revision: the user reported 24 minutes for a Clarity
diagnosis expanded into landing-page fixes. Three pushes repeated builds and
deployment waits, including two stages of the same fix. This sequence motivated
the Git rule change; it is not a measurement of individual stage durations.

- Communicate the first diagnosis as soon as evidence supports it, without
  waiting for release. A question about why a problem occurs must not remain
  unanswered during a broader review authorized in the same conversation.
- A coherent outcome can include multiple files and related fixes. Prepare it
  with targeted tests, then one final build and push, not a build and deployment
  for every hypothesis or tweak. A defect found in tests stays in the same candidate.
- Before repeating a check, ask what change invalidates the green result.
  Repeat only affected checks; CI and mandatory gates remain unchanged.
- Reuse existing harnesses and fixtures. Create a new harness only if the
  existing one cannot verify the concrete risk without distortion.
- If a focused fix exceeds ten minutes, reassess scope: what is necessary,
  what is further investigation, and where time is spent waiting. This is a
  process check, not a deadline permitting skipped verification. Explain the
  concrete reason for remaining time and continue necessary work.
- Prefer CI/deployment notifications or polling at 30-60-second intervals.
  Once commit, artifact, and published behavior are verified, stop checking.
  Do not start new audits merely to fill waiting time.

## Before editing

- Define an observable outcome and acceptance criteria for the increment.
  A small change must remain understandable and independently functional.
  Keep strictly necessary UI, API, tests, and documentation together; separate
  unnecessary broad refactors. Do not substitute fixed file or line counts for judgment.
- Read applicable instructions in full when required. During the same task,
  reuse instructions already read and still in context unless the source changed
  or rereading is mandatory. After context loss, a summary does not replace
  instructions requiring direct reading.
- Use the rules router and relevant skills, not entire catalogs or manuals.
  Check the applicable immutable, reviewed bundled skills and documentation
  against the project's installed versions. Reading instructions is required;
  refreshing them over the network on every development task is not. Follow
  the [shared procedure](01-shared-agent-knowledge.md) for review and updates.
- Search with `rg`; open the affected implementation, callers, and tests.
  Expand reading as dependencies emerge without reprinting known whole files.
- Read content directly in complete sections with sufficient output. Copying
  a file to a temporary location is not reading it. If output is truncated,
  retrieve the missing section before editing it or applying its rules.

## Operational state, not a transcript

In the existing LOG or equivalent, record only what is needed to resume:

- **Goal:** current increment, completion criteria, and non-goals.
- **State:** implemented and missing work; reference branch and commit.
- **Files:** a few relevant paths and links to authoritative decisions.
- **Checks:** command, outcome, verified revision or changes, known limitations.
- **Operations:** any active runners, CI/deployment IDs, and their status.
- **Next step:** concrete action, actual blocker, or remaining decision.

A few lines suffice for small tasks, without a minimum word count or new document.
Omit unnecessary fields. No secrets, production payloads, or history copies.
Before resuming, compare recorded state with the actual worktree, remote, and
processes. “Implemented,” “tested,” “pushed,” and “live” are different states;
a canceled check is not a success.

## Verification at two stages

1. During development, run the smallest check able to detect the regression:
   a case-specific test, type-check, or affected-flow check.
2. On the final candidate, run checks required by the project and risk. For
   documents only: audit, links, and diff; do not start an application build
   without real dependencies on documents. For UI: affected viewports and
   interactions, relevant accessibility. For logic: unit tests and applicable
   integration tests. For auth, data, billing, and migrations: retain every
   specific check.

Previous evidence is reusable only if relevant code, dependencies, configuration,
fixtures, and environment are unchanged. A merge invalidates checks affected by
integrated changes. A CSS change requires checking the affected layout; it does
not automatically require retesting the database. When uncertain, expand checks.
Do not reduce mandatory CI gates.

Depth follows concrete risk: for copy or layout, check relevant rendering,
localization, and accessibility; for interactions, reproduce the regression and
edge states; for authentication, quotas, payments, migrations, and production
writes, retain integration, isolation, and data checks required by the rules.
Do not add tests that merely repeat the implementation.

Reuse compatible runners and caches. Keep a single heavy build or app instance
when sufficient; never run tests concurrently if they clean the same database.
For a green test, read the summary and exit code. For failure, open the relevant
log without truncation hiding the error; retain local artifacts when useful.
Capture only useful screenshot states and inspect them before concluding.

### Identify the target before browser tests

- State whether the browser verifies the current worktree, a recreated local
  container, or a precise production revision. A reachable port does not prove
  the process serves the newly compiled code.
- Before Playwright against Docker Compose, compare the running container's
  image ID with the freshly built image ID and wait for the health check.
  A successful build does not imply replacement of an existing container.
- For a change limited to one service, rebuild and recreate only that service
  with `--no-deps --force-recreate`. Rebuild the frontend/backend pair when the
  shared contract, authentication, common configuration, or protocol changes,
  not for a single CSS tweak.
- Order checks from cheapest to most expensive. During iteration, use static,
  unit, and targeted smoke tests; run production builds and long E2E tests on
  the coherent candidate. Do not play a complete game after every edit.
- If an E2E fails before reaching the changed behavior, stop: fix the target,
  fixture, or precondition before attributing failure to the product. A test
  against the wrong revision produces no evidence.
- Prefer semantic locators, accessible names, domain state, or explicit test IDs.
  Update tests in the same increment when markup changes; do not couple them
  to purely visual classes or incidental CSS structures.
- In apps with polling or persistent connections, `networkidle` may never occur:
  navigate to `domcontentloaded`, then wait for the element or response proving
  the required behavior. A network-idle timeout does not prove data failed to load.

## Proportionate documentation

- Write first in the source already owning the topic. A general lesson adds a
  rule only if not already covered; otherwise local evidence and a reference
  suffice. The required assessment remains mandatory.
- Check the document budget before adding content. If space is insufficient,
  condense in one pass or move detail to a reference. Do not increase the limit
  to pass the audit or repeatedly trim a few words at a time.
- For documents only, run audit, links, and diff; no application build. After
  central changes, check distribution once: repair relevant non-conflicting
  compiled copies within assigned scope, reporting unrelated backlog without
  turning it into refactors of other apps. Follow [shared learning](03-continuous-learning.md)
  for pinned-copy synchronization and unavailable canonical sources.

## Coordination and publication

- When parallel work is authorized, assign non-overlapping scopes and separate
  worktrees. This document does not authorize new agents or sessions.
- One owner integrates and publishes to the deployment branch; others must not
  push concurrently to that branch. Check the remote before pushing. Separate
  worktrees isolate the index, not publication order.
- If uncoordinated work appears on the same files, preserve it and clarify
  ownership before editing. Do not use a global stash to bypass the conflict.
  Integration and Git rejections follow the canonical rule.
- Publish the coherent candidate once, avoiding cosmetic pushes that cancel
  running CI. Do not defer an urgent fix to save a build. Check the exact commit's
  results, not just the latest run.
- Use product waits/events and reasonably spaced summary polling without hiding
  state from the user. Stop only your own unnecessary runners; preserve data
  and artifacts needed for recovery.

## Measure before adding tools

For slow tasks, record development, test, build, and deployment duration, repeated
build count, and causes. Use token counts only when supplied by the tool; printed
words or lines do not demonstrate real savings. Compare similar tasks, not
invented percentages. Prefer reuse and clear module boundaries over abstractions
or frameworks introduced without a demonstrated bottleneck.

## Technical reference

[Google Engineering Practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html),
consulted on 2026-09-05: independent, focused changes, related tests, and a working
build. The context log and release coordination above are local operating choices,
not requirements attributed to Google.
