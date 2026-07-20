---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Telemetry Normalization, Correlation, and Enrichment

## Definition

Telemetry normalization maps heterogeneous events into consistent fields; enrichment adds context; correlation stitches related events into higher-order evidence.

## Why it matters

Detection quality often depends less on the rule and more on whether the telemetry pipeline produces reliable, normalized, enriched events. A perfect detection written against `source.ip` fails if one log calls it `src`, another calls it `client_ip`, and a proxy overwrites it with a load-balancer address.

Security systems engineering lives in this layer. Normalization, enrichment, timestamps, entity resolution, and correlation keys decide whether detections are possible, explainable, and maintainable.

## How it works

A telemetry pipeline has **7 transformation stages**:

1. **Ingest.** Collect raw logs, alerts, flow records, endpoint events, cloud audit events, and application logs.
2. **Parse.** Extract fields from JSON, syslog, CSV, EVE, Zeek TSV, Windows events, web logs, and API records.
3. **Normalize.** Map local fields into a schema such as ECS, OTel semantic conventions, or a local canonical model.
4. **Enrich.** Add asset owner, role, identity, cloud metadata, GeoIP, threat intel, vulnerability, and business context.
5. **Deduplicate.** Collapse duplicate records while preserving count and source details.
6. **Correlate.** Join events by host, user, IP, process, session, flow ID, request ID, cloud resource, or time window.
7. **Quality monitor.** Detect parser failures, field drift, timestamp skew, missing enrichments, and ingestion delay.

Example:

```
Apache: 10.0.0.5 GET /admin 403
Zeek: id.orig_h=10.0.0.5 id.resp_h=10.0.0.20 id.resp_p=443 service=ssl
EDR: DeviceName=web-1 InitiatingProcessFileName=curl RemoteIP=10.0.0.20

Normalized:
source.ip=10.0.0.5 destination.ip=10.0.0.20 destination.port=443
process.name=curl host.name=web-1 event.action=http_request
```

The detection depends on the normalized join, not only the raw events.

## Techniques / patterns

- **Schema mapping.** Map source-specific fields into ECS, OTel semantic conventions, or local fields.
- **Timestamp alignment.** Preserve original timestamp, ingestion timestamp, timezone, clock source, and parsing delay.
- **Correlation keys.** Use stable keys: device ID, process unique ID, cloud instance ID, user SID/object ID, Community ID, session ID, request ID.
- **Entity resolution.** Link IPs, hostnames, device IDs, cloud resources, containers, and identities that represent the same entity.
- **Asset enrichment.** Add owner, environment, criticality, role, exposure, subnet, and business service.
- **Identity enrichment.** Add account type, MFA state, group membership, privilege tier, source identity provider, and service-account ownership.
- **Threat-intel enrichment.** Add reputation and sightings carefully; do not turn weak intel into a verdict.

## Attacker perspective

Attackers exploit pipeline weakness by moving through places where identity is ambiguous, source IPs are shared, logs are delayed, field parsing fails, or entity joins are wrong. They benefit when a SOC cannot tell whether `10.0.0.5` is a user laptop, NAT gateway, container node, scanner, or cloud workload.

## Defender perspective

Defenders need normalized events that preserve raw truth. Good pipelines keep `event.original` or equivalent raw fields, map common fields, and store enough source-specific detail to investigate. The goal is not to flatten every log into sameness; it is to make joins reliable without losing evidence.

## Detection and engineering tradeoffs

1.
**Canonical schema vs source fidelity.**
   A common schema enables correlation. Over-normalization can erase source-specific fields that explain the event.

2.
**Real-time enrichment vs latency.**
   More enrichment improves triage but can delay alerting or fail under dependency outages.

3.
**Deduplication vs evidence loss.**
   Dedup reduces noise but can hide volume, retry behavior, or multi-sensor confirmation.

4.
**GeoIP and threat intel vs false confidence.**
   GeoIP can be wrong, VPN/proxy-heavy, or irrelevant. Threat intel can be stale or overbroad.

5.
**Correlation windows vs false joins.**
   Longer windows catch slow sequences but increase accidental event chaining.

## Detection and defense

Ordered by effectiveness:

1.
**Define required fields per detection.**
   Every detection should declare which normalized fields it needs and what happens when they are absent.

2.
**Preserve raw event content.**
   Raw fields let analysts debug parsers, prove chain-of-custody, and recover when schemas change.

3.
**Use stable entity identifiers.**
   Prefer device IDs, cloud resource IDs, user object IDs, process unique IDs, and flow IDs over display names or recycled PIDs.

4.
**Monitor pipeline health.**
   Parser error rate, missing field rate, enrichment failure, clock skew, and delayed ingestion should alert.

5.
**Version schemas and mappings.**
   ECS, OTel, vendor schemas, and local fields evolve. Detection-as-code should pin and test mapping assumptions.

### What does not work as a primary defense

- **Regex parsing without quality checks.** It silently breaks when formats change.
- **GeoIP as attribution.** Location is weak evidence and often reflects hosting, VPN, or provider routing.
- **Threat intel as verdict.** Intel enriches; it does not replace local behavior and asset context.
- **Hostname-only joins.** Hostnames change and collide; use stable IDs where possible.
- **Discarding original events.** It makes parser mistakes unrecoverable.

### Operational misconceptions

- **"Normalization is boring plumbing."** It is the detection system's sensory cortex.
- **"A common schema solves correlation."** Schema helps, but timestamps, entity resolution, and data quality still decide correctness.
- **"Enrichment always improves detection."** Bad enrichment creates confident false positives.
- **"Deduplication only removes noise."** It can remove evidence of repetition and scale.

### Modern limitations

- ECS and OTel convergence is directional, not a perfect merge; some fields have different names or semantics.
- Vendor schemas change over time.
- Cloud resources are ephemeral and IP identity is unstable.
- SaaS logs may lack raw event fidelity or stable identifiers.

### Telemetry blind spots

- Events without original timestamp or timezone.
- Missing process unique IDs, request IDs, session IDs, cloud IDs, or identity object IDs.
- NAT/proxy/load-balancer logs that hide original source unless forwarded fields are trusted correctly.
- Enrichment systems down during incidents.

## Practical labs

Use local generated logs.

### Lab 1 - Normalize heterogeneous logs

Objective: Convert Apache-like, Zeek-like, and endpoint-like records into common fields.

```
cat > /tmp/raw-events.jsonl <<'EOF'
{"type":"apache","client_ip":"10.0.0.5","host":"web","method":"GET","uri":"/admin","status":403,"ts":"2026-05-11T10:00:00Z"}
{"type":"zeek","id.orig_h":"10.0.0.5","id.resp_h":"10.0.0.20","id.resp_p":443,"service":"ssl","ts":"2026-05-11T10:00:01Z"}
{"type":"edr","DeviceName":"web","InitiatingProcessFileName":"curl","RemoteIP":"10.0.0.20","RemotePort":443,"Timestamp":"2026-05-11T10:00:02Z"}
EOF
jq 'if .type=="apache" then {"@timestamp":.ts,"source.ip":.client_ip,"host.name":.host,"http.request.method":.method,"url.path":.uri,"http.response.status_code":.status}
elif .type=="zeek" then {"@timestamp":.ts,"source.ip":."id.orig_h","destination.ip":."id.resp_h","destination.port":."id.resp_p","network.protocol":.service}
else {"@timestamp":.Timestamp,"host.name":.DeviceName,"process.name":.InitiatingProcessFileName,"destination.ip":.RemoteIP,"destination.port":.RemotePort} end' /tmp/raw-events.jsonl
```

Expected telemetry: three sources become joinable. Defenders would observe that correlation requires common fields. Limitation: toy mapping lacks raw preservation and type validation. Misconception corrected: "the rule is independent of pipeline quality."

### Lab 2 - Demonstrate bad entity resolution

Objective: Show why IP-only joins are weak.

```
cat > /tmp/entities.csv <<'EOF'
time,ip,entity
10:00,10.0.0.5,laptop-a
10:05,10.0.0.5,vpn-nat
10:10,10.0.0.5,container-node
EOF
column -t -s, /tmp/entities.csv
```

Expected telemetry: one IP maps to multiple entities over time. Defenders would need timestamps and stable IDs. Misconception corrected: "source IP equals actor."

## Practical examples

- A Suricata alert and Zeek `conn.log` join cleanly only when timestamps and 5-tuples align.
- An EDR process event and network event join correctly with process unique ID, not just PID.
- A cloud flow log needs instance ID and tags before analysts know owner and criticality.
- A proxy log needs trusted forwarded-header parsing before `source.ip` is meaningful.

## Related notes

- [[network-telemetry-sources-and-visibility]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[false-positives-false-negatives-and-detection-tradeoffs]]
- [[attack-path-correlation-and-kill-chain-observability]]
- [[edr-network-observability-and-process-correlation]]
- [[silver-ticket-and-service-account-persistence|Silver Ticket and Service Account Persistence]]
- [[client-ip-trust|Client IP Trust]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]

### Suggested future atomic notes

- ecs-and-otel-for-security-telemetry
- entity-resolution-for-detection
- pipeline-health-monitoring
- community-id-correlation

## References

- **Foundational:** Elastic Common Schema Reference - https://www.elastic.co/docs/reference/ecs/
- **Foundational:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Foundational:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
