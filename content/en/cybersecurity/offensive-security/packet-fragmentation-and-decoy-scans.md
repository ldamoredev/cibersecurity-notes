---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Packet Fragmentation and Decoy Scans

## Definition

Packet fragmentation (`-f`, `--mtu`) and decoy scans (`-D`) are two Nmap evasion primitives that operate at different layers: fragmentation splits probe headers across the IP fragmentation boundary to defeat *packet-level* signature matching, while decoys flood target logs with additional fake source IPs to defeat *log-level* attribution.

## Why it matters

Both techniques are widely taught and widely misunderstood. They are not stealth — modern stateful inspection reassembles fragments and modern SIEMs cluster by behavior, not by source IP. Their real value is *diagnostic*: each primitive isolates one assumption in a middlebox or detection pipeline. Mapping which primitives still work against a given target is how a senior scan operator reads the inspection stack from the outside.

Mistaking either for actual stealth is the textbook beginner error. Mistaking either for useless is the textbook intermediate error. The senior framing is that they answer the question "what does the target's inspection pipeline assume about packets and sources?".

## How it works

### Fragmentation

1. `-f` splits the TCP header across IP fragments of 8 bytes each. A normal TCP header is 20 bytes, so it ends up across 3 fragments.
2. `--mtu N` lets the operator pick the MTU (must be a multiple of 8). `--mtu 24` is the common variant.
3. The IP reassembly happens at the destination OS — but middleboxes (firewalls, IDSes) may or may not reassemble before applying signatures.
4. The bug being exploited: a signature engine that reads only the first fragment cannot see the TCP flags, source/dest port, or any of the L4 payload. If it does not reassemble, it cannot match.
5. Modern Snort/Suricata/Zeek reassemble by default. Legacy stateless ACLs and some embedded device firewalls do not.

### Decoys

1. `-D decoy1,decoy2,ME,decoy4` injects scan packets with spoofed source IPs alongside the real one. `ME` marks the real source position (defaults to randomized).
2. `-D RND:10` generates 10 random IPs each scan iteration.
3. The target sees 11 sources hitting it. From the *target log*, the real scanner is one entry among many.
4. Decoy packets have spoofed source IPs but the same scan fingerprint, same timing, same probe types as the real ones.
5. Returns go to the spoofed IPs, not the scanner. Decoys are useful only for SYN-scan-like flows where the scanner does not need the SYN-ACK reply to that decoy (the real source still gets its own replies).

The bug is not "fragments are hidden" or "decoys are anonymous"; the bug is "the target's defense assumes whole packets and one-IP-one-actor — primitive checks make the inspection layer reveal which assumption it uses."

## Techniques / patterns

- **Two-pass diagnostic.** Run identical port list with and without `-f`. Ports only `open` in the fragmented run reveal that one middlebox does not reassemble.
- **`-D ME` placement matters.** Decoys before/after `ME` change which packet hits the target first; some IDSes alert on the *first* source seen, which then becomes the "real" attribution from their viewpoint.
- **Decoys must be reachable IPs.** Decoy IPs that are unrouteable get dropped at the first hop and never reach the target — your "10 decoys" might be effectively zero.
- **Combine with `--data-length`.** Without random payload, fragmented probes still have a constant probe-length fingerprint per scan type. `--data-length 200` adds entropy.
- **`--ip-options`** (`R` record-route, `T` timestamp, `L` loose-source-route, `S` strict-source-route) — manipulates IP options. Most edge networks drop source-routed packets; if a target answers a loose-source-routed probe, you have just diagnosed a misconfigured router.
- **Never use real third-party IPs as decoys** for production engagements. Abuse complaints against bystanders happen — random RFC 5737 documentation IPs (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) are operationally safer than `RND:N`.

## Variants and bypasses

### Fragmentation variants

#### Tiny fragments (`-f`)

8-byte fragments. Defeats only signature engines that read the first fragment only. Almost all modern IDSes reassemble.

#### Custom MTU (`--mtu N`)

N must be a multiple of 8. `--mtu 16` produces fragments large enough to include the TCP header in the first fragment but small enough to split the payload — useful against engines that reassemble payload separately from header.

#### Overlapping fragments

Crafted by hand (Scapy), not Nmap. Different OSes use different reassembly policies (first-wins BSD, last-wins Windows, RFC 1122 Linux). An attacker who knows the target's policy can craft fragments such that the IDS reconstructs one TCP segment and the target reconstructs another — the *target-vs-IDS* desync attack.

### Decoy variants

#### Random decoys (`-D RND:N`)

Cheapest, noisiest, most likely to involve unrouteable or unrelated IPs. Default tutorial recipe.

#### Curated decoys

Hand-picked decoy IPs from the target's own AS, partner networks, or known scanners (Censys, Shodan, internet-measurement projects). Buries the real source in expected noise — significantly more effective against analyst review.

#### Idle scan (`-sI`)

Not strictly a decoy but the same family — uses a third-party "zombie" host's incrementing IPID counter to infer port state. Scanner's IP never appears in target logs at all. The only true source-attribution-evading scan Nmap supports.

## Impact

