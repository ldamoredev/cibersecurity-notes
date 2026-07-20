---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Detect External Recon Scan Pipeline

## Goal

Detect an external operator running a two-phase Masscan → Nmap-NSE recon pipeline (the offense playbook [[run-scan-pipeline]]) against your perimeter, with high enough fidelity to identify the source, scope, and intent within minutes — before the operator's depth-phase findings convert into follow-up exploitation.

## Assumptions

- you have **at least one** of: NetFlow/IPFIX collection at the perimeter, Suricata/Zeek/Snort on the perimeter span port, or perimeter firewall logs with per-source connection counts
- your perimeter rules block at least known-bad source IPs and you can hot-block a new source IP within minutes
- the goal is **detect, identify, contain** — not exploit-block; preventing the scan entirely is impossible against a determined operator with control of their own scan box

## Prerequisites

- NetFlow/IPFIX collector (nfdump, FastNetMon, Plixer, or SIEM-side processing of Cisco/Juniper/pfSense exports)
- IDS engine — Suricata or Zeek at the perimeter, with an updated community rule set
- A baseline of "normal" perimeter traffic: per-source connection rates, common destination ports, partner integrations that legitimately fan out
- An incident-response runbook with at least three contact paths (SOC analyst, network engineer, security on-call)
- Optional: honeyports / tarpits on never-used ports — asymmetric high-confidence detection; see the "Honeyports / tarpits" bullet under **Mitigation / remediation** below

## Detection steps

> *This playbook is the defender-side mirror of [[run-scan-pipeline]]. Each phase below pairs to the same-numbered phase in the offense playbook. Read both together.*

### Phase 0 — Baseline (do once, refresh quarterly)

1. Capture a 7-day baseline of perimeter traffic. Record per-source flow rates, top 100 source IPs, distinct destination ports per source, common protocols.
2. Identify legitimate fan-out sources: monitoring vendors, internet measurement projects (Censys, Shodan, BinaryEdge, internetdb), authorized partners, your own external scanning if you do continuous attack-surface monitoring.
3. Allowlist legitimate fan-out sources in your alerting rules. Without this step, the baseline is poisoned by routine internet noise and every alert is a false positive.

### Phase 1 — Detect breadth-phase (Masscan / Zmap signature)

Operator signature: **one source IP issuing thousands of SYNs against many distinct destinations within seconds**, typically with a non-default TCP fingerprint (Masscan's user-space stack ships specific window size + MSS + missing SACK).

1. **NetFlow rule (highest sensitivity).** Alert when a single source produces flows to ≥ 100 distinct destination IPs within 60 s. Tune the threshold to your baseline; some environments need 1000+.
   `text
   # nfdump example
   nfdump -R /var/log/flow -t 2026-05-11/14:00:00-2026-05-11/14:01:00 \
     -A srcip -O bytes -o "fmt:%sa %fl %byt" |
     awk '$2 > 100 {print}'`

2. **Suricata signature for SYN fan-out.**
   `text
   alert tcp $EXTERNAL_NET any -> $HOME_NET any \
     (msg:"Mass SYN fan-out (Masscan-like)"; flow:to_server; flags:S;
      threshold:type both, track by_src, count 100, seconds 60;
      classtype:network-scan; sid:9000001; rev:1;)`

3. **TCP fingerprint correlation.** If multiple alerts fire from "different" source IPs in the same time window, capture full packets and compare TCP fingerprints (window size, MSS, options order). Identical fingerprints across "different" sources confirm decoy-based attribution evasion ([[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]) — cluster as one actor.

### Phase 2 — Detect depth-phase (Nmap + NSE signature)

Operator signature: **one source IP probing many distinct ports on one or a few hosts within ~60s**, with NSE-specific probe payloads that match Suricata/Snort community rules.

1. **Per-host port fan-in alert.** Alert when a single source touches ≥ 100 distinct ports on one destination within 60 s.
2. **NSE probe signatures.** Subscribe to the Emerging Threats or Suricata community rule set; both ship signatures for the most common NSE payloads (`http-shellshock`, `smb-vuln-ms17-010`, `ssl-poodle`, etc.). Update weekly.
3. **`-sV` banner-grab signature.** Nmap's version detection sends a specific sequence of payloads against likely service ports. Suricata rule `2010493` (or equivalent in your ruleset) catches the canonical `-sV` probe sequence.
4. **EDR network-to-process correlation.** If you have EDR coverage on internet-facing hosts, alert when the same source IP that triggered Phase 1 alerts also issues per-port deep probes — and when the destination host's EDR shows the connection arriving but no application-level activity following. The combination is a high-confidence Nmap signature.

### Phase 3 — Detect evasion attempts

Operator signature: **fragmented probes, decoy traffic, source-port spoofing (`--source-port 53`), `--badsum` packets, or idle-scan attribution evasion**.

1. **Fragment reassembly alerts.** Suricata/Zeek with `stream.reassembly` enabled will reassemble fragmented probes before signature matching; the fact that a probe arrived fragmented is itself an alert-worthy anomaly for external traffic.
2. **`--badsum` detection.** Packets with invalid TCP/IP checksums sent to perimeter hosts. Real OSes drop these silently; any host on path that replies has self-identified as inline inspection — but the attacker's `--badsum` probe is also visible at the perimeter as malformed packets, which is anomalous.
3. **Source-port spoofing.** Alert on inbound traffic with source port 53 (DNS) or 88 (Kerberos) to non-DNS/non-Kerberos destination ports. Legacy stateless ACLs sometimes trust these source ports; modern attackers exploit that.
4. **Idle-scan zombie-side detection.** If your own hosts are being used as zombies for an idle scan ([[idle-scan-and-ipid-side-channels|Idle Scan and IPID Side Channels]]), the host shows: unsolicited SYN-ACKs from the operator + unsolicited responses from the target + IPID counter advancing without matching outbound application traffic. Monitor your own infrastructure for this pattern; you can detect being used as a zombie even when the actual scan target's logs show nothing.

## Investigation / response steps

Once a Phase 1 or Phase 2 alert fires:

1. **Capture full packets from the source for 5 minutes.**
   `text
   sudo tcpdump -i $PERIMETER_IFACE -w /tmp/scan-$(date +%s).pcap \
       -s 0 'host SOURCE_IP' &
   sleep 300; sudo pkill -P $! tcpdump`

2. **Identify the operator footprint.** Run `p0f` or Suricata's fingerprint logging against the capture to extract TCP fingerprint, TLS JA3/JA4, User-Agent (if HTTP banner-grab is in play).
3. **WHOIS / ASN attribution.** Identify the source's ASN and known scanner attribution (Censys, Shodan, internetdb). Allowlisted? Stop here. Unknown? Continue.
4. **Hot-block at the perimeter** if the source is unknown and not in an allowlist of legitimate scanners. Document the block for IR ticket.
5. **Check correlated activity.** Did the same source touch any administrative panels, login pages, or API endpoints in the last 24 hours? Pivot to web/API logs.
6. **Open IR ticket** with: source IP, ASN, scan signature, blocked-or-not status, full packet capture path, pivot findings.

## Validation clues

- **High-confidence scan:** ≥ 100 distinct destinations or ports from one source in ≤ 60 s, with no prior baseline activity from that source.
- **Decoy attribution confirmed:** identical TCP fingerprints across "different" source IPs in the same alert window.
- **Banner-grab follow-up confirmed:** the same source that triggered Phase 1 also triggered Phase 2 against a small subset of "interesting" destinations — the operator's prioritization signal.
- **Idle scan against you as target:** target host logs show clean session from a known third-party IP; capture full packets and check the third party's IPID advance rate during the scan window.
- **You as zombie confirmed:** your host's IPID advanced by N units during a window where it issued only ~N/2 outbound flows.

## Mitigation / remediation

On the defender side, these are durable controls (not per-alert fixes):

- **Per-source-IP SYN-rate alerting** at the perimeter — defeats Masscan in seconds. The single highest-leverage control.
- **Behavioral clustering** (fan-out + TCP fingerprint) — defeats decoys. The senior version of the previous control.
- **IP fragment reassembly enabled at the IDS** — defeats `-f`/`--mtu` evasion ([[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]).
- **Per-destination IPID generation on every internet-facing host** — defeats classic idle scan ([[idle-scan-and-ipid-side-channels|Idle Scan and IPID Side Channels]]).
- **Version-banner shaping** — raises NSE `vuln` false-positive rate ([[nse-vuln-category-audit|NSE vuln Category Audit]]), lowers attacker signal asymmetrically.
- **Honeyports / tarpits on never-used ports** (e.g., 4444, 31337) — every external connection is a high-confidence alert with near-zero false-positive rate.
- **Reduce real attack surface** — alerting on scans is monitoring; the durable defense is reducing exposed services so there is less to find.

### What does not work as a primary defense

- **Blocking by source IP after the fact** — Masscan finishes its sweep in seconds; the block is post-mortem.
- **Geo-blocking** — operators rotate VPS in any country trivially.
- **Trusting "no alert" as evidence of safety** — operators using `-T2` `--scan-delay`, idle scan, or selectively targeted Boolean queries fly under threshold-based rules.
- **Counting individual port hits as alerts** — every internet-facing host receives constant port hits from internet noise. Alert on *fan-out* and *fan-in*, not on raw counts.

## Logging / forensics

- **Retain perimeter flow logs for ≥ 90 days.** Operators frequently scan, wait a week, then return to exploit. Without flow retention, the recon → exploit chain is invisible.
- **Retain full packet captures from any alert source for ≥ 30 days.** Captures support post-mortem TCP fingerprint analysis, JA3/JA4 extraction, and decoy clustering.
- **Tag every alert with: source IP, source ASN, TCP fingerprint hash, JA3 hash if TLS in play, allowlist status, blocked status.** These tags drive trend analysis across engagements.
- **Cross-reference with [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection]]** for the conceptual framing of why fan-out clustering beats per-source rate limits.

## Operational safety

- **never** auto-block a source whose ASN belongs to a known measurement / research organization without a manual review — false positives against Shodan / Censys / Project Sonar generate poor signal-to-noise and may violate measurement-research norms.
- **never** rely on a single detection layer. Phase 1 alerts from NetFlow combined with Phase 2 alerts from IDS produce a much higher-fidelity finding than either alone.
- **always** keep your IDS rule set updated weekly. NSE signatures evolve; stale rule sets produce false negatives.
- **always** test your detection rules against an authorized internal lab running [[run-scan-pipeline]] before relying on them. Untested rules are theater.
- **always** baseline first. Alerting without a baseline produces noise; alerting on a deviation from a known baseline produces signal.

## Related notes

- [[run-scan-pipeline]] — the offense playbook this one mirrors note-by-note.
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]] — the timing primitives this playbook is meant to detect.
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]] — the evasion family Phase 3 alerts target.
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]] — the breadth-phase tool whose signature drives Phase 1.
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]] — the depth-phase tool whose signature drives Phase 2.
- [[idle-scan-and-ipid-side-channels|Idle Scan and IPID Side Channels]] — the attribution-evading variant Phase 3 catches at the zombie side, not the target side.
- [[nse-vuln-category-audit|NSE vuln Category Audit]] — why banner shaping is asymmetric defender leverage against NSE.
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]] — the conceptual framing this playbook operationalizes.
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — what you can and cannot see at the perimeter; Phase 0 baseline material.
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]] — the broader framing of the rule pipeline this playbook lives in.
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]] — the specific tools the rules in this playbook target.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-principle this playbook pair operationalizes.

## References

- **Foundational:** MITRE ATT&CK T1595 — Active Scanning — https://attack.mitre.org/techniques/T1595/
- **Foundational:** MITRE D3FEND — Network Traffic Analysis — https://d3fend.mitre.org/technique/d3f:NetworkTrafficAnalysis/
- **Official Tool Docs:** Suricata rules documentation — https://docs.suricata.io/en/latest/rules/
- **Official Tool Docs:** Zeek scan.log and notice framework — https://docs.zeek.io/en/master/scripts/policy/protocols/conn/known-services.zeek.html
- **Research / Deep Dive:** David Bianco — The Pyramid of Pain (cost-asymmetry framing for which detection layers actually hurt attackers) — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html
