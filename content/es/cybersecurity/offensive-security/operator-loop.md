---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - offensive-security
  - operator-loop
  - red-team
  - methodology
  - kill-chain
sources: []
---

# El loop del operador

## Definición
El loop del operador es el ciclo de decisión repetible que un operador de red team (o un intruso real) corre desde afuera del perímetro hasta el objetivo: **recon → acceso inicial → enumerar → escalada-de-privilegios → movimiento lateral → persistencia → acciones-sobre-objetivos**, con las etapas del medio *loopeando* en cada host o identidad recién adquirido. Es la spine de metodología de la que las notas de técnicas individuales del branch (recon, enumeración, escalada de privilegios, los playbooks de detección) son *etapas*. Bajo la presión de EDR/telemetría-de-identidad de 2026 el loop se gobierna menos por "¿puedo hacer esto?" y más por **"¿qué me cuesta esto en telemetría, y puedo deshacerlo?"**.

## Por qué importa
Las técnicas individuales — Kerberoasting, abuso de SUID, un SSRF al endpoint de metadata — son *jugadas*. El loop del operador es el *juego*. Los operadores que solo coleccionan técnicas se hacen atrapar secuenciándolas mal. Tres lecciones transferibles:

- **El loop es una secuencia de apuestas con precio, no un checklist.** Cada etapa es una elección pesada en dos ejes: **reversible ↔ irreversible** (¿puedo deshacer la huella?) y **silencioso ↔ ruidoso** (¿qué telemetría emite esto?). Un password spray fallido es reversible y barato; volcar LSASS o dropear un implant es irreversible y ruidoso. El tradecraft senior front-loadea las acciones reversibles y silenciosas y difiere las irreversibles hasta que el objetivo las fuerza.
- **La telemetría colapsa el espacio de decisión.** En una empresa de 2026 bien instrumentada, el linaje de procesos del EDR, los logs de identidad (recon LDAP, auth anómala) y la metadata de red convierten "muchos caminos hacia adelante" en "unos pocos caminos silenciosos hacia adelante". La visibilidad del defensor *es* la restricción del operador — por eso esta nota se empareja apretadamente con el [[cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability|branch de detection-engineering]].
- **Transfiere entre objetivos.** El mismo loop de siete tiempos corre en Windows-AD, macOS y nube — pero la *mecánica* de cada etapa difiere por completo (Kerberos vs TCC vs IAM). Tener el loop como invariante te deja portar la habilidad en vez de re-aprenderla por plataforma.

Esta nota es la mitad ofensiva de la [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|dualidad atacante-defensor]]; el defensor la lee como la kill chain a interrumpir.

## Cómo funciona
El loop corre en **7 etapas**, donde las etapas 3–5 se repiten en cada nuevo punto de apoyo:

1. **Recon (externo).** OSINT + mapeo de superficie de ataque. Usualmente reversible y casi-invisible para el objetivo. → [[passive-recon|Recon pasivo]], [[active-recon|Recon activo]].
2. **Acceso inicial.** Phish, exploit o credenciales válidas. El primer paso significativamente *ruidoso* — produce un evento de auth o una ejecución de payload.
3. **Enumerar.** Conciencia situacional desde el punto de apoyo: privilegios locales, estructura de dominio/nube, hosts e identidades alcanzables. Alto valor, frecuentemente el paso *más ruidoso* (recon LDAP, enumeración de API de nube). → [[enumeration|Enumeración]].
4. **Escalada de privilegios.** Usuario local → admin/root/SYSTEM, o identidad de bajo-priv → rol de alto-priv. → [[cybersecurity/identity-and-active-directory/windows-privilege-escalation|Escalada de privilegios en Windows]], el branch de Linux privesc.
5. **Movimiento lateral.** Al próximo host o identidad usando credenciales, tickets o tokens cosechados.
6. **Persistencia.** Sobrevivir al reboot y a la rotación de credenciales — un artefacto deliberadamente *diferido e irreversible*, tomado solo cuando el punto de apoyo vale la pena mantener.
7. **Acciones sobre objetivos.** Recolección, exfiltración o impacto — la meta, y el punto de máximo riesgo.

**El loop, no la línea:** las etapas 3→4→5 se re-corren en cada host/identidad adquirido (enumerar el nuevo contexto, escalar dentro de él, moverse de nuevo), y el recon interno re-siembra la etapa 1 desde adentro.

