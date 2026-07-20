# Reverse Proxy Misconfig Checklist

## Objetivo

Identificar si el comportamiento de proxy y backend crea bugs de trust boundary, confusión de parser, abuso de headers o exposición de routing no intencional.

## Supuestos

- uno o más reverse proxies, CDNs o load balancers están delante de la app
- headers pueden agregarse, eliminarse o confiarse de forma inconsistente
- diferencias de parsing entre proxy/backend pueden crear issues de seguridad

## Prerrequisitos

- visibilidad de requests y responses
- capacidad de enviar headers crafted y observar comportamiento
- comprensión aproximada de la cadena de request

## Pasos de recon

1. Identificá todos los hops de request si es posible.
2. Compará comportamiento visible externamente con expectativas del backend.
3. Registrá headers agregados por proxy y comportamientos de ruta.

## Pasos de exploit / testing

1. Testeá confianza en headers: `X-Forwarded-For`, `X-Real-IP`, headers relacionados con host.
2. Observá si también existe acceso directo al backend.
3. Verificá diferencias de routing y normalización de path.
4. Probá ambigüedad de parsing de requests cuando corresponda.
5. Inspeccioná exposición de health, debug o virtual hosts alternativos.

## Señales de validación

- headers de forwarding controlados por atacante influyen en decisiones de seguridad
- proxy y backend discrepan sobre interpretación de requests
- backends son alcanzables directamente fuera del front door previsto
- paths ocultos o comportamientos de routing aparecen por quirks del proxy

## Mitigación

- definir un límite claro de proxy confiable
- normalizar o rechazar requests ambiguas
- restringir exposición directa del backend
- centralizar y revisar policy de confianza en forwarding/headers
- patchear y testear la cadena completa de forma consistente

## Logging / detección

- valores inesperados de forwarding headers
- patrones de request malformados
- tráfico bypasseando entrypoints esperados
- inconsistencias entre edge logs y backend logs

## Notas relacionadas

- [[reverse-proxies|Reverse proxies]]
- [[request-smuggling|Request Smuggling]]
- [[client-ip-trust|Confianza en IP de cliente]]
- [[load-balancers|Load balancers]]

## Referencias

- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** PortSwigger Research — https://portswigger.net/research
- **Fundamental:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
