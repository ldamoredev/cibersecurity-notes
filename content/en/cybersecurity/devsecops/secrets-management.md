---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Secrets Management

## Definition

Secrets management is the secure handling of credentials, tokens, keys, certificates, and other sensitive material across development, build, deployment, and runtime.

## Why it matters

Secrets frequently bridge trust boundaries between source control, CI/CD, infrastructure, and production. Weak handling turns local convenience into systemic compromise.
This note is about the lifecycle and exposure of sensitive material itself, not the whole CI/CD environment or release-governance model around it.

## Attacker perspective

Attackers look for:
- secrets in source control
- credentials in CI logs
- long-lived tokens in environment variables
- overprivileged secrets reused across systems
- stale secrets that were never rotated

## Defender perspective

Defenders should:
- minimize where secrets exist
- separate build-time and runtime secrets
- rotate and scope secrets intentionally
- reduce human handling of secrets
- review exposure in logs, artifacts, and config

## Practical examples

- a deploy token is printed in logs
- the same long-lived credential is reused across environments
- repo history still contains secrets that teams assume are “gone”

## Related notes

- [[ci-cd-hardening]]
- [[supply-chain-security]]
- [[artifact-integrity]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
