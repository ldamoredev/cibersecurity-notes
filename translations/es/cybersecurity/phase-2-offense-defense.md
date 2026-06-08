# Fase 2 — Offense / Defense (en pares)

Tenés un modelo funcional del sustrato desde [[phase-1-substrate|Fase 1]]. Fase 2 es donde la mayoría de learners de ciberseguridad se estanca, porque eligen un lado — offense *o* defense — y lo leen solo. Esta fase existe para prevenir eso.

**Fase 2 es la única fase de este atlas pensada para leerse en pares.** Cada nota ofensiva tiene una nota correspondiente de detection-engineering que enseña cómo se ve la misma actividad desde el otro lado. Leelas juntas. El pairing no es decoración; es todo el valor pedagógico de la fase.

Ver [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]] (Fase 0) para la filosofía. Esta página es la versión operacional.

---

## Cómo leer un par (el ritual de 4 pasos)

Para cada par de abajo:

1. **Leé primero la nota ofensiva.** Enunciá qué hace realmente el atacante a nivel wire / protocolo / código.
2. **Leé segunda la nota defensiva.** Enunciá qué telemetría deja el ataque, qué invariant viola y qué control lo habría prevenido.
3. **Nombrá el gap.** ¿Qué logra offense que defense no captura? ¿Qué captura defense que offense tal como está descrito no aborda?
4. **Ubicalo en la Pyramid of Pain.** ¿La defensa está atada a un indicador barato (hash, IP, domain, fácil de bypass-ear) o a uno caro (TTP, comportamiento, caro de bypass-ear)? Saber el nivel es el movimiento senior.

Si no podés completar pasos 3 y 4 para un par, tu modelo está incompleto y acabás de descubrir qué releer.

---

## Pares de primera pasada (6 pares / 12 notas, ~2-3 semanas)

El set mínimo que te da un modelo offense+defense funcional. Leé cada par como unidad: offense, luego defense, luego pasos 3-4.

### Par 1 — Mentalidad de reconocimiento <-> mentalidad de visibilidad

- **Offense:** [[recon|Recon]] — cómo los atacantes descubren superficie antes de tocarla.
- **Defense:** [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — qué pueden ver los defensores y dónde están los blind spots.
- **Por qué este par va primero:** Ambos lados empiezan con la misma pregunta — *qué se puede observar sobre este sistema* — desde sillas opuestas. El par enmarca todos los demás pares de Fase 2.

### Par 2 — Port scanning <-> detección de anomalías de scan

- **Offense:** [[host-and-port-discovery|Host and Port Discovery]] — el movimiento recon entry-level que corre cualquier operador.
- **Defense:** [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]] — cómo se ve un scan en NetFlow, alertas IDS y TCP fingerprints.
- **Por qué este par va segundo:** El par offense/defense más concreto del atlas. Después de leerlo, podés correr un scan contra un target autorizado *y* encontrar tus propios packets en los logs del defensor.

### Par 3 — Enumeration <-> detección behavioral vs por firmas

- **Offense:** [[enumeration|Enumeration]] — el patrón del operador de hacer muchos probes chicos para construir un modelo.
- **Defense:** [[behavioral-detection-vs-signature-detection|Behavioral Detection vs Signature Detection]] — por qué capturar el *patrón* supera capturar el *payload* en 2026.
- **Por qué este par:** Nombra la tensión central. La evasión de firmas es barata; la evasión behavioral exige cambiar lo que hacés, no solo cómo se ve.

### Par 4 — Cloaking y evasión <-> mitos de evasión de detección

- **Offense:** [[cloaking-and-security-evasion|Cloaking and Security Evasion]] — cómo se ven realmente los intentos de evasión.
- **Defense:** [[detection-evasion-myths-and-modern-limitations|Detection Evasion Myths and Modern Limitations]] — por qué la mayoría de supuestos de "stealth" fallan contra stacks modernos.
- **Por qué este par:** Cierra el loop sobre la mitad "solo voy a bypass-ear la detección" de la dualidad. Leé ambos lados juntos o vas a creerle demasiado a uno.

### Par 5 — Timing/evasión IDS <-> pipelines IDS/IPS

- **Offense:** [[nmap-timing-and-evasion|Nmap Timing and Evasion]] — las primitives de timing/rate/evasión que los operadores realmente usan.
- **Defense:** [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]] — cómo se escriben reglas IDS, qué capturan y dónde fallan.
- **Por qué este par:** El par más quirúrgico. Leerlos juntos te enseña *qué primitive de evasión derrota qué capa de inspección*, diagnóstico en ambas direcciones.

### Par 6 — Handoff de recon <-> correlación de kill-chain

- **Offense:** [[recon-to-testing-handoff|Recon to Testing Handoff]] — cómo pistas de recon se vuelven candidatos de testing validados.
- **Defense:** [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation and Kill Chain Observability]] — cómo defensores conectan señales débiles entre etapas en una cadena.
- **Por qué este par:** Ambas notas tratan seguridad como una *secuencia* más que como un momento. El par enseña la tesis "muchas señales chicas encadenan en una historia grande" que mueve la detección moderna.

**Frená acá en primera pasada.** Después de estos 6 pares tenés un modelo offense+defense funcional y podés elegir con inteligencia qué pares de profundidad importan para tu trabajo.

---

## Pares extendidos (3 pares / 6 notas, profundidad encima de primera pasada)

Leelos por necesidad, no linealmente. Cada uno desbloquea una capacidad específica de operador.

### Par 7 — Scanning a escala internet <-> NetFlow/Zeek/Suricata

- **Offense:** [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]] — scanning async stateless para trabajos de amplitud.
- **Defense:** [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]] — la capa de flow analytics que captura escala antes de que deep packet inspection la vea.
- **Por qué:** A escala internet, los patrones fan-out de flow dominan la inspección por firmas. Defenders capturan Masscan antes que IDS.

### Par 8 — Tech-stack fingerprinting <-> análisis de tráfico cifrado

- **Offense:** [[tech-stack-fingerprinting|Tech-Stack Fingerprinting]] — cómo atacantes identifican qué está corriendo, muchas veces pese a TLS.
- **Defense:** [[encrypted-traffic-analysis-and-metadata-leakage|Encrypted Traffic Analysis and Metadata Leakage]] — JA3/JA4, flow shape, timing, SNI; TLS no oculta tanto como la gente piensa.
- **Por qué:** El par que desarma "TLS vuelve invisible el tráfico". La misma metadata filtra para ambos lados.

### Par 9 — Profundidad de active recon <-> EDR + correlación de procesos

- **Offense:** [[active-recon|Active Recon]] — descubrimiento activo a nivel engagement.
- **Defense:** [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]] — el join host-side que ata comportamiento de red a procesos, users y parents concretos.
- **Por qué:** La feature killer de la detección moderna es atar *qué proceso* hizo *qué conexión*. Acá "vimos el scanner" se vuelve "identificamos la cuenta del operador".

---

## Notas de detección transversales (sin par ofensivo único)

Algunas notas de detection-engineering son sobre la disciplina en sí, no sobre un ataque específico. Leelas después de los primeros 6 pares: aplican a todos los pares.

- **[[false-positives-false-negatives-and-detection-tradeoffs|False positives, false negatives, and detection tradeoffs]]** — la economía precisión/recall que decide si una regla sobrevive en producción.
- **[[telemetry-normalization-correlation-and-enrichment|Telemetry normalization, correlation, and enrichment]]** — ECS/OpenTelemetry, resolución de entidades, por qué "tenemos los logs" no es lo mismo que "podemos correlacionarlos".

Estas dos se leen *después* de tener 6 pares de ejemplos concretos; tienen mucho más sentido cuando tenés algo sobre lo cual aplicarlas.

---

## Qué significa "primera pasada completa" en Fase 2

Completaste primera pasada de Fase 2 cuando, para cualquiera de los 6 pares, podés:

1. Explicar offense a nivel protocolo/wire.
2. Explicar la fuente de telemetría y lógica de detección de defense.
3. Nombrar al menos una clase de bypass para la defensa.
4. Nombrar al menos una detección que capture el bypass.
5. Ubicar la defensa en la Pyramid of Pain (bajo -> bypass trivial / alto -> bypass caro).

Si podés hacer esto para un par, podés hacerlo para los seis con el mismo template. Esa fluidez *es* lo que Fase 2 enseña.

---

## Qué sigue

Después de la primera pasada de Fase 2, podés pasar a:

- **[[index|Security Playbooks]]** — convertir concepto en procedimiento. Específicamente [[run-scan-pipeline|Run External Recon Scan Pipeline]] usa tres pares de Fase 2 como su sustrato operacional.
- **Fase 3 — Superficie de operador** (Attack Surface Mapping, OSINT, Linux Privilege Escalation, Security Playbooks).
- **Fase 4 — Specialty tracks** (API / Cloud / DevSecOps / Wireless) cuando tu contexto laboral los demande.

Futuras páginas de entrada `phase-3-operator.md` y `phase-4-specialty.md` van a curar esas fases igual que esta página cura Fase 2.

---

## Por qué existe esta página

La mayoría de educación en seguridad enseña offense y defense como currículas separadas, por personas separadas, en salas separadas. El costo es el arquetipo de half-practitioner: hábil en un lado, peligroso cuando tiene que razonar sobre el otro. Este atlas está estructurado para que el pairing sea barato, y esta página es el artefacto operacional que convierte el pairing en modo de lectura por defecto, no en aspiración.

Si leés solo una mitad de estos pares, aprendiste la mitad de Fase 2.

---

## Navegación relacionada

- [[start-here|Empezá acá]] — página de triage por persona.
- [[phase-1-substrate|Fase 1 — Sustrato]] — el camino curado de la fase anterior.
- [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]] — la nota de Fase 0 que esta fase operacionaliza.
- [[index|Índice de Offensive Security / Recon]] — listado completo de la rama ofensiva.
- [[index|Índice de Detection Engineering]] — listado completo de la rama defensiva.
- [[must-know-30|Must-Know 30]] — lista must-know transversal (el Par 2 de esta página está ahí).
- [[index|Índice de ciberseguridad]] — roadmap completo del atlas.
