# Next.js, Docker, and Prisma 7

## Applies when

Changing Next.js TypeScript code, Prisma 7 PostgreSQL configuration, or an
application's Docker and Coolify deployment behavior.

## Required

- In Node 22, convert every Node.js `Buffer` passed to a Web API `Response` into
  `Uint8Array`. For example, wrap `renderToBuffer()` output with `new Uint8Array(buffer)`.
- With Prisma 7, `@prisma/adapter-pg`, and pnpm, construct the adapter from
  configuration: `new PrismaPg({ connectionString, connectionTimeoutMillis, idleTimeoutMillis })`.
- Let `@prisma/adapter-pg` manage its own pool. Keep direct `pg` imports out of
  `prisma.ts` unless a separate, reviewed use case requires them.
- Use parameterized database APIs and keep untrusted input out of interpolated raw SQL.
- If Docker uses `pnpm install --ignore-scripts`, explicitly run `prisma generate` afterward.
- After `pnpm fetch --frozen-lockfile`, run a full `pnpm install`: fetch only populates the package store.
- In pnpm Docker builds, copy lockfile and manifests before `pnpm install`, then
  source. Check installation scripts and all targets. The benefit requires caching.
- Commit the lockfile and verify the exact name and source before adding an unfamiliar dependency.
- Pin GitHub Actions to commit SHAs. Do not disable Corepack signature verification:
  update and pin Corepack when bundled keys are obsolete.
- Exclude `.git`, environment files, and keys from the Docker context. Run the final
  stage as a non-root user and verify the effective user in the built image.
- Make `/api/health` independent of the database and startup dependencies. Set `export const dynamic = "force-static"`.
- Set Coolify's Dockerfile Location to the actual repository-relative path.
  For a standalone application, use `/Dockerfile`; do not prefix a removed workspace path.
- Apply security headers and a reviewed Content Security Policy. Do not weaken
  them for a local integration without documenting the necessary origin and risk.
- Do not assume `docker compose up -d --build` replaces an already running container.
  Before browser tests, compare its image ID with the freshly built image ID.
  For an isolated change, use `docker compose build <servizio>` followed by
  `docker compose up -d --no-deps --force-recreate <servizio>`.

## Forbidden

- Passing a `pg.Pool` instance to `new PrismaPg(pool)` unless the current API and
  a reviewed application requirement explicitly demand it.
- Passing `Buffer` directly to `Response` with Node 22's strict types.
- Depending on package lifecycle scripts when installation uses `--ignore-scripts`.
- A health endpoint that queries the database or requires deployment-only services.
- Prefixing the Dockerfile path with a removed workspace directory.
- Interpolating user input into raw SQL.

## Verify

- Run application type-check and production build.
- Build the Docker image from the repository root and confirm Prisma Client generation during the build.
- Start the image with deployment-like variables and request `/api/health` before the database is ready: it must succeed.
- Confirm Prisma connects to the configured host, not `localhost:5432`.
- Confirm the Coolify Dockerfile path exists in the deployed repository.
- Review changed response headers and Content Security Policy against every required external origin.
- During dependency updates, run the repository audit command and investigate relevant findings.
- Confirm the test container runs the freshly built image, then wait for healthy status before Playwright.

## References

Use `platform/06-deploy-new-app.md` for deployment, `14-coolify-server.md` for
production operations, and `strategy/07-security.md` for the threat model.
