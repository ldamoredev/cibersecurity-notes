# API Inventory Management

## Definición

La gestión de inventario de APIs es la práctica de saber qué hosts, versiones, rutas, schemas, clientes, entornos, y propietarios de API existen, son alcanzables, y se supone que todavía existen.

## Por qué importa

Mucho del riesgo de APIs es deriva de exposición más que una vulnerabilidad dramática única. Las versiones viejas, los endpoints no documentados, las rutas de solo-mobile, los hosts internos, los sistemas de staging olvidados, y los schemas obsoletos crean superficie de ataque mucho después de que los equipos dejan de pensar en ellos.

Para las APIs, la gestión de inventario se ubica entre [[api-security-top-10]] y el mapeo de superficie de ataque. Los clientes máquina pueden seguir llamando rutas deprecadas incluso después de que la UI del producto deja de usarlas.

## Cómo funciona

Un inventario de API sólido rastrea **5 dimensiones**:

1. **Hosts y entornos.** Hosts de producción, staging, dev, internos, partner, regionales, y temporales.
2. **Versiones y ciclos de vida.** Rutas `v1`, `v2`, beta, deprecadas, sunset, y legacy.
3. **Rutas y métodos.** Path, método HTTP, operación GraphQL, método RPC, o endpoint de evento.
4. **Schemas y contratos.** OpenAPI, schema GraphQL, protobuf, DTOs de request/response, y clientes generados.
5. **Propietarios y consumidores.** Equipo, propietario de servicio, app cliente, integración, tenant, y exposición pretendida.

El bug no es simplemente "existe un endpoint." El bug es que nadie sabe si debería existir, quién lo posee, o qué controles de seguridad se supone que tiene.

## Técnicas / patrones

Los atacantes y defensores buscan:

- `/api/v1`, `/api/v2`, `/beta`, `/internal`, `/admin`, `/mobile`, `/partner`
- OpenAPI, Swagger UI, introspección GraphQL, colecciones Postman, y client SDKs
- strings de rutas en bundles JavaScript y tráfico mobile
- hosts cloud de staging, preview, regionales, y olvidados
- mismatches entre docs, llamadas del frontend, y disponibilidad del backend
- rutas legacy con auth, validación, o rate limits más débiles

## Variantes y bypasses

Los fallos de inventario aparecen en **7 formas**.

### 1. Versiones zombie

Las versiones de API deprecadas siguen siendo alcanzables y pobremente mantenidas.

### 2. Endpoints shadow

Las rutas existen en código o gateways pero no en documentación o tests.

### 3. Exposición de entorno

Los hosts de staging, dev, preview, o internos son alcanzables desde internet.

### 4. Deriva de cliente específico

Los clientes mobile, partner, o legacy llaman rutas con controles más débiles que la app web principal.

### 5. Filtración de schema

Los docs, la introspección, o los clientes generados exponen rutas sensibles y modelos de datos.

### 6. Gaps de propiedad

Ningún equipo posee una ruta, token, host, o versión, así que los arreglos de seguridad no llegan.

### 7. Mismatch gateway/backend

El inventario del gateway difiere de lo que los servicios backend realmente exponen.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso no autorizado a través de rutas viejas.** Los endpoints legacy pueden perder los controles actuales de auth o autorización.
- **Exposición de datos.** Los schemas obsoletos, las respuestas verbosas, y los endpoints de debug filtran campos sensibles.
- **Exposición del control plane.** Las APIs internas o admin se vuelven alcanzables externamente.
- **Bypass de parches.** Los arreglos llegan a las APIs actuales mientras las versiones viejas siguen siendo vulnerables.
- **Puntos ciegos de monitoreo.** Los endpoints desconocidos no se loggean, testean, o rate-limitan correctamente.

## Detección y defensa

Ordenado por efectividad:

1.
**Mantener un inventario de API vivo desde múltiples fuentes.**
   Combinar config de gateway, rutas de servicio, schemas OpenAPI/GraphQL, logs de tráfico, assets cloud, y uso de clientes. Una sola fuente se perderá la deriva.

2.
**Asignar un propietario y estado de ciclo de vida a cada superficie de API.**
   Cada ruta y host debe tener un propietario, exposición pretendida, modelo de auth, versión, y estado de deprecación.

3.
**Comparar continuamente las APIs documentadas, desplegadas, y observadas.**
   Las diferencias entre specs, código, gateway, y tráfico son donde se esconde el riesgo olvidado.

4.
**Retirar versiones con planes de sunset explícitos.**
   La deprecación sin eliminación deja a los atacantes una capa de compatibilidad de larga duración.

5.
**Gatear la documentación sensible y la introspección.**
   Los docs son valiosos, pero los schemas públicos no deben exponer operaciones de solo-internal u modelos ocultos.

6.
**Incluir el inventario en los tests de seguridad.**
   Las rutas desconocidas deben disparar revisión de auth, autorización, rate limiting, logging, y exposición de datos.

### Qué no funciona como defensa primaria

- **Asumir que la documentación está completa.** Los atacantes testean lo que es alcanzable, no lo que está documentado.
- **Remover links de la UI.** Los clientes máquina pueden llamar rutas viejas directamente.
- **Solo inventarios de gateway.** Los servicios backend pueden exponer rutas fuera del gateway o detrás de hosts alternativos.
- **Compatibilidad hacia atrás indefinida.** Las versiones viejas se convierten en superficie de ataque permanente.
- **Revisiones de seguridad solo en el lanzamiento.** La superficie de API cambia continuamente.

## Labs prácticos

Usar solo sistemas propios o sistemas con permiso explícito para evaluar.

### Construir un inventario de endpoints desde código

```
rg -n "app\\.(get|post|put|patch|delete)|router\\.|@Get|@Post|@RequestMapping|graphql" src routes
```

Normalizar los hallazgos en host, versión, ruta, método, propietario, requisito de auth, y estado de ciclo de vida.

### Comparar docs con tráfico

```
rg -n "/api/|swagger|openapi|graphql" public src mobile openapi.yaml
```

Buscar rutas usadas por clientes pero ausentes del schema oficial, y rutas del schema no usadas por clientes.

### Sondear exposición de versión de forma segura

```
for v in v1 v2 beta internal partner mobile; do
  curl -i "https://api.example.test/api/$v/health"
done
```

El objetivo es inventario y alcanzabilidad, no volumen.

### Verificar exposición de documentación

```
curl -i https://api.example.test/swagger.json
curl -i https://api.example.test/graphql
```

Los docs públicos deben coincidir con la exposición intencional y no revelar operaciones de solo-internal.

## Ejemplos prácticos

- `/api/v1/` sigue funcionando después de la migración a v2.
- Las APIs mobile exponen rutas que el cliente web nunca llama.
- Los endpoints de staging son accesibles desde internet y olvidados.
- Swagger expone operaciones admin internas.
- Un gateway bloquea `/admin`, pero el servicio backend es alcanzable en otro host.

## Notas relacionadas

- [[api-security-top-10]]
- [[api-rate-limiting]]
- [[excessive-data-exposure]]
- [[endpoint-discovery|Endpoint Discovery]]
- [[external-attack-surface|External Attack Surface]]
- [[http-overview|HTTP Overview]]

## Referencias

- **Fundamental:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing and OWASP alignment — https://portswigger.net/web-security/api-testing/top-10-api-vulnerabilities
