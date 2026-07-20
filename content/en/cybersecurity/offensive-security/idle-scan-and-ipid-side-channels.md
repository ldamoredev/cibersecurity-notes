---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Idle Scan and IPID Side Channels

## Definition

An **idle scan** (`nmap -sI zombie:port target`) infers a target's port state without sending a single packet from the attacker's real IP. It works by exploiting a **predictable IPID counter** on a third-party "zombie" host: the attacker probes the zombie's current IPID, sends a spoofed SYN to the target *as if from the zombie*, then re-probes the zombie's IPID. The delta reveals whether the target replied — and to whom. **IPID side channels** is the broader family of inference attacks that use any host's IP identifier field as an observable counter to derive information the attacker cannot see directly.

## Why it matters

Idle scan is the only Nmap scan where the scanner's IP **never appears in the target's logs**. Every other scan — even `-sN`, `-sF`, `-D RND:10` — emits packets from the real source. The decoys raise noise; the source is still there. Idle scan is structurally different: the target only ever sees traffic from the zombie. For source-attribution evasion this is unique.

It also matters as a teaching note because it teaches **three transferable senior ideas**:

- **Predictable counters leak information.** Any globally incrementing counter (IPID, TCP ISN under weak RNGs, certain SNMP counters) is a side-channel oracle. The vulnerability is the predictability, not the protocol.
- **Trust assumptions stack.** Idle scan assumes (a) the zombie answers consistently, (b) the target trusts the zombie's source IP, (c) the zombie is otherwise quiet enough for delta inference to be reliable. Each assumption is its own attack surface.
- **Defenses are protocol-spec changes.** RFC-level guidance to randomize IPID neutralized classic idle scan on every major OS. Senior thinking treats the *protocol field* as the attack surface, not the tool.

Idle scan today is mostly **diagnostic** rather than operational — modern OS IPID randomization defeats it on Linux, OpenBSD, modern Windows, and most cloud workloads. But IoT devices, legacy embedded systems, and misconfigured NAT gateways still ship globally-incrementing IPID generators, and the technique remains a clean way to *prove* an environment is older than its operators claim.

## How it works

Idle scan reduces to **3 round-trips** and **a one-bit observation**:

1. **Probe the zombie's current IPID.** Attacker sends an unsolicited SYN-ACK to the zombie. Zombie replies with RST, carrying IPID = N.
2. **Spoof a SYN to the target from the zombie's IP.** Target receives a SYN that looks like it came from zombie.
   - If the target port is **open**: target replies SYN-ACK to the zombie. Zombie was not expecting this, so it replies with RST — *and increments its IPID*. Zombie IPID is now N+1.
   - If the target port is **closed**: target replies RST to the zombie. Zombie drops the unsolicited RST and does *not* send any packet. Zombie IPID stays at N.
3. **Re-probe the zombie's IPID.** Attacker sends another unsolicited SYN-ACK. Zombie replies with RST, carrying its current IPID:
   - **N+2** (started at N, incremented once during step 2, incremented once now) → port was **open**.
   - **N+1** (no step-2 increment, only this probe) → port was **closed**.

A representative invocation:

```
# 1) Find a candidate zombie — must have INCREMENTAL IPID.
sudo nmap -O ZOMBIE_CANDIDATE | grep -i 'ip id sequence'
# Look for: "IP ID Sequence Generation: Incremental"

# 2) Run the idle scan.
sudo nmap -Pn -sI ZOMBIE:80 -p 22,80,443,3389 TARGET
# Target sees traffic from ZOMBIE only. Your IP appears nowhere in the target's logs.
```

The bug is not "Nmap can spoof source IPs" (that has always been possible); the bug is *the third-party host's IPID counter is a measurable side channel that leaks the target's response — and is observable to anyone who can probe the third party*.

## Techniques / patterns

- **Zombie selection is the entire engagement.** A good zombie has: (a) `IP ID Sequence Generation: Incremental` per `nmap -O`, (b) low traffic so the IPID delta is exactly +2 or +1 (busy zombies advance multiple times between probes, producing noise), (c) network reachability to the target on the relevant ports.
- **Verify the zombie's IPID generation before scanning.** `nmap -O` is the first move; if the result is `Random` or `Randomized`, that zombie is useless. `Broken little-endian incremental` (Windows 95-era) is workable but rare in 2026.
- **Modern IoT and printers are the typical zombie source.** Embedded network stacks frequently still use global incremental IPID. Network printers, KVM switches, video doorbells, industrial controllers, and out-of-band management interfaces are recurring candidates.
- **Idle scan is slow.** Each port requires multiple round-trips. Practical for confirming exposure on a handful of high-value ports; impractical for `-p-` full-range scans.
- **The `--proxies` flag is not the same thing.** `nmap --proxies` chains HTTP/SOCKS proxies and rewrites the source at the proxy layer — useful for reachability, useless for evasion (the proxy still logs you). Idle scan removes the source from the *target's* logs.
- **OPSEC: detection lives at the zombie, not the target.** A defender who controls the zombie can correlate three things — IPID jumps that don't match outbound traffic, unsolicited SYN-ACKs from your IP, and unsolicited responses arriving from the target. The technique evades target-side detection by design; defender response is "watch your own infrastructure for being used as a zombie".

