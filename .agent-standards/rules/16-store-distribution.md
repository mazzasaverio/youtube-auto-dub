# App store distribution

## Applies when

Publishing or updating an app in a mobile store, including Trusted Web Activities
or other wrappers around an existing web application.

## Required

- Publish a **public account-deletion page**: HTTPS, no login barrier, and a
  submitted URL pointing to the deletion page itself. Name the listed app, explain the steps, and disclose deleted data, retained
  data and retention duration. Add an email path for people who uninstalled
  or lost access. Both account- and data-deletion fields require a URL;
  the same page serves both.
- Name **every surface** in the privacy policy, including the store build. A
  “website and PWA” policy linked from the store describes a different product.
- Prevent the store build from **selling**. Hide prices, plan selection, and every
  control starting Checkout; retain web-purchased entitlements, gift codes,
  and management of existing subscriptions. See [`../strategy/05-payments-stripe.md`](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/strategy/05-payments-stripe.md).
- Give apps where users see content published by others an **in-app reporting
  control**, usable without an account and directed to a person who reads it.
- Provide a **reviewer account** when any section requires login: created through
  app registration, non-expiring paid plan, credentials in app secrets, and
  login verified before submission.
- Change **declarations before behavior**. An existing listing is suspended for
  outdated declarations much more often than a new listing is rejected.
- Answer questionnaires from the **text shown on screen**. A question about
  illegal drugs is not about alcohol; one about promotion is not about references.

- Separate web deployment, installed wrapper version, listing edits, review,
  publication, and device update. API track status alone does not prove delivery.
- Test the same shared link through PWA and Play installations, cold and warm,
  including repeats and login redirects. Preserve payloads through Custom Tabs
  fallback; appearing in the share sheet proves only intent registration.
- Review generated-project diffs before building. Version bumps must preserve
  custom launcher code, dependencies and Gradle settings. Inspect the signed artifact.
- Check all supported listing languages, including images and first-run screens.
- Confirm public developer identity/contact disclosures before launch; change
  verified account settings, never invent identity details to hide required fields.

## Forbidden

- Promising approval when preliminary checks finish, or claiming the public
  download count updates within an unverified deadline. Inspect Console metrics
  and their latest date; registrations and PWA installs are different measures.
- Declaring a wrapper fixed from mocked browser tests alone, or reinstalling a
  primary user's app without accounting for local data and signing differences.
- A deletion URL that redirects to login.
- Declaring a capability the reviewer cannot find in the build.
- Underdeclaring to obtain a lower content rating or avoid review.
- Answering a conditional question the form did not ask. CSV import rejects the
  whole file for such an answer; a blank field says no to a question never asked.

## Verify

- Open the deletion URL in a private window: it must render without a session.
- Read the privacy policy and listing surface by surface.
- Log in with reviewer credentials from a clean profile.
- Install from the test channel and confirm there are no purchasing surfaces.
- After payment, data-collection, or sharing changes, reread every declaration before release.

## References

- [`../platform/11-play-console.md`](https://github.com/mazzasaverio/ops/blob/f80e22ac7c1aaf4fa3ed2baf90280e3cbf99d5cb/platform/11-play-console.md) for Play
  mechanics, API separation, and TWA builds.
- [`04-privacy-consent.md`](04-privacy-consent.md) for policy text consistent with declarations.
