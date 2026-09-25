# Stripe subscriptions

## Applies when

Stripe plans, Checkout, subscriptions, quotas, or entitlements.

## Required

- Use the server SDK, hosted Checkout, and Customer Portal.
- Without `STRIPE_SECRET_KEY`, retain the free plan and hide upgrades.
- Store plans, quotas, and entitlements in the database and enforce them server-side;
  Better Auth proves identity only.
- Map logical plan and period to Stripe price IDs server-side. The client does
  not decide price ID, ownership, entitlement, or success.
- Set Checkout `client_reference_id` to the application user ID and reuse the stored Stripe customer.
- Set `automatic_tax` and address updates where needed.
- EU consumer prices: `tax_behavior=inclusive`. An explicit value is immutable:
  errors require a replacement Price and migration.
- Use `txcd_10103000` for consumer SaaS; verify other categories.
- Make webhooks the sole writers of plan state. Do not use local expiration timers.
- Subscribe only to necessary events: normally `checkout.session.completed`,
  `customer.subscription.updated`, and `customer.subscription.deleted`.
- Verify signatures on the raw body and process idempotently. Return `400` for
  invalid signatures and `500` for valid events whose processing fails.
- Make entitlement transitions monotonic relative to Stripe events. Webhooks may
  arrive out of order: retain the last applied event's identity and time, or
  reread authoritative provider state; prevent older events overwriting newer ones.
- Link Checkout with `client_reference_id`; resolve later events through the stored customer ID.
- Treat `active`, `trialing`, and `past_due` as entitled unless a different grace
  policy is documented. Other states are not entitled.
- Read entitlements from the database, never cached auth sessions.
- Index monthly quotas by `(userId, YYYY-MM)`. Use `upsert`, then `updateMany`
  guarded by `< limit` to prevent concurrent overruns.
- Enforce finite usage. Refund commercial quotas for failed work and cache hits;
  distinguish abuse-prevention counters under the [consumption contract](../reference/04-consumption-safety.md).
- Align plan changes across server, subquotas, alternative paths, UI, offers,
  FAQs, guides, and multilingual metadata, including older clients. Removing
  a commercial quota does not remove operational protections.
- Verify availability and server enforcement before advertising benefits.
- Keep public billing routes outside auth redirects. The signature authenticates the webhook.
- Mark runtime-configured pricing pages `force-dynamic`. Every advertised period
  must map to a selectable Checkout option.
- Separate live and test keys; expose one runtime value per key.
- Publish renewal, cancellation, and refund terms. Link terms and privacy in
  the portal and support in the Stripe profile; reread live state.

## Forbidden

- Entitlement decisions based on auth providers, clients, cached sessions, email comparisons, or UI alone.
- Unmapped client-supplied price IDs or unlimited paid usage.
- Session-protected webhooks, signature checks on parsed bodies, or success after processing failure.
- Static runtime pricing or advertised periods without matching options.
- Mixed modes, duplicate environment keys, or test identifiers in live mode.

## Verify

- Test forged signatures, duplicate and out-of-order events, and processing retries.
- Test at least update then deletion, deletion then older update, and delayed Checkout completion.
- Confirm account identity across Checkout and later events.
- Test concurrent quota requests, maximum usage, and refunds.
- Start without Stripe configuration; confirm free operation without billing UI.
- Test every period, Portal cancellation, and advertised tax-inclusive amounts.
- Verify runtime key uniqueness and intended mode.
- Complete tests; live-card verification is separately authorized in `strategy/05-payments-stripe.md`.

## References

Commercial choices and release: `strategy/05-payments-stripe.md`.
