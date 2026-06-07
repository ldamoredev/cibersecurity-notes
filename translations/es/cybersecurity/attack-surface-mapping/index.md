# Índice de Attack Surface Mapping

## Propósito

Este índice es el punto de entrada raíz de la rama attack-surface-mapping del vault de ciberseguridad.

Usalo para:
- mapear qué está realmente expuesto, alcanzable y descubrible
- conectar networking, web-security, api-security y reconocimiento en una vista operacional única
- razonar sobre la deriva de exposición, activos olvidados y puntos de entrada no documentados
- convertir supuestos de arquitectura en superficie de ataque observable

Usá [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]] como fuente de verdad para las referencias de esta rama.
Volvé a [[index|Cybersecurity Index]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Foundations]] (Fase 0).
> - [[index|Networking]] — no podés mapear lo que no podés razonar.

---

## Orden de aprendizaje recomendado

### Fase 1 — Modelo de superficie y marco conceptual

1. [[attack-surface-mapping]]
2. [[external-attack-surface]]
3. [[internal-attack-surface]]

### Fase 2 — Triaje y descubrimiento

1. [[exposed-service-triage|Exposed Service Triage]]
2. [[endpoint-discovery]]
3. [[admin-interface-discovery]]

### Fase 3 — Clases de exposición específicas

1. [[subdomain-takeover|Subdomain Takeover]]
2. [[exposed-storage]]
3. [[deprecated-api-versions]]
4. [[third-party-exposure]]

---

## Cluster central de Attack Surface Mapping

### Madurez de la rama

Esta rama es profunda y madura a partir del 2026-04-29.

Las 10 notas atómicas siguen la plantilla canónica de 11 secciones, incluyen labs prácticos y llevan ejemplos trabajados que convierten descubrimientos crudos en decisiones de exposición.

### Marco conceptual

- [[attack-surface-mapping]]
- [[external-attack-surface]]
- [[internal-attack-surface]]

### Triaje y descubrimiento

- [[exposed-service-triage|Exposed Service Triage]]
- [[endpoint-discovery]]
- [[admin-interface-discovery]]

### Clases de exposición específicas

- [[subdomain-takeover|Subdomain Takeover]]
- [[exposed-storage]]
- [[deprecated-api-versions]]
- [[third-party-exposure]]

---

## Cross-links a otras ramas

### Networking

- [[dns-resolution]]
- [[dns-security]]
- [[ports-and-services]]
- [[nmap-scanning]]
- [[reverse-proxies]]
- [[load-balancers]]

### Web Security

- [[ssrf]]
- [[broken-access-control]]
- [[path-traversal]]
- [[cors-misconfiguration]]

### API Security

- [[api-inventory-management]]
- [[api-security-top-10]]
- [[authorization]]

### Cloud Security

- [[cloud-security-basics|Cloud Security Basics]]
- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[public-cloud-storage-exposure|Public Cloud Storage Exposure]]
- [[cloud-metadata-security|Cloud Metadata Security]]

### Reconocimiento

- [[passive-recon]]
- [[active-recon]]
- [[public-asset-discovery]]
- [[enumeration]]

---

## Notas futuras sugeridas

- health-check-endpoints
- staging-environments
- shadow-it-exposure
- asset-ownership-model
- schema-exposure
- internet-exposure-reduction
- hidden-parameter-discovery
- cloud-asset-inventory
- direct-origin-exposure
- source-map-exposure
- oauth-redirect-uri-inventory
- public-object-storage-review

### Posibles playbooks futuros

- map-public-attack-surface
- enumerate-admin-interfaces
- [[trace-metadata-endpoint-reachability]]
- inspect-api-version-drift

---

## Notas de mantenimiento de la rama

- Usá [[reference-registry-attack-surface-mapping]] antes de agregar referencias.
- Mantené las notas de attack surface enfocadas en exposición, descubribilidad, ownership, deriva del ciclo de vida y alcanzabilidad.
- No dupliques notas de flujo de reconocimiento de [[index]]; enlazalas.
- Los temas cloud de dominio objetivo ahora viven en [[index|Cloud Security]]. Mantené esta rama enfocada en exposición observable y enlazá a las notas cloud para controles específicos del provider.
- Mantené el patrón de ejemplo trabajado: cada nota debería mostrar cómo una pista cruda se convierte en una decisión de exposición con scope, no solo un artefacto de descubrimiento.

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Investigación / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
