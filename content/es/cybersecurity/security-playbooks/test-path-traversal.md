# Test Path Traversal

## Objetivo

Determinar si input de usuario puede escapar el límite de path de filesystem previsto y acceder a archivos o directorios inesperados.

## Supuestos

- la app lee o escribe archivos basados en identificadores controlados por usuario
- la normalización de path puede estar incompleta
- separadores o encodings específicos de plataforma pueden importar

## Prerrequisitos

- endpoints relacionados con archivos o features de upload/extracción
- capacidad de hacer replay de requests y comparar responses

## Pasos de recon

1. Identificá features de download, preview, importación, extracción y templates.
2. Mapeá dónde aparece input tipo path en rutas, params o JSON.
3. Notá comportamiento de OS/plataforma donde sea relevante.

## Pasos de exploit / testing

1. Probá secuencias simples de traversal.
2. Testeá variantes encoded o separadores alternativos cuando corresponda.
3. Compará comportamiento para operaciones de lectura y escritura.
4. Probá workflows de archive extraction o upload por escape de directorio.
5. Observá si la normalización ocurre antes o después de la validación.

## Señales de validación

- acceso a archivos inesperados
- errores distintos al escapar directorios previstos
- escrituras o extracciones caen fuera de paths controlados

## Mitigación

- evitar paths de filesystem raw controlados por usuario
- usar referencias indirectas o allowlists estrictas
- canonicalizar de forma segura y verificar paths finales
- aislar cuentas/directorios de processing y storage

## Logging / detección

- strings repetidos con forma de traversal
- accesos fallidos a archivos fuera de árboles esperados
- intentos de extracción o escritura fuera de áreas de upload

## Notas relacionadas

- [[path-traversal|Path Traversal]]
- [[file-upload-abuse|Abuso de file upload]]
- [[http-messages|Mensajes HTTP]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Testing / Lab:** PortSwigger path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
