---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Breach and Leak Intelligence

## Definition

Breach and leak intelligence is the OSINT practice of identifying public indicators that accounts, domains, credentials, documents, code, or systems may have appeared in breaches, paste sites, public repositories, or exposed datasets. The output is a triaged list of indicators tied to **specific remediation actions**, not a folder of leaked data.

## Why it matters

Leak signals change security priorities. A confirmed credential exposure forces a password reset; a confirmed API token exposure forces token rotation and session revocation; a confirmed document exposure triggers an incident response review. Without breach intelligence, organizations rotate credentials reactively after compromise instead of proactively after exposure.

The dangerous move is treating leaked data casually. Breach indicators must be **scoped, minimal, and handled as sensitive material**. Storing raw dumps creates legal, ethical, and data-handling risk far beyond the original exposure. The goal is to know the indicator exists and act on it — not to collect the contents.

The asymmetry: organizations rarely know about a breach until external indicators surface. Defensive breach OSINT closes that gap by treating public leak feeds as a free early-warning channel.

## How it works

Breach/leak OSINT processes **5 signal types**. Each one triggers a different remediation track.

1. **Account exposure.** Emails or usernames appear in breach indexes (HIBP, public dump listings). Triggers password reset and MFA enforcement for the affected accounts.
2. **Credential exposure.** Passwords, hashes, tokens, API keys, or session cookies are exposed in repositories, pastes, or breach dumps. Triggers immediate rotation and session revocation; **do not debate whether the credential was used**.
3. **Document exposure.** Internal files, logs, backups, or exports become public via misconfigured storage, indexed mistakes, or third-party dumps. Triggers incident response, data classification review, and source removal.
4. **Repository exposure.** Code, configs, secrets, or infrastructure names leak via public commits, fork mistakes, or open mirrors. Triggers secret rotation and a `git history` review (rotation alone does not remove the secret from history).
5. **Third-party exposure.** Vendor or SaaS incidents expose related data (employee accounts on a third-party tool, customer data via a vendor breach). Triggers vendor risk review and downstream credential rotation.

The bug is not "a breach result exists." The OSINT task is **deciding whether the signal is relevant, current, sensitive, and actionable** — and tying it to a remediation owner.

A worked example:

```
Indicator:    HIBP returns 23 employee emails in "Cit0day" 2020 collection.
Sensitivity:  sensitive bucket — contains hashes (per HIBP metadata).
Action 1:     force password reset on the 23 accounts (password reuse risk is the threat).
Action 2:     check whether any of the 23 are admin/privileged → 2 are; rotate session tokens.
Action 3:     enforce MFA for the affected role groups.
Stored:       breach name, date, account count, action ledger. Not raw passwords.
```

The OSINT artifact is the action ledger, not the breach data.

## Techniques / patterns

The discipline is uniform across signal types: **find indicator → triage → minimize → act → record**.

- **Domain-wide email breach indicators** via HIBP `breachedaccount` and `domainsearch` APIs.
- **Public paste/repository mentions of domains or tokens** via secret scanners (gitleaks, trufflehog) against owned repos and via GitHub code search for unowned mentions.
- **Exposed API keys and cloud credentials** via secret-pattern signatures (`AKIA[0-9A-Z]{16}`, GitHub PATs, GCP keys, Slack webhooks).
- **Public document dumps and backups** via [[google-dorking|Google dorking]] and archive monitoring.
- **Vendor breach notices** via vendor security feeds, ENISA/CISA advisories, and public breach disclosures.
- **Repeated password reuse risk signals** via HIBP `Pwned Passwords` (k-anonymity API; never submit full passwords).

## Variants and bypasses

Leak intelligence has **5 handling classes**. Each class implies a different evidence and storage discipline.

### 1. Public breach-index signal

A reputable service reports an account or domain appears in a known breach. Evidence: breach name, date, data classes, source reliability. Storage: indicator + action ledger, never raw passwords. Action: password reset + MFA enforcement scoped to affected accounts.

### 2. Public secret exposure

Tokens, API keys, or credentials appear in public repositories, pastes, or documents. Evidence: source URL, commit hash, timestamp, the secret pattern (not the full secret in long-term storage). Action: **immediate rotation, then forensic review** — rotation first, history cleanup second, "did anyone use it" investigation third.

### 3. Historical leak

Old data may still matter if passwords, emails, or naming patterns persist. Evidence: breach age, persistence indicators (still-current naming conventions, still-active accounts). Action: treat as current exposure if any indicator is still relevant; do not dismiss because the breach is old.

### 4. Third-party leak

A vendor incident affects target data or accounts. Evidence: vendor disclosure, data classes affected, indicator that the target is in scope. Action: vendor risk review, downstream credential rotation for accounts that used the vendor, customer notification if applicable.

### 5. Unverified claim

A forum, paste, or post claims a leak but lacks corroboration. Evidence: claim location, timestamp, any sample provided. Action: **corroborate before escalating**; many "leak" claims are recycled, fake, or aggregations of older data. Do not download samples casually.

## Impact

Ordered roughly by severity:

- **Account takeover risk.** Reused passwords or active credentials in dumps enable direct compromise.
- **Cloud or API compromise.** Exposed tokens may grant direct programmatic access; impact depends on token scope.
- **Sensitive data disclosure.** Documents, exports, and backups leak customer or internal information.
- **Social-engineering enablement.** Leaked context (org charts, internal terminology, vendor relationships) sharpens phishing and pretexting.
- **Incident response trigger.** Even stale leaks require verification, action ledger, and cleanup.

## Detection and defense

Defenses prioritize **rotation-first, investigation-second**, and minimization throughout.

1.
**Treat leaked credentials and tokens as compromised.**
   Rotate secrets and revoke sessions before debating whether they were used. Investigation can run in parallel; rotation cannot wait for investigation to finish.

2.
**Use domain monitoring and secret scanning.**
   Domain-level breach monitoring (HIBP, vendor feeds) and repository secret scanning (CI-integrated, scheduled) feed indicators directly into incident response. Manual sweeps catch nothing in real time.

3.
**Minimize handling of raw leaked data.**
   Store the indicator and the action ledger; avoid storing raw passwords, full dumps, or sensitive documents. Apply retention limits. Encrypt at rest.

4.
**Corroborate unverified claims before escalating.**
   Leak rumors are common. Evidence quality matters; a forum post with no sample is a lead, not an incident.

5.
**Connect leak findings to MFA, password reset, and training.**
   Breach intelligence is only useful when it changes controls. Tie every confirmed indicator to a tracked control change, not a Slack screenshot.

### What does not work as a primary defense

- **Ignoring old breaches.** Old passwords, emails, and naming patterns may still enable attacks today.
- **Downloading full dumps casually.** That creates legal, ethical, and data-handling risk far beyond the original exposure.
- **Relying only on user password changes.** Tokens, API keys, OAuth refresh tokens, and active sessions need separate rotation.
- **Treating all leak claims as true.** Claims need corroboration; recycled and fake leaks are common.
- **Storing the breach contents to "investigate later."** Investigation timelines slip; sensitive data accumulates; the next incident is your own data-handling failure.

## Practical labs

Use your own accounts, owned domains, or authorized defensive monitoring. Never query third-party emails or domains without authorization.

### Build a leak triage table

```
indicator         | source       | timestamp           | sensitivity | confidence | action               | owner
admin@example.com | HIBP Cit0day | 2026-04-29T18:00Z  | sensitive   | verified   | reset+MFA+session    | sec-eng
AKIA... in repo   | gitleaks CI  | 2026-04-29T18:01Z  | sensitive   | verified   | rotate token now     | sre
"example leak"    | forum claim  | 2026-04-29T18:02Z  | sensitive   | uncertain  | corroborate, no DL   | sec-eng
```

Separate the raw indicator (sensitive) from the action ledger (operational).

### Check a domain in HIBP safely

```
# Domain search requires verified ownership and an API key.
# Returns breach-name + email-list-counts only — no plaintext passwords.
curl -s -H "hibp-api-key: $HIBP_API_KEY" -H "user-agent: example-sec-eng" \
  "https://haveibeenpwned.com/api/v3/breaches?domain=example.com"
```

Record breach name, date, data classes, and remediation action — never raw credentials.

### Check a password against `Pwned Passwords` with k-anonymity

```
# Hash locally, send only the first 5 hex chars (k-anonymity).
HASH=$(printf '%s' 'somepassword' | shasum -a 1 | awk '{print toupper($1)}')
PREFIX="${HASH:0:5}"
SUFFIX="${HASH:5}"
curl -s "https://api.pwnedpasswords.com/range/$PREFIX" | grep -i "^$SUFFIX"
```

Never submit a full password to a remote service. The k-anonymity API exists precisely so you don't have to.

### Search owned repos for secrets

```
# ripgrep sweep
rg -nP '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|api_key\s*=\s*["\x27])' .

# gitleaks (history-aware)
gitleaks detect --source . --redact --report-format json --report-path gitleaks.json
```

Rotate every real hit before cleaning history. Rotation first; `git filter-repo` second; investigation third.

### Verify rotation actually invalidated the old credential

```
# After rotating, the old token should now fail.
curl -i -H "Authorization: Bearer $OLD_TOKEN" https://api.example.com/v1/whoami
# Expect 401 Unauthorized.
```

A rotation that does not invalidate the old credential is not a rotation.

## Practical examples

- A company domain appears in HIBP results for a recent breach; 23 employee emails are affected, triggering password reset and MFA enforcement scoped to those accounts.
- A public repo contains an `AKIA` AWS access key in `.env.example`; rotation is immediate, history cleanup follows, and CloudTrail review checks for use.
- An old paste contains internal hostnames matching a current naming convention, suggesting attackers can predict new names.
- A vendor breach includes employee contact data; the vendor risk review identifies all employees with vendor accounts and rotates downstream credentials.
- A leaked document reveals internal project names that match current internal Slack channels, sharpening attacker pretexting.
- An "example leak" forum claim has no sample; the indicator stays in "uncertain" until a sample emerges or 90 days pass.

## Related notes

- [[osint-triage]]
- [[email-and-phone-osint]]
- [[company-osint]]
- [[google-dorking]]
- [[secrets-management|Secrets Management]]
- [[passive-recon|Passive Recon]]

### Suggested future atomic notes

- secret-scanning
- credential-reuse-risk
- paste-site-monitoring
- vendor-breach-triage
- leak-data-handling
- rotation-playbooks

## References

- **Official Tool Docs:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
