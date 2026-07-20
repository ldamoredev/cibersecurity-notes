---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Detection Engineering

## Definition

Detection engineering is the discipline of turning attacker and system behavior into reliable, explainable, operationally useful telemetry, analytics, alerts, and response evidence.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] — you cannot detect what you cannot reason about.
> - [[index|Offensive Security / Recon]] — read each detection note paired with its offensive counterpart.

## Why it matters

Modern cybersecurity is telemetry warfare. Attackers try to control what defenders can observe, correlate, retain, and interpret. Defenders win less by hoping for perfect prevention and more by engineering visibility across endpoints, networks, identities, cloud control planes, and application boundaries.

This branch is not vendor-centric and does not teach shallow tool operation. It explains the detection surfaces, sensor limits, behavioral patterns, and correlation tradeoffs that make tools useful.

## Branch spine

1. [[network-telemetry-sources-and-visibility]]
2. [[zeek-suricata-and-netflow-analysis]]
3. [[ids-ips-and-behavioral-detection-pipelines]]
4. [[behavioral-detection-vs-signature-detection]]
5. [[false-positives-false-negatives-and-detection-tradeoffs]]
6. [[telemetry-normalization-correlation-and-enrichment]]
7. [[encrypted-traffic-analysis-and-metadata-leakage]]
8. [[scan-anomaly-detection-and-fingerprint-analysis]]
9. [[detection-evasion-myths-and-modern-limitations]]
10. [[edr-network-observability-and-process-correlation]]
11. [[attack-path-correlation-and-kill-chain-observability]]

## Study order

### 1. Visibility before rules

- [[network-telemetry-sources-and-visibility]] - what packets, flows, logs, endpoint sensors, and cloud logs can and cannot see.
- [[zeek-suricata-and-netflow-analysis]] - how three common network telemetry layers complement and contradict each other.

### 2. Detection pipeline design

- [[ids-ips-and-behavioral-detection-pipelines]] - how signature, anomaly, behavioral, enrichment, correlation, and response stages fit together.
- [[behavioral-detection-vs-signature-detection]] - why mature detection blends static indicators, IOAs, behavioral analytics, and sequence logic.
- [[false-positives-false-negatives-and-detection-tradeoffs]] - why detection is precision/recall and operational-capacity engineering, not binary truth.
- [[telemetry-normalization-correlation-and-enrichment]] - why schemas, enrichment, entity resolution, timestamps, and joins often decide detection quality.

### 3. Scan behavior as a detection case study

- [[scan-anomaly-detection-and-fingerprint-analysis]] - why scanning is not a single event but a behavioral pattern across timing, fan-out, TCP/IP shape, TLS fingerprints, and scan-to-exploit transitions.
- [[detection-evasion-myths-and-modern-limitations]] - how to test old evasion claims against modern multi-sensor telemetry.

### 4. Encrypted traffic and metadata

- [[encrypted-traffic-analysis-and-metadata-leakage]] - why encryption hides content but not all behavior, metadata, or endpoint context.

### 5. Endpoint-network and attack-path correlation

- [[edr-network-observability-and-process-correlation]] - why modern defense changed when network events became joinable to processes, users, hashes, and parent chains.
- [[attack-path-correlation-and-kill-chain-observability]] - why modern detection often detects relationships between events rather than isolated events.

### 6. Host-side telemetry (Windows)

- [[windows-event-logs]] - the 30 Event IDs that carry most Windows security telemetry, the audit-policy preconditions that make them appear, and the Event-ID-sequence patterns that drive Windows-targeted attack detection.

## Core claims

- Modern stealth is not "slow packets" or "fragmentation tricks"; it is managing telemetry across many sensors.
- Encrypted traffic still leaks metadata: timing, endpoints, sizes, DNS, SNI where visible, ALPN, JA3/JA4-style fingerprints, process ancestry, cloud logs, and identity context.
- NetFlow/IPFIX, Zeek, Suricata, EDR, cloud flow logs, WAF logs, and SIEM detections are different evidence layers, not interchangeable labels.
- Detection quality depends on sensor placement, capture loss, timestamps, entity resolution, baselines, correlation windows, and triage evidence.
- False positives and false negatives are engineering feedback, not embarrassing exceptions.
- Detection maturity moves from brittle artifact matching toward behavior and sequence modeling, while still using signatures where they are precise.

## Cross-branch anchors

### Offensive security

- [[active-recon|Active Recon]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

### Networking

- [[tcp-ip-basics|TCP/IP Basics]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[nmap-scanning|Nmap Scanning]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[service-enumeration|Service Enumeration]]
- [[tls-https|TLS and HTTPS]]

### Cloud and playbooks

- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[run-scan-pipeline|Run External Recon Scan Pipeline]]

### Internal conceptual hubs

- [[behavioral-detection-vs-signature-detection]]
- [[false-positives-false-negatives-and-detection-tradeoffs]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[encrypted-traffic-analysis-and-metadata-leakage]]
- [[detection-evasion-myths-and-modern-limitations]]
- [[attack-path-correlation-and-kill-chain-observability]]

## Suggested future atomic notes

- correlation-windows-and-entity-resolution
- tls-fingerprinting-for-detection
- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- detection-as-code-and-rule-lifecycle
- alert-triage-and-evidence-quality
- honeyports-and-tarpit-detection
- threat-hunting-with-zeek
- scan-to-exploit-transition-detection
- detection-coverage-vs-attack-coverage
- ecs-and-otel-for-security-telemetry
- precision-and-recall-for-security-detections
- attack-graph-detection
- beaconing-analysis

## References

- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