Una rama-de-decisión en un punto de apoyo fresco vuelve concretos los dos ejes:

```text
Punto de apoyo: shell de usuario en una workstation Windows, EDR presente, unida al dominio AD
Necesidad: conciencia situacional del dominio antes de cualquier acción con credenciales
├─ Opción A  SharpHound, recolección completa ... RUIDOSO (alerta LDAP-recon) · reversible
├─ Opción B  LDAP dirigido, paginado + throttleado quieto · más lento · reversible
├─ Opción C  volcar LSASS para credenciales ...... RUIDOSO + IRREVERSIBLE (telemetría de
│                                                   acceso a LSASS + un artefacto de credencial)
└─ Regla del operador: agotá la enumeración reversible+silenciosa (A/B) antes de cualquier
                       acción de credencial irreversible (C). Gastá la irreversibilidad tarde.
```

El loop no es un checklist; es un problema de ordenamiento. La habilidad es *secuenciar* las jugadas para llegar al objetivo gastando la menor telemetría e irreversibilidad posible.

> Adaptación de secciones: esta es una nota de metodología. *Cómo funciona* describe un ciclo de decisión en vez de un único mecanismo; *Variantes y bypasses* abajo carga la vista por-mundo-objetivo; los *Labs prácticos* son ejercicios de mapeo/razonamiento más un range ejecutable.

## Técnicas / patrones
Cómo corren el loop los operadores top:

- **Modelá la vista del defensor antes de cada acción.** Preguntá "¿cómo se ve esto en la telemetría de EDR / identidad / red?" *antes* de hacerlo. La nota de [[cybersecurity/detection-engineering/network-security-monitoring-discipline|disciplina de monitoreo]] es el espejo de esta pregunta.
- **Front-loadeá lo reversible y silencioso; diferí lo irreversible y ruidoso.** Recon y enumeración primero; volcado de credenciales y persistencia al final y solo si hace falta. La irreversibilidad es un presupuesto que gastás, no un default.
- **Vivir de la tierra (LOTL).** Preferí el tooling built-in cuya telemetría se mezcla con la actividad de admin normal por sobre herramientas custom ruidosas que disparan detección conductual.
- **Tené múltiples puntos de apoyo/identidades independientes.** Un acceso quemado no debería resetear el engagement; la redundancia es lo que hace sobrevivible un único error ruidoso.
- **Ramificá según la telemetría, no el hábito.** Si existe un camino silencioso al mismo resultado, tomalo; tratá el camino ruidoso como último recurso, no el default.
- **Quedate dentro del scope y time-box (engagements autorizados).** El loop corre bajo reglas de engagement — [[scope-validation|Validación de scope]] y [[recon-to-testing-handoff|Traspaso de recon a testing]] gatean a dónde puede ir.

## Variantes y bypasses
El mismo loop, tres mundos objetivo — la comparación central de la Q2. El invariante son las siete etapas; la *mecánica de etapa y la telemetría* difieren.

### 1. Windows + Active Directory
El loop canónico. Acceso inicial → enumeración de AD ([[cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis|BloodHound]]) → ataques de Kerberos/credenciales (Kerberoast, AS-REP) → lateral vía pass-the-hash / tickets → DCSync / Golden Ticket → Domain Admin. **Telemetría:** event logs de Windows, EDR, Defender for Identity — el [[cybersecurity/security-playbooks/detect-bloodhound-collection|trío de detección de AD]] vive acá. La superficie de detección más rica de las tres.

### 2. macOS
Acceso inicial (phish/installer) → enumeración de TCC y keychain → privesc vía bypass de TCC o misconfig local → lateral a menudo vía SSH o MDM → persistencia vía LaunchAgents/Daemons. **Telemetría:** Endpoint Security Framework (ESF) y Unified Logs. Menos ataques de identidad estilo-grafo; el loop es céntrico en endpoint y MDM.

### 3. Cloud-native
Acceso inicial vía claves filtradas, abuso de OAuth o SSRF-a-metadata → enumeración de IAM → privesc vía abuso de rol/policy (`iam:PassRole`, caminos de policy de escalada de privilegios) → lateral vía roles asumidos / trust cross-account → persistencia vía usuarios IAM, access keys o triggers serverless. **Telemetría:** CloudTrail / Azure Activity / GCP audit logs. El loop tiene *forma de identidad y API*, no de host — el "movimiento lateral" es un `AssumeRole`, no una sesión SMB.

**Híbrido es la realidad de 2026:** los loops reales encadenan AD on-prem → Entra ID → SaaS, cruzando los tres mundos en un engagement — la extensión natural rastreada en [[identity-attack-paths-across-idps|Rutas de ataque de identidad entre IdPs]].

## Impacto
Para una nota de metodología, "impacto" es lo que produce la *calidad de ejecución* del loop:

- **Objetivo alcanzado sin detección (operador maduro)** vs **quema temprana (secuenciamiento descuidado).** La diferencia casi nunca es conocimiento de técnicas — es ordenamiento y conciencia de telemetría.
- **Dwell time y radio de explosión.** Un loop paciente rinde semanas de acceso no detectado y alcance amplio; uno apurado dispara una detección a nivel de etapa y resetea.
- **Para el defensor, el loop es la kill chain a romper.** Cada etapa por la que el operador *debe* pasar es una oportunidad de detección y disrupción; estancá cualquier etapa y el loop no puede cerrar.

## Detección y defensa
El emparejamiento del defensor — cómo romper el loop. Ordenado por efectividad:

1. **Subí el costo de cada etapa (defensa en profundidad).**
   Cada etapa obligatoria es una oportunidad de detección. La meta no es un único muro sino suficiente fricción como para que el operador deba tomar una acción ruidosa o irreversible — que vos estás vigilando.

2. **Colapsá el espacio de decisión con telemetría amplia.**
   EDR (linaje de procesos, acceso a LSASS), identidad (recon LDAP, auth anómala) y red (auth lateral, beaconing de C2) juntas remueven las opciones silenciosas del operador. Cuanto más rica y correlacionada la telemetría, menos caminos hacia adelante quedan invisibles — ver [[cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability|correlación de rutas de ataque]].

3. **Instrumentá más fuerte las etapas irreversibles.**
   El volcado de credenciales, la instalación de persistencia y la auth lateral privilegiada dejan artefactos durables y telemetría distintiva. Concentrá la detección donde el operador se ve forzado a gastar irreversibilidad.

4. **Segmentá la identidad y protegé Tier 0.**
   Si la escalada de privilegios y el movimiento lateral estructuralmente no pueden alcanzar las joyas de la corona, incluso un loop interno exitoso rinde poco — encogé el grafo de ataque ([[cybersecurity/identity-and-active-directory/tier-zero-administration-and-paw|Tier 0]]).

5. **Asumí brecha y cazá el loop interno.**
   La detección debe apuntar a las etapas 3–7, no solo al acceso inicial. La prevención de perímetro sola concede el loop entero en el momento en que aterriza un punto de apoyo.

### Qué no funciona como defensa primaria
- **Solo-perímetro / prevenir-acceso-inicial.** El loop *asume* brecha. Si tu único control es frenar la etapa 2, las etapas 3–7 corren sin observar una vez que alguien entra.
- **Detectar herramientas en vez de comportamientos.** Los operadores renombran, recompilan y reimplementan el tooling. Las *etapas* del loop persisten; las firmas de herramientas no.
- **Tratar las etapas en aislamiento.** Un evento de enumeración solo parece benigno; la kill chain es la *correlación* entre etapas. Las reglas de una sola etapa se pierden el loop.

## Labs prácticos
Esta es una nota de metodología, así que los labs son ejercicios de mapeo/razonamiento más un range ejecutable. Corré cualquier trabajo hands-on solo contra labs propios o engagements autorizados.

### Mapear un engagement sobre el loop y sus ejes
```text
Para tu último engagement autorizado (o un reporte público de APT), completá la tabla:
Etapa                  | Acción tomada           | ¿Reversible? | Telemetría emitida
acceso-inicial         | ...                     | s/n          | ...
enumerar               | ...                     | s/n          | ...
escalada-de-privilegios| ...                     | s/n          | ...
movimiento-lateral     | ...                     | s/n          | ...
Las filas irreversible+ruidoso son donde el defensor tuvo la mejor chance.
```

### Superponer el loop sobre MITRE ATT&CK
```text
Abrí el ATT&CK Navigator (https://mitre-attack.github.io/attack-navigator/)
y coloreá las tácticas que tu loop tocó: Reconnaissance, Initial Access,
Discovery, Privilege Escalation, Lateral Movement, Persistence, Collection,
Exfiltration, Impact. El camino coloreado ES el loop del operador para ese engagement.
```

