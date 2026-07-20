# Request Smuggling

## Definición

Request smuggling ocurre cuando dos componentes en la cadena de requests HTTP parsean el mismo request de forma diferente, permitiendo a un atacante desincronizar el entendimiento del front-end y el back-end sobre los límites de los mensajes.

## Por qué importa

Request smuggling es uno de los ejemplos más claros de la colisión entre redes y seguridad web. No es solo un bug de HTTP. Es un bug de límite de confianza entre intermediarios.

Importa porque el impacto puede incluir:
- secuestro de requests
- envenenamiento de caché
- efectos secundarios de autenticación
- confusión de rutas
- acceso a funcionalidades ocultas
- interferencia entre usuarios

## Cómo funciona

El mecanismo central es:
1. un atacante envía un request HTTP ambiguo
2. el front-end y el back-end no coinciden sobre dónde termina ese request
3. los bytes sobrantes se interpretan como un segundo request o como parte del stream de request de otra persona

La familia más famosa involucra desacuerdo entre:
- `Content-Length`
- `Transfer-Encoding`

Esqueleto mínimo CL.TE (el front-end usa `Content-Length`, el back-end usa `Transfer-Encoding: chunked`):

```
POST / HTTP/1.1
Host: vulnerable.example
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

El front-end reenvía el cuerpo completo porque confía en `Content-Length: 13`. El back-end se detiene en el terminador de chunk `0\r\n\r\n` y trata `SMUGGLED` como el inicio del próximo request en la conexión keep-alive — al que se agrega el request de la siguiente víctima.

La vulnerabilidad no son los headers en sí. Es el desacuerdo entre dos parsers que comparten una conexión.

## Técnicas / patrones

Los atacantes generalmente testean:
- ambigüedades estilo CL.TE / TE.CL
- mismatch entre parsers del front-end / back-end
- combinaciones inusuales de headers
- edge cases de chunked encoding
- envenenamiento de la queue de requests
- accesibilidad de rutas ocultas a través de desync
- interacción con capas de caché y autenticación

## Variantes y bypasses

### CL.TE

El front-end confía en `Content-Length`, el back-end confía en `Transfer-Encoding`.

### TE.CL

El front-end confía en `Transfer-Encoding`, el back-end confía en `Content-Length`.

### TE.TE / diferencias de parser

Ambos parsean transfer encoding, pero de forma diferente.

### Normalización de headers y quirks de edge

Diferentes componentes pueden reescribir o aceptar headers malformados de forma diferente.

### Efectos secundarios de caché y autenticación

El ataque puede manifestarse como envenenamiento, confusión de ruteo, o rarezas de autenticación en lugar de un efecto directo estilo RCE obvio.

## Impacto

Impacto típico:
- interferir con el request de otro usuario
- alcanzar endpoints ocultos
- bypass de las protecciones esperadas del front-end
- envenenar el comportamiento de la caché o de la queue de requests
- crear efectos secundarios confusos de autenticación y ruteo

## Detección y defensa

Ordenado por efectividad:

1.
**Normalizar o rechazar requests ambiguos**
   El edge debería canonicalizar los mensajes antes de reenviarlos: rechazar requests que contengan tanto `Content-Length` como `Transfer-Encoding`, rechazar chunked encoding malformado, y rechazar espacios en blanco no conformes o headers duplicados. Si el edge no puede arreglar el mensaje, fallar de forma cerrada.

2.
**Usar HTTP/2 de extremo a extremo donde sea posible**
   El framing de HTTP/2 está prefijado por longitud y elimina la ambigüedad textual que impulsa la mayor parte del desync. Las bajadas de HTTP/2 a HTTP/1.1 entre proxy y origen reintroducen la misma superficie de mismatch del parser — mantener el canal trasero en HTTP/2 si el front-end es HTTP/2.

3.
**Mantener alineado el comportamiento del front-end y el back-end**
   Usar la misma familia de servidor web, versión y configuración de parsing en ambos lados donde sea factible. La mayoría de los hallazgos de desync provienen de que un lado es más permisivo que el otro con el mismo input.

4.
**Entender la cadena completa**
   Mapear cada hop: CDN, WAF, load balancer, ingress controller, servidor de app. Cada hop es un parser. Documentar el orden para que el equipo sepa qué componente ve el request primero y cuál lo ve último.

5.
**Reducir la confianza oculta en intermediarios**
   No dejar que headers internos como `X-Forwarded-For`, `X-Original-URL`, o pistas de reescritura se conviertan en límites de confianza en los que el back-end depende sin re-validación. Los requests smuggled pueden llevar versiones falsificadas de estos.

6.
**Monitorear indicadores de desync**
   Estar atento a: requests atribuidos al usuario equivocado, clusters inesperados de `400 Bad Request` del back-end, entradas de caché con claves no coincidentes, y anomalías de reutilización de conexión en la capa keep-alive.

7.
**Testear la cadena desplegada exacta**
   Los parsers de lab no son los parsers desplegados. Ejecutar sondas de smuggling contra la cadena de staging que refleja la producción hop-por-hop. HTTP Request Smuggler de PortSwigger y las sondas estilo `smuggler.py` son las herramientas prácticas.

## Ejemplos prácticos

- el front-end y el back-end no coinciden sobre dónde termina el cuerpo del request
- el atacante envenena la queue para que el request de otro usuario se interprete de forma diferente
- una ruta de admin oculta se vuelve accesible porque el edge y el origen no coinciden sobre la estructura del request
- el comportamiento de la caché cambia por el ruteo desincronizado

## Notas relacionadas

- [[http-messages]]
- [[reverse-proxies]]
- [[caching-and-security]]
- [[reverse-proxy-misconfig-checklist|Reverse Proxy Misconfig Checklist]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- **Investigación / Deep Dive:** James Kettle, "HTTP/2: The Sequel is Always Worse" — https://portswigger.net/research/http2
