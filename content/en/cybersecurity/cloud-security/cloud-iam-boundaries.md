---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud IAM Boundaries

## Definition

Cloud IAM boundaries are the identity, role, policy, trust, and organization controls that decide which cloud principals can perform which actions on which resources.

## Why it matters

Cloud environments are controlled by APIs, and APIs are controlled by identity. Overprivileged users, service accounts, instance roles, or cross-account trusts can turn a small foothold into full account control.

The important mental model is not "who logged in." It is "which principal can call which API under which conditions."

## How it works

Cloud IAM has **5 decision inputs**:

1. **Principal.** User, role, group, service account, workload identity, or external identity.
2. **Action.** The API operation being requested.
3. **Resource.** The object, service, account, project, subscription, or scope.
4. **Condition.** Context such as MFA, IP, tags, time, device, or organization.
5. **Trust path.** Assumption, impersonation, federation, or delegation relationships.

The bug is usually not one policy line in isolation. It is the effective permission graph created by identity plus trust plus resource policies.

A worked example, harmless-looking role path:

```
Principal:
  ci-deploy-role

Direct permissions:
  update function code, pass role app-runtime-role

Trust:
  CI provider can assume ci-deploy-role

Hidden escalation:
  if ci-deploy-role can pass a more privileged runtime role, deployment becomes privilege expansion

Decision:
  review iam:PassRole / service-account impersonation paths, not only obvious admin policies
```

IAM maturity is understanding what a principal can become, not just what it can do directly.

## Techniques / patterns

Reviews look at:

- root/admin usage and MFA status
- long-lived access keys
- wildcard actions and resources
- role assumption and service account impersonation
- external identities and cross-account trusts
- workload identities attached to compute
- unused identities and stale permissions

## Variants and bypasses

IAM failures have **5 common forms**.

### 1. Direct overpermission

An identity has more actions than its job requires.

### 2. Privilege escalation path

A principal can modify policies, pass roles, create keys, or assume stronger identities.

### 3. Confused trust

Cross-account, external, or federated access trusts the wrong party or condition.

### 4. Workload role abuse

A compromised VM, container, or function can use its attached identity.

### 5. Stale identity

Old users, service accounts, and keys remain valid after their purpose ended.

## Impact

Ordered roughly by severity:

- **Account takeover.** Admin-equivalent permissions can persist, exfiltrate, or destroy resources.
- **Data access.** IAM grants direct reads to storage, databases, logs, and secrets.
- **Persistence.** Attackers can create keys, users, roles, or policy backdoors.
- **Lateral movement.** Trust relationships bridge accounts, projects, and workloads.
- **Audit evasion.** Some permissions can disable or alter logging.

## Detection and defense

Ordered by effectiveness:

1.
**Design least privilege around tasks.**
   Smaller permissions reduce both accidental and malicious blast radius.

2.
**Remove long-lived credentials where possible.**
   Federation and short-lived role credentials are easier to revoke and monitor.

3.
**Require MFA and strong conditions for privileged actions.**
   Conditions make identity decisions depend on context, not only possession of a credential.

4.
**Analyze effective permissions and escalation paths.**
   Policy review must include trust, resource policies, and role-passing behavior.

5.
**Review unused identities and keys.**
   Stale access is quiet risk.

### What does not work as a primary defense

- **Naming a role `readonly`.** The effective policy matters, not the label.
- **One admin role for all automation.** It destroys blast-radius control.
- **Deleting users but leaving keys or roles.** Cloud access may survive through other principals.
- **Manual review of huge policies only.** Effective permissions need tooling and queries.

## Practical labs

Use a sandbox account and read-only checks where possible.

### Build an IAM inventory table

```
Principal | Type | Purpose | Privilege level | Last used | Credential type | Owner
```

The goal is to see identity sprawl.

### Review wildcard permissions

```
Policy:
Wildcard action:
Wildcard resource:
Condition:
Business reason:
Safer scope:
```

Wildcards need explicit justification.

### Map a trust path

```
Principal A can assume/impersonate:
Target role/service account:
Conditions:
Resulting permissions:
Escalation risk:
```

Trust paths are often where IAM becomes surprising.

### Review role-passing and impersonation

```
Principal | Can pass/impersonate | To service | Target permissions | Justified? | Condition
```

Role-passing is one of the most important cloud privilege-boundary checks.

### Build a stale credential queue

```
principal | key/service-account credential | last used | owner | rotate/delete | risk
```

Unused credentials should become deletion candidates, not permanent exceptions.

## Practical examples

- A CI role can attach administrator policies.
- A VM role can read all storage buckets.
- A contractor user keeps access after offboarding.
- A service account key is stored in a repository.
- A cross-account trust lacks a strong external condition.

## Related notes

- [[cloud-security-basics]]
- [[cloud-metadata-security]]
- [[cloud-secrets-management]]
- [[cloud-logging-and-detection]]
- [[broken-function-level-authorization|Broken Function-Level Authorization]]

### Suggested future atomic notes

- cloud-iam-policy-analysis
- cloud-service-account-keys
- cloud-role-assumption
- cloud-privilege-escalation-paths

## References

- **Official Docs:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Official Docs:** Google Cloud IAM best practices — https://cloud.google.com/iam/docs/using-iam-securely
- **Official Docs:** Microsoft Entra security operations for privileged accounts — https://learn.microsoft.com/en-us/entra/architecture/security-operations-privileged-accounts