## Variants and bypasses

The IPID-side-channel family has **4 important variants**.

### 1. Classic idle scan (Nmap `-sI`)

The flow described above. Requires an incremental-IPID zombie reachable from both the attacker and the target. The textbook variant, increasingly hard to land against modern OSes.

### 2. Per-destination IPID idle scan

Linux (since 2014) uses a *per-destination-pair* IPID counter rather than a global one. Classic idle scan does not work directly, but a refined variant uses the *zombie-to-target* pair's IPID as the oracle by ensuring the zombie's first interaction with the target is the probe-induced reply. Brittle but documented in academic literature.

### 3. TCP shared-state side channels

Beyond IPID, certain TCP fields (ISN under weak RNGs, challenge ACK counters, packet-count-based rate-limit state) can leak target state to a third-party observer. **Ensafi et al. (USENIX 2015)** demonstrated detecting intentional packet drops on the internet using these primitives — censorship detection from outside the censored network entirely.

### 4. NAT-mapping inference via IPID

A NAT gateway that translates many internal hosts to one external IP frequently shares a single IPID counter across them. Probing the external IPID and watching the rate of advance reveals approximately how many internal hosts are active — an unintended census attack against the perimeter. Defeated by NAT implementations that randomize IPID per outbound flow.

## Impact

Ordered by typical real-world severity:

- **Source-attribution evasion that survives forensic review.** The target's packet captures and logs contain only the zombie. Investigations chase the zombie owner first; the real attacker is invisible unless the zombie itself is captured and its own logs analyzed.
- **Trust-relationship inference.** If the zombie is *trusted* by the target (firewall ACL allows ZOMBIE → TARGET:N but blocks the internet at large), idle scan reveals exposure that no direct scan from the internet would surface. Diagnostic of legacy "allow from this management host" ACLs.
- **NAT-population estimation.** Census-style intelligence about an organization's internal scale, leaked through perimeter IPID counters. Useful for sizing follow-up engagements.
- **False-confidence in defender visibility.** Defenders who say "we monitor every connection" are correct about the target; they miss idle scans entirely if their telemetry is target-side only.
- **Limited operational use today.** Most production OSes randomize IPID. The technique is *educational* and *legacy-target-specific* rather than a standard operator move in 2026.

## Detection and defense

Ordered by effectiveness:

1.
**Use a kernel that randomizes IPID per destination or per packet.**
   Linux 4.1+, modern macOS, FreeBSD, OpenBSD, Windows 10/Server 2016+ all do this by default. The structural fix that ends classic idle scan as a useful attack against modern OSes. Audit any host advertising as a router, gateway, printer, IoT device, or out-of-band management interface — these are the lingering incremental-IPID candidates.

2.
**Egress filtering and source-address verification (BCP 38).**
   Idle scan requires the attacker to spoof the zombie's source IP. Networks that enforce ingress filtering (the *attacker's* upstream drops packets whose source IP is not in the attacker's address space) make the spoof impossible. RFC 2827 / BCP 38 was specified in 2000 and is still inconsistently deployed.

3.
**Behavioral detection at the zombie side.**
   The zombie sees three anomalies: (a) unsolicited SYN-ACKs from the attacker, (b) unsolicited RST or SYN-ACK responses from the target, (c) its own IPID advancing without matching outbound application traffic. Any single anomaly is weak; the combination is high-confidence. Defenders should monitor their own infrastructure for being recruited as zombies.

4.
**Per-destination IPID for any custom network stack.**
   IoT device manufacturers, embedded systems, and custom network stacks frequently inherit the same incremental-IPID bug because the developers do not know it is an attack surface. Secure-by-default guidance for new TCP/IP implementations should include IPID randomization.

