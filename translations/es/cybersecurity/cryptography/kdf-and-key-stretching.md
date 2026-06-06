# KDF and Key Stretching

## Definición

Una Key Derivation Function (KDF) convierte un secreto en una o más claves criptográficas con propósito definido. El key stretching es un caso de uso relacionado donde un secreto de baja entropía, usualmente una contraseña, se hace deliberadamente costoso de adivinar antes de convertirse en un verificador o clave de encryption.

## Por qué importa

La mayoría de los sistemas no tienen una sola clave prolija. Tienen un secreto raíz, secreto de sesión, contraseña, output de Diffie-Hellman, clave de datos KMS cloud, o secreto de recuperación que debe convertirse en varias claves separadas: clave de encryption, clave MAC, clave client-to-server, clave server-to-client, clave de cookie, clave de backup. Usar el secreto raw en todos lados crea reuso de clave y fallo cross-protocol. Las KDFs son cómo un diseño dice: "esta clave es solo para este propósito."

## Cómo funciona

El uso de KDF se divide en **3 trabajos**:

1.
**Extraer**
   Convertir material de input desparejo en una clave pseudoaleatoria fuerte. Ejemplo: HKDF-Extract sobre un secreto compartido de Diffie-Hellman.

2.
**Expandir**
   Derivar una o más claves con etiquetas y contexto explícitos. Ejemplo: `app:v1:cookie-mac`, `app:v1:record-aead`, `app:v1:webhook-hmac`.

3.
**Estirar**
   Hacer costosos los intentos cuando el input es memorable por humanos o de baja entropía. Ejemplo: PBKDF2, bcrypt, scrypt, o Argon2id para contraseñas.

Forma HKDF:

```
prk = HKDF-Extract(salt, input_key_material)
okm = HKDF-Expand(prk, info="app:v1:purpose", length=32)
```

El bug no es "no hasheamos el secreto." El bug es "reutilizamos un secreto a través de propósitos, o tratamos una contraseña de baja entropía como una clave de alta entropía."

## Técnicas / patrones

- Identificar secretos raíz, master keys, contraseñas, secretos de API, secretos de sesión, y outputs de DH.
- Verificar si cada propósito obtiene una clave derivada separada con una etiqueta clara.
- Verificar si las claves derivadas de contraseña usan una KDF de contraseña, no SHA-256 plain.
- Verificar el uso del salt. Los salts de KDF no son secretos, pero previenen outputs compartidos y precomputación.
- Verificar los strings de contexto. Incluir aplicación, versión, tenant/entorno donde corresponda, dirección, y propósito.
- Verificar la rotación. Las etiquetas y el versionado de KDF deben hacer distinguibles las claves viejas/nuevas durante la migración.

## Variantes y bypasses

Los errores de KDF aparecen en **5 familias**.

### 1. Reuso de secreto raw

El mismo secreto firma cookies, cifra registros, verifica webhooks, y deriva tokens CSRF. Una filtración en un subsistema se convierte en una rotura universal.

### 2. Hash-como-KDF

La aplicación usa `sha256(secret)` o `sha256(password)` como clave. Para input de alta entropía esto puede verse accidentalmente bien, pero carece de contexto, separación extract/expand, y key stretching de contraseña.

### 3. Vinculación de contexto faltante

La KDF deriva bytes pero no etiqueta el propósito. Dos funcionalidades diferentes pueden accidentalmente derivar la misma clave o aceptar los outputs de la otra.

### 4. Confusión de KDF de contraseña

PBKDF2, bcrypt, scrypt, y Argon2id son para contraseñas de baja entropía. HKDF no es una función de password hashing; asume que el material de clave de input ya tiene alta entropía o proviene de un acuerdo de clave.

### 5. Mal salt o migración de parámetros

