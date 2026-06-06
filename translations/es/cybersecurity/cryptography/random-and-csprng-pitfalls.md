# Random and CSPRNG Pitfalls

## Definición

Un generador de números pseudoaleatorios criptográficamente seguro (CSPRNG) produce bytes impredecibles apropiados para claves, nonces, session ids, tokens CSRF, salts, y challenges. Las fallas de aleatoriedad ocurren cuando los valores críticos para la seguridad se generan con fuentes predecibles, de baja entropía, repetidas, sesgadas, o influenciadas por el atacante.

## Por qué importa

Muchos controles de seguridad se reducen a "el atacante no puede adivinar este valor antes de que expire." Los session ids, tokens de reset de contraseña, OAuth state, WebAuthn challenges, API keys, claves de encryption, y nonces dependen de ese supuesto. Si la aleatoriedad es débil, la cripto circundante puede ser matemáticamente correcta y aun así fallar completamente. Este es el fallo silencioso debajo de las sesiones rotas, los nonces AES-GCM repetidos, los links de reset predecibles, y las claves duplicadas de VMs.

## Cómo funciona

La aleatoriedad para seguridad tiene **4 requisitos**:

1.
**Suficiente entropía**
   El valor debe provenir de una fuente con suficiente incertidumbre. Un timestamp, PID, nombre de usuario, o contador no es entropía.

2.
**Impredecibilidad**
   Observar outputs anteriores no debe permitirle a un atacante predecir outputs futuros.

3.
**Unicidad donde se requiera**
   Algunos valores, como los nonces, necesitan unicidad bajo una clave. Pueden no necesitar secreto, pero las repeticiones pueden ser catastróficas.

4.
**Uso correcto de la API**
   La aplicación debe usar APIs criptográficas respaldadas por el OS, no PRNGs de propósito general.

```
// Bien: Node CSPRNG
import crypto from "node:crypto";
const token = crypto.randomBytes(32).toString("base64url");

// Mal: PRNG predecible
const token2 = Math.random().toString(36).slice(2);
```

El bug no es "la aleatoriedad es difícil." El bug es usualmente usar una función de aleatorio conveniente donde el diseño necesita un secreto resistente al atacante o un valor único.

## Técnicas / patrones

- Buscar `Math.random`, `random()`, `rand()`, `mt_rand`, `java.util.Random`, timestamps, contadores, UUIDv1, o generación de token hecha a mano.
- Verificar la longitud del token en bits, no en caracteres. La codificación expande o cambia la representación; no crea entropía.
- Verificar si los valores necesitan secreto, unicidad, o ambos. Las claves necesitan secreto; los nonces AES-GCM necesitan unicidad; los session ids necesitan inimaginabilidad.
- Verificar la clonación de VM/container. Los sistemas clonados antes de que los pools de entropía estén listos pueden generar claves o tokens duplicados.
- Verificar fixtures de test y defaults. Los secretos determinísticos "temporales" frecuentemente escapan a producción.
- Verificar el bias de módulo al mapear bytes aleatorios a caracteres o números.

## Variantes y bypasses

Las fallas de aleatoriedad aparecen en **5 familias comunes**.

### 1. PRNG de propósito general usado para secretos

Los PRNGs de lenguaje son frecuentemente determinísticos y optimizados para simulación, no para adversarios. Si un atacante puede inferir el estado de la semilla, los outputs se vuelven predecibles.

### 2. Tokens de timestamp o contador

Los tokens derivados del tiempo, user id, request count, o process id son buscables. Los atacantes pueden acotar el tiempo de creación y brute-forcear el espacio faltante.

### 3. Longitud insuficiente

Un código numérico de 6 dígitos tiene aproximadamente 20 bits de espacio. Puede estar bien con rate limits online estrictos y expiración corta, pero no como secreto bearer de larga duración.

### 4. Reuso de nonce

El reuso de nonce bajo la misma clave rompe los stream ciphers y modos AEAD como AES-GCM y ChaCha20-Poly1305. El reuso puede exponer relaciones del plaintext y a veces claves de autenticación.

### 5. Mapeo sesgado

Usar aritmética de módulo sobre bytes aleatorios para elegir caracteres puede hacer que algunos outputs sean más probables que otros. El sesgo se vuelve explotable cuando el espacio ya es pequeño o muchas muestras son visibles.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de sesión.** Los session ids o tokens de reset predecibles se convierten en bypass de autenticación.
- **Compromiso de clave.** La generación débil de claves puede hacer que los datos cifrados sean brute-forceables.
- **Fallo de AEAD.** Los nonces repetidos pueden destruir la confidencialidad y la integridad.
- **Bypass de CSRF/OAuth.** Los valores de state/challenge predecibles permiten fallas de vinculación de requests.
- **Secretos duplicados en toda la flota.** Las imágenes de VM o containers clonados con estado sembrado generan claves repetidas en todos los sistemas.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar APIs CSPRNG respaldadas por el OS.**
   Usar `crypto.randomBytes`, `crypto.getRandomValues`, `/dev/urandom` a través de librerías vetadas, `secrets` en Python, `SecureRandom` correctamente en Java, y APIs equivalentes de plataforma.

2.
**Diseñar valores por la propiedad requerida.**
   Las claves necesitan secreto; los nonces necesitan unicidad bajo una clave; los salts necesitan unicidad; los challenges necesitan impredecibilidad y frescura. No usar un patrón de generación para cada caso sin nombrar la propiedad.

3.
**Usar longitudes adecuadas.**
   Los session ids, API keys, y tokens de reset generalmente deben usar al menos 128 bits de entropía; 192 o 256 bits es frecuentemente barato y aburrido.

4.
**Dejar que las librerías AEAD generen o gestionen los nonces donde sea posible.**
   Si hay que gestionar nonces, persistir contadores o usar modos misuse-resistant como AES-GCM-SIV cuando el riesgo de repetición es real.

5.
**Testear APIs prohibidas en CI.**
   Las verificaciones estáticas de `Math.random` o `rand()` en paths de auth/cripto capturan muchos errores evitables.

### Qué no funciona como defensa primaria

- **Codificación Base64 o hex.** La codificación no agrega entropía.
- **Hashear un timestamp.** Hashear input predecible da output predecible.
- **UUIDs sin entender la versión.** UUIDv4 es aleatorio; UUIDv1 filtra estructura de tiempo/MAC; los UUIDs no son automáticamente secretos.
- **Solo expiración corta.** La expiración ayuda solo si el guessing también está rate-limited y el espacio es suficientemente grande.
- **"Es solo interno."** Los tokens internos frecuentemente cruzan logs, queues, browsers, y servicios.

## Labs prácticos

### Comparar generación de token predecible y segura

```
node - <<'JS'
const crypto = require("node:crypto");
for (let i = 0; i < 3; i++) {
  console.log("malo", Math.random().toString(36).slice(2));
  console.log("bueno", crypto.randomBytes(32).toString("base64url"));
}
JS
```

Los tokens seguros son más largos y están respaldados por el OS CSPRNG.

### Estimar el espacio de brute-force

```
python3 - <<'PY'
import math
for bits in [20, 32, 64, 128, 256]:
    print(bits, "bits =", f"{2**bits:.3e}", "posibilidades")
PY
```

Los códigos cortos necesitan rate limits porque su espacio de búsqueda es intencionalmente pequeño.

### Detectar APIs de aleatorio prohibidas

```
rg -n "Math\\.random|\\brand\\(|\\bmt_rand\\b|java\\.util\\.Random|new Random" .
```

Cada match en código de token, auth, reset de contraseña, nonce, o generación de clave merece revisión.

### Generar un secreto de 256 bits de forma segura

```
openssl rand -base64 32
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
```

Usar helpers CSPRNG de plataforma en lugar de inventar formatos de token.

## Ejemplos prácticos

- Un link de reset de contraseña usa `md5(user_id + timestamp)`, dejando a los atacantes brute-forcear las URLs de reset para cuentas recientemente solicitadas.
- Un servicio usa `Math.random()` para session ids. El reinicio del proceso re-siembra predeciblemente y las sesiones se vuelven adivinables.
- Una imagen de VM incluye una clave SSH host generada; cada VM clonada tiene la misma identidad.
- Un servicio AES-GCM usa un nonce de timestamp y la alta concurrencia de requests crea colisiones de nonce.
- OAuth state es un contador corto; el CSRF de login se vuelve práctico.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[password-hashing]]
- [[session-management|Session Management]]

## Referencias

- **Estándar / RFC:** NIST SP 800-90A Rev. 1: Random Bit Generation — https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final
- **Estándar / RFC:** NIST SP 800-90B: Entropy Sources — https://csrc.nist.gov/publications/detail/sp/800-90b/final
- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
