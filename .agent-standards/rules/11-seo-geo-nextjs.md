# SEO and GEO rules for Next.js

## Applies when

Public crawlable Next.js routes, metadata, redirects, locales, sitemaps, robots
rules, feeds, `llms.txt`, social images, middleware, and caching. Load
`research/01-seo-geo-aeo.md` only for dated external facts; refresh conditions
are in `01-knowledge-refresh.md`.

## Required

- Give each content unit one canonical host, locale, path, and slug across links,
  sitemaps, redirects, hreflang, and metadata.
- Redirect before streaming output. In affected segments, call `redirect()`,
  `permanentRedirect()`, or `notFound()` from `generateMetadata`; page-body checks are fallback only.
- Configure `htmlLimitedBots` so every allowed search or AI crawler receives
  blocking metadata in `<head>`. An override replaces Next.js's default expression;
  retain relevant defaults too.
- Allow current search crawlers on public canonical content and verify at the CDN.
  For OpenAI, check `OAI-SearchBot` against published IP ranges. Keep training
  controls such as GPTBot and Google-Extended separate.
- Block crawling of non-indexable query-string variants with `Disallow: /*?*`,
  except deliberately indexable query URLs. Canonical and `noindex` control
  indexing, not fetching.
- Emit reciprocal `alternates.languages` only for real variants, using BCP 47
  keys, canonical URLs, and `x-default` where appropriate. Redefine `languages`
  when page metadata overrides `alternates`: Next.js replaces the object.
- Do not turn database failures or timeouts into empty collections: public routes
  may produce false 404s or noindex. Distinguish and test absence and unavailability;
  metadata and HTML must use the same data snapshot. Preserve real totals and
  self-canonicals on intentionally browsable paginated lists.
- Include only indexable canonicals in sitemaps. Use actual content updates for
  `lastModified`, or omit it; include consistent language alternates.
- Allow public SEO surfaces through auth middleware and exclude their static
  extensions from matchers: `/robots.txt`, `/sitemap.xml`, `/llms.txt`, optional
  `/llms-full.txt`, feeds, IndexNow verification, and generated social images.
- Check `public/` before adding or diagnosing an App Router route: a static file may shadow it.
- Serve useful HTML without client JavaScript. Server-render metadata and
  structured data; require answer-first copy, attributable facts, stable entity
  IDs, and quality gates for generated content.
- For public tool pages, index explanations, limitations, and a cost-bounded
  trial; keep personal outputs `noindex`, preserve input through login, and
  exclude it from attribution.
- Measure tools through attempts, enumerated outcomes, and continuation, without
  input. Recoverable outcomes must preserve intent and offer the complete action.
- In structured data, distinguish author, publisher, and source work. Do not use
  publisher for an unknown author or a work's link as a person's `sameAs`.
  Import dates do not prove original publication: omit unsupported dates and
  types rather than inventing rich-result requirements.
- Use `noindex,follow` for intentional navigation, filters, weak pages, and near
  duplicates. Index entity hubs only with substantial standalone value:
  intended exclusions are not defects.
- Explicitly configure bot access and CDN caching. Keep SEO redirects in the app,
  permanently redirect alternative hosts, and use short XML and text caches.
- Use truthful `lastModified` and IndexNow where supported. `llms.txt` is a
  convenience, not a ranking asset. Align titles and descriptions with intent,
  entity, language, and brand or non-brand purpose.
- Declare alternative brand spellings once in `WebSite.alternateName`. For young
  domains, these disambiguate the entity.
- Give sharing-oriented pages distinctive Open Graph and Twitter images. Set
  `twitter.card` to `summary_large_image`: otherwise a generic parent-layout
  image may override the page preview.
- Render FAQs as page prose and build any `FAQPage` from the same array. Markup
  does not guarantee rich results; answer engines primarily extract prose.
- Label answer-engine sessions by engine name from both `utm_source` and referrer
  host, matching host boundaries at dots to exclude lookalikes. Treat results
  as a lower bound: mobile-app clicks lack referrers and arrive as Direct.

## Forbidden

- Redirecting after the first streaming flush: it may become HTTP 200 with meta refresh.
- Internal URLs differing from canonical host, protocol, locale, path, or slug.
- Combining `noindex` with a canonical to another page.
- Sitemap URLs that are noindex, redirected, duplicate, private, or errors;
  stamping every regeneration with the current time.
- Inferring crawler HTML from hydrated metadata, auth `307` on public surfaces,
  or trusting production freshness before bypassing or clearing CDN caches.
- Creating shards below the sitemap limit without confirming the framework emits the required index.
- Creating pages merely to increase count. Scaled content without unique value risks spam.
- Promising clicks from indexing, FAQ markup, `llms.txt`, or video embeds. Each
  has narrower value described in research references.
- Publishing generated social cards before rendering and visually checking
  representative optional fields, fonts, and overflow on the built server.
- Treating query-dimension Search Console click totals as site totals:
  anonymized queries are omitted, undercounting; day and page breakdowns are accurate.

## Verify

Test deployed canonical, duplicate, query variant, and public surface. Fetch with
cache-busting: compliant crawlers are intentionally denied query URLs.

```bash
UA='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
CB=$(date +%s)
curl -fsS -A "$UA" "https://example.com/page?cb=$CB" \
  | sed 's|</head>.*||' \
  | grep -oiE '<title>[^<]*</title>|rel="canonical"[^>]*|hreflang[^>]*'
curl -sS -A "$UA" -o /dev/null \
  -w 'code=%{http_code} loc=%{redirect_url}\n' \
  "https://example.com/old-slug?cb=$CB"
curl -sS -A "$UA" -o /dev/null \
  -w 'code=%{http_code} loc=%{redirect_url}\n' \
  "https://example.com/llms.txt?cb=$CB"
curl -fsS "https://example.com/robots.txt" \
  | grep -F 'Disallow: /*?*'
```

Verify head, case-insensitive hreflang, permanent redirects, public 200s, sitemap
canonicals/dates, robots/CDN, and deployed fingerprint. After technical changes,
run targeted tests and build.

## References

- Current external SEO/GEO research: `research/01-seo-geo-aeo.md`.
- Search measurement/reporting: `strategy/04-search-console.md`.
- Crawlers/CDN caching: `platform/05-cloudflare.md`.
- Engine indexes, crawler taxonomy, referrals: `research/02-answer-engines.md`.
