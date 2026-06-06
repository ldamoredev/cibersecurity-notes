# AEAD and Nonce Misuse

## Definición

AEAD (Authenticated Encryption with Associated Data) es un modo de cifrado que provee confidencialidad e integridad en una sola operación. Cualquier manipulación del ciphertext, el tag, o los associated data hace que el descifrado falle. El nonce misuse ocurre cuando el nonce requerido por el cipher se repite bajo la misma clave, lo cual puede destruir la confidencialidad, la integridad, o ambas.

## Por qué importa

AEAD es la primitiva correcta para la mayoría de las necesidades de encryption. Pero "usar AEAD" no es suficiente — el nonce necesita ser único bajo la clave. AES-GCM, la suite AEAD más desplegada, es especialmente sensible: un único reuso de nonce bajo la misma clave puede exponer el plaintext e incluso la clave de autenticación. La propiedad correcta de nonce (unicidad, no secreto) es diferente a la propiedad correcta de clave (secreto, no necesariamente único), y confundirlas es el error más común en el uso de AEAD.

## Cómo funciona

AEAD toma **3 inputs** y produce 2 outputs:

```
ciphertext, tag = AEAD_Encrypt(key, nonce, plaintext, aad)
plaintext        = AEAD_Decrypt(key, nonce, ciphertext, tag, aad)
                   // falla si tag es inválido
```

- **key**: secreto de larga duración. Nunca debe repetirse con datos sin sentido diferente.
- **nonce** (number used once): único por (clave, mensaje). En AES-GCM es 12 bytes; en ChaCha20-Poly1305 también es 12 bytes. No necesita ser secreto, pero DEBE ser único bajo la misma clave.
- **plaintext**: los datos a proteger.
- **aad** (associated data): datos autenticados pero no cifrados. El tag cubre tanto el ciphertext como el aad.

El esquema de verificación:

```
recibir: nonce, ciphertext, tag, aad
1. calcular tag' = GHASH(key_auth, aad, ciphertext, nonce)
2. comparar tag' con tag en tiempo constante
3. si difieren → rechazar, no descifrar
4. descifrar con keystream derivado de (key, nonce)
```

El bug de nonce misuse más conocido: en AES-GCM, si `nonce_1 == nonce_2` bajo la misma clave, entonces `keystream_1 == keystream_2`. XOR de los dos ciphertexts cancela el keystream y expone la relación entre plaintexts. Además, la clave de autenticación GCM puede recuperarse, permitiendo la falsificación de tags.

## Técnicas / patrones

- Verificar cómo se generan los nonces: ¿aleatorio, contador, o derivado de datos de aplicación?
- Verificar si el estado del contador persiste entre reinicios si se usa un nonce basado en contador.
- Verificar si la misma clave se usa a través de múltiples nodos o procesos con nonces aleatorios independientes.
- Verificar si los associated data cubren todos los campos que deben estar vinculados al ciphertext (ej: version bytes, tenant id, expiration, purpose).
- Buscar `nonce = os.urandom(12)` o equivalente — la mayoría de los lenguajes no tienen un contador global de nonce; la generación aleatoria es el default habitual.
- En escenarios de alta concurrencia o multi-nodo, verificar si la probabilidad de colisión de nonce aleatorio es aceptable para el número esperado de mensajes.

## Variantes y bypasses

Las 5 familias de misuse de AEAD/nonce.

### 1. Colisión de nonce aleatorio

Los nonces de 12 bytes dan aproximadamente 2^96 espacio. Después de ~2^32 mensajes bajo la misma clave, la probabilidad de colisión se vuelve no trivial (paradoja del cumpleaños). La defensa: rotar claves antes de 2^32 operaciones o usar modos de cipher con nonces de 192 bits como XChaCha20-Poly1305.

### 2. Reset del contador de nonce

Un nonce basado en contador persiste solo en memoria. Un reinicio del proceso vuelve el contador a cero. Si la clave no rotó, los nonces se repiten. La defensa: almacenar el estado del contador de forma durable, o usar un CSPRNG si el almacenamiento durable no está disponible.

### 3. Nonce determinístico de campos de baja entropía

Un nonce derivado de timestamp + user_id puede colisionar si dos operaciones ocurren en el mismo segundo para el mismo usuario, o en sistemas con concurrencia alta. La defensa: si se usan nonces determinísticos, asegurarse de que el tuple (key, nonce) sea globalmente único, no solo localmente único.

### 4. Associated data faltante

El ciphertext no está vinculado a su contexto. Un atacante puede mover un ciphertext de un contexto a otro (diferente tenant, diferente versión de protocolo, diferente propósito) y el descifrado tiene éxito porque el tag solo cubre el ciphertext, no el contexto. La defensa: siempre incluir en los associated data cualquier campo que deba estar vinculado al mensaje.

### 5. Reuso de nonce en AES-GCM específicamente

AES-GCM tiene nonce-misuse-sensitivity más alta que ChaCha20-Poly1305 porque la clave de autenticación GCM se puede recuperar con un solo par de nonce repetido. La defensa: preferir AES-GCM-SIV o XChaCha20-Poly1305 cuando el riesgo de reuso de nonce es operacionalmente real.

## Impacto

Ordenado aproximadamente por severidad:

