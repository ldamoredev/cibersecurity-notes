# Fase 4 — Specialty Tracks (elegí lo que tu trabajo demande)

Fase 4 es la **única fase que no se lee linealmente**. Por diseño, se elige por contexto laboral: elegís la especialidad que tu rol realmente requiere, la aprendés con profundidad suficiente para ser efectivo y volvés a las demás solo cuando tu trabajo se expande hacia ellas.

Los generalistas que intentan leer todas las ramas de Fase 4 en paralelo producen conocimiento superficial de todas y profundidad en ninguna. El camino especialista es el correcto acá.

Seis tracks, cada uno con su persona, camino curado y condiciones de entrada:

> **API Security · Cloud Security · DevSecOps · Wireless Security · Identity & Active Directory · Binary Exploitation**

Cada track asume que completaste primera pasada de Fases 0-2; algunos también asumen Fase 3. Las condiciones de entrada del track se declaran explícitamente. **El track de Binary Exploitation tiene los prerequisitos no-vault más fuertes** (alfabetización C/C++, fluidez con debugger, baseline x86-64); ver Track F.

---

## Track A — API Security

**Elegí esto si:** construís, testeás u operás APIs (REST, GraphQL, gRPC). La mayoría de ingeniería web/mobile/SaaS moderna toca esto.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa (especialmente [[http-overview|HTTP overview]], [[http-headers|HTTP headers]], [[tls-https|TLS/HTTPS]]).
- Básicos de [[index|Web Security]] completos: las APIs heredan gran parte del threat model web.

**Camino de primera pasada (8 de 14 notas):**

1. **[[api-security-top-10|API Security Top 10]]** — el canon OWASP API; el punto de entrada correcto porque enmarca cada nota posterior.
2. **[[api-inventory-management|API Inventory Management]]** — no podés securizar APIs que no sabés que existen. Inventory es la primera capacidad.
3. **[[broken-object-level-authorization|Broken Object Level Authorization (BOLA)]]** — la clase de vulnerabilidad API #1 por frecuencia real. El sibling API-shaped de IDOR.
4. **[[broken-function-level-authorization|Broken Function Level Authorization]]** — fallas de límites admin/rol en routing API.
5. **[[broken-object-property-level-authorization|Broken Object Property Level Authorization]]** — autorización fine-grained a nivel campo; cierra los gaps que las dos anteriores dejan abiertos.
6. **[[broken-authentication|Broken Authentication]]** — fallas de emisión, refresh, validación y rotación de tokens.
7. **[[jwt-attacks|JWT Attacks]]** — las fallas más comunes de confianza en token, emparejada con [[jwt-cryptographic-correctness|JWT Cryptographic Correctness]] de Fase 1.
8. **[[excessive-data-exposure|Excessive Data Exposure]]** — APIs que devuelven más de lo que deberían; la falla de data minimization.

**Extendido (6 más):** [[api-auth-flaws|API auth flaws]], [[api-rate-limiting|API rate limiting]], [[authorization|Authorization]], [[token-lifecycle|Token lifecycle]], [[mass-assignment|Mass assignment]], [[polymorphic-deserialization|Polymorphic deserialization]].

**Terminaste primera pasada de API cuando:** dado cualquier API endpoint, podés recorrerlo con las 8 notas de arriba como checklist y articular cuáles de los 8 controles implementa correctamente, cuáles implementa débilmente y cuáles saltea.

---

## Track B — Cloud Security

**Elegí esto si:** tus sistemas corren en cloud (AWS, GCP, Azure, multi-cloud) y los límites de seguridad que te importan viven en control planes cloud, no en equipos de red on-prem.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa.
- [[index|Cryptography]] al menos hasta [[hashing-vs-encryption-vs-signing|hashing vs encryption vs signing]]; razonar sobre IAM y keys depende de eso.

**Camino de primera pasada (6 de 10 notas):**

1. **[[cloud-security-basics|Cloud Security Basics]]** — modelo de responsabilidad compartida y qué garantiza realmente el cloud provider vs qué es tuyo.
2. **[[cloud-iam-boundaries|Cloud IAM Boundaries]]** — IAM es el control primario de cloud security. Todo lo demás está downstream.
3. **[[cloud-metadata-security|Cloud Metadata Security]]** — el metadata endpoint es la superficie cloud más atacada; SSRF + cloud metadata = compromiso.
4. **[[cloud-network-boundaries|Cloud Network Boundaries]]** — security groups, VPC peering, transit gateways y cómo la confianza de networking se traduce a cloud.
5. **[[cloud-secrets-management|Cloud Secrets Management]]** — credenciales short-lived, KMS, rotación de secrets, por qué hard-codear keys es la falla cloud canónica.
6. **[[public-cloud-storage-exposure|Public Cloud Storage Exposure]]** — mala configuración estilo bucket S3, por frecuencia el hallazgo cloud público más encontrado.

**Extendido (4 más):** [[cloud-logging-and-detection|Cloud logging and detection]], [[cloud-dns-and-certbot|Cloud DNS and Certbot]], [[ssh-access-to-cloud-hosts|SSH access to cloud hosts]], [[cloud-lab-infrastructure|Cloud lab infrastructure]].

**Terminaste primera pasada de Cloud cuando:** para cualquier workload cloud, podés recorrer su IAM role / exposición de red / reachability de metadata / manejo de secrets / exposición de storage y evaluar cada uno en menos de 10 minutos contra las 6 notas de arriba.

---

## Track C — DevSecOps

**Elegí esto si:** sos dueño (o contribuís a) un pipeline CI/CD, proceso de release, build de container o control de supply-chain. Este track es cada vez menos opcional para roles backend / platform / SRE.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa (especialmente [[digital-signatures|Digital signatures]] para razonamiento de integridad de artifacts).
- Primera pasada de Fase 2 ayuda, pero no es estrictamente requerida.

**Camino de primera pasada (7 de 12 notas):**

1. **[[secure-by-design|Secure by Design]]** — la filosofía que impulsa todas las otras notas; sin esto el resto se vuelve checklist.
2. **[[ci-cd-hardening|CI/CD Hardening]]** — el build pipeline es parte de la superficie de ataque. Esta nota nombra qué endurecer primero.
3. **[[secrets-management|Secrets Management]]** — la falla canónica de CI/CD. Hard-coded keys, logs expuestos, tokens filtrados.
4. **[[supply-chain-security|Supply Chain Security]]** — el threat model que motiva SBOM, signing y provenance.
5. **[[sbom-and-provenance|SBOM and Provenance]]** — cómo saber qué estás shippeando realmente. SLSA, Sigstore, in-toto.
6. **[[dependency-risk|Dependency Risk]]** — la superficie de dependencias open-source como amenaza de primera clase.
7. **[[container-security|Container Security]]** — amenazas de imagen, runtime y capa de orquestación.

**Extendido (5 más):** [[artifact-integrity|Artifact integrity]], [[image-scanning|Image scanning]], [[branch-protection-and-release-controls|Branch protection and release controls]], [[nist-ssdf|NIST SSDF]], [[asvs-as-dev-process-input|ASVS as dev process input]].

**Terminaste primera pasada de DevSecOps cuando:** podés [[threat-modeling-quickstart|threat-model]] tu propio pipeline CI/CD end-to-end y nombrar los controles que protegen cada etapa (commit -> build -> test -> publish -> deploy).

---

## Track E — Identity and Active Directory

**Elegí esto si:** hacés red-team / pentest en entornos AD, administrás AD, respondés incidentes basados en identidad o trabajás en ingeniería de identity-platform (AD, Entra ID, hybrid). Relevancia de alta frecuencia para roles de seguridad enterprise.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa (especialmente [[password-hashing|password hashing]] y [[symmetric-encryption-modes|symmetric encryption modes]]; ataques a credenciales AD son problemas de economía KDF/cifrado).
- Primera pasada de Fase 2 completa: los ataques AD *no* tienen detección signature-based útil; el encuadre behavioral es obligatorio.

**Camino de primera pasada (4 notas, leer en orden):**

1. **[[bloodhound-attack-path-analysis|BloodHound and Attack Path Analysis]]** — la capa de visibilidad. Te dice qué ataques AD valen la pena y qué ACLs defensivas arreglar primero.
2. **[[as-rep-roasting|AS-REP Roasting]]** — el ataque *pre-foothold* que no requiere credenciales, solo usernames.
3. **[[kerberoasting|Kerberoasting]]** — el ataque *post-foothold* contra cuentas con SPNs.
4. **[[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit Extraction]]** — el endgame: recuperar cada hash incluido `krbtgt`, habilitando Golden Tickets y compromiso permanente del domain.

**Extendido (notas futuras sembradas):** Golden Ticket forgery, Silver Ticket persistence, Pass-the-Hash, DCShadow, krbtgt rotation, Exchange permission legacy, UAC flags, shadow credentials / PKINIT, Tier 0 administration / PAW.

