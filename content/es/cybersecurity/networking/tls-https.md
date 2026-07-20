---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - transport
  - tls
  - https
  - trust-boundary
sources: []
---

# TLS y HTTPS

## Definición
HTTPS es HTTP transportado sobre TLS. TLS (Transport Layer Security, antes SSL) es el protocolo que envuelve una conexión TCP — o una conexión QUIC basada en UDP en HTTP/3 — para proveer tres garantías: **confidencialidad** (los bytes en el wire son ilegibles para cualquiera salvo los endpoints), **integridad** (cualquier manipulación es detectable) y **autenticidad** (la identidad del servidor se verifica vía una cadena de certificados anclada en CAs confiables; mTLS extiende esto al cliente). TLS no dice nada sobre lo que la aplicación hace con esos bytes una vez que llegan — ese es el malentendido de seguridad más común en todo este tema.

## Por qué importa
TLS es una de las pocas primitivas que *realmente funciona* contra un atacante de red — y exactamente una de las defensas más sobreestimadas en producción. Importa porque:

- **Es la única defensa práctica contra la intercepción pasiva** de credenciales, tokens y PII en el wire.
- **Ancla la seguridad de cookies y almacenamiento.** La semántica de `Secure`, `HttpOnly`, `SameSite=None` y los prefijos de cookie `__Host-` solo tienen sentido sobre TLS.
- **Es una frontera de confianza en cada punto de terminación.** Donde termina TLS, empieza el texto plano; ese hop se vuelve interesante para cualquiera en el mismo segmento de red.
- ***No* es una defensa de capa de aplicación.** El smuggling, la deserialización, IDOR, XSS, SSRF y los ataques de host-header ocurren todos *dentro* del túnel TLS. "Usamos HTTPS" es la respuesta equivocada a la mayoría de las preguntas de seguridad.

Esta nota cubre la vista de despliegue-y-confianza de TLS — qué verificar, dónde falla en producción, cómo testearlo. Los internals criptográficos (algoritmos de intercambio de claves, construcciones AEAD, estructura ASN.1 de certificados) quedan fuera de alcance; ver referencias para el tratamiento formal.

## Cómo funciona
TLS provee **3 garantías** a través de **4 fases de handshake** (en TLS 1.2; TLS 1.3 colapsa varias en menos round-trips por rendimiento, pero las fases conceptuales se mantienen).

Las 3 garantías:

1. **Confidencialidad** — el cifrado simétrico (cifrados AEAD como AES-GCM, ChaCha20-Poly1305) protege los bytes después del handshake.
2. **Integridad** — cada record carga un tag de autenticación derivado de las claves de sesión; la manipulación se detecta y la conexión aborta.
3. **Autenticidad** — el servidor presenta una cadena de certificados; el cliente verifica que la cadena ancla en una root CA confiable y que el certificado coincide con el hostname pedido. Opcionalmente, el servidor requiere que el cliente también presente un certificado — esto es **mTLS**.

Las 4 fases:

1. **ClientHello** — el cliente ofrece versiones de TLS, cipher suites, protocolos ALPN (h2 / http/1.1 / h3), extensiones soportadas y un SNI (Server Name Indication) que le dice al servidor con qué hostname quiere hablar el cliente.
2. **ServerHello + Certificate + KeyExchange** — el servidor elige una versión + cipher + ALPN, envía su cadena de certificados, envía sus parámetros de intercambio de claves. El cliente valida la cadena de certificados (firmada por una CA confiable, no expirada, hostname coincide, no revocada).
3. **Derivación de claves + Finished** — ambos lados derivan las claves de sesión y confirman que coinciden. Cualquiera que no pueda derivar las mismas claves (porque no tiene la clave privada del servidor) queda afuera.
4. **Datos de aplicación** — fluye el tráfico HTTP cifrado. De acá en adelante, los bytes del wire son opacos para cualquiera en el camino de red.

Una inspección práctica de un handshake TLS en el wire:

```bash
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null
# La salida revela: versión de TLS, cipher suite, cadena de certificados, resultado de ALPN
```

El bug rara vez está en el protocolo TLS mismo (las primitivas criptográficas son sólidas para las versiones actuales). El bug está abrumadoramente en el **despliegue**: dónde termina TLS, qué pasa después de la terminación, cómo validan los clientes, cuánto viven los certificados y qué asume la aplicación en el momento en que se restaura el texto plano.

## Técnicas / patrones
Qué miran atacantes y operadores:

- **Leé el certificado.** Issuer, subject (`CN` y `Subject Alternative Name`), fechas de validez, algoritmo de firma, parámetros de clave pública. Los SANs en particular revelan arquitectura: certs compartidos entre hostnames, alcance de wildcard, hostnames internos accidentalmente en certs de producción.
- **Chequeá la versión y el cipher.** TLS 1.0 y 1.1 están deprecados y rotos de distintas formas; TLS 1.2 con ciphers no-AEAD (CBC + HMAC) tiene debilidades conocidas (BEAST, Lucky13). Cualquier cosa menor a TLS 1.2 + AEAD o TLS 1.3 es un hallazgo.
- **Chequeá la cadena de redirect.** `http://` debería redirigir a `https://`, idealmente con HSTS ya seteado en un redirect del *mismo hostname* (algunas implementaciones setean HSTS solo en la response segura, perdiéndose la primera request).
- **Chequeá los logs de Certificate Transparency.** `crt.sh` revela cada cert emitido para un dominio — incluyendo los mal-emitidos, los hostnames solo-internos que se filtraron a un cert público y el historial de rotación de certs.
- **Chequeá ALPN y versión de HTTP.** `h2` solo en el edge con `http/1.1` al origin es la trampa de reintroducción de smuggling. Ver [[reverse-proxies|Reverse proxies]] §"downgrade HTTP/2 → HTTP/1.1".
- **Buscá contenido mixto.** Una página servida sobre HTTPS que carga scripts/iframes/forms sobre HTTP en texto plano socava todo el transporte.

## Variantes y bypasses
Los despliegues de TLS fallan en **5 clases distintas**. Cada una es una mala configuración de despliegue; la criptografía subyacente rara vez tiene la culpa.

### 1. TLS solo-en-el-edge
TLS termina en el load balancer / CDN / reverse proxy; el tráfico de ahí al servidor de aplicación es texto plano. Un atacante en la red interna — o cualquiera que haya comprometido un sidecar, contenedor vecino o el link LB/origin mismo — puede observar credenciales y cookies de sesión. El backend también puede confiar en `X-Forwarded-Proto: https` sin verificar que la conexión realmente llegó cifrada.

### 2. Validación de certificado salteada
Los clientes (o librerías del lado del servidor que hacen llamadas HTTP salientes) configuran su cliente HTTP para no verificar el certificado. Ofensores comunes: `requests.get(url, verify=False)`, `curl -k`, `InsecureSkipVerify: true` en Go, `TrustManager` custom aceptando todos los certs en Java. A menudo introducido "temporalmente" contra un cert de dev y olvidado en prod. Neutraliza completamente la autenticidad; la integridad y confidencialidad sobreviven solo contra un atacante que no hace MITM.

### 3. Versiones obsoletas y ciphers débiles
TLS 1.0/1.1 todavía habilitados, ciphers RC4 / 3DES / export-grade todavía soportados, parámetros DH débiles (Logjam), ciphers en modo CBC sin protección (BEAST/Lucky13), SSLv3 (POODLE). Cada uno es una superficie separada de downgrade o ataque conocido; la política moderna es "TLS 1.3 preferido, TLS 1.2 con AEAD solamente, todo lo demás deshabilitado".

### 4. HSTS faltante o débil
Sin header `Strict-Transport-Security`, o uno con `max-age` demasiado corto, o sin `includeSubDomains`, o no en la lista de preload del navegador. La primera request de cualquier cliente nuevo puede ser sobre HTTP y por lo tanto MITM-eable. El riesgo de subdomain takeover (ver [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]]) se amplifica cuando el dominio padre no restringe los subdominios vía HSTS preload + includeSubDomains.

### 5. Mal uso de flags de cookie/almacenamiento
Cookies seteadas sin `Secure` (enviadas por HTTP plano si existe algún camino HTTP), `HttpOnly` (legibles desde JS — combina mal con XSS), o `SameSite` (vulnerable a CSRF). Los prefijos `__Host-` y `__Secure-` proveen garantías estructurales adicionales pero son ampliamente ignorados. Ver [[cookies-and-sessions|Cookies y sesiones]].

## Impacto
Las fallas de despliegue de TLS mapean a techos de impacto específicos:

- **Robo de credenciales / sesión** — TLS solo-en-el-edge más un atacante adyacente a la red, o validación salteada más un MITM activo.
- **MITM de grado phishing** — intercepción completa del handshake cuando la validación se bypassea; el cliente no ve ninguna advertencia.
- **Ataque de downgrade** — negociación forzada de versión vieja (con forma BEAST/POODLE) recupera el texto plano.
- **Amplificación de subdomain takeover** — un alcance de HSTS faltante significa que un takeover de `forgotten.example.com` produce un cert válido que los navegadores confían.
- **Hijacking de cookie vía contenido mixto** — `Secure` faltante significa que una request HTTP en cualquier lado manda la cookie de sesión.
- **Exposición de tráfico interno** — el hueco de TLS solo-en-el-backend filtra credenciales a workloads colocados, sidecars o vecinos comprometidos.

## Detección y defensa
Ordenado por efectividad:

1. **TLS end-to-end, incluyendo proxy → origin.**
   La terminación en el edge está bien por rendimiento pero el *próximo* hop también debe ser TLS. La versión más fuerte es mTLS entre proxy y origin: el origin solo acepta conexiones que presenten un certificado de cliente emitido por el proxy, lo que cifra el hop y autentica el origen. Sin esto, la confianza del backend en `X-Forwarded-Proto: https` es forjable por cualquiera que llegue al origin directamente.

2. **Validación estricta de certificado en cada cliente, cada librería, cada script.**
   `verify=True` es el default en `requests`; no lo sobrescribas. `InsecureSkipVerify: true` en Go es solo para dev; prohibilo en prod vía lint/análisis estático. Los overrides de `TrustManager` custom en Java deberían revisarse de forma adversaria. Confiá en el bundle de CA del SO / lenguaje y rotalo; no lo bypassees.

3. **Configuración moderna de TLS: TLS 1.3 preferido, TLS 1.2 mínimo, solo-AEAD.**
   Deshabilitá TLS 1.0/1.1 por completo, deshabilitá ciphers RC4/3DES/export, preferí la config "intermediate" o "modern" de Mozilla. Corré un escáner (`testssl.sh`, SSL Labs) a una cadencia conocida; la política de certificados y ciphers deriva con el tiempo a medida que se descubren nuevas debilidades.

4. **HSTS con preload + includeSubDomains + max-age ≥ 1 año.**
   Header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`. Enviá a la lista de preload del navegador en `hstspreload.org` para que incluso la *primera* request de un cliente nuevo sea solo-HTTPS. No habilites `preload` hasta estar seguro de que cada subdominio — incluyendo los futuros — puede servir HTTPS, porque la remoción de la lista de preload es lenta.

5. **Automatización del ciclo de vida de certificados.**
   Certs de vida corta (90 días vía Let's Encrypt o equivalente) con renovación automatizada eliminan las caídas de "nos olvidamos de rotar" y reducen la ventana de una clave comprometida. Monitoreá la expiración activamente (alertá a los 30 días) — la automatización se rompe en silencio a veces.

6. **Higiene de cookies: `Secure`, `HttpOnly`, `SameSite=Lax` mínimo.**
   Para cookies sensibles, prefijá con `__Host-` (fuerza `Secure`, sin `Domain`, `Path=/`) para protección estructural que la revisión flag-por-flag puede perderse. Ver [[cookies-and-sessions|Cookies y sesiones]] para el panorama completo.

7. **Restringí quién puede emitir certs para tu dominio vía registros CAA.**
   `example.com.   CAA 0 issue "letsencrypt.org"` le dice a cada CA salvo Let's Encrypt que rechace certificados para este dominio. Combinado con monitorear los logs de CT (`crt.sh`) por emisiones inesperadas, esto atrapa la mal-emisión y los escenarios de CA-rogue.

### Qué no funciona como defensa primaria

- **"Usamos HTTPS".** TLS protege los bytes en tránsito. No protege contra bugs de capa de aplicación. Smuggling, IDOR, XSS, SSRF, deserialización ocurren todos dentro del túnel TLS. HTTPS es necesario; no es suficiente.
- **Confiar en `X-Forwarded-Proto: https`.** Ese header es un string que el cliente (o cualquiera que llegue al backend directamente) puede proveer. La confianza viene del camino de red, no del header. Ver [[client-ip-trust|Confianza en la IP del cliente]] para la misma lección del lado de la IP.
- **Certs autofirmados en prod con clientes skip-verify.** Este patrón es ubicuo en servicios internos y ubicuamente explotable. El supuesto "controlamos ambos extremos así que está bien" se rompe en el momento en que un endpoint es comprometido — todo el modelo de confianza colapsa a "cualquiera en la red puede hacer MITM".
- **Certs de larga vida sin rotación.** Una clave comprometida con un cert de 2 años es peligrosa durante los 2 años completos. Los certs cortos reducen el radio de explosión y fuerzan a que el tooling de rotación realmente funcione.
- **Pinning de cert hecho a mano en apps móviles.** El pinning es útil pero operativamente frágil; una rotación de cert mal hecha brickea la app. Usá monitoreo de Certificate Transparency en su lugar salvo que el modelo de amenaza realmente necesite pinning.
- **Dejar que el HSTS-preload del navegador se resuelva solo.** La lista de preload es opt-in; sin envío explícito, la primera request de cualquier cliente nuevo es HTTP plano.

## Labs prácticos
`openssl`, `curl`, `dig` estándar — más `crt.sh` para Certificate Transparency.

### Inspeccionar la cadena de certificados

```bash
# Handshake completo: versión de TLS, cipher, cadena de certificados, SANs
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null \
  | openssl x509 -text -noout

