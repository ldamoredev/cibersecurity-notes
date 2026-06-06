# Reference Registry — Offensive Security

## Propósito

Esta nota estandariza las referencias para la rama de offensive security.

Usala para:
- mantener las notas de recon vinculadas a fuentes prácticas sólidas
- ayudar a Codex a elegir referencias consistentes
- evitar contenido genérico de recon con sourcing débil
- mantener la rama centrada en descubrimiento, enumeración, validación y handoff operacional mientras se deja espacio para temas más amplios de offensive security

## Regla de fuente de verdad

Para notas de offensive security, este registro es la fuente de verdad primaria.

Usalo junto con:
- `<a href="offensive-security/index.html">Offensive Security / Recon Index</a>`
- registros de networking y attack surface cuando las notas se superponen fuertemente

---

## Política de selección de referencias

### Prioridad de fuente

1. documentación oficial o primaria del proyecto
2. metodología práctica de reconocimiento
3. guías de testing y frameworks estructurados
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias

### Etiquetas

Usar:
- **Fundamental**
- **Testing / Lab**
- **Investigación / Deep Dive**
- **Docs Oficiales**

---

# Mapa de temas offensive / recon

## recon

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OSINT Framework — https://osintframework.com/

## passive-recon

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OSINT Framework — https://osintframework.com/

## active-recon

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 105 — https://projectdiscovery.io/blog/reconnaissance-series-5-additional-active-reconnaissance
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## public-asset-discovery

Referencias preferidas:
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## company-mapping

Referencias preferidas:
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## tech-stack-fingerprinting

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger information disclosure — https://portswigger.net/web-security/information-disclosure

## enumeration

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## subdomain-enumeration

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 102 — https://projectdiscovery.io/blog/recon-series-2
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## host-and-port-discovery

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## scope-validation

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** HackerOne Disclosure Guidelines — https://www.hackerone.com/disclosure-guidelines

## service-validation

Referencias preferidas:
- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## recon-to-testing-handoff

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## cloaking-and-security-evasion

Referencias preferidas:
- **Fundamental:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Testing / Lab:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## nmap-timing-and-evasion

Referencias preferidas:
- **Docs Oficiales:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Docs Oficiales:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

## packet-fragmentation-and-decoy-scans

Referencias preferidas:
- **Docs Oficiales:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Investigación / Deep Dive:** Ptacek & Newsham — Insertion, Evasion, and Denial of Service (1998) — https://insecure.org/stf/secnet_ids/secnet_ids.pdf
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

## masscan-internet-scale-scanning

Referencias preferidas:
- **Docs Oficiales:** Masscan README y man page — https://github.com/robertdavidgraham/masscan
- **Investigación / Deep Dive:** Erratasec — Masscan: the entire internet in 3 minutes — https://blog.erratasec.com/2013/09/masscan-entire-internet-in-3-minutes.html
- **Investigación / Deep Dive:** Durumeric et al. — ZMap (USENIX Security 2013) — https://zmap.io/paper.pdf

## rustscan-and-nse-pipeline

Referencias preferidas:
- **Docs Oficiales:** RustScan repository y docs — https://github.com/RustScan/RustScan
- **Docs Oficiales:** Nmap Scripting Engine — https://nmap.org/book/nse.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

> *Los temas específicos de AD (kerberoasting, as-rep-roasting, bloodhound-attack-path-analysis, dcsync-and-ntdsdit-extraction) fueron promovidos a su propia rama el 2026-05-10. Ver [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]] para esas entradas.*

## idle-scan-and-ipid-side-channels

Referencias preferidas:
- **Docs Oficiales:** Nmap Reference Guide — Idle Scan — https://nmap.org/book/idlescan.html
- **Investigación / Deep Dive:** Antirez — Dumb scan / new TCP scan method (Bugtraq, 1998, disclosura original) — https://seclists.org/bugtraq/1998/Dec/79
- **Investigación / Deep Dive:** Ensafi et al. — Detecting Intentional Packet Drops on the Internet via TCP/IP Side Channels (USENIX Security 2015) — https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/ensafi

## nse-vuln-category-audit

Referencias preferidas:
- **Docs Oficiales:** Nmap Scripting Engine — Categories — https://nmap.org/book/nse-usage.html#nse-categories
- **Docs Oficiales:** NSE script library — `vuln` category index — https://nmap.org/nsedoc/categories/vuln.html
- **Investigación / Deep Dive:** David Bianco — The Pyramid of Pain — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html

---

## Reglas de uso del registro

- elegir el conjunto más pequeño de referencias más fuertes para la nota exacta
- preferir una fuente de metodología más una fuente práctica donde sea posible
- mantener las notas de recon enfocadas en descubrimiento, validación y transición al testing
