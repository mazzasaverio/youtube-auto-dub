# Email with Cloudflare

## Applies when

An application sends or receives email.

## Required

- Use Cloudflare Email Service for sending and Cloudflare Email Routing for receiving.
- Keep the sender in `src/lib/email`, with few dependencies and direct Cloudflare API access.
- Configure `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_EMAIL_API_TOKEN` with
  `Email Sending: Edit`. A controlled fallback to `CLOUDFLARE_API_TOKEN` is
  allowed if already provisioned with the required scope.
- Register every sending domain in Cloudflare under Compute, Email Service.
  Apply generated bounce MX, DKIM, and DMARC records before production sending.
  The `POST /zones/{zone_id}/email/sending/subdomains` API also supports activation;
  verify the result and DNS records. Use a `from` address on the registered domain.
- Use Workers Paid for arbitrary recipients when required. Verify current quotas,
  costs, and abuse-prevention limits for transactional and bulk email.
- Send campaigns only to people with recorded explicit consent. A default opt-out
  value on every account does not prove enrollment or protect against spam complaints.
- A personal contact supplied by the owner is not consent. Tools may allow an
  individually addressed send only after confirmation that the person expects
  that specific update. Keep this classification separate, exclude it from bulk
  selections and automation, and always let withdrawal block sending.
- Informational emails must be readable without images: text-based HTML and
  optional compressed, sized images with alternative text.
- Protect public send actions with Turnstile and rate limits. Lock recipients
  on fixed-destination forms where possible.
- Implement Better Auth password reset through this sender. Add verification
  email only when the product requires verified addresses.
- For incoming email, configure Email Routing rules such as `info@<app>.com`
  and a catch-all to a verified mailbox. Use Cloudflare-required SPF and remove
  conflicting registrar or previous forwarding MX records.
- API acceptance proves queuing, not receipt. Save the primary record first,
  record the outcome, and add retries or alerts if losing the notification
  blocks an obligation. Verify current quotas and costs by recipient type.
- For every new project, email the owner for each actual new registration,
  including waitlist signup where present. Do not notify duplicate submissions
  or failed attempts. Save registration first; configure the recipient at
  runtime and verify a real production send. Exclude unnecessary personal data.

## Forbidden

- AWS SES, Resend, provider-selection branches, or an `EMAIL_PROVIDER` variable.
- Unnecessary shared packages for the sender.
- Committing API tokens.
- Public email endpoints without authentication, bot protection, and rate limits.
- Treating old quotas or prices as current.
- Mixing Email Service sending configuration with Email Routing receiving configuration.

## Verify

- Confirm DNS shows current Cloudflare bounce MX, DKIM, DMARC, and inbound SPF
  records where applicable.
- Send a test from the production domain to a verified destination, then to an
  arbitrary recipient only after confirming plan eligibility.
- Exercise password reset end to end without revealing whether an address exists.
- Trigger rate limits and bot rejection on every public send endpoint.
- Search for and remove active `SES`, `Resend`, and `EMAIL_PROVIDER` paths.

## References

Use `platform/05-cloudflare.md` for dated platform state. Verify current pricing,
quotas, and API behavior in official Cloudflare Email Service documentation before launch.
