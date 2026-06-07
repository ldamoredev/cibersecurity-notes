# Investigate SSRF

## Objetivo

Determinar si funcionalidad de requests server-side puede usarse para alcanzar destinos internos, privilegiados o elegidos por el atacante.

## Supuestos

- la app fetchea URLs, archivos, previews, webhooks o contenido remoto
- la alcanzabilidad interna puede diferir de la alcanzabilidad pública
- redirects y representaciones alternativas pueden bypassear validación ingenua

## Prerrequisitos

- una feature que dispare requests server-side
- capacidad de observar responses, timing o efectos laterales
- conocimiento de posibles objetivos internos donde sea éticamente apropiado

## Pasos de recon

1. Identificá todas las features que aceptan URLs o recursos remotos.
2. Observá cómo el servidor normaliza y fetchea destinos.
3. Notá si sigue redirects, cambios DNS o formatos IP alternativos.

## Pasos de exploit / testing

1. Confirmá capacidad básica de request saliente.
2. Testeá loopback, rangos privados y objetivos tipo metadata donde esté autorizado.
3. Observá timing, status codes, fuga de headers o señales indirectas de éxito.
4. Verificá si redirects bypassean allowlists.
5. Compará comportamiento para HTTP vs HTTPS y formas domain vs IP directa.

## Señales de validación

- el servidor puede fetchear destinos controlados por atacante
- objetivos internos o privados producen comportamiento distinguible
- metadata o paths admin internos son alcanzables
- la validación de URL bloquea algunas formas pero no alternativas equivalentes

## Mitigación

- restringir destinos de egress con precisión
- validar y normalizar URLs cuidadosamente
- evitar fetchers genéricos donde sea posible
- segmentar redes para que app servers no puedan alcanzar sistemas sensibles casualmente
- proteger explícitamente el acceso a metadata

## Logging / detección

- requests salientes inusuales desde el app tier
- requests a loopback, RFC1918 o direcciones tipo metadata
- intentos de fetch fallidos o repetidos contra objetivos internos

## Notas relacionadas

- [[ssrf|SSRF]]
- [[nat-and-private-networks|NAT y redes privadas]]
- [[metadata-endpoints|Metadata endpoints]]
- [[dns-resolution|Resolución DNS]]

## Referencias

- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Investigación / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