Salts globales, salts faltantes, conteos de iteración estáticos bajos, o parámetros sin versionar hacen las actualizaciones dolorosas y debilitan la resistencia a la precomputación.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso cross-protocol.** Una clave filtrada de una función de bajo riesgo autentica tokens de alto riesgo en otros lugares.
- **Aceleración del cracking de contraseñas.** Las claves de contraseña derivadas de hashes rápidos son baratas de brute-forcear.
- **Falsificación de tokens.** Las claves de cookie, CSRF, webhook, y reset-token colisionan o reutilizan material.
- **Descifrado de datos tras filtración parcial.** Una clave derivada expuesta revela datos cifrados no relacionados si la derivación no estaba separada.
- **Fallo de migración.** Los outputs de KDF sin versionar hacen difícil rotar algoritmos o parámetros de forma segura.

El impacto escala cuando el secreto raíz es para todo el entorno, compartido entre tenants, o almacenado en source control.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar HKDF o una KDF estándar para material de clave de alta entropía.**
   HKDF es el workhorse común de extract-y-expand. Usar etiquetas `info` explícitas para propósito, versión, y dirección.

2.
**Usar KDFs de contraseña para contraseñas y passphrases.**
   Argon2id, scrypt, bcrypt, o PBKDF2 donde lo requieran restricciones FIPS. Las contraseñas necesitan stretching, salts, y parámetros actualizables.

3.
**Separar claves por propósito.**
   Derivar claves independientes para encryption, MAC, sesiones, cookies, webhooks, y backups. No reutilizar secretos raíz directamente.

4.
**Versionar el contexto de derivación y los parámetros.**
   Incluir etiquetas de versión y almacenar parámetros de KDF junto a los artefactos derivados donde sea necesario. La rotación es un requisito de diseño, no una tarea de limpieza.

5.
**Mantener los secretos raíz en un gestor de secretos o KMS real.**
   Las KDFs no hacen seguros a los secretos raíz hardcodeados. Solo estructuran cómo se usan los secretos después de recuperarlos.

### Qué no funciona como defensa primaria

- **`sha256(password)` como clave de encryption.** Es demasiado rápido y carece de memory hardness.
- **Un secreto de entorno para todo.** La conveniencia convierte las filtraciones pequeñas en compromiso total.
- **Contexto secreto solo en comentarios.** La KDF necesita etiquetas de contexto que la máquina haga cumplir.
- **Un salt global.** Los salts deben ser lo suficientemente únicos para prevenir outputs compartidos y precomputación.

## Labs prácticos

### Derivar dos claves con propósito específico con HKDF

```
ROOT=$(openssl rand -hex 32)
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"app:v1:cookie-mac" HKDF
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"app:v1:record-aead" HKDF
```

Los dos outputs difieren porque las etiquetas de propósito difieren.

### Esquema de separación de claves para una app

```
root_secret desde KMS
  -> HKDF(info="prod:v3:cookie-mac") -> cookie_mac_key
  -> HKDF(info="prod:v3:webhook-hmac:stripe") -> stripe_webhook_key
  -> HKDF(info="prod:v3:record-aead") -> record_encryption_key
  -> HKDF(info="prod:v3:csrf") -> csrf_key
```

Esto convierte un secreto raíz gestionado en claves de aplicación explícitas y separadas.

## Ejemplos prácticos

- TLS deriva claves de tráfico de un secreto de handshake y contexto del transcript.
- Una herramienta de backup deriva claves separadas de encryption de archivos y autenticación de metadata de una clave de archivo.
- Una web app deriva claves de firma de cookie y CSRF de un secreto raíz en lugar de reutilizar los mismos bytes directamente.
- Los gestores de contraseñas estiran una master password antes de desbloquear las claves vault de alta entropía.
- La envelope encryption cloud separa las claves KMS raíz de las claves de datos por objeto.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[password-hashing]]
- [[asymmetric-encryption-and-key-exchange]]
- [[symmetric-encryption-modes]]
- [[secrets-management|Secrets Management]]

## Referencias

- **Estándar / RFC:** NIST SP 800-108r1: Key Derivation Using Pseudorandom Functions — https://csrc.nist.gov/publications/detail/sp/800-108/rev-1/final
- **Estándar / RFC:** RFC 5869: HKDF — https://www.rfc-editor.org/rfc/rfc5869
- **Estándar / RFC:** RFC 8018: PKCS #5 PBKDF2 — https://www.rfc-editor.org/rfc/rfc8018
