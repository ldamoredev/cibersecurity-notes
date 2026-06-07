# Índice de ciberseguridad

## Propósito

Este es el índice raíz de la rama de ciberseguridad del vault.

El objetivo de este sistema es pasar de:
- aprender conceptos de seguridad aislados

a:
- construir un grafo conectado de conocimiento de seguridad
- entender exposición, explotación y defensa como un solo sistema
- vincular conceptos con workflows prácticos, playbooks y decisiones de ingeniería

Este vault está estructurado para soportar:
- aprendizaje de seguridad
- testing práctico
- razonamiento de arquitectura
- recuperación a largo plazo tanto por mí como por workflows asistidos por LLM

---

## Cómo está organizado este vault

El vault está dividido en ramas canónicas.

### Orientación (empezá acá)

El framework que todo lo demás asume; leelo primero.

- [[index|Fundamentos]] (Fase 0)
- [[start-here|Empezá acá]] — página de triage por persona
- [[must-know-30|Must-Know 30]] — alfabetización mínima viable entre ramas

### Sustrato (cómo funcionan realmente las cosas)

Leé en orden. Networking es el sustrato de todo lo demás, Web Security es la superficie diaria, Cryptography es la capa de correctness.

- [[index|Networking]]
- [[index|Web Security]]
- [[index|Cryptography]]

### Offense / Defense (en pares)

Leé nota por nota como pares. Estudiar una sola mitad te estanca.

- [[index|Offensive Security / Recon]]
- [[index|Detection Engineering]]

### Superficie de operador

Qué está realmente expuesto, de dónde viene la evidencia y cómo los conceptos se vuelven procedimientos repetibles.

- [[index|Attack Surface Mapping]]
- [[index|OSINT]]
- [[index|Linux Privilege Escalation]]
- [[index|Security Playbooks]]

### Specialty tracks (elección por contexto laboral)

Elegí lo que tu trabajo demande. No son prerequisitos entre sí.

- [[index|API Security]]
- [[index|Cloud Security]]
- [[index|DevSecOps]]
- [[index|Wireless Security]]
- [[index|Identity and Active Directory]]
- [[index|Binary Exploitation]]

### Always-on (disciplina personal paralela)

No es una fase. Leela junto con todo lo demás.

- [[index|Privacy, Anonymity & OPSEC]]

---

## Orden de estudio recomendado

> **Roadmap v2 — aterrizado el 2026-05-10.** Reorganizado para la persona de IT entrando a cyber. Fase 0 nombra los modelos mentales; Fase 1 enseña el sustrato (Networking primero porque es el sustrato de todo lo demás, luego Web Security como superficie diaria, luego Cryptography cuando TLS/JWTs ya son lo suficientemente concretos para motivarla); Fase 2 empareja Offensive Security con Detection Engineering nota por nota; Fase 3 convierte concepto en capacidad de operador; Fase 4 es especialización elegida por contexto laboral, no como prerequisito. Privacy, Anonymity & OPSEC se reencuadra como disciplina personal always-on, no como fase. Ver [[start-here|Empezá acá]] para la página de triage por persona.

### Fase 0 — Orientación (empezá acá)

1. [[index|Fundamentos]] — los modelos mentales que todas las otras ramas asumen que ya tenés.

### Fase 1 — Sustrato (cómo funcionan realmente las cosas)

> Página de entrada: [[phase-1-substrate|Fase 1 — Sustrato]] — primera pasada curada de 12 notas + camino extendido de 13 notas por Networking + Web Security + Cryptography.
> 1. [[index|Networking]] — el sustrato de todo lo demás.
> 2. [[index|Web Security]] — la superficie diaria que la mayoría de gente de IT toca.
> 3. [[index|Cryptography]] — la capa de correctness; cobra sentido después de que TLS y sesiones son concretos.

### Fase 2 — Offense / defense en pares

> Página de entrada: [[phase-2-offense-defense|Fase 2 — Offense / Defense (en pares)]] — 6 pares de primera pasada + 3 pares extendidos, cada uno con el ritual de lectura en pares de 4 pasos.
> 4. [[index|Offensive Security / Recon]] — cómo los atacantes descubren y validan.
> 5. [[index|Detection Engineering]] — leer nota por nota emparejada con #4.

