---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Scan Anomaly Detection and Fingerprint Analysis

## Definition

Scan anomaly detection is the identification of reconnaissance behavior from timing, fan-out, port distribution, TCP/IP features, protocol probes, TLS fingerprints, endpoint context, and transitions from discovery into service enumeration or exploitation.

## Why it matters

Scanning is one of the cleanest examples of telemetry warfare. The attacker thinks in targets, ports, timing templates, scan engines, and NSE categories. The defender sees packet rates, failed connection states, port entropy, destination fan-out, process-network joins, TLS handshakes, DNS, flow records, and correlation windows.

Legacy offensive culture often romanticizes "stealth scans." Modern defense changed the equation. Slow or fragmented scans may bypass a naive threshold, but they still create behavioral evidence across NetFlow, Zeek, Suricata, EDR, cloud logs, protocol fingerprints, and first-seen analytics.

## How it works

Scan detection answers **6 behavioral questions**:

1. **Fan-out:** Is one source contacting many destinations, many ports, or both?
2. **Port entropy:** Is the port sequence narrow and repeated, random-looking, full-range, or service-class focused?
3. **Timing:** Are probes bursty, randomized, periodic, or distributed across a long window?
4. **TCP/IP shape:** Do flags, options, window size, TTL, fragmentation, retransmits, and reset behavior resemble a scanner stack?
5. **Protocol depth:** Did the actor stop at SYNs, perform version detection, run NSE-style probes, fetch HTTP paths, or attempt authentication?
6. **Correlation:** Which process, user, asset role, cloud workload, identity, and prior alert history explain the network behavior?

Example:

```
Masscan-like: one source -> thousands of destinations on 443/tcp in seconds.
RustScan-like: one source -> one host, many ports, high concurrency, then Nmap probes.
Nmap NSE-like: few ports, many protocol-specific requests, distinctive HTTP/TLS/SMB script behavior.
Slow scan: low rate, long window, but first-seen contact to unusual ports across many assets.
```

The detection is not "Nmap was used." The detection is "this entity performed communication inconsistent with its role, at a shape and sequence consistent with discovery."

## Techniques / patterns

- **Horizontal scanning.** One or a small set of ports across many hosts. Example: `443/tcp` across a /16. Flow telemetry sees fan-out clearly.
- **Vertical scanning.** Many ports on one or a few hosts. Example: full-range `-p-` against a server. Endpoint and Zeek state patterns matter.
- **Block scanning.** Many hosts and many ports, often randomized. Masscan and ZMap-style tooling live here.
- **Scan entropy analysis.** Measure destination count, port count, service-class diversity, inter-arrival distribution, and novelty against the source host role.
- **Timing fingerprints.** Burst size, inter-packet gaps, retries, scan-delay patterns, and rate ceilings reveal tool behavior even when source IP changes.
- **TCP/IP fingerprinting.** Window size, options order, MSS, TTL distance, initial sequence behavior, fragmentation, and checksum behavior can cluster decoys or custom stacks.
- **TLS fingerprinting.** JA3/JA4-style metadata can distinguish scanner libraries, scripting runtimes, and non-browser clients even when HTTP payload is encrypted.
- **Scan-to-exploit transition.** A source that scans `80/443`, runs HTTP enumeration, then posts exploit-shaped payloads has crossed from discovery into testing.

## Variants and bypasses

Scan behavior has **8 detection-relevant families**.

### 1. Fast SYN fan-out

Masscan-like behavior sends high-rate SYNs with minimal state. It is visible in flow records, edge devices, Zeek `conn.log`, Suricata rules, and router counters long before payload analysis matters.

### 2. Full-range single-host scans

RustScan/Nmap full-range scans create high port entropy against one host. The network view is vertical; the endpoint view may show one scanner process opening many sockets quickly.

### 3. Service-aware Nmap enumeration

`-sV`, `-sC`, and NSE scripts produce fewer connections but more distinctive protocol transactions. This is where Suricata HTTP/SMB/TLS signatures and Zeek protocol logs become more useful than pure flow counts.

### 4. Slow scans

Slow scans lower per-minute thresholds but widen the defender's window. Correlation engines can aggregate first-seen ports and host spread over hours or days, especially when joined to process and asset role.

### 5. Fragmented and decoy scans

