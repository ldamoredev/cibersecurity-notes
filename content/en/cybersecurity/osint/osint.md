---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# OSINT

## Definition

Open Source Intelligence (OSINT) is the disciplined collection, evaluation, and reporting of information from public or legally accessible sources. It is the practice of turning observable public artifacts — search results, certificates, archives, leaks, registries, images, public profiles — into evidence-backed answers to a specific question.

## Why it matters

OSINT turns scattered public clues into usable context. In cybersecurity, it maps companies, domains, technologies, exposed documents, public identities, breach clues, and attack surface without sending packets at the target. It is also the only recon mode that is safe to run before authorization is in place: nothing here causes load, errors, or alerts on the target's infrastructure.

The important distinction: OSINT is not "anything found online." It is evidence-backed analysis with **a question, scoped sources, source-quality grading, ethical limits, and a defensible conclusion**. A folder of screenshots is collection; a triaged answer with provenance is intelligence.

The same skill is also the strongest defensive primitive a small team has. Running OSINT against your own organization shows what an attacker can already infer for free — leaked subdomains, stale documents, source maps, exposed buckets, employee directories — before any active testing happens.

## How it works

OSINT follows **5 stages** that should always run in this order. Skipping any stage is the most common cause of bad OSINT.

1. **Question.** Define exactly what you are trying to learn. "Map the company's public attack surface" is workable. "Find dirt on this person" is not — it has no scope, no stop condition, and no ethical limit. A good question fits in one sentence and names a deliverable.
2. **Collection.** Gather public-source clues against the question. Stay strictly passive: no logins, no port scans, no probes that change target state. Record every source URL and timestamp at the moment of collection — public data drifts.
3. **Triage.** Separate signal from noise. Move every lead into verified / likely / uncertain / noise / sensitive (see [[osint-triage]]). The point of triage is to decide what each lead actually proves and what it does not prove yet.
4. **Corroboration.** Confirm important claims with at least one independent source before reporting them. Identity collisions, stale archives, and tool-output overtrust are easy to commit and hard to notice without this step.
5. **Reporting.** Preserve evidence, confidence labels, source URLs, timestamps, scope limits, and concrete next actions. A report that cannot be re-walked by a second analyst is not finished.

There is no exploit payload. The core skill is turning public data into defensible conclusions without overclaiming, and the deliverable is a report another analyst can audit.

A small worked example:

```
Question: Does example.com expose forgotten subdomains?
Stage 1: scoped to apex domain example.com and known sibling brands.
Stage 2: pull crt.sh certificate transparency results, archive.org snapshots, public DNS.
Stage 3: triage 47 names → 12 verified live, 9 likely-stale, 3 collision (sibling brand), 23 noise.
Stage 4: corroborate "stale" by HTTP head against owned probe + archive.org last-seen.
Stage 5: report 9 stale names with provenance, suggest takedown or claim verification.
```

## Techniques / patterns

Each technique pairs with concrete public sources. Use the registry, not random tool lists.

- **Search and archive.** Search engines (Google, Bing, DuckDuckGo, Yandex), advanced operators, [[google-dorking|Google dorking]] via GHDB, archive.org Wayback Machine, archive.today, common-crawl.
- **Documents and metadata.** Public PDFs/DOCs found via `filetype:` operators, EXIF metadata via [[image-and-location-osint|image OSINT]], package registries (npm, PyPI, Maven), GitHub/GitLab code search, source maps and `.well-known` paths.
- **People and accounts.** Company pages, conference bios, LinkedIn job postings, public commit emails, conference speaker lists; covered with ethics framing in [[social-media-osint]] and [[email-and-phone-osint]].
- **Breach and leak signals.** Have I Been Pwned, public dump listings, paste sites, and credential-exposure feeds; covered in [[breach-and-leak-intelligence]].
- **Image, video, location.** Reverse image search, EXIF, georeferencing, sun-angle/shadow analysis, Mapillary; covered in [[image-and-location-osint]].
- **Domain, DNS, certificate, registration.** WHOIS/RDAP, certificate transparency (crt.sh), DNS history (SecurityTrails, ViewDNS), ASN/BGP records, DNSSEC posture; covered in [[company-osint]] and [[passive-recon|passive recon]].

## Variants and bypasses

OSINT has **5 working modes**. Choose the mode that matches the question; do not blend them.

### 1. Cyber OSINT

Focus: assets, technologies, exposure, leaked secrets, attack surface. Inputs are domains, certificates, source maps, package metadata, GitHub leaks, archive snapshots. Output is an evidence-graded asset inventory and an exposure list. The handoff is into [[external-attack-surface|external attack surface]] and [[recon-to-testing-handoff|active recon]].

### 2. Company OSINT

Focus: brand, ownership, subsidiaries, vendors, products, legal entities, public footprint. Inputs are corporate registries, press releases, job postings, vendor announcements, certificate organization fields. Output is an ownership map that drives scope validation — knowing who owns a domain or asset matters before any test goes live (see [[scope-validation|scope validation]]).

### 3. People OSINT

Focus: public identity clues that connect a person to a role, account, or capability. Inputs are conference bios, public commits, public profiles, breach listings tied to email addresses. **Strongest ethical boundaries apply here**: clear purpose, legal basis, minimization, retention limit, and no aggregation that creates harm beyond the original question. Default to the lightest-touch evidence that answers the question.

### 4. Media and location OSINT

Focus: where, when, and who from images, video, audio, or environmental clues. Inputs are EXIF metadata, reverse image search, landmarks, language/license plate cues, sun position, and street imagery. Output is a corroborated time/place/person claim with confidence and limits, never a single-source assertion.

### 5. Threat intelligence OSINT

Focus: tracking adversary infrastructure, indicators, and campaigns through public sources. Inputs are vendor blogs, public IOC feeds, MISP/ATT&CK mappings, certificate reuse, passive DNS, and public sandbox results. Output is contextual indicators tied to the organization's exposure, not a generic IOC dump.

## Impact

Ordered roughly by severity:

- **Attack surface discovery.** OSINT reveals assets, endpoints, and ownership before any active probe — often the single largest source of exposure for under-funded teams.
- **Scope clarity.** Company and ownership clues prevent wrong-target testing during pentests and bug bounty work.
- **Exposure discovery.** Public documents, leaks, source maps, and metadata reveal sensitive context (internal hostnames, customer data, credentials) that the organization did not know was public.
- **Better testing strategy.** Stack and route clues from passive recon make later active testing faster and quieter.
- **Defensive awareness.** Teams learn what outsiders can already infer for free, which sharpens hardening priorities and incident response posture.

## Detection and defense

OSINT against your own organization is itself a defense. Order is by what changes the most exposure for the least effort.

1.
**Run OSINT against your own organization.**
   Defensive OSINT shows what public sources expose before attackers use it. Repeat it on a cadence (quarterly minimum) because public data drifts; new certs, new repos, new vendors, new docs change the picture.

2.
**Grade source reliability and confidence.**
   Public clues are uneven. Mark every claim as verified, likely, uncertain, stale, or noise, and require corroboration before acting on sensitive conclusions. The label is the educational payload — a verified claim and a likely claim drive different decisions.

3.
**Minimize collection of personal data.**
   People-focused OSINT must have a clear purpose, legal basis, minimization rule, and retention limit. Default to the lightest-touch evidence that answers the question; do not aggregate beyond scope.

4.
**Clean up avoidable public exposure.**
   Stale subdomains, stale docs, stripped EXIF on outbound images, removed source maps, redacted metadata in PDFs, secret-scanning on public repos, and credential rotation after breach mentions are concrete, bounded fixes.