### Fase 3 — Superficie de operador

> Página de entrada: [[phase-3-operator|Fase 3 — Superficie de operador]] — loop de workflow de 4 ramas (surface mapping -> OSINT -> privesc -> playbooks) con un camino curado de primera pasada de 12 notas.
> 6. [[index|Attack Surface Mapping]] — qué está realmente expuesto.
> 7. [[index|OSINT]] — manejo de evidencia de fuentes públicas.
> 8. [[index|Linux Privilege Escalation]] — fallas de límites locales después de un foothold.
> 9. [[index|Security Playbooks]] — conceptos como procedimientos repetibles.

### Fase 4 — Specialty tracks (elegí lo que tu trabajo demande)

> Página de entrada: [[phase-4-specialty|Fase 4 — Specialty Tracks]] — shaped por persona: 6 tracks (API / Cloud / DevSecOps / Wireless / Identity & AD / Binary Exploitation), cada uno con sus condiciones de entrada y camino curado. Elegí uno; la lectura generalista en paralelo es el movimiento equivocado acá.
> 10. [[index|API Security]]
> 11. [[index|Cloud Security]]
> 12. [[index|DevSecOps]]
> 13. [[index|Wireless Security]]
> 14. [[index|Identity and Active Directory]]
> 15. [[index|Binary Exploitation]]

### Always-on — Disciplina personal (paralela, de por vida)

- [[index|Privacy, Anonymity & OPSEC]] — no es una fase. Leela junto con todo lo demás, refrescala cada vez que cambie tu threat model.

## Roles de las ramas

### Foundations (Fase 0)

Explica:
- qué es realmente ciberseguridad (y por qué no es una lista de herramientas)
- la tríada CIA como *herramienta de decisión*, no como definición
- el reflejo de threat modeling de 4 preguntas / STRIDE
- la dualidad atacante-defensor como el metamarco que todas las otras ramas asumen

Fase 0 es la única rama que todo learner lee sin importar su rol.

### Networking

Explica:
- transporte
- reachability
- comportamiento HTTP
- proxies
- caminos internos vs externos

Es el sustrato para web, API, SSRF, request smuggling y razonamiento de superficie de ataque.

### Web Security

Explica:
- clases clásicas de vulnerabilidades web
- comportamiento del navegador
- sesiones
- access control
- patrones de exploit server-side

### Cryptography

Explica:
- hashes, cifrado, MACs, firmas, key exchange y CSPRNGs
- TLS/PKI, firma JWT, password hashing y correctness de KDF
- cómo fallan nonce reuse, modos débiles, algorithm confusion y diseños roll-your-own

Es la capa de correctness debajo de TLS, sesiones, JWTs, MFA/passkeys, secrets management y tooling de privacidad. Queda después de Networking en el nuevo orden de estudio porque crypto cobra más sentido cuando TLS y sesiones ya son concretos.

### Wireless Security

Explica:
- Wi-Fi como comportamiento de radio, frames, asociación y autenticación
- observación en monitor-mode y packet capture
- WEP, handshakes WPA/WPA2 y riesgo de passphrase
- deauthentication, rogue access points y MITM en red local

Specialty track en el nuevo orden: leela cuando tu trabajo demande Wi-Fi específico.

### API Security

Explica:
- autorización a nivel objeto, función y propiedad
- confianza en tokens
- inventory drift
- patrones de abuso machine-readable

### Cloud Security

Explica:
- responsabilidad compartida cloud, identidad y límites seguros de lab
- IAM, metadata, storage, red, DNS/TLS, secrets y controles de logging
- cómo la mala configuración cloud se vuelve superficie de ataque

### Attack Surface Mapping

Explica:
- qué está realmente expuesto
- qué es reachable
- qué es discoverable
- qué se desvió del diseño previsto

### Offensive Security / Recon

Explica:
- cómo descubren los atacantes
- cómo se validan hallazgos
- cómo recon se convierte en testing

### Linux Privilege Escalation

Explica:
- cómo fallan los límites locales de privilegio en Linux después de un foothold autorizado
- cómo la enumeración convierte pistas del host en hipótesis rankeadas de escalada
- cómo verificar de forma segura hallazgos de sudo, SUID/SGID, capabilities, scheduled jobs, PATH, kernel y LinPEAS

