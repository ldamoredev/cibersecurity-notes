---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Network Telemetry Sources and Visibility

## Definition

Network telemetry is the evidence produced by observation points that see communication across a network: packets, flows, protocol transactions, device logs, cloud flow logs, proxy/WAF logs, DNS logs, TLS metadata, and sensor-health records.

## Why it matters

Modern cybersecurity is telemetry warfare. An attacker does not merely interact with a host; they create evidence across routers, switches, firewalls, proxies, DNS resolvers, TLS handshakes, endpoint sockets, cloud control planes, and identity systems. A defender who understands which layer saw which behavior can reconstruct intent even when payloads are encrypted or a single sensor missed the event.

The senior mistake is treating "network logs" as one thing. A SPAN packet capture, NetFlow record, Zeek `conn.log`, Suricata alert, cloud VPC flow log, WAF event, and EDR socket event all describe different projections of the same behavior.

## How it works

Network visibility is a **6-layer evidence stack**:

1. **Packet visibility.** TAPs, SPAN ports, host captures, and full-packet capture expose headers and sometimes payload. This is highest fidelity and highest cost.
2. **Flow visibility.** NetFlow/IPFIX/sFlow/cloud flow logs summarize who talked to whom, when, for how long, and how much.
3. **Protocol visibility.** Zeek, Suricata, proxies, DNS servers, and WAFs reconstruct application-layer transactions when they can parse the protocol.
4. **Control-plane visibility.** Firewall, load balancer, cloud security group, NAT gateway, route-table, and proxy logs expose policy decisions and path changes.
5. **Endpoint visibility.** EDR and host logs connect network activity to process, user, command line, parent, hash, and session.
6. **Correlation visibility.** SIEM/XDR/hunting platforms join events by host, user, IP, process, flow ID, time window, and asset context.

Example interpretation:

```
10.0.4.22 -> 10.0.9.14:445 over 2 minutes

Flow log: 900 short TCP attempts, mostly no bytes returned.
Zeek: many failed conn states, no SMB transactions.
Suricata: scan/fan-out alerts.
EDR: powershell.exe launched nmap.exe from a temp directory.
Cloud log: source host is a newly created workload in a dev subnet.
```

The detection does not live in one log. It lives in the relationship between timing, port behavior, process ancestry, host role, and network path.

## Techniques / patterns

- **Visibility mapping.** For each security question, write the required fields: source, destination, port, protocol, user, process, hostname, DNS name, SNI, JA3/JA4, bytes, packets, verdict, action, sensor health.
- **Observation-point reasoning.** Ask where the sensor sits relative to NAT, load balancers, TLS termination, proxies, routing changes, and cloud overlays.
- **Packet-to-flow-to-process pivoting.** Start broad with flow, deepen with Zeek/Suricata/pcap, then join to EDR where endpoint coverage exists.
- **Sensor-health checks.** Treat packet loss, dropped events, delayed ingestion, clock skew, and parser errors as first-class detection data.
- **Viewpoint comparison.** Compare public, VPN, internal, VPC, container, and endpoint-local telemetry because reachability is path-dependent.

## Variants and bypasses

Network visibility has **7 practical telemetry families**.

### 1. Full packet capture

Full packet capture gives the most replayable evidence, but it is expensive, privacy-sensitive, storage-heavy, and often impossible at cloud scale. TLS hides payload unless termination keys or decrypted proxy logs exist.

### 2. SPAN and TAP feeds

TAPs are preferred for high-fidelity fixed monitoring, while SPAN is common for flexible monitoring. SPAN can be oversubscribed, directional, modified by switch behavior, or misconfigured, so captures from SPAN are a view, not ground truth.

### 3. Flow records

NetFlow/IPFIX/cloud flow logs scale well and detect fan-out, beaconing, long-lived sessions, and volumetric patterns. They usually lack payload, process, hostname, URI, and exact TCP-flag sequences.

### 4. Protocol transaction logs

