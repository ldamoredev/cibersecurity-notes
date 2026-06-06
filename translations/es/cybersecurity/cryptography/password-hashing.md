# Password Hashing

## Definición

El password hashing es una transformación deliberadamente lenta, memory-hard, salteada y keyed que convierte una contraseña ingresada por el usuario en un verificador que es costoso de brute-forcear incluso cuando la base de datos de verificadores se filtra. *No* es hashing de propósito general (SHA-256), *no* es encryption, y *no* es un MAC — es su propio primitivo construido específicamente para resistir el cracking offline.

## Por qué importa

Casi todas las bases de datos de credenciales filtradas que fueron útiles para los atacantes lo fueron porque el verificador era incorrecto: plaintext, MD5, SHA-1, SHA-256 sin salt, bcrypt de ciclo rápido, o "cifrado" con una clave recuperable. Las GPUs y ASICs modernos pueden computar decenas de miles de millones de hashes SHA-256 plain por segundo. Una función correcta de password hashing hace que ese throughput sea económicamente inútil. Los únicos defaults razonables hoy son Argon2id, scrypt, o bcrypt — elegidos por la aptitud del ecosistema, parametrizados para el hardware actual, y verificados con comparación de tiempo constante.

## Cómo funciona

El password hashing resuelve un problema diferente al del hashing de datos. Los 4 ingredientes:

1. **Lentitud (work factor / iteration count / memory cost).** Una función correcta de password hashing debe tomar CPU significativa e idealmente memoria significativa. El usuario legítimo paga este costo una vez por login. El atacante lo paga por cada intento en un crack offline.
2. **Salt (aleatorio por usuario).** Un salt único por usuario previene la precomputación (rainbow tables) y asegura que dos usuarios con la misma contraseña produzcan verificadores diferentes.
3. **Pepper (secreto del lado del servidor, opcional).** Un secreto para todo el sitio mezclado en el hash que vive fuera de la base de datos (HSM, KMS, env). Si solo se filtra la base de datos, el pepper eleva el costo de cracking de "costoso" a "inviable sin robar también el pepper."
4. **Memory hardness.** Las funciones modernas (Argon2, scrypt) requieren memoria significativa por intento, derrotando el paralelismo barato en GPUs y ASICs.

```
verifier = encode(
    algorithm,         // argon2id, scrypt, bcrypt
    parameters,        // cost / m / t / p
    salt,              // 16 bytes aleatorios por usuario
    H(password, salt, pepper, parameters)
)
```

El bug no es "usamos un hash"; es "usamos un hash que es demasiado rápido y demasiado barato." El password hashing es el único lugar en criptografía donde lo lento es la característica.

## Técnicas / patrones

El modelo de razonamiento al revisar almacenamiento de contraseñas:

- **Aptitud del algoritmo:** Argon2id (RFC 9106) es el default moderno; scrypt es maduro y ampliamente soportado; bcrypt es aceptable hasta 72 bytes de input. PBKDF2 está permitido bajo FIPS pero es el más débil de los cuatro para uso con contraseñas.
- **Aptitud de parámetros:** el costo debe saturar el presupuesto de latencia del lado del usuario en el nodo de producción más pequeño — típicamente 0.25–1 segundo por login. Re-ajustar anualmente.
- **Presencia y forma del salt:** 16 bytes aleatorios mínimo, almacenados *con* el hash (codificados en el verificador).
- **Presencia del pepper:** si el threat model incluye filtración solo de la base de datos, un pepper eleva significativamente el umbral.
- **Forma del verificador:** un string auto-descriptivo (`$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>`) lleva el algoritmo y los parámetros con el hash para que el verificador pueda actualizar entradas viejas en el próximo login.
- **Comparación de tiempo constante:** la comparación del verificador debe usar una función de tiempo constante — el `==` naive en hashes filtra timing.
- **Patrón de sondeo en code review:** grep por `md5(`, `sha1(`, `sha256(` cerca de `password`, `pwd`, `passwd`, `secret`. Buscar cualquier función de hashing personalizada. Verificar que la comparación sea de tiempo constante. Confirmar que hay un salt por usuario.

## Variantes y bypasses

