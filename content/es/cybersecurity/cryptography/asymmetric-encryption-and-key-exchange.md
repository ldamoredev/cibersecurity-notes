# Asymmetric Encryption and Key Exchange

## Definición

La encryption asimétrica y el intercambio de claves usan diferentes roles de clave para que dos partes puedan establecer secreto sin compartir previamente una clave simétrica. En la práctica, la criptografía de clave pública rara vez se usa para cifrar mensajes grandes directamente; se usa para acordar o envolver claves simétricas, y luego AEAD simétrico protege los datos reales.

## Por qué importa

TLS, age, mensajería estilo Signal, PGP, SSH, passkeys, package signing, y cloud KMS dependen del pensamiento clave pública/privada. La trampa mental común es "la cripto de clave pública cifra datos." A veces, pero no generalmente. La mayoría de los sistemas reales usan operaciones de clave pública para resolver el problema de distribución: ¿cómo dos partes que no comparten ya un secreto terminan con un secreto compartido que los atacantes no pueden computar?

## Cómo funciona

El patrón aplicado tiene **4 partes en movimiento**:

1.
**Claves de identidad de largo plazo**
   Una parte puede tener una clave privada y clave pública estables. La clave pública puede compartirse; la clave privada no debe salir de su frontera.

2.
**Acuerdo de clave efímera**
   Cada lado crea un par de claves temporales fresh y usa Diffie-Hellman o ECDH para derivar un secreto compartido. X25519 es el caso común moderno.

3.
**Derivación de clave**
   El secreto compartido no se usa directamente como clave de encryption. Un KDF como HKDF lo convierte en claves con contexto.

4.
**Protección simétrica**
   AEAD como AES-GCM o ChaCha20-Poly1305 cifra y autentica el payload.

```
Alice efímera privada a, pública A = aG
Bob efímero privado b, público B = bG

Alice computa shared = aB
Bob computa shared = bA

Ambos derivan claves con HKDF(shared, transcript_context)
Luego usan AEAD para datos de aplicación
```

El bug no es "usamos RSA en lugar de curvas elípticas." El bug es usualmente "fallamos en autenticar al par, reutilizamos la clave incorrecta, omitimos la validación, o confundimos acuerdo de clave con confianza."

## Técnicas / patrones

- Identificar si el sistema necesita encryption hacia un receptor, acuerdo de clave entre pares, o firmas para autoría.
- Verificar si la clave pública está autenticada. Una clave pública de un atacante es simplemente una identidad controlada por el atacante.
- Verificar forward secrecy. El DH efímero significa que el compromiso futuro de una clave de largo plazo no descifra sesiones viejas.
- Verificar separación de claves. Los secretos compartidos deben pasar por un KDF con contexto, transcript, algoritmo, y etiquetas de propósito.
- Verificar elecciones de curva y parámetros. Preferir X25519/X448 para acuerdo de clave donde estén soportados; evitar grupos DH personalizados.
- Verificar uso de RSA. La encryption RSA legacy debe usar OAEP, no PKCS#1 v1.5. TLS moderno no usa transporte de clave RSA.

## Variantes y bypasses

Las fallas de secreto asimétrico caen en **5 familias**.

### 1. Encryption de clave pública

El emisor cifra con la clave pública del receptor, y el receptor descifra con la clave privada. La encryption directa de clave pública está limitada en tamaño, así que los sistemas de producción usan hybrid encryption: generar una clave de datos aleatoria, cifrar datos con AEAD, luego envolver la clave de datos con la clave pública del receptor o la clave KMS.

### 2. Intercambio de claves sin autenticación

El Diffie-Hellman plain crea un secreto compartido pero no prueba quién está del otro lado. Un man-in-the-middle puede establecer secretos separados con cada par a menos que el intercambio esté autenticado con certificados, firmas, pre-shared keys, o un protocolo de identidad verificado.

### 3. Claves estáticas sin forward secrecy

Si las claves de sesión viejas pueden recomputarse después de que una clave de largo plazo se filtre, el tráfico viejo queda legible. El DH efímero en TLS 1.3 previene esa clase.

### 4. Parámetros inválidos o débiles

Curvas no seguras, grupos DH pequeños, validación faltante de clave pública, o aceptar puntos de orden bajo pueden colapsar el acuerdo de clave. Las librerías modernas ocultan la mayoría de esto; las implementaciones personalizadas frecuentemente no.

### 5. Confusión de claves

Una clave destinada a firmar se usa para encryption, o una clave de encryption se acepta como clave de identidad. Los diferentes algoritmos y usos de clave necesitan metadata explícita y enforcement.

## Impacto

Ordenado aproximadamente por severidad:

- **Descifrado man-in-the-middle.** El intercambio de claves no autenticado deja que un atacante se siente entre los pares y lea o altere el tráfico.
- **Exposición de tráfico histórico.** La falta de forward secrecy significa que un futuro compromiso de clave descifra capturas viejas.
- **Confusión de receptor.** Los datos cifrados para la clave pública incorrecta son secretos para el receptor intendido y disponibles para el equivocado.
- **Mal uso de KMS.** Envolver claves de datos sin contexto o separación de política puede cruzar fronteras de tenant o entorno.
- **Riesgo de downgrade.** El transporte de clave legacy o grupos débiles pueden forzarse si la negociación no está autenticada.

La severidad escala cuando el intercambio protege cookies de autenticación, tokens, mensajes privados, backups, o secretos de deployment.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar implementaciones a nivel de protocolo en lugar de primitivos raw.**
   TLS 1.3, age, sealed boxes de libsodium, protocolos basados en Noise, y envelope encryption de KMS resuelven detalles de parámetros y composición que el código de aplicación usualmente se equivoca.

2.
**Autenticar el intercambio de claves.**
   Certificados, claves públicas pinned/verificadas, firmas sobre el transcript, o pre-shared keys previenen la sustitución man-in-the-middle.

3.
**Preferir Diffie-Hellman efímero para sesiones.**
   X25519 efímero o equivalente da forward secrecy. Las claves de largo plazo deben autenticar el intercambio, no convertirse en la clave de sesión.

4.
**Usar un KDF con contexto explícito.**
   Derivar claves separadas para encryption, MAC, export, y diferentes direcciones del protocolo. Incluir nombre de protocolo y transcript cuando estén disponibles.

5.
**Hacer cumplir metadata de uso de clave.**
   Una clave de firma no debe descifrar; una clave de encryption no debe firmar; una clave de test no debe confiarse en producción.

### Qué no funciona como defensa primaria

- **"La clave pública es pública, así que cualquier clave pública está bien."** Pública no significa de confianza. Todavía hay que saber de quién es la clave pública.
- **DH estático sin autenticación.** Puede crear un secreto, pero no necesariamente con el par intendido.
- **RSA PKCS#1 v1.5 encryption para nuevos diseños.** OAEP es el padding seguro de encryption RSA, y muchos diseños modernos evitan la encryption RSA por completo.
- **Cifrar datos grandes directamente con operaciones de clave pública.** La hybrid encryption es el diseño normal.
- **Confiar en key ids sin verificar el material de clave y el emisor.** Un key id es metadata de routing, no prueba.

## Labs prácticos

### Derivar un secreto compartido con X25519 usando OpenSSL

```
openssl genpkey -algorithm X25519 -out alice.key
openssl genpkey -algorithm X25519 -out bob.key
openssl pkey -in alice.key -pubout -out alice.pub
openssl pkey -in bob.key -pubout -out bob.pub
openssl pkeyutl -derive -inkey alice.key -peerkey bob.pub -out alice.shared
openssl pkeyutl -derive -inkey bob.key -peerkey alice.pub -out bob.shared
cmp alice.shared bob.shared && echo "mismo secreto compartido"
```

Ambos lados derivan el mismo secreto sin enviar la clave privada.

### Mostrar por qué se necesita un KDF después de DH

```
openssl kdf -keylen 32 \
  -kdfopt digest:SHA256 \
  -kdfopt key:$(xxd -p -c 256 alice.shared) \
  -kdfopt info:"lab encryption key" \
  HKDF
```

El secreto compartido se convierte en una clave con propósito; diferentes etiquetas `info` deben producir claves diferentes.

### Modelar hybrid encryption

```
1. data_key aleatorio = 32 bytes
2. ciphertext = AEAD_Encrypt(data_key, plaintext, associated_data)
3. wrapped_key = PublicKey_Encrypt(recipient_public_key, data_key)
4. package = {wrapped_key, nonce, associated_data, ciphertext, tag}
```

Este es el modelo mental normal para encryption de clave pública a escala de producción.

## Ejemplos prácticos

- TLS 1.3 usa intercambio de claves efímero autenticado para derivar claves de sesión, luego AEAD protege los datos de aplicación.
- Un sistema de backup cifra cada archivo con una clave de datos aleatoria y envuelve esa clave usando una clave pública de cloud KMS o clave vinculada a política.
- Una herramienta de compartición segura de archivos cifra para la clave pública de cada receptor envolviendo una clave de archivo compartida una vez por receptor.
- Un cliente SSH confía en la clave de host del servidor tras la primera verificación; una clave cambiada es una señal potencial de MITM.
- Un protocolo de mensajería usa claves de identidad de largo plazo para autenticar claves de sesión efímeras, preservando forward secrecy.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[digital-signatures]]
- [[kdf-and-key-stretching]]
- [[tls-handshake-and-pki]]
- [[certificate-validation-and-pinning]]
- [[end-to-end-encryption|End-to-End Encryption]]

## Referencias

- **Estándar / RFC:** NIST SP 800-56A Rev. 3: Pair-Wise Key Establishment — https://csrc.nist.gov/publications/detail/sp/800-56a/rev-3/final
- **Estándar / RFC:** RFC 7748: Elliptic Curves for Security — https://www.rfc-editor.org/rfc/rfc7748
- **Investigación / Deep Dive:** Real-World Cryptography, David Wong — Chapter 6
