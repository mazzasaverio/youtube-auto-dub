# Shared learning in the same session

Owner decision of 2026-09-06, with the approved runtime distribution model of
2026-09-25. Required through [AGENTS.md](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/AGENTS.md) for every project and coding
agent following its instructions. This is not a background process: the agent
performs it during the work without waiting for another owner request.

## When it applies

For every development task, fix, incident, research task, or decision, assess
whether a reusable principle emerges: an error cause, missing control, API
contract, check, operating procedure, or owner correction. Two identical
incidents are not required before correcting a rule. A local preference or
unverified hypothesis does not become a global standard.

## Procedure

1. Before work, read the applicable kernel and relevant routed documents.
   Shared kernel authoring and distribution are defined in
   [agent runtime](07-agent-runtime.md); canonical `ops/AGENTS.md` owns the routes.
   Product agents use their pinned published bundle. New repositories also need
   the [repository bootstrap](../rules/README.md#repository-bootstrap).
   For skills and technical documentation, check the relevant immutable,
   reviewed bundled instructions and their compatibility with installed
   versions under the [shared knowledge policy](01-shared-agent-knowledge.md).
   This does not require a network refresh on every development task.
2. Formulate the principle with applicability, action, evidence, and limits.
   Separate observed fact from hypothesized explanation. Do not copy secrets,
   personal data, chat transcripts, or project commercial figures.
3. Find the document already owning the topic. Update it and resolve conflicts;
   add a reference only when detail is needed. Do not create a parallel rule or
   load the entire catalog into agent context.
4. Record the transfer and canonical path in the project's LOG. Keep local
   decisions and dated evidence there; put the invariant and conditions in the
   standard without imposing the originating product on everyone.
5. Verify documentation audit, links, and diff. After central changes, check
   distribution using the runtime's sync procedure. Repair missing bootstrap
   references and refresh affected compiled copies only within assigned scope
   and without overwriting concurrent work. Coordinate with the publication owner.
6. Commit and push only authorized source changes under the
   [Git workflow](../rules/15-git-merge-workflow.md). Briefly report what was
   generalized and any remaining distribution issue. Delegated work without
   publication authority is handed to its designated owner.

## Completion criterion

Work is not complete if an established reusable lesson remains only in chat or
an agent's personal memory. Do not make artificial changes when no new lesson
emerges: performing the assessment is sufficient.

If `ops` or the canonical source is unavailable, or a conflict prevents updating
it, record the lesson locally in the project's LOG with the canonical destination
and concrete blocker, pending canonical update. This satisfies local capture,
not completed propagation; it must not block unrelated implementation.

## Propagation and boundaries

The shared kernel is authored in `ops` under [agent runtime](07-agent-runtime.md)
and routed by canonical `ops/AGENTS.md`. A product's published `.agent-standards`
is a pinned compiled copy, not an immediate live view of central files. Central
edits require an explicit sync and publication of the updated product bundle;
do not claim they instantly affect every repository or inaccessible environment.
Repository `AGENTS.md` provides the local entry point; existing `CLAUDE.md`
imports it. Verify these entry points during bootstrap and distribution checks.

Updating guidance does not automatically modify application code or migrate
all applications. Apply a relevant rule after its updated bundle is synced;
a shared rollout needs its own scope, checks, and authorization. Preserve other
work in generated copies. The central source remains authoritative for authoring,
while a product's actual loaded revision remains pinned until synchronization.
