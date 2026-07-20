# Inspect File Upload Surface

## Objetivo

Determinar si las features de upload crean paths inseguros de ejecución, storage, parser o exposición.

## Supuestos

- los uploads pueden estar validados débilmente
- el post-processing suele ser más riesgoso que el upload en sí
- los paths de storage y serving pueden cruzar trust boundaries

## Prerrequisitos

- una o más features de upload o importación
- capacidad de inspeccionar storage, comportamiento de response o efectos laterales del processing donde esté autorizado

## Pasos de recon

1. Mapeá todos los puntos de entrada de upload e importación.
2. Identificá dónde se almacenan, transforman, previewean o sirven los archivos.
3. Notá extensiones permitidas, manejo MIME, naming y exposición pública.

## Pasos de exploit / testing

1. Compará checks de extensión contra comportamiento real del parser.
2. Testeá si el contenido subido se sirve desde contextos ejecutables o demasiado confiables.
3. Probá paths de processing de archives y documentos.
4. Inspeccioná manejo de filename y supuestos de path.
5. Buscá URLs públicas predecibles o exposición indirecta de archivos almacenados.

## Señales de validación

- tipos de archivo inseguros son aceptados o mal manejados
- contenido subido se vuelve públicamente alcanzable de forma inesperada
- el path de processing revela issues de parser o storage
- los archivos pueden influir en rendering downstream o comportamiento del servidor

## Mitigación

- validar más que solo la extensión
- aislar paths de storage y serving
- evitar contextos con capacidad de ejecución
- revisar previews/transforms como parte de la superficie de ataque
- usar referencias indirectas y naming seguro

## Logging / detección

- combinaciones MIME/tipo de upload inusuales
- intentos repetidos de processing fallido
- acceso público a archivos que deberían permanecer privados

## Notas relacionadas

- [[file-upload-abuse|Abuso de file upload]]
- [[path-traversal|Path Traversal]]
- [[xss|Cross-Site Scripting (XSS)]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
