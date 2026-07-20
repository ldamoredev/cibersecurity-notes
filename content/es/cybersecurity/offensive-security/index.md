# Índice de Seguridad Ofensiva / Recon

## Propósito

Este índice es el punto de entrada raíz para la rama de seguridad ofensiva / recon del atlas de ciberseguridad.

Usalo para:
- estructurar el pensamiento de descubrimiento y enumeración al estilo atacante
- separar los flujos de trabajo de passive recon, active recon, enumeration y validación
- conectar el reconnaissance con el mapeo de superficie de ataque, seguridad web y seguridad de APIs
- construir una mentalidad de operador repetible en lugar de scanning ad hoc

Usá el [[reference-registry-offensive-security|Registro de Referencias — Seguridad Ofensiva]] como fuente de verdad para las referencias de esta rama.
Volvé al [[index|Índice de Ciberseguridad]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[index|Redes]] — el sustrato que sondea cada técnica de recon.
> - [[index|Mapeo de Superficie de Ataque]] — el recon convierte la superficie en evidencia.
> - **Pareá cada nota con su contraparte de [[index|Detection Engineering]].**

---

## Orden de aprendizaje recomendado

### Fase 1 — Fundamentos de recon

1. [[recon|Recon]]
2. [[passive-recon|Passive Recon]]
3. [[active-recon|Active Recon]]

### Fase 2 — Descubrimiento de assets y tecnología

1. [[public-asset-discovery|Descubrimiento de Assets Públicos]]
2. [[company-mapping|Company Mapping]]
3. [[tech-stack-fingerprinting|Tech Stack Fingerprinting]]

### Fase 3 — Enumeration operacional

1. [[enumeration|Enumeration]]
2. [[subdomain-enumeration|Subdomain Enumeration]]
3. [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]

### Fase 4 — Validación y transición al testing

1. [[scope-validation|Validación de Scope]]
2. [[service-validation|Validación de Servicios]]
3. [[recon-to-testing-handoff|Handoff de Recon a Testing]]
4. [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

---

## Cluster principal ofensivo / recon

### Madurez de la rama

Esta rama es de madurez profunda a partir de 2026-04-29.

Las 12 notas atómicas siguen la plantilla canónica de 11 secciones, incluyen labs prácticos y ahora llevan ejemplos trabajados que convierten pistas descubiertas en evidencia validada, decisiones de scope y handoffs de testing.

### Fundamentos

- [[recon|Recon]]
- [[passive-recon|Passive Recon]]
- [[active-recon|Active Recon]]

### Descubrimiento de assets

- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[company-mapping|Company Mapping]]
- [[tech-stack-fingerprinting|Tech Stack Fingerprinting]]

### Enumeration

- [[enumeration|Enumeration]]
- [[subdomain-enumeration|Subdomain Enumeration]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]

### Validación y handoff

- [[scope-validation|Validación de Scope]]
- [[service-validation|Validación de Servicios]]
- [[recon-to-testing-handoff|Handoff de Recon a Testing]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

### Ingeniería de scan (profundidad)

- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[idle-scan-and-ipid-side-channels|Idle Scan and IPID Side Channels]]
- [[nse-vuln-category-audit|NSE vuln Category Audit]]

### Active Directory e identity attacks

> Promovido a su propia rama el 2026-05-10. Ver [[index|Identity and Active Directory]] para Kerberoasting, AS-REP Roasting, BloodHound, DCSync y notas relacionadas.

### Telemetría de scan del lado defensor

- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, y Análisis de NetFlow]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

---

## Cross-links a otras ramas

### Mapeo de superficie de ataque

- [[attack-surface-mapping|Mapeo de Superficie de Ataque]]
- [[external-attack-surface|Superficie de Ataque Externa]]
- [[endpoint-discovery|Endpoint Discovery]]
- [[admin-interface-discovery|Admin Interface Discovery]]
- [[subdomain-takeover|Subdomain Takeover]]

### OSINT

- [[osint|OSINT]]
- [[osint-triage|OSINT Triage]]
- [[company-osint|Company OSINT]]
- [[osint-reporting|OSINT Reporting]]

### Redes

- [[dns-resolution|Resolución DNS]]
- [[dns-security|Seguridad de DNS]]
- [[ports-and-services|Puertos y Servicios]]
- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]

### Detection engineering

- [[index|Detection Engineering]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS y Pipelines de Detección Conductual]]

### Seguridad inalámbrica

- [[wireless-security|Seguridad Inalámbrica]]
- [[wifi-monitor-mode|Wi-Fi Monitor Mode]]
- [[evil-twin-access-points|Evil Twin Access Points]]
- [[bettercap-workflows|Bettercap Workflows]]

### Seguridad cloud

- [[cloud-security-basics|Fundamentos de Seguridad Cloud]]
- [[cloud-network-boundaries|Límites de Red Cloud]]
- [[cloud-iam-boundaries|Límites de IAM Cloud]]
- [[public-cloud-storage-exposure|Exposición de Storage Cloud Público]]

### Seguridad web/API

- [[api-inventory-management|API Inventory Management]]
- [[broken-access-control|Broken Access Control]]
- [[ssrf|SSRF]]
- [[cors-misconfiguration|CORS Misconfiguration]]
- [[bot-detection-signals|Señales de Detección de Bots]]
- [[evilginx-and-reverse-proxy-phishing|Evilginx and Reverse Proxy Phishing]]

### Playbooks de seguridad

- [[test-client-ip-spoofing|Test Client IP Spoofing]]

---

## Notas futuras sugeridas

- [[osint-triage|OSINT Triage]]
- [[search-engine-operators|Search Engine Operators]]
- [[google-dorking|Google Dorking]]
- [[breach-and-leak-intelligence|Breach and Leak Intelligence]]
- [[social-media-osint|Social Media OSINT]]
- [[email-and-phone-osint|Email and Phone OSINT]]
- [[image-and-location-osint|Image and Location OSINT]]
- historical-internet-artifacts
- js-recon
- route-guessing
- wordlist-strategy
- bug-bounty-recon-loop

---

## Notas de mantenimiento de la rama

- Usá el [[reference-registry-offensive-security|Registro de Referencias]] antes de agregar referencias.
- Mantené esta rama enfocada en descubrimiento, validación, scope y handoff.
- Mantené los detalles de explotación en Seguridad Web, Seguridad de APIs o Playbooks de Seguridad.
- Los temas OSINT de zSecurity ahora viven en [[index|OSINT]]. Mantené esta rama enfocada en el flujo de trabajo de recon y handoff.
- Mantené el patrón de handoff: cada nota de recon debería mostrar cómo una pista cruda se convierte en contexto validado, un candidato de test en scope, una decisión de no-acción o un camino de owner/remediación.

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon series — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OSINT Framework — https://osintframework.com/
