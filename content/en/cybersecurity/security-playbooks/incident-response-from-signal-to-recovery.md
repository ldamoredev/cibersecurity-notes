---
kind: incident
level: intermediate
status: current
perspective: defense
last_verified: 2026-07-19
---

# Incident response from signal to recovery

## Scenario and initial signal

This tabletop uses the local cross-tenant access fixture. A detection reports
unusual authorization decisions with correlation IDs. Treat the alert as a
claim to investigate, not proof of compromise.

## Triage, scope, and evidence

Confirm data source health, preserve relevant structured logs, and establish a
timeline using correlation IDs, principals, tenants, code version, and policy
version. Scope affected objects and identities without collecting unrelated
personal data. Record uncertainty explicitly.

## Containment, eradication, and recovery

Contain by disabling or restricting the affected fixture identity and feature
path. Eradicate the root cause by enforcing server-side object authorization.
Recover by validating fixture data integrity, restoring normal access under the
fixed policy, and monitoring the same evidence channel. Do not declare recovery
until the regression test and detection test pass.

## Lessons and detection improvement

Document which assumption failed, whether telemetry supported the decision,
what false positives occurred, and which policy or test would have prevented
the incident. Update the threat model and exercise the tabletop again after
the change.

## Sources

- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [CISA Incident Response Playbooks](https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks)
