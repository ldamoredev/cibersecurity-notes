---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Linux Privilege Escalation Index

## Purpose

This index is the root entry point for the Linux privilege escalation branch of the cybersecurity atlas.

Use it to:
- understand local Linux privilege boundaries after an authorized foothold
- practice OSCP-style host enumeration in owned labs
- separate misconfiguration proof from reckless exploit execution
- connect host findings back to offensive-security, cloud-security, and defensive hardening

Use [[reference-registry-linux-privilege-escalation|Reference Registry — Linux Privilege Escalation]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] — even local privesc routinely depends on network-reachable services.

---

## Recommended learning order

### Phase 1 — Mental model and enumeration

1. [[linux-privilege-escalation]]
2. [[linux-enumeration]]

### Phase 2 — Common misconfiguration classes

1. [[sudo-misconfigurations]]
2. [[suid-sgid-misconfigurations]]
3. [[linux-capabilities]]
4. [[path-hijacking]]

### Phase 3 — Scheduled and platform-level risk

1. [[cron-and-timer-abuse]]
2. [[kernel-exploit-triage]]

### Phase 4 — Automation as assistant

1. [[linpeas-workflow]]

---

## Core Linux Privilege Escalation Cluster

### Branch maturity

This branch is depth-mature as of 2026-04-30.

All 9 atomic notes follow the canonical 11-section template, include practical labs, and carry worked examples that connect local host clues to minimal proof, remediation, and safe lab boundaries.

### Foundations

- [[linux-privilege-escalation]]
- [[linux-enumeration]]

### Misconfiguration paths

- [[sudo-misconfigurations]]
- [[suid-sgid-misconfigurations]]
- [[linux-capabilities]]
- [[path-hijacking]]

### Scheduled and kernel paths

- [[cron-and-timer-abuse]]
- [[kernel-exploit-triage]]

### Tool workflow

- [[linpeas-workflow]]

---

## Cross-links to other branches

### Offensive / recon

- [[recon-to-testing-handoff|Recon to Testing Handoff]]
- [[service-validation|Service Validation]]
- [[scope-validation|Scope Validation]]

### Cloud security

- [[ssh-access-to-cloud-hosts|SSH Access to Cloud Hosts]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[cloud-metadata-security|Cloud Metadata Security]]
- [[cloud-secrets-management|Cloud Secrets Management]]

### Networking and playbooks

- [[ports-and-services|Ports and Services]]
- [[index|Security Playbooks]]

---

## Suggested future notes

- linux-file-permissions
- linux-groups-and-users
- writable-service-files
- nfs-privilege-escalation
- docker-group-privilege-escalation
- linux-credential-hunting
- linux-log-review-for-privesc
- linux-post-exploitation-cleanup

### Possible future playbooks

- linux-privesc-enumeration-checklist
- validate-sudo-privesc-in-lab
- audit-suid-binaries
- review-linux-capabilities
- triage-kernel-exploit-risk

---

## Branch maintenance notes

- Keep this branch focused on local Linux privilege boundaries after a foothold exists.
- Keep initial access, recon, web exploitation, and cloud identity paths in their existing branches.
- Every lab should name authorization, target host, expected effect, proof boundary, and rollback or remediation evidence.
- Prefer minimal proof over full compromise when the learning goal is defensive validation.
- Use unresolved wikilinks for future atomic notes so Obsidian can track branch expansion.
- Maintain the enumeration-first pattern: identify context, rank paths, manually verify one path, record remediation.

## References

- **Technique Reference:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
