---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Zeek, Suricata, and NetFlow Analysis

## Definition

Zeek, Suricata, and NetFlow/IPFIX are complementary network telemetry layers: Zeek reconstructs protocol transactions, Suricata applies detection rules and emits alert/protocol events, and NetFlow/IPFIX summarizes communication patterns at scale.

## Why it matters

Many teams say "we have network monitoring" without knowing which evidence layer they actually have. That distinction decides what they can detect. NetFlow may show a scan but not the HTTP paths. Suricata may alert on a signature but not preserve a full transaction history. Zeek may reconstruct rich protocol logs but not make the same rule-based alerting decisions.

The senior model is not tool rivalry. It is evidence composition.

## How it works

The three layers answer **3 different questions**:

1. **NetFlow/IPFIX:** Who talked to whom, when, how often, for how long, and how much?
2. **Zeek:** What protocol transactions happened, what metadata was visible, and what looked weird?
3. **Suricata:** Which packets/streams/protocol states matched detection logic, and what alert or event did the engine produce?

Example:

```
Observation: 10.0.5.20 probed 10.0.9.0/24 on 445/tcp.

NetFlow: one source, 254 destinations, low bytes, short duration.
Zeek conn.log: many failed TCP states and no valid SMB sessions.
Suricata eve.json: scan alerts and possible SMB probe signatures.
Conclusion: discovery behavior, not confirmed exploitation.
```

The bug is assuming one layer can answer all three questions.

## Techniques / patterns

- **Use NetFlow for breadth.** Detect fan-out, long-lived connections, byte asymmetry, beacon periodicity, rare ports, and environment-wide movement.
- **Use Zeek for transaction truth.** Inspect `conn.log`, `dns.log`, `http.log`, `ssl.log`, `ssh.log`, `files.log`, `weird.log`, and `notice.log`.
- **Use Suricata for signatures and alert context.** Review `eve.json` alert, flow, HTTP, DNS, TLS, file, and anomaly records.
- **Join with Community ID where possible.** Shared flow identifiers help tie Zeek and Suricata records for the same flow.
- **Check capture quality first.** Zeek `capture_loss.log`, Suricata drop stats, interface counters, and SPAN/TAP health shape every conclusion.
- **Read absence carefully.** No Suricata alert plus Zeek protocol logs is different from no packets, no parser support, encrypted payload, or sensor loss.

## Variants and bypasses

The comparison has **6 operating modes**.

### 1. NetFlow-only monitoring

Useful for high-level behavior and retention at scale. Weak for payload, protocol semantics, and process attribution.

### 2. Zeek-only NSM

Strong for protocol metadata, weird behavior, local policy scripting, and analyst pivoting. Weak when the question is "did this known exploit signature match?"

### 3. Suricata-only IDS

Strong for known detection logic, alert workflows, and protocol-aware signatures. Weak when no rule exists or when analysts need transaction history beyond the alert.

### 4. Zeek plus Suricata

The classic NSM pairing: Zeek explains what happened; Suricata flags known suspicious shapes. Shared pcap and flow IDs make this powerful.

### 5. Flow plus endpoint

Common in cloud or high-speed networks where packet sensors are limited. Useful for role-aware behavior and process correlation, but weaker for protocol-level root cause.

### 6. Offline pcap replay

The safest lab and regression mode. Replay the same pcap through Zeek and Suricata to compare evidence, alerts, parser behavior, and rule changes.

## Impact

- **Investigation depth.** Zeek can reconstruct what a scanner asked for; Suricata can show which rule fired; NetFlow can prove scale and timing.
- **Detection resilience.** If one layer misses an event, another may still preserve enough evidence.
- **Cost control.** Flow records retain broad visibility longer; packet/protocol logs provide depth where needed.
- **Tool misuse risk.** Treating Suricata alerts as protocol logs or NetFlow as packet capture causes bad conclusions.
- **Operational quality.** Capture loss and parser errors can be as important as the adversary behavior.

## Detection and defense

Ordered by effectiveness:

1.
**Design by evidence question.**
   Decide whether you need scale, protocol semantics, signatures, payload, or process context. Then pick the layer that can answer it.

2.
**Run Zeek and Suricata from the same observation points when feasible.**
   Shared packets make contradictions meaningful. Different sensor placement can explain mismatched logs.

3.
**Correlate with flow IDs and timestamps.**
   Community ID, precise timestamps, and consistent normalization reduce manual joins and false disagreements.

4.
**Monitor sensor health as security telemetry.**
   Packet loss, rule-engine drops, parser failures, disk pressure, and queue overflow should create operational alerts.

5.
**Keep packet samples for high-value detections.**
   Full retention may be impossible, but representative pcaps around alerts improve regression testing and analyst trust.

