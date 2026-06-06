# Server-Side Request Forgery (SSRF)

## Definición

SSRF ocurre cuando se puede inducir a una aplicación a hacer un request del lado del servidor hacia un destino elegido por el atacante. El peligro clave es que el servidor frecuentemente puede alcanzar recursos internos o privilegiados a los que el atacante externo no puede acceder directamente.

## Por qué importa

SSRF es uno de los ejemplos más claros de por qué redes y seguridad web deben aprenderse juntas. Convierte la accesibilidad de red del lado del servidor en impacto explotable.

A diferencia de muchos bugs de input, el radio de explosión depende fuertemente del entorno:
- accesibilidad a la red interna
- exposición del servicio de metadatos
- comportamiento del proxy
- manejo de redirecciones
- comportamiento del DNS

## Cómo funciona

La forma habitual es:

1. la aplicación acepta una URL o referencia a recurso remoto
2. el servidor realiza el request en nombre del usuario
3. la validación del destino es débil, bypasseable o inexistente
4. el atacante usa la posición de red y la confianza del servidor para alcanzar objetivos que no puede llamar directamente

Puntos de entrada comunes de SSRF:
- funcionalidades de preview de URL
- webhooks y testers de callback
- fetchers de documentos o imágenes
- funcionalidades de importación/sincronización
- pipelines de PDF/renderizado
- helpers de "obtener recurso remoto"

## Técnicas / patrones

Los atacantes generalmente testean:
- objetivos de loopback y localhost
- rangos RFC1918/privados
- direcciones del servicio de metadatos
- representaciones alternativas de IP
- comportamiento de dominio vs IP directa
- cadenas de redirección
- cambios de destino basados en DNS
- manejo de protocolos y esquemas

## Variantes y bypasses

### Accesibilidad interna básica

La app puede hacer fetch de servicios internos a los que el atacante no puede acceder directamente.

### Targeting de metadatos

La app puede alcanzar endpoints de metadatos de la nube y exponer credenciales o contexto de la instancia.

### Bypass por redirección

La validación ocurre solo en la primera URL, pero las redirecciones llevan a algún lugar peligroso.

### Trucos de DNS rebinding / resolución

La validación y la conexión no tratan la resolución del hostname de forma consistente.

### Quirks del parser / normalización de URL

Diferentes componentes no coinciden sobre el destino real.

### SSRF ciego

El atacante no puede leer la respuesta directamente, pero puede inferir la accesibilidad a partir del timing, efectos secundarios o callbacks out-of-band.

## Impacto

Impacto típico:
- acceso a APIs internas
- exposición de credenciales de metadatos
- accesibilidad a superficies de admin internas
- bypass de límites de confianza hacia servicios privados
- pivoting hacia un compromiso más amplio de la infraestructura

El mismo sink SSRF puede ser de baja severidad en un entorno y crítico en otro.

## Detección y defensa

Ordenado por efectividad:

1. **Restringir adónde pueden ir los requests del lado del servidor**
2. **Validar y normalizar los destinos cuidadosamente**
3. **Ser explícito sobre el manejo de redirecciones, DNS e IP**
4. **Segmentar las redes para que los servidores de app no puedan acceder casualmente a los internos sensibles**
5. **Proteger el acceso a metadatos explícitamente**
6. **Monitorear los requests salientes de los niveles de aplicación**

## Ejemplos prácticos

- una funcionalidad de preview de URL hace fetch de direcciones arbitrarias
- un backend puede alcanzar `169.254.169.254` y exponer metadatos de la nube
- un servicio solo-interno se vuelve accesible a través de la capacidad de fetch de una app pública
- una cadena de redirección bypass una allowlist que solo verifica el primer host

## Notas relacionadas

- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[dns-resolution|DNS Resolution]]
- [[reverse-proxies|Reverse Proxies]]
- [[investigate-ssrf|Investigate SSRF]]

## Referencias

- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Investigación / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
