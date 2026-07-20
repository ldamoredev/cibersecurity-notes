---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Recon to Testing Handoff

## Definition

Recon-to-testing handoff is the transition from discovery and validation into focused security testing, with enough context to choose the right next activity instead of probing blindly.

## Why it matters

Recon without handoff becomes a pile of findings. The real value comes when discovery narrows into clear next steps: access control testing, API review, SSRF assessment, admin interface review, version drift analysis, storage exposure review, or bug bounty reporting.

This note is where discovery becomes testing strategy.

## How it works

A useful handoff contains **6 fields**:

1. **Asset.** Host, route, service, API, storage object, or vendor surface.
2. **Evidence.** How it was found and what proves it is live/relevant.
3. **Scope.** Ownership, authorization status, environment, and limits.
4. **Risk hypothesis.** What might be wrong and why.
5. **Next test.** Specific playbook or concept to apply.
6. **Stop condition.** What result proves the hypothesis false or enough for reporting.

The bug is not incomplete recon. The operational failure is handing off vague leads that cannot be tested or remediated.

A worked example, good handoff:

```
Asset:
  https://api-preview.example.test/api/v1/users/{id}

Evidence:
  found in JS bundle, host live, normal user can read own object

Scope:
  *.example.test included; preview environment allowed; use test account only

Risk hypothesis:
  object-level authorization may trust the path ID

Next test:
  BOLA/IDOR test with two owned test accounts

Stop condition:
  if cross-user object access is denied consistently across GET/PATCH/DELETE, record negative result
```

This is stronger than "found API endpoint, test auth" because it names evidence, scope, method, and stop condition.

## Techniques / patterns

Practitioners hand off:

- endpoint discovery into API inventory, BOLA, BFLA, and BOPLA testing
- admin surfaces into access-control and auth review
- URL fetchers into SSRF testing
- old versions into version-drift and response-diff testing
- storage into access-control and sensitive-data review
- stack fingerprints into targeted configuration checks
- OSINT clues into scope validation, not immediate exploitation

## Variants and bypasses

Handoffs fall into **6 routes**.

### 1. Access-control handoff

Object IDs, admin routes, roles, tenants, or workflow actions.

### 2. API handoff

Versions, schemas, endpoints, parameters, tokens, fields, and rate limits.

### 3. Server-side handoff

URL fetchers, uploads, parsers, file paths, deserialization, and command execution surfaces.

### 4. Exposure-drift handoff

Staging, deprecated versions, stale DNS, direct origins, and storage.

### 5. Infrastructure handoff

Ports, services, admin tools, metadata, cloud, and vendor surfaces.

### 6. Reporting handoff

Validated evidence becomes a clear bug bounty or internal report.

## Impact

Ordered roughly by severity:

- **Higher-quality testing.** The right playbook is applied to the right target.
- **Better bug reports.** Evidence and scope are preserved.
- **Less noise.** Dead leads and off-scope assets are filtered before testing.
- **Faster remediation.** Owners receive clear assets, impact hypotheses, and next steps.
- **Knowledge compounding.** Handoffs become reusable playbooks and atomic notes.

## Detection and defense

Ordered by effectiveness:

1.
**Use a structured handoff template.**
   Asset, evidence, scope, risk hypothesis, next test, and stop condition prevent vague work.

2.
**Require scope and validation before intrusive testing.**
   Handoff should not launder uncertain assets into active exploitation.

3.
**Link to concept notes and playbooks.**
   This keeps testing repeatable and grounded.

4.
**Preserve negative results.**
   "Denied correctly" and "not in scope" prevent repeated dead work.

5.
**Turn repeated handoffs into playbooks.**
   If a handoff happens often, it deserves a procedure.

### What does not work as a primary defense

- **Huge recon dumps.** Lists without context do not guide testing.
- **Jumping from discovery to exploitation.** Validate scope, ownership, and hypothesis first.
- **Reporting without reproducibility.** Evidence and commands matter.
- **Treating every route as the same test.** Different surfaces imply different vulnerability classes.

## Practical labs

Use an owned app or lab.

### Write a handoff card

```
Asset:
Evidence:
Scope:
Risk hypothesis:
Next test:
Stop condition:
Related notes:
```

Do this before starting manual testing.

### Route findings to test classes

```
/api/users/{id}           -> BOLA / IDOR
/admin/export             -> BFLA / access control
?url=https://...          -> SSRF
/api/v1/users/me          -> deprecated version diff
public bucket             -> exposed storage
```

The route-to-test mapping is the core skill.

### Preserve a negative result

```
Finding: /admin exists
Test: normal user receives 403 on GET/POST/PATCH
Result: no BFLA evidence; monitor as exposed admin surface
```

Negative results reduce future noise.

### Create a bug-report skeleton from handoff

```
Title:
Asset:
Scope evidence:
Steps to reproduce:
Expected result:
Actual result:
Impact:
Remediation idea:
Evidence files:
```

If the handoff cannot become this skeleton, it probably needs more validation.

### Route no-action findings

```
lead | reason no action | evidence | revisit trigger
```

No-action decisions are useful when they preserve why testing stopped.

## Practical examples

- Endpoint discovery leads into API inventory and BOLA testing.
- A found admin interface leads into access-control and auth testing.
- An exposed metadata-capable internal path leads into SSRF review.
- A deprecated version leads into response-field diffing.
- A storage bucket leads into sensitive data and policy review.

## Related notes

- [[enumeration]]
- [[service-validation]]
- [[scope-validation]]
- [[endpoint-discovery|Endpoint Discovery]]
- [[api-inventory-management|API Inventory Management]]
- [[exploit-idor|Exploit IDOR]]
- [[investigate-ssrf|Investigate SSRF]]

### Suggested future atomic notes

- bug-bounty-reporting
- recon-finding-triage
- test-selection-from-recon
- evidence-quality-for-reports
- bug-bounty-recon-loop

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