### What does not work as a primary defense

- **Choosing one tool as the whole strategy.** Zeek, Suricata, and NetFlow answer different questions.
- **Counting alerts as incidents.** Suricata alert counts measure rule activity, not business impact.
- **Assuming flow logs prove payload safety.** Flow records cannot validate exploit content.
- **Assuming Zeek logs every application.** Parser support, encryption, visibility, and traffic quality constrain reconstruction.
- **Ignoring capture loss.** Packet loss changes both alert reliability and protocol reconstruction.

### Operational misconceptions

- **"Zeek is an IDS replacement."** Zeek can detect and notice, but its main strength is rich NSM telemetry and programmable policy.
- **"Suricata is only signatures."** Suricata also produces protocol logs, flow records, file events, anomalies, and TLS metadata.
- **"NetFlow is low value because it lacks payload."** Flow is often the only scalable way to detect fan-out, beaconing, and exfil shape over long windows.
- **"Offline replay proves production behavior."** Replay tests engine logic, not production sensor placement, packet loss, or timing effects.

### Modern limitations

- QUIC, TLS 1.3, ECH, DoH, service meshes, and cloud overlays reduce classic payload/protocol visibility.
- High-speed links can exceed commodity sensor capacity.
- Cloud environments may not allow TAP-like packet access.
- Protocol parsers lag behind new protocols and proprietary encodings.

### Telemetry blind spots

- Asymmetric routing where the sensor sees only one direction.
- SPAN oversubscription or dropped mirror traffic.
- Encrypted protocols without visible metadata or proxy logs.
- Sampled flow records that miss short connections.
- Load balancer or NAT points that hide original client identity.

## Practical labs

Use offline pcap replay for repeatability.

### Replay the same scan pcap through Zeek and Suricata

```
mkdir -p zeek-out suricata-out
(cd zeek-out && zeek -r ../scan.pcap)
suricata -r scan.pcap -l suricata-out
ls zeek-out
jq 'select(.event_type=="alert") | .alert.signature' suricata-out/eve.json | sort | uniq -c
```

Expected telemetry: Zeek produces transaction logs; Suricata produces alerts and EVE events. Compare what each layer explains.

### Use Zeek to summarize port scan states

```
zeek-cut id.orig_h id.resp_h id.resp_p conn_state history < zeek-out/conn.log |
  awk '{k=$1" "$3" "$4; c[k]++} END {for (k in c) print c[k], k}' |
  sort -nr | head
```

Expected telemetry: repeated connection states show scan shape even without payload alerts.

### Inspect Suricata TLS metadata

```
jq 'select(.event_type=="tls") | {src:.src_ip,dst:.dest_ip,sni:.tls.sni,ja3:.tls.ja3,ja4:.tls.ja4}' \
  suricata-out/eve.json | head
```

Expected telemetry: encrypted traffic can still expose handshake metadata when configured and visible.

### Check capture loss before trusting absence

```
(cd zeek-out && zeek -r ../busy-link.pcap policy/misc/capture-loss)
cat zeek-out/capture_loss.log
```

Expected telemetry: loss records change the interpretation of missing alerts or incomplete protocol sessions.

### Derive a NetFlow-like table from Zeek

```
zeek-cut ts uid id.orig_h id.resp_h id.resp_p proto duration orig_bytes resp_bytes < zeek-out/conn.log |
  head -30
```

Expected telemetry: flow-like fields are useful for broad behavior, while Zeek keeps additional protocol context in separate logs.

## Practical examples

- NetFlow shows thousands of short `3389/tcp` attempts; Suricata has no exploit alerts; Zeek confirms no successful RDP sessions.
- Zeek `dns.log` shows domain-generation-like query volume; Suricata DNS rules add known-bad matches for a subset.
- Suricata alerts on an HTTP exploit pattern; Zeek `http.log` shows method, host, URI, user agent, and response code for triage.
- Zeek `weird.log` shows malformed protocol behavior during a decoy/fragmentation test that a pure flow system would miss.
- Flow logs show exfil-like byte asymmetry; Zeek `ssl.log` and EDR process telemetry identify the client and TLS profile.

## Related notes

- [[index|Detection Engineering]]
- [[network-telemetry-sources-and-visibility]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[encrypted-traffic-analysis-and-metadata-leakage]]
- [[behavioral-detection-vs-signature-detection]]
- [[scan-anomaly-detection-and-fingerprint-analysis]]
- [[edr-network-observability-and-process-correlation]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]

### Suggested future atomic notes

- threat-hunting-with-zeek
- suricata-rule-tuning
- community-id-correlation
- sensor-health-and-capture-loss
- netflow-beaconing-analysis

## References

- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek Capture Loss Logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Foundational:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
