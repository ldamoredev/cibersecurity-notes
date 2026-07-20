---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# EDR Network Observability and Process Correlation

## Definition

EDR network observability is the endpoint-side capture of network-related activity, especially the ability to correlate sockets, connections, destinations, DNS-like activity, and alerts to process lineage, command lines, users, hashes, sessions, and host identity.

## Why it matters

The major shift in modern defense is not just better packet inspection. It is correlation. A network alert used to say "source IP 10.0.4.20 contacted 10.0.9.14:445." EDR can often say "PowerShell launched a renamed scanner, under this user, from this parent process, then opened these sockets to these hosts."

That changes offensive and defensive tradeoffs. Fragmentation, decoys, source-port tricks, and slow timing can still affect some network sensors, but they do not erase process creation, command-line history, file hashes, parent chains, identity, cloud workload metadata, or host-local socket events.

## How it works

Endpoint-network correlation follows a **5-part join model**:

1. **Process creation.** EDR records executable path, command line, hash, signer, user, token elevation, parent process, and start time.
2. **Network event.** EDR records outbound or inbound connection activity: remote IP/port, local IP/port, protocol, action, and sometimes DNS or URL context.
3. **Ownership join.** The network event is linked to the process or initiating process that caused it.
4. **Lineage join.** Parent, grandparent, user session, logon ID, and host identity place the behavior in context.
5. **Environment join.** Network, cloud, identity, vulnerability, and asset-role context determine whether the behavior is expected.

Example:

```
Network sensor:
  10.0.4.22 scanned 10.0.9.0/24:445.

EDR join:
  powershell.exe -> rundll32.exe -> c:\programdata\svchost.exe
  command line included encoded script
  same process opened 254 SMB connections in 3 minutes
  host role: finance workstation
```

The detection pivots from "an IP scanned" to "a suspicious process chain performed internal discovery."

## Techniques / patterns

- **Process-to-network joins.** Link network destinations to executable, command line, parent process, user, and host role.
- **Rare process network behavior.** Alert when a process that does not normally make network connections contacts many hosts, rare ports, or new external destinations.
- **Scanner ancestry detection.** Identify `nmap`, `masscan`, `rustscan`, `zmap`, `curl`, `python`, `powershell`, or renamed binaries by path, hash, command-line shape, and socket behavior.
- **Living-off-the-land network behavior.** Detect unusual network fan-out from `powershell`, `wscript`, `mshta`, `rundll32`, `wmic`, `certutil`, shells, package managers, and admin tools.
- **Endpoint and network alert correlation.** Elevate when a host has both network IDS alerts and suspicious process/file/logon events in the same window.
- **Cloud workload process context.** In EDR-covered cloud workloads, join flow logs or network alerts to container/VM process telemetry and cloud identity.

## Variants and bypasses

Endpoint-network correlation has **7 detection-relevant patterns**.

### 1. Known scanner process

The easiest case: `nmap`, `masscan`, `rustscan`, or `zmap` launches and creates matching network behavior. This should be benign only on approved scanner assets.

### 2. Renamed scanner binary

The filename changes, but hash, signer, command-line flags, parent, socket pattern, and port fan-out can still reveal the behavior.

### 3. Scripted socket scanner

Python, PowerShell, Go, Bash, or Node opens many sockets. Network telemetry sees scans; EDR supplies the interpreter, script path, command line, and parent.

### 4. Living-off-the-land discovery

Built-in tools enumerate SMB, LDAP, WinRM, HTTP, Kubernetes API, or cloud metadata. The process name looks normal; the target distribution and role mismatch make it suspicious.

### 5. Browser or proxy-mediated activity

Endpoint sees the browser or proxy process, while network sensors see the destination. Attribution to a user action versus malicious automation may need command-line, extension, URL, and timing context.

### 6. Container and ephemeral workload scanning

The process may live inside a container, short-lived pod, serverless runtime, or CI job. Host EDR, container runtime telemetry, cloud flow logs, and orchestrator audit logs must be joined.

### 7. EDR-blind network behavior

Appliances, unmanaged systems, network devices, IoT, BYOD, or tampered hosts may be visible only to network telemetry.

## Impact

- **Attribution improves.** Process, user, parent, hash, and host role provide evidence source IP cannot.
- **Old evasion weakens.** Packet-level tricks do not erase endpoint process evidence.
- **Triage accelerates.** Analysts can scope from process to connections, files, logons, and related alerts.
- **Detection expands inward.** Host-local, cloud, VPN, container, and split-tunnel traffic may be visible where perimeter sensors are blind.
- **Coverage becomes uneven.** EDR visibility depends on deployment, platform support, tamper resistance, retention, and schema fidelity.

## Detection and defense

Ordered by effectiveness:

1.
**Join network behavior to process lineage whenever possible.**
   A network alert without process context is a lead; a network alert with process, user, parent, and command line is an investigation.

2.
**Baseline network behavior by process and host role.**
   `nginx` contacting upstream services differs from `excel.exe` contacting hundreds of internal hosts. Role-aware baselines reduce both missed attacks and noise.

3.
**Prioritize abnormal parent-child-process plus network behavior.**
   Suspicious parents launching network-active children often matter more than the destination alone.

4.
**Correlate EDR with Zeek, Suricata, NetFlow, DNS, proxy, and cloud logs.**
   Each layer can contradict or confirm the others. Endpoint visibility is strongest when it does not stand alone.

