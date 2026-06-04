---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - sql-injection
sources: []
---

# Inyección SQL

## Definición
La inyección SQL (SQLi) ocurre cuando un input controlado por el usuario se incorpora a una query SQL de una forma que cambia la estructura de la query en vez de quedar solo como datos.

## Por qué importa
SQLi es una de las clases de vulnerabilidad más claras e importantes porque enseña la lección central de frontera-de-parser que aparece a lo largo de la seguridad: una vez que el input del atacante se interpreta como código o sintaxis en vez de datos, la confianza colapsa.

También sigue siendo muy práctica. Una sola query vulnerable puede llevar a:
- bypass de autenticación
- acceso no autorizado a datos
- extracción de datos a gran escala
- modificación destructiva
- a veces lectura de archivos, escritura de archivos o ejecución de comandos según el motor de DB y los privilegios

## Cómo funciona
El mecanismo es simple:

1. el input controlado por el atacante llega a un query builder
2. la query se construye de forma insegura por concatenación o interpolación
3. la base de datos parsea el string final como sintaxis SQL

Ejemplo:

```js
const query = `SELECT * FROM users WHERE email = '${email}'`
```

Si `email` es:

```txt
admin@example.com' OR 1=1 --
```

la query efectiva se vuelve:

```sql
SELECT * FROM users WHERE email = 'admin@example.com' OR 1=1 --'
```

Ahora el atacante cambió la lógica de la query, no solo su valor.

### El contexto importa
La forma del payload depende de dónde aterriza la inyección:

- **Contexto de string**  
  `WHERE name = '<input>'`
- **Contexto numérico**  
  `WHERE id = <input>`
- **Contexto de identificador**  
  `ORDER BY <input>`
- **Contexto LIKE**  
  `WHERE name LIKE '%<input>%'`
- **Contexto de limit / offset / dirección de orden**  
  a menudo mal manejado porque los equipos asumen que estos campos son "seguros"

Entender el contexto es una de las habilidades de SQLi de mayor palanca.

## Técnicas / patrones
Los atacantes normalmente testean SQLi a través de:

- formularios de login
- campos de búsqueda
- filtros y report builders
- parámetros de sort/order
- endpoints de export
- features de admin o "internas"
- parámetros ocultos
- cookies o headers usados por código de analytics/reporting
- campos de body JSON mapeados a query builders dinámicos

Patrones de testeo comunes:

- sondas de quote-breaking
- sondas basadas en booleanos
- comportamiento basado en errores
- comportamiento basado en tiempo
- extracción basada en union
- caminos de segundo orden donde input del atacante almacenado se usa luego de forma insegura

## Variantes y bypasses

### SQLi basada en errores
La aplicación devuelve errores de DB o stack traces que revelan el comportamiento del parser.

Señales típicas:
- error de sintaxis cerca de una comilla
- mensajes de error específicos de DB
- errores de cast / tipo que filtran fragmentos de query

### SQLi basada en UNION
Útil cuando la salida controlada por el atacante se refleja en la response y la DB permite un `UNION SELECT` compatible.

Tareas principales:
- determinar la cantidad de columnas
- determinar tipos compatibles
- encontrar qué columnas se reflejan

### SQLi ciega basada en booleanos
La response cambia sutilmente según una condición sea verdadera o falsa.

Patrón de ejemplo:
- `AND 1=1`
- `AND 1=2`

Esto es más lento que el reflejo completo pero común y práctico.

### SQLi ciega basada en tiempo
Se usa cuando la app no refleja resultados visiblemente pero la DB puede introducir delays medibles.

Los patrones de ejemplo difieren por motor:
- MySQL: `SLEEP()`
- PostgreSQL: `pg_sleep()`
- MSSQL: `WAITFOR DELAY`

### SQLi out-of-band
En algunos entornos la DB puede disparar callbacks de DNS o de red. Esto importa cuando la extracción ciega tradicional es demasiado lenta.

### Bypasses de filtros
Las defensas ingenuas a menudo fallan porque se apoyan en:
- blocklists de keywords
- stripping de comillas
- patrones superficiales de WAF

Estilos de bypass comunes incluyen:
- estilos alternativos de comentario
- variación de casing
- payloads codificados
- operadores alternativos
- explotar rarezas de sintaxis específicas de DB
- inyección en contexto-de-identificador donde no se usa parametrización

### Diferencias entre DBMS
Los payloads varían mucho entre:
- MySQL
- PostgreSQL
- MSSQL
- Oracle
- SQLite

Una buena nota de SQLi debería recordarte fingerprintear el motor antes de asumir portabilidad del payload.

## Impacto
El impacto depende de:
- los privilegios de DB
- el entorno
- la posición de red
- a qué datos puede acceder la cuenta de servicio

Impacto típico:
- leer filas sensibles
- modificar o borrar registros
- bypassear el login
- acceder a metadata interna almacenada en la DB
- pivotar a lectura/escritura de archivos o RCE en sistemas mal configurados

Una SQLi "ciega" igual puede ser crítica si corre bajo un rol de DB altamente privilegiado.

## Detección y defensa
Ordenado por efectividad:

1. **Queries parametrizadas en todos lados**
   Este es el arreglo real. La estructura de la query y los valores deben enviarse por separado.

2. **Allowlist para identificadores**
   Para campos como `ORDER BY`, nombres de tabla o nombres de columna, usá allowlists explícitas porque estos normalmente no pueden parametrizarse como valores.

3. **Mínimo privilegio en la capa de base de datos**
   El usuario de DB de la app no debería tener capacidad amplia de DDL, archivos, admin o ejecución de comandos.

4. **Restringí las features peligrosas de DB**
   Deshabilitá o restringí features que amplifican el impacto.

5. **Validá la forma en el borde de la aplicación**
   La validación de tipo, formato y dominio reduce la superficie de ataque, pero no es un sustituto de la parametrización.

6. **Manejo de errores seguro**
   No filtres errores de DB a los usuarios.

7. **Monitoreo**
   Vigilá:
   - sondas tipo-sintaxis repetidas
   - latencia de query inusual
   - picos en las tasas de error
   - comportamiento anómalo de DB en endpoints de bajo riesgo

## Ejemplos prácticos
- bypass de auth en un formulario de login vía inyección en contexto-de-string
- filtro de reporting vulnerable por un campo de orden concatenado de forma insegura
- endpoint de export de admin vulnerable porque los supuestos de "usuario confiable" reemplazaron la codificación defensiva
- endpoint de búsqueda explotable vía SQLi ciega en un campo JSON procesado por un query builder dinámico

## Notas relacionadas
- [[http-messages|Mensajes HTTP]]
- [[broken-access-control|Control de acceso roto]]
- [[auth-flaws|Fallas de autenticación]]
- [[cybersecurity/security-playbooks/exploit-sqli|Explotar SQLi]]

### Notas atómicas futuras sugeridas
- [[second-order-injection|Inyección de segundo orden]]
- [[nosql-injection|Inyección NoSQL]]
- [[orm-injection-patterns|Patrones de inyección en ORM]]

## Referencias
- **Foundational:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Foundational:** OWASP SQL Injection Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Research / Deep Dive:** PortSwigger SQLi cheat sheet — https://portswigger.net/web-security/sql-injection/cheat-sheet