**Terminaste primera pasada de Identity & AD cuando:** dado cualquier entorno AD, podés recolectar con BloodHound, identificar el camino más corto desde cualquier usuario no privilegiado a Domain Admin, nombrar las dos ACE edges más baratas que defensores deberían remover y ejecutar una cadena ofensiva end-to-end contra un lab autorizado.

---

## Track D — Wireless Security

**Elegí esto si:** trabajás con redes Wi-Fi en cualquier profundidad: assessment de Wi-Fi corporativo, seguridad de sucursales, wireless penetration testing o construcción de productos wireless. Elegí esto *último* si tu rol es web/cloud/API; wireless es genuinamente un specialty track.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa (especialmente [[tcp-ip-basics|TCP/IP basics]] y [[ports-and-services|Ports and services]]; Wi-Fi es L1/L2 debajo del mismo TCP/IP).
- Hardware: se requiere un adaptador Wi-Fi que soporte monitor mode para que los labs de este track sean útiles.

**Camino de primera pasada (5 de 10 notas):**

1. **[[wireless-security|Wireless Security]]** — el modelo mental de rama: Wi-Fi como radio + frames + asociación + autenticación.
2. **[[wifi-monitor-mode|Wi-Fi Monitor Mode]]** — la capacidad fundacional; sin capture en monitor-mode, el resto es teoría.
3. **[[wpa-wpa2-handshakes|WPA/WPA2 Handshakes]]** — el target canónico de captura y cracking.
4. **[[wifi-deauthentication|Wi-Fi Deauthentication]]** — el movimiento que convierte "esperar a que conecte un cliente" en "forzar uno a reconectar ahora". Fundacional para handshake capture y evil-twin attacks.
5. **[[evil-twin-access-points|Evil Twin Access Points]]** — el ataque rogue-AP que convierte superficie wireless en compromiso de credenciales / sesión.

**Extendido (5 más):** [[wifi-wordlist-attacks|Wi-Fi wordlist attacks]], [[wep-security|WEP security]], [[mitm-on-local-networks|MITM on local networks]], [[arp-poisoning|ARP poisoning]], [[bettercap-workflows|Bettercap workflows]].

**Terminaste primera pasada de Wireless cuando:** podés capturar un handshake WPA2 de una red de prueba autorizada, crackearlo contra una wordlist controlada y articular por qué tu Wi-Fi corporativo *es o no* vulnerable al mismo workflow.

---

## Track F — Binary Exploitation

**Elegí esto si:** hacés vulnerability research, exploit development, security engineering para software low-level (kernels de OS, hypervisors, navegadores, runtimes de lenguajes), competencias CTF categoría pwn, autoría de tooling de seguridad o mantenés código memory-unsafe en cualquier contexto productivo. **Los prerequisitos no-vault más fuertes de cualquier track**: esta es la especialidad técnica más profunda del vault por distancia de escalera desde código fuente.

**Condiciones de entrada:**
- Primera pasada de Fase 1 completa.
- **Alfabetización de programación C/C++** — la rama asume que podés leer C, tenés un modelo mental funcional de stack frames y heap allocation, y estás cómodo con un debugger (`gdb` / `lldb` / WinDbg). Si no, trabajá *Practical Binary Analysis* u OpenSecurityTraining x86 / OS-internals primero.
- **Baseline Linux + x86-64.** La mayoría de labs targetean Linux sobre x86-64. aarch64, macOS y especificidades Windows se llaman por nota cuando aparecen.
- Primera pasada de Fase 2 útil pero no estrictamente requerida (la detección de exploits vive mayormente dentro de las notas de mitigación de la propia rama más el cross-link [[edr-network-observability-and-process-correlation|EDR / process correlation]]).

**Camino de primera pasada (2 notas, leer en orden):**

1. **[[memory-corruption|Memory Corruption]]** — el concepto raíz, la taxonomía de 6 clases (stack overflow / heap overflow / use-after-free / double-free / out-of-bounds read / integer overflow) y la cadena desde bug a exploit primitive a code execution.
2. **[[stack-buffer-overflow|Stack Buffer Overflow]]** — el ejemplo trabajado canónico de clase 1. El deep-dive que introduce layout de stack, control de return-address, cadena de mitigaciones (canary -> ASLR -> DEP -> CET -> MTE -> PAC), razonamiento estilo ROP y workflow de exploit-development estilo pwntools.

