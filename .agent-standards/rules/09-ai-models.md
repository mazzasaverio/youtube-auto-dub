# AI model lifecycle

## Applies when

A project uses, changes, or evaluates an AI model.

## Required

- Evaluate each task separately: classification, extraction, rewriting, vision,
  and agents do not share a universal winner.
- For transcripts used as evidence, preserve the original and transformations;
  verify speech, anomalies, quotations, and timestamps. Agreement between models
  does not replace checking the audio.
- Before production, commit a versioned evaluation contract with fixtures,
  evaluators, critical errors, quality, latency, and cost thresholds, baseline,
  candidates, and repetitions.
- Use the same prompt, schema, fixtures, limits, and evaluator for baseline and
  candidate. Run at least three repetitions when output can vary.
- If classification uses excerpts, include repetitive introductions and decisive
  passages appearing late. Evaluate sampling separately from the model.
- Do not infer content properties from title, author, or provenance. Verify
  content, include cases contradicting metadata, and retain `sconosciuto`
  when evidence is missing.
- Record provider, model, reasoning setting, feature, status, latency, retry
  count, and the provider's complete token breakdown. When configured, emit
  OpenTelemetry/OpenInference spans to the central Phoenix service.
- Keep raw tokens authoritative; estimate from dated, versioned prices. Unknown
  prices remain unknown. Show estimate, model, and input near the action;
  distinguish scenario, spending, and limit.
- For cost estimates, state period, sample size, and data coverage. Separate
  per-call cost, full-path cost, and infrastructure; include fallbacks and more
  expensive sources. Do not extrapolate a partial sample as total cost or a maximum.
- Bound calls as required by `05-cost-guardrails.md`. An observability error must
  not fail the product request.
- For executable outputs that change state, require a versioned acceptance
  contract with a closed vocabulary. Verify it independently before applying;
  retries cannot weaken it. Bound attempts and preserve the last valid state.
  Add scenarios when inputs or environment determine the outcome.
- Promote through a reversible canary, fallback, and kill switch. Record the
  decision and evidence in the project's decision log.

## Forbidden

- Choosing one model for every task because its family or tier is newer.
- Promoting based only on a synthetic fixture, average latency, JSON validity, or provider benchmark.
- Maintaining separate price catalogs when the central collector supports the provider and model.
- Sending secrets, personal data, raw prompts, or outputs to default telemetry.
- Comparing configurations with different output limits or undisclosed reasoning settings.

## Verify

- Rerun the committed contract and retain results with dataset, prompt,
  evaluator, price, and model versions.
- Confirm zero critical errors, quality at the task threshold, p50 and p95 at
  the latency gate, and estimated cost at the cost gate.
- Force model, parser, telemetry, and retry errors; confirm fallback, bounded
  retries, and product availability.
- During canary, compare success, retries, latency, tokens, cost, and a
  privacy-safe human-reviewed sample against the baseline.

## References

Use `../platform/08-ai-observability.md` for shared architecture and onboarding,
`../research/03-models-openai.md` for dated OpenAI facts, and
`05-cost-guardrails.md` for call limits.
