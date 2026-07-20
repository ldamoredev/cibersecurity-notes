# Endpoint Discovery

## Definición

El endpoint discovery es el proceso de encontrar rutas, APIs, handlers, parámetros, métodos y superficies de request ocultas más allá de lo que la UI visible o la documentación oficial revela.

## Por qué importa

Las aplicaciones y APIs suelen exponer más superficie de backend de la que muestra el frontend. Los bundles JavaScript, las apps móviles, versiones viejas, esquemas, parámetros ocultos, campos GraphQL, URLs archivadas y clientes generados pueden revelar rutas que saltan los flujos normales del producto.

El curriculum de bug bounty de zSecurity lo destaca bien: los endpoints ocultos y los parámetros ocultos no son trivia separada. Son cómo los testers encuentran la forma real del backend.

## Cómo funciona

El endpoint discovery tiene **5 clases de fuentes**:

1. **Tráfico observado.** Navegador, móvil, cliente de API, logs de proxy y capturas HAR.
2. **Contratos publicados.** OpenAPI, Swagger, GraphQL, Postman, SDKs y docs.
3. **Artefactos del lado del cliente.** Bundles JavaScript, source maps, apps móviles y constantes de rutas.
4. **Fuentes históricas.** Wayback, caches de buscadores, docs viejas y ejemplos filtrados.
5. **Patrones adivinables.** Wordlists, familias de rutas, versiones, acciones, parámetros e intercambios de método.

El bug no es que los endpoints sean descubribles. El bug es que los endpoints descubiertos se comportan fuera del modelo de autorización, validación, inventario o ciclo de vida previsto.

Un ejemplo trabajado, de string de ruta a hallazgo:

```
Fuente:
  static/app.8fd3.js contiene "/api/internal/reports/export"

Estado del inventario:
  ausente de la spec OpenAPI pública

Sondeo:
  GET devuelve 401, POST con token de usuario normal devuelve 403

Seguimiento:
  POST con método cambiado y "include=all" sigue denegando

Conclusión:
  endpoint descubierto existe, pero la evidencia actual muestra que la autorización se mantiene
```

El endpoint discovery es maduro cuando puede distinguir "nueva ruta que vale la pena rastrear" de "nueva ruta explotable".

## Técnicas / patrones

Los profesionales testean:

- `/api`, `/v1`, `/v2`, `/graphql`, `/internal`, `/admin`, `/debug`
- cambios de método HTTP en rutas conocidas
- familias de rutas encontradas en bundles JavaScript
- parámetros ocultos como `debug`, `admin`, `role`, `redirect`, `next`, `include`, `expand`, `fields`
- exposición de OpenAPI/Swagger e introspección GraphQL
- endpoints archivados y rutas solo de móvil
- cambios de content-type y parsers alternativos

## Variantes y bypasses

El endpoint discovery produce **7 clases de endpoints**.

### 1. Ruta documentada con controles faltantes

La ruta es conocida pero le falta la auth esperada, rate limits o validación.

### 2. Ruta de backend no documentada

La ruta del backend existe pero está ausente de docs, UI, inventario y tests.

### 3. Versión de API deprecated

Versiones viejas de API permanecen alcanzables con controles más débiles.

### 4. Endpoints de cliente alternativo

Los clientes móvil, partner, interno o admin exponen comportamiento alternativo.

### 5. Parámetros ocultos

Los parámetros alteran la autorización, campos, output de debug, redirecciones o comportamiento del flujo de trabajo.

### 6. Esquemas expuestos

Los esquemas revelan queries, mutations, campos de objeto u operaciones deprecated.

### 7. Endpoints de diagnóstico

Las rutas de health, métricas, trace, actuator y debug revelan estado o controlan el comportamiento.

## Impacto

Ordenado aproximadamente por severidad:

- **Bypass de autorización.** Las rutas o métodos ocultos saltan las políticas aplicadas en otros lugares.
- **Exposición de datos sensibles.** Parámetros ocultos, campos o esquemas revelan datos extra.
- **Exposición del plano de control.** Las rutas admin/debug se vuelven invocables.
- **Explotación de deriva de versión.** Los endpoints viejos preservan las vulnerabilidades viejas.
- **Aceleración del reconocimiento.** El descubrimiento de rutas alimenta testing de BOLA, BFLA, mass assignment, SSRF e inyección.

## Detección y defensa

Ordenado por efectividad:

1.
**Generás y mantenés un inventario autoritativo de rutas.**
   Compará rutas deployadas, config del gateway, esquemas, código y tráfico observado.

2.
**Aplicás controles de seguridad por política, no por oscuridad de rutas.**
   Los endpoints ocultos deberían seguir aplicando autenticación, autorización, validación, rate limits y logging.

3.
**Revisás esquemas y artefactos del cliente antes de la publicación.**
   Las docs y bundles públicos no deberían exponer operaciones solo-internas o detalles sensibles del modelo.

4.
**Testás familias de rutas entre métodos, versiones y clientes.**
   Un `GET` protegido no prueba que `POST`, `PATCH`, móvil o v1 sean seguros.

5.
**Fallás cerrado en parámetros desconocidos.**
   Los parámetros ocultos no deberían alterar silenciosamente el comportamiento relevante para la seguridad.

### Qué no funciona como defensa primaria

- **No enlazar una ruta en la UI.** Los llamadores HTTP directos no necesitan links de UI.
- **Asumir que las docs de API son la superficie.** JavaScript, apps móviles, esquemas e historial revelan más.
- **Seguridad a través de nombres de rutas aleatorios.** Adivinar es solo una fuente de descubrimiento.
- **Filtrado de parámetros solo en frontend.** Los atacantes pueden enviar parámetros ocultos directamente.

## Labs prácticos

Usá una aplicación propia o de lab.

### Extraé rutas de bundles JavaScript

```
rg -o '["'\\''`]/[A-Za-z0-9_./{}:-]+' public dist static | sort -u
```

Normalizá los hallazgos en ruta, método, archivo fuente y probable propietario.

### Compará rutas en código vs spec

```
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src routes openapi.yaml
```

Encontrá rutas presentes en código pero ausentes de docs, y entradas de docs sin ruta activa.

### Testéa parámetros ocultos

```
curl -i 'https://api.example.test/users/me?debug=true&include=roles,permissions'
```

Buscá expansión de campos, output de debug o cambios de política.

### Testéa verbos HTTP

```
for m in GET POST PUT PATCH DELETE OPTIONS; do
  curl -i -X "$m" https://api.example.test/api/users/me
done
```

Cada método aceptado debería tener un motivo y una política.

### Construí una tabla de endpoints descubiertos

```
endpoint | método | fuente | ¿documentado? | resultado auth | propietario | riesgo | próximo test
```

Esto evita que el descubrimiento de rutas se convierta en un montón de URLs sin estructura.

### Inspeccioná source maps

```
curl -sS https://app.example.test/static/app.js.map | jq -r '.sources[]?' | head
```

Los source maps pueden ser artefactos de debug legítimos o exposición accidental de rutas/código fuente.

## Ejemplos prácticos

- Un bundle JavaScript expone `/api/internal/reports`.
- Un endpoint `/v1/` viejo todavía acepta auth más débil.
- `?debug=true` devuelve campos internos.
- La introspección GraphQL revela mutations admin.
- Un endpoint solo-móvil salva CSRF o rate limits.

## Notas relacionadas

- [[api-inventory-management|API Inventory Management]]
- [[deprecated-api-versions]]
- [[admin-interface-discovery]]
- [[broken-function-level-authorization|Broken Function Level Authorization]]
- [[public-asset-discovery|Public Asset Discovery]]

### Notas atómicas futuras sugeridas

- hidden-parameter-discovery
- js-recon
- graphql-introspection-exposure
- openapi-security-review
- route-guessing

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
