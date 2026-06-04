---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - csrf
sources: []
---

# Cross-Site Request Forgery (CSRF)

## Definición
El CSRF ocurre cuando se induce al navegador de una víctima a enviar una request autenticada que la aplicación objetivo acepta como legítima, aunque el usuario no haya pretendido la acción.

## Por qué importa
El CSRF es uno de los ejemplos más claros de cómo el comportamiento del navegador en sí puede volverse parte de la vulnerabilidad. El navegador del usuario carga cookies, estado de sesión y otra autoridad ambiental automáticamente, lo que significa que se puede engañar al navegador para que actúe como un diputado involuntario.

El CSRF sigue siendo importante porque los equipos a menudo malentienden:
- qué credenciales envía el navegador automáticamente
- qué resuelve realmente SameSite
- la diferencia entre CORS y CSRF
- por qué las rutas que cambian estado necesitan validación de intención

## Cómo funciona
El mecanismo es:

1. la víctima está autenticada en la aplicación objetivo
2. el navegador incluye automáticamente las credenciales en una request
3. el atacante hace que el navegador de la víctima envíe una request al objetivo
4. la aplicación acepta la request sin validar suficientemente la intención del usuario

El atacante a menudo no necesita leer la response.
Solo necesita que la acción que cambia estado tenga éxito.

## Técnicas / patrones
Los atacantes típicamente buscan:
- endpoints POST que cambian estado
- endpoints GET que incorrectamente cambian estado
- flujos de auth basados en cookies
- tokens anti-CSRF faltantes
- validación de origen débil o ausente
- endpoints que aceptan envíos de formulario simples
- lugares donde los equipos asumen que CORS previene CSRF

Métodos de entrega comunes:
- formularios ocultos
- formularios auto-submit
- requests disparadas por imagen o script donde sea relevante
- flujos de navegación / links controlados por el navegador
- sitios maliciosos visitados por una víctima ya logueada

## Variantes y bypasses

### CSRF clásico basado en formulario
El objetivo acepta un envío de formulario normal del navegador y las cookies de la víctima se incluyen.

### CSRF basado en GET
La aplicación cambia estado en GET, haciendo la explotación aún más fácil.

### Bypass de token / validación débil
El anti-CSRF existe pero está:
- faltante en algunos endpoints
- no atado correctamente a la sesión/usuario
- aceptado a través de contextos en los que no debería confiar
- filtrado o predecible de alguna forma

### Malentendidos sobre SameSite
`SameSite` ayuda, pero:
- los defaults varían por era de navegador y comportamiento de la app
- algunos flujos de app requieren excepciones
- los desarrolladores a veces sobreestiman lo que bloquea
- las distinciones same-site vs same-origin importan

### Malentendidos sobre JSON/API
Los equipos a veces asumen "los endpoints de API no son CSRF-eables".
Eso depende de:
- el transporte de credenciales
- los content types aceptados
- el comportamiento de preflight
- si el navegador puede enviar la request como un formulario simple o un camino equivalente

### CSRF de login / logout / transición-de-estado
Aunque "cambiar email" esté protegido, flujos como:
- login
- logout
- binding de cuenta
- toggles de estado
igual pueden tener un impacto de CSRF significativo.

## Impacto
El impacto depende de lo que pueda hacer la víctima autenticada.

Impacto típico:
- cambiar la configuración de la cuenta
- iniciar acciones sensibles
- atar estado controlado por el atacante a la cuenta de la víctima
- borrar o modificar recursos
- abusar de roles privilegiados de la víctima (CSRF de admin/staff)

El CSRF a menudo se vuelve mucho más serio cuando:
- los admins pueden realizar acciones de alto impacto
- no hay re-autenticación para operaciones sensibles
- la acción es fácil de disparar y difícil de detectar

## Detección y defensa
Ordenado por efectividad:

1. **Tokens anti-CSRF donde se necesiten**
   Los tokens deberían validarse del lado del servidor y atarse apropiadamente al contexto de usuario/sesión/request.

2. **Usá una estrategia de defensa correcta y consciente del navegador**
   Entendé cuándo se envían las cookies automáticamente y qué hace SameSite en el flujo real de la app.

3. **Validación de Origin / Referer donde sea apropiado**
   Útil como defensa en capas cuando se implementa con cuidado.

4. **No uses GET para operaciones que cambian estado**
   Los métodos seguros deberían quedar seguros.

5. **Re-auth o confirmación más fuerte para acciones sensibles**
   Especialmente para flujos de admin o de cambio-de-cuenta de alto impacto.

6. **No confundas CORS con protección CSRF**
   CORS controla los permisos de lectura del navegador, no la intención del usuario.

7. **Monitoreo**
   Vigilá:
   - requests que cambian estado sospechosas sin los artefactos anti-CSRF esperados
   - patrones de origen inusuales
   - acciones sensibles-de-admin desde flujos de navegación inesperados

## Ejemplos prácticos
- un formulario oculto auto-submit para cambiar el email de una cuenta
- un endpoint GET que cambia estado disparado por visitar un link
- una acción de admin realizada porque la víctima visita una página controlada por el atacante mientras está logueada
- un endpoint JSON asumido seguro, pero los patrones de request entregables-por-navegador igual tienen éxito

## Notas relacionadas
- [[cookies-and-sessions|Cookies y sesiones]]
- [[session-management|Gestión de sesiones]]
- [[cors-misconfiguration|Mala configuración de CORS]]
- [[cybersecurity/security-playbooks/inspect-session-handling|Inspeccionar el manejo de sesiones]]

### Notas atómicas futuras sugeridas
- [[samesite-in-practice|SameSite en la práctica]]
- [[origin-vs-referer-validation|Validación de Origin vs Referer]]

## Referencias
- **Foundational:** OWASP Cross-Site Request Forgery Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf
