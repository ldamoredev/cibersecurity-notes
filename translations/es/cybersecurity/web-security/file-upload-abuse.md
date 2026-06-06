# File Upload Abuse

## Definición

File upload abuse ocurre cuando una aplicación acepta, almacena, transforma o sirve archivos subidos de maneras que permiten que el contenido controlado por el atacante cruce límites de confianza de forma insegura.

## Por qué importa

Las subidas son una de las superficies de ataque más ricas en aplicaciones modernas porque frecuentemente pasan a través de muchas capas:
- navegador
- validación de la app
- almacenamiento
- pipelines de procesamiento
- funcionalidades de preview/renderizado
- consumidores downstream

El riesgo no es solo subir un script. Es cualquier ruta donde el contenido subido gana más confianza, accesibilidad o influencia en la ejecución de lo previsto.

## Cómo funciona

El mecanismo suele ser:
1. el atacante provee un archivo o payload similar a un archivo
2. la aplicación valida débilmente o solo superficialmente
3. el archivo se almacena, transforma o sirve en un contexto peligroso
4. el contenido subido influye en la ejecución, el renderizado, el parsing o la exposición

## Técnicas / patrones

Los atacantes generalmente testean:
- validación de extensión
- verificaciones de MIME/content-type
- comportamiento del parser vs tipo de archivo declarado
- funcionalidades de preview de imagen/documento
- exposición pública directa de almacenamiento
- manejo de nombre de archivo y ruta
- extracción de archivos comprimidos
- formatos con capacidad de SVG/HTML/script
- subida seguida de renderizado dentro de un origen de confianza

## Variantes y bypasses

### Mismatch de extensión / MIME

La app confía en la extensión o el content-type declarado más que en el comportamiento real del parser.

### Abuso de almacenamiento público

El contenido subido se vuelve accesible desde una ruta o bucket público inesperadamente.

### Subida de contenido activo

Los formatos interpretados por el navegador como SVG, HTML u otros se vuelven peligrosos cuando se sirven inline o desde un origen de confianza.

### Explotación del parser

El riesgo viene del componente que lee el archivo más tarde, no de la subida en sí.

### Abuso de archivo comprimido / archivo anidado

Los archivos comprimidos pueden ocultar contenido peligroso o desencadenar path traversal durante la extracción.

### Problemas de manejo de nombre de archivo y ruta

La lógica de subida puede combinarse con path traversal, riesgo de sobreescritura, o acceso predecible a archivos.

## Impacto

Impacto típico:
- XSS almacenado
- efectos secundarios de path traversal o sobreescritura
- exposición de archivos sensibles
- compromiso downstream disparado por el parser
- contenido persistente controlado por el atacante bajo un origen de confianza

## Detección y defensa

Ordenado por efectividad:

1.
**Separar claramente el almacenamiento público y privado**
   El contenido subido vive en una zona de confianza diferente al código de la app y a la configuración. Mantenerlo en un bucket o ruta dedicada que no pueda traversarse hacia el árbol fuente de la app, y servirlo desde un origen diferente (o al menos desde un scope de cookie diferente) para que una subida maliciosa no pueda montarse sobre la sesión de la app.

2.
**Validar más allá de la extensión**
   La extensión y el `Content-Type` son controlados por el atacante. Validar parseando — confirmar que una "imagen" realmente se decodifica como ese formato de imagen, confirmar que un "PDF" tiene los magic bytes y la estructura correctos. Rechazar ante falla de parseo en lugar de intentar reparar.

3.
**Re-encodear el contenido del usuario donde el formato lo permite**
   Para imágenes, re-encodear a través de una librería segura (descartar EXIF, descartar scripts embebidos, descartar payloads políglotas). Para documentos, renderizar a un formato seguro si es que el renderizado es necesario. La re-encodificación elimina la mayoría de los ataques de políglotas y trucos de parsers en el límite.

4.
**Servir el contenido activo de forma segura**
   Los formatos interpretados por el navegador (SVG, HTML, XML) se convierten en vectores de XSS cuando se sirven inline desde un origen de confianza. Servirlos con `Content-Disposition: attachment`, desde un origen sandbox, o detrás de un CSP estricto. Mejor aún: convertir SVG a raster al subir si el renderizado inline no es crítico.

5.
**Tratar los pipelines de procesamiento como parte de la superficie de ataque**
   ImageMagick, Ghostscript, ffmpeg, libreoffice, parsers de PDF — cada procesador es un parser, y los parsers tienen CVEs. Fijar versiones, monitorear advisories, y ejecutar el procesamiento en un sandbox (proceso separado, privilegios reducidos, sin red) para que un RCE del parser no se convierta en un compromiso de la app.

6.
**Usar naming y manejo de ruta seguros**
   Nunca dejar que un nombre de archivo provisto por el usuario llegue al sistema de archivos sin cambios. Generar un identificador del lado del servidor, almacenar el nombre original solo como metadato, y rechazar separadores de ruta y secuencias de traversal antes de cualquier llamada al sistema de archivos. Esto elimina tanto los bugs de sobreescritura como los de traversal-en-escritura.

7.
**Revisar cuidadosamente el manejo de archivos comprimidos**
   Los archivos Zip, tar y similares pueden llevar secuencias de traversal y rutas absolutas en sus entradas (Zip Slip, tar slip). Validar la ruta resuelta de cada entrada extraída contra el directorio base previsto *después* de la canonicalización, no antes.

8.
**Monitorear**
   Estar atento a: subidas con extensión y tipo parseado no coincidentes, patrones repetidos de subida-y-fetch desde el mismo actor, tipos de archivo inesperados en el almacenamiento, y errores del parser agrupados alrededor de un pequeño conjunto de archivos.

## Ejemplos prácticos

- un SVG subido se vuelve ejecutable cuando se sirve inline
- una subida de imagen acepta contenido que luego desencadena XSS almacenado en la revisión del admin
- la extracción de un archivo comprimido escribe archivos fuera del directorio de subida previsto
- un archivo subido se vuelve públicamente accesible aunque el producto asume que es privado

## Notas relacionadas

- [[path-traversal]]
- [[xss]]
- [[exposed-storage]]
- [[inspect-file-upload-surface|Inspect File Upload Surface]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Investigación / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability
