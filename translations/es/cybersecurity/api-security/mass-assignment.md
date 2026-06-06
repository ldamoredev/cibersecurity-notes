# Mass Assignment

## Definición

El mass assignment ocurre cuando una API automáticamente bindea propiedades provistas por el cliente sobre un objeto interno sin restringir explícitamente qué propiedades el cliente puede establecer.

## Por qué importa

El mass assignment convierte la conveniencia del framework en un bug de autorización. Los cuerpos JSON frecuentemente parecen inofensivos, pero los helpers de binding pueden aceptar campos que la UI nunca expone y el producto nunca pretendió que los clientes controlaran.

Este es el síntoma del lado de escritura de [[broken-object-property-level-authorization]]. [[excessive-data-exposure]] es el hermano del lado de lectura: uno filtra demasiados campos, el otro acepta demasiados campos.

## Cómo funciona

El mass assignment es un **mismatch de 3 formas**:

1. **Forma de request público.** Lo que el cliente debería poder enviar.
2. **Forma de dominio interno.** Lo que la aplicación usa para representar el estado del negocio.
3. **Forma de persistencia.** Lo que la base de datos almacena.

La vulnerabilidad aparece cuando la forma de request público se trata como si pudiera mapearse de forma segura a la forma interna o de persistencia.

Patrón inseguro:

```
app.patch('/api/profile', requireLogin, async (req, res) => {
  const user = await db.users.update(req.user.id, req.body)
  res.json(user)
})
```

Forma más segura:

```
const allowed = {
  displayName: req.body.displayName,
  timezone: req.body.timezone
}

const user = await db.users.update(req.user.id, allowed)
```

El límite importante no es si el campo es JSON válido. Es si este caller puede establecer este campo a través de este endpoint en este estado.

## Técnicas / patrones

Los atacantes testean:

- campos de nivel superior adivinados como `isAdmin`, `role`, `status`, `approved`, y `plan`
- campos de propiedad como `ownerId`, `tenantId`, `organizationId`, y `accountId`
- campos financieros como `creditLimit`, `balance`, `price`, `discount`, y `account_credit_cents`
- campos de workflow como `published`, `verified`, `locked`, y `refunded`
- campos anidados que se bindean a objetos relacionados
- diferencias entre create/update donde `PATCH` es más laxo que `POST`
- clientes alternativos, versiones más viejas, y endpoints bulk

## Variantes y bypasses

El mass assignment aparece en **6 formas comunes**.

### 1. Mutación de flag de privilegio

El cliente establece `isAdmin`, `role`, `permissions`, o `scopes`.

### 2. Reasignación de propiedad

El cliente cambia `ownerId`, `tenantId`, o campos de routing relacionados.

### 3. Mutación de estado de workflow

El cliente fuerza `approved`, `published`, `verified`, `locked`, o estado similar.

### 4. Mutación financiera o de cuota

El cliente cambia plan, créditos, caps de uso, descuentos, o límites.

### 5. Binding de objeto anidado

El endpoint allowlistea campos de nivel superior pero acepta objetos anidados que actualizan registros relacionados protegidos.

### 6. Asignación en bulk

Los endpoints batch aplican campos controlados por el atacante a través de muchos objetos sin autorización por campo.

## Impacto

Ordenado aproximadamente por severidad:

- **Escalada de privilegios.** Los flags de rol, permiso, o admin se vuelven controlados por el cliente.
- **Ruptura de límite de tenant.** Los campos de propiedad o tenant se reasignan.
- **Bypass de lógica de negocio.** Se fuerza el estado de aprobación, verificación, precio, cuota, o workflow.
- **Daño a la integridad de datos.** Los campos de propiedad del servidor ya no reflejan el estado confiable.
- **Persistencia sigilosa.** El ataque puede verse como una actualización normal de perfil o configuración.

## Detección y defensa

Ordenado por efectividad:

1.
**Allowlistear campos escribibles por endpoint, rol, y estado.**
   La regla más segura es que los campos no son escribibles a menos que estén intencionalmente expuestos para esa operación.

2.
**Separar DTOs de request de modelos de dominio y persistencia.**
   Nunca bindear JSON de request directamente en entidades ORM u objetos de dominio internos.

3.
**Rechazar propiedades desconocidas o prohibidas en endpoints sensibles.**
   El rechazo explícito captura el sondeo, hace los tests más claros, y previene que actualizaciones parciales silenciosas oculten bugs.

4.
**Mantener los campos de propiedad del servidor como propios del servidor.**
   Los campos de tenant, propietario, rol, workflow, financieros, y auditoría deben venir del contexto del servidor confiable o política, no del cuerpo del request.

5.
**Testear los flows de create, update, patch, nested, y bulk por separado.**
   Un endpoint de create estricto no prueba que el endpoint de update o batch sea seguro.

6.
**Loggear intentos de envío de campos protegidos.**
   Campos inesperados como `isAdmin` o `tenantId` en requests ordinarios son señal de alta intensidad.

### Qué no funciona como defensa primaria

- **Ocultar campos en el frontend.** Los clientes HTTP pueden enviar JSON arbitrario.
- **Solo depender de validación.** Un campo puede ser válido pero no autorizado.
- **Usar campos protegidos de ORM de forma inconsistente.** La protección a nivel de framework frecuentemente varía por modelo, endpoint, o método de update.
- **Ignorar propiedades desconocidas silenciosamente en todas partes.** Esto puede reducir la explotabilidad, pero también oculta el sondeo y puede fallar en paths de update anidados o alternativos.
- **Asumir que PATCH es más seguro porque es parcial.** Las actualizaciones parciales frecuentemente hacen el mass assignment más fácil.

## Labs prácticos

Usar una API propia o lab local donde se puedan crear dos cuentas e inspeccionar el estado resultante.

### Sondear campos protegidos de nivel superior

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","isAdmin":true,"role":"admin","account_credit_cents":999999}' \
  https://api.example.test/profile
```

Después del request, buscar el objeto de nuevo y verificar si cambió algún campo protegido.

### Sondear campos de propiedad

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"tenantId":"other-tenant","ownerId":"other-user"}' \
  https://api.example.test/projects/123
```

Los campos de propiedad deben ignorarse o rechazarse, nunca confiarse desde el body.

### Sondear binding anidado

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"profile":{"timezone":"UTC"},"account":{"plan":"enterprise","locked":false}}' \
  https://api.example.test/settings
```

Los objetos anidados deben tener sus propios allowlists o estar deshabilitados.

### Sondear actualizaciones bulk

```
curl -i -X POST -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"ids":["1","2"],"updates":{"status":"approved","discount":100}}' \
  https://api.example.test/items/bulk-update
```

Los flows bulk necesitan autorización por objeto y por campo.

## Ejemplos prácticos

- Enviar `{"isAdmin": true}` eleva a un usuario normal.
- Una actualización de perfil acepta `support_priority` o `account_credit_cents`.
- Una actualización de proyecto permite a un usuario cambiar `tenantId`.
- Un ítem borrador puede publicarse estableciendo `status: "published"`.
- Un campo anidado `account.plan` cambia el estado de facturación a través de un endpoint de configuración.

## Notas relacionadas

- [[broken-object-property-level-authorization]]
- [[excessive-data-exposure]]
- [[authorization]]
- [[api-security-top-10]]
- [[business-logic-vulnerabilities|Business Logic Vulnerabilities]]

## Referencias

- **Fundamental:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
