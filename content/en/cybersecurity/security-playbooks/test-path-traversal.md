---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Test Path Traversal

## Goal

Determine whether user input can escape the intended filesystem path boundary and access unexpected files or directories.

## Assumptions

- the app reads or writes files based on user-controlled identifiers
- path normalization may be incomplete
- platform-specific separators or encodings may matter

## Prerequisites

- file-related endpoints or upload/extraction features
- ability to replay requests and compare responses

## Recon steps

1. Identify download, preview, import, extraction, and template-related features.
2. Map where path-like input appears in routes, params, or JSON.
3. Note OS/platform behavior where relevant.

## Exploit / test steps

1. Try simple traversal sequences.
2. Test encoded or alternate separator variants where appropriate.
3. Compare behavior for read and write operations.
4. Probe archive extraction or upload workflows for directory escape.
5. Observe whether normalization happens before or after validation.

## Validation clues

- access to unexpected files
- different errors when escaping intended directories
- writes or extractions landing outside controlled paths

## Mitigation

- avoid raw user-controlled filesystem paths
- use indirect references or strict allowlists
- canonicalize safely and verify final paths
- isolate processing and storage accounts/dirs

## Logging / detection

- repeated traversal-like strings
- failed file access outside expected trees
- extraction or write attempts outside upload areas

## Related notes

- [[path-traversal]]
- [[file-upload-abuse]]
- [[http-messages]]
- [[exposed-storage]]

## References

- **Testing / Lab:** PortSwigger path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
