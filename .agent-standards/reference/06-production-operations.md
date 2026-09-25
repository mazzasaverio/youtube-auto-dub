# Extended production operation checks

Load this reference for sensitive production changes or deployment incidents.

## Identity and data

- Resolve a Coolify resource from its stable resource identifier and type. Names
  can change on redeploy; image tags and source directories are not identity.
- Before a write, compare the live table list with the application schema, check
  a known table's expected count, and fetch a record already known to the owner.
  Stop if any result differs.
- For identity or key changes, column removal, or continuity risks, restore a
  read-only compressed production dump to temporary local PostgreSQL with the
  same major version. Run the real migration and seed, then verify counts, joins,
  orphan records, and new associations. For auth changes, also complete a local
  login against the restored copy.
- Keep the rehearsal copy until the authorized migration and its verification
  are complete.

## Runtime and deployment

- Verify behavior in the running process after environment changes and deploys.
  Queued actions and settings lists do not prove completion.
- Read only required deployment fields such as state, revision, timestamp,
  server, and resource. Raw payloads can contain build logs and secrets.
- Check whether values shown in the dashboard are preview-only or available in
  production. Report presence or masked comparisons without printing values.
- If a Compose build coincides with kernel OOM entries, separate CI work from
  Dockerfile commands. Reducing CI tests cannot lower memory use in a deploy that
  does not run those tests.
- Keep internal service checks on the Compose network. Proxy liveness should
  prove that the process accepts requests; dependency diagnostics can report
  secondary failures separately.

## Access

- Restrict dashboard access before creating API tokens. Use team-scoped,
  expiring tokens with only the necessary read or deploy permissions.
- When trusting client IP or country headers, verify both origin isolation and
  proxy replacement of client-supplied headers on the deployed path.