# Solo los SANs y las fechas de validez
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -dates -ext subjectAltName
```

### Sondear versiones de TLS y ciphers

```bash
# Testear qué versiones de TLS sigue aceptando el servidor
for v in tls1 tls1_1 tls1_2 tls1_3; do
  printf '%-8s -> ' "$v"
  echo | openssl s_client -connect example.com:443 -servername example.com -"$v" 2>&1 \
    | grep -E '^(no peer certificate available|Cipher|wrong version|alert)' | head -1
done

# Sondear un cipher suite específico
echo | openssl s_client -connect example.com:443 -servername example.com -cipher 'ECDHE-RSA-AES128-GCM-SHA256' 2>&1 \
  | grep -E '^(Cipher|alert)'

# Para un barrido más profundo, usá testssl.sh: https://github.com/drwetter/testssl.sh
# testssl.sh --severity HIGH https://example.com
```

### Verificar la postura de HSTS

```bash
# ¿Está seteado HSTS, y con qué alcance?
curl -sI https://example.com/ | grep -i 'strict-transport-security'

# ¿El http:// pelado redirige?
curl -sI http://example.com/ | grep -iE 'http/|location|strict-transport-security'

# ¿El dominio está en la lista de preload del navegador?
# Visitá https://hstspreload.org/?domain=example.com — solo formato de consulta,
# los navegadores traen la lista embebida.
```

### Buscar emisiones inesperadas en Certificate Transparency

```bash
# API JSON de crt.sh — listar cada cert emitido para el dominio
curl -s 'https://crt.sh/?q=%25.example.com&output=json' \
  | jq -r '.[] | "\(.not_before)  \(.issuer_name)  \(.name_value)"' \
  | sort -u | head

# Buscá: certs que no emitiste, hostnames que deberían ser solo-internos,
# certs wildcard de CAs que no usás y subdominios sospechosos.
```

### Encontrar clientes con verificación salteada en tu propio código

```bash
# Una auditoría de todo el repo por los ofensores skip-verify más comunes
rg -n --hidden \
  -e 'verify=False' \
  -e '-k\b' \
  -e 'InsecureSkipVerify' \
  -e 'rejectUnauthorized: false' \
  -e 'CURLOPT_SSL_VERIFYPEER' \
  -e 'TrustManager' \
  .
```

### Confirmar que el hop proxy → origin está cifrado

```bash
# Si tenés acceso a la IP del origin, confirmá que también habla TLS
# (y rechaza HTTP plano, idealmente)
echo | openssl s_client -connect <origin-ip>:443 -servername example.com -showcerts </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer

# HTTP plano al origin debería fallar o redirigir, nunca servir datos sensibles
curl -sI http://<origin-ip>/whoami -H 'Host: example.com'
```

## Ejemplos prácticos
- Una app SaaS termina TLS en el AWS ALB y envía HTTP plano a los pods de EKS. Un sidecar comprometido en otro namespace hace ARP-spoofing de la red del pod y cosecha cookies de sesión durante una hora antes de la detección.
- Un microservicio interno llama a una API partner con `requests.post(url, json=payload, verify=False)` que quedó de un fix de staging de 2022. Un atacante on-path reescribe la response y el servicio escribe el resultado en la base de datos sin validación adicional.
- Un hostname de staging `internal-admin.example.com` aterriza accidentalmente en la lista de SAN de un cert público de Let's Encrypt. Los logs de CT lo afloran; un atacante descubre el hostname, lo encuentra alcanzable desde internet y explota una falla de auth del panel de admin.
- Un banco deshabilita TLS 1.0 en su app pública pero se olvida del endpoint de la API partner. Un test de penetración degrada la conexión y reproduce queries de padding-oracle estilo POODLE.
- Una app móvil pinea una sola CA intermedia. La CA rota su clave. La actualización del pin sale con el próximo release de la app — tres semanas después. Durante tres semanas, la app es inutilizable en el campo; un atacante hace MITM impersonando la intermedia no-rotada durante la ventana.
- Un subdominio `legacy.example.com` está colgante (CNAME a una app de Heroku borrada). HSTS está seteado en `example.com` *sin* `includeSubDomains`. Un atacante toma el CNAME legacy, obtiene un cert de Let's Encrypt y sirve una página de phishing que el navegador confía como adyacente al same-origin.

## Notas relacionadas
- [[http-overview|Panorama de HTTP]] — TLS es la etapa 2 del ciclo de vida de 5 etapas de la transacción HTTP (establecer transporte).
- [[http-headers|Headers HTTP]] — `Strict-Transport-Security`, flags de seguridad de cookies.
- [[reverse-proxies|Reverse proxies]] — la terminación de TLS es una de las 5 transformaciones que aplica un reverse proxy; el hop de texto-plano-al-origin es una falla de confianza recurrente.
- [[client-ip-trust|Confianza en la IP del cliente]] — `X-Forwarded-Proto` es la especialización de desacuerdo-de-confianza del lado del transporte.
- [[cookies-and-sessions|Cookies y sesiones]] — semántica de `Secure`, `HttpOnly`, `SameSite`, prefijo `__Host-`.
- [[load-balancers|Load balancers]] — punto común de terminación de TLS; chequeá el hop proxy → origin acá.
- [[dns-security|Seguridad de DNS]] — registros CAA, validación de dominio basada en DNS, riesgo de takeover.
- [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] — amplificado cuando el alcance de HSTS está mal.
- [[cybersecurity/web-security/csrf|CSRF]] — el comportamiento de la cookie `SameSite` es una defensa primaria.
- [[cybersecurity/web-security/cors-misconfiguration|Mala configuración de CORS]] — el razonamiento de `Origin` depende de la identidad confirmada por TLS.

### Notas atómicas futuras sugeridas
- [[tls-1-3-handshake|Handshake de TLS 1.3]]
- [[mtls-deployment-patterns|Patrones de despliegue de mTLS]]
- [[certificate-transparency-monitoring|Monitoreo de Certificate Transparency]]
- [[acme-and-cert-automation|ACME y automatización de certs]]
- [[hsts-preload-strategy|Estrategia de HSTS preload]]
- [[cookie-prefixes-host-secure|Prefijos de cookie __Host- / __Secure-]]
- [[ocsp-and-crl-revocation|Revocación OCSP y CRL]]

## Referencias
- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** RFC 8446 (TLS 1.3) — https://datatracker.ietf.org/doc/html/rfc8446
- **Foundational:** Mozilla SSL Configuration Generator — https://ssl-config.mozilla.org/
- **Official Tool Docs:** OpenSSL s_client — https://docs.openssl.org/master/man1/openssl-s_client/
- **Testing / Lab:** testssl.sh — https://github.com/drwetter/testssl.sh
