# MAC and HMAC

## Definición

Un Message Authentication Code (MAC) es un tag keyed sobre un mensaje que prueba que el mensaje fue producido o aprobado por alguien que conoce la clave secreta compartida. HMAC es la construcción MAC más común: envuelve una función hash criptográfica con una clave secreta para que los verificadores puedan detectar manipulación y falsificación.

## Por qué importa

Los MACs son el workhorse invisible detrás de las cookies firmadas, la verificación de webhooks, la firma de requests de API, la protección de tokens CSRF, la autenticación de registros cifrados, y muchos deployments de JWT. El error común es confundir un hash plain con un MAC. Un hash dice "estos datos tienen esta huella"; un HMAC dice "alguien con esta clave secreta autenticó exactamente estos datos." Esa única palabra, secreto, es la frontera entre un checksum y un control de seguridad.

## Cómo funciona

HMAC responde **3 preguntas**:

1.
**¿Qué mensaje fue autenticado?**
   Los bytes exactos importan. `user=1&admin=false` y `admin=false&user=1` pueden parsear igual en un framework pero son strings de bytes diferentes para HMAC.

2.
**¿Qué clave secreta lo autenticó?**
   El verificador y el firmante conocen la misma clave secreta. Nadie sin la clave debería poder computar un tag válido para un mensaje modificado.

3.
**¿Se verificó el tag de forma segura?**
   El verificador recomputa el HMAC sobre el mensaje recibido y lo compara con el tag recibido con igualdad de tiempo constante.

```
tag = HMAC(secret_key, canonical_message)
valid = constant_time_equal(tag, received_tag)
```

Forma segura de webhook:

```
import crypto from "node:crypto";

function sign(secret, rawBody) {
  return crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
}

function verify(secret, rawBody, receivedHex) {
  const expected = Buffer.from(sign(secret, rawBody), "hex");
  const received = Buffer.from(receivedHex, "hex");
  return expected.length === received.length &&
    crypto.timingSafeEqual(expected, received);
}
```

El bug no es "no ciframos el mensaje." Un MAC no necesita secreto. El bug es "dejamos que un atacante cambie o invente un mensaje sin probar conocimiento de la clave."

## Técnicas / patrones

- Buscar hashes plain usados como firmas: `sha256(secret + message)`, `md5(message)`, `hash(payload)` en cookies o webhooks.
- Verificar si el MAC cubre exactamente los campos críticos para la seguridad: user id, rol, expiración, nonce, method, path, body hash, y key id donde corresponda.
- Verificar la canonicalización antes de firmar. JSON, URLs, query strings, normalización Unicode, y orden de headers pueden crear bugs de "firmó una cosa, parseó otra".
- Verificar la comparación del tag. Los tags HMAC, firmas de API, y tokens de reset deben usar comparación de tiempo constante.
- Verificar la separación de claves. La misma clave no debe autenticar cookies, webhooks, tokens CSRF, y registros cifrados a menos que un KDF derive claves separadas con contexto.
- Verificar la protección contra replay. Un MAC prueba autenticidad, no frescura. Los webhooks y requests firmados usualmente necesitan timestamps, nonces, o tracking de idempotencia.

## Variantes y bypasses

Las fallas de MAC aparecen en **5 familias comunes**.

### 1. Hash plain en lugar de MAC keyed

La aplicación almacena `sha256(payload)` junto a `payload` y trata un hash coincidente como prueba. Cualquiera que pueda editar el payload puede recomputar el hash. Sin clave secreta, no hay autenticidad.

### 2. Construcciones vulnerables a extensión de longitud

Construcciones como `sha256(secret || message)` con hashes de Merkle-Damgard pueden ser vulnerables a extensión de longitud. HMAC fue diseñado para evitar esto. No inventar hashes keyed a mano.

### 3. Autenticación de mensaje parcial

El tag cubre el body pero no el method, path, tenant, o expiración; o firma un string JSON antes de que el servidor agregue metadata de confianza. Los atacantes buscan campos no firmados que igual influyan en la autorización.

### 4. Mismatch de canonicalización

El firmante firma una representación mientras el verificador o la aplicación parsea otra. Ejemplos incluyen parámetros de query duplicados, orden de keys JSON, diferencias de URL decoding, normalización de trailing slash, y formas Unicode mixtas.

### 5. Tags válidos replayables

El tag es válido para siempre porque el mensaje no tiene timestamp, nonce, número de secuencia, ni caché de replay. Un MAC puede probar que el request viejo fue auténtico; no puede probar que sigue siendo apropiado.

## Impacto

Ordenado aproximadamente por severidad:

