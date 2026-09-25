# Print deliverables

## Applies when

A repository generates PDFs, booklets, or sheets that will be printed and paid
for by page or color mode.

## Required

- Treat physical page cost as a layout constraint: check page count, nearly
  empty opening pages, and shifted content after every structural change.
  Count alone does not guarantee quality.
- Keep a heading and its first relevant content on the same page; do not
  combine page breaks on headings and first cards.
- Validate generated block structure: accidentally nested elements can produce
  duplicate borders and alter pagination.
- Inspect the final PDF using thumbnails of every page and samples at actual
  print size. Distinguish digital proof from physical proof.
- For fixed-page layouts, also check DOM content and graphical elements beyond
  margins: clipped text or lines may not appear in extracted PDF text.
  A correct page count does not prove the absence of clipping.
- For printed QR codes, compare the payload decoded from the rasterized PDF
  at proof resolution with the intended destination. Preserve the quiet zone
  and essential information readable without a phone. Digital decoding does
  not replace scanning a physical proof.
- When color materially affects the quote, offer a low-ink or grayscale variant
  preserving content and readability. Clarify that pricing depends on the
  print shop, not the PDF's name.

## Forbidden

- Declaring a PDF print-ready merely because the build succeeds.
- Reducing text size solely to reach a page count without checking readability
  at the final format.

## Verify

- With variable fonts, check the PDF, not just the browser: some renderers
  serialize them as Type 3. If that complicates inspection or delivery, use
  static instances with license and provenance retained. Type 3 does not
  automatically mean missing fonts; verify embedding and selectability.
- Check page count, format, embedded fonts, and rendering of every page.
- Inspect body text, photographs, forms, and cover samples; make a physical
  proof before ordering the full print run when specifications are known.

## References

- Publication and verification workflow: [15-git-merge-workflow.md](15-git-merge-workflow.md).