### Correr una etapa en un lab y mirar la telemetría
```bash
# Levantá Game of Active Directory (GOAD) o DetectionLab, corré BloodHound desde un
# punto de apoyo, y leé lo que ve el defensor (Windows 4662/4661, alerta de
# LDAP-recon de Defender for Identity). Solo lab propio.
# GOAD: https://github.com/Orange-Cyberdefense/GOAD
```
La lección es el *costo de telemetría* de una sola etapa — el input de cada decisión de rama de arriba.

### Construir un árbol de decisión reversible-vs-irreversible
```text
Para un punto de apoyo, enumerá las opciones para llegar a la próxima etapa, etiquetá cada una
reversible/irreversible y silencioso/ruidoso, y ordenalas. Practicar el ordenamiento
es la metodología; las técnicas individuales están en otro lado del branch.
```

## Ejemplos prácticos
- **Engagement de AD silencioso-primero.** Phish → SharpHound (a ritmo) → Kerberoast → crack offline → lateral por pass-the-hash → DCSync → Domain Admin, con el volcado de LSASS diferido hasta que se necesitó una credencial específica. Objetivo alcanzado; pocas acciones irreversibles gastadas.
- **Intrusión paciente del mundo real.** Un APT corre el loop idéntico durante *semanas*, llevando a ritmo la enumeración y el movimiento lateral para quedarse bajo los umbrales conductuales — las mismas etapas, optimizadas para dwell time por sobre velocidad.
- **Loop de nube.** Una clave de CI/CD filtrada → enumeración de IAM → privesc por `iam:PassRole` a un rol admin → `AssumeRole` cross-account → exfiltración de S3. Sin shells de host en ningún lado; todo el loop son llamadas de API en CloudTrail.
- **Loop de macOS.** Installer phisheado → enumeración de TCC/keychain → robo de credenciales del keychain → movimiento lateral asistido por MDM → persistencia por LaunchAgent.
- **Donde el loop se estancó.** Un operador volcó LSASS en la primera hora para "ahorrar tiempo", disparó la detección de acceso-a-LSASS del EDR y perdió el punto de apoyo — un caso de manual de gastar irreversibilidad y ruido demasiado temprano.

## Notas relacionadas
- [[recon|Recon]] — etapa 1; la entrada de recon-externo al loop.
- [[enumeration|Enumeración]] — etapa 3; el motor de conciencia situacional que se re-corre en cada iteración.
- [[recon-to-testing-handoff|Traspaso de recon a testing]] — la frontera de disciplina-de-engagement dentro de la que corre el loop.
- [[scope-validation|Validación de scope]] — el gate de reglas-de-engagement sobre a dónde puede ir el loop.
- [[cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis|Análisis de rutas de ataque con BloodHound]] — la etapa de enumeración del mundo-AD.
- [[cybersecurity/identity-and-active-directory/tier-zero-administration-and-paw|Administración de Tier 0]] — la defensa estructural que mata de hambre a las etapas 4–5.
- [[cybersecurity/security-playbooks/detect-bloodhound-collection|Detectar la recolección de BloodHound]] — el par defensivo para la etapa de enumeración de AD.
- [[cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability|Correlación de rutas de ataque]] — el defensor cosiendo las etapas del loop en una kill chain.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — el meta-encuadre; el loop es la mitad ofensiva.

### Notas atómicas futuras sugeridas
- [[living-off-the-land-and-edr-evasion|Living-off-the-land y evasión de EDR]]
- [[c2-and-command-and-control-tradecraft|Tradecraft de C2 / command-and-control]]
- [[initial-access-techniques|Técnicas de acceso inicial]]
- [[identity-attack-paths-across-idps|Rutas de ataque de identidad entre IdPs]]
- [[detect-the-operator-loop|Detectar el loop del operador]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Foundational:** MITRE ATT&CK Enterprise Matrix (the tactic sequence underpinning the loop) — https://attack.mitre.org/matrices/enterprise/
- **Research / Deep Dive:** Paul Pols — The Unified Kill Chain (end-to-end attack-phase synthesis) — https://www.unifiedkillchain.com/
- **Foundational:** Lockheed Martin — Cyber Kill Chain — https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