### Privacy, Anonymity & OPSEC

Explica:
- cómo las herramientas de privacidad cambian visibilidad de observadores y confianza
- por qué las VPNs son herramientas de ruteo de privacidad, no garantías de anonimato
- cómo metadata, cuentas, estado del navegador, archivos y comportamiento filtran identidad
- cómo Tor, sistemas compartimentalizados, comunicación cifrada y borrado seguro encajan en un threat model

### OSINT

Explica:
- cómo se recolecta y evalúa información de fuentes públicas
- cómo pistas públicas se vuelven evidencia en vez de guesses
- cómo manejar ética y correctamente datos de personas, compañías, media, breaches y search

### DevSecOps

Explica:
- workflow de desarrollo seguro
- software supply chain
- hardening de CI/CD
- confianza en releases
- secrets, containers y artifacts

### Detection Engineering

Explica:
- fuentes de telemetría y límites de visibilidad
- observabilidad de red, pipelines IDS/IPS y correlación behavioral
- Zeek, Suricata, NetFlow/IPFIX, EDR, cloud y joins endpoint-network
- por qué la defensa moderna es behavioral y correlacional más que signature-only

### Security Playbooks

Explica:
- cómo operacionalizar conceptos
- cómo testear clases específicas de debilidad
- cómo pasar de teoría a procedimiento repetible

## Registros de referencias

Estas son las notas source-of-truth para referencias en cada rama.

- [[reference-registry-cryptography|Reference Registry — Cryptography]]
- [[reference-registry-networking|Reference Registry — Networking]]
- [[reference-registry-wireless-security|Reference Registry — Wireless Security]]
- [[reference-registry-web-security|Reference Registry — Web Security]]
- [[reference-registry-api-security|Reference Registry — API Security]]
- [[reference-registry-cloud-security|Reference Registry — Cloud Security]]
- [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]]
- [[reference-registry-osint|Reference Registry — OSINT]]
- [[reference-registry-devsecops|Reference Registry — DevSecOps]]
- [[reference-registry-detection-engineering|Reference Registry — Detection Engineering]]
- [[reference-registry-binary-exploitation|Reference Registry — Binary Exploitation]]
- [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]]
- [[reference-registry-offensive-security|Reference Registry — Offensive Security]]
- [[reference-registry-linux-privilege-escalation|Reference Registry — Linux Privilege Escalation]]
- [[reference-registry-privacy-anonymity-opsec|Reference Registry — Privacy, Anonymity & OPSEC]]
- [[reference-registry-playbooks|Reference Registry — Playbooks]]

---

## Reglas de trabajo del vault

### Notas canónicas

Cada rama debería usar:
- un `index.md` canónico
- notas atómicas con alcance claro
- links fuertes a notas relacionadas
- referencias alineadas al registry de la rama

### Playbooks

Los playbooks deberían:
- operacionalizar conceptos
- conectarse con las notas canónicas relevantes
- mantenerse procedurales, no conceptuales

### Links entre ramas

Los links entre ramas deberían:
- ser significativos
- explicar mecanismos, trust boundaries, exploit flow o diseño de controles
- mantenerse selectivos en vez de exhaustivos

### Regla de cleanup

Cuando existan notas superpuestas:
- preservá la nota canónica
- archivá duplicados más débiles o viejos
- mergeá insights únicos en vez de perderlos

---

## Foco actual

Las ramas maduras actuales, listadas en el nuevo orden de estudio:

- [[index|Foundations]] (Fase 0)
- [[index|Networking]]
- [[index|Web Security]]
- [[index|Cryptography]]
- [[index|Offensive Security / Recon]]
- [[index|Detection Engineering]]
- [[index|Attack Surface Mapping]]
- [[index|OSINT]]
- [[index|Linux Privilege Escalation]]
- [[index|Privacy, Anonymity & OPSEC]]
- [[index|Security Playbooks]]

Este índice raíz debería seguir siendo una nota de navegación y sistema, no una nota resumen gigante.

---

## Futuras adiciones sugeridas

Ramas futuras potenciales:
- mobile-security
- reverse-engineering
- social-engineering
- ai-security / agent-security

Solo deberían agregarse cuando su estructura de rama y registro de referencias sean lo suficientemente maduros.
