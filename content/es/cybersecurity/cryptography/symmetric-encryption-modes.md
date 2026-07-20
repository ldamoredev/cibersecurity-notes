# Symmetric Encryption Modes

## Definición

Un modo de encryption simétrica es el wrapper alrededor de un block cipher (o stream cipher) que decide cómo se divide, rellena, aleatoriza y autentica el plaintext. El block cipher es una pieza (ej. AES); el modo (ECB, CBC, CTR, GCM, GCM-SIV, ChaCha20-Poly1305) es lo que hace que la construcción sea segura o rota en la práctica.

## Por qué importa

"AES es seguro" es una afirmación verdadera pero inútil. AES-ECB filtra patrones del plaintext; AES-CBC sin MAC es maleable; AES-CTR con un nonce reutilizado pierde completamente la confidencialidad; AES-GCM con un nonce reutilizado pierde la autenticación. Casi todos los incidentes reales de "usamos AES y se rompió" son bugs de modo, no bugs del primitivo. Elegir el modo correcto es la línea entre seguro-por-defecto y catastrófico.

## Cómo funciona

Un block cipher solo cifra un único bloque de tamaño fijo (AES = 128 bits). Para cifrar algo más grande, se necesita un modo. Los modos se dividen en 4 familias útiles:

1. **ECB (Electronic Codebook)** — cifra cada bloque independientemente. El mismo bloque de plaintext → el mismo bloque de ciphertext. Filtra patrones. Nunca usar para datos reales.
2. **CBC (Cipher Block Chaining)** — XORea cada bloque de plaintext con el bloque de ciphertext anterior, luego cifra. Necesita un IV aleatorio por mensaje. Solo confidencialidad — *no* detecta manipulación.
3. **CTR (Counter)** — convierte el block cipher en un stream cipher cifrando un contador y haciendo XOR del resultado con el plaintext. Solo confidencialidad. Catastrófico si el par (clave, nonce) alguna vez se repite.
4. **AEAD (Authenticated Encryption with Associated Data)** — combina confidencialidad + integridad + datos opcionales "associated data" no cifrados que también se autentican. AEADs modernas: AES-GCM, AES-GCM-SIV, ChaCha20-Poly1305, AES-OCB. AEAD es el default para nuevos diseños.

```
ECB:    block_i -> Enc(k, block_i)                        # nunca usar
CBC:    c_i    = Enc(k, p_i XOR c_{i-1}), c_0 = IV         # necesita MAC encima
CTR:    c_i    = p_i XOR Enc(k, nonce || counter_i)        # reuso de nonce = catastrófico
AEAD:   (c, tag) = Enc(k, nonce, p, aad)                  # default
```

El bug no es "usamos AES"; es "usamos un modo cuyo modo de fallo no corresponde a nuestro threat model." ECB ignora patrones. CBC ignora manipulación. CTR colapsa con reuso de nonce. AEAD sin disciplina de nonce todavía falla.

## Técnicas / patrones

El modelo de razonamiento al revisar una elección de modo:

- **¿Qué primitivo está en uso?** (AES, ChaCha20, 3DES, RC4) — 3DES y RC4 están deprecados; AES-128/256 y ChaCha20 son actuales.
- **¿Qué modo lo envuelve?** (ECB, CBC, CTR, GCM, GCM-SIV, OCB, CCM)
- **¿De dónde viene el IV/nonce?** ¿Aleatorio? ¿Contador? ¿Predecible? ¿Fijo?
- **¿Hay un MAC?** Si el modo no es AEAD, ¿de dónde viene la integridad?
- **¿Se autentica el associated data?** Headers, content-type, key-id, campo de versión — todo esto puede manipularse si no forma parte del AAD.
- **Patrón de sondeo en code review:** grep por `ECB`, `CBC` sin HMAC cerca, loops `XOR` manuales, padding PKCS#7 hecho a mano, `IV = key`, y cualquier lugar donde un nonce es fijo o se deriva solo de la clave.

## Variantes y bypasses

Los 5 modos que realmente hay que reconocer, con sus modos de fallo canónicos:

### ECB — filtración de patrones

Bloques de plaintext de 16 bytes idénticos producen bloques de ciphertext idénticos. El "pingüino ECB" es la demostración de manual. ECB también es vulnerable a reordenamiento de bloques, copy-paste, y ataques de prefijo elegido. No hay escenario en código de aplicación moderno donde ECB sea la respuesta correcta.

### CBC — maleabilidad y padding oracles

CBC es solo confidencialidad. Hacer bit-flip en el IV determina un flip de bits en el primer bloque de plaintext. El padding PKCS#7 combinado con respuestas de error que filtran información crea un padding oracle (POODLE para SSL 3.0; Vaudenay 2002 para CBC general). Fix: cambiar a AEAD, o usar encrypt-then-MAC donde el MAC cubre IV + ciphertext.

