# Authorization

## Definición

La autorización es la decisión del lado del servidor que determina qué puede leer, escribir, invocar, o transicionar un caller de API autenticado. En APIs, la autorización debe hacerse cumplir en los límites de objeto, función y propiedad.

## Por qué importa

La autenticación solo responde "¿quién está llamando?" La autorización responde "¿este caller tiene permiso de hacer esta cosa exacta a este recurso exacto con estos campos exactos?" Las APIs exponen identificadores, métodos, rutas, cuerpos JSON, acciones en lote, y respuestas legibles por máquina directamente, así que el ocultamiento en el frontend nunca es un control.

Esta es la nota paraguas. [[broken-object-level-authorization]] tiene la autorización de acceso a objetos, [[broken-function-level-authorization]] tiene la autorización de acceso a acciones, y [[broken-object-property-level-authorization]] tiene la visibilidad/mutabilidad de campos.

## Cómo funciona

La autorización de APIs tiene **3 capas de enforcement**:

1. **A nivel de objeto:** ¿puede esta identidad acceder a este objeto? Ejemplo: `invoice_id=123`.
2. **A nivel de función:** ¿puede esta identidad invocar esta operación? Ejemplo: `POST /admin/users/ban`.
3. **A nivel de propiedad:** ¿puede esta identidad ver o modificar este campo? Ejemplo: `isAdmin`, `ownerId`, `account_credit_cents`.

Ejemplo de handler inseguro:

```
app.get('/api/invoices/:id', requireLogin, async (req, res) => {
  const invoice = await db.invoices.findById(req.params.id)
  res.json(invoice)
})
```

El caller está autenticado, pero el lookup del objeto no está con scope a `req.user`. La decisión de autorización está ausente.

El bug es tratar la identidad como permiso.

## Técnicas / patrones

Atacantes y defensores testean:

- IDs de objetos en paths, queries, cuerpos JSON, y estructuras anidadas
- rutas de solo-rol como `/admin`, `/support`, `/internal`, `/moderation`
- campos ocultos aceptados por `POST`, `PUT`, y `PATCH`
- endpoints de lote, export, import, y reporte
- clientes alternativos y versiones de API
- transiciones de estado de workflow como aprobar, reembolsar, publicar, invitar, suspender
- asimetría lectura/escritura donde las lecturas se verifican pero las actualizaciones no

## Variantes y bypasses

Los fallos de autorización de APIs se agrupan en **3 familias canónicas**.

### 1. Fallos a nivel de objeto

La API verifica que el caller esté logueado pero no que el objeto destino le pertenezca o esté de otra manera autorizado. Esto es BOLA/IDOR.

### 2. Fallos a nivel de función

La API expone una ruta o acción que el rol del caller no debería poder invocar. Esto incluye endpoints de admin, soporte, export, destructivos, y de workflow.

### 3. Fallos a nivel de propiedad

La API devuelve o acepta campos que el caller no debería ver o controlar. Esto incluye exposición excesiva de datos y mass assignment.

## Impacto

Ordenado aproximadamente por severidad:

- **Ruptura de límite de tenant.** Un tenant lee o modifica los datos de otro tenant.
- **Escalada de privilegios.** Usuarios normales invocan acciones de admin/soporte o mutan campos privilegiados.
- **Divulgación de datos.** Propiedades sensibles o objetos enteros se filtran a través de respuestas de API.
- **Corrupción de estado.** Se cambian campos no autorizados o estados de workflow.
- **Abuso de negocio.** Se manipulan reembolsos, aprobaciones, exports, invitaciones, créditos, cuotas, o propiedad.
- **Fallo de auditoría.** Los logs muestran usuarios autenticados pero no las decisiones de autorización faltantes.

## Detección y defensa

Ordenado por efectividad:

1.
**Denegar por defecto en las capas de objeto, función y propiedad.**
   Cada ruta debe requerir una decisión de política explícita. La política faltante debe fallar cerrado, no heredar "autenticado es suficiente."

2.
**Scopear el acceso a datos en la query.**
   Buscar objetos a través del dataset permitido del caller: `WHERE id = ? AND account_id = ?`. Las verificaciones post-fetch son mejores que ninguna, pero las queries con scope previenen la exposición accidental y reducen errores de race.

3.
**Centralizar la política pero mantener las decisiones específicas.**
   Usar helpers/objetos de política de autorización compartidos, pero pasar contexto de recurso, acción, actor, tenant, y campo. Las verificaciones de rol genérico solas son demasiado toscas para APIs.

4.
**Separar DTOs de request de los modelos internos.**
   Las formas públicas de request/response deben definir qué campos se aceptan y devuelven. Las entidades internas no deben serializarse ni bindearse directamente.

5.
**Testear la autorización como una matriz.**
   Usar al menos dos usuarios, dos roles, y dos tenants. Testear rutas de lectura, escritura, eliminación, export, lote, y workflow por separado.

6.
**Loggear las denegaciones e intentos sospechosos cross-boundary.**
   Los cambios repetidos de ID de objeto, intentos de rutas admin, y envíos de campos protegidos son señales útiles de abuso.

### Qué no funciona como defensa primaria

- **Ocultar controles de UI.** Los callers de API pueden enviar HTTP directamente.
- **Usar UUIDs como autorización.** La imprevisibilidad ayuda a la resistencia de enumeración pero no prueba el acceso.
- **Confiar en roles o IDs de tenant provistos por el cliente.** El servidor debe derivar la autoridad del contexto de sesión/token confiable y la política.
- **CORS.** CORS controla el acceso de lectura del browser; no autoriza acciones de API.
- **Solo referencias indirectas.** Mapear `abc123` a un objeto no es autorización a menos que el mapeo esté con scope al caller.

## Labs prácticos

Usar una API propia o app de lab con al menos dos usuarios y dos roles.

### Construir una matriz de autorización

```
Filas: usuarios/roles/tenants
Columnas: endpoints/acciones/campos
Celdas: permitido, denegado, no aplica
```

Mantener esto como la fuente de verdad para los tests.

### Testear acceso a objeto con dos usuarios

```
curl -s -H "Authorization: Bearer $USER_A" https://api.example.test/invoices/100
curl -s -H "Authorization: Bearer $USER_B" https://api.example.test/invoices/100
```

El segundo request debe fallar si la factura `100` pertenece solo al usuario A.

### Testear acceso a función

```
curl -i -X POST -H "Authorization: Bearer $USER" \
  https://api.example.test/admin/users/123/disable
```

Los usuarios normales deben recibir `403`, no `200`, `404` por oscuridad, o una acción parcial.

### Testear control de escritura de propiedades

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","isAdmin":true,"account_credit_cents":999999}' \
  https://api.example.test/profile
```

Los campos protegidos deben ser rechazados o ignorados de forma predecible y nunca persistidos.

### Testear exposición de campos de respuesta

```
curl -s -H "Authorization: Bearer $USER" https://api.example.test/users/me | jq .
```

Buscar campos internos, flags de rol, secretos, IDs de propiedad, o datos de otros usuarios.

## Ejemplos prácticos

- Un usuario puede leer la factura de otro usuario cambiando `/api/invoices/{id}`.
- Un no-admin puede llamar `POST /api/admin/export`.
- Una actualización de perfil acepta `isAdmin` o `support_priority`.
- Un endpoint de lista oculta campos sensibles, pero los endpoints de detalle y export los devuelven.
- Una ruta de API mobile omite la política aplicada en la ruta web.

## Notas relacionadas

- [[broken-object-level-authorization]]
- [[broken-function-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[mass-assignment]]
- [[excessive-data-exposure]]
- [[broken-access-control|Broken Access Control]]
- [[exploit-idor|Exploit IDOR]]

## Referencias

- **Fundamental:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
