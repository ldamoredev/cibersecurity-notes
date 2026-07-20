---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Run External Recon Scan Pipeline

## Goal

Map the open ports, services, and version exposure of an authorized target (single host, subnet, or BGP AS) using a two-phase Masscan → RustScan/Nmap-NSE pipeline, with reproducible timing, an enforced exclude-list, and structured output that diffs cleanly across runs.

## Assumptions

- a written authorization (engagement scope, bug-bounty policy, or owned-asset list) exists and covers every IP/CIDR that will appear in the include list
- the scan box has a stable source IP and a clean upstream link (no shared NAT with sensitive workloads)
- the goal is breadth-then-depth recon, not exploitation; vulnerability validation happens in follow-up playbooks
- Nmap, Masscan, RustScan, `jq`, and `whois` are installed and current

## Prerequisites

- `INCLUDE.txt` — authorized targets (one CIDR/IP/host per line)
- `EXCLUDE.txt` — out-of-scope IPs, partner integrations, monitoring infra, RFC 5737 ranges if relevant
- `--adapter-ip` value matching the scan box's actual routable source IP
- `nmap --script-updatedb` run within the last 30 days
- shell `ulimit -n 65535` available (or use the RustScan Docker image)

## Recon steps

> *Runnable reference script:* `cybersecurity/security-playbooks/run-scan-pipeline.sh` packages Phases 1–2 below into one shell script. Use it with `INCLUDE_FILE`, `EXCLUDE_FILE`, and `ADAPTER_IP` env vars; the script refuses to run if `EXCLUDE_FILE` is empty and prompts for an explicit `YES` before scanning unless `--yes` is passed. Phase 0 (authorization gate) and Phase 3 (diagnostic packet-shape matrix) are kept as human-in-the-loop steps and are not automated.

> *Defender pair:* [[detect-external-scan-pipeline]] is the note-by-note defender-side mirror of this playbook — read both together per [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]].

### Phase 0 — Authorization gate

1. Print the scope and exclude list verbatim and confirm against the engagement document.
2. `cat INCLUDE.txt EXCLUDE.txt` — visually verify before any packets go out.
3. If targets are AS-level, expand the AS to prefixes first:
   `bash
   whois -h whois.radb.net -- "-i origin AS<NUMBER>" |
     awk '/^route:/ {print $2}' | sort -u > INCLUDE.txt`

### Phase 1 — Breadth (Masscan)

1. Echo-validate the Masscan config before scanning:
   `bash
   sudo masscan --excludefile EXCLUDE.txt -iL INCLUDE.txt \
        -p1-65535 --rate 1000 --adapter-ip <YOUR_IP> --echo > masscan.conf
   less masscan.conf   # eyeball the merged include/exclude`

2. Calibrate `--rate` on a tiny slice first (`-p80` on one /24) and watch for ICMP-unreachable / loss spikes. Set the real rate to ~½ of the highest clean rate.
3. Run the scan with binary output for lossless re-parsing:
   `bash
   sudo masscan -c masscan.conf -oB scan.bin`

4. Convert to JSON for downstream tooling:
   `bash
   sudo masscan --readscan scan.bin -oJ scan.json
   jq -r '.[] | "\(.ip):\(.ports[0].port)"' scan.json | sort -u > openports.txt`

5. If interrupted, resume with `sudo masscan --resume paused.conf` — never restart from zero.

### Phase 2 — Depth (RustScan → Nmap NSE)

1. Group Masscan output by host so Nmap runs once per host with that host's port list:
   `bash
   awk -F: '{ports[$1]=ports[$1]","$2} END {for (h in ports) print h, substr(ports[h],2)}' openports.txt > hostports.txt`

2. Run Nmap with version detection and a conservative NSE category Boolean:
   `bash
   while read host ports; do
     sudo nmap -Pn -sS -sV -sC \
          --script "(default or vuln) and not (intrusive or dos or brute)" \
          --min-rate 100 --max-rate 300 --max-retries 3 \
          -p "$ports" -oA "nmap/$host" "$host"
   done < hostports.txt`

3. For single-host deep scans where Masscan-scale isn't needed, substitute RustScan as the discovery layer:
   `bash
   rustscan -a <HOST> --ulimit 5000 -- -sV -sC \
       --script "(default or safe or vuln) and not (intrusive or dos or brute)" \
       --min-rate 100`

4. If a target appears rate-limited (high `filtered` count at high rate, lower at low rate), pin `--min-rate 50 --max-rate 100` and re-run only that host.

### Phase 3 — Diagnostic packet-shape matrix (optional)

Run only when Phase 2 reports everything as `filtered` despite expected exposure. Pick one suspected-open port and probe with each evasion primitive separately to fingerprint the inspection layer:

```
PORT=443; HOST=<TARGET>
for FLAG in "" "-f" "--mtu 24" "--data-length 200" "--badsum" "--source-port 53"; do
  echo "===== $FLAG"
  sudo nmap -Pn -sS -p $PORT $FLAG "$HOST"
done
```

Whichever invocation returns `open` reveals what the middlebox does and does not inspect — that intel guides the next phase.

## Exploit / test steps

This playbook intentionally stops at enumeration. Validated findings route to:
- exploitation playbooks per service class (`exploit-sqli`, `break-jwt-validation`, `inspect-file-upload-surface`, etc.)
- `cybersecurity/offensive-security/service-validation` for manual service inspection
- `cybersecurity/offensive-security/recon-to-testing-handoff` for engagement handoff

## Validation clues

- `open` ports appear identically across Masscan and Nmap runs (Masscan ground-truth on discovery, Nmap on protocol)
- Version banners are consistent across NSE scripts (`-sV`, `http-server-header`, `ssl-cert`) — divergence indicates a load balancer with mixed backends
- `filtered` counts drop when `--min-rate` drops — confirms rate limiting, not firewall block
- A `--badsum` probe returning `RST/ACK` confirms an inline IDS not validating checksums (real OSes drop)
- Diff against the previous run shows new ports/services — the actual engagement output

## Mitigation

On the defender side, the right controls for the pipeline being run against you:
- per-source-IP SYN-rate alerting at the perimeter (defeats Masscan in seconds)
- IDS rules tied to fan-out behavior (one source → many destinations) and TCP fingerprint (defeats decoys)
- IP fragment reassembly enabled at the IDS (defeats `-f`/`--mtu`)
- honeyports/tarpits on never-used ports (asymmetric high-confidence detection)
- version-banner shaping (raises NSE `vuln` false-positive rate, lowers attacker signal)

## Logging / detection

- one source IP hitting > N distinct destination IPs on a single port within 60 s — Masscan signature
- one source IP probing > 100 distinct ports on one host within 60 s — RustScan/Nmap signature
- NSE-specific probe patterns in IDS rule packs (Snort/Suricata community sets)
- per-source TCP-fingerprint stability across "different" source IPs — decoy detection
- EDR process-network joins that tie scanner behavior to `nmap`, `masscan`, `rustscan`, `python`, `powershell`, or renamed binaries

## Operational safety

- **never** use real third-party IPs as `-D` decoys; prefer RFC 5737 ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`)
- **never** scan above `--rate 1000` on a shared upstream link without measuring loss first
- **never** run NSE `intrusive`, `exploit`, `dos`, or `brute` categories without explicit written authorization
- **always** keep `EXCLUDE.txt` non-overridable — Masscan honors it before `INCLUDE.txt`, which is the safety property
- **always** write binary output for any scan that takes more than five minutes — Ctrl-C survival matters

## Related notes

- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[nmap-scanning|Nmap Scanning]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[service-validation|Service Validation]]
- [[scope-validation|Scope Validation]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]
- [[external-attack-surface|External Attack Surface]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]
- [[detection-evasion-myths-and-modern-limitations|Detection Evasion Myths and Modern Limitations]]
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation and Kill Chain Observability]]

## References

- **Official Tool Docs:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README — https://github.com/robertdavidgraham/masscan
- **Official Tool Docs:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — Host and Port Discovery — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
