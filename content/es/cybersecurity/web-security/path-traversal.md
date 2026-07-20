---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - path-traversal
sources: []
---

# Path traversal

## Definición
El path traversal ocurre cuando un input controlado por el atacante influye en un path del sistema de archivos de una forma que permite acceder fuera de la frontera de directorio prevista.

## Por qué importa
Esta vulnerabilidad es un ejemplo limpio de confianza insegura entre el input del usuario y recursos sensibles del lado del servidor. A menudo parece simple, pero su profundidad real aparece en:
- la normalización de paths
- los separadores específicos del SO
- el URL encoding
- la extracción de archivos comprimidos
- los patrones de acceso indirecto a archivos
- las diferencias entre el path de validación y la resolución real del sistema de archivos

## Cómo funciona
El mecanismo es:

1. la aplicación toma input controlado por el atacante
2. ese input se usa para construir o resolver un path del sistema de archivos
3. la aplicación no logra restringir el path final resuelto a un directorio base previsto

Patrón vulnerable típico:

```js
const fullPath = baseDir + "/" + userInput
```

Si `userInput` es:
```txt
../../etc/passwd
```

el path resuelto escapa del directorio previsto.

El problema central no es meramente el string `../`.
El problema central es no controlar la resolución final del path.

## Técnicas / patrones
Los atacantes miran:
- endpoints de download
- endpoints de preview de archivos
- handlers de import/export
- mecanismos de template/include
- recuperación de documentos/imágenes
- extracción de archivos comprimidos
- flujos de subir-y-después-leer
- caminos de recuperación de logs, backups o support bundles

Tests típicos:
- secuencias de traversal relativo
- traversal codificado
- separadores alternativos
- patrones de normalización mezclados
- intentos de path absoluto
- comportamiento de path específico de plataforma

## Variantes y bypasses

### Traversal relativo clásico
Usar `../` o equivalente para salir del directorio previsto.

### Traversal basado en encoding
Bypassea la validación que chequea el input crudo pero no la forma decodificada/normalizada.

### Diferencias de separador
Las semánticas de path de Unix y Windows difieren, y las aplicaciones a veces normalizan uno pero no el otro.

### Acceso por path absoluto
A veces la app acepta paths absolutos directos o puede ser engañada para usarlos.

### Extracción de archivos / paths estilo zip-slip
Una familia de traversal especial y muy práctica donde las entradas de un archivo comprimido extraído escapan del directorio destino.

### Construcción indirecta de path
La app puede parecer usar identificadores seguros, pero luego los transforma en paths de forma insegura.

### Malentendidos sobre allowlists
Los equipos a menudo validan "contiene solo chars seguros" pero igual no logran imponer las fronteras de directorio sobre el path canónico final.

## Impacto
Impacto típico:
- leer archivos sensibles
- exponer config, claves, tokens o archivos de entorno
- acceder a templates internos o código fuente
- sobrescribir archivos en algunos casos con capacidad de escritura
- pivotar a un compromiso más amplio si hay datos sensibles del host alcanzables

El impacto es más alto cuando el traversal alcanza:
- secretos
- configs
- código fuente
- credenciales
- artefactos de deploy
- archivos solo-internos usados luego por procesos confiables

## Detección y defensa
Ordenado por efectividad:

1. **No construyas paths crudos del sistema de archivos a partir del input del atacante**
   Usá referencias indirectas o capas de lookup seguras.

2. **Restringí el path canónico final**
   Validá después de la normalización/canonicalización que el path final resuelto quede dentro del directorio base previsto.

3. **Usá allowlists explícitas**
   Permití solo nombres de archivo o identificadores known-safe donde sea posible.

4. **Separá con cuidado las zonas de lectura/escritura/extracción**
   Distintos niveles de confianza no deberían compartir los mismos supuestos de manejo de archivos.

5. **Revisá la lógica de extracción de archivos**
   Los paths de extracción de zip/tar son una falla común de frontera-de-path.

6. **Usá mínimo privilegio en los procesos que acceden a archivos**
   Aunque exista el traversal, privilegios de proceso/archivo más bajos pueden reducir el impacto.

7. **Monitoreo**
   Vigilá:
   - strings de path tipo-traversal
   - fallas inesperadas de acceso a archivos fuera de los dirs de la app
   - recuperación anormal de archivos sensibles del host
   - paths de extracción sospechosos

## Ejemplos prácticos
- endpoint de download de archivos vulnerable a escape de path `../../`
- extracción de archivo que escribe fuera del directorio de subida previsto
- preview de template o generador de reportes leyendo archivos arbitrarios
- mecanismo de download de support/log que confía demasiado en un nombre de archivo provisto por el usuario

## Notas relacionadas
- [[file-upload-abuse|Abuso de subida de archivos]]
- [[http-messages|Mensajes HTTP]]
- [[exposed-storage|Almacenamiento expuesto]]
- [[cybersecurity/security-playbooks/test-path-traversal|Testear path traversal]]

### Notas atómicas futuras sugeridas
- [[zip-slip|Zip slip]]
- [[path-canonicalization-pitfalls|Trampas de canonicalización de paths]]

## Referencias
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Research / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability
