---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# False Positives, False Negatives, and Detection Tradeoffs

## Definition

False positives are benign events classified as suspicious; false negatives are malicious or policy-relevant events that detection fails to identify.

## Why it matters

Security detection is statistical and operational engineering, not binary truth. A detector operates inside a real environment with uneven telemetry, changing baselines, limited analysts, delayed logs, incomplete labels, and adversaries that adapt.

"Detect everything" is impossible. "No alert" is not proof of safety. A mature program manages precision, recall, cost, alert fatigue, and residual risk deliberately.

## How it works

Detection tradeoffs are a **6-variable system**:

1. **Base rate.** Rare attacks produce many false positives when the environment generates huge benign volume.
2. **Precision.** Of the alerts fired, how many are useful?
3. **Recall.** Of the malicious events that occurred, how many were caught?
4. **Thresholds.** Counts, scores, rarity cutoffs, and time windows decide which side of the tradeoff is favored.
5. **Triage capacity.** A detection that exceeds analyst capacity becomes a denial of service against the SOC.
6. **Feedback quality.** Without labels, incident outcomes, and environment context, tuning drifts into guesswork.

Example:

```
Rule: alert when one source contacts more than 20 hosts on 445/tcp in 10 minutes.
High recall: threshold 5, many admin scripts alert.
High precision: threshold 200, slow lateral discovery is missed.
Better: threshold varies by host role, time window, and approved scanner list.
```

The useful question is not "is this threshold correct?" but "what risk and workload does this threshold choose?"

## Techniques / patterns

- **Precision/recall measurement.** Track useful alerts, benign alerts, missed incidents, and near misses.
- **Role-aware baselines.** Tune by source role, destination class, user type, subnet, service account, cloud workload, and maintenance window.
- **Threshold sweeps.** Test multiple thresholds against labeled or simulated data before picking one.
- **Correlation windows.** Tune time windows to attack tempo and environment noise.
- **Suppression hygiene.** Suppress with owner, reason, expiration, and compensating signal.
- **Severity calibration.** Severity should reflect impact, confidence, asset criticality, and response urgency, not rule author anxiety.

## Attacker perspective

Attackers exploit false-positive pressure. They blend into noisy admin patterns, operate slowly, use common tools, trigger low-value detections to desensitize analysts, or act during change windows.

They also exploit false-negative gaps: unmonitored subnets, unmanaged endpoints, sampled flow, disabled logging, cloud services without audit logs, or detections tuned too narrowly after noisy incidents.

## Defender perspective

Defenders must decide which errors are acceptable. A noisy detection on domain-controller credential dumping may be worth tuning slowly. A noisy detection on common browser behavior may need suppression or redesign. A false negative on exfiltration may be more costly than ten benign alerts, but a thousand benign alerts may hide the one true event.

## Detection and engineering tradeoffs

1.
**Recall vs precision.**
   Broader detections catch more variants but create more triage work. Narrower detections reduce work but miss adaptation.

2.
**Short windows vs long windows.**
   Short windows catch bursts and reduce unrelated joins. Long windows catch slow behavior but raise false correlation risk.

3.
**Global thresholds vs local baselines.**
   Global rules are portable. Local baselines are more accurate but require ownership and maintenance.

4.
**Suppression vs blindness.**
   Suppression protects analysts from noise but can hide future attacks that reuse the suppressed path.

5.
**Severity inflation vs trust.**
   Everything cannot be high severity. Inflated severity trains analysts to ignore severity.

## Detection and defense

Ordered by effectiveness:

1.
**Define the cost of both error types.**
   A false positive costs analyst time and trust. A false negative costs dwell time, scope, and incident impact. The relative cost changes by technique and asset class.

2.
**Measure alert outcomes.**
   Track true positive, benign true positive, false positive, duplicate, unresolved, and missed-incident labels. Tuning without outcomes is vibes.

3.
**Tune by entity role.**
   Scanner hosts, admin jump boxes, developer machines, production servers, service accounts, and user workstations need different thresholds.

4.
**Use staged severity.**
   Weak single signals can be low severity until joined to additional behavior, asset criticality, or identity risk.

5.
**Review suppressions as technical debt.**
   Every suppression should have an owner, expiry, rationale, and alternate monitoring if the risk remains.

