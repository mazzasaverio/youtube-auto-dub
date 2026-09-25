# Owner notifications

## Applies when

An application has registrations, payments, subscription changes, contact or
feedback forms, or an event the owner must be able to find later.

## Required

- Send owner notifications by email through Cloudflare Email Service. Telegram
  may supplement email, never replace it.
- Notify account creation, successful payment, significant subscription changes
  including cancellation, and contact or feedback submissions.
- Resolve the recipient from `OWNER_NOTIFICATION_EMAIL`, then `ADMIN_EMAIL`.
  Never put a personal address in code.
- Complete the primary transaction first. Send the notification without awaiting
  it, catch errors, and log them without blocking registration, payment,
  feedback, or a signed webhook.
- Degrade safely when email is not configured.
- Escape every user-controlled value interpolated into HTML.
- Apply final-format escaping to chat messages using HTML or Markdown too.
  Validate URLs and attributes separately rather than treating them as safe
  because the JSON body is correctly serialized.
- In service workers, accept only same-origin click destinations.
- Use searchable subjects containing application and event type.
- Keep one notification module with event-named functions instead of scattering sends throughout code.
- For webhook changes, compare stored state and event identity so retries do not send duplicates.

## Forbidden

- Letting a notification error cancel or retry the event it describes.
- Telegram-only coverage for required owner events.
- A notification helper without a verified call site.
- Searching for function names from another application and treating absent results as proof of missing notifications.
- Provider-specific sends outside `07-email-cloudflare.md`.

## In-app notifications and ephemeral invitations

- Use one durable source for unread notification counts. Do not add persisted
  records and synthesized domain rows for the same event.
- Scope every notification mutation to the authenticated identity even when
  the notification identifier is unique.
- Separate durable notification from ephemeral action state. For an expiring
  invitation, the notification must expire or resolve with the invitation.
- Make acceptance, rejection, and cancellation idempotent. For concurrent actions
  creating a resource, use a short lock or equivalent transactional guarantee.
- Restore still-valid invitations after reconnecting and remove expired references from ephemeral indexes.
- Mount one notification client per session. Change responsive placement with
  CSS without duplicating sockets, polling, and local state.
- Retain polling as low-frequency recovery and pause it when the page is hidden.
  Realtime transport does not replace reconciliation with the durable source.

## Verify

- Inspect call sites, not just helper definitions.
- Search recipient variables and actual `sendEmail` calls, then map each call
  to registration, payment, cancellation, and contact.
- Force an email error and confirm the primary operation succeeds while the error is logged.
- Replay a webhook and confirm it does not notify twice.
- Test unconfigured email and HTML escaping with hostile input.

## References

Use `07-email-cloudflare.md` for sender setup and `strategy/05-payments-stripe.md`
for webhook and entitlement behavior.
