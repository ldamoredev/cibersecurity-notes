---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Masscan Internet-Scale Scanning

## Definition

Masscan is an asynchronous, stateless TCP/IP port scanner with its own user-space network stack, designed to enumerate open ports across very large address spaces (entire BGP AS prefixes, /8 blocks, or the full IPv4 internet) at packet rates that the kernel TCP stack cannot sustain.

## Why it matters

The Nmap mental model — connection state per target, retries, version probing — breaks down past ~/16 of address space because per-connection state dominates RAM and CPU. Masscan answers a different question: "given a huge address list and a fixed port set, where are the doors?". It is the right tool when the question is breadth, and the wrong tool when the question is depth.

The senior framing is the two-phase pipeline: **Masscan finds the doors, Nmap (or service-specific tools) walks through them.** Treating Masscan as a "fast Nmap" produces both wrong results and operational accidents — the safety story (rate, exclude lists, source IP) is entirely different from Nmap's.

## How it works

Masscan's architecture is **4 design choices**:

1. **Stateless asynchronous TX/RX.** Two threads. The TX thread emits SYNs as fast as `--rate` allows. The RX thread listens for SYN-ACKs and logs them. There is no per-target state; both threads see the wire only.
2. **User-space TCP/IP stack.** Masscan emits raw Ethernet frames and reads raw responses, bypassing the kernel. This is what lets it scale; it is also why `--adapter-ip` must be set on multi-homed or non-default-route hosts.
3. **Randomized address-space walk.** Default randomization spreads probes across the target range so no single intermediate router or rate limiter sees a sequential burst.
4. **Rate as the only knob.** `--rate` directly controls the link load. There is no Nmap-style timing template — packets-per-second is the contract.

Example:

```
# A scoped, polite, full-port scan of one /24.
sudo masscan 10.0.0.0/24 -p0-65535 \
    --rate 1000 \
    --excludefile /etc/masscan/exclude.conf \
    -oJ scan.json
```

Interpretation:
- `--rate 1000` = 1000 packets per second. Single-link safe.
- `--excludefile` is honored *before* the include list. Non-overridable. This is the safety property that makes Masscan operationally responsible.
- `-oJ` line-delimited JSON streams to disk — survives Ctrl-C with `paused.conf`.

The bug Masscan exploits is not in the target; it is the *unused capacity* in normal Nmap workflows. The output is identical in semantics to Nmap's `open`/`closed` for the same probe type, just produced 100–10000× faster.

## Techniques / patterns

- **`--excludefile` discipline before anything else.** Build the exclude list (IRR data, government allocations, RFC 5737 documentation ranges, sensitive partners, your own monitoring infra) and `--echo` the merged config to inspect before scanning.
- **Start at `--rate 1000`** on shared links. Measure RTT and ICMP-type-3 (destination unreachable) rate from your upstream. Ramp only after the path is verified.
- **`--shard X/Y`** to split work across Y scan boxes by partitioning the address space deterministically. The operational pattern for any AS-wide scan from a fleet.
- **Always output binary (`-oB`)** for jobs over ~/16. `--readscan` re-parses the binary into JSON/XML/grepable later. Text formats lose packet metadata you may want.
- **Two-phase pipeline.** Masscan produces `host:port` tuples → feed those into Nmap with `-iL` and `-p` for version detection, NSE, OS detection. Never run masscan with `--banners` as a substitute.
- **Use `--source-ip` and `--source-port`** to pin your scan footprint for audit logs (firewall, IDS, NetFlow). Anonymity is not the goal — *reviewability* is.
- **Run with `--ping` enabled** if the goal is host discovery first; otherwise masscan probes every IP in the range regardless of liveness.

## Variants and bypasses

### 1. Bounded enumeration

`masscan 10.0.0.0/8 -p443 --rate 5000`. One port, large space. Standard external attack surface refresh against an organization's owned AS.

### 2. AS-targeted scan

Pre-resolve an AS to its prefixes with `whois -h whois.radb.net -- "-i origin AS123"` and feed the list as `-iL`. The right way to map an organization's public-IP footprint.

### 3. Port-set discovery

`masscan 192.0.2.0/24 -p21,22,23,80,443,3389,5900,8080,8443 --rate 1000`. Common-port sweep across a subnet — fast precursor to focused Nmap.

### 4. Banner snapshot mode

`--banners --rate 100` opens full TCP sessions on found ports and captures the first server packet. Useful for distinguishing SSH versions or HTTP vs. HTTPS without invoking Nmap. *Reduces effective rate by ~10× — not free.*

### 5. UDP scanning

`-pU:53,123,161,1900 --rate 1000`. Smaller probe library than Nmap's, but adequate for the well-known UDP services. Beware: UDP false negatives are easy because responses are protocol-specific.

### 6. Resume after pause

`masscan --resume paused.conf`. Auto-written on Ctrl-C or kill. The right way to run multi-day scans through scheduled maintenance windows.

## Impact

- **Breadth.** Single-host scans of /8 in minutes; full IPv4 in roughly an hour on dedicated hardware at 10M+ pps.
- **Operational fragility.** Misconfigured `--rate` on a shared link is a denial-of-service against everyone on that link. Always start small.
- **Detection.** Masscan is highly detectable — random-source-port floods to many destinations from one IP are textbook scan signatures. Masscan does not pretend to be stealthy.
- **Source attribution.** Trivial. `--adapter-ip` is always logged. Source IP rotation requires running multiple boxes with `--shard`.
- **Path saturation.** Even at safe `--rate`, intermediate routers near your scan box may CPU-bottleneck on the small-packet flood — visible as high jitter on monitoring before the link saturates.

## Detection and defense

1.
**Per-source SYN-rate alerting at the perimeter.**
   Masscan's signature is N distinct destinations per source IP per minute. A threshold rule on this catches Masscan in under a second of scan time.

2.
**`--excludefile`-equivalent allowlisting on the defender side.**
   Targets that should never see scan traffic (out-of-band management, ICS/SCADA, partner integrations) belong on a tarpit/drop list so scanner mistakes do not become operational accidents on either side.

3.
**TCP fingerprinting.**
   Masscan's user-space stack emits a recognizable TCP fingerprint (specific window size, MSS, no SACK by default). p0f-class tools identify Masscan traffic regardless of source IP.

4.
**NetFlow/IPFIX anomaly correlation.**
   Masscan creates a fan-out pattern (one source, many destinations) visible in flow records far below SIEM packet-level visibility. The flow analytics layer often catches Masscan before the IDS does.

### What does not work as a primary defense

- **Blocking individual scan source IPs after the fact** — Masscan finishes its job in seconds; the block is post-mortem.
- **Rate-limiting outbound traffic from the scanner's network** — the scanner controls the scanner. The defender's rate limit is on the *target* side.
- **Trusting `--banners` output as service inventory** — banner is one packet, often misleading on TLS, HTTP/2, or load-balanced services.

## Practical labs

```
# Lab 1 — safe scan of an owned /24 with explicit exclusion.
cat > exclude.conf <<EOF
10.0.0.1
10.0.0.254
EOF
sudo masscan 10.0.0.0/24 -p22,80,443 --rate 200 --excludefile exclude.conf -oJ lab.json
jq '.[].ports[] | "\(.port)/\(.proto)"' lab.json | sort -u
# What ports appear is the door list; feed those into Nmap next.
```

```
# Lab 2 — two-phase Masscan -> Nmap pipeline.
sudo masscan 10.0.0.0/24 -p1-65535 --rate 1000 -oG lab.gnmap
awk '/Host:/ {print $2}' lab.gnmap | sort -u > hosts.txt
awk '/Ports:/ {for(i=1;i<=NF;i++) if($i~/\/open\//) print $i}' lab.gnmap |
  cut -d/ -f1 | sort -un | paste -sd, - > ports.txt
nmap -Pn -sV -iL hosts.txt -p "$(cat ports.txt)" -oA lab.nmap
# Masscan finds doors, Nmap walks through them. This is the standard pipeline.
```

```
# Lab 3 — rate calibration on a lab link.
for R in 100 500 1000 5000 10000; do
  echo "===== rate=$R"
  sudo masscan 10.0.0.0/24 -p80 --rate $R -oG /dev/null 2>&1 | tail -3
done
# Watch ICMP destination-unreachable / packet loss as rate rises.
# The right --rate is the highest with no loss on the path, halved.
```

```
# Lab 4 — banner mode vs port-only.
sudo masscan 10.0.0.0/24 -p22,80 --rate 500 -oJ noban.json
sudo masscan 10.0.0.0/24 -p22,80 --rate 500 --banners -oJ ban.json
diff <(jq -c '.[].ports[].port' noban.json | sort) <(jq -c '.[].ports[].port' ban.json | sort)
# Banner mode adds a "service.banner" field per port. Compare effective throughput.
```

```
# Lab 5 — exclude-file safety regression test.
sudo masscan 10.0.0.0/24 -p80 --rate 500 --excludefile <(echo 10.0.0.5) --echo | grep -E 'exclude|include'
# Verify the merged config excludes 10.0.0.5 even though it is inside the include range.
# Always --echo before scanning anything you care about.
```

## Practical examples

- **Bug bounty external attack surface refresh.** Weekly Masscan over an organization's full AS at `--rate 1000`, output binary, diff against last week's binary with `--readscan`. New ports surface immediately for Nmap follow-up.
- **Internal recon during red-team.** From a foothold inside a /16, Masscan at `--rate 200` finds reachable internal services in minutes that would take Nmap an hour.
- **Targeted port-sweep across acquired ASes.** Post-acquisition exposure mapping uses Masscan per AS with `--shard X/Y` across cloud scan boxes for parallelism.
- **IoT/ICS air-gap audit.** Masscan-UDP over the management VLAN exposes forgotten SNMP/IPMI services that Nmap-UDP is too slow to find at scale.
- **Cloud egress sanity check.** Run Masscan *from* a cloud workload outward to a controlled receiver to verify egress filtering and source-IP NAT actually behave as the security group claims.

## Related notes

- [[nmap-scanning|Nmap Scanning]]
- [[ports-and-services|Ports and Services]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[service-enumeration|Service Enumeration]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[active-recon|Active Recon]]
- [[scope-validation|Scope Validation]]
- [[external-attack-surface|External Attack Surface]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]]
- [[nmap-timing-and-evasion]]
- [[rustscan-and-nse-pipeline]]
- [[packet-fragmentation-and-decoy-scans]]

### Suggested future atomic notes

- zmap-vs-masscan
- as-prefix-resolution-for-scanning
- scan-pipeline-orchestration
- scan-fingerprinting-defense

## References

- **Official Tool Docs:** Masscan README and man page — https://github.com/robertdavidgraham/masscan
- **Research / Deep Dive:** Erratasec — Masscan: the entire internet in 3 minutes (design rationale) — https://blog.erratasec.com/2013/09/masscan-entire-internet-in-3-minutes.html
- **Research / Deep Dive:** Durumeric et al. — ZMap: Fast Internet-wide Scanning and Its Security Applications (USENIX Security 2013), the academic foundation for stateless internet-scale scanning — https://zmap.io/paper.pdf
