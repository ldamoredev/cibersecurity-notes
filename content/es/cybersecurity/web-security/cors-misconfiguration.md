# CORS Misconfiguration

## Definición

La mala configuración de CORS ocurre cuando la política de cross-origin resource sharing de un servidor es demasiado permisiva, está incorrectamente implementada, o se malentiende como sustituto de una autorización real del lado del servidor.

## Por qué importa

CORS es ampliamente malentendido. Los equipos frecuentemente lo tratan como si fuera un mecanismo de control de acceso, cuando en realidad es una política que el navegador aplica sobre si una respuesta puede ser leída por un origen solicitante.

Esta confusión lleva a bugs donde:
- se reflejan orígenes arbitrarios
- las credenciales se permiten demasiado ampliamente
- la lógica de orígenes de confianza es débil
- los desarrolladores asumen que CORS bloquea ataques que en realidad no bloquea

## Cómo funciona

El mecanismo es:
1. el navegador envía un header `Origin`
2. el servidor responde con headers `Access-Control-*`
3. el navegador decide si el origen que hace la llamada puede leer la respuesta

El error del lado del servidor suele ser uno de estos:
- reflejar orígenes arbitrarios
- usar patrones de confianza demasiado amplios
- permitir credenciales con manejo inseguro del origen
- asumir que CORS equivale a autorización

La forma peligrosa — origen arbitrario reflejado con credenciales permitidas — se ve así:

```
GET /api/me HTTP/1.1
Host: api.example.com
Origin: https://attacker.example
Cookie: session=...

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://attacker.example
Access-Control-Allow-Credentials: true

{"email":"victim@example.com","balance":12345}
```

Una página en `attacker.example` puede ahora llamar `fetch("https://api.example.com/api/me", {credentials: "include"})` y leer el cuerpo de la respuesta de la víctima. El navegador no impuso nada, porque el servidor le dijo que el origen del atacante es de confianza.

El mismo antipatrón aparece con regexes descuidadas — por ejemplo, confiar en cualquier origen que coincida con `*.example.com` cuando un atacante puede registrar `example.com.attacker.com` o tomar control de un subdominio abandonado.

## Técnicas / patrones

Los atacantes generalmente testean:
- comportamiento del `Origin` reflejado
- confianza de origen basada en wildcards o patrones
- requests con credenciales
- diferencias en el preflight
- variaciones de esquema / subdominio
- si los equipos confían en CORS donde debería existir autenticación real

## Variantes y bypasses

### Origen reflejado

El servidor refleja cualquier origen que envíe el cliente.

### CORS con credenciales inseguro

Un patrón peligroso donde se permiten credenciales y la confianza en el origen es demasiado amplia.

### Confianza excesiva en subdominios

La política confía en un namespace que el atacante puede influenciar.

### Inconsistencia preflight / ruta

Una ruta o método es más estricto que otro.

### Confusión CORS vs CSRF

Los equipos creen que CORS bloquea a los atacantes cuando el CSRF puede seguir teniendo éxito.

### Malentendidos con clientes no-navegador

CORS es una política del navegador. Los clientes que no son navegadores no le prestan atención.

## Impacto

Impacto típico:
- un origen controlado por el atacante puede leer respuestas sensibles de la API
- los requests del navegador con credenciales se vuelven legibles cross-origin
- las suposiciones de confianza en el origen amplían la exposición de datos
- los administradores o víctimas con sesión iniciada se convierten en fuentes útiles de datos cross-origin

## Detección y defensa

Ordenado por efectividad:

1.
**Tratar CORS como política del navegador, no como autorización**
   CORS controla si el navegador permite que un script lea una respuesta cross-origin. No autentica ni autoriza al llamante. La autorización real debe seguir viviendo en el servidor. Si el argumento de defensa de un endpoint se reduce a "CORS no les dejará leerlo", el endpoint no está realmente protegido.

2.
**Enumerar explícitamente los orígenes de confianza**
   Comparar el header `Origin` contra una allowlist del lado del servidor de orígenes completos (esquema + host + puerto). No reflejar el `Origin` del request. No hacer match por `endsWith` ni por regex sin límites — eso generalmente permite subdominios controlados por el atacante o hosts similares.

3.
**Tener cuidado con el acceso cross-origin con credenciales**
   `Access-Control-Allow-Credentials: true` combinado con un origen permisivo es la combinación más peligrosa. Si se requieren credenciales, la allowlist debe ser exacta y pequeña. Lo ideal es que las APIs sensibles que toman cookies no sean accesibles cross-origin en absoluto.

4.
**Revisar juntos el comportamiento del preflight y el no-preflight**
   Muchos bugs vienen de inconsistencias — la respuesta al preflight es estricta, pero el handler del request real es permisivo (o viceversa). Testear tanto `OPTIONS` como el método real contra cada endpoint interesante.

5.
**Separar los recursos públicos de las APIs sensibles**
   Los assets estáticos sin credenciales pueden usar `Access-Control-Allow-Origin: *`. Cualquier cosa que lea una sesión, devuelva datos específicos del usuario, o acepte una llamada que cambie estado nunca debería compartir esa política.

6.
**No depender de CORS para prevenir CSRF**
   CORS controla las *lecturas* de respuestas cross-origin. Los navegadores pueden seguir *enviando* requests cross-origin que cambian estado (envíos de formularios, requests simples). El CSRF requiere su propia defensa — tokens, cookies SameSite, o verificaciones de origin/referer en las rutas que cambian estado.

7.
**Monitorear**
   Estar atento a: reflexión de `Origin` en respuestas de producción, `Access-Control-Allow-Credentials: true` combinado con un origen no allowlisteado, y orígenes inesperados apareciendo en endpoints sensibles. El escaneo activo con un CORS-fuzzer (CORStest, Corsy) detecta las formas más comunes.

## Ejemplos prácticos

- la API refleja un `Origin` arbitrario y permite la lectura del lado del navegador
- el patrón de subdominio de confianza amplio incluye orígenes que el atacante puede influenciar
- un endpoint sensible autenticado por cookie es legible desde un origen externo inesperado
- el equipo cree que CORS previene el CSRF, dejando vacíos de validación de intención en otro lado

## Notas relacionadas

- [[http-headers]]
- [[csrf]]
- [[cookies-and-sessions]]
- [[test-cors-behavior|Test CORS Behavior]]

## Referencias

- **Fundamental:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Investigación / Deep Dive:** PortSwigger, "Exploiting CORS misconfigurations for Bitcoins and bounties" — https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties
