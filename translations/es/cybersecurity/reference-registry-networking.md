# Reference Registry — Networking

## Propósito

Esta nota es la semilla específica de networking para el registry más amplio de referencias de ciberseguridad.

Usala para:
- estandarizar referencias para notas de networking
- mantener consistente la calidad de fuentes
- ayudar a Codex a asignar referencias sin inventar sets débiles
- hacer más fácil expandir futuras notas de networking

## Regla de fuente de verdad

Para notas de networking, este registry es la fuente de verdad primaria.

Usalo junto con:
- `<a href="networking/index.html">Networking Index</a>` para orden de estudio y estructura de rama
- `<a href="reference-registry.html">Cybersecurity Reference Registry</a>` para fallback cross-branch más amplio solo cuando esta nota todavía no cubra un tema networking

Al asignar referencias:
- elegí el set más chico de referencias fuertes para la nota exacta
- no inventes sets random de referencias networking ad hoc
- si falta una nota acá, inferí desde el tema padre de networking más cercano y agregá una propuesta de entrada al registry
- mantené las referencias de networking atadas a implicancias de seguridad, no a abstracción académica

---

## Política de selección de referencias

### Prioridad de fuentes

1. documentación oficial
2. labs oficiales y training práctico
3. estándares y guías de testing
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar inflar notas con listas largas

### Etiquetas

Usar:
- **Fundamental**
- **Testing / Lab**
- **Investigación / Deep Dive**
- **Docs oficiales de herramienta**

---

# Mapa de temas Networking

## tcp-ip-basics

Referencias preferidas:
- **Fundamental:** RFC 9293 (Transmission Control Protocol) — https://datatracker.ietf.org/doc/html/rfc9293
- **Fundamental:** RFC 791 (Internet Protocol) — https://datatracker.ietf.org/doc/html/rfc791
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Docs oficiales de herramienta:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/

Por qué:
- las notas TCP/IP deberían mantenerse ancladas en comportamiento real de red, no teoría abstracta
- Nmap y Wireshark son los anchors más prácticos para observar comunicación y reachability

---

## ports-and-services

Referencias preferidas:
- **Docs oficiales de herramienta:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/

Por qué:
- este tema es operacional y está directamente atado a attack surface
- Nmap es la referencia práctica central

---

## dns-resolution

Referencias preferidas:
- **Fundamental:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Fundamental:** ICANN DNS Concepts — https://www.icann.org/resources/pages/dns-2012-02-25-en
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Investigación / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers

Por qué:
- esta nota debería explicar cómo resuelven los nombres en la práctica y por qué eso importa para ownership, exposición y asset discovery

---

## dns-security

Referencias preferidas:
- **Fundamental:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Fundamental:** ICANN DNSSEC — https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en
- **Mitigación:** CISA Domain Name System Security Best Practices — https://www.cisa.gov/resources-tools/resources/domain-name-system-dns-security-best-practices
- **Investigación / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Investigación / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20

Por qué:
- DNS importa acá sobre todo como attack surface, ownership drift e higiene de control de dominio, no solo como teoría de protocolo

---

## dangling-dns-records

Referencias preferidas:
- **Fundamental:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Investigación / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Investigación / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20

Por qué:
- esta nota posee el lifecycle DNS y el mecanismo de stale-record que luego puede convertirse en un hallazgo de subdomain-takeover en attack-surface mapping

---

## http-overview

Referencias preferidas:
- **Fundamental:** MDN HTTP overview — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview
- **Fundamental:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Fundamental:** MDN HTTP request methods — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security

Por qué:
- MDN da el anchor práctico de comportamiento browser/server; RFC 9110 ancla la semántica formal; PortSwigger es el camino canónico de labs hands-on para vulnerabilidades enraizadas en HTTP

---

## http-messages

Referencias preferidas:
- **Fundamental:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Fundamental:** RFC 9112 (HTTP/1.1 Message Syntax) — https://datatracker.ietf.org/doc/html/rfc9112
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn

Por qué:
- HTTP messages se entienden mejor con forma de protocolo y consecuencias de seguridad. RFC 9112 ancla la sintaxis formal wire de HTTP/1.1; el paper de Kettle es el anchor de investigación más fuerte sobre qué pasa cuando dos parsers discrepan

---

## http-headers

Referencias preferidas:
- **Fundamental:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Fundamental:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Mitigación:** OWASP HTTP Headers Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security

Por qué:
- el comportamiento de headers vive en la intersección de semántica de protocolo, comportamiento del navegador, caching, confianza en proxy y múltiples clases de exploit

---

## cookies-and-sessions

Referencias preferidas:
- **Fundamental:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- **Fundamental:** OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- **Testing / Lab:** OWASP WSTG Session Management Testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf

Por qué:
- esta nota necesita semántica de navegador más framing de testing/mitigación de seguridad

---

## tls-https

Referencias preferidas:
- **Fundamental:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Fundamental:** RFC 8446 (TLS 1.3) — https://datatracker.ietf.org/doc/html/rfc8446
- **Fundamental:** Mozilla SSL Configuration Generator — https://ssl-config.mozilla.org/
- **Docs oficiales de herramienta:** OpenSSL s_client — https://docs.openssl.org/master/man1/openssl-s_client/
- **Testing / Lab:** testssl.sh — https://github.com/drwetter/testssl.sh

Por qué:
- esta nota se mantiene práctica (trust de transporte, terminación TLS, HSTS, inspección de certificados). RFC 8446 ancla la spec TLS moderna, Mozilla SSL Configuration Generator es la referencia canónica de posture-policy, openssl s_client es la herramienta estándar de inspección y testssl.sh es el scanner estándar. MDN sigue siendo el punto de entrada práctico

---

## reverse-proxies

Referencias preferidas:
- **Fundamental:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Fundamental:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn

Por qué:
- los reverse proxies son una nota de trust-boundary. RFC 7239 y MDN anclan la semántica de forwarding headers, PortSwigger academy es el lab canónico de smuggling y el paper de Kettle es el mejor anchor único para la clase parser-disagreement

---

## client-ip-trust

Referencias preferidas:
- **Fundamental:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Fundamental:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Investigación / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Por qué:
- esta nota trata sobre cómo trust headers afectan logging, rate limiting, allowlists y access controls. RFC 7239 ancla la spec estructurada Forwarded; el paper de Kettle es el writeup canónico sobre por qué headers forwarding sin key como XFF y X-Forwarded-Host son peligrosos

---

## header-trust-in-node-express

Referencias preferidas:
- **Docs oficiales de herramienta:** Express behind proxies — https://expressjs.com/en/guide/behind-proxies.html
- **Fundamental:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Fundamental:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239

Por qué:
- esta nota es el puente framework-specific desde [[client-ip-trust]] hacia Express. La documentación Express posee `trust proxy`; MDN y RFC 7239 anclan la semántica de forwarding headers

---

## load-balancers

Referencias preferidas:
- **Fundamental:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Fundamental:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Investigación / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Por qué:
- los load balancers son notas de entry-point y trust-boundary, no solo notas de infra

---

## firewalls-and-network-boundaries

Referencias preferidas:
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Docs oficiales de herramienta:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Mitigación:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html

Por qué:
- esta nota debería conectar supuestos de exposición con discovery basado en evidencia

---

## nat-and-private-networks

Referencias preferidas:
- **Fundamental:** RFC 1918 (Private Address Allocation) — https://datatracker.ietf.org/doc/html/rfc1918
- **Fundamental:** RFC 6598 (CGNAT shared address space) — https://datatracker.ietf.org/doc/html/rfc6598
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html

Por qué:
- el valor de esta nota está en vincular private reachability con SSRF e internal trust boundaries. RFC 1918 + 6598 anclan las definiciones formales de address-space; el cheat sheet OWASP ancla defensas SSRF que cierran link-local / private-range gates; PortSwigger y Nmap son los anchors prácticos de lab

---

## metadata-endpoints

Referencias preferidas:
- **Fundamental:** AWS Instance Metadata Service docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Fundamental:** GCP metadata server docs — https://cloud.google.com/compute/docs/metadata/overview
- **Fundamental:** Azure Instance Metadata Service docs — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf

Por qué:
- esta nota conecta fuertemente internal reachability, SSRF y riesgo de exposición de credenciales cloud. Los tres docs de vendors cloud son las únicas fuentes autoritativas sobre forma de protocolo por plataforma (AWS IMDSv1/v2, GCP Metadata-Flavor, Azure header-required). OWASP y PortSwigger son los anchors canónicos de defensa y lab

---

## nmap-scanning

Referencias preferidas:
- **Docs oficiales de herramienta:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/

Por qué:
- Nmap debería enseñarse primero desde el manual oficial

---

## service-enumeration

Referencias preferidas:
- **Docs oficiales de herramienta:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Docs oficiales de herramienta:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/

Por qué:
- esta nota es donde discovery se vuelve entendimiento accionable de servicios y protocolos expuestos

---

## wireshark-workflows

Referencias preferidas:
- **Docs oficiales de herramienta:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Docs oficiales de herramienta:** Wireshark docs portal — https://www.wireshark.org/docs/
- **Docs oficiales de herramienta:** Wireshark display filters — https://www.wireshark.org/docs/man-pages/wireshark-filter.html

Por qué:
- este tema es tool-native y debería mantenerse anclado en docs oficiales

---

## packet-analysis

Referencias preferidas:
- **Docs oficiales de herramienta:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Docs oficiales de herramienta:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Docs oficiales de herramienta:** tcpdump man page — https://www.tcpdump.org/manpages/tcpdump.1.html
- **Fundamental:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages

Por qué:
- packet analysis necesita tanto tooling de capture como interpretación de mensajes

---

## caching-and-security

Referencias preferidas:
- **Fundamental:** MDN HTTP caching — https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- **Fundamental:** MDN Cache-Control — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
- **Testing / Lab:** PortSwigger Web Cache Poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Investigación / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Por qué:
- los problemas de caching son sutiles y suelen surgir de semántica de protocolo interactuando con infraestructura compartida

---

# Reglas de uso del registry

- elegí el set más chico de referencias fuertes para cada nota exacta
- no asignes links genéricos ciegamente
- preferí documentación oficial y labs fuertes
- si una futura nota networking falta en este registry, mapeala primero al tema padre más cercano
- cuando agregues notas networking cloud-specific más adelante, agregá docs de provider solo si la nota se vuelve implementation-specific

---

# Próximas entradas sugeridas del registry networking

Agregalas cuando la rama se expanda:
- dns-record-types
- http-status-codes
- http-methods
- caching-keys-and-vary
- content-negotiation
- health-check-endpoints
- network-segmentation
- egress-control