### What does not work as a primary defense

- **"Detect everything."** Unlimited recall creates unbounded noise and still misses telemetry gaps.
- **Permanent allowlists.** They silently turn into blind spots as assets and users change.
- **One threshold for all assets.** It ignores role, baseline, and business function.
- **Severity as motivation.** Marking everything critical does not make response faster; it destroys prioritization.
- **No-alert closure.** Absence of an alert is only meaningful if telemetry and detection coverage are known.

### Operational misconceptions

- **"False positives are just bad rules."** Some are unavoidable because benign and malicious behavior overlap.
- **"False negatives are only missed signatures."** Many are missing telemetry, bad joins, retention gaps, or scope assumptions.
- **"Tuning means suppressing noise."** Tuning can mean adding context, changing windows, splitting detections, improving enrichment, or moving to correlation.
- **"More data always improves accuracy."** More noisy or unnormalized data can reduce accuracy.

### Modern limitations

- Labels are incomplete: many alerts are never conclusively true or false.
- Cloud and SaaS logs can arrive late, making real-time thresholds incomplete.
- Baselines drift with deployments, remote work, autoscaling, and business cycles.
- Adversaries deliberately choose behaviors that resemble administration.

### Telemetry blind spots

- Logs disabled or delayed during the event.
- Missing negative examples for training/tuning.
- Event deduplication that hides repeated behavior.
- Short retention that prevents missed-incident analysis.
- Aggregated cloud logs that collapse event detail.

## Practical labs

Use generated local data.

### Lab 1 - Tune a noisy threshold

Objective: Observe precision/recall tradeoffs.

Setup and steps:

```
cat > /tmp/scan-labels.csv <<'EOF'
source,distinct_hosts,label
scanner-approved,250,benign
admin-script,35,benign
dev-laptop,28,benign
compromised-1,42,malicious
compromised-2,12,malicious
db-server,8,malicious
EOF
for t in 5 10 20 40 100; do
  awk -F, -v t=$t 'NR>1 {alert=($2>t); if(alert&&$3=="malicious") tp++; if(alert&&$3=="benign") fp++; if(!alert&&$3=="malicious") fn++} END {print "threshold",t,"TP",tp+0,"FP",fp+0,"FN",fn+0}' /tmp/scan-labels.csv
done
```

Expected telemetry: low thresholds catch more malicious rows but create more benign alerts. High thresholds miss slow or smaller attacks. Defenders would tune by role rather than pick one global number. Misconception corrected: "threshold tuning has a perfect value."

### Lab 2 - Test suppression debt

Objective: Show how an allowlist can hide later compromise.

```
cat > /tmp/suppressions.csv <<'EOF'
entity,reason,expires
scanner-approved,monthly vuln scan,2026-06-01
admin-script,legacy maintenance,never
EOF
cat > /tmp/events.csv <<'EOF'
source,distinct_hosts,label
admin-script,120,malicious
scanner-approved,250,benign
EOF
awk -F, 'NR==FNR {s[$1]=$3; next} {print $0,"suppression_expires="s[$1]}' /tmp/suppressions.csv /tmp/events.csv
```

Expected telemetry: a non-expiring suppression masks risk. Limitation: real systems need owner and change context. Misconception corrected: "allowlist equals resolved."

## Practical examples

- A scan detector is noisy on vulnerability scanners but high value on database servers.
- A PowerShell rule becomes useful only after excluding approved admin jump hosts and adding suspicious parentage.
- A cloud API anomaly fires every deployment until release windows and service-account roles are added.
- A high-severity alert category loses analyst trust because most alerts are low-impact policy noise.

## Related notes

- [[behavioral-detection-vs-signature-detection]]
- [[ids-ips-and-behavioral-detection-pipelines]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[attack-path-correlation-and-kill-chain-observability]]
- [[network-telemetry-sources-and-visibility]]
- [[gmsa-and-modern-service-account-hardening|gMSA and Modern Service Account Hardening]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]

### Suggested future atomic notes

- precision-and-recall-for-security-detections
- suppression-debt
- severity-calibration
- detection-regression-testing

## References

- **Mitigation / Operations:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Foundational:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Research / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Foundational:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/
