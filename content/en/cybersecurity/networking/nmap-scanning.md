---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Nmap Scanning

## Definition

Nmap is a network discovery and scanning tool used to identify reachable hosts, open ports, service versions, protocol behavior, and basic exposure from a chosen network viewpoint.

## Why it matters

Nmap turns architecture assumptions into evidence. It tells you what responds from where you are standing: public internet, VPN, bastion, container, subnet, or cloud workload. That viewpoint matters because an "open" port is always relative to a path.

This note owns Nmap scan strategy. [[ports-and-services]] owns the concept of listening surface. [[service-enumeration]] owns interpreting what the service appears to be after a port is found.

## How it works

Nmap scanning answers **5 questions**:

1. **Is the host reachable?** Host discovery probes decide whether Nmap treats a target as alive.
2. **Which ports respond?** TCP/UDP scan types infer open, closed, or filtered state.
3. **What service is likely listening?** Version detection probes banners and protocol responses.
4. **What extra behavior is exposed?** NSE scripts can check TLS, HTTP, SMB, DNS, and many other services.
5. **What does this viewpoint see?** Results differ from public internet, internal subnet, VPN, or cloud VPC.

Example:

```
nmap -Pn -sS -sV --top-ports 1000 app.example.com
```

Interpretation:

- `-Pn` skips host discovery and scans even if ping-like probes are blocked.
- `-sS` performs TCP SYN scanning where privileges allow.
- `-sV` asks services to identify themselves.
- `--top-ports 1000` prioritizes common ports quickly.

The bug is not "a port is open"; the bug is unexpected reachability or service behavior from a viewpoint that should not have access.

## Techniques / patterns

Attackers and defenders use Nmap to:

- compare intended exposure against observed exposure
- scan from multiple viewpoints: public, VPN, internal, container, cloud workload
- distinguish `open`, `closed`, and `filtered`
- identify service versions with `-sV`
- inspect TLS/HTTP posture with safe NSE scripts
- enumerate UDP carefully because silence can mean filtering or packet loss
- validate firewall/security-group changes before and after deployment
- produce repeatable evidence for findings and remediation

## Variants and bypasses

Nmap workflows fall into **6 practical modes**.

### 1. Host discovery

`-sn`, ARP, ICMP, TCP ping, and related probes identify live hosts. Firewalls may block some probes, so a host that looks down may still have open services.

### 2. TCP port scanning

SYN (`-sS`), connect (`-sT`), and full-range scans identify listening TCP services. `open`, `closed`, and `filtered` are network observations, not vulnerability labels.

### 3. UDP scanning

UDP (`-sU`) is slower and noisier because many services do not respond unless the payload is protocol-correct. Use targeted ports and expect ambiguity.

### 4. Service/version detection

`-sV` sends probes to infer protocol and software. It is more useful than banner grabbing alone, but still an inference that should be validated manually for important findings.

### 5. NSE script checks

Nmap Scripting Engine can check TLS ciphers, HTTP titles, default scripts, SMB info, DNS behavior, and more. NSE is powerful; choose scripts deliberately and avoid intrusive categories unless authorized.

### 6. Evasion and timing controls

Timing (`-T`), rate limits, source ports, fragmentation, and decoys exist, but defensive validation usually benefits more from clear, reproducible scans than stealth.

## Impact

Ordered roughly by severity:

- **Unexpected public exposure.** Databases, admin panels, SSH, Redis, Elasticsearch, or dev servers reachable from the internet.
- **Boundary failure.** Ports visible from a network segment that should not reach them.
- **Shadow services.** Old daemons or sidecar ports not tracked in inventory.
- **Version disclosure.** Service detection reveals outdated software or risky defaults.
- **False confidence.** A scan from the wrong viewpoint misses the real path attackers or workloads can use.
- **Operational noise.** Aggressive scans can trigger alerts or degrade fragile systems if run carelessly.

## Detection and defense

Ordered by effectiveness:

1.
**Scan from the same viewpoints real callers use.**
   Public exposure, VPN exposure, internal subnet exposure, and container-to-host exposure are different truths. A single scan from your laptop is not enough to validate a boundary.

2.
**Keep scans scoped, authorized, and reproducible.**
   Save target lists, flags, date, source IP, and output. Reproducible scans let defenders compare before/after remediation without arguing from screenshots.

3.
**Use staged depth.**
   Start with fast top-port or known-port scans, then deepen only where needed with full ports, `-sV`, UDP, or scripts. This reduces noise and keeps results interpretable.

4.
**Validate high-impact results manually.**
   If Nmap says a database or admin service is exposed, confirm with protocol-specific tooling or banner grabs. False positives and service mislabels happen.

5.
**Integrate scan results with inventory.**
   Every unexpected service should become an ownership question: who owns it, why is it reachable, and what boundary should protect it?

6.
**Monitor for scanning but do not treat scanning as the root problem.**
   Alerts on scan patterns are useful, but the durable defense is reducing exposed services and tightening boundaries.

### What does not work as a primary defense

- **"Nmap did not find it" as proof of absence.** Firewalls, UDP ambiguity, timing, IPv6, alternate hostnames, and viewpoint differences can all hide exposure.
- **Scanning only DNS names.** Direct IPs, old origins, and cloud ranges may expose services not linked from current DNS.
- **Using `-A` everywhere.** Aggressive detection increases noise and may run scripts you did not intend. Use it deliberately.
- **Treating filtered as safe.** Filtered means Nmap could not get a clear answer from that path. It does not prove the service is secure.
- **Ignoring IPv6.** Many environments secure IPv4 and accidentally expose IPv6.

## Practical labs

Run only on systems you own or have explicit authorization to test.

### Fast external posture scan

```
nmap -Pn --top-ports 1000 -oA scans/app-top app.example.com
```

Use this as a quick public exposure snapshot.

### Service/version detection on known ports

```
nmap -Pn -sV -p 22,80,443,8080,8443 -oA scans/app-services app.example.com
```

Follow up any unexpected protocol or version manually.

### Compare public and internal viewpoints

```
# From public internet
nmap -Pn -p 22,80,443,5432,6379 app.example.com

# From VPN/internal host
nmap -Pn -p 22,80,443,5432,6379 app.example.com
```

The difference between these outputs is often the boundary story.

### Full TCP scan when top ports are not enough

```
nmap -Pn -p- --min-rate 1000 -oA scans/app-alltcp app.example.com
```

Use when you suspect high-port admin/dev services.

### Targeted UDP scan

```
nmap -Pn -sU -p 53,123,161,500,4500 --version-light app.example.com
```

UDP is slower and ambiguous; keep it targeted.

### Safe NSE usage

```
nmap -Pn -sV --script "default,safe" -p 80,443 app.example.com
nmap -Pn --script ssl-enum-ciphers -p 443 app.example.com
```

Avoid intrusive scripts unless the scope explicitly allows them.

## Practical examples

- Public scan finds `5432/tcp open postgresql` on a host that should expose only HTTPS.
- Internal scan sees Redis on `6379` while public scan does not, confirming segmentation is partly working.
- IPv6 scan finds SSH reachable even though IPv4 security groups are tight.
- `-sV` identifies a dev server on `3000` behind an old DNS record.
- A before/after scan proves a firewall change removed public access to an admin port.

## Related notes

- [[ports-and-services]] — what listening surface means.
- [[service-enumeration]] — interpreting service behavior after discovery.
- [[firewalls-and-network-boundaries]] — validating boundary rules.
- [[exposed-service-triage|Exposed Service Triage]]
- [[packet-analysis]] — inspect traffic when scan behavior is unclear.
- [[wireshark-workflows]] — packet-capture workflow for scan validation.
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]] — deep dive on timing/evasion knobs introduced in mode 6.
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]] — companion deep dive on `-f`/`--mtu`/`-D` mechanics.
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]] — the bulk-discovery pair when address space exceeds Nmap's comfortable scale.
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]] — single-host accelerator that feeds Nmap.
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]] — defender-side interpretation of scan timing, entropy, fingerprints, and transitions.
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]] — how scanner behavior joins to process and user context.

### Suggested future atomic notes

- nmap-scan-types
- udp-scanning
- nse-scripts
- ipv6-exposure-scanning
- scan-scope-and-authorization
- external-vs-internal-scanning
- scan-to-exploit-transition-detection

## References

- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