Las 4 funciones de password hashing que verás en la práctica, con sus trade-offs.

### Argon2id (default moderno)

Argon2id es el ganador del Password Hashing Competition (2015), estandarizado como RFC 9106. Combina la resistencia a side-channel de Argon2i con la resistencia a GPU de Argon2d. Parámetros: memory cost `m` en KiB, time cost `t` en iteraciones, paralelismo `p`. Defaults sensatos para 2026: `m = 19 MiB a 64 MiB, t = 2 a 3, p = 1 a 4`, ajustados a ~1 segundo en el nodo objetivo.

### scrypt

scrypt (RFC 7914) fue diseñado para memory hardness. Maduro, ampliamente soportado. Parámetros: `N` (CPU/memory cost, potencia de 2), `r` (block size, usualmente 8), `p` (paralelismo, usualmente 1). Defaults sensatos: `N = 2^17, r = 8, p = 1` para ~256 MiB y ~1 segundo.

### bcrypt

bcrypt (1999) es más viejo pero todavía aceptable. Parámetros: `cost` (work factor, 2^cost). Límite: el input se trunca a 72 bytes; pre-hashear los inputs largos con HMAC-SHA-256 o usar un algoritmo diferente. Defaults sensatos para 2026: `cost = 12 o 13`.

### PBKDF2

PBKDF2 (RFC 8018) es aprobado por FIPS pero el más débil de los cuatro. Usar solo cuando un entorno requiere criptografía validada FIPS 140-3 y Argon2id/scrypt no están disponibles. Defaults sensatos para 2026: PBKDF2-HMAC-SHA-256 con `≥ 600.000` iteraciones, según OWASP.

## Impacto

La severidad está dominada por la velocidad del verificador y el tamaño del espacio de salt + pepper:

- **Almacenamiento en plaintext:** compromiso instantáneo de cada contraseña al filtrarse. Lo mismo para contraseñas "cifradas" de forma reversible.
- **SHA-1 / SHA-256 / MD5 sin salt:** cracking por rainbow table; toda la base de datos rota en horas en hardware de consumo.
- **Hash rápido con salt:** crackeado por GPU a 10⁹ a 10¹⁰ intentos por segundo por tarjeta moderna; las listas de contraseñas comunes limpian millones de usuarios en días.
- **bcrypt con cost 8 / scrypt N bajo / Argon2 t=1 m=4 MiB:** todavía crackeable en hardware dedicado, pero lo suficientemente lento como para que el cracking masivo sea anti-económico.
- **Argon2id con salt y parámetros actuales + pepper:** el cracking offline es en gran medida anti-económico. El riesgo restante se desplaza hacia credential stuffing, phishing, y reutilización de contraseñas — no el verificador en sí.

La severidad escala cuando la contraseña también desbloquea objetivos de alto valor (admin, pago, claves de encryption), cuando el MFA está ausente, y cuando la reutilización de contraseñas entre servicios es probable.

## Detección y defensa

Ordenado por lo que funciona:

1.
**Usar Argon2id con parámetros ajustados a ~1 segundo en el nodo de producción más lento.**
   `m = 19456 KiB (19 MiB), t = 2, p = 1` es el punto de partida recomendado por OWASP a partir de 2024–2026. Re-ajustar anualmente a medida que avanza el hardware.

2.
**Usar un salt por usuario de al menos 16 bytes aleatorios de un CSPRNG.**
   Almacenarlo con el verificador en el string codificado. El salt único por usuario previene rainbow tables y ataques de igualdad de hash entre usuarios.

3.
**Usar un pepper del lado del servidor mantenido fuera de la base de datos.**
   HMAC-SHA-256(pepper, password) antes de hashear, o usar una librería que soporte un secreto del servidor nativamente. El pepper vive en HSM/KMS/env, no en la misma fila SQL que el verificador.

4.
**Comparar en tiempo constante y rehashear al actualizar parámetros.**
   `crypto.timingSafeEqual`, `hmac.compare_digest`, o funciones `verify` de librería que manejan la comparación. Después de un login exitoso, si los parámetros almacenados están por debajo de los objetivos actuales, re-hashear transparentemente con nuevos parámetros.

5.
**Combinar password hashing con rate limiting y MFA.**
   Incluso un verificador perfecto no detiene el guessing online. Throttlear, bloquear, alertar, y preferir MFA resistente a phishing — ver [[mfa-phishing-resistance|MFA Phishing Resistance]].

### Qué no funciona como defensa primaria

- **"Usamos SHA-256 con un salt."** SHA-256 es demasiado rápido. El salting previene rainbow tables pero no ralentiza el costo por intento. Cambiar a Argon2id o scrypt.
- **"Usamos MD5 pero con un salt largo."** MD5 está roto para colisiones y es demasiado rápido. Reemplazar.
- **"Ciframos la contraseña y la desciframos al login."** El descifrado significa que la clave existe; la clave eventualmente se filtrará. Usar una función hash, no encryption.
- **"Almacenamos la contraseña hasheada una vez con bcrypt cost 4."** El cost 4 está por debajo del presupuesto de latencia del usuario legítimo; esto es esencialmente un hash sin salt desde la perspectiva de un cracker.
- **"Comparamos con `==`."** La igualdad naive filtra timing por byte; un atacante puede recuperar el verificador midiendo el timing.
- **"bcrypt limita los inputs a 72 bytes, así que simplemente truncamos."** La truncación silenciosa hace que las contraseñas largas sean equivalentes a sus primeros 72 bytes; las colisiones se vuelven fáciles. Pre-hashear con HMAC-SHA-256 o migrar fuera de bcrypt.

## Labs prácticos

### Hashear una contraseña con Argon2id y verificarla

```
# pip install argon2-cffi
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
verifier = ph.hash("correct horse battery staple")
print(verifier)  # $argon2id$v=19$m=19456,t=2,p=1$...$...
print(ph.verify(verifier, "correct horse battery staple"))
print(ph.check_needs_rehash(verifier))
```

Resultado: el verificador es auto-descriptivo. Comparar el timing de contraseñas correctas vs incorrectas; ambas deben tomar el mismo tiempo.

### Comparar factores de cost de bcrypt y cronometrarlos

```
import bcrypt, time
pw = b"correct horse battery staple"
for cost in (8, 10, 12, 13):
    salt = bcrypt.gensalt(rounds=cost)
    t0 = time.time()
    bcrypt.hashpw(pw, salt)
    print(cost, round(time.time() - t0, 3), "s")
```

Resultado: cada `+1` al cost aproximadamente duplica el tiempo. Elegir el cost más alto donde la latencia de login se mantenga bajo el presupuesto.

### Inventariar verificadores existentes en una app de muestra

```
rg -i "md5\(|sha1\(|sha256\(.+password|hashlib\.md5|new MD5|MessageDigest\.getInstance\(\"MD5\"\)" .
rg -i "hash\(\s*pw\s*\)" .
```

Resultado: una lista de hits no vacía es el backlog de migración.

## Ejemplos prácticos

- Un SaaS importa un CSV legacy con `md5(password)` para 800k usuarios. Plan de migración: en el próximo login exitoso, pre-hashear la contraseña ingresada con el mismo MD5 legacy, comparar contra el verificador almacenado, luego re-hashear con Argon2id y actualizar la fila.
- Una herramienta interna almacena bcrypt con cost 4 porque "probamos cost 12 y ralentizó el login a 700 ms." Esa latencia es el *punto*; aumentar el cost a 12, escalar el servicio de auth horizontalmente, y agregar MFA.
- Un producto self-built "cifra" contraseñas con AES-GCM usando una clave en `config.yml`. La primera filtración del config compromete a cada usuario. Cambiar a Argon2id; eliminar el code path de encryption.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[kdf-and-key-stretching]]
- [[mac-and-hmac]]
- [[random-and-csprng-pitfalls]]
- [[auth-flaws|Auth Flaws]]
- [[session-management|Session Management]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]]

## Referencias

- **Fundamental:** OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **Estándar / RFC:** RFC 9106 Argon2 Memory-Hard Function — https://www.rfc-editor.org/rfc/rfc9106
- **Estándar / RFC:** NIST SP 800-63B Digital Identity Guidelines (Memorized Secret Verifiers) — https://pages.nist.gov/800-63-3/sp800-63b.html