5.
**Turn findings into inventory, training, or remediation.**
   OSINT is only useful when it changes decisions. Tie reports to a tracked inventory item, a training change, or a remediation ticket — not to a Slack screenshot.

### What does not work as a primary defense

- **Assuming "public" means "harmless."** Public clues compose; an org chart plus a job post plus a cert SAN is sensitive even if each piece is not.
- **Assuming old data is useless.** Archives and stale records often expose patterns still true today (naming conventions, vendor relationships, internal terminology).
- **Collecting everything.** Unfocused OSINT creates noise, privacy risk, and analyst fatigue. Every collected item should answer the question.
- **Single-source conclusions.** Important claims need at least one independent corroborating source.
- **Robots.txt and noindex.** They reduce indexing pressure, not exposure. The asset is still public.

## Practical labs

Use your own name/domain/company, an authorized engagement, or an intentionally chosen public training target. Stay strictly passive — none of these labs should send any packets at non-owned infrastructure.

### Define the OSINT question first

```
Question:           "Map example.com's public subdomain footprint and flag stale entries."
Allowed sources:    crt.sh, archive.org, public DNS, public WHOIS/RDAP.
Out-of-scope:       any HTTP request to non-owned hosts; any login attempt.
Evidence standard:  >=2 independent sources for any "live" claim.
Stop condition:     all certificate-transparency names triaged into 5 buckets.
```

A scoped question is the difference between an investigation and a link-pile.

### Pull certificate transparency names

```
curl -s 'https://crt.sh/?q=%25.example.com&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sort -u
```

Certificate transparency is the single highest-signal passive source for subdomain discovery — every public TLS cert appears here.

### Capture public DNS without active scanning

```
dig +short ANY example.com
dig +short txt example.com
dig +short mx example.com
```

Inspect from your own resolver. This is passive lookup, not authoritative probing of the target.

### Inspect archive snapshots for stale assets

```
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&output=json&limit=200" \
  | jq -r '.[1:] | .[] | [.[1], .[2]] | @tsv'
```

Archive.org reveals paths and subdomains that no longer respond. Stale assets often outlive the team that built them.

### Source-table every claim before reporting

```
claim                          | source                | timestamp           | confidence | corroboration       | next action
api-staging.example.com exists | crt.sh cert #98231    | 2026-04-29T18:00Z  | likely     | archive.org 2024-08 | http-head probe (owned scope)
old-blog.example.com exists    | archive.org snapshot  | 2026-04-29T18:01Z  | stale      | none                | triage as noise
```

This is the artifact that turns "I found a thing" into a report another analyst can audit.

### Compare passive vs active before each action

```
Search result reading:           passive
Certificate transparency lookup: passive
WHOIS/RDAP query:                passive
HTTP request to target host:     active
Port scan / banner grab:         active
Login attempt or credential use: active and intrusive
```

Keep OSINT strictly passive; the boundary into active recon is the moment you owe the target a notification.

## Practical examples

- Public certificates reveal forgotten staging or admin subdomains long after the original project ends.
- Job postings reveal cloud provider, framework, and tooling choices that narrow active recon.
- Public documents (PDF, DOCX) carry author names, internal project labels, and template artifacts in metadata.
- Search operators (`filetype:`, `inurl:`, `intitle:`) surface exposed internal documents and old admin pages.
- Breach indicators tied to corporate emails suggest credential-rotation and MFA-enforcement priorities.
- Public source maps from production frontends reveal route names, API paths, and internal module names.

## Related notes

- [[osint-triage]]
- [[search-engine-operators]]
- [[google-dorking]]
- [[breach-and-leak-intelligence]]
- [[company-osint]]
- [[passive-recon|Passive Recon]]
- [[external-attack-surface|External Attack Surface]]

### Suggested future atomic notes

- osint-opsec
- source-reliability-grading
- historical-internet-artifacts
- public-document-metadata
- threat-intelligence-osint
- osint-legal-and-ethical-framework

## References

- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
