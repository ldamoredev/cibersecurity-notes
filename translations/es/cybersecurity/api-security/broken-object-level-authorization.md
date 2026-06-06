# Broken Object Level Authorization

## Definición

Broken Object Level Authorization (BOLA) ocurre cuando una API permite que un caller lea, actualice, elimine, exporte, o actúe sobre un objeto para el que no está autorizado a acceder, usualmente cambiando un identificador de objeto.

## Por qué importa

BOLA es una de las clases de bug de APIs de mayor valor porque las APIs naturalmente exponen referencias a objetos en URLs, query strings, cuerpos JSON, y datos de respuesta. Los clientes máquina pueden enumerar, reproducir, y mutar estas referencias más rápido que un atacante dirigido por UI.

BOLA es la forma específica de APIs de [[idor|IDOR]], pero la escala de API, las operaciones en lote, y los grafos de objetos ricos la hacen más amplia que el clásico swapping de IDs web.

## Cómo funciona

BOLA tiene **4 pasos**:

1. La API expone una referencia a un objeto.
2. El caller se autentica exitosamente.
3. El servidor carga el objeto por referencia.
4. El servidor falla en verificar que el caller puede acceder a ese objeto.

Patrón inseguro:

```
const invoice = await db.invoice.findById(req.params.invoiceId)
return res.json(invoice)
```

Forma más segura:

```
const invoice = await db.invoice.findFirst({
  where: { id: req.params.invoiceId, accountId: req.user.accountId }
})
if (!invoice) return res.sendStatus(404)
```

El bug es buscar por identificador sin scopear el objeto a la autoridad del caller.

## Técnicas / patrones

Los atacantes testean:

- IDs en paths: `/users/123`, `/orders/456`, `/files/789`
- IDs en queries: `?accountId=`, `?invoice=`, `?tenant=`
- IDs en body en `POST`, `PUT`, `PATCH`, y endpoints de acción
- IDs anidados: proyecto → tarea, org → usuario, factura → adjunto
- pivots de lista-a-detalle donde las respuestas de lista filtran IDs útiles
- endpoints de export, bulk, share, preview, y download
- IDs predecibles y UUIDs copiados de logs, emails, tráfico mobile, o respuestas de API

## Variantes y bypasses

BOLA aparece en **6 formas comunes**.

### 1. BOLA de lectura

El caller lee el objeto, archivo, metadata, o respuesta de detalle de otro usuario.

### 2. BOLA de escritura

El caller modifica, elimina, o dispara un cambio de estado en el objeto de otro usuario.

### 3. BOLA de objeto anidado

El objeto padre se verifica, pero los IDs hijos no están con scope a ese padre o tenant.

### 4. BOLA de bulk/export

Los endpoints de objeto único están protegidos, pero las rutas de bulk, exports, reportes, o background jobs no lo están.

### 5. BOLA de relación

El caller no puede acceder al objeto directamente pero puede adjuntarlo, compartirlo, invitarlo, transferirlo, o vincularlo a través de un endpoint de relación.

### 6. Mito del UUID/ID opaco

El equipo depende de IDs no adivinables en lugar de verificar la autorización. Los IDs filtrados siguen funcionando.

## Impacto

Ordenado aproximadamente por severidad:

- **Exposición de datos cross-tenant.** Un tenant lee los registros de otro tenant.
- **Modificación no autorizada de objetos.** Las actualizaciones, eliminaciones, transferencias, aprobaciones, o acciones de workflow afectan otro objeto.
- **Filtración de archivos o exports.** Los downloads y reportes exponen datos sensibles a escala.
- **Pivote de privilegio.** El acceso al objeto lleva a usuarios relacionados, tokens, facturas, o workflows de admin.
- **Daño a la integridad del negocio.** Se cambia la propiedad, estado, precio, cuota, o estado de aprobación.

## Detección y defensa

Ordenado por efectividad:

1.
**Scopear cada lookup de objeto al contexto de autorización del caller.**
   Buscar tanto por ID de objeto como por tenant/account/owner/relación. Esto hace que los objetos no autorizados sean indistinguibles de los objetos ausentes para el handler.

2.
**Aplicar la misma política a los paths de lectura, escritura, eliminación, export, y acción.**
   Proteger `GET` mientras se olvida `DELETE`, `download`, o `export` es común.

3.
**Validar las relaciones de objetos anidados.**
   Verificar que los recursos hijos pertenecen al padre y tenant autorizados, no solo que ambos IDs existen.

4.
**Testear con dos identidades reales.**
   BOLA no se prueba con una cuenta. Usar dos usuarios o tenants y swapear solo la referencia al objeto.

5.
**Loggear intentos cross-objeto.**
   Los intentos repetidos de acceder a IDs adyacentes, tenants foráneos, o IDs de objeto desconocidos son señal de alta intensidad.

### Qué no funciona como defensa primaria

- **UUIDs o IDs opacos solos.** Reducen el guessing pero no autorizan referencias filtradas o cosechadas.
- **Autenticación de ruta.** Estar logueado no implica acceso a cada objeto.
- **Ocultar IDs de objeto en la UI.** Las APIs, apps mobile, logs, exports, y el tráfico revelan IDs.
- **Devolver 404 sin hacer cumplir la política.** El camuflaje de código de estado no es autorización.

## Labs prácticos

Usar dos usuarios o tenants.

### Capturar un request de objeto válido

```
curl -i -H "Authorization: Bearer $USER_A" \
  https://api.example.test/invoices/100
```

Registrar status, forma del body, y propietario del objeto.

### Reproducir con otra identidad

```
curl -i -H "Authorization: Bearer $USER_B" \
  https://api.example.test/invoices/100
```

Esperado: denegado o no encontrado sin filtrar datos.

### Testear BOLA de escritura

```
curl -i -X PATCH -H "Authorization: Bearer $USER_B" \
  -H 'Content-Type: application/json' \
  -d '{"nickname":"changed"}' \
  https://api.example.test/invoices/100
```

Las rutas de escritura frecuentemente fallan diferente que las rutas de lectura.

### Testear scope de objeto anidado

```
curl -i -H "Authorization: Bearer $USER_A" \
  https://api.example.test/projects/1/tasks/900
```

Verificar que la tarea `900` pertenece al proyecto `1` y al caller, no solo a cualquier proyecto accesible.

### Testear rutas de export y batch

```
curl -i -X POST -H "Authorization: Bearer $USER_A" \
  -H 'Content-Type: application/json' \
  -d '{"invoiceIds":[100,200,300]}' \
  https://api.example.test/invoices/export
```

Los inputs en lote deben autorizar cada objeto.

## Ejemplos prácticos

- `/api/orders/101` puede cambiarse a `/api/orders/102`.
- Un usuario puede descargar el PDF de factura de otro tenant.
- Un miembro de proyecto puede adjuntar una tarea de otro proyecto.
- Un export en lote incluye IDs foráneos mezclados en el cuerpo del request.
- Un endpoint de share permite que un usuario se auto-invite al objeto de otra cuenta.

## Notas relacionadas

- [[authorization]]
- [[broken-function-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[idor|IDOR]]
- [[exploit-idor|Exploit IDOR]]

## Referencias

- **Fundamental:** OWASP API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-bola/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger IDOR — https://portswigger.net/web-security/access-control/idor
