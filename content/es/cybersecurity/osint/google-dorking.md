# Google Dorking

## Definición

Google dorking es el uso de operadores de motores de búsqueda y patrones de consulta con forma de exposición para encontrar contenido público sensible, mal configurado, indexado o relevante para la seguridad. Es [[search-engine-operators]] apuntado específicamente a lo que no debería ser encontrable: backups, source maps, páginas de error, portales admin, credenciales indexadas y listados de directorio.

## Por qué importa

Google dorking **no es magia hacker — es descubrimiento de exposición a través de la indexación**. Si un motor de búsqueda puede encontrar archivos sensibles, páginas de error, portales de login, listados de directorio o backups, el problema es la exposición pública que permitió la indexación en primer lugar. El dork es solo una consulta que revela un fallo preexistente.

El uso defensivo es más importante que el ofensivo. Ejecutar consultas con forma de exposición contra tu propia organización con una cadencia atrapa artefactos accidentalmente publicados (backups, dumps, logs de build, source maps) más rápido que cualquier scanner externo porque los motores de búsqueda ya han hecho el trabajo de descubrimiento por vos.

La Google Hacking Database (GHDB) cataloga cientos de plantillas de consulta con forma de exposición. Son útiles como **inspiración**, no como lista de copiar/pegar — la forma de exposición de cada organización es diferente.

## Cómo funciona

Google dorking apunta a **5 clases de exposición**. Una consulta dork útil apunta exactamente a una de ellas y acota a un dominio.

1. **Archivos sensibles.** Backups (`.bak`, `.sql`, `.zip`, `.tar`), logs, hojas de cálculo, PDFs, configs (`.env`, `web.config`), source maps (`.map`) y dumps de base de datos.
2. **Portales de login y admin.** Páginas con formularios de login o rutas de gestión (`inurl:admin`, `inurl:manage`, `inurl:dashboard`, `intitle:"login"`).
3. **Listados de directorio.** Páginas `Index of /` indexadas que exponen un árbol de archivos navegable porque el servidor web tiene autoindexación habilitada.
4. **Output de error y debug.** Stack traces, páginas de error de frameworks y output debug verboso que filtran rutas internas, versiones de librerías y fragmentos SQL.
5. **Pistas de tecnología y vulnerabilidad.** Cadenas de versión (`"Apache/2.4.49"`), páginas de instalación por defecto, rutas vulnerables conocidas (`inurl:wp-content/plugins/...`).

El bug no es Google. El bug es que el contenido sensible sea públicamente alcanzable e indexable. La corrección es eliminar la alcanzabilidad, no el resultado de búsqueda.

Un ejemplo trabajado:

```
Pregunta:    ¿example.com expone archivos backup indexados?
Iteración 1: site:example.com (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
             → 0 hits
Iteración 2: site:*.example.com (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
             → 4 hits, todos en dev.example.com
Iteración 3: site:*.example.com filetype:sql -site:docs.example.com
             → 1 hit: dev.example.com/exports/2024_users.sql
Triaje:      exposición verificada, bucket sensible, escalar a respuesta a incidentes.
```

La primera iteración se perdió la exposición porque estaba en un subdominio. El dorking es iterativo.

## Técnicas / patrones

La técnica de dorking está construida sobre cadenas de operadores disciplinadas, no cadenas GHDB memorizadas.

- `site:` acotado a **dominios propios** (o scope explícitamente autorizado).
- `filetype:` para las clases de documento que coinciden con cada categoría de exposición.
- `intitle:"index of"` para listados de directorio, el dork único de mayor rendimiento.
- Búsqueda de frase exacta para cadenas de error conocidas (`"Whitelabel Error Page"`, `"SQLSTATE"`, `"Notice: Undefined"`).
- Patrones `inurl:` para rutas admin, login, backup, config, api, debug, callback y de versión.
- Categorías de consulta estilo GHDB como inspiración; nunca copies ciegamente consultas GHDB contra terceros.
- Combinación con `cache:` para leer la copia indexada cuando la página activa ha sido cambiada o eliminada.

