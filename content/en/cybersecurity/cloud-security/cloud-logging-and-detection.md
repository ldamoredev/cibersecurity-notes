---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Logging and Detection

## Definition

Cloud logging and detection is the collection, retention, analysis, and alerting of cloud control-plane and workload events that reveal risky changes or compromise.

## Why it matters

Cloud attacks often happen through API calls: creating keys, changing policies, reading storage, disabling logs, opening firewalls, or launching resources. Without cloud audit logs, those actions become invisible.

The security question is not "do logs exist?" It is whether the right events are retained, protected, and reviewed quickly enough to matter.

## How it works

Cloud detection has **5 layers**:

1. **Control-plane audit logs.** Provider APIs record who changed what.
2. **Data access logs.** Storage, database, and secret reads may need separate logging.
3. **Network and workload logs.** Flow logs, host logs, and app logs show runtime behavior.
4. **Detection rules.** Alerts identify risky changes and suspicious use.
5. **Protected retention.** Logs are stored where attackers cannot easily erase them.

The bug is not missing one dashboard. The bug is unprotected, incomplete, or unactioned telemetry.

A worked example, high-risk change detection:

```
Event:
  security group modified to allow 0.0.0.0/0 on TCP/22

Control-plane log:
  actor, source IP, API action, resource ID recorded

Detection:
  alert fires because admin port became world-reachable

Response:
  owner confirms it was temporary debugging; rule removed; exception process updated

Decision:
  detection succeeded because logs, rule logic, owner routing, and response path all existed
```

Cloud detection is a workflow: event, signal, owner, decision, and remediation.

## Techniques / patterns

Reviews look at:

- whether audit logging is enabled in all accounts/projects/subscriptions
- log retention duration and immutability
- alerts for IAM changes, public exposure, key creation, and log tampering
- storage data-event logging
- network flow logs for sensitive subnets
- centralized security accounts or workspaces

## Variants and bypasses

Cloud logging failures have **5 common forms**.

### 1. Control-plane blind spot

Audit logs are disabled or incomplete in some regions/accounts.

### 2. Data-plane blind spot

Object reads, secret reads, or database access are not logged.

### 3. Tamperable logs

The same admin who can attack can delete or alter logs.

### 4. Alert fatigue

Important events are buried in noisy findings.

### 5. No response path

Alerts fire but nobody owns triage or containment.

## Impact

Ordered roughly by severity:

- **Delayed incident response.** Teams discover compromise late.
- **Weak forensics.** Missing history prevents scope analysis.
- **Persistence.** Attackers can create keys or roles without detection.
- **Data exposure uncertainty.** Without data access logs, read impact is unclear.
- **Compliance failure.** Required audit trails may be absent.

## Detection and defense

Ordered by effectiveness:

1.
**Enable organization-wide audit logging early.**
   Logs must exist before incidents and labs, not after.

2.
**Protect logs from workload and daily-admin identities.**
   Separate retention reduces attacker ability to cover tracks.

3.
**Alert on high-risk control-plane changes.**
   IAM changes, public exposure, key creation, and logging changes deserve fast review.

4.
**Capture data events for sensitive storage and secrets.**
   Control-plane logs alone may not show who read sensitive data.

5.
**Write triage runbooks.**
   Detection is incomplete without a human path from alert to decision.

### What does not work as a primary defense

- **Assuming default logs cover everything.** Data events and regions often need explicit setup.
- **Keeping logs in the same blast radius.** Attackers may delete what they can administer.
- **Alerting on everything.** Noise trains people to ignore real signals.
- **Only checking logs manually after suspicion.** Important changes need proactive alerts.

## Practical labs

Use a sandbox account.

### Cloud logging baseline

```
Audit logs enabled:
Regions covered:
Data events enabled:
Retention:
Protected storage:
Alert destinations:
Owner:
```

This is a prerequisite for meaningful cloud labs.

### Create safe detection rules

```
Rule: new access key created
Rule: public storage policy changed
Rule: security group opened to world
Rule: logging disabled
Rule: admin policy attached
```

Use harmless test changes and revert them.

### Incident timeline practice

```
Time:
Principal:
API/action:
Resource:
Source IP:
Expected/Unexpected:
Response:
```

Practice reading audit logs before you need them.

### Build a minimum alert matrix

```
event | why it matters | alert owner | expected false positives | response
new admin policy | privilege expansion | platform | deployments | confirm ticket or revert
public storage | data exposure | app owner | static sites | classify bucket
logging disabled | evidence loss | security | none | investigate immediately
```

Alerts need owners and expected interpretation, not just event names.

### Check log tamper resistance

```
who can disable logs:
who can delete log storage:
retention:
immutability/versioning:
break-glass path:
```

Logs in the same blast radius as attackers are weak evidence.

## Practical examples

- An access key is created for a dormant user.
- A bucket policy is changed to public read.
- A security group is opened to `0.0.0.0/0`.
- CloudTrail or audit logging is disabled.
- A workload role reads secrets it never normally accesses.

## Related notes

- [[cloud-security-basics]]
- [[cloud-iam-boundaries]]
- [[public-cloud-storage-exposure]]
- [[cloud-network-boundaries]]
- [[external-attack-surface|External Attack Surface]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

### Suggested future atomic notes

- cloud-detection-rules
- cloud-log-retention
- cloudtrail-event-analysis
- guardduty-findings
- cloud-flow-logs-and-network-detection

## References

- **Official Docs:** AWS CloudTrail security best practices — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html
- **Official Docs:** Google Cloud Audit Logs — https://cloud.google.com/logging/docs/audit
- **Official Docs:** Microsoft Defender for Cloud — https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-cloud-introduction
