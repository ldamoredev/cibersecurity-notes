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
  - threat-modeling
  - stride
sources: []
---

# Arranque rápido de modelado de amenazas

## Definición
El modelado de amenazas es la práctica de mirar un sistema, recorrer sus componentes y fronteras de confianza, y responder cuatro preguntas: **qué estamos construyendo, qué puede salir mal, qué vamos a hacer al respecto, e hicimos un buen trabajo?** Bien hecho lleva una hora para una feature y un día para un servicio. Mal hecho — o salteado — produce controles apuntados a amenazas que nadie enfrenta realmente mientras los riesgos reales quedan sin analizar.

## Por qué importa
El trabajo de seguridad sin modelado de amenazas se reduce a correr checklists. Los checklists son útiles pero no pueden decirte *cuáles* de sus ítems importan para *tu* sistema, ni dónde dejan huecos. El modelado de amenazas es la disciplina que produce el checklist *correcto* para un activo particular, en lugar de tratar cada sistema como si tuviera las mismas amenazas.

El encuadre también corrige la confusión más común del principiante: "la seguridad es trabajo del equipo de seguridad". Un modelo de amenazas lo construye mejor *la gente que construyó el sistema* — conocen los componentes, los supuestos y las fronteras de confianza mucho mejor que cualquier revisor externo. El rol del equipo de seguridad es enseñar la metodología, revisar el output e identificar amenazas transversales. El equipo que escribió el código es dueño del modelo de amenazas igual que es dueño del diseño.

El encuadre senior es que el modelado de amenazas es **paranoia estructurada**: reemplazás "tengo un mal presentimiento con esto" por un artefacto repetible que nombra las amenazas, las ata a elementos del sistema y registra las decisiones que tomaste sobre cada una.

## Cómo funciona

El modelado de amenazas se reduce a **4 preguntas** (el marco de Adam Shostack) y **1 categorización** (STRIDE).

### Las 4 preguntas
1. **¿Qué estamos construyendo?** Dibujá el sistema como un diagrama de flujo de datos (DFD): cajas para procesos y almacenes de datos, flechas para flujos de datos, líneas punteadas para fronteras de confianza. El dibujo es el artefacto; los bullets no alcanzan.
2. **¿Qué puede salir mal?** Recorré cada elemento del DFD y aplicale STRIDE (abajo). Por cada par elemento-amenaza, preguntá "¿es creíble en nuestro modelo de amenaza?".
3. **¿Qué vamos a hacer al respecto?** Por cada amenaza creíble, elegí una de cuatro respuestas: *mitigar* (agregar un control), *aceptar* (convivir con ella, registrar por qué), *transferir* (seguro, contrato, dependencia de un tercero más capaz), *eliminar* (sacar la feature).
4. **¿Hicimos un buen trabajo?** Revisá el modelo después de que el sistema sale a producción, y en cada cambio significativo. Actualizá o invalidá.

### STRIDE — la categorización
Seis categorías de amenaza, cada una mapeada a una propiedad de la [[cia-triad-and-what-it-actually-decides|tríada CIA]]:

| Letra | Amenaza | Propiedad CIA | Familia de mitigación de ejemplo |
|---|---|---|---|
| **S** | Spoofing (suplantación) | Autenticidad (un sabor de integridad) | Autenticación, tokens firmados, mTLS |
| **T** | Tampering (manipulación) | Integridad | MACs, firmas, almacenamiento inmutable, AEAD |
| **R** | Repudiation (repudio) | Integridad + auditabilidad | Logs de auditoría firmados/inmutables |
| **I** | Information disclosure (fuga de info) | Confidencialidad | Control de acceso, cifrado, aislamiento de canal |
| **D** | Denial of service (denegación de servicio) | Disponibilidad | Rate limiting, capacidad, redundancia, degradación elegante |
| **E** | Elevation of privilege (elevación de privilegios) | Integridad + autorización | Mínimo privilegio, chequeos de autorización, sandboxing |

El bug no es "no modelamos amenazas"; el bug es *no recorrimos nuestras fronteras de confianza preguntando STRIDE en cada una, así que nuestros controles protegen los elementos equivocados*.

## Errores comunes

### "El modelado de amenazas es un proyecto de 6 meses que necesita un consultor."
Esa es la versión académica, útil para sistemas críticos de seguridad. La versión de trabajo que un desarrollador o persona de IT debería dominar es la pasada de 4-preguntas / STRIDE sobre una feature, que lleva una hora. La curva inversión-a-retorno es empinada al principio y se aplana rápido — la primera hora produce el 80% del valor. Saltearse esa hora porque "necesitamos un programa de threat-modeling de verdad" es una excusa común para nunca hacerlo.

### "Solo el equipo de seguridad puede hacerlo."
Lo opuesto es cierto. El equipo que construyó el sistema tiene el modelo más profundo de cómo funciona, dónde viven sus supuestos y qué fronteras de confianza son reales vs aspiracionales. La palanca del equipo de seguridad es *enseñar* la metodología y revisar el output buscando amenazas transversales, no modelar amenazas en nombre de cada equipo de producto.

### "STRIDE atrapa todo."
STRIDE es una ayuda de categorización, no una garantía de cobertura. Se pierde:
- **Fallas de lógica de negocio** (race conditions en el checkout, abusar de códigos de referido para crédito gratis) — encajan incómodamente en "tampering" pero suelen pasarse por alto.
- **Amenazas de privacidad / sensibilidad de datos** más allá de la fuga de información (p. ej., ataques de correlación, re-identificación de datos anonimizados).
- **Amenazas de cadena de suministro** que abarcan sistemas para los que STRIDE no fue originalmente pensado.
Tratá a STRIDE como andamiaje, no como la respuesta. Las 4 preguntas son el marco real; STRIDE es uno de varios prompts útiles.

### "Modelamos amenazas en el diseño, ya está."
Los modelos de amenaza son artefactos vivos. Cada feature nueva, cada dependencia nueva, cada integración nueva cambia las fronteras de confianza. Un modelo de amenazas que no se actualiza está equivocado en cuestión de meses. Tratalo como tratás los diagramas de arquitectura o los ADRs — versionalo, enlazalo desde el código y actualizalo cuando la realidad cambia.

### "Las herramientas (Microsoft TMT, OWASP Threat Dragon, IriusRisk) piensan por vos."
Las herramientas capturan y presentan bien los modelos de amenaza; no los *generan*. El razonamiento es humano. La lista de amenazas auto-generada por una herramienta es un punto de partida, no un entregable. El uso senior es "usá la herramienta para dibujar y guardar el DFD; usá tu cabeza (y los prompts de STRIDE) para poblar las amenazas".

### "El modelado de amenazas es solo para sistemas nuevos."
Los sistemas existentes se benefician *más* del modelado de amenazas que los nuevos, porque sus supuestos se desviaron del diseño original. Un ejercicio de "modelá las amenazas de un servicio existente" descubre rutinariamente controles que ya no coinciden con las amenazas que el servicio realmente enfrenta.

## Cómo aplicar esto

Las 4 preguntas + STRIDE se convierten en **un ritual repetible de una hora** para cualquier feature:

1. **Dibujá el DFD en un pizarrón o en Excalidraw.** Cajas (procesos), cilindros (almacenes de datos), flechas (flujos), líneas punteadas (fronteras de confianza). Pasá 10–20 minutos acá. Si no podés dibujarlo, no entendés el sistema lo suficiente como para modelarle las amenazas.
2. **Recorré cada elemento por STRIDE.** Por cada caja, flecha y almacén de datos, hacé las seis preguntas de STRIDE en voz alta. Algunas obviamente no aplican; muchas van a hacer aflorar amenazas que nadie había nombrado. Registrá las creíbles.
3. **Decidí sobre cada amenaza creíble.** Mitigar / aceptar / transferir / eliminar. Escribí la decisión y la justificación al lado de la amenaza.
4. **Cruzá contra la prioridad CIA.** Para tu activo dominante, ¿la C/I/A que rankeaste más alta está cubierta por tus mitigaciones? Si no, tenés un hueco de cobertura.
5. **Guardá el artefacto al lado del código.** Un archivo markdown de modelo de amenazas en el repo, versionado, enlazado desde el README. Los modelos de amenaza que viven en drives compartidos mueren.
6. **Reabrí ante cambios.** Cuando el diseño cambia de forma significativa, volvé a recorrer la parte afectada del DFD.

## Ejemplos prácticos

- **Formulario de login.** DFD: navegador → reverse proxy → app → DB de usuarios + store de sesión. La pasada STRIDE hace aflorar: spoofing (credential stuffing → MFA), tampering (forja de cookie de sesión → cookies firmadas/cifradas), repudio ("yo no inicié sesión" → log de auditoría), fuga de información (enumeración de usuarios vía diferencia de tiempo de respuesta / mensaje de error → respuestas uniformes), DoS (fuerza bruta de contraseñas → rate limit + estrategia de bloqueo de cuenta), elevación (bypass de auth vía manipulación de parámetros → autorización del lado del servidor en cada acción).
- **Subida de archivos.** DFD: cliente → app → object storage → consumidor aguas abajo. STRIDE: tampering (archivo subido modificado después del escaneo → hash de integridad + almacenamiento write-once), fuga de info (path-traversal exponiendo archivos de otros tenants → paths generados por el servidor), DoS (archivos enormes o zip-bombs → límites de tamaño y de descompresión), elevación (ejecutable subido corrido por el servidor → guardar fuera del path ejecutable de la app, escanear en sandbox).
- **Endpoint de API que hace de proxy a servicios internos.** El DFD muestra una frontera de confianza que los desarrolladores olvidaron que existía. STRIDE sobre el proxy: spoofing (identidad del cliente reproducida aguas abajo → propagar identidad firmada, no el token crudo), tampering (request reescrita → validación de entrada), fuga de info (topología interna filtrada por mensajes de error → mapeo opaco de errores), elevación (SSRF llegando al servicio de metadata → allowlist de destinos salientes).
- **Pipeline de CI/CD.** DFD: desarrollador → git → runner de CI → registry → producción. STRIDE: tampering (pasos de build modificados → builds reproducibles, artefactos firmados), fuga de info (secretos en logs de build → escaneo de secretos, logs enmascarados), DoS (agotamiento del runner vía PR abusiva → cuotas de recursos), elevación (privilegios del runner abusados → tokens OIDC de mínimo privilegio, runners efímeros). Esta única pasada es cómo se motivan la mayoría de los controles modernos de cadena de suministro (SLSA, Sigstore).
- **Rebuild de un servicio legacy existente.** Dibujá el DFD como está *hoy*, no como afirma el documento de arquitectura original. La brecha entre el "DFD de diseño" y el "DFD de la realidad" es en sí misma un hallazgo.

## Notas relacionadas

- [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|Qué es la ciberseguridad y por qué no es una lista de herramientas]] — el marco dentro del cual vive esto.
- [[cia-triad-and-what-it-actually-decides|Tríada CIA — Qué decide en realidad]] — las categorías STRIDE mapean de vuelta a las propiedades CIA.
- [[attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor como herramienta de aprendizaje]] *(futuro)* — el modelado de amenazas es una de las disciplinas que vuelve concreta la dualidad.
- [[cybersecurity/web-security/index|Seguridad Web]] — STRIDE aplicado a la clase de sistema de la superficie diaria.
- [[cybersecurity/api-security/index|Seguridad de APIs]] — STRIDE aplicado a superficies legibles por máquina.
- [[cybersecurity/devsecops/index|DevSecOps]] — modelar las amenazas del propio pipeline de build/release.
- [[cybersecurity/detection-engineering/index|Ingeniería de Detección]] — cada amenaza que tu modelo acepta necesita una historia de detección correspondiente.

### Notas atómicas futuras sugeridas
- [[stride-vs-pasta-vs-octave|STRIDE vs PASTA vs OCTAVE]]
- [[dfd-conventions-and-trust-boundaries|Convenciones de DFD y fronteras de confianza]]
- [[threat-modeling-as-code|Modelado de amenazas como código]]
- [[business-logic-threat-modeling|Modelado de amenazas de lógica de negocio]]

## Referencias

- **Foundational:** Adam Shostack — Threat Modeling: Designing for Security (el texto canónico) — https://shostack.org/books/threat-modeling-book
- **Foundational:** Microsoft — STRIDE Threat Model — https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **Testing / Lab:** OWASP Threat Modeling Process — https://owasp.org/www-community/Threat_Modeling_Process
