# Free features and metered-use protections

Generalized on 2026-09-06 from Memotaste's free import, release `85ee182`.
Application contract referenced by the [cost rule](../rules/05-cost-guardrails.md).
Thresholds and commercial models remain project decisions, never universal defaults.

## Three separate counters

- **Commercial quota:** allowance included in the plan and communicated to users.
  Refund failed work and cache hits according to the product contract.
- **Operational protection:** attempts and frequency to counter intensive loads.
  An error may already have consumed resources: do not automatically refund the
  abuse-prevention counter, or errors become a bypass.
- **Advance budget:** capacity reserved before metered work. A conventional
  per-request reservation is neither measured cost nor a guaranteed bill cap.
  Demonstrate a complete upper bound before calling it one, including input,
  output, audio, retries, fallbacks, and background work.

When a plan has no commercial quota, represent its absence explicitly (for
example `null` in the contract), separately from operational counters. Do not
use an arbitrarily large number or `Infinity`, which may serialize as `null`
or be rejected by the datastore. Retain measurement, protections, and refunds;
test requests beyond the old cap and client interpretation of the contract.

## Required controls

- Validate inputs before paid work. Reuse authorized caches before consuming
  processing budget; cache hits and invalid requests may still need rate limits
  to protect infrastructure.
- Share counters across equivalent endpoints. Changing source, account,
  workspace, or plan must not accidentally open a new budget. Combine authenticated
  identity and network where appropriate; trust proxy headers only through a
  verified ingress chain. Minimize data and retention.
- Reserve atomically before calling the provider, with persistence across
  processes and restarts. Exceeding a threshold must be distinguishable from
  reaching it. Fully roll back a rejected composite reservation.
- If the essential spending control is unavailable, reject new paid work.
  Failure of telemetry alone is not this case.
- Retain counters and reservations at least until the active window expires:
  cleanup, TTL, and resets must not reopen daily or monthly budgets.
- Size thresholds for actual paths, including the most expensive. Limit images
  by count, dimensions, and decoded pixels; for audio, consider duration and
  tokens, not just bytes; bound retries and parallelism.
- Where capacity is reserved for paying users, free-pool abuse must not exhaust
  it. Document pools, renewals, recovery, and review conditions.

## Reservation reconciliation

Memotaste lesson of 2026-09-06: always retaining the maximum reservation turns
a budget into a request cap disproportionate to inexpensive paths. Reconciliation
requires known cost and complete path coverage, including background work:
do not release the reserve when only the HTTP response has arrived. Isolate
concurrent contexts, retain original keys across resets and plan changes, and
prevent duplicate reconciliation. Unknown costs and failures are not zero;
do not reopen the attempt counter together with the budget. Uncovered multimodal
pricing and invisible retries require an explicit conservative reserve.
A conventional margin does not prove the maximum bill. Test costs above the
reservation and failed reconciliation without losing the reserve or undoing
an already saved result.

## Leases and calls with ambiguous outcomes

Lesson verified in local queue tests on 2026-09-15: an expired lease does not
prove the provider did not execute the metered request. Preserve idempotency
and persistent state; without reconciliation or upstream idempotency, report
the ambiguous outcome without automatically resending. Reject final writes
from workers with expired leases or replaced ownership. Test interruption after
sending, recovery by another worker, and a late result from the previous one:
no automatic double spending and no state overwrite.

## Response to blocking

Distinguish plan exhaustion, operational protection, and service unavailability.
For temporary suspensions, use localized messages and retry times consistent
with the actual reset; no upgrade may bypass a safety control. An unadvertised
threshold does not authorize a false unlimited promise. State personal or fair
use and the possibility of suspensions, without necessarily exposing parameters
that help bypass protections.

Rate limiting bounds volume and speed: it does not prove a person is a bot.
Do not attribute abuse to the user when the global pool has exhausted its budget.
The message must identify the actual reason for suspension.

Before release, simulate normal individual and aggregate usage: initial archive
loading, multiple active people, and composite operations (for example voice
followed by extraction). Calculate how many real operations each budget allows,
not just its nominal monetary value. Very high per-account thresholds do not
prevent an undersized shared pool from blocking everyone. Document expected
capacity, false positives, shared networks, and recovery; do not promise absence
of blocking without representative evidence.

## Verification

Test concurrency on the real datastore, different accounts and endpoints,
workspace changes, the exact threshold, resets, cleanup, rollback, cache,
already-costly errors, database unavailability, and older clients. Demonstrate
that no paid call starts after rejection; verify cost separately using provider data.