Zeek, proxies, DNS logs, and WAF logs expose parsed protocol meaning: DNS queries, HTTP methods, TLS metadata, files, certificates, user agents, and parser weirdness. They depend on visibility, parser support, and clean enough traffic.

### 5. IDS/IPS alert streams

Suricata/Snort-like engines convert packets and streams into rule matches. They are high value when tuned and contextualized, but an alert is a sensor claim, not a completed investigation.

### 6. Endpoint network telemetry

EDR sees process-owned network behavior from the host perspective. It can observe traffic that perimeter sensors miss, but it usually lacks packet detail and can be absent on appliances, unmanaged hosts, containers, and short-lived workloads.

### 7. Cloud-native telemetry

Cloud flow logs, load-balancer logs, DNS resolver logs, firewall logs, NAT gateway logs, and control-plane events expose paths that physical sensors cannot see. They are aggregated, provider-specific, and often delayed.

## Impact

- **Detection coverage.** Telemetry selection determines which attacks are detectable before any rule is written.
- **Triage quality.** Rich context shortens investigations; weak context creates IP-only or alert-only dead ends.
- **False negatives.** Missing sensors, sampled flow, SPAN loss, asymmetric routing, encrypted payloads, and unmanaged endpoints create blind spots.
- **False positives.** Telemetry without asset role, change windows, user context, and baselines makes normal operations look malicious.
- **Cost and retention pressure.** High-fidelity logs cost money. Detection programs must decide what to keep hot, warm, summarized, or discarded.

## Detection and defense

Ordered by effectiveness:

1.
**Engineer telemetry from questions, not tools.**
   Start with the behavior you need to prove or disprove, then list fields and observation points. This prevents "we bought a sensor" from becoming a fake visibility strategy.

2.
**Place sensors at trust-boundary transitions.**
   Monitor where traffic changes meaning: internet edge, VPN ingress, east-west choke points, identity boundaries, TLS termination, cloud NAT, service mesh, and privileged admin subnets.

3.
**Correlate across packet, flow, protocol, endpoint, and cloud.**
   Single-source detections fail under modern conditions. Correlation lets flow fan-out become a process-backed incident instead of an anonymous IP statistic.

4.
**Continuously validate sensor health.**
   Capture loss, queue drops, ingestion lag, parser failures, clock drift, and broken normalization should alert. A silent sensor is a detection outage.

5.
**Use retention tiers deliberately.**
   Keep high-value metadata longer than raw payloads. Store enough detail to reconstruct incidents: timestamps, 5-tuples, direction, action, asset, process, user, and parse status.

### What does not work as a primary defense

- **Buying a SIEM without telemetry design.** A SIEM only correlates what exists, arrives on time, and has usable fields.
- **Relying on packet capture alone.** Packets lack identity, process ancestry, cloud context, and long retention in many environments.
- **Relying on NetFlow alone.** Flow sees patterns but cannot usually explain protocol content, process cause, or exploit payload.
- **Assuming encryption means invisibility.** Payload is hidden, but timing, endpoints, DNS, TLS handshake metadata, flow size, and endpoint process context often remain.
- **Treating SPAN captures as perfect truth.** SPAN can drop, duplicate, modify, or omit traffic depending on direction and oversubscription.

### Operational misconceptions

- **"Slow scans are stealthy."** Slow scans reduce simple rate alerts but still create rare service contact, process-network joins, long-window fan-out, DNS/TLS metadata, and first-seen behavior.
- **"Cloud means no network monitoring."** Cloud changes the collection points: flow logs, load balancer logs, DNS resolver logs, NAT logs, service meshes, and endpoint sensors replace physical TAPs.
- **"More logs means better detection."** More unactionable data increases cost and analyst load unless fields support triage.

### Modern limitations

- TLS 1.3, QUIC, ECH, DNS-over-HTTPS, mobile apps, cloud NAT, service meshes, and ephemeral workloads reduce classic payload visibility.
- Asset identity changes faster than IP identity in cloud and container environments.
- Vendor schemas change; detections need regression tests and field-quality monitoring.

