# Rules router

The shared runtime owns authorization and documentation language. Operational rules
cannot authorize commits, pushes, deployments, or production changes. Load only
the rules relevant to the task.

## Task routes

1. API or domain architecture: `01-api-first.md`.
2. AI models: `09-ai-models.md`.
3. Authentication or authorization: `03-better-auth-nextjs.md`.
4. Production containers, databases, or migrations: `14-coolify-server.md`.
5. PDF or document sanitization: `17-document-sanitization.md`.
6. Metered API, storage, or public spending: `05-cost-guardrails.md`.
7. Project docs: `../strategy/02-project-docs.md`.
8. Email: `07-email-cloudflare.md`.
9. Owner notifications: `08-notifications.md`.
10. Requested publication or deployment: `15-git-merge-workflow.md`.
11. Frontend or UI: `10-frontend.md`.
12. Next.js, Docker, Prisma, or PostgreSQL: `02-nextjs-docker-prisma.md`.
13. Error tracking or alert webhooks: `12-observability-nextjs.md`.
14. Paid plans or access rights: `06-payments-stripe.md`.
15. Analytics, replay, consent, or privacy text: `04-privacy-consent.md`.
16. Public routes, SEO, or GEO: `11-seo-geo-nextjs.md`.
17. Security threats or incidents: `../strategy/07-security.md`, then the
    applicable rule.
18. Shell scripts: `13-shell-scripts.md`.
19. Mobile app store releases: `16-store-distribution.md`.
20. Roadmaps, changelogs, or versions: `18-release-versioning.md`.
21. Printable PDFs: `19-print-deliverables.md`.
22. Project startup or reusable components: `20-registry.md`.

Load references only when needed.

## Repository bootstrap

From an ops checkout, install into the actual target repository:

```bash
bash scripts/rules-sync.sh --install ../products/example --ci
```

Commit and publish the generated bundle before starting a cloud session.
Normal development needs no ops checkout or workstation home directory.

`AGENTS.md` is the agent entry point. Do not create a new `CLAUDE.md`; existing
Claude-specific instructions belong in `AGENTS.md`. Preserve any existing
`CLAUDE.md` and keep its `@AGENTS.md` import.

Do not distribute personal context. Map the six project document roles in
`../strategy/02-project-docs.md` before implementation. Competitor claims require
current research.

## Distribution checks

From `ops/`, run the non-destructive fleet check:

```bash
bash scripts/rules-sync.sh --check
```

It reports missing, changed, or stale bundles. In a product clone, run
`python3 .agent-standards/verify.py` for offline integrity checks.
Legacy `STANDARDS.lock` needs reviewed migration, not blind replacement.
See [distribution](../reference/08-agent-distribution.md) for profiles, safe
migration, skill adapters, and cloud acceptance tests.
