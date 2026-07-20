---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Nmap Timing and Evasion

## Definition

Nmap timing and evasion is the use of Nmap's rate, retry, parallelism, and packet-shape primitives to either (a) reduce false `filtered` results against rate-limited networks or (b) test what an IDS/IPS, WAF, or stateful firewall will and will not catch.

## Why it matters

Default Nmap behavior optimizes for accuracy on a quiet LAN. Production internet targets sit behind rate limiters, dropping middleboxes, and per-source-IP thresholds — defaults produce *wrong* results there, not just slow ones. Senior usage drives the individual timing knobs explicitly so that scan output is repeatable, comparable across runs, and defensible in a report.

The evasion primitives matter less for hiding (modern stateful inspection neutralizes most of them) and more as a diagnostic toolkit: each primitive isolates one inspection layer, so a probe matrix tells you exactly which control caught you. That mapping is what separates a scan operator from someone running `nmap -A target`.

## How it works

Nmap timing is **5 dials** wearing one preset's clothing:

1. **Per-probe timeout** (`--min-rtt-timeout`, `--max-rtt-timeout`, `--initial-rtt-timeout`) — how long to wait before declaring a probe lost.
2. **Retry count** (`--max-retries`) — how many times to resend a lost probe before calling the port `filtered`.
3. **Concurrency** (`--min-parallelism`, `--max-parallelism`) — how many in-flight probes Nmap maintains.
4. **Rate** (`--min-rate`, `--max-rate`) — packets-per-second floor/ceiling, the most predictable knob.
5. **Spacing** (`--scan-delay`, `--max-scan-delay`) — deterministic gap between probes to defeat rate-limit detectors.

The `-T0` through `-T5` templates are preset combinations of those 5 dials. They are useful as conversation, not as engagement controls:

```
-T0 paranoid    5 min between probes        IDS evasion theatre
-T1 sneaky      15 s between probes         IDS evasion theatre
-T2 polite      0.4 s spacing, low rate     shared-network considerate
-T3 normal      Nmap default                LAN baseline
-T4 aggressive  fast, max-retries 6         what most tutorials use
-T5 insane      very fast, max-retries 2    accuracy starts dropping
```

The bug in most engagements is not "the scan was too slow"; it is "the scan was rate-limited by an upstream control and Nmap silently relabeled `open` ports as `filtered`."

## Techniques / patterns

- Pin **`--min-rate`** instead of `-T` for reproducible runs (e.g., `--min-rate 100 --max-rate 300`).
- Detect rate limiting with **two runs at different rates**: if `filtered` count rises sharply at higher rates, a rate limiter is in path, not a firewall blocking the port outright.
- Use **`--scan-delay`** when an IDS triggers on N probes within W seconds — deterministic spacing under the threshold beats randomized timing.
- Use **`--max-retries 1`** for fast first-pass discovery, then rescan only `open` and `open|filtered` ports with `--max-retries 6` and `-Pn`.
- **Source-port spoofing** (`--source-port 53`, `--source-port 88`) — many old firewall ACLs trust traffic *from* port 53/88 to permit DNS/Kerberos returns. Still works on misconfigured perimeter ACLs in 2026.
- **`--badsum`** — IDS detection: real OSes drop checksum-invalid packets, IDS engines that don't validate the checksum reply anyway and self-report their presence.
- **`--data-length N`** — varies probe payload size, defeating signature rules that match on exact length.
- **`--spoof-mac 0`** or `--spoof-mac Cisco` — randomizes/spoofs the local MAC. Layer-2 only, so useful only inside a broadcast domain (Wi-Fi audit, lab segment).

## Variants and bypasses

Senior usage clusters into **4 modes**.

### 1. Accurate-against-rate-limiters

Goal: get true `open` state on a hardened target. `nmap -Pn -sS --min-rate 200 --max-rate 500 --max-retries 3 -p- target`. Knobs pinned, not template-driven, so the next operator can reproduce.

### 2. Diagnostic packet-shape matrix

Goal: figure out which inspection layer caught the scan. Run the *same* port list with `-f`, `--mtu 16`, `--data-length 200`, `--badsum`, `--source-port 53`, and `-D RND:10` separately. Whichever variant returns `open` reveals what the middlebox does and does not inspect.

### 3. Stealth-from-logs (idle scan)

`nmap -sI zombie:port target` — the scanner's IP never appears in target logs. Requires a "zombie" host with globally-incrementing IPID. Most modern OSes randomize IPID; this is now a niche technique for legacy environments.

### 4. Source-port and TTL trickery

`--source-port 53` and `--ttl N` exploit stateless ACLs that trust *source-port equals 53* or *TTL equals expected hop-count*. Both are legacy patterns, both still appear on old appliances.

## Impact

- **False negatives** from defaulting to `-T4` against rate-limited targets, missing real exposure.
- **Engagement detection** — a `-T5` scan trips most modern IDS/WAFs in seconds. Most red-team detections are not malware, they are aggressive scans.
- **Scope blowback** — `-D` with random decoys can include in-scope third-party IPs as fake sources, which some IDS pipelines escalate to abuse complaints against those third parties.
- **Service disruption** — `-T5 --min-rate 50000` against an embedded device or low-spec service can lock it up (legacy SCADA, printers, IoT).

## Detection and defense

1.
**Stateful inspection plus connection-rate limiting per source IP.**
   The combination defeats almost all of Nmap's stealth and timing tricks at once. Stateless ACLs that trust `--source-port 53` or fragment behavior are the failure mode evasion was designed against.

2.
**IDS rules tied to TCP flag combinations.**
   `-sN`, `-sF`, `-sX`, `-sM` send invalid flag combinations. Snort/Suricata/Zeek default rule sets catch these reliably — their continued use is a marker of an unsophisticated scanner.

3.
**Distribution-based anomaly detection on probe distribution.**
   Per-source-IP entropy on destination port × time defeats `--scan-delay` evasion because the *fingerprint* (one source touching many ports, even slowly) is still anomalous.

4.
**Honeyports / tarpits.**
   A handful of monitored ports that should never see traffic (`tcp/4444`, `tcp/31337`) turn any external scan into a high-confidence alert without false positives from normal traffic.

### What does not work as a primary defense

- **Hiding the perimeter** ("we're not listed in DNS") — Masscan/Shodan see you anyway. Not a control.
- **Banner suppression** as a primary control — it reduces noise in NSE output, not exploitability.
- **`-Pn` blocking** by dropping ICMP echo — Nmap defaults to TCP probes when ICMP is filtered; you have not blocked discovery, you have only made it slower.

## Practical labs

```
# Lab 1 — reveal rate limiting on an authorized target.
nmap -Pn -sS -p 1-1000 --min-rate 50 --max-rate 100 -oN slow.txt LAB
nmap -Pn -sS -p 1-1000 --min-rate 5000 --max-rate 5000 -oN fast.txt LAB
diff <(grep '^[0-9]' slow.txt) <(grep '^[0-9]' fast.txt)
# What ports moved from open -> filtered between runs is the rate-limit signature.
```

```
# Lab 2 — packet-shape diagnostic matrix on one open port.
PORT=443
for FLAG in "" "-f" "--mtu 16" "--data-length 200" "--badsum" "--source-port 53"; do
  echo "===== $FLAG"
  nmap -Pn -sS -p $PORT $FLAG LAB
done
# Whichever invocation still reports open tells you what the inspection device skipped.
```

```
# Lab 3 — confirm an IDS validates checksums.
nmap -Pn --badsum -p 80,443 LAB
# Real targets answer with nothing (OS drops invalid checksum). If you get RST/ACK,
# something on path is replying without validating the TCP checksum — an inline IDS.
```

```
# Lab 4 — idle scan against an authorized lab zombie.
sudo nmap -sn -PR LAB_NET                            # find candidate zombies
sudo nmap -sI ZOMBIE:80 -p 22,80,443,3389 TARGET     # only works if ZOMBIE has incrementing IPID
# Verify with: nmap -O ZOMBIE  -> look for "IP ID Sequence Generation: Incremental".
```

```
# Lab 5 — `--scan-delay` to evade per-source connection-rate IDS.
sudo nmap -Pn -sS -p 22,80,443,3389 --scan-delay 2s --max-retries 1 LAB
# Compare alert count in IDS console with and without --scan-delay 2s.
# This is the empirical version of the textbook claim "spacing defeats threshold detection".
```

## Practical examples

- **External engagement against a CDN-fronted app.** Default `-T4` returns all ports `filtered`; pinning `--min-rate 50 --max-rate 100` reveals real open ports behind the CDN's per-IP rate limit.
- **Bug bounty asset rescan.** Quarterly `nmap -Pn -sS --min-rate 200 -p- ASN-IP-LIST` with locked timing flags lets you diff exposure across quarters without timing noise.
- **Lab vs. production parity.** Same scan flags against staging and production reveal that the staging WAF is configured differently from prod — a recurring real finding.
- **Detecting a transparent IDS.** A `--badsum` probe to a well-known closed port returning RST/ACK is a clean indicator of inline inspection that does not validate checksums.
- **Old DC perimeter.** `--source-port 53` against an unmanaged perimeter still finds open services the default scan misses — diagnostic of an obsolete stateless ACL.

## Related notes

- [[nmap-scanning|Nmap Scanning]]
- [[ports-and-services|Ports and Services]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[service-enumeration|Service Enumeration]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[active-recon|Active Recon]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[detection-evasion-myths-and-modern-limitations|Detection Evasion Myths and Modern Limitations]]
- [[packet-fragmentation-and-decoy-scans]]
- [[masscan-internet-scale-scanning]]
- [[rustscan-and-nse-pipeline]]

### Suggested future atomic notes

- ids-evasion-fundamentals
- scan-to-exploit-transition-detection
- [[idle-scan-and-ipid-side-channels]]
- firewall-fingerprinting-with-nmap

## References

- **Official Tool Docs:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — Host and Port Discovery — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
