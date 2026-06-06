# Content Security Policy

## Definición

Content Security Policy (CSP) es un control de seguridad del navegador que le indica al navegador qué fuentes y patrones de ejecución están permitidos para scripts, estilos, imágenes, frames, conexiones y otros tipos de recursos.

## Por qué importa

CSP es una defensa en profundidad para XSS e inyección de contenido, no un reemplazo para el encoding de output o los templates seguros. Una política fuerte puede reducir la explotabilidad cuando existe un bug de inyección, mientras que una política débil puede crear falsa confianza.

## Cómo funciona

CSP controla **5 decisiones del navegador**:

1. **Ejecución de scripts.** Qué scripts pueden cargarse o ejecutarse.
2. **Carga de recursos.** Qué orígenes pueden proveer imágenes, estilos, fuentes, media y frames.
3. **Conexiones de red.** A qué endpoints puede conectarse JavaScript.
4. **Embebido.** Quién puede enmarcar la página y qué puede enmarcar la página.
5. **Reportes.** Dónde se reportan las violaciones.

Ejemplo de header:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-random'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'
```

El bug no es la ausencia de CSP solamente. El bug es depender de CSP mientras se permiten fuentes inseguras o ejecución inline que derrota la política.

## Técnicas / patrones

Los atacantes testean:

- debilidades en `script-src`: `unsafe-inline`, wildcards, CDNs amplios, JSONP, orígenes de subida
- nonces faltantes o reutilizables
- omisiones de `object-src`, `base-uri` y `frame-ancestors`
- dominios de confianza bypasseables
- sinks de DOM XSS bajo restricciones de política
- políticas report-only confundidas con aplicación real

## Variantes y bypasses

Las fallas de CSP aparecen en **6 formas**.

### 1. Sin política

El navegador no recibe restricciones de ejecución significativas.

### 2. Política report-only

Las violaciones se reportan pero no se bloquean.

### 3. Ejecución inline insegura

`unsafe-inline`, hashes inseguros, o mal uso de nonces permite scripts inyectados.

### 4. Fuentes de confianza demasiado amplias

Wildcards o CDNs amplios permiten contenido controlado por el atacante desde orígenes de confianza.

### 5. Directivas estructurales faltantes

La ausencia de `base-uri`, `object-src` o `frame-ancestors` deja rutas de bypass abiertas.

### 6. Deriva de la política

La política se vuelve permisiva con el tiempo para soportar nuevas funcionalidades.

## Impacto

Ordenado aproximadamente por severidad:

- **Reducción o falla en la explotabilidad de XSS.** Un CSP fuerte puede bloquear la ejecución de scripts inyectados.
- **Control de clickjacking y framing.** `frame-ancestors` protege páginas sensibles.
- **Reducción de la exfiltración de datos.** `connect-src` limita adónde los scripts pueden enviar datos.
- **Contención de la inyección de contenido.** Las restricciones de recursos reducen la carga maliciosa.
- **Telemetría.** Los reportes revelan intentos de violación y vacíos en la política.

## Detección y defensa

Ordenado por efectividad:

1.
**Arreglar la inyección en la fuente primero.**
   El encoding de output, los templates seguros, la sanitización y la seguridad del DOM son las defensas primarias contra XSS.

2.
**Usar `script-src` basado en nonce o hash sin ejecución inline insegura.**
   Este es el control CSP más significativo para la reducción moderna de XSS.

3.
**Establecer defaults restrictivos y directivas estructurales.**
   `default-src 'self'`, `object-src 'none'`, `base-uri 'none'` y `frame-ancestors` reducen el espacio de bypass.

4.
**Mantener los orígenes de confianza acotados.**
   Cada origen permitido debería ser propio, necesario, e incapaz de hospedar scripts controlados por el atacante.

5.
**Desplegar con reportes y revisar las violaciones.**
   Report-only es útil durante el rollout, pero la protección final requiere aplicación real.

### Qué no funciona como defensa primaria

- **CSP en lugar de encoding de output.** CSP es una defensa en profundidad, no la corrección primaria de XSS.
- **`unsafe-inline`.** Generalmente derrota el propósito de las restricciones de scripts.
- **Wildcards amplios.** `*.cdn.example` puede incluir rutas controladas por el atacante.
- **Modo report-only.** Observa pero no bloquea.

## Labs prácticos

Usá apps propias.

### Inspeccionar la política

```
curl -I https://app.example.test/ | rg -i "content-security-policy"
```

Verificar si la política se aplica o es report-only.

### Revisar directivas riesgosas

```
curl -I https://app.example.test/ | rg -i "unsafe-inline|unsafe-eval|\\*|data:"
```

Cada fuente riesgosa debería tener una justificación.

### Testear la protección de frames

```
curl -I https://app.example.test/account | rg -i "frame-ancestors|x-frame-options"
```

Las páginas sensibles no deberían ser enmarcables ampliamente.

## Ejemplos prácticos

- Un sitio tiene XSS pero un CSP fuerte basado en nonce bloquea la ejecución del script.
- Una política usa `unsafe-inline`, haciéndola inefectiva contra muchos bugs de XSS.
- Una ruta de CDN de confianza permite JavaScript subido por el usuario.
- Falta `frame-ancestors` en la configuración de la cuenta.
- El CSP report-only registra violaciones pero no bloquea ataques.

## Notas relacionadas

- [[xss]]
- [[http-headers]]
- [[cors-misconfiguration]]
- [[open-redirect]]
- [[clickjacking]]

## Referencias

- **Fundamental:** MDN Content Security Policy — https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- **Testing / Lab:** PortSwigger CSP — https://portswigger.net/web-security/cross-site-scripting/content-security-policy
- **Fundamental:** OWASP Content Security Policy Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
