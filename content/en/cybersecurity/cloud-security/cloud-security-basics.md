---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Security Basics

## Definition

Cloud security is the discipline of protecting cloud-hosted identities, resources, networks, data, workloads, logs, and control-plane operations.

## Why it matters

Cloud changes the security model because infrastructure becomes API-driven. A single identity permission, public storage rule, exposed security group, leaked key, or metadata path can create broad impact.

The core idea is shared responsibility: the provider secures the underlying cloud, while the customer still owns configuration, identity, data, workloads, access, and monitoring decisions.

## How it works

Cloud security has **6 control planes**:

1. **Identity.** Users, roles, service accounts, and policies decide who can do what.
2. **Network.** VPCs, subnets, security groups, firewalls, and routes decide reachability.
3. **Data.** Storage permissions, encryption, retention, and sharing decide exposure.
4. **Compute.** Instances, containers, functions, and images run workloads.
5. **Metadata and secrets.** Workloads often receive credentials through platform channels.
6. **Logging.** Audit trails and detections decide whether risky changes are visible.

There is no single cloud vulnerability payload. Most cloud failures are control-plane misconfigurations or identity paths that make dangerous actions possible.

A worked example, cloud risk as combined boundaries:

```
Resource:
  lab-web-01 VM

Identity:
  attached role can read all object storage

Network:
  SSH open to 0.0.0.0/0 and HTTPS public

Data:
  app writes exports to a private bucket

Logging:
  control-plane logs enabled, storage data events disabled

Decision:
  the immediate risk is not "a VM exists"; it is public admin reachability plus broad workload identity
  plus incomplete data-access visibility
```

Cloud security maturity comes from reading identity, network, data, compute, secrets, and logs together.

## Techniques / patterns

Cloud reviews look at:

- account/project/subscription structure
- administrator and workload identities
- public IPs, open security groups, and exposed admin ports
- object storage public access and cross-account sharing
- instance metadata configuration
- secrets in environment variables, repos, images, and CI/CD
- audit logging, alerting, and retention

## Variants and bypasses

Cloud risk has **5 recurring shapes**.

### 1. Overprivileged identity

An identity can perform actions far beyond its job.

### 2. Public exposure

Storage, hosts, admin panels, or APIs are reachable from the internet.

### 3. Credential leakage

Keys, tokens, or role credentials escape into code, logs, images, or metadata abuse.

### 4. Boundary confusion

Teams misunderstand VPCs, security groups, accounts, projects, or shared responsibility.

### 5. Invisible change

Risky configuration changes happen without useful logs or alerts.

## Impact

Ordered roughly by severity:

- **Account compromise.** Identity abuse can create new users, roles, keys, and persistence.
- **Data exposure.** Public or cross-account storage can leak sensitive data.
- **Workload compromise.** Exposed hosts or metadata access can lead to credentials.
- **Lateral movement.** One role or subnet can reach other services.
- **Runaway cost.** Compromise can create expensive resources.

## Detection and defense

Ordered by effectiveness:

1.
**Design least-privilege identity first.**
   Cloud control planes are identity-driven. Narrow permissions reduce the blast radius of every other mistake.

2.
**Keep public exposure intentional and inventoried.**
   Public IPs, buckets, load balancers, and admin ports should have owners, reasons, and review dates.

3.
**Segment accounts, networks, and environments.**
   Production, dev, labs, and personal experiments should not share one flat trust boundary.

4.
**Enable audit logs before experiments.**
   Logs are most useful when they exist before the risky event.

5.
**Set budgets and teardown habits.**
   Cloud security includes cost safety because resource creation is part of the attack surface.

### What does not work as a primary defense

- **Assuming provider-managed means provider-secured.** Customer configuration still matters.
- **Using one admin account for everything.** Convenience becomes blast radius.
- **Relying only on private IPs.** SSRF, peering, VPNs, and compromised workloads can cross "private" boundaries.
- **Turning on logs after an incident.** Missing history cannot be reconstructed.

## Practical labs

Use a personal sandbox account with no production access.

### Draw the shared-responsibility split

```
Provider owns:
Customer owns:
Ambiguous/shared:
Evidence source:
```

Apply it to one service such as object storage, VM compute, or managed database.

### Build a cloud risk inventory

```
Identity:
Public endpoints:
Storage:
Compute:
Secrets:
Logs:
Budget:
Teardown date:
```

Keep the first lab boring and safe.

### Identify public resources

```
Public IPs:
Public buckets:
Public DNS names:
Open admin ports:
Owner:
Reason:
```

This turns cloud concepts into attack-surface evidence.

### Build a six-plane risk card

```
Resource:
Identity risk:
Network risk:
Data risk:
Compute risk:
Metadata/secrets risk:
Logging risk:
Top next action:
```

Use this when a cloud finding feels too broad to triage.

### Separate provider and customer controls

```
Control | Provider responsibility | Customer responsibility | Evidence
IAM role design | no | yes | policy review
physical datacenter access | yes | no | provider docs
bucket public policy | no | yes | storage config
```

Shared responsibility becomes useful only when mapped to concrete controls.

## Practical examples

- A lab VM exposes SSH to the internet with no IP restriction.
- A public bucket contains backups thought to be internal.
- A CI role can create admin policies.
- A compromised instance reads role credentials from metadata.
- CloudTrail or audit logs were never enabled in a small account.

## Related notes

- [[cloud-iam-boundaries]]
- [[cloud-network-boundaries]]
- [[public-cloud-storage-exposure]]
- [[cloud-metadata-security]]
- [[external-attack-surface|External Attack Surface]]

### Suggested future atomic notes

- cloud-asset-inventory
- cloud-account-organization
- cloud-cost-security
- cloud-tagging-strategy

## References

- **Foundational:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Foundational:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Foundational:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/