5.
**Track sensor coverage and tamper signals.**
   Missing EDR on a critical host, disabled network sensors, stale agents, and telemetry gaps should be treated as risk findings.

### What does not work as a primary defense

- **Endpoint-only visibility.** EDR misses unmanaged assets, appliances, network devices, and sometimes packet-level truth.
- **Network-only visibility.** Network sensors often cannot identify process, user, parent, or script source.
- **Filename-based scanner detection.** Renaming binaries and wrapping tools in scripts is trivial.
- **Source-IP attribution.** NAT, proxies, decoys, VPNs, cloud egress, and compromised hosts make IP attribution weak without endpoint or identity context.
- **Assuming EDR sees all sockets.** Loopback, kernel drivers, containers, short-lived processes, tampering, and platform limitations can create gaps.

### Operational misconceptions

- **"If EDR is installed, the host is visible."** Agent health, policy, OS support, exclusions, tamper events, and ingestion delay determine actual visibility.
- **"Process lineage is always truthful."** Process injection, parent spoofing, hollowing, and telemetry truncation can weaken lineage.
- **"Network detections are obsolete."** Endpoint telemetry complements but does not replace packet, flow, and protocol evidence.
- **"The parent process proves intent."** Parentage is evidence, not motive. Admin tooling and automation can look suspicious without malicious intent.

### Modern limitations

- Containers, ephemeral workloads, serverless functions, and managed PaaS reduce traditional host EDR coverage.
- Privacy controls and OS sandboxing can limit command-line or network-detail collection.
- Attackers may use signed binaries, injected processes, legitimate remote-management tools, and cloud APIs to blend into normal operations.
- Vendor schemas evolve, and detections tied to field names require maintenance.

### Telemetry blind spots

- Unmanaged endpoints, appliances, IoT, network gear, printers, storage devices, and BYOD.
- EDR exclusions for performance-sensitive directories or processes.
- Short-lived processes that create network connections before full enrichment arrives.
- Split-tunnel VPN, host-local proxying, container bridges, service mesh sidecars, and loopback.
- PID reuse when detections do not use unique process IDs and timestamps.

## Practical labs

Use a lab endpoint with your own EDR, Sysmon, osquery, Elastic Defend, Defender for Endpoint, or equivalent telemetry.

### Correlate a scanner process to network fan-out

```
nmap -Pn -p 22,80,443 LAB_SUBNET/28
```

Expected telemetry: EDR should record process creation for `nmap` and network events to multiple hosts/ports. Network sensors should show scan fan-out. The detection occurs at the join.

### Rename a scanner and test behavior-based detection

```
cp "$(command -v nmap)" /tmp/update-helper
/tmp/update-helper -Pn -p 80,443 LAB_SUBNET/28
```

Expected telemetry: filename-only rules may fail; hash, signer, command-line flags, parent, and network fan-out should still reveal scanner behavior.

### Generate scripted socket scanning

```
python3 - <<'PY'
import socket
for host in [f"10.10.10.{i}" for i in range(10, 30)]:
    for port in [22, 80, 443]:
        s = socket.socket()
        s.settimeout(0.2)
        try:
            s.connect((host, port))
        except Exception:
            pass
        s.close()
PY
```

Expected telemetry: EDR sees `python3` as the process; flow/Zeek sees the fan-out. The false assumption: only named scanners matter.

### Join PowerShell network behavior to parent process

```
1..20 | ForEach-Object {
  Test-NetConnection -ComputerName "10.10.10.$_" -Port 445 -InformationLevel Quiet
}
```

Expected telemetry: process command line, parent shell, user, and outbound connection attempts should align. Defenders should distinguish admin scripts from abnormal host-role behavior.

### Compare endpoint and network blind spots

```
# On a lab host, compare endpoint event count with Zeek conn.log count
nmap -Pn -p 1-100 LAB_HOST
zeek-cut id.orig_h id.resp_h id.resp_p conn_state < conn.log | wc -l
```

Expected telemetry: counts may differ because EDR records attempted sockets, Zeek records observed packets, and each has timing/visibility limits.

## Practical examples

- A perimeter IDS alert on HTTP exploit probing becomes high confidence when EDR shows `python.exe` launched from a suspicious archive and contacted the same host.
- A slow internal scan from a workstation is detected because `powershell.exe` made first-ever connections to many SMB ports.
- A Masscan burst from a cloud VM is triaged quickly because cloud asset tags show it is an approved scanner instance.
- A decoy scan confuses target logs, but EDR on the real scanner host records the actual process and command line.
- A network appliance scans unexpectedly; EDR is absent, so defenders rely on NetFlow, Zeek, asset inventory, and change records.

## Related notes

- [[index|Detection Engineering]]
- [[network-telemetry-sources-and-visibility]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[behavioral-detection-vs-signature-detection]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[attack-path-correlation-and-kill-chain-observability]]
- [[detection-evasion-myths-and-modern-limitations]]
- [[scan-anomaly-detection-and-fingerprint-analysis]]
- [[zeek-suricata-and-netflow-analysis]]
- [[active-recon|Active Recon]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[client-ip-trust|Client IP Trust]]

### Suggested future atomic notes

- process-lineage-for-detection
- edr-schema-field-quality
- container-runtime-network-telemetry
- endpoint-network-correlation-queries
- pid-reuse-and-process-identity

## References

- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Foundational:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Research / Deep Dive:** Elastic Endpoint Investigation Across the Environment - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment
