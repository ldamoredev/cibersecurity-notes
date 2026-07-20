# Roll-Your-Own Crypto Failures

## Definición

"Roll-your-own crypto" (RYOC) es el patrón de construir primitivos criptográficos personalizados, componer primitivos estándar de maneras no estándar, o implementar cripto conocida desde cero en lugar de usar librerías auditadas. Los fallos de RYOC son las vulnerabilidades que resultan de composiciones incorrectas, supuestos inválidos sobre los primitivos, o invariantes que no se mantienen en todos los contextos de uso.

## Por qué importa

La criptografía moderna es matemáticamente correcta solo bajo condiciones exactas. Los primitivos estándar como AES-GCM o Ed25519 son seguros cuando se usan correctamente porque los cryptographers han especificado y probado esas condiciones. La composición personalizada introduce nuevas superficies de ataque que los cryptographers no han analizado — y los atacantes no tienen que romper el algoritmo subyacente; solo tienen que encontrar la suposición violada en la composición.

## Cómo funciona

El patrón de fallo de RYOC tiene **4 pasos**:

1. **Requisito real:** la aplicación necesita proteger datos, autenticar una afirmación, o verificar integridad.
2. **Primitivo familiar:** el desarrollador elige un primitivo conocido — SHA-256, AES, RSA — porque lo ha visto antes.
3. **Composición inventada:** el desarrollador combina el primitivo de una manera que parece correcta — "ciframos y luego hasheamos" o "usamos la clave de sesión como IV."
4. **Los atacantes atacan la composición:** la construcción tiene una propiedad que el desarrollador no consideró — maleabilidad, inferencia de keystream, oráculo de padding — y eso se vuelve el vector de ataque.

```
// Mal: "encrypt-then-hash" personalizado (no es MAC)
const hash = sha256(key + encrypt(plaintext))

// Bien: AEAD estándar
const {ciphertext, tag} = aes256gcm.seal(key, nonce, plaintext, aad)
```

El bug no es "el developer usó cripto," es "el developer inventó la composición."

## Técnicas / patrones

- Buscar construcciones MAC personalizadas: `hash(key + data)`, `hash(data + key)`, hash de concatenación de cualquier tipo con un secreto.
- Buscar encryption sin autenticación: AES-CBC, AES-CTR, AES-ECB solos sin ningún MAC.
- Buscar IV/nonce estáticos, hardcodeados, o derivados del timestamp.
- Buscar uso "directo" de RSA — PKCS#1v1.5 raw, sin OAEP o PSS.
- Buscar implementaciones de cripto desde cero: funciones de hash custom, stream ciphers ad-hoc, multiplicación de punto ECC manual.
- Buscar compresión antes del cifrado (potencial oracle de compresión como CRIME/BREACH).
- Buscar mensajes de error detallados del descifrado (potencial oracle de padding).

## Variantes y bypasses

Las 7 familias de cripto custom rompible.

### 1. MAC personalizado

`hash(key + message)` es vulnerable a la extensión de longitud con hashes Merkle-Damgård (SHA-256, SHA-1, MD5). El atacante puede extender el mensaje sin conocer la clave. `HMAC-SHA-256` resiste esto. La regla: nunca inventar MACs, usar HMAC.

### 2. Encryption sin autenticación

AES-CBC o AES-CTR sin MAC es maleable: el atacante puede voltear bits conocidos en el ciphertext para modificar el plaintext descifrado. El resultado es modificación de datos no detectada. La regla: usar AEAD (AES-GCM, ChaCha20-Poly1305).

### 3. IV/nonce estático o derivado de fuente predecible

Un IV constante en CBC transforma los primeros bloques en ECB. Un nonce repetido en AES-GCM filtra el keystream. La regla: los IVs/nonces deben ser únicos por mensaje; generados aleatoriamente o con contadores durables.

### 4. Mal uso de RSA

PKCS#1v1.5 encryption es vulnerable al ataque de Bleichenbacher (padding oracle). La implementación directa del cifrado de libro de texto RSA (sin padding) filtra relaciones de plaintext. RSA sin PSS para firmas no tiene seguridad comprobable. La regla: usar RSA-OAEP para encryption, RSA-PSS para firmas, o preferir curvas elípticas.

### 5. Mismatch de parser/canonicalización

El sistema cifra el mensaje como lo serializa el productor, pero lo verifica como lo parsea el consumidor. Si los parsers difieren en espacios, Unicode, encoding, o whitespace, el atacante puede producir un mensaje que el productor acepta como válido pero que el consumidor interpreta diferente. La regla: firmar la representación canónica. Usar formatos con encoding determinístico.

### 6. Side channels de compresión

Comprimir antes de cifrar permite al atacante inferir el plaintext midiendo el largo del ciphertext. CRIME (TLS) y BREACH (HTTP compression) son explotaciones reales. La regla: no comprimir datos sensibles antes del cifrado, o comprimir datos insensibles y secretos por separado.

### 7. Oráculo de error

Los mensajes de error del descifrado que diferencian entre "padding incorrecto" y "MAC incorrecto" o "datos incorrectos" crean oráculos que pueden usarse para descifrar ciphertexts conocidos sin la clave. La regla: siempre verificar autenticidad antes de revelar detalles de error; retornar un error genérico en tiempo constante.

## Impacto

Ordenado aproximadamente por severidad:

- **MAC personalizado (extensión de longitud):** falsificación de mensajes autenticados.
- **Encryption sin autenticación:** modificación de plaintext no detectada; en algunos contextos, descifrado completo.
- **Oráculo de padding:** descifrado de cualquier ciphertext capturado.
- **Nonce/IV estático:** pérdida de confidencialidad, a veces recuperación de keystream.
- **Mal uso de RSA:** descifrado de mensajes capturados (Bleichenbacher), falsificación de firmas.
- **Side channel de compresión:** inferencia del plaintext con acceso a ciphertexts múltiples.

El impacto escala cuando la cripto custom protege sesiones de autenticación, datos de pago, clave privadas, o comunicaciones de alta sensibilidad.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar protocolos y librerías de alto nivel.**
   Para encryption+autenticación: Fernet, libsodium/NaCl, tink. Para TLS: librerías de TLS del sistema operativo con configuración estándar. Para passwords: Argon2id. Para firmas: Ed25519 vía libsodium o equivalente. No componer primitivos manualmente.

2.
**Preferir construcciones "aburridas" y ampliamente auditadas.**
   Una construcción usada por 10 millones de deployments tiene más ojos que una inventada la semana pasada. El costo de "aburrido" es cero; el costo de inventado puede ser el incidente.

3.
**Usar formatos versionados y explícitos para los artefactos criptográficos.**
   Un ciphertext sin versión no puede migrar a un algoritmo diferente sin una ruptura. Un formato que incluye version bytes permite la rotación de algoritmo. Ejemplo: `version(1B) | algorithm(1B) | nonce | ciphertext | tag`.

4.
**Fail closed: si la verificación falla, rechazar y no descifrar.**
   Nunca revelar por qué falló la verificación criptográfica. Un error genérico en tiempo constante es suficiente para el cliente.

5.
**Threat-model la composición, no solo el primitivo.**
   La pregunta de seguridad no es "¿es AES seguro?" sino "¿es segura esta composición específica de AES, SHA-256, y este protocolo de generación de nonce para este threat model?"

### Qué no funciona como defensa primaria

- **"Lo revisé y parece correcto."** Los atacantes encuentran propiedades que los defensores no consideraron.
- **"Es solo para datos internos."** Los datos internos eventualmente cruzan límites de confianza.
- **"Nadie sabe cómo funciona, así que es seguridad por oscuridad."** La oscuridad se resuelve con reverse engineering; la correctitud matemática no.
- **"El primitivo es estándar así que la composición es segura."** La seguridad del primitivo no se hereda a la composición.

## Labs prácticos

### Demostrar extensión de longitud contra MAC personalizado

```
python3 - <<'PY'
import hashlib, struct

def bad_mac(key, msg):
    return hashlib.sha256(key + msg).digest()

# La extensión de longitud agrega datos sin conocer la clave
# usando hashpumpy o manualmente via re-padding
# Solo demostración del concepto:
key = b"secretkey"
msg = b"amount=100"
mac = bad_mac(key, msg)
print("MAC original:", mac.hex()[:16], "...")
print("HMAC resiste extensión; bad_mac no.")
PY
```

### Comparar latencia de error constante vs variable

```
python3 - <<'PY'
import time, hmac, secrets

def timing_unsafe_compare(a, b):
    return a == b

def timing_safe_compare(a, b):
    return hmac.compare_digest(a, b)

secret = secrets.token_bytes(32)
wrong  = b"\x00" * 32

t0 = time.perf_counter_ns()
timing_unsafe_compare(secret, wrong)
print("unsafe:", time.perf_counter_ns() - t0, "ns")

t0 = time.perf_counter_ns()
timing_safe_compare(secret, wrong)
print("safe:  ", time.perf_counter_ns() - t0, "ns")
PY
```

### Auditar uso de primitivos criptográficos crudos

```
rg -n "AES\.new|Cipher\.new|createCipheriv.*cbc|createCipheriv.*ecb|new PaddedBufferedBlockCipher|RSA\.encrypt|PKCS1_v1_5" .
rg -n "sha256\(.+key|sha1\(.+key|md5\(.+key|hashlib\.(sha|md)" .
```

Cada match necesita revisión manual de la composición.

## Ejemplos prácticos

- Una app Python usa `sha256(secret + data)` para autenticar cookies. Un atacante usa length extension para producir cookies con roles de admin adicionales.
- Un servicio de backup cifra chunks con AES-CBC y un IV fijo. Los primeros bloques idénticos entre chunks producen ciphertexts idénticos — filtrando repetición de datos.
- Una API retorna "padding incorrecto" vs "datos incorrectos" como mensajes de error diferentes. Un atacante usa el oracle de padding para descifrar tokens de sesión robados.
- Un generador de QR usa `aes.encrypt(qr_data)` sin MAC. Un atacante voltea bits en el ciphertext para cambiar la URL de destino.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[mac-and-hmac]]
- [[digital-signatures]]
- [[asymmetric-encryption-and-key-exchange]]

## Referencias

- **Fundamental:** "Cryptographic Right Answers" — https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html
- **Investigación / Deep Dive:** "Should You Use HMAC or AEAD for Your Message Authentication?" — https://www.cryptologie.net/article/505/should-you-use-mac-or-hmac/
- **Docs Oficiales:** libsodium Documentation — https://doc.libsodium.org/
