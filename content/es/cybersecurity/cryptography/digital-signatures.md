# Digital Signatures

## Definición

Una firma digital es una prueba asimétrica de que una clave privada específica aprobó un mensaje específico. Cualquiera con la clave pública correspondiente puede verificar la firma, pero solo el poseedor de la clave privada debería poder crearla.

## Por qué importa

Las firmas digitales están debajo de los certificados TLS, WebAuthn/passkeys, JWTs firmados, package signing, code signing, actualizaciones de software, firmas PGP, SSH host keys, y audit trails. Son diferentes de los MACs: con un MAC, cada verificador también puede falsificar porque comparten el mismo secreto; con una firma, el verificador solo necesita la clave pública. Esa distinción es por qué las firmas importan a través de fronteras organizacionales.

## Cómo funciona

Las firmas digitales responden **4 preguntas**:

1.
**¿Qué bytes se firmaron?**
   Las firmas se vinculan a bytes, no a intenciones. Si la representación firmada difiere de la representación parseada, el sistema igual puede fallar.

2.
**¿Qué clave privada los firmó?**
   La clave privada crea la firma. Si la clave privada se filtra, la garantía de autoría colapsa.

3.
**¿Qué clave pública los verifica?**
   La verificación prueba solo "la clave privada correspondiente firmó esto." No prueba que la clave pertenece a la entidad que pensás a menos que la clave pública en sí sea de confianza.

4.
**¿El algoritmo es seguro para este ecosistema?**
   Defaults modernos: Ed25519 donde esté disponible, RSA-PSS para compatibilidad RSA, ECDSA P-256 donde lo requieran restricciones de plataforma.

```
signature = Sign(private_key, message)
valid = Verify(public_key, message, signature)
```

Forma mínima de Ed25519:

```
openssl genpkey -algorithm ed25519 -out signing.key
openssl pkey -in signing.key -pubout -out signing.pub
printf "release artifact digest" > message.txt
openssl pkeyutl -sign -rawin -inkey signing.key -in message.txt -out sig.bin
openssl pkeyutl -verify -rawin -pubin -inkey signing.pub -in message.txt -sigfile sig.bin
```

El bug no es "necesitamos encryption." Las firmas no ocultan datos. Prueban autoría e integridad para datos que pueden ser completamente públicos.

## Técnicas / patrones

- Encontrar cada lugar donde el sistema acepta datos firmados: JWTs, SAML, package metadata, webhooks, actualizaciones móviles, API callbacks, passkey assertions.
- Verificar qué bytes exactos se firman y si el parser consume los mismos bytes.
- Verificar la confianza en la clave pública: cadena de certificados, origen JWKS, clave pinned, registro raíz del paquete, credencial del dispositivo, o huella verificada manualmente.
- Verificar las allowlists de algoritmo. Los verificadores deben pinar los algoritmos esperados, no aceptar lo que pida el header del mensaje.
- Verificar rotación y revocación de claves. Las claves viejas necesitan un camino de retiro definido; las claves comprometidas necesitan eliminación de emergencia.
- Verificar el replay de firma. Una firma válida en un mensaje viejo puede necesitar timestamp, challenge, nonce, origin, o vinculación de audience.

## Variantes y bypasses

Las fallas de firma aparecen en **6 familias**.

### 1. Verificación omitida

El sistema parsea el objeto firmado pero nunca llama a la verificación, o ignora el fallo de verificación. Este es el bug de "firma como decoración".

### 2. Clave pública incorrecta de confianza

La firma es válida, pero bajo una clave pública controlada por el atacante. La confusión de JWKS, el fallo de validación de certificado, o aceptar claves públicas embebidas pueden crear esto.

### 3. Confusión de algoritmo

El verificador acepta un algoritmo más débil o diferente al pretendido. JWT `alg=none`, confusión HS256-vs-RS256, y aceptar RSA-PKCS1 donde se requiere RSA-PSS son ejemplos comunes.

### 4. Fallas de nonce en esquemas tipo ECDSA

ECDSA y DSA requieren un nonce fresh e impredecible para cada firma a menos que se use generación determinística de nonce. El reuso de nonce puede revelar la clave privada.

### 5. Metadata firmada pero payload no firmado

El sistema firma un manifiesto pero no los bytes del artefacto, o firma un header pero no el body. Los atacantes intercambian la porción no firmada.

### 6. Vinculación de contexto faltante

La misma firma válida se acepta en el origen, audience, tenant, protocolo, o ventana de tiempo incorrectos porque el mensaje firmado omite el contexto.

## Impacto

Ordenado aproximadamente por severidad:

- **Falsificación de identidad o sesión.** Los tokens firmados aceptados bajo la clave o algoritmo incorrectos se convierten en bypass de autenticación.
- **Compromiso de supply chain.** Las actualizaciones de software, paquetes, o artefactos instalan contenido malicioso si la verificación de firma es débil.
- **Presión de bypass de Passkey/WebAuthn.** Los errores de verificación de origin o challenge socavan la resistencia a phishing.
- **Fallo de no repudio en auditoría.** El sistema no puede probar quién aprobó una acción si las claves son compartidas o la verificación es débil.
- **Envenenamiento del trust store.** Agregar una clave pública de atacante al conjunto de claves de confianza hace que toda firma futura sea válida.

El impacto escala cuando las firmas protegen releases de software, tokens de autenticación, aprobaciones cross-organization, o flujos financieros.

## Detección y defensa

Ordenado por efectividad:

1.
**Tratar la confianza en la clave pública como parte de la verificación.**
   Una firma es significativa solo bajo una clave pública de confianza. Verificar cadenas de certificados, orígenes JWKS, huellas pinned, o raíces de confianza del registro antes de confiar en el resultado de la firma.

2.
**Pinar los algoritmos permitidos por caso de uso.**
   El verificador ya debe saber si espera EdDSA, RS256, ES256, o RSA-PSS. No dejar que headers controlados por el atacante elijan la política de verificación.

3.
**Firmar la decisión de seguridad completa.**
   Incluir sujeto, emisor, audience, expiración, nonce/challenge, origin, tenant, acción, digest del artefacto, y versión donde sea relevante.

4.
**Usar librerías modernas y esquemas de nonce determinístico donde aplique.**
   Preferir Ed25519 por simplicidad donde el soporte del ecosistema exista. Para ECDSA, usar implementaciones vetadas con nonces determinísticos o CSPRNGs fuertes.

5.
**Diseñar rotación y revocación de claves.**
   Mantener los key ids como metadata de routing, no como prueba. Rastrear claves activas, retiradas, y revocadas por separado.

### Qué no funciona como defensa primaria

- **Verificar que existe un campo de firma.** La existencia no es verificación.
- **Confiar en una clave pública incluida por el atacante.** Una firma válida bajo una clave de atacante prueba autoría del atacante, no autoría legítima.
- **Dejar que el token elija el algoritmo.** La negociación de algoritmo dentro de datos no confiables crea bugs de confusión.
- **Firmar solo el texto de display.** Los campos que la máquina hace cumplir deben estar firmados.
- **Usar una sola clave privada en todas partes.** Un único compromiso rompe entonces cada frontera de confianza.

## Labs prácticos

### Firmar y verificar con Ed25519

```
openssl genpkey -algorithm ed25519 -out sk.pem
openssl pkey -in sk.pem -pubout -out pk.pem
printf "amount=100&to=alice" > message.txt
openssl pkeyutl -sign -rawin -inkey sk.pem -in message.txt -out sig.bin
openssl pkeyutl -verify -rawin -pubin -inkey pk.pem -in message.txt -sigfile sig.bin
```

La verificación tiene éxito solo para el mensaje exacto.

### Mostrar vinculación al mensaje

```
printf "amount=900&to=alice" > message.txt
openssl pkeyutl -verify -rawin -pubin -inkey pk.pem -in message.txt -sigfile sig.bin || echo "verification failed"
```

Cambiar el mensaje invalida la firma.

### Inspeccionar una cadena de firma de certificado

```
echo | openssl s_client -connect example.com:443 -servername example.com -showcerts 2>/dev/null \
  | openssl x509 -noout -subject -issuer -text | rg "Subject:|Issuer:|Signature Algorithm"
```

La identidad del servidor TLS depende de firmas encadenadas a una CA de confianza.

## Ejemplos prácticos

- Un JWT con RS256 se acepta solo si el verificador usa la clave pública de confianza del emisor y rechaza la confusión de algoritmo.
- Un autenticador WebAuthn firma un challenge y datos vinculados al origin; la resistencia a phishing depende de verificar el origin y el challenge.
- Un gestor de paquetes verifica las firmas de metadata del repositorio antes de instalar paquetes.
- Un sistema CI/CD firma los artefactos de release para que el deployment pueda rechazar builds manipulados.
- Un cliente SSH alerta cuando la clave de host del servidor cambia porque el vínculo de clave pública cambió.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[jwt-cryptographic-correctness]]
- [[tls-handshake-and-pki]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]]
- [[artifact-integrity|Artifact Integrity]]

## Referencias

- **Estándar / RFC:** NIST FIPS 186-5: Digital Signature Standard — https://csrc.nist.gov/publications/detail/fips/186/5/final
- **Estándar / RFC:** RFC 8032: Edwards-Curve Digital Signature Algorithm — https://www.rfc-editor.org/rfc/rfc8032
- **Estándar / RFC:** RFC 8017: PKCS #1 v2.2 RSA Cryptography Specifications — https://www.rfc-editor.org/rfc/rfc8017
