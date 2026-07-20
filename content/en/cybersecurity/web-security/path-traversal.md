---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Path Traversal

## Definition

Path traversal happens when attacker-controlled input influences a filesystem path in a way that allows access outside the intended directory boundary.

## Why it matters

This vulnerability is a clean example of unsafe trust between user input and sensitive server-side resources. It often looks simple, but its real depth appears in:
- path normalization
- OS-specific separators
- URL encoding
- archive extraction
- indirect file access patterns
- differences between validation path and real filesystem resolution

## How it works

The mechanism is:

1. the application takes attacker-controlled input
2. that input is used to build or resolve a filesystem path
3. the application fails to constrain the final resolved path to an intended base directory

Typical vulnerable pattern:

```
const fullPath = baseDir + "/" + userInput
```

If `userInput` is:

```
../../etc/passwd
```

the resolved path escapes the intended directory.

The core problem is not merely the string `../`.
The core problem is failure to control the final path resolution.

## Techniques / patterns

Attackers look at:
- download endpoints
- file preview endpoints
- import/export handlers
- template/include mechanisms
- document/image retrieval
- archive extraction
- upload-followed-by-read flows
- logs, backups, or support bundle retrieval paths

Typical tests:
- relative traversal sequences
- encoded traversal
- alternate separators
- mixed normalization patterns
- absolute path attempts
- platform-specific path behavior

## Variants and bypasses

### Classic relative traversal

Using `../` or equivalent to move out of the intended directory.

### Encoding-based traversal

Bypasses validation that checks raw input but not the decoded/normalized form.

### Separator differences

Unix and Windows path semantics differ, and applications sometimes normalize one but not the other.

### Absolute path access

Sometimes the app accepts direct absolute paths or can be tricked into them.

### Archive extraction / zip-slip style paths

A special and very practical traversal family where extracted archive entries escape the target directory.

### Indirect path construction

The app may appear to use safe identifiers, but later transforms them into paths unsafely.

### Allowlist misunderstandings

Teams often validate “contains only safe chars” but still fail to enforce directory boundaries on the final canonical path.

## Impact

Typical impact:
- read sensitive files
- expose config, keys, tokens, or environment files
- access internal templates or source
- overwrite files in some write-capable cases
- pivot into broader compromise if sensitive host data is reachable

Impact is highest when traversal reaches:
- secrets
- configs
- source code
- credentials
- deployment artifacts
- internal-only files later used by trusted processes

## Detection and defense

Ordered by effectiveness:

1.
**Do not build raw filesystem paths from attacker input**
   Use indirect references or safe lookup layers.

2.
**Constrain the final canonical path**
   Validate after normalization/canonicalization that the final resolved path stays inside the intended base directory.

3.
**Use explicit allowlists**
   Only allow known-safe filenames or identifiers where possible.

4.
**Separate read/write/extraction zones carefully**
   Different trust levels should not share the same file handling assumptions.

5.
**Review archive extraction logic**
   Zip/tar extraction paths are a common path-boundary failure.

6.
**Use least privilege on file-accessing processes**
   Even if traversal exists, lower process/file privileges can reduce impact.

7.
**Monitoring**
   Watch for:
   - traversal-like path strings
   - unexpected file access failures outside app dirs
   - abnormal retrieval of sensitive host files
   - suspicious extraction paths

## Practical examples

- file download endpoint vulnerable to `../../` path escape
- archive extraction that writes outside intended upload directory
- template preview or report generator reading arbitrary files
- support/log download mechanism that trusts a user-supplied filename too much

## Related notes

- [[file-upload-abuse]]
- [[http-messages]]
- [[exposed-storage]]
- [[test-path-traversal|Test Path Traversal]]

### Suggested future atomic notes

- zip-slip
- path-canonicalization-pitfalls

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Research / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability
