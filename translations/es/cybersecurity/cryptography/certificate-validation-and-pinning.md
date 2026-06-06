# Certificate Validation and Pinning

## Definición

La validación de certificados es el proceso de decidir si una cadena de certificados presentada prueba la identidad del par para el nombre que se está contactando. El certificate pinning estrecha esa decisión de confianza requiriendo un certificado específico, clave pública, CA, o trust anchor además de la validación normal.

## Por qué importa

TLS no protege contra un man-in-the-middle a menos que el cliente valide la identidad del servidor. Muchos "bugs de TLS" catastróficos son en realidad bugs de validación: verificación deshabilitada, mismatch de hostname ignorado, cert expirado aceptado, CA privada accidentalmente de confianza, o pinning deployed sin un plan de rotación. El pinning puede reducir el riesgo de CA y del trust-store local, pero también puede inutilizar clientes si se trata como magia.

## Cómo funciona

La validación de certificados responde **5 preguntas**:

1.
**¿Es la cadena criptográficamente válida?**
   Cada certificado está firmado por el siguiente emisor hasta un root de confianza o anchor configurado.

2.
**¿Es el certificado válido ahora?**
   No antes, no después, y no evidentemente revocado donde se verifica la revocación.

3.
**¿Coincide el nombre?**
   El nombre DNS o IP que se está contactando debe coincidir con el Subject Alternative Name.

4.
**¿Está la clave permitida para este uso?**
   El key usage y extended key usage deben permitir la autenticación del servidor o el rol relevante.

5.
**¿Es el trust anchor aceptable para este contexto?**
   WebPKI público, CA privada, CA de identidad de workload, o SPKI pinned debe ser el trust root intendido.

```
conectar a https://api.example.com
  -> recibir leaf + intermedios
  -> construir cadena hasta trust anchor
  -> verificar validez, nombre, uso, política
  -> opcional: verificar pin / CT / emisor esperado
  -> solo entonces enviar secretos
```

El bug no es "el certificado es self-signed." Self-signed puede ser correcto en un sistema privado si se confía explícitamente. El bug es aceptar una identidad sin un trust path deliberado.

## Técnicas / patrones

- Buscar `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`, `curl -k`, trust managers personalizados de confiar-todo, y verificación de hostname deshabilitada.
- Inspeccionar SANs, emisor, expiración, key usage, y path de cadena con `openssl`.
- Verificar si las CAs privadas están con scope a clientes internos en lugar de agregadas ampliamente a dispositivos de usuarios.
- Verificar el tipo de pin: pin de cert leaf, pin SPKI, pin de CA, o restricción del trust store.
- Verificar la rotación del pin. Debe haber al menos pins actuales y siguientes o un canal de actualización seguro.
- Usar monitoreo de Certificate Transparency para nombres públicos.

## Variantes y bypasses

Las fallas de validación se agrupan en **5 familias**.

### 1. Verificación deshabilitada

Los flags de desarrollo escapan a producción. La conexión está cifrada, pero la identidad no está autenticada.

### 2. Verificación de hostname omitida

La cadena es válida para algún nombre, pero no el nombre solicitado. Los atacantes con cualquier certificado válido para un dominio controlado pueden hacerse pasar por alguien si las verificaciones de nombre están deshabilitadas.

### 3. Trust store demasiado amplio

La app confía en cada CA instalada en el OS/usuario cuando debería confiar solo en una CA privada o clave de servicio pinned. Los roots enterprise, los roots instalados por malware, y los proxies locales se convierten en parte de la frontera de confianza.

### 4. Pinning frágil

La app pina un único certificado leaf y no tiene backup. La rotación normal rompe los clientes, así que los equipos deshabilitan el pinning durante los incidentes.

### 5. Puntos ciegos de revocación y CT

La verificación de revocación es inconsistente en los clientes, y CT es usualmente monitoreo más que bloqueo. Los atacantes pueden explotar el tiempo entre la emisión, la detección, y la respuesta.

## Impacto

Ordenado aproximadamente por severidad:

- **Intercepción de credenciales/tokens.** MITM puede leer bearer tokens si el cliente acepta el par incorrecto.
- **Manipulación de respuestas de API.** Los clientes autenticados procesan respuestas controladas por el atacante.
- **Compromiso de actualización.** Los canales de actualización de software que omiten la validación pueden instalar artefactos maliciosos.
- **Blast radius de CA privada.** Los roots internos con exceso de confianza pueden hacerse pasar por servicios no relacionados.
- **Fallo de disponibilidad.** El mal pinning puede bloquear flotas enteras móviles o IoT.

## Detección y defensa

Ordenado por efectividad:

1.
**Mantener habilitada la validación de certificados de plataforma.**
   Las stacks TLS por defecto son usualmente más seguras que los validadores personalizados. Override solo con trust anchors estrechos y revisados.

2.
**Verificar hostnames e identidad intendida.**
   La validez de la cadena no es suficiente. El certificado debe ser válido para el nombre DNS exacto o identidad de servicio que se está contactando.

3.
**Usar confianza privada con scope para sistemas internos.**
   El mTLS interno o la identidad de workload deben confiar en roots internos solo donde sea necesario, no globalmente a través de browsers y dispositivos de usuarios.

4.
**Pinar solo cuando el threat model lo justifique.**
   El pinning ayuda a apps móviles, APIs de alto riesgo, y clientes controlados. Requiere pins de backup, telemetría, y un playbook de rotación.

5.
**Monitorear CT y expiración.**
   CT detecta emisión inesperada de cert público; el monitoreo de expiración detecta el fallo operacional más común.

### Qué no funciona como defensa primaria

- **"Usa HTTPS."** HTTPS sin validación es encryption hacia una parte desconocida.
- **`curl -k` en scripts de producción.** Esto deshabilita la verificación de identidad.
- **Certificado self-signed sin distribución de confianza.** El cliente debe confiar explícitamente en el certificado o CA correcto.
- **Un único pin de leaf para siempre.** Los certificados rotan; los pins frágiles se convierten en interrupciones.
- **Depender solo de la revocación.** El comportamiento de revocación es inconsistente; la prevención y el monitoreo ambos importan.

## Labs prácticos

### Inspeccionar una cadena de certificados

```
HOST=example.com
echo | openssl s_client -connect "$HOST:443" -servername "$HOST" -showcerts 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```

Verificar si el SAN coincide con el hostname y el certificado está dentro de su ventana de validez.

### Detectar verificación deshabilitada en un codebase

```
rg -n "verify\\s*=\\s*False|rejectUnauthorized\\s*:\\s*false|InsecureSkipVerify|TrustAll|curl\\s+-k|--insecure" .
```

Cada match necesita revisión de entorno y threat model.

### Comparar hostnames válidos e inválidos

```
openssl s_client -connect example.com:443 -servername example.com -verify_hostname example.com </dev/null
openssl s_client -connect example.com:443 -servername example.com -verify_hostname wrong.example </dev/null
```

El segundo comando debe fallar la verificación de hostname.

### Extraer un candidato a pin SPKI

```
HOST=example.com
echo | openssl s_client -servername "$HOST" -connect "$HOST:443" 2>/dev/null \
  | openssl x509 -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary | openssl base64
```

Pinar SPKI es usualmente más amigable con la rotación que pinar el cert leaf completo, pero todavía necesita pins de backup.

## Ejemplos prácticos

- Una app móvil establece `TrustAllCerts` durante el testing y lo shipea, permitiendo al Wi-Fi MITM capturar API tokens.
- Un CLI interno usa `curl -k` contra producción porque una CA intermedia faltaba una vez.
- Una service mesh confía tanto en el WebPKI público como en la CA interna para el tráfico de workload, expandiendo quién puede hacerse pasar por servicios internos.
- Una app de banca móvil pina un cert leaf y se rompe durante la rotación planificada del certificado.
- El monitoreo CT alerta sobre un certificado para un subdominio sensible emitido por una CA inesperada.

## Notas relacionadas

- [[tls-handshake-and-pki]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[tls-https|TLS / HTTPS]]

## Referencias

- **Estándar / RFC:** RFC 5280: Internet X.509 Public Key Infrastructure Certificate and CRL Profile — https://www.rfc-editor.org/rfc/rfc5280
- **Fundamental:** OWASP Pinning Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- **Estándar / RFC:** RFC 6962: Certificate Transparency — https://www.rfc-editor.org/rfc/rfc6962
