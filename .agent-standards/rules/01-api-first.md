# API-first application architecture

## Applies when

Building or changing an application with users, user-facing operations, or a
credible future non-web client base.

Capabilities live in versioned HTTP APIs; the web is a client.

An internal tool may defer public transport until the second client, but must
retain domain and services. Record exceptions and reconsideration triggers in
`strategy/02-project-docs.md`.

## Required

- Keep business behavior independent of the client:
  - `src/lib/domain/`: pure rules without framework, Prisma, storage, or network imports.
  - `src/lib/services/`: use cases and the only layer accessing Prisma or R2.
  - `src/app/api/v1/`: handlers that parse input, authorize, call a service, and serialize.
  - `src/app/`: thin UI calling the same services as API handlers.
- Expose every user-facing capability through `/api/v1/...`.
- Keep arithmetic in code and ask models only for judgments.
- For assignments across intervals, check constraints across the entire interval:
  a local choice may leave avoidable empty results.
- For filters affecting health or safety, test variants, negations, and
  substitutes; state free-text limitations without certifying their absence.
- Create records with every field needed for visibility.
- One module owns limits, prices, and model instructions.
- Use the transport in `03-better-auth-nextjs.md` for consistent web and non-web session semantics.
- Export Zod request and response schemas from `contracts/`, using JSON inputs and outputs.
- Limit bodies before parsing and during streaming, without trusting
  `Content-Length`. Stop polling and waits when the request is aborted.
- Use opaque string IDs, UTC ISO-8601 timestamps, cursor pagination, and stable JSON errors.
- Honor `Idempotency-Key` for repeatable mutations.
- GET does not create data, grant authority, opt into processing, or consume
  resources. Link credentials may only reduce authority or revoke consent.
  Other browser mutations require a mutating method and origin or CSRF checks.
- Scope every bearer token to its declared direction and action. A token for
  revocation, cancellation, or unsubscribe does not authorize the reverse action.
- Before passing a client-supplied URL to a library or server request, enforce
  protocol, length, and an exact trusted-host allowlist. Syntactic `https:`
  validity alone does not prevent SSRF to arbitrary destinations.
- Use parameterized database APIs and signed R2 URLs for file transfers.
- After publishing a native client, make only additive changes to `/api/v1`.
  Put breaking changes in `/api/v2`, with a documented deprecation window.

## Forbidden

- Business rules in route handlers, server actions, components, or client-only code.
- Duplicated limits, prices, prompts, or free and paid business rules.
- Web-only capabilities without equivalent API operations.
- HTML errors under `/api/`, breaking changes to published versions, or streaming
  file bytes when signed object URLs suffice.

## Verify

- Mentally remove `src/app/`: business behavior must remain.
- Run API contract tests for status codes and JSON schemas.
- Test names containing spaces and encoded characters in the browser: avoid
  double encoding between routes and APIs.
- Test anonymous, unauthorized, malformed, and wrong-owner requests.
- Test external origins on browser mutations and local, private, credential-bearing,
  and non-allowlisted URL destinations on outgoing requests.
- Repeat each idempotent mutation with the same key and confirm no duplicate work.

## References

Use `03-better-auth-nextjs.md` for authentication transport and
`strategy/02-project-docs.md` for architectural exceptions.
