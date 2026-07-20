---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Google Dorking

## Definition

Google dorking is the use of search-engine operators and exposure-shaped query patterns to find sensitive, misconfigured, indexed, or security-relevant public content. It is [[search-engine-operators]] aimed specifically at what should not be findable: backups, source maps, error pages, admin portals, indexed credentials, and directory listings.

## Why it matters

Google dorking is **not magic hacking — it is exposure discovery through indexing**. If a search engine can find sensitive files, error pages, login portals, directory listings, or backups, the issue is the public exposure that allowed indexing in the first place. The dork is just a query that reveals a pre-existing failure.

The defensive use is more important than the offensive use. Running exposure-shaped queries against your own organization on a cadence catches accidentally-published artifacts (backups, dumps, build logs, source maps) faster than any external scanner because search engines have already done the discovery work for you.

The Google Hacking Database (GHDB) catalogs hundreds of exposure-shaped query templates. They are useful as **inspiration**, not as a copy/paste list — every organization's exposure shape is different.

## How it works

Google dorking targets **5 exposure classes**. A useful dork query targets exactly one of them and scopes to a domain.

1. **Sensitive files.** Backups (`.bak`, `.sql`, `.zip`, `.tar`), logs, spreadsheets, PDFs, configs (`.env`, `web.config`), source maps (`.map`), and database dumps.
2. **Login and admin portals.** Pages containing login forms or management paths (`inurl:admin`, `inurl:manage`, `inurl:dashboard`, `intitle:"login"`).
3. **Directory listings.** Indexed `Index of /` style pages that expose a browsable file tree because the web server has autoindexing enabled.
4. **Error and debug output.** Stack traces, framework error pages, and verbose debug output that leak internal paths, library versions, and SQL fragments.
5. **Technology and vulnerability clues.** Version strings (`"Apache/2.4.49"`), default install pages, known vulnerable paths (`inurl:wp-content/plugins/...`).

The bug is not Google. The bug is sensitive content being publicly reachable and indexable. The fix is removing reachability, not removing the search result.

A worked example:

```
Question:    Does example.com expose any indexed backup files?
Iteration 1: site:example.com (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
             → 0 hits
Iteration 2: site:*.example.com (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
             → 4 hits, all on dev.example.com
Iteration 3: site:*.example.com filetype:sql -site:docs.example.com
             → 1 hit: dev.example.com/exports/2024_users.sql
Triage:      verified exposure, sensitive bucket, escalate to incident response.
```

The first iteration missed the exposure because it was on a subdomain. Dorking is iterative.

## Techniques / patterns

Dorking technique is built on disciplined operator chains, not memorized GHDB strings.

- `site:` scoped to **owned domains** (or explicitly authorized scope).
- `filetype:` for the document classes that match each exposure category.
- `intitle:"index of"` for directory listings, the highest-yield single dork.
- Exact-phrase search for known error strings (`"Whitelabel Error Page"`, `"SQLSTATE"`, `"Notice: Undefined"`).
- `inurl:` patterns for admin, login, backup, config, api, debug, callback, and version paths.
- GHDB-style query categories as inspiration; never blind-copy GHDB queries against third parties.
- Combination with `cache:` to read the indexed copy when the live page has been changed or removed.

## Variants and bypasses

Dork queries cluster into **6 query families**. Most defensive dorking sweeps run one of each per quarter.

### 1. File exposure queries

Look for backups, logs, configs, spreadsheets, and source maps. Highest-impact category — a single indexed `.sql` or `.env` is often a credential-exposure incident.

### 2. Portal discovery queries

Find login, admin, support, dashboard, and device pages. Often surfaces forgotten vendor admin panels (printers, IoT, cameras) that nobody considered part of the surface.

### 3. Directory listing queries

Find indexed file indexes (`intitle:"index of"`). Almost always accidental; the result is a browsable file tree that anyone can walk.

### 4. Error-message queries

Find framework, database, or stack trace pages. They expose internal paths, ORM fragments, library versions, and sometimes secrets in stack frames.

### 5. Secret-pattern queries

Look for public pages containing token-like or credential-like strings (`"AKIA"`, `"-----BEGIN PRIVATE KEY-----"`, `"api_key="`). High false-positive rate (documentation, test fixtures), so triage carefully.

### 6. Technology fingerprint queries

Find version-specific assets, default pages (`/phpinfo.php`, `/server-status`), or known vulnerable paths. Useful for prioritizing patching, dangerous to use against non-owned scope.

## Impact

Ordered roughly by severity:

