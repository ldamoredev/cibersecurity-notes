# Índice de Wireless Security

## Propósito

Este índice es el punto de entrada raíz para la rama wireless-security del atlas de ciberseguridad.

Usalo para:
- entender Wi-Fi como un sistema de radio, frames, asociación y autenticación
- practicar observación inalámbrica en labs propios
- separar los conceptos de captura de paquetes, interrupción, riesgo de credenciales y MITM en redes locales
- conectar hallazgos inalámbricos de vuelta a redes, OSINT, reconocimiento ofensivo y controles defensivos

Usá [[reference-registry-wireless-security|Reference Registry — Wireless Security]] como fuente de verdad para referencias en esta rama.
Volvé a [[index|Índice de Ciberseguridad]] para navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[tcp-ip-basics|TCP/IP basics]] y [[ports-and-services|Ports and services]] — Wi-Fi es solo radio + frames sobre L2/L3.

---

## Orden de estudio recomendado

### Fase 1 — Modelo inalámbrico y observación

1. [[wireless-security]]
2. [[wifi-monitor-mode]]

### Fase 2 — Autenticación Wi-Fi legacy y moderna

1. [[wep-security]]
2. [[wpa-wpa2-handshakes]]
3. [[wifi-wordlist-attacks]]

### Fase 3 — Management frames y access points rogues

1. [[wifi-deauthentication]]
2. [[evil-twin-access-points]]

### Fase 4 — Intercepción en redes locales

1. [[arp-poisoning]]
2. [[mitm-on-local-networks]]
3. [[bettercap-workflows]]

---

## Cluster central de Wireless Security

### Madurez de la rama

Esta rama está madura en profundidad a partir de 2026-04-30.

Las 10 notas atómicas siguen la plantilla canónica de 11 secciones, incluyen labs prácticos y ahora llevan ejemplos trabajados que conectan observaciones inalámbricas con evidencia de labs propios, controles defensivos, rollback y límites de seguridad.

### Fundamentos

- [[wireless-security]]
- [[wifi-monitor-mode]]

### Autenticación y riesgo de claves

- [[wep-security]]
- [[wpa-wpa2-handshakes]]
- [[wifi-wordlist-attacks]]

### Ataques al plano de gestión

- [[wifi-deauthentication]]
- [[evil-twin-access-points]]

### MITM en red local

- [[arp-poisoning]]
- [[mitm-on-local-networks]]
- [[bettercap-workflows]]

---

## Cross-links a otras ramas

### Redes

- [[tcp-ip-basics|TCP/IP Basics]]
- [[ports-and-services|Ports and Services]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[nat-and-private-networks|NAT and Private Networks]]

### Ofensivo / reconocimiento

- [[recon|Recon]]
- [[active-recon|Active Recon]]
- [[scope-validation|Scope Validation]]
- [[service-validation|Service Validation]]

### OSINT y superficie de ataque

- [[osint|OSINT]]
- [[internal-attack-surface|Internal Attack Surface]]
- [[exposed-service-triage|Exposed Service Triage]]

---

## Notas futuras sugeridas

- wifi-channel-and-band-planning
- wpa3-sae
- enterprise-wifi-8021x
- wps-security
- bluetooth-security
- zigbee-security
- wireless-intrusion-detection
- radio-frequency-basics

### Posibles playbooks futuros

- build-owned-wifi-lab
- audit-home-wifi-security
- capture-wifi-handshake-in-lab
- detect-rogue-access-points
- validate-local-network-mitm-controls

---

## Notas de mantenimiento de la rama

- Mantener esta rama enfocada en el medio inalámbrico, frames Wi-Fi, autenticación, access points rogues e intercepción en redes locales.
- Mantener routing IP genérico, DNS, HTTP, TLS y análisis de paquetes fundamentales en [[index]].
- Todos los procedimientos inalámbricos disruptivos deben estar enmarcados como trabajo en lab propio o autorizado explícitamente.
- Preferir labs de observación primero antes de labs de inyección, deautenticación o spoofing.
- Usar wikilinks sin resolver para notas atómicas futuras para que Obsidian pueda rastrear la expansión de la rama.
- Mantener el patrón de seguridad en labs: cada nota inalámbrica activa debería nombrar el scope, dispositivos propios, impacto esperado, evidencia capturada y verificación de rollback.

## Referencias

- **Fundamental:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
- **Docs Oficiales:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Docs Oficiales:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
