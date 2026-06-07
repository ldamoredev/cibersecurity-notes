# Cybersecurity Reference Registry

## Propósito

Esta nota es la política raíz de referencias para el vault de ciberseguridad.

Existe para:
- definir reglas globales de calidad de referencias
- definir familias de fuentes preferidas
- dar guía de fallback cuando un registro específico de rama todavía no cubre un tema

Esta nota **no** es el registry principal para cada tema.

## Regla de fuente de verdad

Para cualquier rama madura, usá primero el registry específico de esa rama.

Ejemplos:
- [[reference-registry-cryptography|Reference Registry — Cryptography]]
- [[reference-registry-networking|Reference Registry — Networking]]
- [[reference-registry-web-security|Reference Registry — Web Security]]
- [[reference-registry-api-security|Reference Registry — API Security]]
- [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]]
- [[reference-registry-devsecops|Reference Registry — DevSecOps]]
- [[reference-registry-detection-engineering|Reference Registry — Detection Engineering]]
- [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]]
- [[reference-registry-offensive-security|Reference Registry — Offensive Security]]
- [[reference-registry-privacy-anonymity-opsec|Reference Registry — Privacy, Anonymity & OPSEC]]
- [[reference-registry-playbooks|Reference Registry — Playbooks]]

Usá este registry raíz solo cuando:
- todavía no existe un registry de rama
- una nota es cross-branch y ningún registry de rama la posee claramente
- un tema nuevo necesita guía temporal de fallback

---

## Política global de referencias

### Prioridad de fuentes

1. estándares oficiales y documentación de proyecto
2. labs oficiales y plataformas primarias de aprendizaje
3. documentación oficial de herramientas
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias
- máximo default 5 referencias

### Etiquetas

Usar:
- **Fundamental**
- **Testing / Lab**
- **Investigación / Deep Dive**
- **Docs oficiales de herramienta**

### Regla de calidad de referencias

Preferí:
- menos referencias, pero más fuertes
- fuentes primarias por encima de resúmenes
- fuentes que coincidan con el tema exacto de la nota
- referencias que soporten entendimiento, testing y mitigación

Evitá:
- blogspam random
- posts genéricos de "top 10 tools"
- referencias apenas relacionadas
- listas largas de referencias sin propósito claro

---

## Familias de fuentes preferidas

### Application security core

- OWASP Top 10
- OWASP WSTG
- OWASP API Security Project
- OWASP Cheat Sheet Series
- OWASP ASVS
- OWASP MASVS / MASTG

### Explotación práctica y labs

- PortSwigger Web Security Academy
- PortSwigger Research

### Entendimiento de networking y protocolos

- MDN HTTP docs
- Nmap docs
- Wireshark docs

### Ingeniería segura y software delivery

- NIST SSDF
- CISA Secure by Design

### Detection engineering y monitoreo

- Zeek documentation
- Suricata documentation
- IETF IPFIX / NetFlow references
- Microsoft Defender XDR advanced hunting schema
- MITRE ATT&CK data sources
- MITRE ATT&CK detection strategies and analytics
- CISA event logging and threat detection guidance
- Elastic Security Labs detection engineering research
- Elastic Common Schema and OpenTelemetry semantic conventions
- JA3 / JA4 TLS fingerprinting references

### Identity and Active Directory

- Microsoft Learn Active Directory and Windows Server identity documentation
- MITRE ATT&CK Kerberos ticket, credential access, and detection strategy entries
- SpecterOps / BloodHound research and documentation
- ADSecurity / Sean Metcalf canonical Kerberos and AD compromise research
- RFC 4120 and Kerberos protocol references when protocol mechanics are central

### Recon y descubrimiento de exposición

- ProjectDiscovery research and recon series
- OSINT Framework

### Privacidad, anonimato y OPSEC

- EFF Surveillance Self-Defense
- NIST Privacy Framework
- OWASP User Privacy Protection Cheat Sheet
- Tor Project documentation
- Tails, Qubes, and Whonix official documentation

### Cryptography

- NIST Cryptographic Standards and Guidelines
- RFCs for TLS, JOSE/JWT, PKIX, and password-based cryptography
- OWASP Cryptographic Storage Cheat Sheet
- OWASP Password Storage Cheat Sheet
- libsodium documentation

---

## Regla del vault

Los registries de rama tienen precedencia sobre esta nota.

Esta nota debería mantenerse corta, estable y orientada a política.
No debería crecer hasta convertirse en un duplicado gigante de todos los registries de rama.
