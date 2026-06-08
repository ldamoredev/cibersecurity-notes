# Índice de Privacidad, Anonimato y OPSEC

## Propósito

Este índice es el punto de entrada raíz para la rama de Privacidad, Anonimato y OPSEC del atlas de ciberseguridad.

Usalo para entender cómo las herramientas de privacidad realmente modifican un threat model:
- qué ocultan
- qué exponen
- hacia quién desplazan la confianza
- qué metadatos quedan
- dónde los errores operacionales anulan la herramienta

La rama evita el encuadre de criptomonedas y mercados darknet. Su foco es la ingeniería de privacidad, los límites del anonimato, los threat models de VPN, Tor, fuga de metadatos, comunicación cifrada, sistemas compartimentados, eliminación segura y fallas comunes de desanonimización.

Usá [[reference-registry-privacy-anonymity-opsec|Reference Registry - Privacidad, Anonimato y OPSEC]] como fuente de verdad para las referencias en esta rama.
Volvé a [[index|Índice de Ciberseguridad]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).

> *Siempre activa:* esta rama es una disciplina personal paralela, no una fase. Leela junto a todo lo demás.

---

## Modelo mental de la rama

Las herramientas de privacidad no crean anonimato por defecto.
Cambian la visibilidad, la confianza, la exposición de metadatos y los modos de falla.

La pregunta recurrente no es "¿es privada esta herramienta?". Es:

```
¿Contra qué observador, para qué actividad, con qué señales de identidad todavía presentes?
```

---

## Orden de aprendizaje recomendado

### Vocabulario central y fuga

1. [[privacy-vs-anonymity-vs-confidentiality]]
2. [[metadata-and-identity-leakage]]
3. [[vpn-threat-models]]

### VPNs y confianza en el ruteo

1. [[vpn-protocols]]
2. [[vpn-logging-and-trust]]
3. [[vpn-leakage-risks]]
4. [[vpn-dns-and-ipv6-leaks]]
5. [[vpn-kill-switches]]
6. [[vpn-fingerprinting-limitations]]
7. [[vpn-vs-tor]]

### Tor, composición y file OPSEC

1. [[tor-and-onion-services]]
2. [[tor-browser-security-settings]]
3. [[tor-bridges-and-pluggable-transports]]
4. [[vpn-with-tor]]
5. [[corporate-vpns-vs-consumer-vpns]]
6. [[file-metadata-removal]]

### Entornos de anonimato y compartición

1. [[tails-operational-model]]
2. [[qubes-compartmentalization]]
3. [[whonix-gateway]]
4. [[secure-file-sharing]]
5. [[anonymity-threat-models]]
6. [[deanonymization-failures]]

### Privacidad en mensajería y email

1. [[private-email-threat-models]]
2. [[temporary-email-risks]]
3. [[xmpp-and-private-messaging]]
4. [[end-to-end-encryption]]
5. [[pgp-encryption-and-signatures]]

### Almacenamiento y eliminación

1. [[secure-deletion-and-storage-wiping]]

### OPSEC y correlación

1. [[opsec-failure-chains]]
2. [[browser-fingerprinting]]
3. [[account-correlation]]
4. [[traffic-correlation]]

---

## Notas iniciales maduras actuales

### Modelo central

- [[privacy-vs-anonymity-vs-confidentiality]]
- [[metadata-and-identity-leakage]]

### Modelo VPN

- [[vpn-threat-models]]
- [[vpn-protocols]]
- [[vpn-logging-and-trust]]
- [[vpn-leakage-risks]]
- [[vpn-dns-and-ipv6-leaks]]
- [[vpn-kill-switches]]
- [[vpn-fingerprinting-limitations]]
- [[vpn-vs-tor]]
- [[vpn-with-tor]]
- [[corporate-vpns-vs-consumer-vpns]]

### Tor, entorno y file OPSEC

- [[tor-and-onion-services]]
- [[tor-browser-security-settings]]
- [[tor-bridges-and-pluggable-transports]]
- [[tails-operational-model]]
- [[qubes-compartmentalization]]
- [[whonix-gateway]]
- [[file-metadata-removal]]
- [[secure-file-sharing]]
- [[anonymity-threat-models]]
- [[deanonymization-failures]]

### Privacidad en mensajería y email

- [[private-email-threat-models]]
- [[temporary-email-risks]]
- [[xmpp-and-private-messaging]]
- [[end-to-end-encryption]]
- [[pgp-encryption-and-signatures]]

### Almacenamiento y eliminación

- [[secure-deletion-and-storage-wiping]]

### OPSEC y correlación

- [[opsec-failure-chains]]
- [[browser-fingerprinting]]
- [[account-correlation]]
- [[traffic-correlation]]

---

## Cross-links a otras ramas

### Networking

- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]
- [[tls-https|TLS / HTTPS]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[http-headers|HTTP Headers]]

### Seguridad web y de API

- [[session-management|Session Management]]
- [[content-security-policy|Content Security Policy]]
- [[oauth-security|OAuth Security]]
- [[token-lifecycle|Token Lifecycle]]

### OSINT

- [[osint|OSINT]]
- [[social-media-osint|Social Media OSINT]]
- [[image-and-location-osint|Image and Location OSINT]]
- [[email-and-phone-osint|Email and Phone OSINT]]

### Cloud y DevSecOps

- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[secrets-management|Secrets Management]]
- [[secure-by-design|Secure by Design]]

---

## Cola de labs prácticos

Candidato futuro de lab privado: lab de privacidad y OPSEC.

Ejercicios posibles:
- comparar IP visible antes y después de una VPN
- testear rutas de fuga DNS
- testear rutas de fuga IPv6
- inspeccionar superficies de browser fingerprint
- inspeccionar metadatos de archivos antes de compartir
- eliminar metadatos de imágenes y verificar la eliminación
- comparar visibilidad de ruteo VPN vs Tor
- simular comportamiento ante desconexión de VPN con kill switch
- documentar una cadena de falla OPSEC a partir de indicios aparentemente inocuos

---

## Notas de mantenimiento de la rama

- Mantener la rama defensiva, educativa y orientada a threat models.
- Evitar el encuadre de criptomonedas, marketplaces y evasión para actividades delictivas.
- Tratar el anonimato como una propiedad específica del adversario, no como una etiqueta de producto.
- Mantener las notas de VPN precisas: las VPN desplazan la confianza en la ruta de red; no borran la identidad.
- Mantener las notas de Tor cuidadosas: Tor cambia el modelo de observador pero igual requiere comportamiento disciplinado en el browser y en las cuentas.
- Mantener las notas de OPSEC prácticas: las identidades se filtran a través de cuentas, comportamiento, archivos, tiempo, lenguaje, estado del dispositivo y contexto social.
- Los links futuros sugeridos locales a cada nota siguen siendo útiles para subtemas adyacentes, pero el backlog a nivel de rama para este paso está cerrado.

## Referencias

- **Fundamental:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** Tor Browser User Manual - https://tb-manual.torproject.org/