Fragmentation and decoys target outdated packet or source-IP assumptions. Modern defenses reassemble fragments and cluster by behavior, TCP fingerprint, destination overlap, and timing.

### 6. Distributed scans

Botnets, cloud accounts, proxies, and compromised hosts distribute source IPs. Detection shifts toward destination-centric aggregation, shared fingerprints, common timing, URI/probe sequence, and threat-intel enrichment.

### 7. TLS/application fingerprint scans

Scanners that probe HTTPS expose ClientHello shape, ALPN, SNI behavior, certificate validation patterns, user agents, and HTTP method/path sequences even without decrypted payload.

### 8. Internal authenticated discovery

EDR and identity logs matter more when scanning happens after a foothold. `net.exe`, PowerShell, `nmap`, `ldapsearch`, SMB enumeration, and cloud API inventory calls create process and identity evidence.

## Impact

- **Early warning.** Scanning can expose attack preparation before exploitation begins.
- **Asset validation.** Scan telemetry reveals unexpected services and boundary failures even if the scanner is benign.
- **Noise pressure.** Internet background scanning is constant; detections need asset criticality, novelty, and transition logic.
- **Adversary cost.** Correlation forces attackers to manage process identity, timing, TLS shape, source reputation, and target sequence, not just packets.
- **False confidence risk.** Missing scan alerts does not prove no scanning occurred; blind spots and thresholds may hide it.

## Detection and defense

Ordered by effectiveness:

1.
**Model source and destination role.**
   A vulnerability scanner, domain controller, CI runner, developer laptop, and database host should have different allowed discovery behavior. Baselines by role beat global thresholds.

2.
**Detect fan-out and entropy over multiple windows.**
   Use short windows for Masscan-like bursts and long windows for slow scans. Track distinct destination hosts, distinct ports, port classes, failed states, and first-seen combinations.

3.
**Correlate scan to process, user, and change context.**
   Authorized scans should map to known scanner assets, scheduled jobs, tickets, and expected tools. Unknown scan behavior from `powershell`, `python`, `curl`, or renamed binaries deserves priority.

4.
**Use protocol and fingerprint pivots.**
   JA3/JA4, HTTP user-agent, TLS ALPN, Zeek service inference, Suricata app-layer alerts, and TCP fingerprints add identity beyond source IP.

5.
**Detect transition, not only discovery.**
   Prioritize sources that scan, enumerate versions, fetch risky paths, attempt credentials, exploit a CVE path, or touch high-value services after discovery.

### What does not work as a primary defense

- **Blocking one scanner IP after detection.** Fast scanners finish before reactive blocking matters; durable defense needs exposure reduction and behavioral detection.
- **Assuming slow scans are invisible.** Slow scans trade rate visibility for long-window novelty, role mismatch, and correlation evidence.
- **Assuming fragmentation and decoys defeat modern sensors.** Reassembly, behavior clustering, TCP fingerprints, and EDR joins weaken these legacy tricks.
- **Relying on banner suppression alone.** It reduces one enumeration signal but does not remove port, timing, TLS, DNS, or process evidence.
- **Treating scan alerts as the root problem.** The root problem is often unexpected reachable services, weak boundaries, or unmanaged assets.

### Operational misconceptions

- **"Stealth means no logs."** Real stealth means managing all relevant telemetry, including endpoint, cloud, DNS, flow, TLS, and identity.
- **"Nmap timing templates define detectability."** `-T` changes packet timing; it does not erase protocol probes, process creation, target selection, or first-seen behavior.
- **"Encrypted scans hide everything."** TLS hides payload after handshake; it still exposes connection metadata and often handshake fingerprints.
- **"Decoys confuse attribution forever."** Decoys confuse naive per-IP logs, not behavior clustering across identical probe sequences.

### Modern limitations

- Internet background noise creates high baseline scan volume at the edge.
- NAT, proxies, cloud egress, VPN concentrators, and scanner fleets can collapse many actors into one source IP.
- Privacy-preserving protocols and encrypted client hello reduce some TLS metadata.
- Distributed low-volume scans can be hard to distinguish from normal service use without asset and identity context.

### Telemetry blind spots

- Flow sampling can miss low-rate or short-lived scans.
- Packet sensors may miss asymmetric paths, cloud east-west traffic, or overloaded SPAN feeds.
- EDR may not cover appliances, containers, unmanaged hosts, or scanner jump boxes.
- IDS signatures may miss custom probe order or encrypted application behavior.

