# Third-Party Exposure

## Definición

El third-party exposure es la porción de la superficie de ataque creada por vendors, plataformas SaaS, APIs externas, CDNs, proveedores de identidad, servicios gestionados, widgets y dependencias que manejan tráfico, contenido, autenticación o datos en tu nombre.

## Por qué importa

La superficie de ataque moderna se extiende más allá de los activos que una organización hostea directamente. DNS, proveedores de auth, herramientas de observabilidad, plataformas de soporte, servicios CI/CD, almacenamiento de objetos, scripts de analytics y APIs externas pueden influir en la exposición y la confianza.

Mantené el límite estricto: esta nota es sobre la alcanzabilidad conectada a vendors y la confianza en superficies expuestas, no sobre el problema completo de la seguridad de la supply chain de software.

## Cómo funciona

El third-party exposure tiene **5 roles de confianza**:

1. **Mediador de tráfico.** CDN, WAF, reverse proxy, load balancer, DNS o provider de email.
2. **Mediador de identidad.** SSO, provider OAuth/OIDC, vendor MFA o sincronización de directorio.
3. **Host de contenido.** Docs, marketing, soporte, estado, almacenamiento, scripts, widgets y descargas.
4. **Procesador de datos.** Analytics, CRM, ticketing, logs, observabilidad y APIs externas.
5. **Provider del plano de control.** CI/CD, cloud, infraestructura, herramientas admin o plataforma de automatización.

El riesgo es que una superficie de vendor hereda confianza de tu dominio, usuarios, cookies, callbacks, tokens o flujos de datos.

Un ejemplo trabajado, de CNAME de vendor a decisión de confianza:

```
Host:
  support.example.test

Provider:
  SaaS de soporte vía CNAME

Rol de confianza:
  host de contenido + procesador de datos

Datos:
  adjuntos de clientes y metadatos de tickets

Confianza técnica:
  dominio personalizado, callback SSO, links de email

Estado de offboarding:
  contrato de vendor terminado, DNS sigue apuntando al provider

Decisión:
  deriva de offboarding de alta prioridad: eliminar DNS, revocar SSO/callbacks, exportar/eliminar datos, rotar tokens
```

El third-party exposure es maduro cuando cada vendor se describe por rol, datos, ruta de confianza y estado del ciclo de vida.

## Técnicas / patrones

Los profesionales buscan:

- CNAMEs de vendor y custom domains
- URIs de redirect OAuth y URLs de callback SSO
- scripts, widgets, iframes y orígenes de analytics externos
- orígenes CDN y comportamiento de caché
- portales SaaS de soporte/docs/estado
- archivos y almacenamiento hosted por vendor públicos
- integraciones obsoletas después del offboarding
- APIs externas confiadas sin validación

## Variantes y bypasses

El third-party exposure aparece en **7 formas**.

### 1. DNS obsoleto o custom domain colgante

Los mapeos DNS o de dominio personalizado permanecen después de que se eliminan los recursos de vendor.

### 2. Callbacks de identidad sobre-amplios

Los callbacks OAuth/OIDC/SAML, URIs de redirect o configuraciones de tenant confían en una superficie demasiado amplia.

### 3. Scripts e iframes de terceros

Los scripts, widgets o iframes se ejecutan en contextos sensibles del producto.

### 4. Bypass de edge de terceros

Se asumen controles de edge, pero los orígenes o rutas alternativas permanecen alcanzables.

### 5. Consumo inseguro de API externa

La aplicación confía en las responses de terceros sin validación, aislamiento o manejo de fallos.

### 6. Datos expuestos en plataformas de vendor

Las herramientas de soporte, docs, analytics u observabilidad exponen datos fuera de la audiencia prevista.

### 7. Integración abandonada

Los vendors son eliminados del proceso de negocio pero permanecen en DNS, código, OAuth, webhooks o allowlists.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso de cuenta o token.** Los callbacks de identidad y subdominios de confianza se convierten en rutas de takeover.
- **Inyección de contenido.** Los scripts de terceros o mapeos obsoletos sirven contenido controlado por el atacante.
- **Divulgación de datos.** Los logs, tickets, archivos o analytics hosted por vendors exponen datos sensibles.
- **Compromiso del plano de control.** Los vendors CI/CD, cloud o de automatización influyen en sistemas de producción.
- **Fallos de disponibilidad e integridad.** El fallo o la manipulación de APIs externas afecta flujos de trabajo centrales.

