---
type: concept
status: active
created: 2026-05-10
updated: 2026-05-10
tags:
  - cybersecurity
  - foundations
  - phase-0
  - mindset
  - cia-triad
sources: []
---

# Tríada CIA — Qué decide en realidad

## Definición
La tríada CIA — **Confidencialidad, Integridad, Disponibilidad** — es el modelo de tres propiedades de lo que la seguridad de la información intenta preservar. La confidencialidad es "quién puede leer". La integridad es "quién puede modificar sin autorización, y lo detectaríamos". La disponibilidad es "¿el sistema funciona cuando se lo necesita?". El valor de la tríada no está en ser una definición para memorizar, sino en ser una **herramienta de decisión**: nombrar la propiedad bajo amenaza es el primer movimiento en cualquier incidente, revisión de diseño, elección de control o análisis de vulnerabilidad.

## Por qué importa
A cada estudiante le dicen qué es la tríada CIA. Casi a nadie le enseñan a usarla como reflejo. El resultado es una generación de profesionales que responden "ciframelo" a preguntas que no tienen nada que ver con la confidencialidad, o que tratan todos los incidentes como el mismo "problema de seguridad" en lugar de derivar cada uno a los controles que realmente aplican.

La tríada importa porque **la mayoría de los controles apuntan a una propiedad, a veces dos, rara vez las tres**. El cifrado es un control de confidencialidad — por sí solo no impide la manipulación. Las firmas digitales son un control de integridad — no ocultan nada. El rate limiting es principalmente un control de disponibilidad, a veces de confidencialidad (evita la enumeración), y casi nunca de integridad. Si no podés nombrar qué propiedad sirve un control, no podés razonar si tenés los controles correctos para tus amenazas.

El encuadre senior es que *el modelado de amenazas es fundamentalmente un triaje CIA*: recorré el sistema, nombrá los activos y, para cada activo, preguntá cuál de las tres propiedades importa más. La respuesta guía el resto de la ingeniería.

## Cómo funciona
La tríada son **3 propiedades, cada una con su propia familia de controles y su propio modelo de adversario dominante**:

1. **Confidencialidad — quién puede leer.**
   - Objetivo del adversario: ver información que no está autorizado a ver.
   - Familia de controles: control de acceso (authn + authz), cifrado en reposo, cifrado en tránsito, gestión de claves, aislamiento de canal, hardening contra side-channels, minimización de datos.
   - Modo de falla: una fuga — los datos son observados por alguien que no debería haberlos observado.
   - Señal de detección: patrones de lectura anómalos, egress inesperado, credenciales filtradas en escaneos.

2. **Integridad — quién puede modificar sin autorización, y lo detectaríamos.**
   - Objetivo del adversario: modificar datos o comportamiento de una forma no autorizada y que pase inadvertida.
   - Familia de controles: firmas digitales, MACs, AEAD (cifrado autenticado), control de versiones, almacenamiento inmutable, registros de auditoría, firma de código, controles de cadena de suministro de software.
   - Modo de falla: una *manipulación* — datos o comportamiento se cambian y el cambio pasa inadvertido o se atribuye al actor equivocado.
   - Señal de detección: discrepancia de firma/hash, cambio no autorizado en registros, alertas de monitoreo de integridad.

3. **Disponibilidad — ¿el sistema funciona cuando se lo necesita?**
   - Objetivo del adversario: negar a los usuarios legítimos el acceso al sistema o a sus datos.
   - Familia de controles: redundancia, planificación de capacidad, rate limiting, protección DDoS, circuit breakers, degradación elegante, backup y recuperación ante desastres, planificación de continuidad del negocio.
   - Modo de falla: una *caída* — el sistema es inalcanzable, lento, o perdió datos sin copia recuperable.
   - Señal de detección: picos de latencia, picos de tasa de error, anomalías de tráfico, alertas de fallo de backup.

El bug no es "nos hackearon"; el bug es *no nombramos qué propiedad le importaba a cada activo, así que nuestros controles protegieron lo equivocado*.

## Errores comunes

