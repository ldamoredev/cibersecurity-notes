# Exposed Storage

## Definición

El exposed storage es cualquier superficie de almacenamiento de archivos, objetos, artefactos, backups, logs o documentos que sea alcanzable más allá de su audiencia prevista a través de acceso público, política débil, rutas predecibles, confianza heredada o publicación olvidada.

## Por qué importa

La exposición de almacenamiento a menudo se convierte en una filtración silenciosa de datos en lugar de un exploit dramático. Los backups, logs, source maps, artefactos CI, carpetas de upload, screenshots, exportaciones y documentos internos son fáciles de publicar y difíciles de gobernar.

Mantené la distinción con [[file-upload-abuse|File Upload Abuse]]: esa nota es sobre la lógica de aplicación que acepta archivos; esta nota es sobre el almacenamiento como superficie de ataque expuesta.

## Cómo funciona

El exposed storage tiene **5 superficies de almacenamiento**:

1. **Almacenamiento de objetos.** Buckets S3, Azure Blob, buckets GCS, objetos backed por CDN.
2. **Archivos servidos por web.** Uploads, directorios estáticos, backups, logs, source maps y exportaciones.
3. **Artefactos de build y release.** Outputs CI, paquetes, capas de contenedor, símbolos y bundles.
4. **Documentos e informes.** PDFs, hojas de cálculo, screenshots, docs internos y adjuntos de soporte.
5. **Índices y listados.** Directory listing, bucket listing, indexación por buscadores y nombres de archivo predecibles.

El bug no es que los archivos estén hosted. Es que el modelo de acceso no coincide con la sensibilidad y el ciclo de vida del contenido almacenado.

Un ejemplo trabajado, de archivo público a decisión de exposición:

```
URL:
  https://cdn.example.test/releases/app.js.map

Contenido:
  rutas de fuente, constantes de rutas API, comentarios, sin secretos activos

Sensibilidad:
  divulgación de implementación y endpoints

Pista de confianza/ciclo de vida:
  artefacto generado por build de producción, no un backup olvidado

Decisión:
  exposición media: eliminar source maps públicos o publicar intencionalmente con revisión;
  dar seguimiento a las rutas descubiertas del mapa
```

El mismo hecho de public-read puede ser bajo, medio o crítico dependiendo del contenido, propietario y confianza downstream.

## Técnicas / patrones

Los profesionales buscan:

- buckets, containers y rutas CDN públicos
- directory listing y nombres de backup predecibles
- `.map`, `.bak`, `.old`, `.zip`, `.tar.gz`, `.sql`, `.env`, `.log`
- artefactos CI/CD enlazados desde jobs públicos
- archivos subidos accesibles sin autorización
- documentos indexados por buscadores y archivos en caché
- almacenamiento obsoleto vinculado a entornos o vendors viejos

## Variantes y bypasses

El exposed storage aparece en **7 formas**.

### 1. Bucket público no intencionado

La política del bucket permite lectura o listado público de forma no intencional.

### 2. Backups y archivos predecibles

Los backups, dumps o archivos se sirven desde URLs adivinables.

### 3. Artefactos de frontend expuestos

Los artefactos frontend revelan rutas, secretos, nombres internos o estructura de código fuente.

### 4. Autorización de upload sin descarga

Los archivos requieren auth para subir pero no para descargar.

### 5. Artefactos CI y de build expuestos

Los logs de build, paquetes, screenshots, informes o outputs de test son públicamente alcanzables.

### 6. Exposición por indexación de buscadores

Los archivos sensibles se vuelven descubribles a través de búsqueda o páginas en caché.

### 7. Almacenamiento de entorno obsoleto

El almacenamiento viejo permanece después de una migración, offboarding o teardown de entorno.

## Impacto

Ordenado aproximadamente por severidad:

