# Test Client IP Spoofing

## Objetivo

Determinar si la aplicación o componentes upstream confían en headers controlados por atacante al derivar la IP de cliente.

## Supuestos

- rate limits, logs, allowlists o controles admin pueden depender de la IP de cliente
- los proxies pueden forwardear información del cliente original
- la configuración de trust puede ser más amplia de lo previsto

## Prerrequisitos

- una ruta donde la IP de cliente afecte comportamiento o sea observable
- capacidad de hacer replay de requests con headers custom

## Pasos de recon

1. Encontrá endpoints o logs que expongan la IP de cliente percibida.
2. Identificá si la app está detrás de proxies o load balancers.
3. Revisá comportamiento default de trust-proxy del framework si se conoce.

## Pasos de exploit / testing

1. Enviá requests con `X-Forwarded-For` y headers relacionados crafted.
2. Observá logs, rate limits o comportamiento de allowlist.
3. Probá valores multi-hop de header para ver cómo se parsean.
4. Compará comportamiento a través del edge normal vs paths alternativos si existen.

## Señales de validación

- los logs registran IPs enviadas por atacante
- rate limits se resetean o aplican mal según valores spoofed
- restricciones basadas en IP se bypassean
- servicios distintos discrepan sobre la IP de cliente

## Mitigación

- confiar en forwarding headers solo desde proxies conocidos
- configurar explícitamente trust boundaries del framework
- derivar decisiones de seguridad desde una fuente consistente y revisada
- documentar y testear la cadena de headers esperada

## Logging / detección

- cadenas de forwarding imposibles o malformadas
- alta rotación de IP de cliente para la misma sesión/cuenta
- mismatches entre edge logs y app logs

## Notas relacionadas

- [[client-ip-trust|Confianza en IP de cliente]]
- [[reverse-proxies|Reverse proxies]]
- [[http-headers|HTTP headers]]
- [[api-rate-limiting|API Rate Limiting]]

## Referencias

- **Fundamental:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