### "La confidencialidad es la más importante de las tres."
Este es el instinto más común del principiante y es incorrecto en muchos contextos reales. La respuesta correcta depende del activo:
- **Historias clínicas de pacientes** → domina C (modelo de amenaza estilo HIPAA).
- **Firmware de control industrial / firmware de marcapasos** → domina I. Una copia filtrada es recuperable; una copia manipulada puede matar gente.
- **Plataforma de trading de una bolsa de valores** → domina A. Cada minuto de caída cuesta millones; la filtración de una sola transacción es menor en comparación.
- **Integridad electoral** → domina I. Manipular los totales de votos es el daño irrecuperable.
El trabajo de seguridad maduro *rankea las tres por clase de activo* y luego diseña los controles en consecuencia.

### "Cifrado = seguridad."
El cifrado es un control de *confidencialidad*. El cifrado simétrico plano (p. ej., AES-CBC sin un MAC) no te da integridad alguna — un atacante puede invertir bits del texto cifrado y el resultado descifrado será texto plano modificado, sin detección. Por eso exactamente los protocolos modernos usan [[cybersecurity/cryptography/aead-and-nonce-misuse|AEAD]] (cifrado autenticado), que provee C *e* I en una sola primitiva. Decir "usamos TLS" te dice que el canal es confidencial y autenticado, no que los datos adentro estén protegidos en integridad en reposo.

### "La tríada CIA alcanza — cubre todo."
La tríada es el núcleo que sostiene la estructura, pero existen extensiones por buenas razones:
- **Autenticidad** — ¿este mensaje vino realmente del remitente que dice ser? (A veces se subsume en integridad, pero distinto en la práctica — las firmas digitales proveen ambas.)
- **No repudio** — ¿puede el remitente negar haberlo enviado? (Distinto de integridad; podés detectar manipulación sin poder probar quién envió el original.)
- **AAA** — Autenticación, Autorización, Accounting — expansión operativa de los controles de confidencialidad.
- **Hexágono de Parker** — agrega Posesión, Autenticidad, Utilidad encima de CIA.
Para la mayoría del trabajo cotidiano la tríada alcanza; para el diseño de protocolos criptográficos o sistemas con calidad forense, necesitás las extensiones. Saber que existen es el movimiento senior.

### "La disponibilidad no es realmente seguridad; es un problema de SRE / confiabilidad."
La disponibilidad se vuelve un problema de seguridad en el momento en que un adversario puede *causar* la caída. Una caída de red por un router mal configurado es confiabilidad; la misma caída causada por un DDoS o un evento de cifrado por ransomware es seguridad. La frontera es "¿hay un adversario?". Muchos ataques modernos (ransomware, malware wiper, sabotaje de cadena de suministro) son ataques puros de A disfrazados de otra cosa.

### "Confidencialidad e integridad son independientes."
No lo son. El cifrado sin integridad (los debates de "MAC-then-encrypt vs encrypt-then-MAC", los ataques de manipulación en modo ECB, los ataques de padding-oracle contra CBC) muestra que un control solo de confidencialidad sin integridad puede *filtrar datos igual* porque el atacante manipula el texto cifrado para forzar un canal lateral. Por eso existe AEAD. Ver [[cybersecurity/cryptography/aead-and-nonce-misuse|AEAD y mal uso de nonce]].

## Cómo aplicar esto

La tríada se convierte en **4 reflejos** que un estudiante debería construir:

1. **Nombrá la propiedad primero — antes de cualquier otro análisis.**
   Cuando leas sobre un incidente o vulnerabilidad, forzate a declarar explícitamente: "esto es una brecha de C" / "esto es una brecha de I" / "esto es una brecha de A" *antes* de leer los detalles técnicos. La disciplina rinde en cada rama del atlas.

2. **Etiquetá cada control con su propiedad.**
   Cuando diseñes o revises un control, escribí al lado cuál de C/I/A sirve. Si un control dice servir a las tres, sospechá — la mayoría no lo hace. El ejercicio revela controles que no están haciendo nada por la propiedad bajo amenaza.

3. **Rankeá C/I/A por clase de activo, no globalmente.**
   Para cada activo (base de datos, stream de logs, firmware, almacén de credenciales), preguntá cuál de las tres importa más. La respuesta guía el presupuesto de controles. Un plan de controles que trata cada activo como "C-dominante" es un plan que mal-asigna la atención.

4. **En incidentes, la pregunta de triaje es "¿qué propiedad está vulnerada?".**
   Esa única pregunta enruta la respuesta: una brecha de C va a rotación de credenciales, revocación de claves, contención de la fuga. Una brecha de I va a verificación de registros, rollback a un estado bueno conocido, atribución. Una brecha de A va a restauración, failover, análisis de causa raíz del mecanismo de la caída.

## Ejemplos prácticos

- **Inyección SQL que filtra filas de usuarios** → brecha de C. Respuesta: identificar qué se filtró, notificar, rotar cualquier credencial filtrada, arreglar el sink de inyección.
- **Inyección SQL que actualiza `is_admin=1` en la fila de otro usuario** → brecha de I. Respuesta: auditar cambios recientes, revertir escrituras no autorizadas, arreglar el sink, *y* verificar si la integridad de algún sistema aguas abajo quedó contaminada.
- **Inyección SQL que ejecuta `DROP TABLE users`** → brecha de A (y brecha de I para los backups). Respuesta: restaurar desde backup, arreglar el sink, auditar qué más usaba esa cuenta.
- **Token de API de larga vida robado** → brecha de C (el atacante puede leer todo lo que el token puede leer) + potencialmente I (si el token tiene scopes de escritura). La división C-vs-I decide si los logs de acceso de lectura solos cuentan toda la historia.
- **Ransomware cifrando un fileserver** → brecha de A principalmente (archivos no disponibles) + brecha de C en segundo plano (los atacantes suelen exfiltrar antes de cifrar). La respuesta está dominada por A: backups, restauración, continuidad del negocio. La respuesta de C es forense: qué se exfiltró, a quién hay que notificar.
- **Manipulación de entradas de log firmadas** → brecha de I. A menudo el *verdadero* ataque escondido detrás de otra cosa — un atacante que puede reescribir logs ya comprometió la integridad de toda investigación aguas abajo que dependa de esos logs.
- **Certificado TLS no validado por el cliente (skip-verify)** → brecha de C (escucha posible) *y* brecha de I (un MITM puede inyectar contenido). Ambas, porque la validación del certificado sostiene ambas propiedades del canal.
- **DDoS contra una pasarela de pago durante el Black Friday** → brecha pura de A. El costo se mide en ingresos, no en datos. Una defensa que se enfoca en "los datos están cifrados" se pierde toda la amenaza.

## Notas relacionadas

- [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|Qué es la ciberseguridad y por qué no es una lista de herramientas]] — el marco dentro del cual vive esta nota.
- [[threat-modeling-quickstart|Arranque rápido de modelado de amenazas]] *(futuro)* — usa la tríada como primera pregunta de triaje.
- [[attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor como herramienta de aprendizaje]] *(futuro)* — cada propiedad tiene su propio par ofensa/defensa.
- [[cybersecurity/cryptography/hashing-vs-encryption-vs-signing|Hashing vs Cifrado vs Firma]] — distinción concreta de C/I/autenticidad en las primitivas.
- [[cybersecurity/cryptography/aead-and-nonce-misuse|AEAD y mal uso de nonce]] — por qué los protocolos modernos dan C e I juntas.
- [[cybersecurity/cryptography/digital-signatures|Firmas Digitales]] — el control canónico de I + autenticidad.
- [[cybersecurity/cryptography/mac-and-hmac|MAC y HMAC]] — primitiva de integridad.
- [[cybersecurity/web-security/broken-access-control|Control de Acceso Roto]] — la mayoría de las brechas de C en apps web se reducen a esto.
- [[cybersecurity/detection-engineering/index|Ingeniería de Detección]] — cada propiedad tiene su propia telemetría de detección.

### Notas atómicas futuras sugeridas
- [[parkerian-hexad-and-when-the-triad-is-not-enough|Hexágono de Parker y cuándo la tríada no alcanza]]
- [[aaa-authentication-authorization-accounting|AAA: autenticación, autorización, accounting]]
- [[non-repudiation-and-when-it-actually-matters|No repudio y cuándo importa de verdad]]
- [[ranking-cia-per-asset-class|Rankear CIA por clase de activo]]

## Referencias

- **Foundational:** NIST SP 800-12 — An Introduction to Information Security (define CIA como el modelo organizador) — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-12r1.pdf
- **Foundational:** ISO/IEC 27000:2018 — Information security management systems overview (definición canónica de CIA en los estándares internacionales) — https://www.iso.org/standard/73906.html
- **Research / Deep Dive:** Donn B. Parker — Toward a New Framework for Information Security (Hexágono de Parker, la crítica estándar a los límites de la tríada) — https://onlinelibrary.wiley.com/doi/10.1002/9780470051986.j0027
