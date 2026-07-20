---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry - Detection Engineering

## Purpose

This registry is the source of truth for references in `cybersecurity/detection-engineering/`.

Use it to:
- keep detection-engineering notes grounded in primary telemetry and sensor documentation
- avoid vendor-tutorial drift
- connect offensive behavior to defender-visible evidence
- distinguish packet, flow, protocol, endpoint, cloud, and correlation telemetry

Use it together with:
- [[index|Detection Engineering Index]]
- [[reference-registry-networking|Reference Registry - Networking]]
- [[reference-registry-offensive-security|Reference Registry - Offensive Security]]
- [[reference-registry-cloud-security|Reference Registry - Cloud Security]]

---

## Reference selection policy

### Source priority

1. official standards and project documentation
2. official vendor schema documentation when the note depends on telemetry fields
3. high-signal engineering research from reputable security teams
4. standards-aligned public guidance from CISA/NIST/MITRE/SANS
5. secondary sources only when they add a concrete engineering detail not covered elsewhere

### Per-note target

- minimum 2 references
- target 3-4 references
- default maximum 5 references

### Labeling

Use:
- **Foundational**
- **Official Tool Docs**
- **Telemetry Schema**
- **Research / Deep Dive**
- **Mitigation / Operations**

---

# Detection-engineering topic map

## Common external authority set

Use these as registry-level source families. Add the smallest relevant subset to each atomic note's compact `## References` section; do not create new `wiki/sources/` pages for these ordinary external references.

- **Official Tool Docs:** Zeek documentation - https://docs.zeek.org/
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek capture loss logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata documentation - https://docs.suricata.io/
- **Official Tool Docs:** Suricata EVE JSON output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Foundational:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Foundational:** RFC 5470 IPFIX Architecture - https://www.rfc-editor.org/rfc/rfc5470.html
- **Telemetry Schema:** Microsoft Defender XDR advanced hunting schema tables - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Foundational:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Research / Deep Dive:** Salesforce Engineering TLS fingerprinting with JA3 and JA3S - https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967
- **Research / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Research / Deep Dive:** FoxIO JA4+ overview - https://foxio.io/ja4
- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Mitigation / Operations:** CISA Use Logging on Business Systems - https://www.cisa.gov/use-logging-business-systems
- **Research / Deep Dive:** Elastic higher-order detection rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Research / Deep Dive:** Elastic endpoint-to-environment investigation - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment
- **Official Tool Docs:** Cisco Catalyst 9000 SPAN guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Official Tool Docs:** Cisco SPAN configuration example - https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/10570-41.html
- **Foundational:** Elastic Common Schema reference - https://www.elastic.co/docs/reference/ecs/
- **Foundational:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Foundational:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Foundational:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Foundational:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/
- **Foundational:** MITRE ATT&CK Enterprise Tactics - https://attack.mitre.org/tactics/enterprise/
- **Foundational:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Foundational:** RFC 8446 TLS 1.3 - https://datatracker.ietf.org/doc/html/rfc8446

## behavioral-detection-vs-signature-detection

Preferred references:
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Foundational:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table

Why:
- this note distinguishes artifact matching, IOCs, IOAs, behavior analytics, and sequence logic without pretending one model replaces the others

---

## false-positives-false-negatives-and-detection-tradeoffs

Preferred references:
- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Foundational:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Research / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Foundational:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/

Why:
- this note owns precision/recall, alert fatigue, base-rate problems, thresholds, tuning drift, suppression risk, and SOC operating limits

---

## telemetry-normalization-correlation-and-enrichment

Preferred references:
- **Foundational:** Elastic Common Schema Reference - https://www.elastic.co/docs/reference/ecs/
- **Foundational:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Foundational:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Why:
- this note owns schema mapping, field quality, enrichment, entity resolution, timestamp alignment, and correlation-key reliability

---

## encrypted-traffic-analysis-and-metadata-leakage

Preferred references:
- **Foundational:** RFC 8446 TLS 1.3 - https://datatracker.ietf.org/doc/html/rfc8446
- **Foundational:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Research / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Why:
- this note explains why encryption hides content but leaves metadata, timing, flow shape, TLS handshakes, endpoint context, and correlation evidence

---

## detection-evasion-myths-and-modern-limitations

Preferred references:
- **Official Tool Docs:** Nmap Firewall/IDS Evasion and Spoofing - https://nmap.org/book/man-bypass-firewalls-ids.html
- **Official Tool Docs:** Zeek Capture Loss and Reporter Logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table

Why:
- this note dismantles old evasion folklore by separating partial truths from residual telemetry and modern correlation

---

## attack-path-correlation-and-kill-chain-observability

Preferred references:
- **Foundational:** MITRE ATT&CK Enterprise Tactics - https://attack.mitre.org/tactics/enterprise/
- **Foundational:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Research / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table

Why:
- this note owns sequence correlation, weak-signal accumulation, graph reasoning, timeline reconstruction, and attack-path observability

## scan-anomaly-detection-and-fingerprint-analysis

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide - Timing and Performance - https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README and man page - https://github.com/robertdavidgraham/masscan
- **Foundational:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Research / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Suricata EVE JSON TLS fields - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Why:
- this note ties offensive scan mechanics to defender-visible timing, fan-out, TCP/TLS fingerprints, and protocol metadata

---

## network-telemetry-sources-and-visibility

Preferred references:
- **Foundational:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Cisco SPAN configuration guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection

Why:
- this note owns visibility architecture: where sensors sit, what they can infer, and how loss/aggregation/encryption/cloud abstraction affect evidence

---

## ids-ips-and-behavioral-detection-pipelines

Preferred references:
- **Official Tool Docs:** Suricata User Guide and EVE JSON - https://docs.suricata.io/
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Research / Deep Dive:** Elastic Security Labs higher-order detection rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection

Why:
- this note explains signature, anomaly, behavior, enrichment, correlation, and response pipelines without reducing detection engineering to rule syntax

---

## zeek-suricata-and-netflow-analysis

Preferred references:
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek capture loss logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Foundational:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html

Why:
- this note compares protocol reconstruction, signature telemetry, and flow aggregation as complementary evidence layers

---

## edr-network-observability-and-process-correlation

Preferred references:
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Research / Deep Dive:** Elastic endpoint-to-environment investigation - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment

Why:
- this note owns the endpoint side of network observability: process lineage, socket ownership, user context, and where EDR differs from packet sensors

---

## windows-event-logs

Preferred references:
- **Foundational:** Microsoft Learn — Advanced security audit policy settings — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/advanced-security-audit-policy-settings
- **Foundational:** Microsoft Learn — Events to Monitor — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/appendix-l-events-to-monitor
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers / Windows audit guidance — https://adsecurity.org/?p=3299
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon

Why:
- this note owns the Windows host-side telemetry foundation: the 30-Event-ID subset that actually drives detection, the audit-policy preconditions that make those events appear, and the Event-ID-sequence patterns that AD attack detection depends on

---

## Suggested next registry entries

Add these when the branch expands:
- correlation-windows-and-entity-resolution
- tls-fingerprinting-for-detection
- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- detection-as-code-and-rule-lifecycle
- alert-triage-and-evidence-quality
- honeyports-and-tarpit-detection
- threat-hunting-with-zeek
- ioc-lifecycle-management
- living-off-the-land-detection
- ecs-and-otel-for-security-telemetry
- entity-resolution-for-detection
- beaconing-analysis
- attack-graph-detection