- **False reduction in source-IP detection rate** when log triage is naive.
- **Diagnostic disclosure** — fragmentation differences and decoy effectiveness reveal the inspection stack to the operator, which on a red team is itself valuable intel.
- **Operational risk** — random decoys against critical infrastructure can trigger abuse complaints against unrelated third parties. RFC 5737 documentation ranges or test-net IPs avoid this.
- **Misattribution within the target SOC** — analysts who do not realize decoys are in play may chase one of the decoy IPs as the "real" attacker, wasting engagement time.

## Detection and defense

1.
**Reassemble at the IDS.**
   Default Snort/Suricata/Zeek behavior. Defeats fragmentation entirely. The defense is *configuration audit*, not buying a new product — the feature is in every modern engine, but operators sometimes disable it for throughput.

2.
**Cluster log entries by behavior, not source IP.**
   If 11 IPs send identical probe sequences within milliseconds, they are one actor with decoys. Modern SIEM correlation rules express this as "alert when N distinct source IPs hit the same dst:port within W seconds with identical TCP fingerprint."

3.
**Drop source-routed and timestamp-option packets at the edge.**
   `--ip-options` games stop working if the perimeter drops IP options unconditionally. Most modern routers do this by default but legacy core/distribution layers may not.

4.
**Per-source-IP rate limit combined with TCP fingerprinting (p0f-style).**
   Even with decoys, the scanner's OS leaks (TTL, window size, options order, MSS) appear identically across all decoy packets — the fingerprint *is* the cluster key.

### What does not work as a primary defense

- **Blocking ICMP** in the belief it will stop scans — Nmap defaults to TCP probes; this slows nothing and gives a false sense of security.
- **Hoping the IDS sees through `-f`** without auditing reassembly settings — reassembly is configurable, and "default on" varies by vendor and rule pack.
- **Geo-blocking the obvious decoy IPs** — random IP ranges defeat geo filtering trivially; the right control is behavioral clustering, not geography.

## Practical labs

```
# Lab 1 — fragmentation diagnostic on an authorized lab IDS.
sudo nmap -Pn -sS -p 22,80,443 LAB > normal.out
sudo nmap -Pn -sS -p 22,80,443 -f > frag.out
sudo nmap -Pn -sS -p 22,80,443 --mtu 24 > mtu24.out
diff normal.out frag.out; diff frag.out mtu24.out
# Ports open in frag.out/mtu24.out but missing in normal.out reveal a non-reassembling middlebox.
```

```
# Lab 2 — decoy attribution test on an authorized lab IDS.
sudo nmap -Pn -sS -p 80 -D 192.0.2.10,192.0.2.20,ME,192.0.2.30 LAB
# Then check the IDS console: does it cluster the 4 sources as one actor, or alert 4 times?
# That distinguishes a modern SIEM from a per-IP alert engine.
```

```
# Lab 3 — TCP fingerprint persists across decoys.
sudo nmap -Pn -sS -p 80 -D RND:10 LAB
# In a Wireshark capture from the IDS sensor, all 11 source IPs carry identical
# TTL, window size, MSS, and TCP options. That is the fingerprint that beats decoys.
sudo tshark -i any -f 'host LAB and tcp port 80' -T fields -e ip.src -e ip.ttl -e tcp.window_size_value
```

```
# Lab 4 — idle scan when a zombie exists.
sudo nmap -O ZOMBIE | grep "IP ID Sequence"        # need "Incremental"
sudo nmap -Pn -sI ZOMBIE:80 -p 22,80,443,3389 LAB
# Target logs will show ZOMBIE, never your scanner IP. Only ethical against owned labs.
```

```
# Lab 5 — IP options probe.
sudo nmap -Pn --ip-options "L 192.0.2.1" -p 80 LAB
# Replies indicate the path tolerates loose source routing, which is a routing misconfiguration finding.
```

## Practical examples

- **Hardened cloud target.** Fragmentation produces zero new `open` ports — the cloud provider's edge reassembles. Useful negative result: rules out that evasion class for the next phase.
- **Legacy industrial network.** `-f` reveals ports invisible to the default scan because the inline appliance is a 2008-era stateless firewall.
- **Red-team engagement against a SIEM team.** Curated decoys from the target's own AS test whether SIEM clusters by behavior or by source IP — the answer drives the next phase's noise budget.
- **Bug bounty scope with strict per-IP rate limiting.** Decoys are useless (rate limit applies to your IP regardless of fakes); switch to `--scan-delay` instead. Recognizing this saves hours.
- **Forensic exercise.** Given a packet capture with `-D RND:10` traffic, reconstruct the real scanner IP by comparing TTL distance and TCP fingerprint across sources — the senior defensive skill that mirrors the offensive primitive.

## Related notes

- [[nmap-timing-and-evasion]]
- [[nmap-scanning|Nmap Scanning]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[detection-evasion-myths-and-modern-limitations|Detection Evasion Myths and Modern Limitations]]
- [[masscan-internet-scale-scanning]]

### Suggested future atomic notes

- ids-evasion-fundamentals
- fragmentation-reassembly-policies
- scan-fingerprinting-defense
- [[idle-scan-and-ipid-side-channels]]

## References

- **Official Tool Docs:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Research / Deep Dive:** Ptacek & Newsham — Insertion, Evasion, and Denial of Service (1998), foundational fragmentation-evasion paper — https://insecure.org/stf/secnet_ids/secnet_ids.pdf
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — Host and Port Discovery — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
