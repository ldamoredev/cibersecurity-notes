---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Lab Infrastructure

## Definition

Cloud lab infrastructure is a deliberately isolated, budget-limited, and disposable cloud environment for learning, testing, and building security exercises.

## Why it matters

Cloud labs are useful because they let you practice real hosting, SSH, DNS, TLS, storage, IAM, and logging. They are also risky because mistakes can expose services, leak credentials, or generate cost.

The safe lab mindset is: isolate first, grant least privilege, log early, budget hard, and tear down intentionally.

## How it works

A safe cloud lab has **6 guardrails**:

1. **Separate account/project/subscription.** Labs should not touch production or personal critical assets.
2. **Budget and alerts.** Spending limits and notifications exist before resources are created.
3. **Least-privilege identity.** Daily lab work avoids root or global admin.
4. **Minimal network exposure.** Only required ports are reachable, preferably from known IPs.
5. **Logging baseline.** Audit logs exist before experiments.
6. **Teardown plan.** Every resource has an owner and removal date.

The bug in many labs is not the vulnerable exercise. It is the uncontrolled cloud environment around it.

A worked example, safe lab boundary:

```
Goal:
  practice SSH + HTTPS + DNS on one VM

Sandbox:
  separate account, budget alert at low spend, no production peering

Identity:
  daily user can create one VM and one DNS record, not administer IAM broadly

Network:
  SSH limited to current home IP, HTTPS public

Teardown:
  VM, disk, static IP, DNS record, key pair, and cert renewal all listed

Decision:
  lab is acceptable because cost, identity, exposure, and cleanup boundaries are explicit
```

Cloud labs should be designed like temporary production systems with a smaller blast radius.

## Techniques / patterns

Build labs around:

- one provider and one region at a time
- a sandbox account/project with billing alerts
- tagged resources for cleanup
- read-only inventory commands before changes
- SSH keys, not passwords
- explicit security groups/firewall rules
- snapshots and buckets treated as sensitive

## Variants and bypasses

Cloud labs fail in **4 common ways**.

### 1. Shared account lab

Experiments run in the same account as real workloads.

### 2. Public-by-default lab

VMs, buckets, or dashboards are reachable from the internet without review.

### 3. No-cost-control lab

Resources keep running after the exercise.

### 4. Secret-sprawl lab

Keys are copied into notes, repos, shell history, or images.

## Impact

Ordered roughly by severity:

- **Credential exposure.** Lab keys can become real account access.
- **Unexpected internet exposure.** Public services may be indexed or attacked.
- **Cost spikes.** Compute, bandwidth, storage, and snapshots can persist.
- **Bad habits.** Unsafe lab patterns transfer into production.

## Detection and defense

Ordered by effectiveness:

1.
**Use a dedicated sandbox boundary.**
   Separation prevents lab mistakes from becoming production incidents.

2.
**Create budget alerts before compute.**
   Cost controls are preventive only when they exist before resources are created.

3.
**Use tags and teardown checklists.**
   Cleanup is easier when every resource carries owner, purpose, and expiry metadata.

4.
**Restrict inbound access by default.**
   SSH, admin panels, databases, and dashboards should not be world-reachable unless the lab requires it.

5.
**Store secrets in provider secret stores or local password managers.**
   Lab convenience should not normalize plaintext keys in files.

### What does not work as a primary defense

- **Trusting free-tier marketing.** Free tiers have limits and exceptions.
- **Relying on memory to clean up.** Resources persist longer than attention.
- **Using root credentials for convenience.** Root/admin access makes every mistake bigger.
- **Publishing lab IPs and keys in notes.** Obsidian notes are not a secret store.

## Practical labs

Use only a sandbox account.

### Create a lab preflight

```
Provider:
Account/project:
Budget alert:
Region:
Admin identity:
Daily identity:
Logging enabled:
Teardown date:
```

Do this before creating compute.

### Tag resources

```
owner=ldamore
purpose=cloud-security-lab
expires=2026-05-06
environment=lab
```

Tags make cleanup and cost review possible.

### Teardown review

```
Instances:
Volumes:
Snapshots:
Buckets:
Elastic/static IPs:
DNS records:
Secrets:
Logs retained:
```

Run this at the end of every lab.

### Create a cost kill-switch checklist

```
Budget alert configured:
Compute quotas checked:
Auto-scaling disabled or capped:
Static IP inventory:
Snapshots/volumes reviewed:
Teardown calendar reminder:
```

Cost safety is a security control in disposable cloud labs.

### Review lab identity permissions

```
Action needed | Permission granted | Broader than needed? | Safer alternative
create VM      | compute admin      | yes                 | scoped VM role
edit DNS       | DNS zone admin     | acceptable          | limited hosted zone
```

Lab users should not normalize broad admin permissions.

## Practical examples

- A forgotten VM keeps billing for a month.
- A static IP remains allocated after the instance is deleted.
- A lab bucket becomes public during a test and is not reverted.
- A key pair is copied into a markdown note.
- Budget alerts catch an accidental resource loop.

## Related notes

- [[cloud-security-basics]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-logging-and-detection]]
- [[cloud-secrets-management]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- build-safe-cloud-lab
- cloud-cost-security
- cloud-tagging-strategy
- cloud-account-organization

## References

- **Official Docs:** AWS Free Tier — https://aws.amazon.com/free/
- **Official Docs:** AWS Budgets — https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- **Official Docs:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
