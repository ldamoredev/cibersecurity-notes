# Reference Registry — Attack Surface Mapping

## Propósito

Esta nota estandariza las referencias para la rama attack-surface-mapping.

Usala para:
- mantener las notas orientadas a exposición vinculadas a fuentes fuertes
- ayudar a Codex a elegir referencias consistentes
- evitar blogspam random de recon
- mantener la rama enfocada en discoverability práctica y control de exposición

## Regla de fuente de verdad

Para notas de attack-surface-mapping, este registry es la fuente de verdad primaria.

Usalo junto con:
- `<a href="attack-surface-mapping/index.html">Attack Surface Mapping Index</a>`
- los registries relacionados de networking y API-security cuando una nota se superpone fuertemente

---

## Política de selección de referencias

### Prioridad de fuentes

1. estándares oficiales y documentación de proyecto
2. guía práctica de recon / ASM
3. guías de testing
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
- **Docs oficiales de herramienta**

---

# Mapa de temas attack-surface

## attack-surface-mapping

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
- **Fundamental:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services

## external-attack-surface

Referencias preferidas:
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services

## internal-attack-surface

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP API7:2023 SSRF — https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/

## exposed-service-triage

Referencias preferidas:
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## endpoint-discovery

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## admin-interface-discovery

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## subdomain-takeover

Referencias preferidas:
- **Investigación / Deep Dive:** ProjectDiscovery guide to DNS takeovers / subdomain takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## exposed-storage

Referencias preferidas:
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design

## deprecated-api-versions

Referencias preferidas:
- **Fundamental:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## third-party-exposure

Referencias preferidas:
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP API10:2023 Unsafe Consumption of APIs — https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/
- **Investigación / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools

---

## Reglas de uso del registry

- elegí el set más chico de referencias fuertes para la nota exacta
- preferí estándares más una fuente práctica de discovery
- mantené las notas de attack-surface enfocadas en exposición, discoverability y drift
