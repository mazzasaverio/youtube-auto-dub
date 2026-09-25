# Cost guardrails

## Applies when

Metered models, D1, KV, and R2, Durable Objects, or email from public endpoints.

## Required

- Bound cost in code. Provider billing controls and alerts do not replace per-request limits.
- Before consuming quota or calling models, verify input, entitlements, and
  required data. Reject impossible requests without spending, explaining what
  is missing; also test new, empty accounts.
- Start metered background work only after an actual durable mutation. An
  unchanged `upsert`, a zero-row deletion, UI mounting, or repeating the same
  command does not authorize new generation. Coalesce equivalent concurrent
  work by subject and operation.
- For every model call:
  - set explicit `max_tokens`;
  - enforce a caller-owned maximum iteration count for agents, retries,
    refinement, and tool loops;
  - use bounded retries with exponential backoff;
  - use one provider project key per application for attributable, isolated usage and cost.
- For public routes or Workers with metered D1, KV, or R2:
  - add distributed rate limiting at publication;
  - start browser background work once per intended action;
  - bound every client retry;
  - batch writes and avoid unnecessary storage operations.
- Use Durable Objects only for realtime coordination or distributed locking.
  Bound chains with a hop counter and persist the termination condition of `alarm()`.
- Apply the abuse controls in `07-email-cloudflare.md` to public email.
- For free features, apply the [abuse-prevention contract](../reference/04-consumption-safety.md):
  persistent atomic counters, advance budget reservation, safe rejection, and
  retention aligned with windows. Always distinguish commercial quotas,
  attempts, and estimated spending.
- A global pool protects the bill, not fairness. Pair it with a sufficiently
  stable per-principal or browser limit so one caller cannot exhaust shared
  capacity. Repeated edits to the same record must not consume another slot
  intended to count distinct items.

## Forbidden

- Model calls without `max_tokens`.
- Loops whose only exit condition is the model choosing to stop.
- Retrying deterministic `4xx` or [calls with ambiguous outcomes](../reference/04-consumption-safety.md#leases-and-calls-with-ambiguous-outcomes).
- Unbounded client retries or effects that can repeatedly issue metered calls.
- Durable Objects for ordinary counters, caches, queues, or daily aggregates. Use D1, KV, or Queues.
- Chains between Durable Objects without an exception and hop limit.
- Treating a dashboard budget as an enforced limit.
- Paying for a call when inputs guarantee an empty result, or prompts instructed
  to answer that there was nothing to do.
- Issuing a metered call because a screen mounts or a default differs from the stored value.

## Verify

- In tests, isolate inherited credentials from metered hooks.
- Verify termination at the configured maximum.
- Test every metered function from a new, empty account.
- Force retryable and non-retryable errors; confirm retry count, backoff, and `4xx` behavior.
- Load-test through the distributed rate limiter.
- Confirm rendering and navigation do not repeat metered actions.
- Repeat identical mutations and edits to the same record; confirm no new work
  starts and capacity intended for others does not decrease.
- Review dashboards by application key and investigate unexpected growth in
  requests, tokens, or storage operations.

## References

Use `strategy/06-cost-guardrails.md` for risk classification, weekly operations,
pricing, and current exposure; `research/03-models-openai.md` for model selection;
and `07-email-cloudflare.md` for email implementation.
