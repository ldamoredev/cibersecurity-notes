---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - owasp
sources: []
---

# OWASP Top 10

## Definición
El OWASP Top 10 es un documento de concientización de alto nivel que resume las categorías de riesgo de seguridad de aplicaciones web más importantes. No es una metodología completa, pero es uno de los mejores mapas de partida para lo que repetidamente sale mal en aplicaciones reales.

## Por qué importa
Esta nota importa porque ayuda a organizar el branch de web-security alrededor de causas raíz en vez de exploits al azar. Te da un vocabulario para las categorías de riesgo comunes y un marco compartido para discutir prioridades, testeo y mitigación.

## Perspectiva del atacante
A los atacantes no les importa el Top 10 como checklist. Les importan las clases subyacentes de debilidad que nombra:
- control de acceso roto
- inyección
- diseño inseguro
- fallas de identificación y autenticación
- mala configuración de seguridad

El valor de esta nota no es la memorización. Es aprender de dónde vienen familias enteras de errores explotables.

## Perspectiva del defensor
Los defensores deberían usar el Top 10 como:
- una ayuda de priorización
- una herramienta de comunicación con los desarrolladores
- un puente hacia estándares más profundos como WSTG y ASVS

Es útil para orientación, pero no alcanza por sí solo para testear o asegurar una aplicación.

## Ejemplos prácticos
- Un equipo dice "no tenemos inyección SQL", pero igual tiene control de acceso roto y diseño inseguro.
- Una revisión nombra "XSS" como el problema, pero la causa raíz es un manejo de input/output más amplio y controles de seguridad faltantes.
- Una hoja de ruta usa las categorías del Top 10 para decidir qué labs y playbooks construir primero.

## Notas relacionadas
- [[broken-access-control|Control de acceso roto]]
- [[auth-flaws|Fallas de autenticación]]
- [[sql-injection|Inyección SQL]]
- [[xss|XSS]]
- [[ssrf|SSRF]]

## Referencias
- **Foundational:** OWASP Top Ten Web Application Security Risks — https://owasp.org/www-project-top-ten/
- **Foundational:** OWASP Top 10 2021 Introduction — https://owasp.org/Top10/2021/A00_2021_Introduction/
- **Foundational:** OWASP Top 10 related cheat sheets — https://cheatsheetseries.owasp.org/IndexTopTen.html