- **Bypass de autenticación.** Las cookies firmadas o los tags de session-state falsificados pueden convertirse en impersonación de usuario o admin.
- **Falsificación de webhooks.** Eventos falsos de pago, entrega, CI, o proveedor de identidad pueden manejar lógica de negocio.
- **Manipulación de requests.** Los atacantes pueden cambiar monto, destino, tenant, rol, o expiración si esos campos no se autentican.
- **Ataques de replay.** Mensajes válidos viejos vuelven a disparar acciones.
- **Confusión forense.** Los logs muestran un mensaje "firmado", pero la firma cubría una representación más débil que la que usó la aplicación.

El impacto escala cuando el MAC guarda movimientos de dinero, recuperación de cuentas, automatización de releases, provisioning dirigido por webhooks, o estado cross-tenant.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar HMAC estándar o AEAD, nunca hashes keyed inventados.**
   HMAC-SHA-256 sigue siendo el default aburrido y seguro para autenticación de mensajes keyed. Para datos cifrados, preferir AEAD para vincular confidencialidad e integridad.

2.
**Autenticar un mensaje canónico y completo para seguridad.**
   Decidir exactamente qué bytes se firman e incluir cada campo que afecta autorización, routing, expiración, scope de tenant, y manejo de replay.

3.
**Comparar tags en tiempo constante.**
   Usar helpers de plataforma como `crypto.timingSafeEqual` o `hmac.compare_digest`. Primero normalizar la longitud de forma segura, luego comparar.

4.
**Agregar frescura para los requests.**
   Incluir timestamp, nonce, número de secuencia, o event id. Almacenar identificadores vistos recientemente donde el replay tiene impacto real.

5.
**Separar claves por propósito.**
   Derivar claves separadas para cookies, webhooks, CSRF, y registros cifrados. La separación de claves previene que una clave de integración expuesta autentique datos no relacionados.

### Qué no funciona como defensa primaria

- **SHA-256 plain sobre el mensaje.** Un hash plain no tiene secreto ni propiedad de autoría.
- **`sha256(secret + message)`.** Esta es una forma de MAC inventado a mano y puede ser vulnerable a errores de construcción como extensión de longitud.
- **Codificación Base64.** La codificación cambia la representación; no autentica nada.
- **Cifrar sin autenticación.** El ciphertext confidencial puede seguir siendo maleable a menos que se autentique.
- **Verificar solo que existe un header de firma.** La presencia no es verificación.

## Labs prácticos

### Verificar un HMAC de webhook

```
SECRET="lab-secret"
BODY='{"event":"payment.succeeded","amount":1000,"currency":"USD"}'
TAG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -binary | xxd -p -c 256)
echo "$TAG"
printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -binary | xxd -p -c 256
```

Los dos tags coinciden solo cuando se usan exactamente los mismos bytes y secreto.

### Mostrar que cambiar un byte rompe el tag

```
SECRET="lab-secret"
BODY1='{"admin":false}'
BODY2='{"admin":true}'
printf '%s' "$BODY1" | openssl dgst -sha256 -hmac "$SECRET"
printf '%s' "$BODY2" | openssl dgst -sha256 -hmac "$SECRET"
```

Demuestra integridad: cambios pequeños en el mensaje producen tags no relacionados.

### Comparar hash plain y HMAC

```
MSG='user=123&role=user'
printf '%s' "$MSG" | openssl dgst -sha256
printf '%s' "$MSG" | openssl dgst -sha256 -hmac "secret-a"
printf '%s' "$MSG" | openssl dgst -sha256 -hmac "secret-b"
```

El hash plain es público y reproducible; el HMAC depende del secreto.

## Ejemplos prácticos

- Un procesador de pagos firma los cuerpos de webhook con HMAC; el receptor debe validar los bytes del body crudo antes de procesar el evento.
- Una cookie firmada almacena user id y expiración; el HMAC debe cubrir ambos o la expiración puede manipularse.
- Una API firma method, path, timestamp, y body hash; omitir el path deja que una firma válida en un endpoint se repita en otro.
- Un token CSRF es un HMAC sobre session id y nonce; los tokens aleatorios plain también funcionan, pero HMAC permite que el servidor verifique sin estado.
- Una app móvil firma requests con un secreto compartido embebido en la app; una vez extraído, el MAC ya no prueba un cliente de confianza.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[jwt-cryptographic-correctness]]
- [[kdf-and-key-stretching]]
- [[session-management|Session Management]]
- [[api-auth-flaws|API Auth Flaws]]

## Referencias

- **Estándar / RFC:** NIST FIPS 198-1: The Keyed-Hash Message Authentication Code — https://csrc.nist.gov/publications/detail/fips/198/1/final
- **Estándar / RFC:** RFC 2104: HMAC — https://www.rfc-editor.org/rfc/rfc2104
- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