- **Secret or credential exposure.** Indexed `.env`, `.sql`, `.bak`, or config files may leak tokens, passwords, or keys directly.
- **Sensitive data disclosure.** Documents, exports, and logs reveal customer data or internal terminology.
- **Admin surface discovery.** Search reveals portals and dashboards that were never meant to be discoverable.
- **Vulnerability targeting.** Version clues and default install pages narrow what an attacker would test next.
- **Attack-surface drift evidence.** Indexed old content proves the exposure existed and lets you scope its lifetime via cache and archive.

## Detection and defense

Defensive dorking is the highest-leverage defense — it uses Google's existing crawl as a free exposure scanner.

1.
**Remove sensitive content from public reachability.**
   The fix is access control and cleanup, not only deindexing. If the file is still reachable, the exposure persists.

2.
**Scan your own domains with exposure-focused queries.**
   Run the 6 query families against `site:*.your-domain` quarterly. Tie findings to a tracked remediation queue with an owner.

3.
**Block indexing for non-sensitive pages that should not appear in search.**
   `noindex` and `robots.txt` reduce discoverability; they are not security boundaries. Treat them as documentation hygiene.

4.
**Review build artifacts and public documents before release.**
   Source maps, build logs, debug pages, and public exports are common indexed exposures introduced by deploy automation. CI checks for these are cheap and high-yield.

5.
**Monitor search result drift.**
   New indexed content can reveal new deployments, new vendor portals, or new mistakes. A scheduled defensive-dork sweep catches exposure within one indexing cycle.

### What does not work as a primary defense

- **Blaming the search engine.** The sensitive content was publicly reachable; the search engine just made it findable.
- **`robots.txt` alone.** It may even reveal paths of interest (the `Disallow:` list is a roadmap of sensitive paths).
- **Deleting the search result while leaving the file public.** Anyone with the URL can still access it; the next crawl re-indexes it.
- **Blindly using GHDB queries against third parties.** Stay authorized and scoped; running exposure-shaped queries against unowned domains is fine, but acting on findings against unowned domains is not.
- **Relying on dork output alone for severity.** A `.sql` filename does not prove the file is a real database dump; corroborate with [[osint-triage|triage]] and a content fetch under owned scope.

## Practical labs

Use owned domains, an authorized engagement scope, or deliberately public training targets.

### Look for public backups

```
site:example.test (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak OR filetype:7z)
site:*.example.test (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
```

Confirm whether each result is intentionally public. A single hit here is an incident.

### Look for directory listings

```
site:example.test intitle:"index of"
site:*.example.test intitle:"index of" -github.com
```

Directory listings are almost always accidental.

### Look for admin portals

```
site:*.example.test (inurl:admin OR inurl:manage OR inurl:dashboard OR inurl:console)
site:*.example.test (intitle:"login" OR intitle:"sign in")
```

Route findings to [[admin-interface-discovery|admin interface discovery]].

### Look for source maps and build artifacts

```
site:*.example.test (filetype:map OR inurl:.map)
site:*.example.test (inurl:webpack OR inurl:dist OR inurl:build)
```

Source maps reveal route names, internal module names, and API hosts. Removing them from production builds is a one-line build-config fix.

### Look for error pages and debug output

```
site:*.example.test ("Whitelabel Error Page" OR "SQLSTATE" OR "Stack Trace")
site:*.example.test ("DEBUG" OR "Traceback (most recent call last)")
```

Error pages leak framework, database, and internal-path context.

### Look for indexed secrets

```
site:*.example.test ("api_key" OR "AKIA" OR "-----BEGIN PRIVATE KEY-----")
```

High false-positive rate; triage every hit before declaring it a real exposure.

## Practical examples

- A query for `filetype:sql` finds an indexed `.sql` backup on a forgotten dev subdomain.
- `intitle:"index of"` reveals an autoindex page exposing uploaded user files.
- A public Whitelabel error page exposes Spring Boot version and internal package paths.
- An old admin portal at `admin.legacy.example.com` appears in indexed results long after the team that built it left.
- A production source map exposes route names and API hostnames that were never in any public spec.
- A vendor printer admin panel appears in `inurl:admin` results because nobody knew it was internet-facing.

## Related notes

- [[search-engine-operators]]
- [[osint-triage]]
- [[breach-and-leak-intelligence]]
- [[exposed-storage|Exposed Storage]]
- [[admin-interface-discovery|Admin Interface Discovery]]
- [[passive-recon|Passive Recon]]

### Suggested future atomic notes

- ghdb-workflow
- indexed-secret-exposure
- directory-listing-exposure
- source-map-exposure
- search-engine-deindexing
- defensive-dork-cadence

## References

- **Official Tool Docs:** Exploit-DB Google Hacking Database — https://www.exploit-db.com/google-hacking-database
- **Official Tool Docs:** Google Search Help: refine searches — https://support.google.com/websearch/answer/2466433/refine-web-searches
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
