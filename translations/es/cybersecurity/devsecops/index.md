# Índice de DevSecOps

## Propósito

Este índice es el punto de entrada raíz para la rama DevSecOps del vault de ciberseguridad.

Usalo para:
- conectar desarrollo seguro, CI/CD, dependency risk, manejo de secrets y delivery de containers
- razonar sobre riesgo de software antes de runtime
- mapear controles de seguridad dentro del workflow developer en vez de atornillarlos después
- convertir ideas secure-by-design en prácticas de ingeniería

Usá [[reference-registry-devsecops|Reference Registry — DevSecOps]] como fuente de verdad para referencias en esta rama.
Volvé a [[index|Índice de ciberseguridad]] para navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[index|Web Security]] y [[index|Cryptography]] — las amenazas de build-pipeline heredan ambas.

---

## Orden de aprendizaje recomendado

### Fase 1 — Fundamentos de desarrollo seguro

1. [[nist-ssdf]]
2. [[secure-by-design]]
3. [[asvs-as-dev-process-input]]

### Fase 2 — Supply chain y dependencias

1. [[supply-chain-security]]
2. [[dependency-risk]]
3. [[artifact-integrity]]

### Fase 3 — Pipeline y controles de release

1. [[ci-cd-hardening]]
2. [[branch-protection-and-release-controls]]
3. [[secrets-management]]

### Fase 4 — Containers y build delivery

1. [[container-security]]
2. [[image-scanning]]
3. [[sbom-and-provenance]]

---

## Cluster DevSecOps core

### Fundamentos

- [[nist-ssdf]]
- [[secure-by-design]]
- [[asvs-as-dev-process-input]]

### Supply chain

- [[supply-chain-security]]
- [[dependency-risk]]
- [[artifact-integrity]]
- [[sbom-and-provenance]]

### Pipelines y releases

- [[ci-cd-hardening]]
- [[branch-protection-and-release-controls]]
- [[secrets-management]]

### Containers y delivery

- [[container-security]]
- [[image-scanning]]

---

## Cross-links a otras ramas

### API security

- [[api-inventory-management]]
- [[broken-authentication]]
- [[jwt-attacks]]

### Web security

- [[file-upload-abuse]]
- [[broken-access-control]]
- [[request-smuggling]]

### Attack surface mapping

- [[exposed-storage]]
- [[third-party-exposure]]
- [[deprecated-api-versions]]

### Cloud security

- [[cloud-security-basics|Cloud Security Basics]]
- [[cloud-secrets-management|Cloud Secrets Management]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[cloud-lab-infrastructure|Cloud Lab Infrastructure]]

### Security playbooks

- [[inspect-file-upload-surface]]
- [[reverse-proxy-misconfig-checklist]]

---

## Futuras notas sugeridas

- iac-security
- policy-as-code
- build-isolation
- signed-releases
- dependency-confusion
- secret-scanning
- runtime-vs-build-time-controls

### Posibles playbooks futuros

- leak-secrets-from-ci
- inspect-ci-secrets-exposure
- review-container-hardening
- inspect-release-provenance
- test-dependency-risk-hotspots

## Notas de mantenimiento de rama

- Mantené controles de CI/CD, dependencias, build, release y software-delivery en esta rama.
- Mantené identidad de cloud provider, red, storage, metadata, logging y controles de lab-infrastructure en [[index|Cloud Security]].

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
