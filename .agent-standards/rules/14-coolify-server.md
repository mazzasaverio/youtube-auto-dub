# Coolify server operations

## Applies when

Inspecting or managing containers controlled by Coolify. Resolve hosts and database locations through
`platform/02-servers.md` and the credential inventory.

## Required

- Identify containers using `coolify.resourceName` and `coolify.type` labels.
  Names or image tags do not prove identity.
- Use the existing shared PostgreSQL service for new apps unless the inventory
  records an exception. Resolve its hostname with `POSTGRES_DB_HOST`; the new-app
  script creates a database, not a container.
- Treat `DATABASE_URL` as configuration, not proof of the destination. Verify
  environment-dependent behavior in the running process. Do not print secret
  values; report presence or masked comparisons.
- When an authenticated app changes host, update its router, Better Auth URL,
  OAuth callbacks, and old-host redirects together. Test both hosts externally.
- Trust proxy identity headers only when the origin cannot be reached outside
  the proxy and the proxy always replaces client-supplied values.
- Select deployment fields; raw responses may contain secrets. Verify service, revision and state on proxy failure.
- Run one-off scripts from the deployed app directory with its dependencies and
  connection. Use embedded IDs and unique constraints for idempotent writes.
- For Compose health checks, define checks in Compose or Dockerfiles, install the
  check command in the runtime, and use the container's internal port. Keep proxy
  liveness independent of secondary dependencies; expose full diagnostics separately.
- After creating a service, verify image version, published
  ports, proxy routes, and Docker networks before exposing it. Template defaults
  may differ.
- Verify file-storage mounts and loaded modules in every consuming container.
  API records do not prove actual bind mounts. Use persistent sources and
  read-only code mounts; see [GlitchTip](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/infra/glitchtip/README.md).
- Use Compose service names and networks for checks between containers. Do not
  route internal checks through public DNS, TLS, and the proxy.
- Prefer a runtime revision variable such as `APP_REVISION=${SOURCE_COMMIT}` to
  preserve image cache. Compose deployments can briefly interrupt service;
  `docker compose up` reconciles services without application-level rolling updates.
- Protect Coolify with HTTPS or private access before using API tokens. Use scoped, expiring team tokens; avoid `root`
  and `read:sensitive` unless necessary.
- Before automation, read
  [Coolify API observations](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/platform/reference/01-coolify-api.md).
- For build OOM, measure memory, swap and concurrency before retrying or
  attributing cause. Disk cleanup does not fix OOM.

## Forbidden

- Infer identity from names, tags, passwords, ports, size, or code structure.
- Change a database until identity, schema, expected counts, and a known record match.
- Run an irreversible or identity-bound production migration without evidence and snapshot.
- Assume production has `tsx`, a top-level `/app/node_modules`, or bundled `cuid`.
- Claim a runtime setting is active because Coolify lists it.
- Print, persist, or forward raw deployment payloads or secrets.

## Verify

Before database writes or migrations, compare tables with the app schema, a known
table count with its expected value, and a known record by ID, email, or slug.
For identity, primary-key, or data-continuity changes, rehearse on a local restore
of a read-only compressed production dump using the same PostgreSQL major version.
Verify preserved counts, valid joins, no orphans, and correct new links. Snapshot
production before the authorized migration, then verify the running process and
retain the rehearsal until verification ends.

## Reference

- Server inventory: `platform/02-servers.md`.
- [Extended production operation checks](../reference/06-production-operations.md).
- API limits: [dated observations](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/platform/reference/01-coolify-api.md).
- Provisioning and recovery: [new-app reference](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/scripts/new-app/README.md).
