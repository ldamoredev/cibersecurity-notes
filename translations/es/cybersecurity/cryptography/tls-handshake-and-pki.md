# TLS Handshake and PKI

## Definición

TLS es un protocolo de capa de transporte que establece un canal confidencial y autenticado entre dos partes combinando (1) un handshake asimétrico que autentica al menos un par usando un certificado firmado por una CA de confianza, con (2) un protocolo de registro AEAD simétrico que protege el resto de la conversación. PKI (X.509 public key infrastructure) es el grafo de confianza de certificados, intermedios, y root stores que hace significativa la afirmación de autenticidad del handshake.

## Por qué importa

Casi todos los bugs de TLS en producción son una de tres cosas: un certificado mal configurado (SAN incorrecta, expirado, clave débil), un handshake mal configurado (versión deprecada, cipher débil, forward secrecy faltante), o una decisión de confianza mal configurada (sin validación, root store incorrecto, pinning roto). Leer configuraciones TLS correctamente es la base para razonar sobre HTTPS, mTLS, MQTT-over-TLS, gRPC, y mediación de reverse proxy. También es un prerequisito para entender ataques mid-path (mitmproxy, evilginx, CAs falsas) y detección dirigida por certificados (CT logs, TOFU estilo SSH).

## Cómo funciona

TLS 1.3 (RFC 8446) es el handshake moderno. Colapsa el flujo de TLS 1.2 de 2 round-trips en un solo round-trip y elimina primitivos débiles por construcción. El handshake tiene 5 pasos lógicos:

1. **ClientHello** — el cliente envía una lista de versiones soportadas, cipher suites (solo AEAD en TLS 1.3), grupos soportados (X25519, P-256), algoritmos de firma (Ed25519, RSA-PSS, ECDSA-P256), y un key share (su clave pública ECDH).
2. **ServerHello + Certificate + CertificateVerify + Finished** — el servidor elige un cipher suite y grupo, envía su cadena de certificados, firma el transcript del handshake con su clave privada (`CertificateVerify`), y confirma con `Finished`. Desde aquí la conexión está cifrada con claves de tráfico del handshake.
3. **El cliente valida la cadena de certificados.** El cliente recorre la cadena desde el leaf → intermedios → root, verifica firmas con la clave pública de cada emisor, verifica `notBefore`/`notAfter`, verifica `keyUsage`/`extKeyUsage`/`basicConstraints`, valida el hostname contra `subjectAltName`, y consulta revocación (CRL u OCSP, opcionalmente OCSP stapling).
4. **`Finished` del cliente y derivación de clave.** Ambos lados derivan claves AEAD simétricas para el tráfico de aplicación del secreto compartido ECDH vía HKDF. El transcript del handshake se vincula a las claves, así que cualquier manipulación rompe el próximo mensaje.
5. **Datos de aplicación** — AEAD de capa de registro (AES-GCM, AES-CCM, ChaCha20-Poly1305) protege todo lo demás.

```
ClientHello (versions, suites, groups, signature_algs, key_share)
     -->                                                          <-- ServerHello
                                                                       Certificate
                                                                       CertificateVerify
                                                                       Finished
cliente valida cert chain + hostname
Finished -->
<-- datos de aplicación sobre protocolo de registro AEAD
```

El bug no es "TLS es difícil"; es "la afirmación de autenticidad depende de una cadena de confianza que la implementación debe verificar activamente." Deshabilitar la validación, aceptar hostnames incorrectos, o confiar en un root store personalizado convierte a TLS en transporte cifrado pero no autenticado — que es exactamente lo que quieren los atacantes mid-path.

## Técnicas / patrones

El modelo de razonamiento al revisar un deployment TLS:

- **Postura de versión:** TLS 1.3 preferido; TLS 1.2 aceptable; TLS 1.0/1.1 deshabilitado; SSL 3.0/2.0 deshabilitado.
- **Postura de cipher:** solo suites AEAD de TLS 1.3 (AES-GCM, ChaCha20-Poly1305); TLS 1.2 solo ECDHE con forward secrecy y AEAD; intercambio de clave static-RSA deshabilitado.
- **Postura de certificado:** claves ECDSA-P256 o RSA-2048+; firmas SHA-256+; `notBefore`/`notAfter` actuales y bien formados; SAN incluye los hostnames en uso; la cadena sirve los intermedios requeridos; registrado en CT.
- **Postura de confianza:** los clientes usan el root store del OS o plataforma; los roots personalizados son explícitos y mínimos; el pinning se usa cuando el conjunto de confianza es más estrecho que "el Internet público"; la revocación se verifica vía OCSP o certs de corta duración.
- **Patrón de sondeo en code review:** grep por `verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`, `setSSLSocketFactory`, overrides de `TrustManager`, verificadores de hostname personalizados, y overrides de `sslcontext.set_default_verify_paths`. Cada uno es un lugar donde alguien podría haber deshabilitado la validación "solo para testing" y olvidado quitarlo.

## Variantes y bypasses

Las 5 formas de deployment TLS que encontrarás en la práctica.

### Server-auth TLS (la forma web por defecto)

El cliente valida el certificado del servidor; el servidor no autentica al cliente en la capa TLS. La autenticación del cliente ocurre en capas más altas (contraseñas, tokens, cookies). Este es todo el web público. La decisión de confianza es "¿el leaf encadena a una CA que confía mi OS y su SAN coincide con el hostname que pedí?"

### Mutual TLS (mTLS)

Tanto el cliente como el servidor presentan certificados. Usado para autenticación service-to-service, flotas de dispositivos IoT, y redes zero-trust. La decisión de confianza se vuelve bidireccional: ambos lados deben validar la cadena del otro, hostname/identificador, y cualquier política organizacional embebida en el cert (SPIFFE IDs, convenciones internas CN/OU). mTLS es *autenticación de transporte*, no autorización — qué está permitido hacer el cert es una decisión separada.

### CA pública vs CA privada

Las CAs públicas (Let's Encrypt, Sectigo, DigiCert) son de confianza por defecto para browsers/OSes. Las CAs privadas (corporativas, service mesh de K8s, AWS PCA) son de confianza solo dentro de su org. Mezclarlas — aceptar una CA privada en un contexto público, o confiar en CAs públicas en una malla privada — amplía la superficie de ataque innecesariamente.

### Pinning

El cliente solo acepta un certificado específico, hash de clave pública, o CA. Útil cuando se controlan ambos extremos (app móvil a tu API, dispositivo IoT a tu fleet manager). Frágil si el conjunto de pins es una única clave — la rotación requiere una actualización de software. Mejor práctica: pinar al hash SPKI de múltiples claves, rotar antes de la expiración de cualquier pin, preferir pinning dinámico cuando esté disponible.

### TOFU y TLS anónimo

Trust on first use (estilo SSH) o anónimo-DH. Común en SSH, servicios onion de Tor, y sistemas Noise-Protocol. Útil donde no hay PKI global; vulnerable al MITM del primer encuentro.

## Impacto

- **Sin validación de certificado:** cualquier atacante mid-path (Wi-Fi rogue, proxy comprometido, evilginx) puede MITM de forma transparente. Todo el tráfico "cifrado" es plaintext para el atacante. Credenciales, tokens, y PII se filtran.
- **Aceptación de hostname incorrecto:** incluso un cert firmado por CA real para un hostname diferente tiene éxito, lo que permite que un atacante que valida dominios pivotee.
- **Primitivos débiles (TLS 1.0, RC4, 3DES, ciphers NULL, export-grade):** ataques conocidos (BEAST, CRIME, POODLE, SWEET32, FREAK, Logjam) erosionan la confidencialidad e integridad en escenarios específicos.
- **Sin forward secrecy (intercambio de clave static-RSA):** si la clave privada del servidor alguna vez se filtra, *todo el tráfico pasado* que fue capturado es descifrable. ECDHE previene esto.
- **Certificados de larga duración sin revocación:** una clave privada robada sigue siendo utilizable hasta que el cert expire. La mejor práctica moderna se inclina hacia certs de 90 días o más cortos y OCSP must-staple.
- **Confiar en una CA privada en toda la org:** cualquier poseedor de cualquier cert de CA privada puede crear certs para cualquier hostname; un CI runner comprometido se convierte en un MITM wildcard.

La severidad escala cuando TLS protege identidad de alto valor (sesiones admin, code signing, pagos), cuando el pinning está ausente en apps móviles, y cuando la validación del cliente está deshabilitada "para desarrollo".

## Detección y defensa

Ordenado por lo que funciona:

1.
**Solo TLS 1.3 o TLS 1.3 + TLS 1.2 con suites solo-FS.**
   Deshabilitar TLS 1.0, 1.1, y SSL 3.0/2.0. En TLS 1.2, permitir solo ECDHE_ECDSA / ECDHE_RSA con AES-GCM o ChaCha20-Poly1305. El perfil "intermediate" o "modern" de Mozilla es un buen punto de partida. Re-verificar con SSL Labs.

2.
**Validar certificados por defecto; nunca deshabilitar la validación en código de producción.**
   Tratar `verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`, y `TrustManager`/`HostnameVerifier` overrideados como fallas de lint de producción. Proporcionar un path de configuración solo para desarrollo que sea imposible de alcanzar en builds de producción.

3.
**Usar certificados gestionados por ACME con tiempos de vida cortos.**
   Let's Encrypt y emisores ACME similares automatizan la emisión y renovación. Los certs de corta duración (≤ 90 días) reducen la ventana de valor de una clave robada. Los servicios internos deben usar un ACME interno (step-ca, smallstep, K8s cert-manager) en lugar de certs emitidos manualmente de larga duración.

4.
**Monitorear CT logs para hostnames propios.**
   Los logs de Certificate Transparency (RFC 6962) registran cada cert emitido. Suscribirse a alertas para tus dominios (Cert Spotter, Censys CT alerts, Crt.sh feed) — la emisión inesperada es una señal de CA rogue o supply-chain.

5.
**Pinar en apps donde el conjunto de confianza es más estrecho que el Web PKI.**
   Las apps móviles y los dispositivos embedded que hablan con tus propios servicios deben pinar a tus hashes SPKI, con múltiples pins para rotación. Los browsers no deben pinar vía HPKP (deprecado); depender de CT y Expect-CT.

### Qué no funciona como defensa primaria

- **"Usamos HTTPS, así que estamos seguros."** TLS sin validación es encryption contra observadores pasivos solamente. Los atacantes activos (Wi-Fi rogue, portales cautivos, proxies comprometidos, phishing tipo evilginx reverse-proxy) hacen MITM trivialmente a TLS no validado.
- **"Usamos una clave larga (RSA-4096), así que el cipher no importa."** El tamaño de clave es irrelevante al modo de cipher. RSA-4096 + RC4 sigue siendo roto por RC4.
- **"Confiamos en el cert porque está en nuestro Java keystore."** Agregar un root personalizado al keystore amplía la confianza a *cada* cert que ese root firma, para siempre. El pinning estrecha; confiar amplía.
- **"El responder OCSP está caído así que simplemente omitimos la revocación."** OCSP soft-fail es esencialmente sin revocación. Preferir OCSP must-staple y certs de corta duración sobre fail-open manual.
- **"Deshabilitamos la validación para el entorno de staging y usamos el mismo code path en prod."** Esta es la única falla de TLS de grado producción más común. Usar un límite a nivel de plataforma: configs distintas por entorno, secret stores distintos, y verificaciones de CI que fallen el build si la validación está deshabilitada en un artefacto de prod.

## Labs prácticos

### Inspeccionar un handshake TLS con curl/openssl

```
openssl s_client -connect example.com:443 -servername example.com -tls1_3 -showcerts < /dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName -ext extendedKeyUsage
curl -vI --tls-max 1.3 https://example.com 2>&1 | grep -E 'TLS|cipher|ALPN|subject|issuer'
```

Resultado: podés ver la versión negociada, suite, ALPN, SAN del leaf, emisor, y validez. Si tu servidor cae por debajo del piso, los valores de suite y versión lo revelan.

### Puntuar el deployment con SSL Labs

```
https://www.ssllabs.com/ssltest/analyze.html?d=example.com
```

Resultado: una letra más la razón exacta de cada deducción. Apuntar a A+, con HSTS, cadena completa, OCSP must-staple, y solo suites modernas.

### Validar lifetime, SAN, y emisor del cert en CI

```
HOST=example.com
NOTAFTER=$(echo | openssl s_client -servername $HOST -connect $HOST:443 2>/dev/null \
  | openssl x509 -noout -enddate | cut -d= -f2)
EXP_TS=$(date -j -f "%b %e %T %Y %Z" "$NOTAFTER" +%s 2>/dev/null || date -d "$NOTAFTER" +%s)
NOW_TS=$(date +%s)
echo "days_left=$(( (EXP_TS - NOW_TS) / 86400 ))"
```

Resultado: una sola verificación de CI que captura el bug TLS operacional más común — expiración silenciosa.

## Ejemplos prácticos

- Una malla de microservicios interna acepta tanto Let's Encrypt como un root de CA privada debido a una migración histórica. Eliminar la CA pública del trust store interno reduce la superficie de ataque cross-trust a cero sin costo funcional.
- Una app móvil usa `verify=False` para un build de desarrollo y un flag olvidado se activa en producción. Agregar una verificación de CI que escanea el binario de producción por el símbolo o string y falla el build.
- Un fleet manager IoT pina un único hash SPKI en el firmware. El cert rota y 100k dispositivos se rompen. Moverse a multi-pin (actual + siguiente) y documentar el playbook de rotación.

## Notas relacionadas

- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[certificate-validation-and-pinning]]
- [[tls-https|TLS / HTTPS]]
- [[evilginx-and-reverse-proxy-phishing|Evilginx and Reverse-Proxy Phishing]]

## Referencias

- **Estándar / RFC:** RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3 — https://www.rfc-editor.org/rfc/rfc8446
- **Fundamental:** Mozilla Server Side TLS Recommendations — https://wiki.mozilla.org/Security/Server_Side_TLS
- **Testing / Lab:** SSL Labs SSL Server Test — https://www.ssllabs.com/ssltest/