**Extendido (notas futuras sembradas):** Heap exploitation, use-after-free, double-free, info-leak primitives, ROP / ret2libc, ASLR / PIE leak chains, format-string bugs, exploit mitigations (el panorama completo), stack canaries / shadow stacks / PAC, ARM MTE, CFI, formato ELF, loop de reverse-engineering, fuzzing con libFuzzer / AFL++, sanitizers (ASAN / MSAN / UBSan), symbolic execution con angr.

**Terminaste primera pasada de Binary Exploitation cuando:** dado un programa C vulnerable, podés identificar la clase de bug, localizar la saved return address (o primitive equivalente de control-flow), construir un exploit funcional contra un build sin mitigaciones, articular qué mitigaciones derrotan ese exploit simple y nombrar al menos dos primitives que encadenarías para derrotarlas. El exploit script estilo pwntools para un challenge CTF básico de stack-overflow debería ser una tarea de 20 líneas, no una tarde.

---

## Cómo Fase 4 conecta con fases anteriores

| Track de Fase 4 | Dependencias más fuertes de Fase 0-3 |
| --- | --- |
| API Security | Web Security (Fase 1), JWT correctness (Fase 1 Crypto), Broken Access Control + playbook IDOR (Fase 3) |
| Cloud Security | Networking + Crypto (Fase 1), SSRF + metadata endpoints (Fase 1 Web), playbook Investigate-SSRF (Fase 3) |
| DevSecOps | Crypto digital signatures + AEAD (Fase 1), threat-modeling (Fase 0), cada par de Fase 2 para pensar "¿mi pipeline es detectable?" |
| Wireless Security | Networking L1/L2/L3 (Fase 1), pairing de evasión y detección (Fase 2) |
| Identity & Active Directory | Password hashing + symmetric encryption modes (Fase 1 Crypto), behavioral-vs-signature detection (Fase 2), dualidad atacante-defensor (Fase 0) |
| Binary Exploitation | **Alfabetización C/C++ + fluidez con debugger + baseline x86-64 (prerequisitos no-vault)**, threat-modeling en la capa systems-software (Fase 0), telemetría de detección del lado EDR (Fase 2) |

Elegí el track cuyas dependencias ya cubriste; ese es el camino más eficiente.

---

## Elegir más de un track

La disciplina paralela always-on de [[index|Privacy, Anonymity & OPSEC]] es tu quinto track en espíritu: corre junto a todos los demás y nunca deja de ser relevante.

Si tu rol demanda dos especialidades (por ejemplo, API + Cloud es común en ingeniería backend moderna), hacelas **secuencialmente, no en paralelo**. Terminá primera pasada de una, luego empezá primera pasada de la otra. Leer en paralelo produce retención más superficial en ambas.

---

## Qué hay después de Fase 4

No hay Fase 5 en este vault. Después de primera pasada de especialidad de Fase 4, estás operando como especialista con amplitud completa en Fases 0-3 y profundidad en una (o dos, secuencialmente) áreas de especialidad. El próximo movimiento de aprendizaje está **fuera de este vault**:

- **Engagements reales** bajo autorización: bug bounty programs, ejercicios internos red/purple-team, drills IR.
- **Defender un sistema real** que use tu especialidad: construir u operar uno es el contexto de aprendizaje de mayor leverage.
- **Las ramas futuras sugeridas** en [[index|Índice de ciberseguridad]] (mobile, reverse-engineering, social-engineering, AI/agent-security): abrirlas cuando se vuelvan relevantes laboralmente.

La estructura del vault termina acá. Todo lo demás es profundidad.

---

## Navegación relacionada

- [[start-here|Empezá acá]] — página de triage por persona (las personas ahí mapean a los tracks de acá).
- [[phase-1-substrate|Fase 1 — Sustrato]] · [[phase-2-offense-defense|Fase 2 — Offense / Defense]] · [[phase-3-operator|Fase 3 — Superficie de operador]] — páginas de entrada de fases previas.
- [[index|Fase 0 — Fundamentos]] — modelos mentales que los seis tracks asumen.
- [[index|Índice de API Security]] · [[index|Índice de Cloud Security]] · [[index|Índice de DevSecOps]] · [[index|Índice de Wireless Security]] — listados completos de ramas.
- [[index|Privacy, Anonymity & OPSEC]] — la disciplina paralela always-on.
- [[must-know-30|Must-Know 30]] — lista must-know transversal.
- [[index|Índice de ciberseguridad]] — roadmap completo del vault.
