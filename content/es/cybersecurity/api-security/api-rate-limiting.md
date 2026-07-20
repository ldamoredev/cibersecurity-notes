# API Rate Limiting

## Definición

El rate limiting de APIs es el conjunto de controles que restringen con qué frecuencia un cliente, identidad, token, fuente, tenant, o workflow puede consumir recursos de API dentro de un período.

## Por qué importa

Las APIs están pensadas para llamarse programáticamente, lo que significa que el abuso puede ocurrir a velocidad de máquina. Los límites débiles habilitan ataques de credenciales, scraping, enumeración, picos de costo, generación de reportes costosos, agotamiento de inventario, e incidentes de denial-of-wallet incluso cuando no existe un bug clásico de inyección.

El rate limiting pertenece cerca de [[broken-authentication]], [[api-inventory-management]], y [[client-ip-trust|Client IP Trust]] porque la pregunta clave es: ¿qué identidad o recurso se está realmente protegiendo?

## Cómo funciona

Los límites de API útiles combinan **4 claves de límite**:

1. **Límites de fuente.** Dirección IP, ASN, región, reputación de proxy, o identidad de red edge.
2. **Límites de caller.** Cuenta, usuario, tenant, client ID, API key, o subject del token.
3. **Límites de ruta.** Endpoint, método, acción, workflow, o tipo de recurso.
4. **Límites de costo.** Complejidad de search, tamaño de export, costo de reporte, tamaño de archivo, o gasto downstream.

El bug usualmente es elegir solo una clave. Los límites por IP fallan bajo abuso distribuido; los límites por cuenta se pierden endpoints anónimos; los límites de ruta se pierden parámetros costosos.

Forma de política de ejemplo:

```
POST /auth/login      -> por cuenta + por IP + par de credenciales
GET /search           -> por cuenta + costo de query + cuota de tenant
POST /reports/export  -> por cuenta + costo de reporte + concurrencia
POST /auth/refresh    -> por familia de refresh token + cuenta + señales de anomalía
```

## Técnicas / patrones

Los atacantes testean:

- capacidad burst y tasa de requests sostenida
- enforcement por IP vs por cuenta vs por token
- versiones alternativas de API, rutas mobile, endpoints GraphQL, y rutas batch
- headers de proxy falsificados o confiados
- endpoints de login, reset, MFA, y refresh
- endpoints costosos de search, export, reporte, archivo, y AI/modelo
- si los límites se resetean en la rotación de token o el cambio de cuenta

## Variantes y bypasses

Los fallos de rate limit aparecen en **7 formas**.

### 1. Limitación solo por IP

Los atacantes rotan IPs o explotan problemas de confianza en headers de proxy.

### 2. Limitación solo por cuenta

Los flows anónimos o de credential stuffing bypassean los límites cambiando cuentas objetivo o credenciales.

### 3. Inconsistencia de ruta

El endpoint principal está limitado, pero las rutas mobile, versionadas, GraphQL, batch, o export no lo están.

### 4. Límites ciegos al costo

Cada request cuenta como uno aunque algunos requests disparen trabajo costoso.

### 5. Bypass por reset de token

Refrescar o reemitir tokens resetea contadores incorrectamente.

### 6. Lag de enforcement distribuido

Múltiples gateways o servicios mantienen contadores inconsistentes.

### 7. Gaps de concurrencia

La API limita el conteo de requests pero no los trabajos, exports, o background tasks simultáneos.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso de credenciales.** Brute force, credential stuffing, adivinanza de reset-token, o fatiga de MFA.
- **Scraping y enumeración de datos.** Los endpoints de search, lista, y detalle se filtran a escala.
- **Agotamiento de recursos.** CPU, base de datos, queue, almacenamiento, email, SMS, o costos de API de terceros se disparan.
- **Denial-of-wallet.** Los servicios downstream costosos se consumen por abuso.
- **Degradación de confiabilidad.** Los usuarios legítimos son ralentizados o bloqueados por callers sin límite.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir el recurso protegido antes de elegir la clave de límite.**
   El login protege cuentas y credenciales; los exports protegen el volumen de datos y los trabajos del backend; el search protege el costo de query y la superficie de scraping.

2.
**Combinar límites conscientes de fuente, caller, ruta, y costo.**
   Las claves en capas hacen los bypasses comunes más difíciles y reducen los falsos positivos.

3.
**Hacer cumplir los límites en el edge y en la aplicación.**
   Los gateways son útiles para controles toscos; la lógica de aplicación entiende cuentas, tenants, workflows, y costo de negocio.

4.
**Normalizar y confiar en IPs de cliente solo a través de cadenas de proxy conocidas.**
   Los rate limits basados en `X-Forwarded-For` falsificable son fáciles de bypassear.

5.
**Agregar límites de concurrencia y trabajo para operaciones costosas.**
   Los reportes, exports, imports, procesamiento de archivos, y llamadas AI/modelo necesitan más que límites de request-por-minuto.

6.
**Monitorear denegaciones, near-limits, y patrones distribuidos.**
   El abuso frecuentemente aparece como muchos callers que se mantienen justo debajo de un umbral simple.

### Qué no funciona como defensa primaria

- **Límites por IP solos.** El tráfico de cloud, proxy, y bot hace que la IP sea una identidad débil por sí misma.
- **CORS.** Los clientes no-browser lo ignoran, y el control de origen del browser no es control de abuso.
- **Pacing del frontend.** Los atacantes llaman la API directamente.
- **Un límite global para cada ruta.** Las rutas costosas y sensibles a la seguridad necesitan políticas diferentes.
- **Confiar en headers de IP provistos por el cliente.** Solo los headers insertados por proxies conocidos deben influir en la identidad.

## Labs prácticos

Usar solo sistemas propios o targets de lab, y mantener volúmenes de request bajos.

### Identificar claves de límite desde respuestas

```
curl -i -H "Authorization: Bearer $USER" https://api.example.test/search?q=test
```

Registrar el comportamiento de `429`, `Retry-After`, headers de rate-limit, y si los contadores parecen por IP, cuenta, token, o ruta.

### Testear por cuenta vs por IP de forma segura

```
for i in 1 2 3 4 5; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $USER" \
    https://api.example.test/auth/refresh
done
```

Observar si la política está documentada y es estable; no generar volumen disruptivo.

### Testear confianza de header de proxy en un lab

```
curl -i -H 'X-Forwarded-For: 203.0.113.10' \
  https://api.example.test/rate-limit-demo
```

Cambiar headers no confiables no debe cambiar la identidad del caller.

### Testear límites conscientes del costo

```
curl -i -H "Authorization: Bearer $USER" \
  'https://api.example.test/search?q=a&limit=1000&include=deep'
```

Los parámetros de alto costo deben tener límites más estrictos que las lecturas baratas.

## Ejemplos prácticos

- Los endpoints de login permiten intentos de credenciales ilimitados.
- El search puede scrapear en alto volumen porque solo las rutas de escritura están limitadas.
- El spoofing de `X-Forwarded-For` bypassea los controles por IP.
- La generación de reportes permite muchos trabajos costosos concurrentes.
- Refrescar un token resetea los contadores y habilita el abuso sostenido.

## Notas relacionadas

- [[client-ip-trust|Client IP Trust]]
- [[broken-authentication]]
- [[api-auth-flaws]]
- [[api-inventory-management]]
- [[test-client-ip-spoofing|Test Client IP Spoofing]]

## Referencias

- **Fundamental:** OWASP API4:2023 Unrestricted Resource Consumption — https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
