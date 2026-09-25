# Document sanitization

## Applies when

Code inspects, pseudonymizes, redacts, or rewrites PDFs, Office files, images,
or other formatted documents.

## Required

- Test with realistic synthetic artifacts produced by the libraries or applications users use.
- Independently verify both representations: extracted content for underlying
  data removal and rendered images for visual integrity.
- Compare unchanged regions pixel by pixel before and after processing.
  Extraction tests can pass while opaque overlays make a document unreadable.
- Configure redaction effects by content source. Text-layer detections must
  preserve vector backgrounds and intersecting images, while OCR detections
  must still remove sensitive image pixels. Explicitly verify library defaults
  for annotation fills and overlapping graphics.
- Confirm detected source values are absent from extracted output, serialized
  objects, and relevant metadata.
- Keep real validation artifacts and derived images out of repositories.
  Reduce each regression to a synthetic fixture before committing.
- Treat every uninspected region as an explicit limitation or failed coverage case.

## Forbidden

- Accepting visual overlays as secure redaction without proving removal of underlying content.
- Claiming format preservation from semantic extraction checks alone.
- Using real personal, financial, credential, or production data in committed
  fixtures, logs, screenshots, or issue reports.

## Verify

- Reopen output through an independent reading path where practical.
- Search extracted text and raw serialized content for every synthetic value selected for removal.
- Rasterize original and output documents and compare unchanged regions.
- Test malformed inputs, metadata, annotations, embedded content, and
  format-specific hidden regions that may contain sensitive values.
- Run the project's full tests, type-check, lint, and packaging after targeted regression tests.

## References

Use `strategy/07-security.md` for the cross-project threat model. Project-specific
format limitations and accepted rendering tradeoffs belong in project documentation.
