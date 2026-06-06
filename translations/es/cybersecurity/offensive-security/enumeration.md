# Enumeration

## Definición

La enumeration es la expansión enfocada y metódica de pistas descubiertas en conocimiento concreto y validado sobre servicios alcanzables, rutas, identidades, parámetros, versiones y comportamientos.

## Por qué importa

El recon encuentra assets candidatos. La enumeration convierte candidatos en entendimiento accionable: qué está vivo, qué responde, qué contiene la superficie y qué merece testing más profundo.

Operacionalmente se ubica entre el recon amplio y la validación. El [[subdomain-enumeration|Subdomain Enumeration]] y el [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]] expanden el conjunto de objetivos, mientras que la [[service-validation|Validación de Servicios]] confirma qué hallazgos merecen tiempo de testing.

## Cómo funciona

La enumeration hace **5 preguntas de expansión**:

1. **¿Qué nombres existen?** Dominios, subdominios, virtual hosts y aliases.
2. **¿Qué responde?** Hosts en vivo, puertos, protocolos, apps HTTP, APIs y storage.
3. **¿Qué rutas existen?** Paths, métodos, parámetros, versiones, schemas y endpoints ocultos.
4. **¿Qué identidades o roles existen?** Superficies de login, pistas de tenant, usernames, roles públicos y contactos de soporte.
5. **¿Qué patrones se repiten?** Naming, stack, rutas, entornos y pistas de ownership.

El error en la enumeration es recolectar listas enormes sin validarlas ni priorizarlas.

Un ejemplo trabajado, enumeration a cola de testing:

```
Input:
  api-preview.example.test is live and in scope

Expansion:
  JS bundle reveals /api/v1/users/{id}, /api/v1/admin/export, /api/v2/search

Validation:
  normal user gets 200 on /users/{own_id}, 403 on /admin/export, 200 on /search

Classification:
  object-ID route, admin function, search endpoint

Handoff:
  /users/{id} -> BOLA/IDOR testing
  /admin/export -> BFLA/access-control testing
  /search -> injection/rate-limit review
```

La enumeration es madura cuando ordena los hallazgos por clase de test probable en lugar de solo aumentar la cantidad.

## Técnicas / patrones

Los operadores enumeran:

- subdominios y registros DNS
- hosts, puertos, virtual hosts y servicios
- rutas web, rutas de API, schemas de GraphQL y parámetros
- fingerprints tecnológicos y endpoints por defecto
- pistas de usuario/tenant/cuenta donde sea ético y en scope
- superficies de staging, legacy, admin y soporte

## Variantes y bypasses

La enumeration tiene **6 streams**.

### 1. Name enumeration

Subdominios, hostnames, virtual hosts y aliases DNS.

### 2. Network enumeration

Hosts en vivo, puertos, protocolos y banners de servicio.

### 3. Web route enumeration

Paths, métodos, redirects, status codes y patrones de contenido.

### 4. API enumeration

Versiones, schemas, endpoints, campos, parámetros y estados de auth.

### 5. Technology enumeration

Frameworks, proveedores edge, servicios cloud, versiones y paths por defecto.

### 6. Context enumeration

Flujos de negocio, roles, tenants, vendors y funciones de soporte/admin.

## Impacto

Ordenado aproximadamente por severidad:

- **Priorización de objetivos.** La enumeration identifica assets con probabilidad real de contener hallazgos.
- **Descubrimiento de superficie oculta.** Rutas, versiones y parámetros se vuelven visibles.
- **Selección de path de ataque.** Los hallazgos se enrutan a testing de BOLA, BFLA, SSRF, SQLi, XSS o misconfiguration.
- **Corrección de inventario.** Los defensores ven qué pueden enumerar los de afuera.
- **Calidad de evidencia.** La enumeration validada crea inputs de testing reproducibles.

## Detección y defensa

Ordenado por efectividad:

1. **Corré enumeration controlada contra assets propios.**
   La enumeration defensiva previene exposición sorpresa.

2. **Alimentá los resultados al inventario y ownership.**
   La enumeration sin ownership se convierte en un montón de texto.

3. **Hardening de superficies ocultas y por defecto.**
   Las rutas ocultas, páginas por defecto y versiones viejas necesitan controles reales.

4. **Monitoreá patrones de enumeration.**
   Muchos 404, route guessing, probes de vhost y probing de parámetros son señales útiles.

5. **Reducí la descubribilidad innecesaria mientras preservás controles reales.**
   Menos ruido ayuda, pero el control de autorización y exposición importa más que esconder.

### Qué no funciona como defensa primaria

- **Depender de la oscuridad.** La enumeration está diseñada para encontrar superficies no linkeadas.
- **Rate limiting solo por IP.** La enumeration distribuida puede mantenerse baja y amplia.
- **Tratar los 404 como inofensivos.** Los patrones de misses suelen revelar enumeration activa.
- **Asumir que la documentación está completa.** La enumeration testea la realidad desplegada.

## Labs prácticos

Usá objetivos propios.

### Construir una tabla de pipeline de enumeration

```
lead | stream | evidence | validation | risk hint | next step
```

Mantené evidencia y siguiente acción juntas.

### Enumerar patrones de rutas desde código/artefactos

```
rg -o '["'\\''`]/[A-Za-z0-9_./{}:-]+' public dist src | sort -u
```

Clasificar rutas por app, API, admin, debug o desconocido.

### Agrupar hallazgos por clase de test probable

```
admin route -> access control / BFLA
object id route -> BOLA / IDOR
url fetch route -> SSRF
file route -> path traversal / file access
search route -> injection / rate limits
```

El handoff importa tanto como la lista.

### Preservar el estado de enumeration

```
asset | stream | candidate | verified? | auth state | likely class | next test
```

Esto evita que la enumeration amplia pierda contexto.

### Comparar vistas autenticada y no autenticada

```
curl -i https://app.example.test/api/profile
curl -i -H "Authorization: Bearer $TOKEN" https://app.example.test/api/profile
```

Los diferentes estados de auth suelen revelar familias de rutas y controles distintos.

## Ejemplos prácticos

- Enumerar subdominios revela hosts de staging y admin en vivo.
- La validación de rutas identifica assets que vale testear manualmente.
- La enumeration encuentra desajuste entre la documentación y la API desplegada.
- Parámetros ocultos cambian los campos de la response.
- Servicios en puertos altos revelan dashboards y productos de vendors.

## Notas relacionadas

- [[recon|Recon]]
- [[subdomain-enumeration|Subdomain Enumeration]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[service-validation|Validación de Servicios]]
- [[recon-to-testing-handoff|Handoff de Recon a Testing]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
