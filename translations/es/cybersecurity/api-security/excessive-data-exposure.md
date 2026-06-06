# Excessive Data Exposure

## Definición

La exposición excesiva de datos ocurre cuando una API devuelve más datos de los que el cliente necesita o el caller está autorizado a ver, frecuentemente confiando en el frontend para ocultar o ignorar los campos sensibles.

## Por qué importa

Las APIs son legibles por máquina. Los campos extra son fáciles de inspeccionar, diffear, scriptear, y almacenar incluso si la UI nunca los renderiza. Esto hace que los datos ocultos en la respuesta sean un fallo directo de límite de confianza, no un problema cosmético.

Este es el síntoma del lado de lectura de [[broken-object-property-level-authorization]]. [[mass-assignment]] es el riesgo correspondiente del lado de escritura donde el servidor acepta demasiados campos.

## Cómo funciona

La exposición excesiva de datos tiene **4 formas de filtración**:

1. **Serialización completa del objeto.** La API devuelve modelos internos en lugar de DTOs de respuesta.
2. **Filtración de relación anidada.** Las relaciones incluidas revelan campos de usuarios, cuentas, tenants, o archivos relacionados.
3. **Filtración de campos de rol o tenant.** Los callers normales reciben campos reservados para admin, soporte, u otro tenant.
4. **Filtración de metadata oculta.** La metadata de debug, auditoría, token, riesgo, IP, path, o infraestructura aparece en las respuestas.

El patrón inseguro común es:

```
const user = await db.users.findAuthorized(req.user, req.params.id)
res.json(user)
```

La autorización para leer el objeto de usuario no significa que cada propiedad del registro interno de usuario deba cruzar el límite de API.

## Técnicas / patrones

Los atacantes testean:

- respuestas raw de API vs lo que muestra la UI
- diferencias de campos entre cuentas de usuario, admin, soporte, y tenant incorrecto
- respuestas de detalle, lista, search, export, y reporte
- versiones viejas de API y endpoints específicos de mobile
- comportamiento de `include=`, `expand=`, `fields=`, y selección de GraphQL
- metadata de respuesta, cuerpos de error, y modos debug

## Variantes y bypasses

La exposición excesiva aparece en **7 formas**.

### 1. Serialización de entidad interna

Los objetos ORM o de dominio se devuelven directamente con campos internos.

### 2. Filtrado oculto en el frontend

El backend envía campos sensibles y espera que la UI no los renderice.

### 3. Filtración por diff de rol

Los usuarios normales reciben campos pensados solo para admin, soporte, o clientes internos.

### 4. Filtración por include anidado

Los objetos relacionados exponen campos que el endpoint de nivel superior normalmente no revelaría.

### 5. Filtración en export y reporte

Los formatos bulk incluyen datos más ricos que las respuestas normales de API.

### 6. Deriva de versión

Las versiones viejas de API siguen devolviendo objetos verbosos después de que se arreglan los endpoints más nuevos.

### 7. Exposición de error y debug

Los cuerpos de error incluyen stack traces, IDs internos, tokens, paths, o detalles de infraestructura.

## Impacto

Ordenado aproximadamente por severidad:

- **Divulgación de datos sensibles.** PII, secretos, tokens, hashes, notas internas, o campos financieros se filtran.
- **Filtración de información de tenant.** Un tenant infiere datos, IDs, o estructura de otro.
- **Reconocimiento de privilegio.** Los flags de rol, risk scores, feature gates, y metadata de soporte revelan paths de ataque.
- **Exposición regulatoria.** Los datos personales o financieros se procesan o filtran fuera de los propósitos previstos.
- **Explotación de seguimiento.** Los IDs y campos de estado extra habilitan el testing de BOLA, BFLA, o mass assignment.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar DTOs de respuesta explícitos por endpoint y contexto de caller.**
   La respuesta de API debe contener solo campos intencionalmente expuestos para esa ruta, rol, tenant, y estado del objeto.

2.
**Autorizar propiedades, no solo objetos.**
   Un caller puede leer un objeto pero no cada propiedad de él. La visibilidad de campos es una decisión de política.

3.
**Revisar los paths de lista, detalle, export, search, e include anidado por separado.**
   Los diferentes code paths frecuentemente usan diferentes serializadores o proyecciones.

4.
**Fail closed en features de `include`, `expand`, `fields`, y selecciones GraphQL.**
   Las features de proyección controladas por el caller necesitan allowlists y autorización por campo.

5.
**Diffear respuestas entre roles y versiones en tests.**
   Los tests deben afirmar la ausencia de campos sensibles, no solo la presencia de campos esperados.

6.
**Eliminar metadata de debug e interna de las respuestas de producción.**
   Los errores deben ser útiles para los clientes sin exponer detalles de implementación.

### Qué no funciona como defensa primaria

- **Ocultamiento en el frontend.** Los datos ya cruzaron el límite.
- **Asumir que "leer objeto" significa "leer todos los campos."** La autorización de propiedades es separada.
- **Confiar en los defaults del serializador.** Los defaults tienden a exponer lo que sea que contenga el objeto.
- **Arreglar solo el endpoint de detalle.** Las listas, exports, reportes, y versiones viejas frecuentemente siguen siendo verbosos.
- **Nombres de campo oscuros.** Los clientes máquina pueden inspeccionar y diffear cada propiedad.

## Labs prácticos

Usar una API propia con al menos dos roles o tenants.

### Comparar respuesta raw con display de UI

```
curl -s -H "Authorization: Bearer $USER" \
  https://api.example.test/users/me | jq .
```

Listar cada campo no mostrado en la UI y decidir si está intencionalmente expuesto.

### Diffear campos entre roles

```
curl -s -H "Authorization: Bearer $USER"  https://api.example.test/accounts/123 | jq -S 'keys'
curl -s -H "Authorization: Bearer $ADMIN" https://api.example.test/accounts/123 | jq -S 'keys'
```

Las diferencias deben coincidir con la política de campos documentada.

### Testear expansión anidada

```
curl -s -H "Authorization: Bearer $USER" \
  'https://api.example.test/projects/123?include=members,owner,billing' | jq .
```

Las relaciones anidadas necesitan el mismo filtrado de propiedades que los endpoints de nivel superior.

### Testear forma de respuesta de export

```
curl -s -H "Authorization: Bearer $USER" \
  https://api.example.test/accounts/export | jq '.[0]'
```

Los exports no deben bypassear los DTOs de respuesta.

## Ejemplos prácticos

- Una respuesta incluye hashes de contraseña, reset tokens, o IDs internos.
- Un campo de solo-admin aparece para usuarios normales pero está oculto por la UI.
- Las versiones viejas de API siguen devolviendo objetos internos verbosos.
- `include=owner` filtra el email y risk score de otro usuario.
- Las respuestas de error incluyen stack traces y paths del servidor.

## Notas relacionadas

- [[broken-object-property-level-authorization]]
- [[mass-assignment]]
- [[api-inventory-management]]
- [[authorization]]
- [[http-messages|HTTP Messages]]
- [[broken-access-control|Broken Access Control]]

## Referencias

- **Fundamental:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
