---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Recon

## Definition

Reconnaissance is the structured process of gathering and validating information about a target to understand its assets, exposures, technologies, ownership boundaries, and likely avenues for deeper testing.

## Why it matters

Good recon raises the quality of every downstream activity. It reduces blind testing, exposes undocumented assets, finds stale systems, and helps decide whether the next step is API testing, access-control testing, SSRF review, admin-surface review, or no test at all.

This is the umbrella note for the branch. [[passive-recon]] collects low-interaction clues, [[active-recon]] validates live behavior, [[enumeration]] expands discovered leads, and [[recon-to-testing-handoff]] converts findings into test strategy.

## How it works

Recon has **5 phases**:

1. **Seed.** Start with domains, company names, products, IP ranges, apps, or scope documents.
2. **Expand.** Collect subdomains, hosts, routes, technologies, people/org clues, and public artifacts.
3. **Validate.** Confirm what is live, owned, in-scope, and relevant.
4. **Classify.** Sort findings by asset type, environment, exposure, owner, and likely test class.
5. **Handoff.** Move high-signal targets into focused testing or attack-surface remediation.

There is no exploit payload here. Recon is an evidence-building workflow: every lead should become either validated context, a test candidate, or discarded noise.

A worked example, from lead to handoff:

```
Seed:
  example.test from scope document

Expand:
  crt.sh reveals api-preview.example.test and old-docs.example.test

Validate:
  api-preview resolves and returns 200; old-docs redirects to a vendor support platform

Classify:
  api-preview = staging-like API surface; old-docs = third-party content host

Handoff:
  api-preview -> scope validation + API inventory/version testing
  old-docs -> third-party exposure review, not exploitation
```

The mature recon output is a decision path, not a bigger hostname list.

## Techniques / patterns

Practitioners combine:

- OSINT, certificate transparency, DNS, ASN, search operators, and archived URLs
- subdomain, host, port, route, and API discovery
- JavaScript, source map, mobile, and schema review
- technology fingerprinting and service validation
- scope and ownership validation
- finding-to-test handoff notes

## Variants and bypasses

Recon has **4 operating modes**.

### 1. Passive recon

Collects public clues without directly touching target infrastructure.

### 2. Active recon

Interacts with target systems to confirm live assets, routes, ports, and behavior.

### 3. Authenticated recon

Uses legitimate low-privilege access to map reachable features, APIs, and state.

### 4. Continuous recon

Repeats discovery over time to catch drift, new deployments, and retired-but-live systems.

## Impact

Ordered roughly by severity:

- **High-quality target selection.** Recon focuses effort on assets likely to produce real findings.
- **Attack surface drift detection.** Forgotten systems and hidden APIs become visible.
- **Better vulnerability testing.** The right concepts are applied to the right targets.
- **Reduced noise.** Scope validation and service validation prevent random probing.
- **Defensive inventory improvement.** Recon mirrors what outsiders can learn quickly.

## Detection and defense

Ordered by effectiveness:

1.
**Run your own recon continuously.**
   Defensive teams should know what outside observers can learn before attackers do.

2.
**Keep scope, inventory, and ownership current.**
   Recon findings are only actionable when they can be tied to an owner and intended exposure.

3.
**Reduce unnecessary public metadata.**
   Source maps, verbose errors, stale docs, public artifacts, and over-descriptive names accelerate recon.

4.
**Monitor for probing and discovery patterns.**
   Scanning, route guessing, admin path probes, and unusual host-header patterns are useful signals.

5.
**Use recon output to drive remediation, not just reports.**
   Findings should flow into retirement, hardening, testing, or branch notes.

### What does not work as a primary defense

- **Pretending public data is not discoverable.** Search, certificates, archives, DNS, and code artifacts make it visible.
- **Blocking one tool.** Recon is a method, not a single scanner.
- **Treating recon findings as low severity by default.** Exposure context determines impact.
- **Keeping stale assets "for later."** Unknown or unowned surface becomes attacker-owned time.

## Practical labs

Use owned scope.

### Create a recon table

```
lead | source | validation status | owner | exposure | next action
```

Every recon lead should end with a decision.

### Seed from certificate transparency

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u
```

This provides passive subdomain candidates.

### Separate live from stale

```
while read host; do curl -m 3 -ks -o /dev/null -w "%{http_code} $host\n" "https://$host"; done < hosts.txt
```

Treat live hosts as candidates for validation, not automatic findings.

### Route leads to next actions

```
lead | evidence | class | confidence | next note/playbook | stop condition
api-preview.example.test | 200 + cert | staging API | medium | scope-validation | owner denies scope
```

The branch skill is converting leads into the right next action.

### Preserve discarded noise

```
lead | source | reason discarded | checked by | date
random.example.test | CT | wildcard DNS noise | analyst | 2026-04-29
```

Keeping negative decisions prevents repeated recon loops.

### Create a recon day boundary

```
Today I will expand:
Today I will validate:
Today I will not test:
Stop when:
```

Time and scope boundaries keep recon from turning into endless collection.

## Practical examples

- A recon pass finds staging hosts and an old API version.
- DNS and ASN clues reveal more public assets than product docs mention.
- JavaScript and mobile artifacts expose hidden routes.
- OSINT reveals acquired brands and vendor-hosted support surfaces.
- Service validation turns a noisy port scan into three actionable targets.

## Related notes

- [[passive-recon]]
- [[active-recon]]
- [[enumeration]]
- [[recon-to-testing-handoff]]
- [[attack-surface-mapping|Attack Surface Mapping]]

### Suggested future atomic notes

- [[osint-triage]]
- bug-bounty-recon-loop
- recon-evidence-model
- continuous-recon
- authenticated-recon

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OSINT Framework — https://osintframework.com/