### Telemetry blind spots

- East-west traffic inside flat networks with no choke point.
- Host-local traffic, loopback, container bridge traffic, and service-mesh sidecar behavior.
- Unmanaged endpoints, appliances, network devices, IoT, and third-party SaaS.
- Sampled flow records, short-lived connections, and low-volume beaconing.
- SPAN/TAP gaps, asymmetric routing, packet loss, and clock skew.

## Practical labs

Run only in owned local labs, private cloud accounts, HTB/THM-style ranges, or isolated containers.

### Compare packet, flow, and protocol views

```
# Terminal 1: capture packets on a lab host
sudo tcpdump -i any -w scan.pcap 'host 10.10.10.10'

# Terminal 2: generate a small authorized scan
nmap -Pn -sS -p 22,80,443,445 10.10.10.10

# Terminal 3: derive Zeek logs from the same pcap
mkdir -p zeek-out && cd zeek-out
zeek -r ../scan.pcap
cat conn.log
```

Expected telemetry: tcpdump shows packets and flags; Zeek `conn.log` summarizes connections and TCP states; no single view includes process ancestry unless endpoint telemetry is added.

### Observe SPAN/TAP-style loss as a detection variable

```
# Use a lab pcap or safe capture feed.
zeek -r busy-link.pcap policy/misc/capture-loss
cat capture_loss.log
```

Expected telemetry: `capture_loss.log` reports loss evidence. The defensive lesson is that missing alerts during loss windows cannot be interpreted as clean traffic.

### Build a flow-shaped scan table from Zeek

```
zeek -r scan.pcap
zeek-cut id.orig_h id.resp_h id.resp_p proto conn_state duration orig_pkts resp_pkts < conn.log |
  sort | head -50
```

Expected telemetry: scan behavior appears as many short connections with repeated source, destination spread, unusual states, and low response payload.

### Compare public and internal viewpoint

```
# From a public-controlled host
nmap -Pn --top-ports 100 LAB_PUBLIC_IP

# From an internal lab subnet
nmap -Pn --top-ports 100 LAB_PRIVATE_IP
```

Expected telemetry: the difference between outputs is the boundary story. Defenders should compare logs from edge devices, internal sensors, and endpoint events for the same time window.

### Test encrypted metadata visibility

```
openssl s_client -connect example.com:443 -servername example.com -alpn h2 </dev/null 2>/dev/null |
  sed -n '1,30p'
```

Expected telemetry: payload is encrypted, but SNI, certificate details, negotiated protocol, destination, timing, and byte counts can still be useful depending on sensor placement.

## Practical examples

- A perimeter sensor sees Masscan-like SYN fan-out; EDR shows it originated from `masscan` launched by a temporary script on a dev workstation.
- Cloud VPC flow logs show a new workload contacting hundreds of internal `445/tcp` destinations; Zeek is blind because no sensor exists inside that subnet.
- A WAF logs URI enumeration, but NetFlow shows the same client also probing SSH and RDP on adjacent hosts.
- Zeek `ssl.log` sees a first-seen JA4-like TLS profile from a database subnet that should only run Java services.
- An incident review finds no Suricata alert during an exploit window, but `capture_loss.log` shows sensor loss above the threshold.

## Related notes

- [[index|Detection Engineering]]
- [[zeek-suricata-and-netflow-analysis]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[encrypted-traffic-analysis-and-metadata-leakage]]
- [[scan-anomaly-detection-and-fingerprint-analysis]]
- [[edr-network-observability-and-process-correlation]]
- [[packet-analysis|Packet Analysis]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[active-recon|Active Recon]]
- [[run-scan-pipeline|Run External Recon Scan Pipeline]]

### Suggested future atomic notes

- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- telemetry-retention-tiers
- sensor-health-and-capture-loss
- encrypted-traffic-metadata

## References

- **Foundational:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Cisco SPAN Configuration Guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
