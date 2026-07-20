# Service Validation

## Definición

La service validation es el proceso de confirmar qué es realmente un servicio observado, cómo se comporta, si es propiedad del objetivo y está en scope, y si es suficientemente relevante como para avanzar a testing más profundo.

## Por qué importa

No todos los puertos abiertos o rutas que responden importan por igual. La validación distingue ruido, páginas de parking, edges de CDN, servicios por defecto y banners engañosos de aplicaciones significativas o targets de control-plane.

Esta nota viene después de [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]: primero encontrá qué responde, luego determiná qué es realmente y si debería transicionar a testing.

## Cómo funciona

La service validation hace **5 preguntas sobre el servicio**:

1. **Protocolo.** ¿Qué protocolo habla realmente aquí?
2. **Rol.** ¿App de producto, API, superficie admin, servicio de datos, proxy, origen o vendor?
3. **Límite.** ¿Público, interno, mediado por CDN, origen directo o plataforma compartida?
4. **Control.** ¿Qué auth, headers, TLS, redirects y errores aparecen?
5. **Próximo test.** ¿Control de acceso, inventario de API, SSRF, drift de versión, storage o sin acción?

El problema no es ver un banner. El valor es probar el rol del servicio y decidir la próxima acción válida.

Un ejemplo trabajado, de banner a rol de servicio:

```
Input:
  203.0.113.42:8443 open, banner says nginx

HTTP:
  redirects to /login, title "Build Console"

TLS SAN:
  ci-preview.example.test

Auth:
  SSO redirect to target IdP

Role:
  CI/CD control surface, not generic nginx

Next action:
  admin-interface review + scope/owner confirmation
```

La validación debería reemplazar etiquetas genéricas con roles operacionales.

## Técnicas / patrones

Los operadores validan con:

- status HTTP, título, redirects, headers y cookies
- comportamiento del certificado TLS y SNI
- banners de servicio y probes de protocolo
- comportamiento de virtual-host y Host-header
- requerimientos de autenticación y autorización
- páginas por defecto y fingerprints de vendors
- comparación contra hosts pares e inventario

## Variantes y bypasses

La service validation produce **6 resultados**.

### 1. App pública esperada

Servicio conocido con controles y owner esperados.

### 2. Superficie de app interesante

App o API en vivo que vale rutas y testing de auth.

### 3. Superficie admin/control

Servicio de alto impacto que requiere revisión de admin-interface.

### 4. Origen directo o bypass de edge

Servicio backend alcanzable fuera del path previsto de proxy/CDN.

### 5. Servicio de datos o infraestructura

Base de datos, queue, caché, métricas, storage o protocolo interno expuesto.

### 6. Ruido o falso positivo

Páginas de parking, plataformas compartidas, puertos filtrados o infraestructura no relacionada.

## Impacto

Ordenado aproximadamente por severidad:

- **Mejor selección de tests.** Los servicios validados alimentan los playbooks correctos.
- **Descubrimiento de control-plane.** Los servicios admin o de infraestructura se identifican temprano.
- **Detección de bypass de edge.** Los orígenes directos revelan errores de límite de confianza.
- **Reducción de falsos positivos.** La validación ahorra tiempo y reduce reportes malos.
- **Corrección de inventario.** Los defensores obtienen evidencia accionable del rol del servicio.

## Detección y defensa

Ordenado por efectividad:

1. **Validá cada servicio inesperado antes del routing de remediación.**
   Los owners necesitan evidencia de qué es el servicio y por qué importa.

2. **Usá múltiples verificaciones de protocolo y contexto.**
   Los banners mienten; el comportamiento, TLS, routing y auth cuentan la historia más completa.

3. **Comparar el rol del servicio con la exposición prevista.**
   Un servicio puede estar parcheado y aun así ser incorrectamente público.

4. **Preservar artefactos de validación.**
   Los headers, screenshots, títulos, comandos y timestamps hacen los hallazgos reproducibles.

5. **Ruta servicios validados a testing específico.**
   Evitar handoffs genéricos de "scaneá más".

### Qué no funciona como defensa primaria

- **Confiar solo en banners.** Los proxies y banners custom engañan.
- **Asumir que 403 significa seguro.** Un servicio protegido todavía puede revelar rol, ruta o gaps de auth.
- **Ignorar redirects.** Los redirects revelan hosts canónicos, sistemas de auth y vendors.
- **Tratar todos los servicios HTTP igual.** Admin, API, docs y sitios estáticos requieren testing diferente.

## Labs prácticos

Usá objetivos propios.

### Validar rol de servicio HTTP

```
curl -k -i https://target.example.test:8443/ | head -n 40
```

Registrar status, headers, título, comportamiento de auth y redirects.

### Comparar comportamiento SNI vs IP directa

```
curl -k -i --resolve app.example.test:443:203.0.113.10 https://app.example.test/
```

Ayuda a detectar comportamiento de origen y virtual-host.

### Capturar identidad TLS básica

```
openssl s_client -connect target.example.test:443 -servername target.example.test </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -ext subjectAltName
```

Los certificados frecuentemente revelan nombres y roles.

### Construir una tarjeta de validación de servicio

```
endpoint | protocolo | rol | auth | evidencia de owner | pista de riesgo | próximo test | artefactos
```

Cada servicio validado debería convertirse en una tarjeta de handoff o en un lead descartado.

### Comparar calidad de denegación autenticada

```
curl -i https://app.example.test/admin
curl -i -H "Authorization: Bearer $NORMAL" https://app.example.test/admin
```

Las diferencias de 403, 401, redirect y contenido ayudan a clasificar superficies de control.

## Ejemplos prácticos

- Un host responde en 443 pero sirve solo un redirect.
- Una interfaz de soporte expone acciones privilegiadas.
- Un banner sugiere una tecnología pero el comportamiento muestra un reverse proxy.
- Un origen directo acepta tráfico sin headers de CDN.
- Un dashboard está protegido por basic auth pero es público.

## Notas relacionadas

- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[tech-stack-fingerprinting|Tech Stack Fingerprinting]]
- [[service-enumeration|Service Enumeration]]
- [[recon-to-testing-handoff|Recon-to-Testing Handoff]]
- [[admin-interface-discovery|Admin Interface Discovery]]

## Referencias

- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
