---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Attack Surface Mapping Index

## Purpose

This index is the root entry point for the attack-surface-mapping branch of the cybersecurity atlas.

Use it to:
- map what is actually exposed, reachable, and discoverable
- connect networking, web-security, API-security, and recon into one operational view
- reason about exposure drift, forgotten assets, and undocumented entry points
- turn architecture assumptions into observable attack surface

Use [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] — you cannot map what you cannot reason about.

---

## Recommended learning order

### Phase 1 — Core mental model

1. [[attack-surface-mapping]]
2. [[external-attack-surface]]
3. [[internal-attack-surface]]

### Phase 2 — Discovery and enumeration

1. [[exposed-service-triage|Exposed Service Triage]]
2. [[endpoint-discovery]]
3. [[admin-interface-discovery]]

### Phase 3 — Asset drift and exposure mistakes

1. [[subdomain-takeover|Subdomain Takeover]]
2. [[exposed-storage]]
3. [[deprecated-api-versions]]
4. [[third-party-exposure]]

## Core attack-surface cluster

### Branch maturity

This branch is depth-mature as of 2026-04-29.

All 10 atomic notes follow the canonical 11-section template, include practical labs, and now carry worked examples that turn raw discovery into exposure decisions.

### Foundations

- [[attack-surface-mapping]]
- [[external-attack-surface]]
- [[internal-attack-surface]]

### Discovery

- [[exposed-service-triage|Exposed Service Triage]]
- [[endpoint-discovery]]
- [[admin-interface-discovery]]

### Exposure drift

- [[subdomain-takeover|Subdomain Takeover]]
- [[exposed-storage]]
- [[deprecated-api-versions]]
- [[third-party-exposure]]

---

## Cross-links to other branches

### Networking

- [[dns-resolution]]
- [[dns-security]]
- [[ports-and-services]]
- [[nmap-scanning]]
- [[reverse-proxies]]
- [[load-balancers]]

### Web security

- [[ssrf]]
- [[broken-access-control]]
- [[path-traversal]]
- [[cors-misconfiguration]]

### API security

- [[api-inventory-management]]
- [[api-security-top-10]]
- [[authorization]]

### Cloud security

- [[cloud-security-basics|Cloud Security Basics]]
- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[public-cloud-storage-exposure|Public Cloud Storage Exposure]]
- [[cloud-metadata-security|Cloud Metadata Security]]

### Offensive / recon

- [[passive-recon]]
- [[active-recon]]
- [[public-asset-discovery]]
- [[enumeration]]

---

## Suggested future notes

- health-check-endpoints
- staging-environments
- shadow-it-exposure
- asset-ownership-model
- schema-exposure
- internet-exposure-reduction
- hidden-parameter-discovery
- cloud-asset-inventory
- direct-origin-exposure
- source-map-exposure
- oauth-redirect-uri-inventory
- public-object-storage-review

### Possible future playbooks

- map-public-attack-surface
- enumerate-admin-interfaces
- [[trace-metadata-endpoint-reachability]]
- inspect-api-version-drift

---

## Branch maintenance notes

- Use [[reference-registry-attack-surface-mapping]] before adding references.
- Keep attack-surface notes focused on exposure, discoverability, ownership, lifecycle drift, and reachability.
- Do not duplicate pure recon workflow notes from [[index]]; link to them.
- zSecurity-derived cloud target-domain topics now live in [[index|Cloud Security]]. Keep this branch focused on observable exposure and link to cloud notes for provider-specific controls.
- Maintain the worked-example pattern: every note should show how a raw clue becomes a scoped exposure decision, not just a discovery artifact.

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Research / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
