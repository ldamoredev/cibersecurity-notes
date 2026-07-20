---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Offensive Security / Recon Index

## Purpose

This index is the root entry point for the offensive-security / recon branch of the cybersecurity atlas.

Use it to:
- structure attacker-style discovery and enumeration thinking
- separate passive recon, active recon, enumeration, and validation workflows
- connect reconnaissance to attack surface mapping, web security, and API security
- build a repeatable operator mindset instead of ad hoc scanning

Use [[reference-registry-offensive-security|Reference Registry — Offensive Security]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] — the substrate every recon technique probes.
> - [[index|Attack Surface Mapping]] — recon turns surface into evidence.
> - **Pair every note with its [[index|Detection Engineering]] counterpart.**

---

## Recommended learning order

### Phase 1 — Recon foundations

1. [[recon]]
2. [[passive-recon]]
3. [[active-recon]]

### Phase 2 — Asset and technology discovery

1. [[public-asset-discovery]]
2. [[company-mapping]]
3. [[tech-stack-fingerprinting]]

### Phase 3 — Operational enumeration

1. [[enumeration]]
2. [[subdomain-enumeration]]
3. [[host-and-port-discovery]]

### Phase 4 — Validation and transition to testing

1. [[scope-validation]]
2. [[service-validation]]
3. [[recon-to-testing-handoff]]
4. [[cloaking-and-security-evasion]]

---

## Core offensive / recon cluster

### Branch maturity

This branch is depth-mature as of 2026-04-29.

All 12 atomic notes follow the canonical 11-section template, include practical labs, and now carry worked examples that turn discovered leads into validated evidence, scope decisions, and testing handoffs.

### Foundations

- [[recon]]
- [[passive-recon]]
- [[active-recon]]

### Asset discovery

- [[public-asset-discovery]]
- [[company-mapping]]
- [[tech-stack-fingerprinting]]

### Enumeration

- [[enumeration]]
- [[subdomain-enumeration]]
- [[host-and-port-discovery]]

### Validation and handoff

- [[scope-validation]]
- [[service-validation]]
- [[recon-to-testing-handoff]]
- [[cloaking-and-security-evasion]]

### Scan engineering (depth)

- [[nmap-timing-and-evasion]]
- [[packet-fragmentation-and-decoy-scans]]
- [[masscan-internet-scale-scanning]]
- [[rustscan-and-nse-pipeline]]
- [[idle-scan-and-ipid-side-channels]]
- [[nse-vuln-category-audit]]

### Active Directory and identity attacks

> Promoted to its own branch on 2026-05-10. See [[index|Identity and Active Directory]] for Kerberoasting, AS-REP Roasting, BloodHound, DCSync, and related notes.

### Defender-side scan telemetry

- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

---

## Cross-links to other branches

### Attack surface mapping

- [[attack-surface-mapping]]
- [[external-attack-surface]]
- [[endpoint-discovery]]
- [[admin-interface-discovery]]
- [[subdomain-takeover|Subdomain Takeover]]

### OSINT

- [[osint|OSINT]]
- [[osint-triage|OSINT Triage]]
- [[company-osint|Company OSINT]]
- [[osint-reporting|OSINT Reporting]]

### Networking

- [[dns-resolution]]
- [[dns-security]]
- [[ports-and-services]]
- [[nmap-scanning]]
- [[service-enumeration|Service Enumeration]]

### Detection engineering

- [[index|Detection Engineering]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]]

### Wireless security

- [[wireless-security|Wireless Security]]
- [[wifi-monitor-mode|Wi-Fi Monitor Mode]]
- [[evil-twin-access-points|Evil Twin Access Points]]
- [[bettercap-workflows|Bettercap Workflows]]

### Cloud security

- [[cloud-security-basics|Cloud Security Basics]]
- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[public-cloud-storage-exposure|Public Cloud Storage Exposure]]

### Web/API security

- [[api-inventory-management]]
- [[broken-access-control]]
- [[ssrf]]
- [[cors-misconfiguration]]
- [[bot-detection-signals|Bot Detection Signals]]
- [[evilginx-and-reverse-proxy-phishing|Evilginx and Reverse Proxy Phishing]]

### Security playbooks

- [[test-client-ip-spoofing]]

---

## Suggested future notes

- [[osint-triage]]
- [[search-engine-operators]]
- [[google-dorking]]
- [[breach-and-leak-intelligence]]
- [[social-media-osint]]
- [[email-and-phone-osint]]
- [[image-and-location-osint]]
- historical-internet-artifacts
- js-recon
- route-guessing
- wordlist-strategy
- bug-bounty-recon-loop

### Possible future playbooks

- build-recon-pipeline
- map-public-attack-surface
- enumerate-admin-interfaces
- validate-staging-hosts
- enumerate-public-apis
- trace-subdomain-ownership

---

## Branch maintenance notes

- Use [[reference-registry-offensive-security]] before adding references.
- Keep this branch focused on discovery, validation, scope, and handoff.
- Keep exploitation details in Web Security, API Security, or Security Playbooks.
- zSecurity-derived OSINT topics now live in [[index|OSINT]]. Keep this branch focused on recon workflow and handoff.
- zSecurity-derived wireless topics now live in [[index|Wireless Security]]. Keep this branch focused on general recon workflow and handoff.
- zSecurity-derived cloud topics now live in [[index|Cloud Security]]. Keep this branch focused on general recon workflow and handoff.
- Maintain the handoff pattern: every recon note should show how a raw clue becomes either validated context, a scoped test candidate, a no-action decision, or an owner/remediation path.

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon series — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OSINT Framework — https://osintframework.com/
