---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Network Security Monitoring Discipline

## Definition

Network security monitoring (NSM) is the discipline of *collecting, retaining, and analyzing network evidence* so that intrusions are detected and investigated even when prevention has already failed. NSM is not a product or a rule format — it is the operating posture that says **visibility is engineered before detection is written**: you decide where sensors sit and what evidence layers you keep, and only then compose detections on top of that evidence. This note is the spine for the network side of the detection-engineering branch; the sensor, tool, and telemetry notes hang off it.

## Why it matters

Prevention eventually fails — every credential gets phished, every perimeter gets a hole, every EDR has a gap. NSM is the discipline built on that premise (Richard Bejtlich's founding thesis): if you cannot stop the intrusion, you must at least *see* it and reconstruct what happened. The branch-level payoff is fourfold:

- **Detection quality is capped by visibility.** A perfect rule on data you never collected fires zero times. The load-bearing decision is sensor placement and evidence retention, not rule syntax — which is why this note sits above [[network-telemetry-sources-and-visibility]] and [[zeek-suricata-and-netflow-analysis]].
- **High fidelity comes from composition, not from any single signal.** A single rule is either noisy or blind. Modern high-fidelity detection accumulates several weak network signals (flow shape + protocol anomaly + fingerprint + endpoint correlation) into one strong, evasion-resistant finding. This is the core of the discipline and the answer to "stay under 1% false-positive at enterprise scale."
- **Evidence outlives the alert.** NSM keeps session and transaction records so that an intrusion discovered on Tuesday can be walked backward to its Saturday origin. Detection without retained evidence is an alarm with no flight recorder.
- **The discipline is adversarial.** Every collection choice has a corresponding evasion (encrypted payloads, low-and-slow beacons, east-west blind spots), and every evasion has a residual signal. NSM is the defender's half of the [[attacker-defender-duality-as-a-learning-tool|attacker-defender duality]] played at the wire.

## How it works

NSM runs as a **4-stage cycle** — *collect → detect → analyze → escalate* — feeding back into collection as gaps are found:

1. **Collect.** Place sensors at trust boundaries (perimeter, DMZ, inter-VLAN, cloud egress) and on endpoints, and decide which evidence layers to retain and for how long.
2. **Detect.** Run signature, anomaly, behavioral, and correlation logic against the collected evidence to surface candidate events.
3. **Analyze.** A human (or higher-order rule) pivots across evidence layers to confirm or dismiss the candidate and scope it.
4. **Escalate.** Confirmed activity becomes an incident; gaps found during analysis become new collection requirements, closing the loop.

The evidence the cycle runs on comes in **4 layers**, ordered cheapest-and-longest-retained to richest-and-shortest-retained — and, critically, *poorest-fidelity to richest-fidelity*:

| Layer | Example source | Answers | Retention economics |
| --- | --- | --- | --- |
| **Flow / session** | NetFlow / IPFIX | who talked to whom, how much, when | cheap, weeks–months, no content |
| **Transaction / protocol logs** | Zeek `conn`/`dns`/`http`/`ssl`/`x509` | structured per-protocol records, fingerprints | mid cost, high analytic value |
| **Alert / signature** | Suricata / Snort EVE | known-bad pattern matched | event-only, points at the needle |
| **Full content** | PCAP | every byte on the wire | expensive, hours–days, ground truth |

Two cross-cutting evidence types survive encryption and matter disproportionately in 2026: **fingerprints** (JA3/JA4 client/server TLS fingerprints, HTTP/2 fingerprints) and **metadata** (timing, flow shape, SNI, certificate fields) — see [[encrypted-traffic-analysis-and-metadata-leakage]].

The discipline's central insight: **the cache key of detection is the cache key of evidence.** If the origin behavior reads a signal your sensors never recorded, no rule can ever see it. The bug is rarely "the rule was wrong"; it is "the evidence layer that would have shown it was never collected, or was collected where the traffic doesn't pass."

> Section adaptation: this is a methodology note, so *How it works* describes a cycle and an evidence model rather than a single exploit mechanism, and *Variants and bypasses* below carries the adversary-evasion view rather than payload variants.

## Techniques / patterns

What a detection engineer actually does inside the discipline:

- **Map collection to a coverage model before writing rules.** Use [MITRE ATT&CK Data Sources](https://attack.mitre.org/datasources/) as the checklist: for each technique you care about, name the data source and the sensor that would witness it. Unmapped techniques are blind spots, not "low risk."
- **Compose multi-signal detections (source → corroboration → enrichment → verdict).** Start from one suspicious primitive (a new JA3 hash, a rare DNS parent domain, a flow to a fresh ASN), corroborate with a second independent layer, enrich with asset/identity context, then decide. Single-layer rules are the FP factory.
- **Choose the enrichment-vs-filter boundary deliberately.** Filtering drops events before storage (cheap, irreversible, creates blind spots); enrichment adds context at query time (flexible, costly). Filter only what you can prove is never evidentiary; enrich the rest.
- **Baseline per-entity, not globally.** "Unusual" is meaningful only against a per-host / per-service-account / per-segment baseline. A global threshold misses the surgical operator and drowns the noisy one.
- **Pivot across layers during analysis.** Alert (Suricata) → transaction (Zeek `ssl.log`, `dns.log`) → flow (was this a one-shot or a beacon?) → full content (PCAP, only if retained). Fluency in moving up and down the layer stack is the analyst skill.
- **Treat detections as code.** Version rules, write them against test captures, and review changes — see *Detection and defense* below.

## Variants and bypasses

For a discipline note, this section is the **adversary-pressure map**: the 4 structural ways operators defeat NSM, and the residual signal each leaves.

### 1. Encryption blindness

TLS 1.3, ESNI/ECH, and DoH hide payloads and increasingly hide SNI. The content layer goes dark. **Residual signal:** JA3/JA4 fingerprints, certificate metadata, flow timing and volume, and destination reputation still survive — the operator can encrypt the *what* but not the *that-it-happened*.

### 2. Volumetric / low-and-slow evasion

Beacons jittered to once-per-hour, data exfil throttled below alerting thresholds, traffic blended into business hours. Threshold rules miss it. **Residual signal:** regularity itself is anomalous — beaconing analysis on inter-arrival timing and byte-count consistency catches machine-paced traffic a human would never generate.

### 3. Sensor-placement gaps (east-west and cloud)

NSM historically watched north-south (perimeter) traffic; lateral movement inside a segment, and traffic between cloud workloads, may never cross a sensor. **Residual signal:** endpoint telemetry — this is where [[edr-network-observability-and-process-correlation|EDR network observability]] and cloud flow logs claw back the visibility packet sensors lack. The discipline's modern form is *network + endpoint + identity*, not network alone.

### 4. Living-off-the-land / protocol mimicry

C2 over HTTPS to a CDN, DNS tunneling that looks like normal resolution, traffic shaped to mimic legitimate SaaS. Signature matching fails because the bytes are "normal." **Residual signal:** behavioral and relational anomalies — a workstation that has never spoken to a host now beaconing to it, a process with no business making DNS TXT queries.

The through-line: **no single layer is evasion-proof, but the layers are not independent.** Defeating all of them at once — encrypted, slow, off-sensor, *and* behaviorally normal across endpoint and identity — is the expensive bar NSM forces the operator to clear.

## Impact

What the quality of the discipline determines, ordered by consequence:

- **Dwell time.** Mature NSM compresses attacker dwell from months to hours; absent or alert-only NSM leaves intrusions undiscovered until a third party reports them.
- **Investigative reach.** Retained session/transaction evidence lets responders reconstruct the full kill chain; without it, scoping is guesswork and remediation is incomplete.
- **False-positive load and analyst burnout.** Single-signal, un-baselined detection floods the SOC, drives alert fatigue, and *lowers* real detection rate as analysts tune out — the precision/recall problem owned by [[false-positives-false-negatives-and-detection-tradeoffs]].
- **Evasion resilience.** Multi-layer composition raises the operator's cost; single-layer detection is bypassed by the first technique that avoids that layer.
- **Audit and compliance defensibility.** "We would have seen it" is only true if the evidence layer and retention existed at the time — NSM is also the record that answers regulators.

## Detection and defense

For a detection-discipline note, "defense" is *how to make the discipline high-fidelity*. Ordered by effectiveness:

1.
**Engineer visibility before detection.**
   Decide sensor placement and evidence-layer retention against an ATT&CK Data Sources coverage map first. A rule on uncollected data is theater. This is the single highest-leverage control because it caps everything downstream.

2.
**Compose multi-signal (higher-order) detections.**
   Aggregate several independent weak signals into one strong finding rather than alerting on each. Elastic's [higher-order detection rules](https://www.elastic.co/security-labs/higher-order-detection-rules) formalize this: detections whose inputs are other detections. This is what simultaneously raises recall (catches evasion that dodges one signal) and precision (a coincidence across independent layers is rarely benign).

3.
**Treat detections as code with a lifecycle.**
   Version rules in source control, test them against labeled captures (true-positive and known-benign), and review changes. Decide explicitly whether to **retire** (the technique is dead / the FP cost exceeds value) or **evolve** (re-baseline, add a corroborating signal) a rule — rules that are never reviewed silently rot into noise or blindness.

4.
**Baseline and enrich per-entity.**
   Maintain per-host/per-account/per-segment normal, and enrich events with asset criticality and identity context at analysis time so the verdict accounts for *who* and *what*, not just *what packet*.

5.
**Tune against operator evasion, not just lab traffic.**
   Test detections against the evasions in *Variants and bypasses* (encrypted, throttled, off-sensor, LOTL). A rule that only catches the noisy default tool is a rule the real operator walks past — see [[detection-evasion-myths-and-modern-limitations]].

6.
**Instrument the gaps you cannot close.**
   Where a layer is genuinely blind (encrypted east-west, unmanaged cloud), document the blind spot and compensate with the adjacent layer (endpoint/identity) rather than pretending coverage exists.

### What does not work as a primary defense

- **Signature-only detection.** Signatures catch known-bad bytes; they are blind to novel and encrypted-and-mimicked C2. Necessary as one layer, fatal as the only one.
- **Threshold-only alerting.** Volumetric thresholds miss the surgical, low-and-slow operator and flood on noisy-but-benign bursts. Behavior and per-entity baselines are the fix, not a bigger number.
- **IOC feeds as a strategy.** Atomic indicators (IPs, hashes, domains) are the cheapest thing for an attacker to rotate — the base of David Bianco's Pyramid of Pain. Useful for enrichment, not a detection program.
- **"We have a SIEM."** A SIEM is a query engine over whatever you fed it. Without engineered collection and composed detections, it is an expensive log bucket.
- **More alerts.** Volume is not fidelity. Un-composed, un-baselined alerting *reduces* effective detection by burning analyst attention.

## Practical labs

Run only against owned lab environments or authorized engagements.

### Triage Zeek transaction evidence

```
# From a Zeek output directory: top destinations by connection count, then
# pull the matching SSL fingerprints. Two layers (flow + transaction) in one pivot.
cat conn.log | zeek-cut id.resp_h | sort | uniq -c | sort -rn | head
cat ssl.log  | zeek-cut id.resp_h server_name ja3 ja3s validation_status | sort | uniq -c | sort -rn | head
```

A destination that is high-volume *and* presents a rare JA3 with `validation_status` not "ok" is worth more than either signal alone.

### Surface beaconing in flow timing

```
# Inter-arrival regularity for one src→dst pair. Machine-paced C2 shows
# near-constant deltas; human traffic is bursty and irregular.
cat conn.log | zeek-cut ts id.orig_h id.resp_h \
  | awk '$2=="10.0.0.50" && $3=="203.0.113.10" {if(p)print $1-p; p=$1}' \
  | sort -n | uniq -c | sort -rn | head
```

A tight cluster of identical deltas is the residual signal that survives jitter only partially — exactly the evasion-resilience point.

### Read a Suricata EVE alert and pivot to the flow

```
# Pull one alert, then the flow record for the same flow_id — alert layer → flow layer.
jq -c 'select(.event_type=="alert")  | {ts:.timestamp, sig:.alert.signature, fid:.flow_id, src:.src_ip, dst:.dest_ip}' eve.json | head
jq -c 'select(.event_type=="flow" and .flow_id==<FLOW_ID>) | {bytes:.flow.bytes_toserver, pkts:.flow.pkts_toserver, age:.flow.age}' eve.json
```

The alert says "what"; the flow says "how much / how long" — the analyst verdict needs both.

### Build a tiny ATT&CK coverage map

```
# For three techniques you care about, name the data source and the sensor.
# Empty cells are blind spots — the output of the discipline's first stage.
Technique                  | Data source (ATT&CK)        | Sensor / layer        | Collected?
T1071 App-Layer C2 (HTTPS) | Network Traffic Flow        | Zeek ssl/conn + JA4   | y/n
T1048 Exfil over alt proto | Network Traffic Content     | Suricata + NetFlow    | y/n
T1021 Lateral (east-west)  | Network Traffic Flow        | inter-VLAN tap?       | y/n  <-- usually the gap
```

The blank "Collected?" cells are your real backlog — they outrank any new rule.

## Practical examples

- **Beaconing C2 over HTTPS to a CDN.** Signatures see nothing; the detection is built from flow regularity + a rare JA4 + a destination the host has never contacted, composed into one finding.
- **Slow exfil under the DLP threshold.** No single hour trips the alert; the cumulative byte count to one external ASN over a week, baselined per-host, does.
- **East-west lateral movement.** Never crosses the perimeter sensor; caught by endpoint network telemetry correlated to a process with no business opening SMB to a peer ([[edr-network-observability-and-process-correlation]]).
- **DNS tunneling that looks like resolution.** Per-domain entropy and TXT-record volume against a per-resolver baseline flag it where signature matching fails.
- **Post-incident reconstruction.** A credential-theft alert on Tuesday is walked back through retained Zeek `conn`/`ssl` logs to a Saturday drive-by — only because session evidence was retained, not just alerts.

## Related notes

- [[network-telemetry-sources-and-visibility]] — the sensor-placement and visibility-architecture layer this discipline sits on.
- [[zeek-suricata-and-netflow-analysis]] — the three tools that produce the transaction/alert/flow evidence layers.
- [[ids-ips-and-behavioral-detection-pipelines]] — the detection-pipeline mechanics inside the *detect* stage.
- [[telemetry-normalization-correlation-and-enrichment]] — schema mapping and enrichment that make cross-layer correlation possible.
- [[behavioral-detection-vs-signature-detection]] — the model choice that decides what each layer can catch.
- [[false-positives-false-negatives-and-detection-tradeoffs]] — the precision/recall discipline behind "under 1% FP at scale."
- [[attack-path-correlation-and-kill-chain-observability]] — multi-stage correlation, the higher-order composition this note points to.
- [[encrypted-traffic-analysis-and-metadata-leakage]] — the residual-signal story when the content layer goes dark.
- [[edr-network-observability-and-process-correlation]] — the endpoint half that closes the east-west and cloud blind spots.
- [[detect-external-scan-pipeline|Detect External Scan Pipeline]] — a concrete NSM playbook that instantiates this cycle.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-frame: NSM is the defender's chair facing the operator's.

### Suggested future atomic notes

- detection-as-code-and-rule-lifecycle
- tap-vs-span-sensor-placement
- beaconing-analysis
- cloud-flow-logs-and-network-detection

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Foundational:** MITRE ATT&CK Data Sources — https://attack.mitre.org/datasources/
- **Foundational:** NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems — https://csrc.nist.gov/pubs/sp/800/94/final
- **Official Tool Docs:** Zeek logs reference — https://docs.zeek.org/en/current/logs/
- **Research / Deep Dive:** Elastic Security Labs — Higher-Order Detection Rules — https://www.elastic.co/security-labs/higher-order-detection-rules
- **Mitigation / Operations:** CISA — Best Practices for Event Logging and Threat Detection — https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
