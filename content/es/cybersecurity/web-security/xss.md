---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - xss
sources: []
---

# Cross-Site Scripting (XSS)

## Definición
El XSS ocurre cuando un input controlado por el atacante se renderiza en un contexto de navegador de una forma que hace que el navegador lo interprete como código ejecutable en vez de datos inertes.

## Por qué importa
El XSS no es solo "JavaScript que tira un alert". Convierte un origen confiable en un entorno de ejecución bajo influencia del atacante.

Eso puede llevar a:
- abuso de sesión
- acción-en-nombre-del-usuario
- phishing dentro de un origen confiable
- robo de datos disponibles para el navegador
- escalada de privilegios cuando admins o staff ven contenido controlado por el atacante

El XSS también enseña la misma lección profunda que SQLi: el contexto determina la seguridad. El escaping que es correcto en un contexto de parser puede fallar por completo en otro.

## Cómo funciona
La forma central es:

1. el input controlado por el atacante entra a la app
2. ese input llega a un sink de navegador
3. la aplicación no logra codificar o sanear correctamente para ese sink/contexto exacto

Contextos típicos:
- body HTML
- atributo entre comillas
- atributo sin comillas
- atributo de URL
- bloque de script
- event handler
- sink del DOM del lado del cliente
- HTML generado por template

### Sabores principales

#### XSS reflejado
El input viene en la request y se refleja inmediatamente en la response.

#### XSS almacenado
El input se guarda y luego se renderiza a otros usuarios.

#### XSS basado en DOM
El flujo vulnerable ocurre enteramente en el código del lado del navegador, a menudo a través de sinks de JavaScript como `innerHTML`.

## Técnicas / patrones
Los atacantes normalmente miran:

- campos de búsqueda
- mensajes de error reflejados
- campos de perfil
- comentarios / chat / tickets
- editores de markdown o rich text
- código de frontend que lee de `location`, `hash`, `postMessage` o storage
- sinks de DOM inseguros
- patrones de renderizado basados en URL
- caminos de subida/visualización de HTML o SVG controlado por el usuario

Mentalidad de testeo útil:
- identificá la fuente
- identificá el sink
- identificá el contexto
- testeá patrones de breakout específicos del contexto

## Variantes y bypasses

### Contexto de body HTML
Vectores comunes:
- inyección de tags
- event handlers en tags como `img`, `svg`, `details`
- variaciones de tag tolerantes al parser

### Contexto de atributo
Hay que salir del atributo o influir en su semántica.

Ejemplos de áreas de riesgo:
- `value=""`
- `title=""`
- `src=""`
- `href=""`

### Contexto de URL
El peligro a menudo viene de:
- URLs `javascript:`
- URLs `data:`
- debilidades de validación de esquema
- construcción de URL confiable-pero-insegura

### Contexto de bloque de script
El atacante intenta salir del contexto de string-JS / sintaxis-JS en vez del contexto HTML.

### Sinks de DOM XSS
Sinks de alto valor incluyen:
- `innerHTML`
- `outerHTML`
- `insertAdjacentHTML`
- `document.write`
- escape hatches inseguros de frameworks

### Problemas específicos de frameworks
Incluso los frameworks que escapan por defecto a menudo exponen escape hatches peligrosos:
- `dangerouslySetInnerHTML` de React
- `v-html` de Vue
- APIs de bypass-de-trust de Angular
- templates de servidor con interpolación sin escapar
- pipelines de markdown/render que permiten HTML crudo

### Bypasses de sanitizers
Los sanitizers son importantes, pero no mágicos.
Los bypasses reales a menudo involucran:
- diferencias de parser
- mutation XSS
- comportamiento específico de SVG
- errores de manejo de URL
- bypasses recién descubiertos en librerías de sanitizer

### Interacciones con CSP
La CSP puede reducir la explotabilidad, pero:
- una CSP débil a menudo es decorativa
- los scripts en whitelist igual pueden crear bypasses basados-en-gadgets
- la fuga de nonce o `unsafe-inline` debilitan significativamente el control

## Impacto
El impacto depende de lo que el navegador de la víctima pueda hacer en ese origen.

Impacto típico:
- robar o usar el contexto de sesión
- realizar acciones autenticadas
- acceder a tokens CSRF o al estado de la app
- escalar a través de XSS almacenado/de-vista-de-admin
- lanzar phishing muy creíble dentro del sitio real
- pivotar a interfaces internas alcanzables desde el navegador de la víctima en algunos entornos

Incluso si las cookies son `HttpOnly`, el XSS igual puede realizar acciones directamente a través de requests same-origin.

## Detección y defensa
Ordenado por efectividad:

1. **Encoding de salida consciente del contexto**
   Codificá para el sink exacto, no genéricamente.

2. **Evitá las APIs de renderizado peligrosas**
   Usá los defaults seguros del framework y evitá los escape hatches inseguros salvo que sea absolutamente necesario.

3. **Saneamiento de HTML donde se requiere contenido rico**
   Usá un sanitizer mantenido y mantenelo actualizado.

4. **CSP como defensa en profundidad**
   Una buena CSP reduce la explotabilidad, pero no reemplaza el manejo correcto.

5. **Endurecimiento de cookies**
   Los settings `HttpOnly`, `Secure` y un `SameSite` apropiado reducen algún daño.

6. **Trusted Types donde aplique**
   Especialmente útil para reducir la exposición a DOM XSS.

7. **Revisá los flujos fuente → sink**
   Especialmente en código de frontend y librerías de componentes.

8. **Monitoreo**
   Vigilá:
   - comportamiento de renderizado sospechoso
   - input con forma de payload repetido
   - errores inusuales del lado del cliente
   - contenido de usuario anómalo de cara al admin

## Ejemplos prácticos
- XSS reflejado de término-de-búsqueda en una página de resultados
- XSS almacenado en un ticket de soporte visto por el staff
- DOM XSS vía `location.hash` insertado en `innerHTML`
- renderizado de markdown inseguro que permite contenido adyacente-a-HTML/script
- subida de SVG que se vuelve ejecutable cuando se sirve inline

## Notas relacionadas
- [[http-headers|Headers HTTP]]
- [[session-management|Gestión de sesiones]]
- [[csrf|CSRF]]
- [[cybersecurity/security-playbooks/inspect-file-upload-surface|Inspeccionar la superficie de subida de archivos]]

### Notas atómicas futuras sugeridas
- [[content-security-policy|Content Security Policy]]
- [[mutation-xss|Mutation XSS]]
- [[dom-xss-sinks|Sinks de DOM XSS]]

## Referencias
- **Foundational:** OWASP Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Cross-site scripting topic — https://portswigger.net/web-security/cross-site-scripting
- **Research / Deep Dive:** PortSwigger XSS cheat sheet — https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