## Variantes y bypasses

Las consultas dork se agrupan en **6 familias de consultas**. La mayoría de los sweeps de dorking defensivo ejecutan una de cada una por trimestre.

### 1. Consultas de exposición de archivos

Buscá backups, logs, configs, hojas de cálculo y source maps. Categoría de mayor impacto — un solo `.sql` o `.env` indexado es a menudo un incidente de exposición de credenciales.

### 2. Consultas de descubrimiento de portales

Encontrá páginas de login, admin, soporte, dashboard y dispositivos. A menudo saca a la superficie paneles admin de vendors olvidados (impresoras, IoT, cámaras) que nadie consideró parte de la superficie.

### 3. Consultas de listado de directorio

Encontrá índices de archivos indexados (`intitle:"index of"`). Casi siempre accidental; el resultado es un árbol de archivos navegable que cualquiera puede recorrer.

### 4. Consultas de mensajes de error

Encontrá páginas de framework, base de datos o stack trace. Exponen rutas internas, fragmentos ORM, versiones de librerías y a veces secretos en frames de stack.

### 5. Consultas de patrones de secretos

Buscá páginas públicas que contengan cadenas tipo token o tipo credencial (`"AKIA"`, `"-----BEGIN PRIVATE KEY-----"`, `"api_key="`). Alta tasa de falsos positivos (documentación, fixtures de test), así que triá con cuidado.

### 6. Consultas de fingerprint de tecnología

Encontrá assets específicos de versión, páginas por defecto (`/phpinfo.php`, `/server-status`) o rutas vulnerables conocidas. Útil para priorizar parching, peligroso para usar contra scope no propio.

## Impacto

Ordenado aproximadamente por severidad:

- **Exposición de secretos o credenciales.** Los archivos `.env`, `.sql`, `.bak` o de config indexados pueden filtrar tokens, contraseñas o claves directamente.
- **Divulgación de datos sensibles.** Documentos, exportaciones y logs revelan datos de clientes o terminología interna.
- **Descubrimiento de superficie admin.** La búsqueda revela portales y dashboards que nunca debían ser descubribles.
- **Apuntado a vulnerabilidades.** Las pistas de versión y las páginas de instalación por defecto estrechan lo que un atacante probaría a continuación.
- **Evidencia de desplazamiento de superficie de ataque.** El contenido antiguo indexado prueba que la exposición existió y permite acotar su vida útil vía caché y archivo.

## Detección y defensa

El dorking defensivo es la defensa de mayor apalancamiento — usa el crawl existente de Google como un scanner de exposición gratuito.

1.
**Eliminá el contenido sensible de la alcanzabilidad pública.**
   La corrección es control de acceso y limpieza, no solo desindexación. Si el archivo sigue siendo alcanzable, la exposición persiste.

2.
**Escanear tus propios dominios con consultas enfocadas en exposición.**
   Ejecutá las 6 familias de consultas contra `site:*.tu-dominio` trimestralmente. Vinculá los hallazgos a una cola de remediación rastreada con un propietario.

3.
**Bloqueá la indexación para páginas no sensibles que no deberían aparecer en búsquedas.**
   `noindex` y `robots.txt` reducen la descubribilidad; no son límites de seguridad. Tratarlos como higiene de documentación.

4.
**Revisá los artefactos de build y documentos públicos antes del lanzamiento.**
   Los source maps, logs de build, páginas de debug y exportaciones públicas son exposiciones indexadas comunes introducidas por la automatización de deploy. Las verificaciones de CI para estas son baratas y de alto rendimiento.

5.
**Monitoreá el desplazamiento de resultados de búsqueda.**
   El nuevo contenido indexado puede revelar nuevos deployments, nuevos portales de vendors o nuevos errores. Un sweep de dorking defensivo programado atrapa la exposición dentro de un ciclo de indexación.

### Qué no funciona como defensa primaria

