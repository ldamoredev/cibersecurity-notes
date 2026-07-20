# Broken Object Property Level Authorization

## Definición

Broken Object Property Level Authorization (BOPLA) ocurre cuando una API autoriza el acceso a un objeto pero falla en autorizar cuáles propiedades de ese objeto el caller puede leer o modificar.

## Por qué importa

Las APIs frecuentemente exponen objetos estructurados directamente. Incluso cuando la ruta y el objeto están permitidos, los campos individuales pueden cruzar límites de confianza: flags de rol, IDs de tenant, límites financieros, estados de workflow, notas internas, PII, y metadata de seguridad.

BOPLA es la rama de autorización a nivel de propiedad de [[authorization]]. Sus dos síntomas más importantes son [[excessive-data-exposure]] en el lado de lectura y [[mass-assignment]] en el lado de escritura.

## Cómo funciona

BOPLA tiene **2 direcciones**:

1. **Exposición de propiedad en lectura.** El caller recibe campos que no debería ver.
2. **Mutación de propiedad en escritura.** El caller cambia campos que no debería controlar.

Usualmente aparece porque la API trata "puede acceder a este objeto" como equivalente a "puede ver o editar cada campo de este objeto."

Forma de respuesta insegura:

```
app.get('/api/users/:id', requireLogin, async (req, res) => {
  const user = await db.users.findAuthorized(req.user, req.params.id)
  res.json(user)
})
```

El lookup del objeto puede estar autorizado, pero serializar la entidad interna filtra cada propiedad.

Forma de actualización insegura:

```
app.patch('/api/profile', requireLogin, async (req, res) => {
  const updated = await db.users.update(req.user.id, req.body)
  res.json(updated)
})
```

El caller puede actualizar su perfil, pero no necesariamente `role`, `tenantId`, `creditLimit`, o `mfaEnabled`.

## Técnicas / patrones

Los atacantes testean:

- campos de respuesta entre roles, tenants, y versiones de API
- propiedades ocultas presentes en respuestas mobile o admin
- campos JSON extra en `POST`, `PUT`, y `PATCH`
- objetos anidados como `user.role.name`, `account.billingPlan`, o `permissions[]`
- campos devueltos por endpoints de export, search, report, y debug
- diferencias entre callers públicos, autenticados, de soporte, y admin

## Variantes y bypasses

BOPLA es más fácil de razonar como **5 clases de propiedades protegidas**.

### 1. Campos de identidad y propiedad

Campos como `userId`, `ownerId`, `tenantId`, `organizationId`, y `accountId` deciden quién controla o ve el objeto.

### 2. Campos de rol y permiso

Campos como `role`, `isAdmin`, `scopes`, `permissions`, y `supportAccess` alteran la autoridad.

### 3. Campos de workflow y estado

Campos como `approved`, `published`, `locked`, `refunded`, y `status` controlan transiciones de negocio.

### 4. Campos financieros y de cuota

Campos como `creditLimit`, `account_credit_cents`, `plan`, `discount`, y `usageCap` afectan dinero o consumo de recursos.

### 5. Campos sensibles o internos

Campos como `passwordHash`, `mfaSecret`, `resetToken`, `internalNotes`, `riskScore`, y `debugMetadata` no deben exponerse a clientes ordinarios.

## Impacto

Ordenado aproximadamente por severidad:

- **Escalada de privilegios.** Los campos de rol o permiso escribibles otorgan autoridad más fuerte.
- **Ruptura de límite de tenant.** Los campos de propiedad o tenant mueven datos entre cuentas.
- **Divulgación de datos sensibles.** Los campos internos, financieros, o personales se filtran a través de respuestas.
- **Abuso de lógica de negocio.** Los campos de workflow, cuota, precio, o aprobación se cambian directamente.
- **Confusión de auditoría.** Los logs muestran endpoints legítimos pero pierden el acceso a campo no autorizado.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir campos legibles y escribibles por rol, acción, y estado del objeto.**
   La política de propiedades debe ser explícita. Un usuario puede leer `email` pero no `riskScore`, o actualizar `displayName` pero no `role`.

2.
**Usar DTOs de respuesta y de request en lugar de modelos internos.**
   Las formas públicas de API deben ser intencionalmente más pequeñas que las entidades de persistencia. Esto previene la serialización y binding accidental de campos internos.

3.
**Rechazar propiedades de request desconocidas o prohibidas.**
   El ignorado silencioso puede ser aceptable para compatibilidad, pero el rechazo explícito es mejor para endpoints sensibles porque muestra el sondeo y previene la falsa confianza en los tests.

4.
**Testear el comportamiento de campos con múltiples roles y tenants.**
   Comparar respuestas y escrituras aceptadas para usuarios normales, admin, soporte, de solo lectura, y de tenant incorrecto.

5.
**Revisar los endpoints de export, search, y batch por separado.**
   Estos frecuentemente usan diferentes serializadores o proyecciones de query que los endpoints de detalle normales.

6.
**Loggear intentos de escritura en campos protegidos.**
   Los intentos de enviar `isAdmin`, `tenantId`, `ownerId`, o campos financieros son señales útiles de abuso.

### Qué no funciona como defensa primaria

- **Autorización a nivel de ruta sola.** El acceso a `/profile` no implica acceso a cada propiedad del perfil.
- **Formularios del frontend.** Los atacantes pueden enviar propiedades JSON que la UI nunca renderiza.
- **Defaults del serializador.** Los defaults del framework frecuentemente serializan más de lo que el contrato de API pretende.
- **Filtrado de campos del lado del cliente.** Los campos sensibles ya cruzaron el límite si el cliente tuvo que quitarlos.
- **Nombrar campos de forma oscura.** Los campos ocultos o no documentados se filtran a través del tráfico, schemas, clientes mobile, y mensajes de error.

## Labs prácticos

Usar una API propia, lab local, o app deliberadamente vulnerable con al menos dos roles.

### Diffear campos de respuesta por rol

```
curl -s -H "Authorization: Bearer $USER"  https://api.example.test/users/me | jq -S 'keys'
curl -s -H "Authorization: Bearer $ADMIN" https://api.example.test/users/me | jq -S 'keys'
```

Esperado: las diferencias deben coincidir con una política de propiedad documentada, no con el comportamiento accidental del serializador.

### Enviar campos de escritura protegidos

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","role":"admin","tenantId":"other","creditLimit":999999}' \
  https://api.example.test/users/me
```

La API debe rechazar o ignorar los campos prohibidos de forma predecible, y no debe persistirlos.

### Verificar binding de propiedad anidada

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"profile":{"timezone":"UTC"},"account":{"plan":"enterprise"}}' \
  https://api.example.test/profile
```

Los objetos anidados frecuentemente bypassean los allowlists simples de nivel superior.

### Testear serializadores de export/search

```
curl -s -H "Authorization: Bearer $USER" \
  'https://api.example.test/users/export?format=json' | jq '.[0]'
```

Los exports no deben devolver un objeto interno más rico que las respuestas normales de API.

## Ejemplos prácticos

- Una respuesta de perfil incluye `mfaSecret` o `passwordResetToken`.
- Un usuario normal puede establecer `role: "admin"` en un cuerpo JSON.
- Un usuario de soporte puede ver `riskScore` para cuentas fuera de su queue.
- Un endpoint de export incluye notas internas ocultas del endpoint de detalle.
- Un campo anidado `account.plan` puede cambiarse a través de una actualización de perfil.

## Notas relacionadas

- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-function-level-authorization]]
- [[excessive-data-exposure]]
- [[mass-assignment]]

## Referencias

- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
