# Shared agent runtime

## Always apply

- Follow the user's language in conversation. State the conclusion first.
- Write documentation in English in every repository, including agent instructions,
  plans, logs, and non-Markdown documents. Preserve exact identifiers, commands,
  URLs, and quotations. Do not change interface language or vendor content.
  This supersedes earlier repository documentation-language exceptions. Retroactive
  translation remains limited to ops and private repositories mapped in Console;
  do not start mass translations elsewhere.
- Preserve existing work and local conventions. Inspect actual files before edits;
  fix causes and avoid unrelated changes. Never stage another session's work.
- Protect secrets. Destructive production changes unrelated to the task need
  explicit authorization. Instructions and skills are not security boundaries.
- Use one canonical source. Generated standards are reviewed snapshots, not a
  second authoring location. Do not edit generated files to fix their checksums.
- No Markdown tables or em dashes in authored documentation. Prefer concise lists;
  move extended rationale to references.

## Task routing

Read `{{STANDARDS}}/rules/README.md` for implementation, then only relevant rules.
Do not load every rule, skill, or reference for every task.

- UI, UX, design engineering, or frontend: `{{STANDARDS}}/rules/10-frontend.md`.
  For new visual design use `ops-frontend-design`; for shadcn components use
  `ops-shadcn`; for accessibility checks use `ops-a11y-debugging`, when installed.
- Prisma queries: use installed `ops-prisma-client-api` and the database rule.
- Skills and changing technical facts: `{{STANDARDS}}/reference/01-shared-agent-knowledge.md`.
  Prefer reviewed project `ops-` skills over same-purpose global copies. Read the
  relevant skill entry point, not its entire upstream tree. Missing browser tools
  or skills must be reported; never claim unperformed checks.
- Follow project-specific product requirements and resolved dependency versions.
  Shared stack constraints do not authorize unsolicited framework migrations.

## Platform constraints

- Better Auth is the only authentication standard. Identity belongs to it;
  roles, permissions, ownership, plans, quotas, and access rights belong in the
  application database with server-side enforcement.
- Integrate Stripe directly through server APIs, normally hosted Checkout,
  Customer Portal, and signature-verified webhooks.
- Cloudflare Email Service is the only email delivery provider.
- Keep domain and service logic outside `src/app/`; use versioned API transports.
- Set explicit limits and rate limits for every metered call.

## Completion

- Gather evidence, make coherent increments, and start with focused checks.
  Diagnose wrapper errors from underlying responses with secrets redacted.
  Check official documentation when provider instructions no longer match.
- Run applicable tests, `git diff --check`, and for shell changes `bash -n` plus
  ShellCheck when available. For bundle changes run the offline verifier.
- Standing owner authorization of 2026-09-05 covers completion, verification,
  documentation, commit, and push to the configured publication branch, including
  ordinary triggered deployment. Follow `{{STANDARDS}}/rules/15-git-merge-workflow.md`;
  do not infer an ambiguous publication destination. Publish working increments.
- Assess reusable lessons in the same session under
  `{{STANDARDS}}/reference/03-continuous-learning.md`. Update ops when available;
  otherwise record a concise pending lesson in existing project documentation.
  The entire ops `context/` tree is private. Never copy its files or personal
  details into product repositories, public rules, skills, logs, or commits.
  Promote only reviewed, non-personal lessons and operational decisions.
- Report changes, checks, publication status, and unavailable validation honestly.

## Optional restricted source references

Only explicitly allowlisted standards are bundled. Pinned GitHub ops links outside
this bundle are optional restricted source references and may require authorized
repository access. Do not recursively copy or fetch referenced documents, including
private context. Inline code paths may also refer to optional, unbundled sources.
If a reference is unavailable, stop only the affected operation, report the missing
source, and continue independent work. Network access requires a separate explicit
permission and version check; installing or verifying this bundle is offline.
