# Frontend and UI behavior

## Applies when

Building or changing a web UI.

## Required

- In Next.js, use Tailwind for layout and states, and shadcn/ui for interactive
  controls. Keep domain logic outside components. Document justified visual
  exceptions in project docs.
- Check the installed Next.js version and current official docs before changing
  its APIs. Prefer Server Components; isolate browser interactions in Client
  Components. Use `next/image` and responsive dimensions for public images.
- For localized public pages, verify rendered language, canonical URL,
  `hreflang`, sitemap, and robots. Do not claim incomplete translations as
  complete; use `noindex` and a canonical URL for the available language, or
  redirect to it.
- When changing locale through client navigation, verify `html lang` and `dir`.
  Use full navigation or remount the root layout if those attributes stay stale.
- Start new Tailwind projects from the shared shadcn registry. Own copied
  components in `src/components/ui/`; do not depend on a shared runtime package.
  Use `cn` for class merging. Adopt `shadcn/lint` at the next substantial
  Tailwind v4 UI change, beginning with rules the project already satisfies.
- Adopt UI changes incrementally, not as a retroactive rewrite. Put transient
  feedback where it does not obscure content; avoid redundant labels and
  invented progress. Keep mobile forms recoverable and accessible.
- Keep skeletons aligned with the screen they promise. Refresh stale clients
  automatically, expose real phases for async work, and never render missing
  values such as `null` to users.
- Give DOM-mutating SDKs a dedicated child node. Ignore callbacks from disposed
  instances and distinguish a timeout from a confirmed service rejection.
- Verify external-app deep links separately on each promised platform.
- Preserve user responses; check conflicts, order, and focus.

## Forbidden

- Hand-write controls with shadcn equivalents without a documented reason.
- Add a second component library or shared internal UI runtime to an app.
- Ask users to reload when the app can update itself.
- Keep a sticky element that covers a scrolling list; remove its cause.

## Verify

- Test the requested gesture, object, context, and viewport with real data.
- Check changed screens on phones and remove redundant text.
- Confirm newly built forms and dialogs import from `@/components/ui/*`, or
  document the exception.
- Keep `pnpm build` green after adding shadcn components.
- Check mobile exploration at 360 px, including horizontal overflow and the
  order of results, secondary filters, and analysis.
- Validate selectable asset sets against every valid application and API value.
- Keep an installed app open after deployment and confirm it reaches the new build.
- Check computed styles when migrating global CSS to Tailwind; remove or scope
  conflicting selectors instead of accumulating `!important`.
- Derive desktop and mobile navigation from one route model and test both sides
  of the breakpoint.

## Reference

- [Extended UI guidance](../reference/05-frontend-guidance.md).
- [shadcn/ui](https://ui.shadcn.com), the shared registry in `20-registry.md`,
  the [`cn` package](https://github.com/shadcn-ui/cn), and
  [shadcn/lint](https://github.com/shadcn-ui/lint).
