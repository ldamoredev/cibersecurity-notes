# Deprecated API Versions

## Definición

Las deprecated API versions son endpoints viejos, reemplazados, beta, móviles, de partner o legacy que permanecen alcanzables después de que la organización cree que los clientes ya migraron.

## Por qué importa

Las versiones viejas de API a menudo preservan autenticación más débil, responses más ruidosas, validación más laxa, rate limits faltantes o lógica de negocio más simple. Crean superficie de ataque desfasada en el tiempo: un diseño viejo permanece explotable después de que el producto principal ha mejorado.

Esto es deriva de inventario primero y una categoría de vulnerabilidad segundo. La superficie vieja permanece alcanzable porque el retiro se rezagó respecto a la entrega.

## Cómo funciona

El riesgo de API deprecated tiene **4 estados del ciclo de vida**:

1. **Actual.** Soportado, con propietario, testeado, monitoreado y documentado.
2. **Deprecated.** Todavía soportado temporalmente, pero programado para retiro.
3. **Zombie.** Se suponía que debía irse, pero sigue alcanzable.
4. **Desconocido.** Descubierto desde tráfico, clientes, docs o código sin propietario claro.

El estado de mayor riesgo no siempre es "deprecated"; es "desconocido" o "zombie", porque los controles y propietarios son poco claros.

Un ejemplo trabajado, de endpoint viejo a deriva de controles:

```
Endpoint actual:
  GET /api/v2/users/me -> id, email, displayName

Endpoint viejo:
  GET /api/v1/users/me -> id, email, displayName, role, billingPlan, internalNotes

Auth:
  ambos requieren login

Diferencia:
  v1 devuelve campos eliminados en la revisión de privacidad de v2

Decisión:
  deriva de forma de datos; arreglá v1 o eliminalo, porque "deprecated" no reduce el impacto activo
```

La comparación clave no es solo la disponibilidad de la ruta. Es si los controles de seguridad y la forma de datos cambiaron entre versiones.

## Técnicas / patrones

Los profesionales buscan:

- `/v1`, `/v2`, `/beta`, `/legacy`, `/old`, `/mobile`, `/partner`
- headers de versión y negociación de contenido
- specs OpenAPI viejas, SDKs, colecciones Postman y clientes móviles
- docs archivadas y requests de ejemplo
- diferencias en auth, campos de response, rate limits y validación
- rutas legacy encontradas en JavaScript o source maps

## Variantes y bypasses

La exposición de API deprecated aparece en **6 formas**.

### 1. Versión de ruta URL obsoleta

Las rutas `/api/v1` viejas permanecen activas después del lanzamiento de `/api/v2`.

### 2. API de cliente alternativo

Las APIs móviles, de partner o internas permanecen alcanzables con supuestos más débiles.

### 3. Contrato de API público obsoleto

Las docs o esquemas viejos revelan rutas y campos que ya no son visibles en el producto principal.

### 4. Paridad de controles desigual

La autenticación, autorización, rate limits, validación o logging difieren entre versiones.

### 5. Forma de datos más amplia

Los endpoints viejos devuelven más campos o aceptan input más amplio.

### 6. Deprecación sin retiro

Los avisos de deprecación existen, pero el retiro nunca ocurre.

## Impacto

Ordenado aproximadamente por severidad:

- **Bypass de autorización.** Las rutas viejas no tienen los chequeos actuales de objeto/función/propiedad.
- **Exposición de datos sensibles.** Las responses legacy exponen campos eliminados de las APIs más nuevas.
- **Mass assignment o bypass de validación.** Los modelos de request más viejos aceptan campos protegidos.
- **Bypass de rate limit.** Los controles de abuso se aplican solo a las rutas actuales.
- **Bypass de parche.** Las vulnerabilidades corregidas en v2 permanecen en v1.

## Detección y defensa

Ordenado por efectividad:

1.
**Inventariás versiones de API con propietarios y fechas de sunset.**
   Cada versión debería tener un estado de soporte y un plan de eliminación.

2.
**Aplicás correcciones de seguridad en cada versión alcanzable.**
   Hasta ser eliminadas, las versiones deprecated son superficie de ataque de producción.

3.
**Comparás versiones viejas y nuevas con diffs enfocados en seguridad.**
   Testéa auth, autorización, campos, validación, rate limits y logging.

4.
**Medís el tráfico activo antes del retiro, luego enforceás la eliminación.**
   El monitoreo soporta la migración, pero la compatibilidad indefinida crea riesgo permanente.

5.
**Eliminás docs, SDKs y esquemas obsoletos o los marcás claramente.**
   Los contratos viejos públicos aceleran el descubrimiento y el abuso.

### Qué no funciona como defensa primaria

- **Etiquetas de deprecación.** Un endpoint deprecated sigue siendo explotable mientras sea alcanzable.
- **Eliminar las llamadas del frontend.** Las apps móviles, scripts y clientes HTTP directos siguen pudiendo llamar rutas viejas.
- **Corregir solo las versiones actuales.** Los atacantes eligen la versión alcanzable más débil.
- **Asumir que el bajo tráfico significa bajo riesgo.** Los endpoints legacy de bajo volumen son frecuentemente de alto impacto.

## Labs prácticos

Usá APIs propias.

### Enumerá versiones activas

```
for v in v1 v2 v3 beta legacy mobile partner; do
  curl -i "https://api.example.test/api/$v/health"
done
```

Registrá versiones activas, redirigidas, denegadas y desconocidas.

### Comparás la forma de datos entre versiones

```
curl -s -H "Authorization: Bearer $USER" https://api.example.test/api/v1/users/me | jq -S 'keys'
curl -s -H "Authorization: Bearer $USER" https://api.example.test/api/v2/users/me | jq -S 'keys'
```

Los campos extra inesperados en versiones viejas son hallazgos.

### Testéa la validación de input

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin","debug":true}' \
  https://api.example.test/api/v1/users/me
```

Las versiones viejas a menudo preservan el comportamiento de binding y validación más viejo.

### Construí una tabla de inventario de versiones

```
versión | estado | propietario | tráfico activo | paridad de seguridad | fecha de sunset | bloqueador
```

El propietario desconocido o la fecha de sunset faltante es un smell de superficie de ataque.

### Testéa la paridad de rate limit

```
for v in v1 v2; do
  for i in $(seq 1 20); do
    curl -s -o /dev/null -w "$v %{http_code}\n" "https://api.example.test/api/$v/search?q=test"
  done
done
```

Las versiones deprecated a menudo no tienen los controles de abuso más nuevos.

## Ejemplos prácticos

- `/api/v1/` sigue devolviendo más campos que `/api/v2/`.
- Una ruta de API móvil deprecated permanece expuesta a internet.
- Los chequeos de auth o rol viejos persisten en una versión legacy.
- Las rutas de partner siguen aceptando API keys amplias.
- Los esquemas deprecated revelan endpoints ocultos.

## Notas relacionadas

- [[api-inventory-management|API Inventory Management]]
- [[endpoint-discovery]]
- [[excessive-data-exposure|Excessive Data Exposure]]
- [[mass-assignment|Mass Assignment]]
- [[external-attack-surface]]

### Notas atómicas futuras sugeridas

- api-version-sunsetting
- mobile-api-drift
- schema-exposure
- legacy-api-control-diffing
- partner-api-exposure

## Referencias

- **Fundamental:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