### CTR / streaming — catástrofe por reuso de nonce

CTR convierte AES en un stream cipher: `c = p XOR keystream(k, nonce)`. Si el mismo `(k, nonce)` se usa alguna vez dos veces, el XOR de los dos ciphertexts da `p1 XOR p2`, lo que filtra relaciones del plaintext. El overflow del contador, los nonces determinísticos de campos del request, o reutilizar un nonce al reiniciar, todo dispara esto. CTR solo no tiene integridad, así que debe parearse con un MAC.

### AEAD con nonce aleatorio — el default moderno

AES-GCM y ChaCha20-Poly1305 toman `(k, nonce, plaintext, aad)` y producen `(ciphertext, tag)`. El tag vincula el plaintext, ciphertext y AAD. Cualquier manipulación cambia el tag y el descifrado falla. El nonce no debe repetirse para una clave dada — para AES-GCM la construcción segura es o bien un nonce aleatorio de 96 bits (con un presupuesto estricto de rotación de clave) o un contador determinístico dentro de un envelope.

### AEAD con resistencia a mal uso — GCM-SIV / SIV / OCB

AES-GCM-SIV (RFC 8452) y AES-SIV (RFC 5297) son nonce-misuse-resistant: un nonce repetido solo filtra igualdad del mensaje, no el contenido del mensaje. Útil para servicios sin estado donde es difícil garantizar la unicidad del nonce. Más lento que GCM plain pero el margen de seguridad es mucho más grande.

## Impacto

- **ECB sobre datos confidenciales:** la forma del plaintext filtra, a veces el plaintext mismo (si los bloques son predecibles). Fácilmente identificable entre mensajes.
- **CBC sin MAC:** padding oracle → recuperación completa del plaintext. Bit-flipping → modificación dirigida del plaintext.
- **CTR / GCM con reuso de nonce:** confidencialidad y autenticación ambas perdidas; todo el keystream es recuperable para el nonce reutilizado.
- **AEAD sin cobertura AAD de headers:** el atacante intercambia headers (ej. key-id, content-type, recipient) sin invalidar el tag.
- **3DES / RC4 / DES:** roturas a nivel de primitivo; tamaños de clave demasiado pequeños o sesgos demasiado explotables para ser seguros en cualquier modo.

La severidad escala con el acceso del adversario: un observador pasivo del ciphertext CBC es peligroso; un oracle que devuelve "error de padding" vs "error de MAC" es catastrófico.

## Detección y defensa

Ordenado por lo que funciona:

1.
**Default a AES-256-GCM o ChaCha20-Poly1305 con nonces aleatorios de 96 bits (o envelopes de contador).**
   Ambos son AEAD, ambos están bien soportados, ambos son misuse-resistant cuando se usan con disciplina de nonce apropiada. ChaCha20-Poly1305 se prefiere en plataformas sin aceleración hardware AES-NI.

2.
**Usá AES-GCM-SIV o AES-SIV cuando la unicidad del nonce no está garantizada.**
   Workers sin estado, re-cifrado cross-restart, y patrones de "cifrar este blob pequeño con la misma clave para siempre" se benefician de la resistencia a mal uso.

3.
**Autenticar el associated data, no solo el plaintext.**
   Key-id, versión, content-type, recipient, y campos de routing van en el AAD para que la manipulación se detecte. El AAD no está cifrado; está vinculado al ciphertext.

4.
**Gestionar claves, no memorizarlas en el código.**
   KMS, HSM, envelope encryption (data-encryption-key wrapped por key-encryption-key). Rotar claves con versionado para poder descifrar datos viejos mientras los nuevos usan una nueva clave.

5.
**Usar librerías, no primitivos de block cipher directamente.**
   `libsodium`, `cryptography.hazmat` AEAD, Tink, AWS Encryption SDK, age. Las llamadas directas a una API de block cipher de bajo nivel son una señal de alerta.

### Qué no funciona como defensa primaria

- **"Usamos AES, así que estamos seguros."** AES-ECB, AES-CBC sin MAC, y AES-CTR con nonce reutilizado están todos rotos en la práctica.
- **"Usamos un IV largo, así que el IV no puede colisionar."** Un IV largo *aleatorio* de un CSPRNG más una política de rotación suficiente está bien; un IV largo *predecible* (timestamp, contador desde cero en cada reinicio) no lo está.
- **"Hasheamos el ciphertext para integridad."** Un hash plain no tiene clave y no está vinculado a la clave — un atacante puede volver a hashear. Usá un MAC sobre `IV || ciphertext`, o usá AEAD.
- **"El IV es secreto."** Los IVs no son secretos; viajan con el ciphertext. La confidencialidad no debe depender del secreto del IV.
- **"Ciframos-luego-base64 así que está seguro."** La codificación no es encryption. Agregar una capa de base64 no cambia nada sobre confidencialidad o integridad.

## Labs prácticos

### Mostrar el pingüino ECB (filtración de patrones)

```
# requiere imagemagick: brew install imagemagick
curl -L -o tux.png https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/512px-Tux.svg.png
convert tux.png -depth 8 tux.bmp
KEY=$(openssl rand -hex 32)
dd if=tux.bmp of=body.bin bs=54 skip=1
openssl enc -aes-256-ecb -K "$KEY" -nopad -in body.bin -out body.enc
dd if=tux.bmp of=header.bin bs=54 count=1
cat header.bin body.enc > tux-ecb.bmp
open tux-ecb.bmp
```

Resultado: la silueta de Tux sigue siendo visible porque bloques de plaintext idénticos produjeron bloques de ciphertext idénticos. ECB no oculta la estructura.

### Reproducir bit-flipping en CBC

```
from Crypto.Cipher import AES
import os
key = os.urandom(32); iv = os.urandom(16)
pt  = b"transfer 0001 to alice____________"
ct  = AES.new(key, AES.MODE_CBC, iv).encrypt(pt)
iv2 = bytearray(iv); iv2[10] ^= 0x01
pt2 = AES.new(key, AES.MODE_CBC, bytes(iv2)).decrypt(ct)
print(pt2)
```

Resultado: un solo bit flippeado en el IV modifica determinísticamente el primer bloque de plaintext. CBC no detecta manipulación por sí solo.

### Reproducir reuso de nonce en GCM

```
from Crypto.Cipher import AES
key = b"\x00"*32; nonce = b"\x00"*12  # fijo intencionalmente
m1 = b"transfer 100 to alice"
m2 = b"transfer 999 to mallory"
c1, _ = AES.new(key, AES.MODE_GCM, nonce=nonce).encrypt_and_digest(m1)
c2, _ = AES.new(key, AES.MODE_GCM, nonce=nonce).encrypt_and_digest(m2)
xored = bytes(a^b for a,b in zip(c1, c2))
# xored == m1 XOR m2 — el plaintext conocido revela el otro mensaje
```

Resultado: dos ciphertexts bajo el mismo `(key, nonce)` se XORean al XOR de los plaintexts. La confidencialidad se pierde.

### Round-trip de un AEAD ChaCha20-Poly1305 con AAD

```
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
key = ChaCha20Poly1305.generate_key()
aead = ChaCha20Poly1305(key)
nonce = os.urandom(12)
aad = b"key-id=2026-05-01;version=1"
ct = aead.encrypt(nonce, b"sensitive payload", aad)
print(aead.decrypt(nonce, ct, aad))
```

Resultado: manipular `aad` lanza `InvalidTag`. El AAD se autentica aunque no está cifrado.

## Ejemplos prácticos

- Un servicio de backup almacena archivos de clientes con AES-CBC y HMAC-SHA-256 sobre el ciphertext. Migrar a AES-GCM elimina una capa de complejidad (orden encrypt-then-MAC) y elimina una clase de bugs de padding-oracle.
- Un microservicio memoiza una única clave AES-GCM con un nonce determinístico de 96 bits derivado de `(timestamp, contador)`. Tras un reinicio el contador se resetea y los nonces colisionan. Cambiar a GCM-SIV o persistir el estado del nonce.
- Una cookie está "cifrada" con AES-CBC. La aplicación usa el campo de rol descifrado para autorización. Hacer bit-flip en la cookie cambia el rol. Fix: AEAD sobre todo el payload de la cookie, o firmar la cookie.
- Una app de mensajería usa AES-CTR con un nonce aleatorio de 64 bits y sin MAC. El riesgo de birthday en los nonces es real para claves de alto volumen, y no hay integridad. Fix: ChaCha20-Poly1305.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[aead-and-nonce-misuse]]
- [[random-and-csprng-pitfalls]]
- [[kdf-and-key-stretching]]
- [[secrets-management|Secrets Management]]

## Referencias

- **Estándar / RFC:** NIST SP 800-38A Recommendation for Block Cipher Modes — https://csrc.nist.gov/publications/detail/sp/800-38a/final
- **Estándar / RFC:** NIST SP 800-38D GCM and GMAC — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Estándar / RFC:** RFC 8439 ChaCha20 and Poly1305 — https://www.rfc-editor.org/rfc/rfc8439
