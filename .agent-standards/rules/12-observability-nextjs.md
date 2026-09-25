# Next.js exception tracking

## Applies when

Connecting or verifying Next.js capture to self-hosted GlitchTip and its Telegram
webhook. Service setup belongs to [observability](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/07-observability.md).

## Required

- Initialize the browser SDK in `instrumentation-client.ts`; export
  `onRouterTransitionStart = Sentry.captureRouterTransitionStart`.
- Initialize server/edge in `instrumentation.ts` through `register()`, branching
  on `process.env.NEXT_RUNTIME`; export `onRequestError = Sentry.captureRequestError`.
- Keep the public DSN in an imported module, as a literal with an environment
  override. An explicitly empty DSN must disable both initializations without
  changing app behavior. Never apply public defaults to secrets.
- Allow the GlitchTip origin in CSP `connect-src` and send envelopes directly there.
- Suppress expected outcomes already explained by the UI, such as a refused
  port, disconnected board, or unsupported browser.
- Protect alert webhooks with `?secret=`, compared in constant time. Authenticate
  before checking configuration: missing or incorrect credentials must be
  indistinguishable from a missing route.
- Limit the body before parsing, including checks during reading when
  `Content-Length` is absent or unreliable. Encode every remote field for the
  final Telegram context and accept only valid HTTPS URLs in links.
- Bound Telegram requests with timeouts and message counts per window; report
  how many were suppressed during an error storm.
- Disclose browser error reporting, payload contents, and self-hosted EU storage
  in every supported language, following `04-privacy-consent.md`.

## Forbidden

- Using `tunnelRoute` with GlitchTip: the observed Sentry rewrite targeted Sentry
  ingestion hosts and failed for self-hosted DSNs.
- Reusing legacy `sentry.client.config.ts` wiring without verifying the current
  build. The observed Turbopack configuration did not bundle it.
- Enabling session replay in exception tracking: behavior recording belongs to
  its own consent path.
- Uploading source maps by default: it adds CI credentials and a release step.
- Treating container output as request access logs. `next start` does not emit
  every request; retained logs contain only what the process writes.

## Verify

Check the deployed site, not only configuration:

1. Confirm the DSN in served browser code, then trigger a controlled browser
   exception and find the matching event in the intended GlitchTip project.
2. Independently trigger a controlled server exception and find its event.
3. Confirm an incorrect webhook secret returns 404 and an authorized alert
   reaches Telegram. Repeat with an unconfigured secret, hostile markup, and
   an oversized body. Inspect timeouts and suppression.
4. Verify an empty DSN leaves the app working and capture disabled.

Absence from a sample of client chunks is inconclusive: inspect loaded code and
network activity. A present DSN alone does not prove event delivery.

## References

- Architecture, setup, and alerts: [observability](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/07-observability.md).
- Dated failure evidence: [capture notes](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/reference/02-exception-capture.md).
- Build-time limits: [Coolify API](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/reference/01-coolify-api.md).
- Disclosure: `04-privacy-consent.md`.