5.
**Network-level flow monitoring at the perimeter.**
   Detection on the perimeter (the target's edge router) catches a different signature: the spoofed SYN arrives from a source that does not normally communicate with the target on that port. NetFlow / IPFIX correlation with known communication baselines catches the anomaly even though target host logs miss it.

### What does not work as a primary defense

- **Target-host logging alone.** Idle scan was designed to defeat this. The target sees a clean session that came from a trusted source IP (the zombie).
- **Firewall rules that block "scan-like" patterns.** Idle scan is one SYN per port, spread across whatever pace the attacker chooses. No volumetric signature on the target side.
- **TLS / encryption.** Idle scan operates at L3/L4. TLS is irrelevant.
- **Geo-blocking the zombie's country.** If the zombie is in-network or near-network, geo-blocking either blocks legitimate traffic or fails to apply.

## Practical labs

Run **only** against owned lab environments or authorized engagements. Idle scan against arbitrary internet hosts uses third-party IP addresses without their consent — operationally and legally hazardous outside authorized scope.

```
# Lab 1 — Find a candidate zombie in a lab subnet.
sudo nmap -O 10.0.0.0/24 2>/dev/null |
    awk '/Nmap scan report/{ip=$NF} /IP ID Sequence Generation: Incremental/{print ip}'
# Output: every host with incremental IPID is a candidate zombie.
```

```
# Lab 2 — Verify a specific zombie's IPID behavior in detail.
sudo nmap -O ZOMBIE | grep -A1 "IP ID Sequence"
# Expected: "IP ID Sequence Generation: Incremental"
# If you see "Random" or "Randomized", this zombie cannot be used.
```

```
# Lab 3 — Run an idle scan against an authorized lab target.
sudo nmap -Pn -sI ZOMBIE:80 -p 21,22,80,443,3389,8080 TARGET
# The target's packet capture will show ZOMBIE as the source.
# Verify by running tcpdump on TARGET during the scan.
```

```
# Lab 4 — Confirm the source-attribution property from TARGET's perspective.
# On TARGET:
sudo tcpdump -i any -nn "host ATTACKER_REAL_IP or host ZOMBIE" -c 50
# Expected: zero packets to/from ATTACKER_REAL_IP, many packets to/from ZOMBIE.
```

```
# Lab 5 — Defender lab: detect being used as a zombie.
# On the ZOMBIE host:
sudo tcpdump -i any -nn 'tcp and ((tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack != 0) or (tcp[tcpflags] & tcp-rst != 0))' -c 200
# Look for: SYN-ACK or RST packets arriving from the TARGET that do not correspond
# to any outbound connection your host initiated. That is the zombie-side signature.
```

```
# Lab 6 — IPID-based NAT-population inference (educational, against owned NAT).
# Probe the NAT external IP repeatedly and watch IPID advance.
for i in $(seq 1 20); do
  sudo hping3 -c1 -S -p 80 NAT_EXTERNAL_IP 2>/dev/null |
      grep -oP 'id=\K\d+'
  sleep 1
done
# If IPID advances by more than ~1 between samples, the NAT is sharing the counter
# across multiple internal hosts — the rate of advance approximates the active host count.
```

## Practical examples

- **Engagement against legacy industrial network.** Target perimeter has strict ACLs but trusts a 2010-era network printer in the same subnet. Idle scan with the printer as zombie reveals ports the direct internet scan reports as `filtered`. The printer's incremental IPID makes it the only viable path for source-attribution-evading reconnaissance.
- **Forensic exercise after a perimeter scan.** Defender team sees scan traffic apparently from `printer-3F-001`. Investigation reveals the printer's IPID advanced inconsistently with its outbound traffic during the scan window — confirming idle scan and pointing to the real attacker via NetFlow at the printer's egress.
- **Modern Linux target — idle scan fails.** Same engagement, but the target is a Linux 5.x host. The per-destination IPID generator means the classic technique does not work; operator falls back to ordinary `-sS` and accepts the attribution cost.
- **NAT census during pre-engagement recon.** Probing an organization's perimeter IP reveals the IPID counter advancing at roughly 50 units per minute, suggesting ~30-50 active internal hosts at the time of measurement. Sized the follow-up internal engagement accordingly.
- **Honey-zombie defender win.** Defender deploys an obviously-attractive host (named `mgmt-jump-01`) with incremental IPID and monitors it for unsolicited SYN-ACKs from the internet. Six months later, an external scan attempt against the corporate IP space generates the expected pattern — caught the operator mid-recon.

## Related notes

- [[nmap-timing-and-evasion]] — broader timing/evasion primitives; idle scan is the deepest case of the attribution-evasion question.
- [[packet-fragmentation-and-decoy-scans]] — sibling evasion family; decoys obscure attribution by noise, idle scan eliminates it by mechanism.
- [[tcp-ip-basics|TCP/IP basics]] — the IP identifier field this attack uses.
- [[nmap-scanning|Nmap Scanning]] — broader scan strategy this fits inside.
- [[packet-analysis|Packet Analysis]] — the right tool to verify the zombie/target packet flow during a lab.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — idle scan is a clean example of an attack whose defenses are protocol-spec changes, not perimeter rules.
- [[network-telemetry-sources-and-visibility|Network telemetry sources and visibility]] — explains why target-side telemetry alone misses this.

### Suggested future atomic notes

- ipid-randomization-policies-by-os — comparative table of Linux / macOS / Windows / OpenBSD / BSD-derivative / IoT-stack IPID behavior.
- tcp-ip-side-channels-beyond-ipid — ISN inference, challenge-ACK counters, packet-count rate limits.
- nat-population-inference-attacks — the census variant; defense via per-flow IPID randomization at the NAT.
- bcp38-egress-filtering-and-spoofing-defense — the structural anti-spoofing defense at the attacker's upstream.
- detect-idle-scan-at-zombie-side — defender-side playbook pair for catching being used as a zombie.

## References

- **Official Tool Docs:** Nmap Reference Guide — Idle Scan — https://nmap.org/book/idlescan.html
- **Research / Deep Dive:** Antirez (Salvatore Sanfilippo) — Dumb scan / new TCP scan method (original 1998 disclosure on Bugtraq) — https://seclists.org/bugtraq/1998/Dec/79
- **Research / Deep Dive:** Ensafi et al. — Detecting Intentional Packet Drops on the Internet via TCP/IP Side Channels (USENIX Security 2015) — https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/ensafi
