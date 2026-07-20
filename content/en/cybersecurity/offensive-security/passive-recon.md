---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Passive Recon

## Definition

Passive recon is information gathering that does not directly interact with the target's systems in a way that would normally generate target-side traffic.

## Why it matters

Passive recon is broad, low-friction, and often enough to reveal large parts of external attack surface before touching the target. The zSecurity OSINT topics belong here for now: search operators, breach/leak clues, social profiles, public documents, email/phone clues, image/location work, and company mapping.

Keep the boundary clear: passive recon collects clues; [[active-recon]] proves live target behavior.

## How it works

Passive recon uses **6 public clue sources**:

1. **Names and domains.** Domains, brands, subsidiaries, acquisitions, and naming patterns.
2. **Public infrastructure records.** DNS, certificate transparency, WHOIS/RDAP, ASNs, and cloud hostnames.
3. **Search and archives.** Search operators, cached pages, GHDB-style queries, Wayback, old docs.
4. **Code and artifacts.** Public repos, source maps, package metadata, mobile apps, and docs.
5. **People and organization.** Job posts, social profiles, emails, phone numbers, roles, and vendors.
6. **Breach/leak context.** Public leak references, exposed credentials indicators, and historical incidents.

The bug is not public information existing. The security lesson is that public clues combine into an accurate model of systems and trust boundaries.

A worked example, passive clue chain:

```
Search clue:
  site:example.test filetype:pdf "staging"

Document clue:
  PDF mentions "preview-api.example.test"

Certificate clue:
  CT confirms preview-api.example.test had a cert issued last month

Archive clue:
  Wayback has /api/v1/examples for that host

Passive conclusion:
  likely staging/API asset; do not test yet, send to scope + live validation
```

Passive recon is strongest when independent public sources corroborate each other.

## Techniques / patterns

Practitioners collect:

- certificate transparency subdomains
- search operator results and archived URLs
- public repository strings and package names
- public docs, PDFs, metadata, and support pages
- job postings that reveal stack and vendors
- social media and company profile clues
- email patterns and contact surfaces

## Variants and bypasses

Passive recon has **5 useful lenses**.

### 1. Asset lens

Find names, domains, hosts, cloud providers, and external services.

### 2. Route lens

Find URLs, API paths, parameters, docs, and historical endpoints.

### 3. Technology lens

Infer frameworks, languages, vendors, and deployment patterns.

### 4. Organization lens

Map brands, subsidiaries, teams, roles, and vendors.

### 5. Human/context lens

Find support channels, emails, public roles, and social-engineering context. Keep this ethical and scope-aware.

## Impact

Ordered roughly by severity:

- **Hidden asset discovery.** Passive sources reveal forgotten domains and subdomains.
- **Route and endpoint discovery.** Archives and code artifacts expose backend paths.
- **Credential and secret exposure clues.** Public repos or leaks can reveal security issues.
- **Technology targeting.** Stack clues guide deeper testing.
- **Scope clarification.** Company mapping reduces wrong-target testing.

## Detection and defense

Ordered by effectiveness:

1.
**Audit public information as part of attack-surface management.**
   If outsiders can find it, defenders should know it exists.

2.
**Reduce stale public artifacts.**
   Old docs, source maps, leaked examples, and archived references often outlive the system.

3.
**Review public repositories and package metadata.**
   Names, endpoints, tokens, and internal domains often leak through development artifacts.

4.
**Limit unnecessary technology disclosure.**
   Hiding stack names is not a primary defense, but avoid gratuitous banners, error pages, and comments.

5.
**Use findings to improve inventory and training.**
   Passive recon should feed ownership cleanup, secrets hygiene, and awareness.

### What does not work as a primary defense

- **Ignoring cached or historical data.** Old information remains useful for attackers.
- **Treating OSINT as separate from security engineering.** Public clues map to real systems.
- **Relying on robots.txt or noindex as secrecy.** These are indexing hints, not access controls.
- **Only cleaning the main website.** Repos, docs, vendors, and archives leak too.

## Practical labs

Use owned targets or public self-audit.

### Use search operators

```
site:example.test filetype:pdf
site:example.test inurl:api
site:example.test intitle:index.of
```

Record only relevant, in-scope findings.

### Pull certificate names

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u
```

Feed candidates into scope and live validation.

### Search local/public repos

```
rg -n "api\\.|secret|token|password|internal|staging|callback|webhook" .
```

For owned repos, classify real secrets versus harmless examples.

### Build a passive corroboration table

```
claim | source 1 | source 2 | source 3 | confidence | active validation needed
```

Do not promote one public clue into a target without corroboration or scope review.

### Pull archived URLs safely

```
curl -s "https://web.archive.org/cdx?url=example.test/*&output=text&fl=original&collapse=urlkey" \
  | rg "/api/|admin|staging|debug" \
  | sort -u
```

Archived routes are leads; live probing belongs in active recon.

## Practical examples

- Certificate logs reveal subdomains.
- Archived URLs show routes no longer linked from the UI.
- Public docs expose internal naming patterns.
- Job postings reveal framework and cloud choices.
- Public repositories mention API hostnames and webhook paths.

## Related notes

- [[recon]]
- [[active-recon]]
- [[public-asset-discovery]]
- [[company-mapping]]
- [[subdomain-enumeration]]

### Suggested future atomic notes

- [[search-engine-operators]]
- [[google-dorking]]
- [[breach-and-leak-intelligence]]
- [[social-media-osint]]
- [[email-and-phone-osint]]
- [[image-and-location-osint]]

## References

- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
