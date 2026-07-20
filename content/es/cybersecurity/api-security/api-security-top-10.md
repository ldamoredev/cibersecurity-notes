# API Security Top 10

## Definición

El OWASP API Security Top 10 es un framework de conciencia enfocado en las categorías de riesgo más importantes específicas de APIs. Complementa la guía general de web security enfatizando acceso a objetos, exposición de funciones, control de propiedades, consumo de recursos, y deriva del inventario de APIs.

## Por qué importa

Las APIs exponen objetos de negocio, identificadores, datos legibles por máquina, funciones del backend, y superficies de integración de forma más directa que la mayoría de las UIs de browser. Esto cambia cómo los atacantes enumeran sistemas y cómo los defensores deben pensar sobre los límites de confianza.

Esta página es el mapa de la rama de APIs. Las notas individuales llevan el detalle operacional: [[authorization]], [[broken-object-level-authorization]], [[broken-authentication]], [[broken-object-property-level-authorization]], [[api-rate-limiting]], [[broken-function-level-authorization]], [[api-inventory-management]], y [[polymorphic-deserialization]].

## Cómo funciona

El API Top 10 de 2023 puede mantenerse como **5 preguntas de seguridad de APIs**:

1. **¿Quién puede acceder a qué objeto?** BOLA y autorización de objetos.
2. **¿Quién puede invocar qué función?** BFLA y autorización de acciones/workflows.
3. **¿Qué propiedades cruzan el límite?** BOPLA, exposición excesiva, y mass assignment.
4. **¿Cuánto pueden consumir los callers?** Rate limits, controles de costo, y consumo de recursos no restringido.
5. **¿Qué superficie de API existe?** Inventario, versiones, mala configuración, y consumo inseguro.

Este encuadre es más útil que memorizar la lista porque la mayoría de las revisiones de APIs involucran estas preguntas repetidamente.

## Técnicas / patrones

Los atacantes usan APIs porque:

- los identificadores de objetos son más fáciles de manipular directamente
- las funciones son invocables sin el frontend
- las respuestas legibles por máquina son fáciles de diffear y automatizar
- los endpoints no documentados o legacy frecuentemente siguen siendo alcanzables
- los clientes móviles y de partners revelan paths alternativos de API
- los schemas y docs revelan estructura de rutas, campos, y modelos

## Variantes y bypasses

Las categorías del OWASP API Top 10 2023 son:

1.
**API1: Broken Object Level Authorization.**
   Las referencias a objetos son accesibles sin autorización por objeto.

2.
**API2: Broken Authentication.**
   La identidad, credenciales, tokens, o workflows de auth son débiles o inconsistentes.

3.
**API3: Broken Object Property Level Authorization.**
   Las APIs exponen o aceptan propiedades que el caller no debería ver o controlar.

4.
**API4: Unrestricted Resource Consumption.**
   Los callers pueden consumir demasiado cómputo, memoria, almacenamiento, costo downstream, o recurso de negocio.

5.
**API5: Broken Function Level Authorization.**
   Los callers invocan funciones que su rol o estado no debería permitir.

6.
**API6: Unrestricted Access to Sensitive Business Flows.**
   Los workflows de negocio pueden ser automatizados o abusados a escala incluso sin un bug técnico clásico.

7.
**API7: Server Side Request Forgery.**
   Los fetches de URL controlados por la API alcanzan recursos internos o no previstos de la red.

8.
**API8: Security Misconfiguration.**
   Defaults inseguros, errores verbosos, headers débiles, parsers permisivos, o superficies de management expuestas aumentan el riesgo.

9.
**API9: Improper Inventory Management.**
   Versiones, hosts, entornos, o rutas desconocidas siguen siendo alcanzables.

10.
**API10: Unsafe Consumption of APIs.**
    Una API confía en APIs upstream o de terceros sin suficiente validación, aislamiento, o manejo de fallos.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso de tenant y cuenta.** Los fallos de autorización de objeto, función y propiedad cruzan límites de cuenta.
- **Toma de cuenta o persistencia.** Los fallos de auth y token permiten acceso no autorizado o de larga duración.
- **Exposición de datos sensibles.** Respuestas, exports, schemas, y output de debug filtran datos.
- **Abuso de negocio.** Los workflows, cuotas, inventario, precios, o aprobaciones se automatizan o manipulan.
- **Daño a infraestructura y costos.** El agotamiento de recursos, SSRF, y mala configuración alcanzan sistemas backend o crean grandes gastos.

## Detección y defensa

Ordenado por efectividad:

1.
**Hacer threat modeling de APIs por objeto, función, propiedad, recurso, e inventario.**
   Estas cinco preguntas atrapan la mayor parte del riesgo específico de APIs durante el diseño y la revisión.

2.
**Construir tests de autorización y autenticación como matrices.**
   Usar múltiples usuarios, roles, tenants, estados de token, y versiones de API. Los tests de happy-path de un solo usuario se pierden los bugs de API security.

3.
**Usar contratos explícitos de request y response.**
   Los DTOs, schemas, y políticas de campos reducen mass assignment y exposición excesiva.

4.
**Inventariar y monitorear la superficie de API desplegada continuamente.**
   La seguridad depende de lo que es alcanzable, no solo de lo que está documentado.

5.
**Aplicar controles de abuso a workflows de alto valor y alto costo.**
   Los rate limits, límites de concurrencia, cuotas, y detección de anomalías pertenecen a los flujos de negocio, no solo al login.

6.
**Tratar las dependencias de API y los parsers como límites de confianza.**
   Validar los datos de API entrantes y salientes, evitar la deserialización insegura, y aislar los fallos de terceros.

### Qué no funciona como defensa primaria

- **Controles solo en el frontend.** Las APIs son directamente invocables.
- **Autenticación sola.** Los usuarios logueados siguen necesitando autorización por objeto, función y campo.
- **Inventario solo de documentación.** Los atacantes enumeran la superficie desplegada.
- **Cobertura WAF genérica.** Los bugs de APIs son frecuentemente fallos de lógica de negocio y autorización.
- **Revisión única en el lanzamiento.** La superficie de API y los clientes derivan continuamente.

## Labs prácticos

Usar una API propia, lab de entrenamiento, o app intencionalmente vulnerable.

### Construir una matriz de revisión OWASP API

```
endpoint | object auth | function auth | property read/write | rate/cost | version/owner
```

Llenar con los endpoints más sensibles primero.

### Mapear un endpoint a las cinco preguntas

```
POST /api/projects/{id}/members
objeto: ¿puede el caller acceder al proyecto?
función: ¿puede el caller invitar miembros?
propiedades: ¿puede el caller establecer rol/estado?
recurso: ¿están limitadas las invitaciones?
inventario: ¿se comporta igual v1/mobile?
```

Esto crea un hábito de revisión reutilizable.

### Comparar rutas desplegadas con la documentación

```
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src routes openapi.yaml
```

Buscar rutas ausentes de los docs o tests.

## Ejemplos prácticos

- La UI oculta campos que la API sigue devolviendo.
- Las acciones de admin son invocables directamente por un cliente normal.
- Las versiones viejas de la API siguen desplegadas y son descubribles.
- Un endpoint de reporte puede dispararse repetidamente para crear alto costo en el backend.
- Una API hace fetch de URLs provistas por el atacante desde dentro de la red.

## Notas relacionadas

- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-authentication]]
- [[broken-object-property-level-authorization]]
- [[api-rate-limiting]]
- [[broken-function-level-authorization]]
- [[api-inventory-management]]
- [[polymorphic-deserialization]]

## Referencias

- **Fundamental:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
