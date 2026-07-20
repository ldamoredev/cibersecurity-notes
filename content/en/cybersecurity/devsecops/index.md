---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# DevSecOps Index

## Purpose

This index is the root entry point for the DevSecOps branch of the cybersecurity atlas.

Use it to:
- connect secure development, CI/CD, dependency risk, secrets handling, and container delivery
- reason about software risk before runtime
- map security controls into the developer workflow instead of bolting them on later
- turn secure-by-design ideas into engineering practices

Use [[reference-registry-devsecops|Reference Registry — DevSecOps]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Web Security]] and [[index|Cryptography]] — build-pipeline threats inherit both.

---

## Recommended learning order

### Phase 1 — Secure development foundations

1. [[nist-ssdf]]
2. [[secure-by-design]]
3. [[asvs-as-dev-process-input]]

### Phase 2 — Supply chain and dependencies

1. [[supply-chain-security]]
2. [[dependency-risk]]
3. [[artifact-integrity]]

### Phase 3 — Pipeline and release controls

1. [[ci-cd-hardening]]
2. [[branch-protection-and-release-controls]]
3. [[secrets-management]]

### Phase 4 — Container and build delivery

1. [[container-security]]
2. [[image-scanning]]
3. [[sbom-and-provenance]]

---

## Core DevSecOps cluster

### Foundations

- [[nist-ssdf]]
- [[secure-by-design]]
- [[asvs-as-dev-process-input]]

### Supply chain

- [[supply-chain-security]]
- [[dependency-risk]]
- [[artifact-integrity]]
- [[sbom-and-provenance]]

### Pipelines and releases

- [[ci-cd-hardening]]
- [[branch-protection-and-release-controls]]
- [[secrets-management]]

### Containers and delivery

- [[container-security]]
- [[image-scanning]]

---

## Cross-links to other branches

### API security

- [[api-inventory-management]]
- [[broken-authentication]]
- [[jwt-attacks]]

### Web security

- [[file-upload-abuse]]
- [[broken-access-control]]
- [[request-smuggling]]

### Attack surface mapping

- [[exposed-storage]]
- [[third-party-exposure]]
- [[deprecated-api-versions]]

### Cloud security

- [[cloud-security-basics|Cloud Security Basics]]
- [[cloud-secrets-management|Cloud Secrets Management]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[cloud-lab-infrastructure|Cloud Lab Infrastructure]]

### Security playbooks

- [[inspect-file-upload-surface]]
- [[reverse-proxy-misconfig-checklist]]

---

## Suggested future notes

- iac-security
- policy-as-code
- build-isolation
- signed-releases
- dependency-confusion
- secret-scanning
- runtime-vs-build-time-controls

### Possible future playbooks

- leak-secrets-from-ci
- inspect-ci-secrets-exposure
- review-container-hardening
- inspect-release-provenance
- test-dependency-risk-hotspots

## Branch maintenance notes

- Keep CI/CD, dependency, build, release, and software-delivery controls in this branch.
- Keep cloud provider identity, network, storage, metadata, logging, and lab-infrastructure controls in [[index|Cloud Security]].

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
