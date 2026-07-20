# Broken Function Level Authorization

## Definición

Broken Function Level Authorization (BFLA) ocurre cuando una API permite que un caller invoque una operación, ruta, método, o acción de workflow que su rol o contexto no debería poder ejecutar.

## Por qué importa

Las APIs exponen funciones de negocio directamente: aprobar, reembolsar, exportar, invitar, suspender, impersonar, eliminar, publicar, sincronizar. Si esas funciones dependen de la visibilidad en la UI, la oscuridad de la ruta, o un middleware inconsistente, los clientes normales pueden llamar operaciones privilegiadas directamente.

BFLA es diferente de [[broken-object-level-authorization]]: el problema no es solo qué objeto se apunta, sino si el caller puede invocar la función en absoluto.

## Cómo funciona

BFLA tiene **4 pasos**:

1. Existe una función privilegiada en el backend.
2. La ruta, método, parámetro de acción, o mutación GraphQL es descubrible.
3. El servidor autentica al caller pero no hace cumplir el privilegio requerido.
4. La función se ejecuta para el rol incorrecto o el estado de workflow incorrecto.

Ejemplo:

```
POST /api/admin/users/123/disable HTTP/1.1
Authorization: Bearer normal-user-token
```

Si el handler solo verifica "logueado", el usuario normal ejecuta una acción de admin.

## Técnicas / patrones

Los atacantes testean:

- `/admin`, `/manage`, `/internal`, `/support`, `/moderation`, `/ops`
- cambios de método HTTP: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- acciones ocultas en JavaScript, apps mobile, schemas OpenAPI, e introspección GraphQL
- botones de solo-rol deshabilitados en la UI pero respaldados por rutas invocables
- versiones alternativas de API y clientes mobile/internos
- transiciones de workflow: aprobar, rechazar, reembolsar, publicar, suspender, invitar, exportar

## Variantes y bypasses

BFLA aparece en **6 formas**.

### 1. Exposición de ruta admin

Las rutas admin/soporte existen y son alcanzables por usuarios con menores privilegios.

### 2. Confusión de método

Un método sobre un recurso está protegido mientras que otro método sobre la misma ruta no lo está.

### 3. Abuso de parámetro de acción

Un endpoint genérico acepta `action=approve` u `operation=delete` sin autorización por acción.

### 4. Path de cliente alternativo

Los clientes mobile, de partner, legacy, o internos exponen un gating de rutas más débil que la UI web.

### 5. Bypass de estado de workflow

El caller puede invocar una función antes de que se completen los prerequisites o después de que un estado debería estar bloqueado.

### 6. Exposición de mutación GraphQL

Las queries pueden ser seguras, pero las mutaciones o campos de admin son invocables sin verificaciones a nivel de resolver.

## Impacto

Ordenado aproximadamente por severidad:

- **Escalada de privilegios.** Usuarios normales ejecutan acciones de admin o soporte.
- **Operaciones destructivas.** Acciones de eliminar, suspender, reembolsar, resetear, revocar, o publicar se ejecutan incorrectamente.
- **Exports sensibles.** Los reportes o exports bypassean la política objeto por objeto.
- **Abuso de workflow.** Se fuerzan aprobaciones, invitaciones, pagos, o transiciones de estado.
- **Compromiso del control plane.** Las funciones internas u operadoras se convierten en superficie de API pública.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir permisos a nivel de función explícitamente.**
   Cada operación privilegiada debe mapear a un permiso o política nombrada, no solo a un prefijo de ruta.

2.
**Hacer cumplir la autorización en handlers/resolvers del lado del servidor.**
   El ocultamiento en la UI, los botones deshabilitados, y las verificaciones de rol del frontend son irrelevantes para callers directos de la API.

3.
**Proteger cada método y variante de acción.**
   Revisar `GET/POST/PATCH/DELETE`, acciones en lote, imports/exports, y campos de acción genérica por separado.

4.
**Mantener las APIs admin/soporte/internas detrás de límites y políticas fuertes.**
   La restricción de red ayuda, pero las verificaciones a nivel de función siguen perteneciendo al servidor.

5.
**Testear con tokens con rol degradado.**
   Probar cada función privilegiada con identidades normales, de solo lectura, vencidas, y de tenant incorrecto.

6.
**Loggear las acciones sensibles denegadas.**
   Los intentos de invocar operaciones privilegiadas son indicadores de abuso de alta señal.

### Qué no funciona como defensa primaria

- **Ocultar rutas admin.** Las rutas se filtran a través de JS, apps mobile, docs, tráfico, y guessing.
- **Verificar solo prefijos de ruta.** Las funciones privilegiadas frecuentemente aparecen bajo familias de rutas normales.
- **Confiar en afirmaciones de rol del cliente.** El servidor debe derivar y hacer cumplir el rol/permiso.
- **Devolver 404 para todas las denegaciones.** El camuflaje sin política sigue siendo roto.

## Labs prácticos

Usar cuentas normal y privilegiada.

### Descubrir superficies de función

```
rg -n "admin|disable|approve|refund|export|invite|impersonate|delete" app.js src/ openapi.yaml
```

Buscar en rutas, schemas, bundles de cliente, y tráfico mobile.

### Reproducir ruta privilegiada con token normal

```
curl -i -X POST -H "Authorization: Bearer $NORMAL" \
  https://api.example.test/admin/users/123/disable
```

Esperado: `403` sin efectos secundarios.

### Testear confusión de método

```
for method in GET POST PUT PATCH DELETE; do
  curl -i -X "$method" -H "Authorization: Bearer $NORMAL" \
    https://api.example.test/users/123
done
```

Cada método necesita su propia decisión de autorización.

### Testear abuso de parámetro de acción

```
curl -i -X POST -H "Authorization: Bearer $NORMAL" \
  -H 'Content-Type: application/json' \
  -d '{"action":"approve","targetUserId":"123"}' \
  https://api.example.test/workflows
```

Los endpoints de acción genérica son imanes de BFLA.

## Ejemplos prácticos

- Un usuario normal llama `/api/admin/export`.
- Un usuario de solo lectura envía `DELETE /api/users/123`.
- Una ruta mobile permite la suspensión de cuenta sin verificaciones web admin.
- Una mutación GraphQL `makeUserAdmin` carece de autorización en el resolver.
- Un endpoint de impersonación de soporte es invocable desde la API pública.

## Notas relacionadas

- [[authorization]]
- [[broken-object-level-authorization]]
- [[api-inventory-management]]
- [[broken-access-control|Broken Access Control]]

## Referencias

- **Fundamental:** OWASP API5:2023 Broken Function Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa5-bfla/
- **Fundamental:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
