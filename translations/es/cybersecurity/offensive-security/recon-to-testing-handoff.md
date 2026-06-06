# Recon-to-Testing Handoff

## Definición

El recon-to-testing handoff es el documento o estado de conocimiento compartido que transiciona la fase de recon de un engagement a la fase de testing activo. Define qué assets están confirmados en scope, qué hipótesis técnicas generó el recon, qué áreas se priorizan primero y qué restricciones de engagement aplican.

## Por qué importa

Sin un handoff explícito, el testing empieza con contexto implícito que vive solo en la cabeza del operador de recon. En engagements en equipo, esto produce testeo duplicado, activos fuera de scope tocados por error o pérdida de hipótesis de recon de alto valor que no sobreviven a la transición.

Incluso en engagements en solitario, el handoff sirve como un punto de control: ¿está el modelo del objetivo suficientemente completo como para que el testing sea eficiente? ¿Están documentadas las restricciones de scope? ¿Se validó el ownership de los assets? Comprometerse a hacer el handoff explícito convierte el recon en un output utilizable, no solo en notas personales.

El handoff también establece el límite entre observación y interacción activa. Los activos que no pasaron por validación de scope no entran en el inventario de testing. Los activos de terceros — vendors, CDNs, proveedores de identidad, herramientas de soporte — se anotan como fuera de scope con justificación.

## Cómo funciona

Un handoff de recon tiene **5 secciones**:

1. **Inventario de assets validados.** Lista de dominios, subdominios, IPs y servicios confirmados como pertenecientes al objetivo y en scope.
2. **Hipótesis de stack tecnológico.** Qué tecnologías, frameworks, vendors y patrones de deployment infirió el recon.
3. **Mapa de superficie de ataque.** Qué puntos de entrada probablemente son de alto valor: endpoints autenticados, APIs, uploads, callbacks, headers de confianza, flujos de usuario que cambian estado.
4. **Activos fuera de scope anotados.** CDNs, vendors, sistemas de soporte, terceros y cualquier activo que apareció en recon pero no entra en testing.
5. **Restricciones y presupuesto del engagement.** Rate limits, ventanas de testing, activos excluidos por el programa, y cualquier instrucción especial del scope.

Un ejemplo de formato de inventario mínimo:

```
asset                         | in-scope | tech hypothesis        | priority
------------------------------|----------|------------------------|----------
app.example.test              | yes      | React SPA + Node API   | high
api.example.test/v2/*         | yes      | REST, JWT auth         | high
staging.example.test          | yes      | same stack, less WAF   | high
docs.example.test             | yes      | Docusaurus, static     | low
status.example.test           | no       | third-party (Atlassian)| skip
cdn.example-assets.net        | no       | CDN origin             | skip
support.example.test          | no       | Zendesk                | skip
```

El handoff no tiene que ser un documento formal en todos los contextos. En un bug bounty en solitario, puede ser una tabla en el bloc de notas del engagement. Lo que importa es que exista y que sea consultado antes de que empiece el testing.

## Técnicas / patrones

- **No mover assets del recon al testing sin validación de scope.** Cada asset necesita una fuente de descubrimiento y una confirmación de ownership antes de entrar al inventario de testing.
- **Anotar por qué algo está fuera de scope.** "CDN — no es infraestructura del objetivo" es más útil que solo "skip". Protege de testear esos assets por error más adelante.
- **Documentar las hipótesis de tech stack con su confianza.** "Express API (visto en X-Powered-By)" es más útil que solo "Node". La fuente de la hipótesis importa.
- **Ordenar el inventario por prioridad.** El testing empieza por los assets más probables de tener hallazgos de alto impacto, no en orden alfabético.
- **El handoff es un input, no un plan de testing.** Define qué testear, no cómo. El operador de testing usa el inventario para derivar el plan de testing específico.

## Variantes y bypasses

### Handoff en equipo

En un engagement con múltiples operadores (recon + testing separados), el handoff es un documento compartido explícito que se revisa en una llamada de transición. Incluye sección de preguntas abiertas de recon que el testing puede resolver.

### Handoff individual (bug bounty / solitario)

El operador hace recon y testing. El handoff es un estado de conocimiento self-documentado — una tabla o nota que el operador consulta antes de cambiar el modo de "observar" a "interactuar".

### Handoff incremental

En assessments largos, el handoff ocurre en etapas: primero los assets de mayor prioridad, luego los secundarios. Permite empezar el testing de alta prioridad mientras el recon continúa en assets de menor prioridad.

### Handoff con scope abierto

Algunos engagements tienen scope muy amplio ("cualquier cosa de la empresa"). El handoff en este caso incluye una priorización explícita porque testear todo no es posible — se define qué entrar primero y por qué.

## Impacto

- **Prevención de testing fuera de scope.** El handoff es el mecanismo principal para evitar tocar activos de terceros o fuera de programa por error.
- **Eficiencia de testing.** Un inventario bien priorizado evita gastar tiempo en activos de bajo valor.
- **Calidad del reporte.** La sección de scope y superficie de ataque del reporte final viene del handoff, no del testing en sí.
- **Cobertura del engagement.** El handoff hace visibles los gaps — activos descubiertos pero no priorizados que se pueden revisar en scope reviews.

## Labs prácticos

### Construir un template de handoff mínimo

```
# Recon-to-Testing Handoff
## Engagement
  target: example.test
  scope: *.example.test, api.example.test/v2
  out-of-scope: third-party services, CDN origins, support tooling

## Asset inventory
  [table: asset | in-scope | tech hypothesis | source | priority]

## Key hypotheses
  [list of testable hypotheses derived from recon]

## Open questions
  [list of things recon couldn't confirm that testing should check]

## Constraints
  [rate limits, windows, excluded assets, special instructions]
```

### Checklist de validación antes de empezar el testing

```
[ ] Todos los activos en el inventario tienen fuente de descubrimiento confirmada
[ ] El ownership de cada activo está validado (no solo en scope del programa)
[ ] Los activos de terceros están anotados y excluidos
[ ] Las hipótesis de tech stack tienen fuente de evidencia
[ ] El inventario está ordenado por prioridad
[ ] Las restricciones del engagement están documentadas
[ ] Los activos de staging / dev están marcados y aislados del scope de producción si corresponde
```

## Notas relacionadas

- [[recon|Recon]]
- [[passive-recon|Passive Recon]]
- [[active-recon|Active Recon]]
- [[scope-validation|Scope Validation]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[tech-stack-fingerprinting|Tech Stack Fingerprinting]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP Testing Guide v4 — Information Gathering — https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/01-Information_Gathering/