- **Filtración de credenciales o secretos.** Logs, `.env`, source maps o artefactos exponen tokens y claves.
- **Divulgación de datos sensibles.** Datos de clientes, documentos, informes y exportaciones se filtran.
- **Divulgación de fuente y rutas.** Los bundles y maps revelan endpoints ocultos y detalles de implementación.
- **Riesgo de supply chain.** Los artefactos públicos pueden exponer el proceso de build o metadatos de paquetes.
- **Riesgo de marca y compliance.** Los documentos y backups públicos crean exposición de larga duración.

## Detección y defensa

Ordenado por efectividad:

1.
**Clasificás el almacenamiento por sensibilidad y audiencia prevista.**
   El contenido público y los artefactos privados deberían vivir en diferentes buckets, políticas y flujos de revisión.

2.
**Denegás el acceso público por defecto.**
   La lectura pública debería ser una excepción explícita, no heredada de defaults convenientes.

3.
**Vinculás el ciclo de vida del almacenamiento al ciclo de vida de la aplicación y el entorno.**
   Retirar una app debería retirar los buckets, rutas CDN, artefactos y referencias DNS.

4.
**Escaneás en busca de extensiones riesgosas, source maps y listados.**
   Los chequeos automatizados capturan exposiciones accidentales comunes antes que los atacantes.

5.
**Autorizás la recuperación de archivos, no solo el upload.**
   Los uploads privados necesitan chequeos de acceso en el momento de descarga y previsualización.

6.
**Logueás y monitoreás el acceso a objetos.**
   Las lecturas de objetos públicos y los picos inusuales de descarga deberían ser visibles.

### Qué no funciona como defensa primaria

- **URLs no enlazadas.** Las búsquedas, logs, referrers, wordlists y nombres predecibles revelan archivos.
- **Solo nombres de archivo aleatorios.** La entropía ayuda pero no reemplaza el control de acceso.
- **Nombres de bucket como secretos.** Los nombres de bucket y las rutas CDN se filtran a través de tráfico y docs.
- **Limpieza única.** La deriva de almacenamiento sigue a cada build, exportación y cambio de entorno.

## Labs prácticos

Usá activos propios.

### Auditá extensiones riesgosas

```
rg -n "\\.(map|bak|old|zip|tar\\.gz|sql|env|log)$" public dist docs
```

Decidí si cada archivo es intencionalmente público.

### Verificá el acceso a source maps

```
curl -I https://app.example.test/static/app.js.map
```

Los source maps pueden revelar fuente y rutas incluso sin secretos.

### Testéa la autorización de descarga de archivos

```
curl -i -H "Authorization: Bearer $USER_A" https://app.example.test/files/123
curl -i -H "Authorization: Bearer $USER_B" https://app.example.test/files/123
```

El usuario B no debería poder recuperar el archivo privado del usuario A.

### Verificá el directory listing

```
curl -i https://storage.example.test/
```

Los listados y responses de índice XML merecen revisión.

### Construí una tabla de clasificación de archivos

```
archivo | fuente | ¿público? | clase de datos | ¿secretos? | propietario | eliminar/mantener | seguimiento
```

La clasificación evita tratar un logo, un source map y un dump de base de datos como el mismo tipo de exposición.

### Buscá exposición con dorks

```
site:example.test filetype:pdf internal
site:example.test filetype:xls OR filetype:xlsx
site:example.test inurl:backup OR inurl:export
```

Usá los resultados de búsqueda como pistas; verificá el acceso y la sensibilidad antes de escalar.

## Ejemplos prácticos

- Un bucket público expone artefactos de build o source maps.
- Los archivos subidos son públicamente accesibles aunque deberían ser privados.
- Un archivo de backup es alcanzable por una URL predecible.
- Los logs CI exponen variables de entorno.
- El almacenamiento de staging viejo permanece público después de que la app es eliminada.

## Notas relacionadas

- [[file-upload-abuse|File Upload Abuse]]
- [[external-attack-surface]]
- [[deprecated-api-versions]]
- [[third-party-exposure]]
- [[secrets-management|Secrets Management]]

### Notas atómicas futuras sugeridas

- source-map-exposure
- public-bucket-review
- predictable-backup-files
- ci-artifact-exposure
- file-download-authorization

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
