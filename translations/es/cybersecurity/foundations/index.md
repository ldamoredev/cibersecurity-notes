---
type: index
status: active
created: 2026-05-10
updated: 2026-05-13
tags:
  - cybersecurity
  - foundations
  - index
  - phase-0
---

# Índice de Fundamentos — Fase 0

## Propósito
Este índice es lo **primero** que un estudiante debería leer en el vault. Existe porque toda otra rama asume que el estudiante ya *piensa security-first*. La Fase 0 construye esa mentalidad antes de abrir cualquier rama técnica.

Volvé al [[cybersecurity/index|Índice de Ciberseguridad]] para navegar entre ramas.

---

## Para quién es esta rama

- Persona de IT que nunca pensó la seguridad como disciplina.
- Desarrollador al que le dijeron que "haga seguridad" y no está seguro de qué significa eso.
- Ingeniero senior que reconstruye las bases deliberadamente.
- Cualquiera que haya confundido "sé Wireshark" con "entiendo seguridad".

Si ya pensás en términos de la tríada CIA, reflejos de modelado de amenazas y emparejamiento ofensa/defensa, ojeá esta rama y pasá a [[cybersecurity/networking/index|Redes]].

---

## Orden de lectura recomendado

### Fase 0 — Orientación
1. [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|Qué es la ciberseguridad y por qué no es una lista de herramientas]]
2. [[cia-triad-and-what-it-actually-decides|Tríada CIA — Qué decide en realidad]]
3. [[threat-modeling-quickstart|Arranque rápido de modelado de amenazas]]
4. [[attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor como herramienta de aprendizaje]]
5. [[minimum-viable-cybersecurity-literacy|Alfabetización mínima viable en ciberseguridad]]
6. [[job-context-specialization|Especialización por contexto de trabajo]]
7. [[certifications-as-validation-signals|Las certificaciones como señales de validación]]

Después de las primeras cuatro notas de orientación, usá las notas 5-7 al elegir un camino de aprendizaje, track de especialidad o secuencia de certificación. Luego seguí a la Fase 1 — Sustrato, empezando por [[cybersecurity/networking/index|Redes]] (el nuevo orden de la Fase 1 es Redes → Seguridad Web → Criptografía; ver [[cybersecurity/index|Índice de Ciberseguridad]] para el rastro de migración).

---

## Convenciones de la rama

Las notas de la Fase 0 son **notas de marco**, no notas técnicas. Se diferencian de las notas atómicas de otras ramas en dos formas:

- Enseñan *cómo razonar*, no *qué es una vulnerabilidad*. Por eso saltean las secciones "Variantes y bypasses" y "Labs prácticos" de la plantilla de nota atómica, y en su lugar usan "Errores comunes" y "Cómo aplicar esto".
- No necesitan un `reference-registry-foundations.md` dedicado. Las referencias son documentos de marco (NIST CSF, OWASP, guía de modelado de amenazas de Microsoft) y se listan directamente en la sección `## Referencias` de cada nota.

Si la rama crece más allá de ~6 notas, debería agregarse un registro.

---

## Cross-links a otras ramas

Las notas de la Fase 0 están pensadas para enlazarse **desde** la primera nota del índice de cada rama (una entrada "Antes de esta rama"), dándole a cada estudiante un camino alcanzable de vuelta al marco.

- [[cybersecurity/networking/index|Redes]] — Fase 1, primera rama técnica
- [[cybersecurity/web-security/index|Seguridad Web]] — Fase 1, la superficie de todos los días
- [[cybersecurity/cryptography/index|Criptografía]] — Fase 1, después de que TLS se vuelve concreto
- [[cybersecurity/offensive-security/index|Seguridad Ofensiva / Recon]] — Fase 2, emparejada con detección
- [[cybersecurity/detection-engineering/index|Ingeniería de Detección]] — Fase 2, emparejada con ofensa