- **Culpar al motor de búsqueda.** El contenido sensible era públicamente alcanzable; el motor de búsqueda solo lo hizo encontrable.
- **`robots.txt` solo.** Incluso puede revelar rutas de interés (la lista `Disallow:` es un mapa de rutas sensibles).
- **Eliminar el resultado de búsqueda mientras se deja el archivo público.** Cualquiera con la URL puede acceder igualmente; el próximo crawl lo reindexará.
- **Usar ciegamente consultas GHDB contra terceros.** Mantenete autorizado y acotado; ejecutar consultas con forma de exposición contra dominios no propios está bien, pero actuar sobre hallazgos contra dominios no propios no lo está.
- **Confiar solo en el output del dork para la severidad.** Un nombre de archivo `.sql` no prueba que el archivo sea un dump de base de datos real; corroborá con [[osint-triage|triaje]] y una fetch del contenido bajo scope propio.

## Labs prácticos

Usá dominios propios, un scope de engagement autorizado o objetivos de entrenamiento públicos deliberados.

### Buscá backups públicos

```
site:example.test (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak OR filetype:7z)
site:*.example.test (filetype:zip OR filetype:tar OR filetype:sql OR filetype:bak)
```

Confirmá si cada resultado es intencionalmente público. Un solo hit aquí es un incidente.

### Buscá listados de directorio

```
site:example.test intitle:"index of"
site:*.example.test intitle:"index of" -github.com
```

Los listados de directorio son casi siempre accidentales.

### Buscá portales admin

```
site:*.example.test (inurl:admin OR inurl:manage OR inurl:dashboard OR inurl:console)
site:*.example.test (intitle:"login" OR intitle:"sign in")
```

Enrutá los hallazgos a [[admin-interface-discovery|admin interface discovery]].

### Buscá source maps y artefactos de build

```
site:*.example.test (filetype:map OR inurl:.map)
site:*.example.test (inurl:webpack OR inurl:dist OR inurl:build)
```

Los source maps revelan nombres de rutas, nombres de módulos internos y hosts de API. Eliminarlos de los builds de producción es una corrección de una línea en la config de build.

### Buscá páginas de error y output debug

```
site:*.example.test ("Whitelabel Error Page" OR "SQLSTATE" OR "Stack Trace")
site:*.example.test ("DEBUG" OR "Traceback (most recent call last)")
```

Las páginas de error filtran contexto de framework, base de datos y ruta interna.

### Buscá secretos indexados

```
site:*.example.test ("api_key" OR "AKIA" OR "-----BEGIN PRIVATE KEY-----")
```

Alta tasa de falsos positivos; triá cada hit antes de declararlo una exposición real.

## Ejemplos prácticos

- Una consulta para `filetype:sql` encuentra un backup `.sql` indexado en un subdominio dev olvidado.
- `intitle:"index of"` revela una página de autoindex que expone archivos de usuario cargados.
- Una página pública de error Whitelabel expone la versión de Spring Boot y rutas de paquetes internos.
- Un portal admin antiguo en `admin.legacy.example.com` aparece en resultados indexados mucho después de que el equipo que lo construyó se fue.
- Un source map de producción expone nombres de rutas y hostnames de API que nunca estuvieron en ninguna especificación pública.
- Un panel admin de impresora de vendor aparece en resultados `inurl:admin` porque nadie sabía que era accesible desde internet.

## Notas relacionadas

- [[search-engine-operators]]
- [[osint-triage]]
- [[breach-and-leak-intelligence]]
- [[exposed-storage|Exposed Storage]]
- [[admin-interface-discovery|Admin Interface Discovery]]
- [[passive-recon|Passive Recon]]

### Notas atómicas futuras sugeridas

- ghdb-workflow
- indexed-secret-exposure
- directory-listing-exposure
- source-map-exposure
- search-engine-deindexing
- defensive-dork-cadence

## Referencias

- **Docs Oficiales:** Exploit-DB Google Hacking Database — https://www.exploit-db.com/google-hacking-database
- **Docs Oficiales:** Google Search Help: refine searches — https://support.google.com/websearch/answer/2466433/refine-web-searches
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
