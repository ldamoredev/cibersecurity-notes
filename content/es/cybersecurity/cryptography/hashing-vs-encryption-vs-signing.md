# Hashing vs Encryption vs Signing

## Definición

Hashing, encryption y signing son tres primitivos criptográficos diferentes que resuelven tres problemas diferentes: hashing produce una huella de tamaño fijo y unidireccional de los datos; encryption transforma los datos para que solo el poseedor de la clave pueda leerlos; signing produce un token que prueba que un poseedor específico de clave autorizó un mensaje específico. Casi todos los bugs de "usamos cripto" son en realidad bugs de "usamos el primitivo equivocado".

## Por qué importa

El error criptográfico más común en sistemas reales es elegir el primitivo incorrecto: hashear una contraseña con SHA-256 (rápido, sin stretching), "cifrar" datos con un hash (imposible — es unidireccional), "firmar" una sesión cifrando con un secreto compartido (eso es un MAC, no una firma), o "verificar" identidad con un hash que cualquiera puede recomputar. Saber qué *garantiza* cada primitivo es el requisito de entrada para leer correctamente las fallas de TLS, JWT, almacenamiento de contraseñas, MFA y gestión de secretos.

## Cómo funciona

Los tres primitivos se distinguen por **dirección**, **modelo de clave** y **qué prueban**:

1.
**Hashing** — unidireccional, sin clave, output de tamaño fijo. Dado el input *m* se computa `H(m)`. No hay función inversa. La garantía es *integridad*: si `H(m)` coincide con un valor conocido, el input es el mismo. No hay secreto ni garantía de autoría. Ejemplos: SHA-256, SHA-3, BLAKE2, BLAKE3.

2.
**Encryption** — bidireccional (con clave), tamaño de output ≈ tamaño de input + overhead. Dado el input *m* y la clave *k* se computa `Enc(k, m) = c`, y `Dec(k, c) = m`. La garantía es *confidencialidad*: solo los poseedores de la clave pueden leer *m*. Por sí sola, la encryption **no** prueba autoría ni detecta manipulación — para eso existe AEAD (authenticated encryption) o un MAC separado.

3.
**Signing** — prueba de autoría asimétrica. Dada la clave privada `sk` y el mensaje *m*, el firmante computa `Sign(sk, m) = σ`. Cualquiera con la clave pública `pk` puede ejecutar `Verify(pk, m, σ)` y saber si el poseedor de `sk` realmente produjo la firma. La garantía es *autenticidad* y *no repudio*. Ejemplos: RSA-PSS, ECDSA, Ed25519.

```
hash:      H(m) -> digest                  (sin clave, sin inversa)
encrypt:   Enc(k, m) -> c    Dec(k, c) -> m (simétrico o asimétrico)
sign:      Sign(sk, m) -> σ  Verify(pk, m, σ) -> bool
```

El bug no es "usamos mal la cripto"; es "elegimos un primitivo cuya garantía no corresponde al threat model." Un chequeo de igualdad de contraseña necesita hashing keyed y lento. Un chequeo de session token necesita un MAC o firma. Un campo confidencial en reposo necesita AEAD. El hashing solo nunca resuelve confidencialidad, el cifrado sin MAC nunca resuelve autenticidad, y la firma nunca resuelve secreto.

## Técnicas / patrones

El modelo de razonamiento es: *¿contra qué amenaza nos defendemos, y qué primitivo prueba la ausencia de esa amenaza?*

- **¿Qué necesita mantenerse secreto?** Confidencialidad → AEAD encryption (ej. AES-GCM, ChaCha20-Poly1305).
- **¿Qué necesita ser infalsificable pero legible?** Integridad + autenticidad, sin secreto → MAC (HMAC) o firma.
- **¿Qué necesita ser infalsificable *y* secreto?** Encrypt-then-MAC, o AEAD.
- **¿Qué necesita ser no repudiable a través de fronteras de confianza organizacional?** Firma, no MAC. Un verificador de MAC tiene la misma clave que el firmante, por lo que podría haber producido el MAC él mismo; eso rompe el no repudio.
- **¿Qué necesita ser solo una huella?** Hash. Pero no para contraseñas (ver [[password-hashing]]).
- **Patrón de sondeo en code review:** encontrá cada llamada a `hash`, `encrypt`, `sign`, `verify`, `compare`, o `==` sobre datos con forma de secreto. Para cada una, preguntarse "¿contra qué amenaza defiende esto, y este primitivo realmente defiende contra eso?"

## Variantes y bypasses

La familia de primitivos se divide en 5 subcategorías útiles que aparecen en sistemas reales. Conocerlas previene la confusión más común.

### Hash plain (sin clave)

SHA-256 de un valor. Cualquiera puede recomputarlo con el mismo input. Útil para content-addressing, chequeo de integridad contra un digest conocido, y Merkle trees. Inútil para almacenamiento de contraseñas (sin lentitud, sin secreto), inútil para "firmar" (sin clave, sin autoría), y nunca apropiado para HMAC por sí solo.

### Hash keyed / MAC

HMAC-SHA-256, KMAC, BLAKE3 con clave. Dos partes que comparten una clave pueden probar que un mensaje fue creado por *alguien con la clave*. Simétrico: verificador y firmante son intercambiables. Esto es un tag, no una firma. Los JWTs con `alg=HS256` son MACs, no firmas.

### Encryption simétrica

AES-GCM, ChaCha20-Poly1305, AES-CBC + HMAC. Ambas partes comparten una clave. Solo los poseedores de la clave pueden descifrar. Los modos AEAD también detectan manipulación. CBC + HMAC requiere orden cuidadoso (encrypt-then-MAC).

### Encryption asimétrica

RSA-OAEP, ECIES, hybrid encryption (cifrar la clave simétrica de datos con la clave pública, cifrar el payload con esa clave de datos). El emisor usa la clave *pública* del receptor, el receptor descifra con su clave *privada*. Más lenta que la simétrica y limitada por ancho de banda; casi siempre se usa en modo híbrido.

### Firma digital

RSA-PSS, ECDSA, Ed25519. El firmante usa la clave *privada*, cualquiera usa la clave *pública* para verificar. La firma prueba autoría e integridad, no secreto. WebAuthn, autenticación de servidor TLS, code signing, JWT `alg=RS256`/`ES256`/`EdDSA`, package signing, y firmas PGP viven aquí.

## Impacto

Elegir el primitivo incorrecto escala casi linealmente con cuánta confianza parece tener el artefacto incorrecto:

- Hashear una contraseña sin stretching → toda la base de datos de contraseñas es crackeable con una GPU farm.
- Encryption sin autenticación → ataques de padding oracle (ej. CBC sin MAC), ataques de bit-flip, maleabilidad del ciphertext, y corrupción silenciosa.
- Hashear en lugar de MAC para tokens → cualquiera que pueda leer el token puede forjar otros nuevos.
- MAC en lugar de firma para tokens cross-org → cualquiera de las partes puede alegar que la otra forjó el mensaje; se pierde el no repudio.
- Firmar sin verificar → sin seguridad alguna (un bug sorprendentemente común; el verificador nunca se conectó).
- Firmar el campo incorrecto → se "firmó" el metadata pero no el body; el atacante intercambia el body.

La severidad escala aún más cuando el artefacto cruza fronteras de confianza (multi-tenant, cross-organization, espejo público) o gobierna autenticación, pagos, o release artifacts.

## Detección y defensa

Ordenado por lo que funciona:

1.
**Elegí el primitivo por la garantía que necesitás, no por el verbo en el requerimiento.**
   "Cifrar la contraseña" casi siempre está mal; el requerimiento es *verificar la contraseña*, lo cual necesita hashing keyed y lento. "Firmar la cookie" casi siempre es en realidad MAC. "Hashear el archivo para integridad" está bien si solo necesitás integridad contra accidentes, pero para manipulación adversarial necesitás un MAC o firma. Traducí los verbos a garantías primero.

2.
**Usá AEAD para encryption por defecto.**
   AES-256-GCM, AES-256-GCM-SIV, ChaCha20-Poly1305. AEAD combina confidencialidad e integridad en un solo primitivo y elimina el bug de orden encrypt-then-MAC.

3.
**Usá HMAC para integridad keyed, no "cifrado con un hash" ni `==`.**
   HMAC-SHA-256 es el workhorse. Comparar con igualdad de tiempo constante (`crypto.timingSafeEqual`, `hmac.compare_digest`) — *no* `==`, que filtra timing.

4.
**Usá firmas para autenticidad cross-trust.**
   Ed25519 es el default moderno; RSA-PSS para compatibilidad; ECDSA-P256 para ecosistemas que lo requieren. Nunca usar ECDSA sin un nonce determinístico (RFC 6979) o un nonce respaldado por CSPRNG — el reuso de nonce filtra la clave privada (incidentes de Sony PS3, wallets de Bitcoin).

5.
**Usá password hashing lento y memory-hard (no hashing de propósito general) para contraseñas.**
   Argon2id, scrypt, bcrypt. SHA-256 de una contraseña no es password hashing — ver [[password-hashing]].

### Qué no funciona como defensa primaria

- **"La hasheamos, así que está segura."** El hashing no es encryption ni firma. Un hash plain provee integridad contra corrupción accidental; no provee nada contra un atacante que puede recomputarlo.
- **"La ciframos, así que no puede manipularse."** La encryption sola no detecta manipulación. Usá AEAD o encrypt-then-MAC.
- **"Usamos SHA-256, que es aprobado por FIPS, así que el almacenamiento de contraseñas está bien."** La aprobación FIPS del primitivo no tiene relación con su aptitud para almacenamiento de contraseñas. SHA-256 es demasiado rápido para ser un verificador de contraseñas.
- **"Lo MACeamos, así que está firmado."** Un MAC es simétrico. Cualquiera de las partes podría haberlo producido. Para autoría cross-organization o auditable, se necesita una firma real.
- **"Comparamos con `==`."** La igualdad naive es vulnerable al timing side-channel en tags, MACs y HMACs. Siempre usá igualdad de tiempo constante.

## Labs prácticos

### Mostrar la diferencia entre hashear, cifrar y firmar los mismos datos

```
# hash
echo -n "hello" | openssl dgst -sha256
# cifrar con AES-GCM (AEAD)
openssl rand -hex 32 > key.hex
KEY=$(cat key.hex)
echo -n "hello" | openssl enc -aes-256-gcm -K "$KEY" -iv $(openssl rand -hex 12) -A -a
# firmar con Ed25519 (firma moderna)
openssl genpkey -algorithm ed25519 -out sk.pem
openssl pkey -in sk.pem -pubout -out pk.pem
echo -n "hello" > m.txt
openssl pkeyutl -sign -inkey sk.pem -rawin -in m.txt -out sig.bin
openssl pkeyutl -verify -pubin -inkey pk.pem -rawin -in m.txt -sigfile sig.bin
```

Comparar qué produce cada operación y qué le permite aprender al verificador.

### Demostrar que la encryption sola no detecta manipulación

```
# cifrar con AES-CBC sin MAC (intencionalmente malo)
openssl rand -hex 32 > key.hex && openssl rand -hex 16 > iv.hex
echo -n "transfer 100 to alice" | openssl enc -aes-256-cbc -K "$(cat key.hex)" -iv "$(cat iv.hex)" -out ct.bin
# flip un bit en el ciphertext
python3 -c "b=open('ct.bin','rb').read(); b=bytearray(b); b[16]^=1; open('ct.bin','wb').write(b)"
# descifrar — la corrupción es silenciosa a menos que la aplicación verifique la forma del plaintext
openssl enc -d -aes-256-cbc -K "$(cat key.hex)" -iv "$(cat iv.hex)" -in ct.bin
```

Resultado: el plaintext está corrupto pero no se lanza ningún error. Repetir con `-aes-256-gcm` (AEAD) y observar que el descifrado falla.

### Demostrar que MAC ≠ firma para no repudio

```
Dos servicios comparten una clave HMAC de 32 bytes. El Servicio A envía un mensaje y un tag HMAC.
El Servicio B puede validar la autoría — pero B también podría haber producido el tag él mismo.
Si B acusa a A de haber enviado un mensaje y A lo niega, el tag no resuelve la disputa.
Con Ed25519: solo A tiene sk_A, así que una firma válida ancla la autoría en A.
```

Por eso JWT `HS256` está bien dentro de una frontera de confianza pero es inapropiado cuando el receptor no debería poder crear tokens.

## Ejemplos prácticos

- Una web app almacena contraseñas de usuarios como `SHA-256(password)`. Una base de datos filtrada se crackea completamente en una sola GPU 4090 en días. Fix: cambiar a Argon2id con parámetros de [[password-hashing]] y forzar re-hashing en el próximo login.
- Un dispositivo IoT usa AES-CBC sin HMAC. Un atacante hace bit-flip en el ciphertext de una actualización de firmware para introducir un bug de parser de un byte y ganar ejecución de código. Fix: AEAD o encrypt-then-MAC.
- Un SaaS usa JWT con `alg=HS256` para autenticar API callbacks cross-tenant. El Tenant B puede crear tokens que parecen ser del Tenant A. Fix: claves por tenant, o cambiar a RS256/EdDSA.
- Un servicio de firma de documentos "firma" documentos aplicándoles HMAC con una clave compartida. Los clientes no pueden probar qué firmante produjo el tag. Fix: firmas reales con claves por firmante.
- Un microservicio "verifica" tokens pero la llamada de verificación devuelve `null` ante una firma mala en lugar de lanzar — y el llamador trata `null` como "válido". Fix: resultado de verificación explícito, fail-closed por defecto.

## Notas relacionadas

- [[symmetric-encryption-modes]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[password-hashing]]
- [[aead-and-nonce-misuse]]
- [[jwt-cryptographic-correctness]]
- [[auth-flaws|Auth Flaws]]
- [[jwt-attacks|JWT Attacks]]

## Referencias

- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Estándar / RFC:** NIST FIPS 180-4 Secure Hash Standard — https://csrc.nist.gov/publications/detail/fips/180/4/final
- **Fundamental:** OWASP ASVS V6 Stored Cryptography — https://github.com/OWASP/ASVS
