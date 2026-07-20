# Recon

## Definición

El recon es la fase de un engagement de seguridad ofensiva en la que el operador recopila información sobre el objetivo antes de testear vulnerabilidades o ejecutar exploits. Abarca el [[passive-recon|Passive Recon]] (sin contacto directo), el [[active-recon|Active Recon]] (contacto directo, descubrimiento de assets) y el [[public-asset-discovery|Public Asset Discovery]].

## Por qué importa

Un engagement que salta directo al testing pierde scope, no entiende la arquitectura del objetivo y testea los servicios equivocados. El recon bien hecho produce un modelo del objetivo que guía todo lo que viene después: qué assets entran en scope, qué stack tecnológico llevan, qué puntos de entrada existen, qué comportamiento está dentro del presupuesto de riesgo del engagement.

El recon también es donde más frecuentemente se cometen errores éticos y legales: testear assets fuera de scope, rebotar contra infraestructura de terceros o generar tráfico que el programa de bug bounty prohíbe explícitamente. El primer resultado de un buen recon es saber lo que *no* vas a testear.

## Cómo funciona

El recon tiene **3 fases** en orden:

1. **Passive recon.** Recopilar pistas públicas sin contacto directo con el objetivo: registros DNS, certificate transparency, resultados de búsqueda, repositorios, ofertas de trabajo, docs, archivos y context de brechas.

2. **Public asset discovery.** Convertir las pistas en un inventario de assets en scope: dominios, subdominios, IPs, ASNs, aplicaciones, APIs y superficies de terceros.

3. **Active recon.** Contacto directo controlado y en scope: descubrimiento de hosts y puertos, fingerprinting de servicios, tech stack fingerprinting y validación de endpoints.

El recon produce **3 outputs** antes de que comience el testing:

1. **Lista de assets validados.** Qué está en scope, qué está fuera, qué es territorio de terceros.
2. **Hipótesis de tecnología.** Qué stack, frameworks y vendors probablemente corre el objetivo.
3. **Superficie de ataque inicial.** Puntos de entrada probables y áreas de interés para el testing.

Un ejemplo trabajado, de pista a superficie:

```
Passive clue:
  job listing mentions "Node.js microservices on AWS ECS + an API gateway"

Public asset clue:
  crt.sh shows *.api.example.test with cert issued 6 weeks ago

Active clue:
  api.example.test:443 returns HTTP 200, Server: nginx/1.24, X-Powered-By: Express

Recon output:
  Node/Express API behind nginx; ECS deployment; likely REST endpoints
  Hypothesis: JWT auth, rate limiting, possible SSRF surface in outbound calls
```

El output del recon informa el plan de testing, no lo reemplaza.

## Técnicas / patrones

- **Passive-first.** Siempre completar el passive recon antes del active, así el active no toca assets fuera de scope.
- **Validación de scope en cada paso.** Un asset descubierto en passive recon no está en scope hasta que se valide la pertenencia al objetivo.
- **Documentar las fuentes.** Cada asset en el inventario debería tener una fuente de descubrimiento (CT log, búsqueda, DNS brute, etc.).
- **Handoff a testing.** El [[recon-to-testing-handoff|Recon-to-Testing Handoff]] es el documento que separa la fase de recon de la fase de testing; sin él, el testing empieza sin contexto compartido.

## Variantes y bypasses

### Recon externo

El punto de partida por defecto para engagements de bug bounty y pentests externos. Empieza sin credenciales ni acceso interno.

### Recon con scope estrecho

Algunos engagements entregan un dominio o IP específicos. El passive recon todavía se aplica, pero el public asset discovery empieza desde el asset conocido.

### Recon con acceso parcial

Algunos bug bounty programs o assessments entregan credenciales de usuario básico. El passive y active recon externo se complementa con reconocimiento autenticado interno.

### Recon continuo

En programas de bug bounty maduros o en attack surface management defensivo, el recon se automatiza en pipelines continuos que alertan en assets nuevos.

## Impacto

- **Descubrimiento de scope real.** Los engagements sin recon frecuentemente pierden la mitad de la superficie de ataque.
- **Prevención de testing fuera de scope.** El recon define los límites antes de que empiece el contacto activo.
- **Eficiencia de testing.** El testing dirigido por un buen modelo de recon produce más hallazgos en menos tiempo.
- **Calidad del reporte.** La sección de superficie de ataque del reporte final es el output directo de la fase de recon.

## Detección y defensa

Desde la perspectiva del defensor, el recon es en su mayoría pasivo e invisible. Las defensas están en el ataque surface management continuo y la reducción de información pública:

1. **Auditá tu propia información pública.**
   Los registros DNS, certificate logs, repos y docs revelan assets que los defensores pueden no saber que existen.

2. **Inventario de assets continuo.**
   El equipo de seguridad debería tener un modelo de assets más completo que el que puede construir un atacante con recon pasivo.

3. **Minimizá artefactos de información útil.**
   No por seguridad a través de la oscuridad — por reducción de superficie: dominios obsoletos, DNS viejos, source maps públicos, docs con patrones de naming internos.

4. **El active recon sí es detectable.**
   Los scans de puertos, HTTP probing y DNS brute tienen firmas. Los defensores con honeypots, IDS y alertas de anomalía detectan activos bien.

## Notas relacionadas

- [[passive-recon|Passive Recon]]
- [[active-recon|Active Recon]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[company-mapping|Company Mapping]]
- [[subdomain-enumeration|Subdomain Enumeration]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[tech-stack-fingerprinting|Tech Stack Fingerprinting]]
- [[recon-to-testing-handoff|Recon-to-Testing Handoff]]
- [[scope-validation|Scope Validation]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OSINT Framework — https://osintframework.com/