## Practical labs

Use only owned lab ranges or explicit training environments.

### Compare Masscan and Nmap telemetry

```
# Owned lab /24 only.
sudo masscan 10.10.10.0/24 -p80,443 --rate 200 -oL masscan.lst
sudo nmap -Pn -sS -p80,443 10.10.10.0/24 -oA nmap-http
```

Expected telemetry: Masscan produces faster horizontal SYN fan-out with sparse state; Nmap creates slower, more stateful retries. Defenders should compare flow counts, Zeek `conn.log`, and Suricata scan alerts.

### Generate Zeek scan logs

```
sudo tcpdump -i any -w nmap-scan.pcap 'net 10.10.10.0/24'
nmap -Pn -p 22,80,443,445 10.10.10.20-40
zeek -r nmap-scan.pcap
zeek-cut id.orig_h id.resp_h id.resp_p conn_state history < conn.log | sort | uniq -c
```

Expected telemetry: repeated source, repeated ports, failed states, and similar TCP histories. The false assumption to test: "no Suricata alert means no scan."

### Observe NSE depth after discovery

```
nmap -Pn -sV --script "default,safe" -p 80,443 LAB_HOST -oA nse-depth
```

Expected telemetry: fewer ports but deeper HTTP/TLS transactions. Zeek `http.log`/`ssl.log` and Suricata HTTP/TLS rules should show script-specific behavior.

### Test slow-scan correlation

```
for p in 22 80 443 445 3389; do
  nmap -Pn -p "$p" --scan-delay 20s LAB_HOST
done
```

Expected telemetry: simple per-minute thresholds may not fire. Long-window analytics should still observe first-seen port contacts and unusual process-network behavior.

### Test fragmentation as a modern evasion claim

```
sudo nmap -Pn -sS -p 80 LAB_HOST
sudo nmap -Pn -sS -f -p 80 LAB_HOST
sudo nmap -Pn -sS --mtu 24 -p 80 LAB_HOST
```

Expected telemetry: a modern Suricata/Zeek lab should still reconstruct or at least expose fragment behavior. If results differ, the lab found an inspection-path property, not "magic stealth."

### Compare TLS fingerprint pivots

```
curl -vk https://LAB_HOST/ >/dev/null
python3 - <<'PY'
import urllib.request
urllib.request.urlopen("https://LAB_HOST/", timeout=3)
PY
```

Expected telemetry: the same URL can produce different TLS/client fingerprints and user agents. Defenders should treat fingerprints as pivots that need process and asset context.

## Practical examples

- A vulnerability scanner account runs a scheduled Nmap job; it is noisy but expected, ticketed, and source-pinned.
- A workstation launches `rustscan` then `nmap -sV`; EDR and Zeek together show discovery followed by enumeration.
- A cloud workload contacts hundreds of internal `22/tcp` and `445/tcp` endpoints after a new deployment, indicating either misconfigured service discovery or compromise.
- A decoy scan produces 20 source IPs with identical TCP option order and target sequence, making behavior clustering stronger than IP attribution.
- A slow scan over 48 hours is detected because a database host made first-ever contact to many admin ports.

## Related notes

- [[index|Detection Engineering]]
- [[network-telemetry-sources-and-visibility]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[zeek-suricata-and-netflow-analysis]]
- [[edr-network-observability-and-process-correlation]]
- [[behavioral-detection-vs-signature-detection]]
- [[false-positives-false-negatives-and-detection-tradeoffs]]
- [[encrypted-traffic-analysis-and-metadata-leakage]]
- [[detection-evasion-myths-and-modern-limitations]]
- [[attack-path-correlation-and-kill-chain-observability]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[nmap-scanning|Nmap Scanning]]
- [[external-attack-surface|External Attack Surface]]
- [[run-scan-pipeline|Run External Recon Scan Pipeline]]

### Suggested future atomic notes

- scan-to-exploit-transition-detection
- tls-fingerprinting-for-detection
- honeyports-and-tarpit-detection
- scan-entropy-analysis
- distributed-scan-correlation

## References

- **Official Tool Docs:** Nmap Timing and Performance - https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README and man page - https://github.com/robertdavidgraham/masscan
- **Foundational:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Research / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
