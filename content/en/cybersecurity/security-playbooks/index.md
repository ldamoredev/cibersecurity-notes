---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Security Playbooks Index

## Purpose

This index is the root entry point for the security-playbooks branch of the cybersecurity atlas.

Use it to:
- navigate reusable offensive and defensive workflows
- connect concept notes to repeatable procedures
- turn theory into testable checklists
- create a personal operator manual for security work

Use [[reference-registry-playbooks|Reference Registry — Playbooks]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - Whatever concept branch the playbook operationalizes (named in each playbook's Related notes).

---

## First playbooks

### Access control and auth

1. [[exploit-idor]]
2. [[inspect-session-handling]]
3. [[break-jwt-validation]]

### Server-side and proxy-aware

1. [[investigate-ssrf]]
2. [[reverse-proxy-misconfig-checklist]]
3. [[test-client-ip-spoofing]]
4. [[trace-metadata-endpoint-reachability]]

### Input and file handling

1. [[exploit-sqli]]
2. [[test-path-traversal]]
3. [[test-cors-behavior]]
4. [[inspect-file-upload-surface]]

### Recon and scan engineering

1. [[run-scan-pipeline]] — offense
2. [[detect-external-scan-pipeline]] — defender mirror of #12, paired note-by-note
3. [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Identity and Active Directory

1. [[detect-kerberoasting-and-as-rep-roasting]] — defender mirror for the Kerberoasting / AS-REP Roasting offense pair
2. [[detect-dcsync-and-ntdsdit-access]] — defender mirror for the DCSync / ntds.dit extraction endgame attack

---

## Why playbooks matter

Concept notes teach:
- what a vulnerability is
- why it matters
- what mitigation should look like

Playbooks teach:
- how to test for it
- what sequence to follow
- what artifacts to observe
- how to validate impact
- how to move from suspicion to evidence

---

## Cross-links to concept branches

### Networking

- [[reverse-proxies]]
- [[client-ip-trust]]
- [[metadata-endpoints]]
- [[packet-analysis]]
- [[http-messages]]

### Web security

- [[broken-access-control]]
- [[session-management]]
- [[sql-injection]]
- [[ssrf]]
- [[request-smuggling]]
- [[cors-misconfiguration]]
- [[file-upload-abuse]]
- [[path-traversal]]

### API security

- [[broken-object-level-authorization|Broken Object Level Authorization]]
- [[jwt-attacks|JWT Attacks]]
- [[api-rate-limiting|API Rate Limiting]]

### Detection engineering

- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

### Identity and Active Directory

- [[index|Identity and Active Directory]] — full branch (10 atomic notes covering BloodHound, roasting attacks, DCSync, PtH, ticket forgery, Tier 0 administration, and krbtgt recovery)

---

## Playbook template

Each playbook should prefer:
- goal
- assumptions
- prerequisites
- recon steps
- exploit / test steps
- validation clues
- mitigation
- logging / detection
- related notes
- commands / payloads
- gotchas

---

## Suggested future playbooks

- enumerate-admin-interfaces
- map-public-attack-surface
- test-rate-limit-bypass
- inspect-cache-behavior
- test-auth-recovery-flow

## References

- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
