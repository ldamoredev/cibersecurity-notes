# Open Redirect

## Definición

Open redirect ocurre cuando una aplicación redirige a los usuarios hacia destinos controlados por el atacante basándose en input no confiable, sin validación estricta del destino.

## Por qué importa

Los open redirects frecuentemente parecen de bajo impacto solos, pero se vuelven poderosos cuando se encadenan con phishing, flujos de OAuth, redirects de login, filtración de tokens, bypasses de CSP, o allowlists de dominios de confianza. El dominio de confianza realiza la redirección, por lo que los usuarios y sistemas pueden tratar el destino como legítimo.

## Cómo funciona

Open redirect tiene **3 partes**:

1. **Parámetro de redirección.** `next`, `url`, `redirect`, `returnTo`, `continue` u otros similares.
2. **Comportamiento de redirección del servidor/cliente.** HTTP `Location`, asignación de JavaScript, meta refresh, o ruteo del framework.
3. **Validación débil.** La aplicación acepta destinos arbitrarios o bypasseables.

Ejemplo con forma de payload:

```
GET /login?next=https://evil.example HTTP/1.1
Host: app.example.test
```

El bug no es redirigir después del login. El bug es dejar que el input no confiable elija un destino fuera del límite de confianza permitido.

## Técnicas / patrones

Los atacantes testean:

- parámetros de redirección en flujos de login, logout, SSO, restablecimiento de contraseña e invitación
- URLs absolutas, URLs relativas al protocolo y URLs codificadas
- confusión de ruta: `//evil.example`, `/\evil.example`, `%2f%2fevil.example`
- trucos de userinfo: `https://app.example.test@evil.example`
- confusión de subdominio y sufijo
- cadenas de redirect URI y callback de OAuth

## Variantes y bypasses

Los open redirects aparecen en **5 contextos**.

### 1. Redirect de retorno al login

La app redirige después de la autenticación hacia un destino arbitrario.

### 2. Cadena de redirect en OAuth

Un endpoint de redirect de confianza se usa para bypass de restricciones de redirect URI de OAuth.

### 3. Redirect del lado del cliente

JavaScript lee un parámetro de URL y navega el navegador.

### 4. Bypass de validación de dominio

Trucos de sufijo, subcadena, userinfo, codificación o esquema bypass las allowlists.

### 5. Redirect de filtración de tokens

Los tokens o códigos en URLs se reenvían hacia destinos controlados por el atacante.

## Impacto

Ordenado aproximadamente por severidad:

- **Cadena de compromiso de OAuth o SSO.** Los redirects bypass las reglas estrictas de callback.
- **Phishing de credenciales.** Los dominios de confianza dan credibilidad a los links de phishing.
- **Filtración de tokens o códigos.** Los fragmentos de URL sensibles o parámetros de query se filtran.
- **Cadenas de bypass de control de acceso.** El comportamiento de redirección interactúa con allowlists o filtros de SSRF.
- **Abuso de marca.** Los links de confianza llevan a los usuarios a contenido malicioso.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar IDs de destino del lado del servidor en lugar de URLs raw.**
   Mapear `next=dashboard` a una ruta interna conocida en lugar de aceptar URLs arbitrarias.

2.
**Permitir solo rutas relativas cuando sea posible.**
   La mayoría de los redirects post-login no necesitan destinos externos.

3.
**Validar los destinos con parsers de URL y allowlists exactas.**
   Comparar el esquema canónico, host y ruta; evitar las verificaciones de subcadena.

4.
**Mantener las redirect URIs de OAuth exactas y evitar endpoints de cadenas de redirect.**
   Los clientes OAuth no deberían permitir open redirectors de confianza como rutas de callback.

5.
**No poner secretos en URLs.**
   Esto reduce el daño si los redirects o referrers se comportan mal.

### Qué no funciona como defensa primaria

- **Allowlists de subcadena.** `trusted.com.evil.example` no es de confianza.
- **Verificar solo si la URL empieza con.** La codificación y el userinfo pueden bypass las verificaciones naïve.
- **Solo páginas de confirmación del usuario.** Reducen el phishing pero no arreglan la lógica de redirect insegura.
- **Asumir que los redirectores del mismo dominio son inofensivos.** Las cadenas importan.

## Labs prácticos

Usar apps propias o labs.

### Encontrar parámetros de redirección

```
rg -n "redirect|returnTo|next|continue|callback|url" src routes public
```

Revisar dónde se aceptan destinos controlados por el usuario.

### Testear destino absoluto

```
curl -i 'https://app.example.test/login?next=https://example.org'
```

Verificar si `Location` apunta fuera del dominio previsto.

### Testear confusión del parser

```
curl -i 'https://app.example.test/login?next=//example.org'
curl -i 'https://app.example.test/login?next=https://app.example.test@example.org'
```

Usar un destino controlado en labs.

## Ejemplos prácticos

- El login acepta `next=https://evil.example`.
- El restablecimiento de contraseña redirige a una URL controlada por el usuario después de completarse.
- La allowlist de callback de OAuth incluye una ruta que es en sí misma un open redirect.
- JavaScript redirige basado en `location.hash`.
- Un link de soporte usa un redirector que puede apuntar a dominios arbitrarios.

## Notas relacionadas

- [[oauth-security]]
- [[auth-flaws]]
- [[session-management]]
- [[ssrf]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

## Referencias

- **Fundamental:** OWASP Unvalidated Redirects and Forwards Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
