# Privacy, consent, and analytics

This document defines client-side privacy and consent. Apply it before publishing
telemetry code or policy text.

## Applies when

Adding or changing analytics, session replay, client-side error tracking,
advertising, third-party scripts, or behavior described in a privacy policy.

## Required

- Publish behavior and matching privacy policy text together, including summary
  notices and policy date.
- Name every processor, what it collects, why, and its privacy notice. Clarity's
  terms require explicit disclosure: “analytics providers” is insufficient.
- Design for the actual need. Filtering authenticated users is only a tag;
  replay still requires applicable consent. Load a tracker before the decision
  only when its disclosed cookieless collection is acceptable. If the policy
  promises no collection, wait for consent before injecting the script.
- When loading a tool, send its explicit consent decision. Clarity uses Consent
  Mode by default and requires a valid signal in the EEA, UK, and Switzerland
  from 2025-10-31. Use `consentv2`; the boolean API is deprecated.
- For analytics-only Clarity after consent:

  ```js
  window.clarity("consentv2", {
    ad_Storage: "denied",
    analytics_Storage: "granted",
  });
  ```

- Without granted analytics storage, Clarity still records cookieless page views
  and populates the dashboard, but writes no persistent cookies. Navigation
  appears as separate recordings and unique users without an integration error.
- Fully honor refusal or withdrawal. For Clarity, send both storage values as
  `denied`, persist the app's refusal, and reload a path without Clarity.
  Refusal alone does not stop cookieless recording.
- Do not make opt-out reversible through GET or a link another site can activate.
  Reactivation requires an explicit gesture in a same-origin-bound mutating
  request; an unsubscribe credential authorizes only withdrawal, never re-enrollment.
- Mask sensitive fields and portals, not page containers. Renew consent before
  exposing previously masked content; verify recordings.
- Prefer first-party server-side events and self-hosted cookieless analytics for
  counts that must be complete. A consent-based funnel cannot distinguish lower
  usage from lower consent.
- Forms with personal data: declare `method="post"`. Verify without JavaScript
  that no data enters the URL.

## Forbidden

- Inferring consent from use or account creation without policy disclosure and
  an opt-out reachable in the app.
- Publishing code whose behavior contradicts the policy, in either direction.
- Sending names or email addresses to an analytics processor when an opaque account ID suffices.
- Confusing purpose with the test: consent applies to storing or reading any
  device data, so localStorage and sessionStorage count like cookies;
  legitimate interest does not exempt storage.

## Verify

- With Clarity analytics storage granted, navigate two pages and confirm `_clck`
  and `_clsk` exist and both pages appear in the same recording.
- Before consent, confirm policy compliance. Disclosed cookieless collection
  uses no cookies and creates separate recordings; a no-collection promise
  loads no trackers and sends no provider requests.
- Refuse or withdraw, reload, and confirm tracker absence, stopped provider
  requests, both values denied, and removal of existing cookies.
- Read policy and code path sentence by sentence after changing either.

## References

- Use [Microsoft Consent API v2](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-consent-api-v2) and disclosure documentation for current provider behavior.
- Use [`platform/07-observability.md`](https://github.com/mazzasaverio/ops/blob/c7523488ec26286019546983f0963082331611ff/platform/07-observability.md) for
  operational telemetry and persistent business events.