- **Reuso de nonce en AES-GCM:** exposición del plaintext XOR + recuperación de la clave de autenticación → falsificación de tag → pérdida total de confidencialidad e integridad.
- **Reuso de nonce en otros modos AEAD:** exposición del plaintext XOR, puede o no recuperar clave de autenticación según el modo.
- **Associated data faltante:** el ciphertext puede ser movido a un contexto diferente — escalada de privilegios, confusión de tenant, downgrade de protocolo.
- **Nonce predecible:** si el nonce es predecible y hay un oráculo de descifrado, puede ser explotable para ataques elegidos.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar un cipher con nonce sintético o misuse-resistant cuando el riesgo de reuso es real.**
   AES-GCM-SIV (RFC 8452) o XChaCha20-Poly1305 son opciones. AES-GCM-SIV es seguro incluso si un nonce se repite (degrada graciosamente en lugar de romperse catastróficamente).

2.
**Incluir context en los associated data para cada propósito de cipher.**
   Los AAD deben incluir version, tenant, purpose, y cualquier campo que deba estar vinculado al ciphertext. "Ciphertext sin contexto" es un objetivo de cortar-y-pegar.

3.
**Usar nonces aleatorios con rotación de clave antes de 2^32 mensajes.**
   Para AES-GCM con nonces de 12 bytes, el límite de seguridad es 2^32 mensajes por clave. Rotar claves automáticamente, no manualmente.

4.
**Si se usan contadores de nonce, hacer el estado del contador durable.**
   Un contador que vive solo en memoria se resetea con el proceso. Persistir el estado del contador o usar un esquema de generación de nonce que no dependa de estado persistente.

5.
**Diseñar un ciphertext envelope estándar para el sistema.**
   Un envelope como `version(1B) | nonce(12B) | aad_len(2B) | aad | ciphertext | tag(16B)` hace que la generación y el parseo de nonce sean consistentes en todo el código.

### Qué no funciona como defensa primaria

- **"Usamos AEAD, así que estamos bien."** AEAD sin manejo correcto de nonce puede ser catastrófico.
- **"Los nonces son probablemente únicos."** "Probablemente" no es una propiedad de seguridad para confidencialidad.
- **"El nonce está incluido en el mensaje así que el receptor puede verificar la unicidad."** Los receptores generalmente no mantienen estado de todos los nonces pasados. El emisor debe garantizar la unicidad.
- **"Usamos nonces más largos así que las colisiones son más raras."** Los nonces más largos ayudan con la seguridad estadística de la generación aleatoria, pero el riesgo fundamental del reuso de nonce no desaparece.

## Labs prácticos

### Demo de XOR de nonce repetido

```
python3 - <<'PY'
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=128)
aead = AESGCM(key)

nonce = os.urandom(12)  # mismo nonce, dos mensajes
m1 = b"mensaje secreto A"
m2 = b"mensaje secreto B"
ct1 = aead.encrypt(nonce, m1, b"")
ct2 = aead.encrypt(nonce, m2, b"")

# Remover tag (últimos 16 bytes) para comparar keystrams
ks1 = bytes(a ^ b for a, b in zip(m1, ct1[:len(m1)]))
ks2 = bytes(a ^ b for a, b in zip(m2, ct2[:len(m2)]))
print("keystreams iguales:", ks1 == ks2)  # True — nonce misuse
PY
```

### Diseño de envelope AEAD

```
python3 - <<'PY'
import struct, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def seal(key_bytes: bytes, plaintext: bytes, aad: bytes) -> bytes:
    nonce = os.urandom(12)
    tag_included_ct = AESGCM(key_bytes).encrypt(nonce, plaintext, aad)
    return nonce + tag_included_ct

def open_sealed(key_bytes: bytes, envelope: bytes, aad: bytes) -> bytes:
    nonce, ciphertext = envelope[:12], envelope[12:]
    return AESGCM(key_bytes).decrypt(nonce, ciphertext, aad)

key = AESGCM.generate_key(bit_length=256)
env = seal(key, b"datos sensibles", b"tenant:acme:v1")
print(open_sealed(key, env, b"tenant:acme:v1"))
PY
```

Los AAD están vinculados al ciphertext; cambiar los AAD hace que el descifrado falle.

## Ejemplos prácticos

- Un servicio de logging cifra eventos con AES-GCM. Cada evento incluye un nonce aleatorio de 12 bytes. Después de 4.3 mil millones de eventos bajo la misma clave, la probabilidad de colisión de nonce supera el 50%. La solución: rotación de clave programada automáticamente.
- Un sistema de almacenamiento en la nube usa nonce = sha256(path) para que cada path tenga un nonce determinístico. Si dos versiones del mismo archivo se cifran con la misma clave y path, los nonces se repiten. La solución: incluir un número de versión en el nonce o en los AAD.
- Un servicio de cache cifra valores sin AAD. Un atacante que puede escribir en el cache mueve el ciphertext de un usuario a otro. La solución: incluir user_id y propósito en los AAD.

## Notas relacionadas

- [[symmetric-encryption-modes]]
- [[random-and-csprng-pitfalls]]
- [[mac-and-hmac]]
- [[roll-your-own-crypto-failures]]
- [[kdf-and-key-stretching]]

## Referencias

- **Estándar / RFC:** RFC 5116: An Interface and Algorithms for Authenticated Encryption — https://www.rfc-editor.org/rfc/rfc5116
- **Estándar / RFC:** RFC 8452: AES-GCM-SIV — https://www.rfc-editor.org/rfc/rfc8452
- **Investigación / Deep Dive:** "Nonce-Disrespecting Adversaries" — https://eprint.iacr.org/2016/475.pdf