## Detección y defensa

Ordenado por efectividad:

1.
**Inventariás terceros por rol de confianza y sensibilidad de datos.**
   Las listas de vendors no son suficientes; capturá qué puede influir cada provider.

2.
**Vinculás el onboarding/offboarding de vendors a DNS, callbacks, tokens y código.**
   Eliminar un vendor de procurement no elimina sus rutas de confianza técnicas.

3.
**Restringís las allowlists de identidad y callback de forma estricta.**
   Los redirects y webhooks OAuth/OIDC/SAML deberían usar orígenes y rutas exactos donde sea posible.

4.
**Revisás la ejecución de contenido externo.**
   Los scripts, widgets e iframes de terceros necesitan CSP, subresource integrity donde sea factible, aislamiento y ownership.

5.
**Validás y aislás el consumo de APIs externas.**
   Tratá las responses de APIs de terceros como input no confiable y definí el comportamiento de fallo.

6.
**Monitoreás dominios hosted por vendors y mapeos personalizados.**
   Los CNAMEs obsoletos y los estados cambiados del provider deberían disparar revisión.

### Qué no funciona como defensa primaria

- **Confianza de vendor como declaración general.** La confianza depende del rol específico, datos y ruta de control.
- **Offboarding sin limpieza técnica.** El DNS, OAuth, webhooks, API keys y scripts frecuentemente permanecen.
- **Reglas de redirect o CORS wildcard.** La confianza amplia amplifica las superficies de terceros obsoletas o comprometidas.
- **Asumir que CDN equivale a protección del origen.** Las rutas directas al origen pueden saltear los controles de edge.

## Labs prácticos

Usá apps propias y configuraciones de vendor.

### Mapeá CNAMEs de terceros

```
while read host; do
  dig CNAME "$host" +short | sed "s|^|$host -> |"
done < subdomains.txt
```

Etiquetá cada provider, propietario y propósito de negocio.

### Auditá orígenes de recursos cargados

```
curl -s https://app.example.test/ | rg -o 'https://[^"]+' | sort -u
```

Revisá orígenes de scripts, frames, imágenes, APIs y analytics.

### Inventariá URIs de redirect OAuth

```
client_id | redirect_uri | propietario | entorno | exacto/wildcard | ¿todavía necesario?
```

Los URIs de redirect wildcard o obsoletos merecen atención inmediata.

### Buscá integraciones en código y docs

```
rg -n "webhook|callback|redirect_uri|saml|oauth|oidc|vendor|stripe|slack|zendesk" src config docs
```

El código y las docs frecuentemente preservan integraciones viejas.

### Construí un registro de inventario de vendors

```
vendor | rol | dominio/ruta | datos manejados | auth/callbacks | propietario | pasos de offboarding
```

El inventario de vendors necesita rutas de confianza técnicas, no solo nombres de procurement.

### Auditá scripts de terceros

```
curl -s https://app.example.test/ \
  | rg -o '<script[^>]+src="https://[^"]+"' \
  | sort -u
```

Cada origen de script externo puede ejecutarse en un contexto de navegador que vos controlás.

## Ejemplos prácticos

- Un mapeo SaaS eliminado deja un subdominio reclamable.
- Una integración de API externa es confiada de forma demasiado amplia.
- Un origen de archivo o widget de terceros amplía la exposición inesperadamente.
- Un URI de redirect OAuth apunta a un entorno obsoleto.
- Un portal de soporte expone adjuntos de clientes.

## Notas relacionadas

- [[subdomain-takeover|Subdomain Takeover]]
- [[external-attack-surface]]
- [[api-inventory-management|API Inventory Management]]
- [[api-security-top-10|API Security Top 10]]
- [[supply-chain-security|Supply Chain Security]]

### Notas atómicas futuras sugeridas

- oauth-redirect-uri-inventory
- third-party-script-risk
- webhook-exposure
- vendor-offboarding-security
- cdn-origin-exposure

## Referencias

- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP API10:2023 Unsafe Consumption of APIs — https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/
- **Investigación / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
