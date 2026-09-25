# Extended frontend guidance

Load this reference when the UI task involves the cases below.

## Responsive data views

- Sort data columns by value and expose visible sort controls.
- Keep compared chart series on one scale; omit bars for zero values.
- On mobile, place short errors near fixed actions and long details in the
  scrollable body. Test recovery and accessible field descriptions with long text.
- In mobile exploration views, show initial results after search and essential
  filters. Collapse secondary filters and place analysis after the first result
  group unless analysis is the view's primary purpose.
- Put transient feedback where there is no content to read. On phones, place it
  above the tab bar and select placement with a media query.

## Async work and account support

- Show actual phases and refresh status automatically. Explain whether
  navigation is safe and preserve access to the result.
- Do not show percentages when the backend only knows discrete states.
- Show timestamps in account support views.
- When account clients can become stale, expose a build ID with health status,
  record it on load, and check again when the app returns to the foreground.

## Integrations and navigation

- If an external SDK replaces DOM nodes, give it a child node inside a
  framework-owned container. Test retries and unmounting; ignore callbacks from
  disposed instances.
- For deep links, verify schema, parameters, and supported behavior on Android,
  iOS, and desktop separately. A shared URL scheme does not imply shared fields
  or actions. Test the promised gesture on each platform.
- Derive desktop sidebars, mobile headers, and bottom navigation from one route
  model. Use the same breakpoint and test widths immediately above and below it.

## Design system and copy

- Name exceptions such as custom visual experiments, email HTML, or surfaces
  where shadcn adds no value in project documentation.
- `shadcn/lint` supports `no-restyle`, `no-raw-colors`, `no-arbitrary-values`,
  `no-inline-styles`, `no-unknown-classes`, and `require-static-classes`.
  Record the chosen configuration and promote stable configurations to the
  shared registry.
- After AI extraction, ask only for subjective context. Pre-fill suggestions,
  confirm them at the destination, allow non-exclusive choices, and offer a
  “later” option.
- Give text a variant that omits optional data. For example, a price-less button
  must not display `null/month`.
