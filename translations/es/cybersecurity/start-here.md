# Empezá acá — triage del vault de ciberseguridad

Llegaste a un vault de 240 notas organizado en 14 ramas. Leerlo linealmente es incorrecto. Esta página te enruta al camino correcto según **quién sos ahora mismo**.

Si no estás seguro de qué persona encaja, arrancá por **"Soy nuevo en ciberseguridad"**: el camino no cuesta nada extra y los fundamentos aplican a todos.

---

## "Soy nuevo en ciberseguridad"

Usaste computadoras, quizás trabajás en IT, pero nunca pensaste security-first como disciplina.

**Tu camino (4-8 semanas de lectura casual):**

1. **Leé [[index|Fundamentos]] (Fase 0) de punta a punta.** 4 notas, ~1 hora. Es el framework que todo lo demás asume.
2. **Leé [[phase-1-substrate|Fase 1 — Sustrato]]** para el recorrido curado de primera pasada de 12 notas por Networking -> Web Security -> Cryptography. Salteá notas que profundicen más de lo que necesitás en la primera vuelta; podés volver.
3. **Leé la lista [[must-know-30|Must-Know 30]]** para ver dónde estás vs dónde querés estar.
4. **Abrí [[phase-2-offense-defense|Fase 2 — Offense / Defense (en pares)]] y leé sus primeros 6 pares.** Ahí empieza a componer la *habilidad real*. La página vuelve operativo el pairing (ritual de 4 pasos por par) para que realmente leas ambos lados en vez de uno solo.
5. **Dejá de intentar aprender todo.** Especializate cuando tengas un contexto laboral que lo demande.

---

## "Soy IT admin / sysadmin / infrastructure engineer"

Operás sistemas. Querés endurecer lo que tenés y razonar con confianza sobre riesgo.

**Tu camino:**

1. **Fase 0 — [[index|Fundamentos]]** — no negociable.
2. **Networking primero, completo:** [[index|Networking]] — gran parte te va a resultar familiar, pero el punto es el encuadre de seguridad sobre cosas que ya conocés.
3. **[[index|Attack Surface Mapping]]** — qué está realmente expuesto y desde dónde.
4. **[[index|Offensive Security / Recon]]** — cómo los atacantes ven tus sistemas.
5. **[[index|Detection Engineering]]** — la mitad que te vuelve empleable en seguridad, no solo en IT.
6. **[[index|Linux Privilege Escalation]]** — si operás servidores Linux, esto no es opcional.
7. **Elegí tu especialidad:** [[index|Cloud]] si operás cloud, [[index|Wireless]] si operás redes de oficina, [[index|DevSecOps]] si sos dueño de un build pipeline.

---

## "Soy software developer"

Escribís código. Querés shippear features que no se vuelvan titulares.

**Tu camino:**

1. **Fase 0 — [[index|Fundamentos]]** — la nota de threat modeling en particular cambia cómo leés tickets.
2. **[[index|Web Security]]** completa. Si construís apps web/mobile, esta es tu superficie diaria.
3. **[[index|API Security]]** — probablemente tu segunda superficie diaria.
4. **[[index|Cryptography]]** enfocada en notas de correctness de aplicación: [[password-hashing|password hashing]], [[jwt-cryptographic-correctness|JWT correctness]], [[aead-and-nonce-misuse|AEAD]], [[certificate-validation-and-pinning|validación de certificados]].
5. **[[index|DevSecOps]]** — tu build pipeline es parte de la superficie de amenaza.
6. **Par de Fase 2 — Offensive + Detection** — incluso una lectura completa cambia cómo escribís código.
7. **Entrá en [[index|Security Playbooks]]** para los procedimientos de testing que sí podés correr sobre tu propio código.

---

## "Estoy reconstruyendo fundamentos deliberadamente"

Estuviste en seguridad o cerca por un tiempo y querés limpiar tu modelo en vez de aprender la próxima herramienta.

**Tu camino:**

1. **Fase 0 — [[index|Fundamentos]]** — sí, incluso si "ya lo sabés". Los reflejos nombrados ahí son lo que evita que practitioners senior se estanquen.
2. **Fase 1 completa**, pero leyendo las *conexiones entre notas* más que el contenido aislado de cada una.
3. **Fase 2 leída en pares** — [[index|Offensive]] y [[index|Detection Engineering]] nota por nota. Este es el movimiento senior que la mayoría de practitioners "experimentados" nunca hizo de verdad.
4. **Auditá tus propios gaps de [[must-know-30|Must-Know 30]].** Si no podés explicar cualquiera de las 30 en 90 segundos, esa es tu próxima lectura.
5. **Leé [[index|Cryptography]] por correctness, no por memorización.** La mayoría de claims "sé crypto" fallan en AEAD, KDFs o [[random-and-csprng-pitfalls|pitfalls de CSPRNG]].
6. **Pasá un sistema real que operes** por [[threat-modeling-quickstart|Threat Modeling Quickstart]]. El ejercicio revela qué rama deberías refrescar después.

---

## "Quiero entrar a seguridad como carrera"

Querés un trabajo en seguridad y estás trabajando hacia atrás desde ahí.

**Tu camino:**

1. Leé las cuatro personas anteriores. Tu camino real es una mezcla de "nuevo en ciberseguridad" (fundamentos) + la persona más cercana a tu trabajo actual (IT admin / developer) + la disciplina de reconstrucción.
2. **Fase 0 + Fase 1 + Fase 2** es el portfolio mínimo de *entendimiento*. Sin eso vas a ser un operador de botones para cualquier stack de herramientas.
3. **[[index|Security Playbooks]]** es donde el entendimiento se vuelve capacidad. Elegí tres playbooks y ejecutalos sobre targets propios/autorizados hasta poder correrlos de memoria.
4. **[[phase-4-specialty|Fase 4 — Specialty Tracks]]** — elegí *un* track (API / Cloud / DevSecOps / Wireless) según tu contexto laboral. Los generalistas son valiosos; los candidatos de "aplico a cualquier trabajo cyber" no.
5. **[[index|Privacy, Anonymity & OPSEC]]** también es profesionalmente útil: todo engagement ofensivo, toda investigación IR y todo trabajo de threat intel tiene requisitos de OPSEC.

---

## "Solo quiero leer una cosa"

Leé [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|What Is Cybersecurity, and Why It Is Not a Tool List]]. Esa nota sola vale más que la mayoría de cursos "Intro to cybersecurity".

---

## Navegación relacionada

- [[index|Índice de ciberseguridad]] — listado completo de ramas y orden de estudio.
- [[index|Fundamentos]] — entrada de Fase 0.
- [[must-know-30|Must-Know 30]] — el corte diagonal de 30 must-know entre ramas.
- [[index|Security Playbooks]] — concepto llevado a procedimiento.
