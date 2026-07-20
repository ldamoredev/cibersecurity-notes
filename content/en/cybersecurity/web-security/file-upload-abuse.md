---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# File Upload Abuse

## Definition

File upload abuse happens when an application accepts, stores, transforms, or serves uploaded files in ways that let attacker-controlled content cross trust boundaries unsafely.

## Why it matters

Uploads are one of the richest attack surfaces in modern applications because they often pass through many layers:
- browser
- app validation
- storage
- processing pipelines
- preview/render features
- downstream consumers

The risk is not only upload a script. It is any path where uploaded content gains more trust, reachability, or execution influence than intended.

## How it works

The mechanism is usually:
1. attacker supplies a file or file-like payload
2. the application validates weakly or only superficially
3. the file is stored, transformed, or served in a dangerous context
4. the uploaded content influences execution, rendering, parsing, or exposure

## Techniques / patterns

Attackers usually test:
- extension validation
- MIME/content-type checks
- parser behavior vs claimed file type
- image/document preview features
- direct public storage exposure
- file naming and path handling
- archive extraction
- SVG/HTML/script-capable formats
- upload followed by rendering inside a trusted origin

## Variants and bypasses

### Extension / MIME mismatch

App trusts extension or declared content type more than actual parser behavior.

### Public storage abuse

Uploaded content becomes reachable from a public path or bucket unexpectedly.

### Active-content upload

SVG, HTML, or other browser-interpreted formats become dangerous when served inline or from a trusted origin.

### Parser exploitation

The risk comes from the component that reads the file later, not the upload itself.

### Archive / nested file abuse

Archives can hide dangerous content or trigger path traversal during extraction.

### Filename and path handling issues

Upload logic may combine with path traversal, overwrite risk, or predictable file access.

## Impact

Typical impact:
- stored XSS
- path traversal or overwrite side effects
- exposure of sensitive files
- parser-triggered downstream compromise
- persistent attacker-controlled content under a trusted origin

## Detection and defense

Ordered by effectiveness:

1.
**Separate public and private storage clearly**
   Uploaded content lives in a different trust zone from app code and config. Keep it on a dedicated bucket or path that cannot be traversed into the app's source tree, and serve it from a different origin (or at least a different cookie scope) so a malicious upload cannot ride the app's session.

2.
**Validate beyond extension alone**
   Extension and `Content-Type` are attacker-controlled. Validate by parsing — confirm an "image" actually decodes as that image format, confirm a "PDF" has the correct magic bytes and structure. Reject on parse failure rather than trying to repair.

3.
**Re-encode user content where the format allows it**
   For images, re-encode through a safe library (drop EXIF, drop embedded scripts, drop polyglot payloads). For documents, render to a safe format if rendering is needed at all. Re-encoding kills most polyglot and parser-tricks attacks at the boundary.

4.
**Serve active content safely**
   Browser-interpreted formats (SVG, HTML, XML) become XSS vectors when served inline from a trusted origin. Serve them with `Content-Disposition: attachment`, from a sandbox origin, or behind a strict CSP. Better: convert SVG to raster on upload if the inline rendering isn't critical.

5.
**Treat processing pipelines as part of the attack surface**
   ImageMagick, Ghostscript, ffmpeg, libreoffice, PDF parsers — every processor is a parser, and parsers have CVEs. Pin versions, monitor advisories, and run processing in a sandbox (separate process, dropped privileges, no network) so a parser RCE doesn't become an app compromise.

6.
**Use safe naming and path handling**
   Never let a user-supplied filename reach the filesystem unchanged. Generate a server-side identifier, store the original name only as metadata, and reject path separators and traversal sequences before any filesystem call. This kills both overwrite and traversal-on-write bugs.

7.
**Review archive handling carefully**
   Zip, tar, and similar archives can carry traversal sequences and absolute paths in their entries (Zip Slip, tar slip). Validate every extracted entry's resolved path against the intended base directory *after* canonicalization, not before.

8.
**Monitor**
   Watch for: uploads with mismatched extension and parsed type, repeated upload-then-fetch patterns from the same actor, unexpected file types in storage, and parser errors clustered around a small set of files.

## Practical examples

- uploaded SVG becomes executable when served inline
- image upload accepts content that later triggers stored XSS in admin review
- archive extraction writes files outside intended upload directory
- uploaded file becomes publicly accessible even though the product assumes it is private

## Related notes

- [[path-traversal]]
- [[xss]]
- [[exposed-storage]]
- [[inspect-file-upload-surface|Inspect File Upload Surface]]

### Suggested future atomic notes

- svg-upload-risk
- upload-processing-pipeline-threat-model
- image-parser-cves
- zip-slip

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Research / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability
