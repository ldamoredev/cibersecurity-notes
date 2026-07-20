# Fase 3 — Superficie de operador (concepto -> capacidad)

Tenés un modelo de sustrato desde [[phase-1-substrate|Fase 1]] y podés leer offense y defense como pares desde [[phase-2-offense-defense|Fase 2]]. Fase 3 es donde ese conocimiento se vuelve **capacidad de operador**: workflows que podés ejecutar de verdad contra targets autorizados, no solo razonar.

Fase 3 es la única fase organizada alrededor de un **workflow**, no de un cuerpo de teoría. Las 4 ramas forman un loop end-to-end:

> **Mapear la superficie -> recolectar evidencia pública -> recorrer un foothold -> ejecutar procedimientos repetibles.**

Las 41 notas atómicas de esas ramas colapsan en ~12 notas de primera pasada que te dan el loop funcional de operador, y luego ~12 más que convierten el loop en un workflow de engagement pulido.

---

## El loop de Fase 3

```
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  ▼                                                         │
ATTACK SURFACE MAPPING  →  OSINT  →  LINUX PRIVESC  →  PLAYBOOKS  →
  (qué está expuesto)     (evidencia   (falla de límite    (procedimientos
                          pública)      post-foothold)      repetibles)
```

Podés entrar al loop por cualquier nodo según el contexto del engagement. El orden de lectura de primera pasada recorre el loop en su secuencia natural.

---

## Orden de lectura de primera pasada (12 notas, ~2 semanas)

### Attack Surface Mapping — 3 notas

1. **[[attack-surface-mapping|Attack Surface Mapping]]** — el modelo mental central: superficie como intersección de reachability, discoverability y drift.
2. **[[external-attack-surface|External Attack Surface]]** — qué está expuesto a internet público, con una disciplina para separar lo previsto de lo real.
3. **[[exposed-service-triage|Exposed Service Triage]]** — cómo rankear cien servicios descubiertos en orden de prioridad para dedicar tiempo a los correctos.

### OSINT — 3 notas

1. **[[osint|OSINT]]** — recolección de evidencia de fuentes públicas, con una disciplina para convertir pistas en hechos validados y no guesses.
2. **[[osint-triage|OSINT Triage]]** — qué hallazgos merecen investigación ahora, cuáles son ruido y cómo registrar la decisión.
3. **[[google-dorking|Google Dorking]]** — la técnica OSINT más concreta; enseña qué hacen realmente los search operators y dónde filtran datos indexados.

### Linux Privilege Escalation — 3 notas

1. **[[linux-privilege-escalation|Linux Privilege Escalation]]** — el modelo mental central: límites locales de privilegio, qué falla después de un foothold, cómo la enumeración se vuelve hipótesis rankeadas.
2. **[[linux-enumeration|Linux Enumeration]]** — el inventario breadth-first que convierte "tengo una shell" en "tengo una lista rankeada de caminos hacia arriba".
3. **[[sudo-misconfigurations|Sudo Misconfigurations]]** — por frecuencia, el camino #1 de Linux privesc real. Enseña el patrón de "delegación de confianza" que reaparece en todo lo demás.

### Security Playbooks — 3 notas

1. **[[index|Índice de Security Playbooks]]** — leelo primero para ver el template de playbook y el catálogo.
2. **[[exploit-idor|Exploit IDOR]]** — leé un playbook ofensivo de punta a punta para ver cómo un concepto se vuelve procedimiento. IDOR es el correcto porque es el hallazgo web real más común.
3. **[[run-scan-pipeline|Run External Recon Scan Pipeline]]** — el playbook recon a nivel engagement que une Fases 1-3. Leelo último porque depende de todo lo demás.

**Frená acá en primera pasada.** Con estas 12 notas tenés un loop funcional de operador y podés ejecutar un engagement básico de external recon sobre un target autorizado end-to-end.

---

## Lectura extendida (12 notas más, profundidad encima de primera pasada)

Leé por necesidad, por rama, cuando tu engagement lo requiera.

### Profundidad de Attack Surface Mapping — 4 notas

- **[[endpoint-discovery|Endpoint Discovery]]** — cuando la superficie web/API domina el engagement.
- **[[admin-interface-discovery|Admin Interface Discovery]]** — el subconjunto de alto impacto de endpoint discovery.
- **[[subdomain-takeover|Subdomain Takeover]]** — la clase canónica de bug por dangling DNS; alto impacto y encontrable.
- **[[third-party-exposure|Third-Party Exposure]]** — superficie de ataque supply-chain; muchas veces el componente no gestionado más grande de la postura de una organización.

### Profundidad de OSINT — 3 notas

- **[[company-osint|Company OSINT]]** — mapeo a nivel organización cuando el engagement tiene alcance corporativo.
- **[[breach-and-leak-intelligence|Breach and Leak Intelligence]]** — exposición de credenciales como fuente primaria de recon.
- **[[osint-reporting|OSINT Reporting]]** — convertir evidencia en hallazgos estructurados que sobreviven revisión.

### Profundidad de Linux Privesc — 3 notas

- **[[suid-sgid-misconfigurations|SUID/SGID Misconfigurations]]** — la segunda clase de privesc más común en hallazgos reales.
- **[[linux-capabilities|Linux Capabilities]]** — el reemplazo moderno de SUID y una fuente común de privesc sutil.
- **[[linpeas-workflow|LinPEAS Workflow]]** — la capa práctica de tooling que convierte teoría en una pasada de enumeración de 60 segundos.

### Profundidad de Playbooks — 2 notas

- **[[exploit-sqli|Exploit SQL Injection]]** — el playbook canónico de injection; transfiere a command injection, NoSQL injection, etc.
- **[[investigate-ssrf|Investigate SSRF]]** — el hallazgo web cloud-era de mayor impacto; el playbook enseña la cadena metadata-endpoint que convierte SSRF en compromiso.

---

## Cómo Fase 3 conecta con Fase 0 / 1 / 2

Fase 3 es donde pagan las fases anteriores. Usalas como lentes:

- **Desde Fase 0:** Cada hallazgo de operador se nombra con su [[cia-triad-and-what-it-actually-decides|propiedad CIA]] antes de reportar. Cada workflow recibe una pasada de [[threat-modeling-quickstart|threat model]] antes de ejecutarse. Cada movimiento ofensivo se empareja con su [[attacker-defender-duality-as-a-learning-tool|contraparte defensiva]] antes de afirmar que tuvo éxito.
- **Desde Fase 1:** El sustrato de Networking y Web Security vuelve inteligible el attack-surface mapping; la correctness de Cryptography vuelve creíbles los claims "el JWT valida".
- **Desde Fase 2:** Cada playbook de Fase 3 tiene una contraparte de detección de Fase 2. El operador senior corre el playbook ofensivo *y* sabe qué vio el SOC.

---

## Qué saltear en primera pasada

Fase 3 tiene 41 notas; primera pasada 12 + extendida 12 = 24. Las otras 17 son profundidad:

- **Notas specialty de OSINT** (email-and-phone-osint, image-and-location-osint, social-media-osint, historical-internet-artifacts) — específicas de workflow; volvé cuando el tipo de engagement lo demande.
- **Specialty de Attack Surface Mapping** (deprecated-api-versions, exposed-storage, internal-attack-surface) — volvé cuando el engagement tenga esos tipos de superficie.
- **Specialty de Linux Privesc** (path-hijacking, kernel-exploit-triage, cron-and-timer-abuse) — volvé después de que sudo y SUID sean reflejo.
- **Playbooks de nicho** (test-client-ip-spoofing, test-cors-behavior, test-path-traversal, inspect-session-handling, etc.) — volvé cuando el scope del engagement los incluya.

Esta lista no es un juicio de valor. Es priorización de operador para alguien que quiere ejecutar un engagement autorizado end-to-end antes de especializarse.

---

## Qué significa "primera pasada completa" en Fase 3

Completaste primera pasada de Fase 3 cuando podés:

1. **Recorrer el loop** desde attack surface mapping -> OSINT -> privesc-after-foothold -> ejecución de playbook contra un target autorizado sin receta externa.
2. **Triage de hallazgos** — dados 100 servicios, nombrar cuáles 10 merecen atención inmediata y por qué.
3. **Ejecutar un playbook de memoria** — elegir uno de [[exploit-idor]], [[run-scan-pipeline]] o [[exploit-sqli]] y correrlo desde inicio hasta "hallazgo validado o resultado negativo" sin leer la página.
4. **Escribir el reporte** — convertir la corrida en un hallazgo con pasos de reproducción, propiedad CIA, blast radius y remediación, en menos de una página.

Estos cuatro pasos son la unidad de capacidad de operador. La especialización de Fase 4 se construye encima de esta unidad.

---

## Qué sigue

Después de la primera pasada de Fase 3, elegís specialty tracks de Fase 4 según tu trabajo:

- **API Security** si construís o testeás APIs.
- **Cloud Security** si tus sistemas corren en cloud.
- **DevSecOps** si sos dueño de un build/release pipeline.
- **Wireless Security** si trabajás con redes Wi-Fi.

Un futuro `phase-4-specialty.md` va a mostrar las notas de arranque correctas para cada una. Hasta entonces, los índices de [[index|API Security]], [[index|Cloud Security]], [[index|DevSecOps]] y [[index|Wireless Security]] llevan sus propias listas de lectura ordenadas.

La disciplina paralela always-on de [[index|Privacy, Anonymity & OPSEC]] se vuelve profesionalmente relevante en Fase 3: cada engagement deja artifacts del lado operador que necesitan disciplina de OPSEC.

---

## Navegación relacionada

- [[start-here|Empezá acá]] — página de triage por persona.
- [[phase-1-substrate|Fase 1 — Sustrato]] — entrada de fase anterior.
- [[phase-2-offense-defense|Fase 2 — Offense / Defense]] — entrada de fase anterior.
- [[index|Fase 0 — Fundamentos]] — los modelos mentales que Fase 3 operacionaliza.
- [[index|Índice de Attack Surface Mapping]] — rama completa.
- [[index|Índice de OSINT]] — rama completa.
- [[index|Índice de Linux Privilege Escalation]] — rama completa.
- [[index|Índice de Security Playbooks]] — rama completa.
- [[must-know-30|Must-Know 30]] — lista must-know transversal.
- [[index|Índice de ciberseguridad]] — roadmap completo del atlas.
