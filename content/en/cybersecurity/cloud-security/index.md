---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Security Index

## Purpose

This index is the root entry point for the cloud-security branch of the cybersecurity atlas.

Use it to:
- understand cloud as identity, network, storage, metadata, logging, and cost boundaries
- build safe cloud labs without accidental exposure or runaway spend
- map cloud misconfigurations into attack surface and defensive controls
- separate cloud target-domain security from DevSecOps delivery workflow

Use [[reference-registry-cloud-security|Reference Registry — Cloud Security]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] (especially DNS, TLS, reverse proxies).
> - [[index|Cryptography]] for IAM/keys/secrets reasoning.

---

## Recommended learning order

### Phase 1 — Cloud model and safe labs

1. [[cloud-security-basics]]
2. [[cloud-lab-infrastructure]]

### Phase 2 — Access and administration

1. [[cloud-iam-boundaries]]
2. [[ssh-access-to-cloud-hosts]]
3. [[cloud-secrets-management]]

### Phase 3 — Exposure and reachability

1. [[cloud-network-boundaries]]
2. [[cloud-metadata-security]]
3. [[public-cloud-storage-exposure]]
4. [[cloud-dns-and-certbot]]

### Phase 4 — Visibility and response

1. [[cloud-logging-and-detection]]

---

## Core Cloud Security Cluster

### Branch maturity

This branch is depth-mature as of 2026-04-30.

All 10 atomic notes follow the canonical 11-section template, include practical labs, and now carry worked examples that connect provider configuration to identity, network, data, metadata, logging, cost, and teardown decisions.

### Foundations and labs

- [[cloud-security-basics]]
- [[cloud-lab-infrastructure]]

### Identity and secrets

- [[cloud-iam-boundaries]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-secrets-management]]

### Exposure and network boundaries

- [[cloud-network-boundaries]]
- [[cloud-metadata-security]]
- [[public-cloud-storage-exposure]]
- [[cloud-dns-and-certbot]]

### Detection

- [[cloud-logging-and-detection]]

---

## Cross-links to other branches

### Networking

- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS and HTTPS]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Attack surface mapping

- [[external-attack-surface|External Attack Surface]]
- [[exposed-storage|Exposed Storage]]
- [[admin-interface-discovery|Admin Interface Discovery]]
- [[third-party-exposure|Third-Party Exposure]]

### DevSecOps

- [[secrets-management|Secrets Management]]
- [[container-security|Container Security]]
- [[ci-cd-hardening|CI/CD Hardening]]

---

## Suggested future notes

- IaC Security
- cloud-asset-inventory
- cloud-tagging-strategy
- cloud-kms-boundaries
- cloud-container-security
- cloud-serverless-security
- cloud-iam-policy-analysis
- cloud-account-organization
- cloud-cost-security

### Possible future playbooks

- build-safe-cloud-lab
- audit-public-cloud-storage
- review-cloud-iam-risk
- trace-cloud-metadata-exposure
- cloud-logging-baseline

---

## Branch maintenance notes

- Keep cloud service behavior and provider-control design in this branch.
- Keep generic TCP/IP, DNS, TLS, and metadata mechanics in [[index]].
- Keep CI/CD, dependency, build, and release controls in [[index]].
- Cloud labs should include budget, least privilege, teardown, and exposure checks.
- Use unresolved wikilinks for future atomic notes so Obsidian can track the branch expansion.
- Maintain the cloud decision pattern: every note should show how a provider setting affects blast radius, ownership, evidence, and the next safe action.

## References

- **Foundational:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Foundational:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Foundational:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/
