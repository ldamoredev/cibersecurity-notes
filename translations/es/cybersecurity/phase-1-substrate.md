# Fase 1 — Sustrato (cómo funcionan realmente las cosas)

Terminaste [[index|Fase 0 — Fundamentos]] y tenés los cuatro modelos mentales: *ciberseguridad no es una lista de herramientas*, *CIA como herramienta de decisión*, *threat modeling como reflejo*, *dualidad atacante-defensor como metamarco*. Fase 1 es donde esas abstracciones aterrizan en sistemas reales.

El sustrato son **3 ramas apiladas en orden**:

> **Networking -> Web Security -> Cryptography.**

Networking va primero porque es el sustrato de todo lo demás. Web Security va segundo porque es la superficie diaria que la mayoría de gente de IT toca. Cryptography va tercera porque es la capa de correctness, y solo cobra sentido después de que TLS, sesiones y JWTs son lo suficientemente concretos para motivarla.

Esta página es el **camino curado** por las 62 notas atómicas de esas tres ramas. No necesitás leer las 62. Necesitás las 12 correctas primero, luego las 25 correctas, y después todo lo demás como profundidad.

---

## Orden de lectura de primera pasada (12 notas, ~2 semanas de lectura casual)

La secuencia mínima que te da un modelo funcional del sustrato. Leé en orden; cada nota depende de la anterior.

### Networking — 5 notas

1. **[[tcp-ip-basics|TCP/IP basics]]** — Sin esto, toda otra nota de networking es memorización. Nombra qué *son* los packets y cómo llegan de A a B.
2. **[[ports-and-services|Ports and services]]** — Qué significa realmente "open port", más allá del output de Nmap. La primera mitad de toda pregunta de reachability.
3. **[[dns-resolution|DNS resolution]]** — DNS es la mitad de cada historia de ataque y la mitad de cada fix. Name resolution es su propio sistema de confianza encima de IP.
4. **[[http-overview|HTTP overview]]** — El protocolo que vas a debuggear por el resto de tu carrera. Todo en Web Security es HTTP en el wire.
5. **[[tls-https|TLS/HTTPS]]** — Qué prueba realmente TLS (confidencialidad + integridad de canal + autenticidad del servidor), y qué *no* prueba (sin client-trust, sin end-to-end). Esta nota es el puente hacia Cryptography.

### Web Security — 4 notas

1. **[[broken-access-control|Broken access control]]** — La clase de vulnerabilidad web #1 en todos los estudios del mundo real. La mayoría de historias "nos hackearon" se reducen a esto.
2. **[[sql-injection|SQL injection]]** — La clase canónica de injection. Entenderla transfiere a command injection, LDAP injection, NoSQL injection, template injection, cualquier bug donde "input de usuario fue interpretado como código".
3. **[[xss|XSS]]** — La vulnerabilidad de confianza del navegador que todos escucharon nombrar y pocos internalizaron. Te enseña qué significa "contexto" en seguridad.
4. **[[ssrf|SSRF]]** — El bug que convierte "el servidor fetch-ea una URL por mí" en compromiso cloud. Demuestra cómo una sola falla de trusted boundary escala.

### Cryptography — 3 notas

1. **[[hashing-vs-encryption-vs-signing|Hashing vs encryption vs signing]]** — La distinción que arregla la mitad de toda confusión de crypto. Mapea directo a la tríada CIA que aprendiste en Fase 0: hashing para integridad, cifrado para confidencialidad, firma para integridad + autenticidad.
2. **[[password-hashing|Password hashing]]** — bcrypt / scrypt / argon2 y *por qué* usar `MD5` o `SHA-256` sobre contraseñas es un bug. Te enseña qué es un KDF y por qué "sigue siendo hashing" erra el punto.
3. **[[aead-and-nonce-misuse|AEAD and nonce misuse]]** — El cifrado moderno te da confidencialidad *e* integridad en una primitive. Cierra el loop sobre el malentendido "encryption != security" nombrado en [[cia-triad-and-what-it-actually-decides|CIA Triad]].

**Frená acá en primera pasada.** Con estas 12 notas tenés un modelo funcional del sustrato. Ahora podés pasar a Fase 2 (Offense + Detection en pares) y volver a Fase 1 por profundidad cuando sea relevante.

---

## Lectura extendida (después de la primera pasada, antes de trabajo profundo de Fase 2)

Las siguientes 13 notas convierten "modelo funcional" en "operador confiado". Leelas por necesidad, no linealmente.

### Profundidad de Networking — 6 notas

- **[[http-headers|HTTP headers]]** — Qué *significa cada header a nivel confianza*, no solo "qué valor setear".
- **[[http-messages|HTTP messages]]** — Estructura request/response en profundidad; necesario para entender request smuggling, ataques HTTP/2, header injection.
- **[[cookies-and-sessions|Cookies and sessions]]** — Cómo persiste realmente el estado web y dónde se gana o pierde la integridad de sesión.
- **[[reverse-proxies|Reverse proxies]]** — Las apps modernas están mediadas; acá se ubica mal la confianza. Fundamental para SSRF, header smuggling y exposición de admin panels.
- **[[client-ip-trust|Client IP trust]]** — La falla de header-trust más común. Todo bug de producción "usamos X-Forwarded-For" vive acá.
- **[[firewalls-and-network-boundaries|Firewalls and network boundaries]]** — Qué hacen los firewalls, qué no pueden hacer, y por qué "tenemos firewall" no es una defensa.

### Profundidad de Web Security — 5 notas

- **[[csrf|CSRF]]** — Suele enseñarse como "viejo", sigue vivo en todo admin panel mal diseñado. Te enseña qué significa realmente la confianza en *cross-site request*.
- **[[command-injection|Command injection]]** — La variante de SQLi donde el intérprete es el sistema operativo. Mismo modelo mental, distinto sink.
- **[[xxe|XXE]]** — XML external entity injection. A menudo olvidada, todavía común en APIs legacy y flujos SAML.
- **[[open-redirect|Open redirect]]** — Parece trivial, encadena hacia account takeover vía OAuth state y phishing.
- **[[content-security-policy|Content Security Policy]]** — La defensa del lado navegador que cierra la mayoría de variantes XSS en apps modernas.

### Profundidad de Cryptography — 2 notas

- **[[jwt-cryptographic-correctness|JWT cryptographic correctness]]** — Los JWTs están bien o son teatro. Casi nadie los valida correctamente en el primer intento. Cubre `alg:none`, algorithm confusion, falta de checks `aud`/`iss`, rotación de claves.
- **[[certificate-validation-and-pinning|Certificate validation and pinning]]** — Qué hacen realmente los clientes TLS (y qué saltean) cuando validan un cert. El puente entre "TLS funciona" y "TLS funciona contra este threat model".

---

## Cómo leer Fase 1 junto con Fase 0

Los modelos mentales de Fase 0 no son memorizar-una-vez-y-seguir. Son *lentes* que aplicás nota por nota.

Por cada nota de Fase 1 que leas, obligate a hacer los cuatro reflejos de Fase 0:

1. **Nombrá la propiedad CIA bajo amenaza.** ¿Es un problema de confidencialidad, integridad o disponibilidad? (La mayoría de notas de Web Security son C+I; la mayoría de notas TLS/crypto son C+I de canal; la mayoría de notas DNS/availability son A.)
2. **Recorré el trust boundary.** ¿Dónde sale un dato de un componente confiado y entra a otro? Ese borde es donde vive el bug.
3. **Enunciá el par amenaza -> control.** Para cada vulnerabilidad, ¿quién es el adversario y qué control prevendría la violación?
4. **Articulá ambos lados.** Si podés nombrar el ataque pero no la detección, tu modelo de esa nota está incompleto y acabás de descubrir qué leer después.

Las notas van a *sentirse* distintas que antes de Fase 0. Ese sentimiento es el punto.

---

## Qué podés saltear en primera pasada

Fase 1 tiene 62 notas; primera pasada 12 + extendidas 13 = 25. Las otras 37 son profundidad: *no* son menos importantes, son *más especializadas*. Salteá en primera pasada:

- **Workflows de Wireshark / packet-analysis** — tácticos, no fundacionales. Volvé cuando tengas un packet capture para analizar.
- **HTTP-header-trust-in-Node-Express** — específico de lenguaje. Volvé cuando escribas Node.
- **NAT and private networks** — útil, pero salvo que construyas infraestructura de red, no es primera pasada.
- **Dangling DNS records, caching and security, packet analysis** — volvé cuando hagas attack-surface mapping (Fase 3).
- **La mayoría de notas variant-XSS (DOM XSS, mutation XSS, etc.)** — profundidad encima de XSS base. Volvé cuando hagas engagements AppSec.
- **Deep dives de crypto** (`asymmetric-encryption-and-key-exchange`, `mac-and-hmac`, `digital-signatures`, `kdf-and-key-stretching`, `random-and-csprng-pitfalls`, `roll-your-own-crypto-failures`, `post-quantum-awareness`) — leelos cuando tengas un protocolo o diseño real que razonar.

Esta lista no es un juicio de valor. Es una *priorización de primera pasada* para la persona de IT entrando a cyber. Practitioners senior eventualmente necesitan la mayoría de estas; nadie necesita todas a la vez.

---

## Qué sigue

Después de las 12 de primera pasada (o las 25 extendidas), estás listo para [[index|Fase 2 — Offense / Defense en pares]]. Fase 2 es única en este vault: está pensada para leerse **en pares**, no como dos ramas separadas. Cada nota ofensiva tiene una nota correspondiente de [[index|Detection Engineering]] que enseña cómo se ve el ataque desde el otro lado. Leelas juntas.

Una futura página de entrada `cybersecurity/phase-2-offense-defense.md` va a curar el orden de lectura en pares; hasta entonces, el [[index|índice de offensive-security]] y el [[index|índice de detection-engineering]] son el par correcto para leer nota por nota.

---

## Navegación relacionada

- [[start-here|Empezá acá]] — página de triage por persona (algunas personas tienen un énfasis distinto en Fase 1).
- [[index|Fase 0 — Fundamentos]] — la orientación que esta fase asume.
- [[must-know-30|Must-Know 30]] — la lista must-know transversal que se superpone con la primera pasada de Fase 1.
- [[index|Índice de ciberseguridad]] — listado completo de ramas y roadmap.
