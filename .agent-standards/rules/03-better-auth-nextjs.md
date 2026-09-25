# Better Auth with Next.js

## Applies when

Changing authentication, sessions, OAuth, account linking, or authorization in Next.js.

## Required

- Use only Better Auth, pin its exact version, and verify current official APIs.
- Keep identity and sessions in Better Auth, entitlements in the application database, and payments in Stripe.
- Define `betterAuth({...})` in `src/lib/auth.ts` without module-level request APIs
  such as `next/headers`; with Prisma, use `prismaAdapter(prisma, { provider: "postgresql" })`.
- Expose `src/app/api/auth/[...all]/route.ts` through `toNextJsHandler(auth)` with
  `runtime = "nodejs"`; export only used client methods from `src/lib/auth-client.ts`.
- Enable `better-auth/plugins/bearer`: cookies for web, bearer for other clients.
- In Next.js 16, use `src/proxy.ts` only for optimistic cookie routing. Every
  protected operation must call `auth.api.getSession` and enforce current roles,
  entitlements, quotas, and ownership in the database.
- Generate auth tables after setup and plugin changes. Define application fields
  with `user.additionalFields` and `input: false` if not user-writable.
- Invalidate `session_data`, including numbered chunks and the `__Secure-` prefix,
  after direct writes to `additionalFields`.
- Rate-limit public auth endpoints. Retain CSRF and origin checks, secure cookies
  in production, and explicit `trustedOrigins`.
- Revoke old sessions during password recovery. If signup creates a session before
  email verification, prevent third-party preregistration from surviving owner recovery.
- Keep the secret and credentials in the environment. Rotating the secret logs
  everyone out. For OAuth, use exact callbacks and minimal scopes.
- If landing and app use different hosts, pass absolute return URLs on the app
  host to OAuth; test them in the browser along with the final session.
- For provisioned users, `emailVerified=false` may block OAuth. Relax the local
  requirement only with closed signup; require provider-verified email. Avoid `trustedProviders`.
- If OAuth returns `signup_disabled`, check the email. If different, link after
  local login or migrate the email while preserving the ID, after backup and a
  rehearsal on a copy. Keep signup closed and recovery active until real OAuth
  login succeeds; revoke old sessions.
- Use Cloudflare Email Service. Keep auth and public routes out of redirects.
- Allow through the proxy every route authenticated without a session cookie:
  webhook signatures, bearer tokens, and cron secrets. The edge gate runs first,
  and a `307` may appear successful to the sender.

## Forbidden

- Other auth providers or auth-provider billing.
- Authorization based only on UI, client claims, proxy checks, or cached sessions.
- Cookie-only auth when non-web clients are needed, or JWTs without a documented external verifier.
- Unreviewed account linking or committed secrets.

## Verify

- **After an upgrade, perform a real login before deployment.** Build and schema
  are insufficient. Verify on a database copy and prepare rollback.
- Regenerate the schema after plugin changes; inspect migrations.
- Test cookie and bearer sessions on a protected operation, plus anonymous,
  unauthorized, and wrong-owner requests on protected handlers.
- Create two test sessions, complete a password reset from a third session, and
  confirm both earlier sessions are rejected.
- Confirm public routes return `200`.
- Test cookie-free routes with correct and incorrect credentials. A `307` comes
  from the edge gate, not the handler.
- Test every configured OAuth origin and native callback.

## References

Official Better Auth documentation, `07-email-cloudflare.md` for auth email,
and `rules/01-api-first.md` for the API contract.
