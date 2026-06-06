# Post-Quantum Awareness

## Definición

La criptografía post-cuántica (PQC) es el conjunto de algoritmos criptográficos diseñados para ser seguros contra ataques de computadoras cuánticas. La "conciencia post-cuántica" es el conjunto mínimo de contexto que los practicantes de seguridad necesitan para evaluar el riesgo y planificar migraciones: qué primitivos actuales son vulnerables, qué estándares reemplazarlos, cuándo actuar, y cómo construir sistemas crypto-agile.

## Por qué importa

Las computadoras cuánticas suficientemente capaces amenazan la criptografía de clave pública actual (RSA, DH, ECDH, ECDSA, EdDSA). Los sistemas protegidos por esos algoritmos son vulnerables al ataque "harvest now, decrypt later" (HNDL): los adversarios capturan tráfico cifrado hoy con la intención de descifrarlo cuando las computadoras cuánticas estén disponibles. Los datos con períodos de confidencialidad largos — datos de salud, secretos diplomáticos, secretos industriales de largo plazo — ya tienen riesgo medible hoy. El NIST finalizó los primeros estándares PQC en 2024 (FIPS 203, 204, 205), lo que hace que las migraciones de alto riesgo puedan comenzar.

## Cómo funciona

La conciencia PQC tiene **4 conceptos**:

1.
**Primitivos amenazados**
   El algoritmo de Shor corre en un computador cuántico grande y resuelve los problemas subyacentes de RSA (factorización de enteros), DH/ECDH (logaritmo discreto), y ECDSA/EdDSA (logaritmo discreto de curva elíptica) en tiempo polinomial. Esto no es teórico: es el caso matemático probado. La pregunta solo es si y cuándo existirán computadoras cuánticas "criptográficamente relevantes."

2.
**Primitivos menos amenazados**
   La criptografía simétrica (AES, ChaCha20, SHA-256, SHA-3) es afectada por el algoritmo de Grover, que reduce el costo de brute-force de `O(2^n)` a `O(2^(n/2))`. Para AES-128, el costo cae de `2^128` a `2^64` operaciones cuánticas — aún inviable pero con menor margen. La defensa: usar AES-256 y SHA-384 o SHA-512 para longitudes de clave y output dobles, respectivamente. Estos cambios son de bajo costo y se pueden hacer hoy.

3.
**Nuevos estándares NIST (2024)**
   NIST finalizó tres estándares PQC:
   - **FIPS 203** — ML-KEM (CRYSTALS-Kyber): key encapsulation mechanism. Reemplaza RSA-KEM y ECDH para establecimiento de clave.
   - **FIPS 204** — ML-DSA (CRYSTALS-Dilithium): firma digital. Reemplaza RSA-PSS y ECDSA/EdDSA para firmas.
   - **FIPS 205** — SLH-DSA (SPHINCS+): firma digital basada en hash. Alternativa stateless para firmas, tamaños de firma grandes.
   Los algoritmos adicionales (FALCON/FN-DSA) están en aprobación para firmas más compactas.

4.
**Crypto-agility y migración híbrida**
   La transición no es "apagar RSA, encender ML-KEM." Es "desplegar híbridos (clásico + post-cuántico en paralelo), probar interoperabilidad, luego migrar." TLS 1.3 ya soporta extensiones de grupo híbridas (X25519Kyber768). El inventario cripto — saber qué algoritmos están en uso dónde — es el prerequisito para la migración.

```
// Establecimiento de clave híbrido (TLS 1.3 with PQC groups)
// X25519 + ML-KEM-768 en paralelo
// El secreto compartido es KDF(x25519_output || mlkem_output)
// Seguro contra atacante cuántico (ML-KEM) Y atacante clásico (X25519)
```

El bug no es "no usamos PQC todavía." El bug es "no sabemos qué cripto tenemos, qué datos tienen sensibilidad de largo plazo, y no hay un plan."

## Técnicas / patrones

- Inventariar todos los usos de criptografía de clave pública: RSA (cualquier tamaño de clave), ECDH, ECDSA, EdDSA, DH.
- Identificar qué datos tienen requisitos de confidencialidad de largo plazo (> 5-10 años).
- Verificar si las librerías de TLS (BoringSSL, OpenSSL 3.x, rustls) ya soportan grupos híbridos PQC.
- Verificar si los formatos de mensaje/protocolo son crypto-agile: ¿pueden expresar el algoritmo y los parámetros de forma que no requieran un cambio de formato para actualizar?
- Verificar si los certificados de code signing, firmware, o PKI de larga duración están en el path de migración.
- Seguir el radar de amenazas: el NIST mantiene actualizaciones sobre las timelines de la computación cuántica.

## Variantes y bypasses

Las 5 familias de fallos de planificación PQC.

### 1. "Las computadoras cuánticas no existen todavía, así que es un problema futuro"

El riesgo HNDL es un riesgo presente. Los adversarios sofisticados pueden estar recolectando tráfico cifrado TLS hoy. Los datos con sensibilidad de 10+ años ya deberían estar en el path de migración.

### 2. Crypto-agility ausente

Los sistemas que hardcodean algoritmos (sin campo de version en el ciphertext, sin negociación de algoritmo, claves en formatos de archivo fijos) no pueden migrar sin una reescritura de código. La crypto-agility es un requisito de diseño que no se puede retrofitear fácilmente.

### 3. Migrar a PQC sin período de transición híbrida

Apagar RSA/ECDH y encender ML-KEM directamente rompe la compatibilidad y elimina la confianza establecida en los algoritmos clásicos antes de que ML-KEM tenga tiempo de ganar confianza operacional equivalente. Los híbridos dan ambos.

### 4. Olvidar las firmas

La mayoría de las conversaciones PQC se enfocan en el cifrado (ECDH → ML-KEM). Las firmas (ECDSA, EdDSA, RSA-PSS) también son vulnerables. Los certificados de code signing, PKI, firmware signing, y document signing deben migrar también.

### 5. Sin inventario, sin propietario

La migración PQC requiere saber exactamente qué algoritmos están en uso en qué sistemas y quién es responsable de cada uno. Sin un inventario cripto, la migración es imposible de planificar.

## Impacto

El impacto es asimétrico en el tiempo:

- **Riesgo actual:** HNDL para datos de confidencialidad de largo plazo. El volumen de datos afectados crece cada día hasta la migración.
- **Riesgo futuro (cuando existan computadoras cuánticas relevantes):** compromiso de toda la criptografía de clave pública no migrada — TLS sessions, PKI, firmas de software, claves de device identity.
- **Riesgo de transición:** los híbridos mal implementados pueden crear nuevas superficies de ataque; la interoperabilidad entre implementaciones PQC es una área activa de verificación.

El impacto organizacional escala con la duración de sensibilidad de los datos y la prominencia del objetivo (gobierno, defensa, finanzas, infraestructura crítica).

## Detección y defensa

Ordenado por urgencia:

1.
**Construir un inventario cripto.**
   Para cada sistema: qué algoritmos, para qué propósito, en qué formatos, con qué tamaños de clave. Incluir TLS, SSH, code signing, firmware signing, PKI interna, tokens JWT, encryption de base de datos, y backup encryption.

2.
**Priorizar sistemas con requisitos de confidencialidad de largo plazo para migración temprana.**
   Datos de salud, secretos de diseño, comunicaciones diplomáticas, secretos de IP de larga duración. Migracion de TLS a grupos híbridos X25519+ML-KEM-768 para estos sistemas.

3.
**Actualizar a AES-256 y SHA-384/SHA-512 donde sea bajo costo.**
   El impacto de Grover en simétrica se mitiga con claves más largas. Los cambios son de bajo impacto operacional.

4.
**Habilitar grupos híbridos PQC en TLS donde las librerías lo soporten.**
   OpenSSL 3.x, BoringSSL, y librerías TLS modernas tienen soporte para grupos híbridos. Habilitarlos en infraestructura de alto riesgo hoy.

5.
**Planificar la migración de code signing y PKI de larga duración.**
   Los certificados root pueden tener vidas de 20+ años. La migración de PKI lleva tiempo y requiere períodos de validez superpuestos.

### Qué no funciona

- **"Usaremos algoritmos PQC cuando sea necesario."** El "cuando sea necesario" puede ser después de que el adversario ya haya capturado datos.
- **"Solo necesitamos proteger contra ataques actuales."** Para datos de larga duración, los ataques futuros son riesgo actual.
- **"Migraremos todo a la vez."** La migración PQC es incremental; el inventario y la priorización van primero.

## Labs prácticos

### Inventario cripto inicial

```
# Escanear uso de algoritmos en un codebase
rg -n "RSA|ECDH|ECDSA|P-256|P-384|secp256k1|curve25519" .
rg -n "sha1With|sha256With|ecdsa-with" .  # en certs o formatos de firma

# Verificar negociación de grupos TLS en un servidor
openssl s_client -connect example.com:443 -tls1_3 2>&1 | grep -i "key exchange\|group\|curve"
```

### Tabla de referencia: primitivos amenazados vs migración sugerida

```
Primitivo actual       Amenaza cuántica    Reemplazo sugerido
─────────────────────────────────────────────────────────────
RSA-2048 (cifrado)     Alto (Shor)         ML-KEM-768 (FIPS 203)
ECDH-P256              Alto (Shor)         ML-KEM-768 (FIPS 203)
ECDSA-P256             Alto (Shor)         ML-DSA-65 (FIPS 204)
EdDSA-Ed25519          Alto (Shor)         ML-DSA-65 (FIPS 204)
AES-128                Bajo (Grover)       AES-256 (preventivo)
SHA-256                Bajo (Grover)       SHA-384/SHA-512
AES-256                Mínimo (Grover)     Sin cambio necesario
SHA-3-256              Mínimo (Grover)     Sin cambio necesario
```

### Verificar soporte de grupos híbridos en TLS

```
# Con OpenSSL 3.2+ y provider oqs instalado:
openssl s_client -connect example.com:443 -groups X25519MLKEM768 2>&1 | grep -i "group\|key exchange"
```

## Ejemplos prácticos

- Un proveedor de salud cifra registros con RSA-2048. Los datos de pacientes tienen requisitos de retención de 25 años. La ventana de riesgo HNDL ya está abierta; el inventario cripto debe ser el primer paso.
- Un sistema de firmware signing de dispositivos IoT usa ECDSA-P256. Los dispositivos tienen vidas de campo de 15+ años. Migrar el sistema de signing a ML-DSA-65 y planificar la distribución de roots de confianza actualizados.
- Una empresa fintech habilita grupos híbridos X25519+ML-KEM-768 en su API TLS — costo operacional cero, protección HNDL habilitada.

## Notas relacionadas

- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[tls-handshake-and-pki]]
- [[kdf-and-key-stretching]]
- [[roll-your-own-crypto-failures]]

## Referencias

- **Estándar / RFC:** NIST FIPS 203 ML-KEM — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
- **Estándar / RFC:** NIST FIPS 204 ML-DSA — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf
- **Estándar / RFC:** NIST FIPS 205 SLH-DSA — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf
- **Fundamental:** NIST PQC Project Overview — https://csrc.nist.gov/projects/post-quantum-cryptography
- **Investigación / Deep Dive:** "Harvest Now, Decrypt Later" — https://globalriskinstitute.org/publications/quantum-threat-timeline-report-2023/
