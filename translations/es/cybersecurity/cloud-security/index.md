# Índice de Cloud Security

## Propósito

Este índice es el punto de entrada raíz de la rama cloud-security del vault de ciberseguridad.

Usalo para:
- entender el cloud como límites de identidad, red, almacenamiento, metadatos, logging y costos
- construir labs de cloud seguros sin exposición accidental ni gasto descontrolado
- mapear malas configuraciones de cloud hacia superficie de ataque y controles defensivos
- separar la seguridad del dominio objetivo en cloud del flujo de entrega DevSecOps

Usá [[reference-registry-cloud-security|Reference Registry — Cloud Security]] como fuente de verdad para las referencias de esta rama.
Volvé a [[index|Cybersecurity Index]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Foundations]] (Fase 0).
> - [[index|Networking]] (especialmente DNS, TLS, reverse proxies).
> - [[index|Cryptography]] para razonamiento sobre IAM/keys/secrets.

---

## Orden de aprendizaje recomendado

### Fase 1 — Modelo cloud y labs seguros

1. [[cloud-security-basics]]
2. [[cloud-lab-infrastructure]]

### Fase 2 — Acceso y administración

1. [[cloud-iam-boundaries]]
2. [[ssh-access-to-cloud-hosts]]
3. [[cloud-secrets-management]]

### Fase 3 — Exposición y alcanzabilidad

1. [[cloud-network-boundaries]]
2. [[cloud-metadata-security]]
3. [[public-cloud-storage-exposure]]
4. [[cloud-dns-and-certbot]]

### Fase 4 — Visibilidad y respuesta

1. [[cloud-logging-and-detection]]

---

## Cluster central de Cloud Security

### Madurez de la rama

Esta rama es profunda y madura a partir del 2026-04-30.

Las 10 notas atómicas siguen la plantilla canónica de 11 secciones, incluyen labs prácticos y llevan ejemplos trabajados que conectan la configuración del provider con decisiones de identidad, red, datos, metadatos, logging, costos y teardown.

### Fundamentos y labs

- [[cloud-security-basics]]
- [[cloud-lab-infrastructure]]

### Identidad y secretos

- [[cloud-iam-boundaries]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-secrets-management]]

### Exposición y límites de red

- [[cloud-network-boundaries]]
- [[cloud-metadata-security]]
- [[public-cloud-storage-exposure]]
- [[cloud-dns-and-certbot]]

### Detección

- [[cloud-logging-and-detection]]

---

## Cross-links a otras ramas

### Networking

- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS and HTTPS]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Mapeo de superficie de ataque

- [[external-attack-surface|External Attack Surface]]
- [[exposed-storage|Exposed Storage]]
- [[admin-interface-discovery|Admin Interface Discovery]]
- [[third-party-exposure|Third-Party Exposure]]

### DevSecOps

- [[secrets-management|Secrets Management]]
- [[container-security|Container Security]]
- [[ci-cd-hardening|CI/CD Hardening]]

---

## Notas futuras sugeridas

- IaC Security
- cloud-asset-inventory
- cloud-tagging-strategy
- cloud-kms-boundaries
- cloud-container-security
- cloud-serverless-security
- cloud-iam-policy-analysis
- cloud-account-organization
- cloud-cost-security

### Posibles playbooks futuros

- build-safe-cloud-lab
- audit-public-cloud-storage
- review-cloud-iam-risk
- trace-cloud-metadata-exposure
- cloud-logging-baseline

---

## Notas de mantenimiento de la rama

- Manté el comportamiento de servicios cloud y el diseño de controles del provider en esta rama.
- Manté las mecánicas genéricas de TCP/IP, DNS, TLS y metadatos en [[index]].
- Manté los controles de CI/CD, dependencias, build y releases en [[index]].
- Los labs de cloud deberían incluir presupuesto, least privilege, teardown y verificaciones de exposición.
- Usá wikilinks no resueltos para notas atómicas futuras para que Obsidian pueda rastrear la expansión de la rama.
- Mantené el patrón de decisión cloud: cada nota debería mostrar cómo una configuración del provider afecta el blast radius, la propiedad, la evidencia y la próxima acción segura.

## Referencias

- **Fundamental:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Fundamental:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Fundamental:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/
