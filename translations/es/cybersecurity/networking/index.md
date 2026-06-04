---
type: index
status: active
created: 2026-04-23
updated: 2026-05-01
tags:
  - cybersecurity
  - networking
  - index
---

# Índice de Redes

## Propósito
Este índice es el punto de entrada raíz para la rama de redes del vault de ciberseguridad.

Usalo para:
- navegar las notas de redes
- entender el orden de estudio
- ver cómo las redes se conectan con la seguridad web, la seguridad de APIs, el mapeo de superficie de ataque y los playbooks
- ver dónde termina la red genérica y empieza la seguridad específica de inalámbrico
- mantener la rama coherente a medida que se agregan notas nuevas

Usá [[cybersecurity/reference-registry-networking|Registro de referencia — Redes]] como fuente de verdad para las referencias de esta rama.
Volvé al [[cybersecurity/index|Índice de Ciberseguridad]] para la navegación raíz entre ramas.

> _Antes de esta rama:_
> - [[cybersecurity/foundations/index|Fundamentos]] (Fase 0) — los modelos mentales que toda rama técnica asume.

---

## Orden de aprendizaje recomendado

### Fase 1 — Comunicación central y exposición
1. [[tcp-ip-basics|Fundamentos de TCP/IP]]
2. [[ports-and-services|Puertos y servicios]]
3. [[dns-resolution|Resolución DNS]]
4. [[dns-security|Seguridad de DNS]]
5. [[dangling-dns-records|Registros DNS colgantes]]

### Fase 2 — Tráfico web y estado
6. [[http-overview|Panorama de HTTP]]
7. [[http-messages|Mensajes HTTP]]
8. [[http-headers|Headers HTTP]]
9. [[cookies-and-sessions|Cookies y sesiones]]
10. [[tls-https|TLS y HTTPS]]

### Fase 3 — Fronteras, ruteo y confianza
11. [[reverse-proxies|Reverse proxies]]
12. [[client-ip-trust|Confianza en la IP del cliente]]
13. [[header-trust-in-node-express|Confianza en headers en Node Express]]
14. [[load-balancers|Load balancers]]
15. [[firewalls-and-network-boundaries|Firewalls y fronteras de red]]
16. [[nat-and-private-networks|NAT y redes privadas]]
17. [[metadata-endpoints|Endpoints de metadata]]

### Fase 4 — Descubrimiento y observación
18. [[nmap-scanning|Escaneo con Nmap]]
19. [[cybersecurity/networking/service-enumeration|Enumeración de servicios]]
20. [[wireshark-workflows|Flujos de trabajo con Wireshark]]
21. [[packet-analysis|Análisis de paquetes]]

### Fase 5 — Capas de rendimiento con impacto en seguridad
22. [[caching-and-security|Caché y seguridad]]

Este orden va desde:
- cómo se comunican los sistemas
- a cómo los nombres y servicios se vuelven alcanzables
- a cómo se comporta realmente el tráfico HTTP
- a cómo se construyen y se rompen las fronteras de confianza
- a cómo atacantes y defensores observan el entorno

---

## Cluster central de redes

### Comunicación fundamental
- [[tcp-ip-basics|Fundamentos de TCP/IP]]
- [[ports-and-services|Puertos y servicios]]
- [[dns-resolution|Resolución DNS]]
- [[dns-security|Seguridad de DNS]]
- [[dangling-dns-records|Registros DNS colgantes]]

### Tráfico web y de capa de aplicación
- [[http-overview|Panorama de HTTP]]
- [[http-messages|Mensajes HTTP]]
- [[http-headers|Headers HTTP]]
- [[cookies-and-sessions|Cookies y sesiones]]
- [[tls-https|TLS y HTTPS]]

### Exposición, ruteo y fronteras
- [[reverse-proxies|Reverse proxies]]
- [[client-ip-trust|Confianza en la IP del cliente]]
- [[header-trust-in-node-express|Confianza en headers en Node Express]]
- [[load-balancers|Load balancers]]
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]]
- [[nat-and-private-networks|NAT y redes privadas]]
- [[metadata-endpoints|Endpoints de metadata]]

### Descubrimiento y observación
- [[nmap-scanning|Escaneo con Nmap]]
- [[cybersecurity/networking/service-enumeration|Enumeración de servicios]]
- [[wireshark-workflows|Flujos de trabajo con Wireshark]]
- [[packet-analysis|Análisis de paquetes]]

### Rendimiento y entrega
- [[caching-and-security|Caché y seguridad]]

---

## Por qué importa esta rama

Las redes no están separadas de la seguridad de aplicaciones.

Son el sustrato para:
- seguridad web
- seguridad de APIs
- fronteras de confianza de reverse proxy
- impacto de SSRF
- exposición de interfaces de admin
- mapeo de superficie de ataque
- supuestos de alcanzabilidad en la nube
- comportamiento de caché y entrega

Si un servicio es alcanzable, ruteable, forwardeado, cacheado o traducido incorrectamente, el problema de seguridad puede empezar mucho antes de que se revise el código de la aplicación.

---

## Cross-links a otras ramas

### Seguridad web
- [[http-overview|Panorama de HTTP]] → da soporte a XSS, CSRF, CORS, sesiones, request smuggling
- [[http-messages|Mensajes HTTP]] → da soporte al abuso de headers, análisis de auth, confusión de parsers
- [[http-headers|Headers HTTP]] → da soporte a CORS, CSP, auth, comportamiento de forwarding
- [[cookies-and-sessions|Cookies y sesiones]] → da soporte a auth, gestión de sesiones, CSRF
- [[tls-https|TLS y HTTPS]] → da soporte a seguridad de cookies, HSTS, confianza de transporte
- [[reverse-proxies|Reverse proxies]] → da soporte a request smuggling y razonamiento de frontera-de-confianza

### Seguridad de APIs
- [[http-overview|Panorama de HTTP]] → da soporte a la semántica REST y el comportamiento de API
- [[http-headers|Headers HTTP]] → da soporte a headers de auth, caché, forwarding, negociación de contenido
- [[client-ip-trust|Confianza en la IP del cliente]] → da soporte a rate limiting, logs, allowlists
- [[header-trust-in-node-express|Confianza en headers en Node Express]] → da soporte a la confianza de proxy específica de Express, `req.ip` y las decisiones de header forwarded
- [[reverse-proxies|Reverse proxies]] → da soporte al pensamiento de frontera-de-confianza para APIs
- [[nat-and-private-networks|NAT y redes privadas]] → da soporte a SSRF y acceso a servicios internos
- [[metadata-endpoints|Endpoints de metadata]] → da soporte al pensamiento de SSRF-a-riesgo-de-credencial

### Mapeo de superficie de ataque
- [[ports-and-services|Puertos y servicios]]
- [[dns-resolution|Resolución DNS]]
- [[dns-security|Seguridad de DNS]]
- [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]]
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]]
- [[nmap-scanning|Escaneo con Nmap]]
- [[cybersecurity/networking/service-enumeration|Enumeración de servicios]]
- [[load-balancers|Load balancers]]

### Seguridad inalámbrica
- [[cybersecurity/wireless-security/wireless-security|Seguridad inalámbrica]]
- [[cybersecurity/wireless-security/wifi-monitor-mode|Modo monitor de Wi-Fi]]
- [[cybersecurity/wireless-security/arp-poisoning|ARP poisoning]]
- [[cybersecurity/wireless-security/mitm-on-local-networks|MITM en redes locales]]

### Seguridad en la nube
- [[cybersecurity/cloud-security/cloud-network-boundaries|Fronteras de red en la nube]]
- [[cybersecurity/cloud-security/cloud-metadata-security|Seguridad de metadata en la nube]]
- [[cybersecurity/cloud-security/cloud-dns-and-certbot|DNS de nube y Certbot]]
- [[cybersecurity/cloud-security/ssh-access-to-cloud-hosts|Acceso SSH a hosts de nube]]

### Ingeniería de detección
- [[cybersecurity/detection-engineering/network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[cybersecurity/detection-engineering/zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[cybersecurity/detection-engineering/scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de escaneo y análisis de fingerprint]]

### Playbooks
- [[nmap-scanning|Escaneo con Nmap]]
- [[cybersecurity/networking/service-enumeration|Enumeración de servicios]]
- [[packet-analysis|Análisis de paquetes]]
- [[reverse-proxies|Reverse proxies]]
- [[cookies-and-sessions|Cookies y sesiones]]
- [[client-ip-trust|Confianza en la IP del cliente]]
- [[metadata-endpoints|Endpoints de metadata]]

---

## Notas futuras sugeridas

### Posibles próximas notas atómicas
- [[dns-record-types|Tipos de registros DNS]]
- [[http-status-codes|Status codes HTTP]]
- [[http-methods|Métodos HTTP]]
- [[caching-keys-and-vary|Claves de caché y Vary]]
- [[content-negotiation|Negociación de contenido]]
- [[health-check-endpoints|Endpoints de health-check]]
- [[network-segmentation|Segmentación de red]]
- [[egress-control|Control de egress]]
- [[client-isolation|Aislamiento de clientes]]

### Posibles playbooks
- [[enumerate-exposed-services|Enumerar servicios expuestos]]
- [[inspect-login-traffic|Inspeccionar el tráfico de login]]
- [[reverse-proxy-misconfig-checklist|Checklist de mala configuración de reverse proxy]]
- [[map-public-attack-surface|Mapear la superficie de ataque pública]]
- [[test-client-ip-spoofing|Testear el spoofing de IP de cliente]]
- [[trace-metadata-endpoint-reachability|Trazar la alcanzabilidad del endpoint de metadata]]

---

## Reglas de mantenimiento del vault para las notas de redes

Cada nota de redes debería seguir la forma interna de nota atómica de 11 secciones:
- Definición
- Por qué importa
- Cómo funciona
- Técnicas / patrones
- Variantes y bypasses
- Impacto
- Detección y defensa
- Labs prácticos o ejemplos prácticos
- Notas relacionadas
- Notas atómicas futuras sugeridas
- Referencias

Preferí `## Labs prácticos` cuando el tema soporta comandos ejecutables. Usá `## Ejemplos prácticos` cuando el tema es principalmente conceptual, arquitectónico u orientado a políticas.

Cada nota de redes debería quedar práctica, no demasiado académica.
Sesgá hacia:
- exposición
- comportamiento de protocolo
- observación a nivel de paquete
- enumeración real de servicios
- implicancias de seguridad

Mantené los temas específicos de radio, tramas, handshakes, rogue-AP y labs inalámbricos locales de Wi-Fi en [[cybersecurity/wireless-security/index|Seguridad inalámbrica]].
Mantené los controles específicos de proveedor de VPC, IAM, metadata, almacenamiento, DNS y logging de nube en [[cybersecurity/cloud-security/index|Seguridad en la Nube]].

---

## Referencias
- **Foundational:** MDN HTTP docs — https://developer.mozilla.org/en-US/docs/Web/HTTP
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
