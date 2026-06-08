# Must-Know 30 — La alfabetización mínima viable en seguridad

Las más de 200 notas de este atlas son la forma larga. Esta es la **forma corta**: 30 notas que cualquier persona de IT, developer o practitioner junior de seguridad debería poder explicar en 90 segundos cada una.

Si podés hacer eso con las 30, tenés un modelo de seguridad funcional; no completo, pero funcional. Todo lo demás en el atlas es *profundidad* encima de esta *amplitud*.

**Cómo leer esta lista:**
- La agrupación espeja el orden Fase 0 -> Fase 1 -> Fase 2, pero cada entrada se puede leer sola.
- Cada entrada tiene una línea de *por qué esto importa para todos*; esa línea es el punto, no el título.
- Las notas marcadas *(futuro)* están sembradas pero todavía no escritas; podés saltearlas en la primera vuelta.

---

## Mindset (4)

1. [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|Qué es ciberseguridad (y por qué no es una lista de herramientas)]] — corrige el error más común de principiante antes de que aterrice el resto de la lista.
2. [[cia-triad-and-what-it-actually-decides|Tríada CIA como herramienta de decisión]] — nombrá primero la propiedad bajo amenaza, antes de razonar sobre controles.
3. [[threat-modeling-quickstart|Threat modeling quickstart]] — las 4 preguntas + pasada STRIDE que toma una hora y cambia cómo leés tickets.
4. [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]] — cada tema en seguridad es un par; estudiar una sola mitad te estanca.

## Sustrato de networking (6)

1. [[tcp-ip-basics|TCP/IP basics]] — sin esto, toda otra nota de networking es memorización.
2. [[ports-and-services|Ports and services]] — qué significa realmente "open port", más allá del output de Nmap.
3. [[dns-resolution|DNS resolution]] — DNS es la mitad de cada historia de ataque y la mitad de cada fix.
4. [[http-overview|HTTP overview]] — el protocolo que vas a debuggear por el resto de tu carrera.
5. [[tls-https|TLS/HTTPS]] — qué prueba realmente TLS (y qué no).
6. [[reverse-proxies|Reverse proxies]] — las apps modernas están mediadas; acá es donde se ubica mal la confianza.

## Superficie web (5)

1. [[broken-access-control|Broken access control]] — la clase de vulnerabilidad web #1 en todos los estudios del mundo real.
2. [[sql-injection|SQL injection]] — la clase canónica de injection; entenderla transfiere a todas las demás injections.
3. [[ssrf|SSRF]] — el bug que convierte "el servidor fetch-ea una URL por mí" en compromiso cloud.
4. [[xss|XSS]] — la vulnerabilidad de confianza del navegador que todos escucharon nombrar y pocos internalizaron.
5. [[csrf|CSRF]] — enseñada como "vieja", sigue viva en todo admin panel mal diseñado.

## Correctness criptográfica (4)

1. [[hashing-vs-encryption-vs-signing|Hashing vs encryption vs signing]] — la distinción que arregla la mitad de todas las preguntas de crypto.
2. [[password-hashing|Password hashing]] — bcrypt/scrypt/argon2 y por qué MD5/SHA-256 sobre contraseñas es un bug.
3. [[aead-and-nonce-misuse|AEAD and nonce misuse]] — el cifrado moderno te da confidencialidad *e* integridad; entender por qué importa.
4. [[jwt-cryptographic-correctness|JWT cryptographic correctness]] — los JWTs están bien o son teatro; casi nadie los valida correctamente en el primer intento.

## Par offense / defense (5 — leer cada fila junta)

1. [[host-and-port-discovery|Host and port discovery]] <-> [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan]] — el movimiento recon más básico y cómo se ve para defensores.
2. [[nmap-scanning|Nmap scanning]] <-> [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]] — qué es un scan Nmap y dónde aparece en tus logs.
3. [[active-recon|Active recon]] <-> [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS y pipelines de detección behavioral]] — cómo enumeran los atacantes y cómo los defensores capturan el patrón, no el payload.
4. [[enumeration|Enumeration]] <-> [[behavioral-detection-vs-signature-detection|Detección behavioral vs por firmas]] — las dos formas de capturar la misma actividad y por qué behavioral gana en 2026.
5. [[cloaking-and-security-evasion|Cloaking y evasión de seguridad]] <-> [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección]] — qué compra realmente la evasión para un atacante y qué no.

## Capacidad práctica (3)

1. [[threat-modeling-quickstart|Threat modeling quickstart]] *(releer)* — la única entrada que aparece dos veces. Es el hábito de mayor leverage de esta lista.
2. [[exploit-sqli|Playbook: explotar SQLi]] — leé un playbook ofensivo de punta a punta para ver cómo un concepto se vuelve procedimiento.
3. [[run-scan-pipeline|Playbook: correr scan pipeline]] — el workflow recon a nivel engagement que une Fases 1-3.

## Always-on (3)

1. [[index|Privacy, Anonymity & OPSEC]] *(índice de rama)* — como mínimo las notas de threat model y correlación de cuentas; el resto es profundidad.
2. [[index|DevSecOps]] *(índice de rama)* — como mínimo las notas de secrets-management y supply-chain si tocás CI/CD.
3. [[index|Cloud Security]] *(índice de rama)* — como mínimo las notas de IAM-boundaries y metadata-endpoints si tus sistemas corren en cloud.

---

## Cómo usar esta lista

- **Como pre-test.** Antes de leer algo nuevo, escaneá las 30 entradas y calificate "podría explicarlo en 90 segundos" / "no podría". Tus gaps *son* tu lista de lectura.
- **Como refresh trimestral.** Los practitioners senior drift-ean. Recalificate cada trimestre; las direcciones del drift son diagnósticas.
- **Como preparación de entrevistas.** La mayoría de entrevistas "junior security engineer" / "AppSec engineer" / "detection engineer" tantean directamente un subconjunto de estas 30.
- **Como índice de enseñanza.** ¿Onboarding de un teammate junior? Este es el curriculum. Trackeá cuáles de las 30 internalizó.

Esta lista es **deliberadamente corta**. Lo difícil de curarla no fue elegir 30; fue dejar afuera las próximas 30. El atlas es profundidad encima de estas; las próximas 30 (database security, Kubernetes hardening, básicos de AD/Kerberos, internals de EDR, IR/forensics, básicos de malware analysis, governance de secure SDLC) viven en las ramas, alcanzables desde acá.

---

## Navegación relacionada

- [[start-here|Empezá acá]] — página de triage por persona.
- [[index|Índice de ciberseguridad]] — listado completo de ramas.
- [[index|Fundamentos]] — entrada de Fase 0.
