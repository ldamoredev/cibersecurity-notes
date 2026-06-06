# File Metadata Removal

## Definición

La eliminación de metadatos de archivos es el proceso de inspeccionar, reducir o limpiar datos descriptivos ocultos de los archivos antes de compartirlos, mientras se verifica que el output ya no contiene señales de identidad no deseadas.

## Por qué importa

Los archivos frecuentemente llevan más que el contenido visible. Las imágenes pueden incluir coordenadas GPS, modelo de cámara, timestamp y miniaturas. Los documentos pueden incluir nombres de autor, historial de edición, comentarios, archivos embebidos, nombres de software y trazas del sistema de archivos.

Los metadatos pueden desanonimizar a un usuario incluso cuando el archivo se subió a través de Tor, una VPN o un canal cifrado. La privacidad del transporte protege la ruta; no limpia el archivo.

## Cómo funciona

Usá el flujo de trabajo de metadatos de 5 pasos:

1.
**Inspeccionar**
   Leer los metadatos antes de compartir para que el riesgo sea visible.

2.
**Decidir**
   Determinar si el formato del archivo, el propósito y el destinatario requieren preservar algún metadato.

3.
**Limpiar o convertir**
   Limpiar metadatos con una herramienta o convertir a un formato más simple cuando sea apropiado.

4.
**Verificar**
   Inspeccionar el output limpiado. No asumir que la exportación o la captura de pantalla eliminaron todo.

5.
**Evitar la recontaminación**
   No embeber archivos limpiados en documentos sucios ni editar archivos limpiados con herramientas que añadan nuevos metadatos.

Ejemplo:

```
Imagen original:
  coordenadas GPS
  modelo de cámara
  timestamp
  software de edición

Imagen limpiada:
  sin GPS
  sin serial/modelo de cámara si no es necesario
  sin miniatura embebida
  sin campos de autor/comentario
```

El bug no es usar imágenes o documentos. El bug es compartirlos sin verificar qué más dicen.

## Técnicas / patrones

- Inspeccionar los metadatos con una herramienta dedicada antes de compartir.
- Preferir formatos más simples cuando el riesgo de metadatos es alto.
- Limpiar los archivos fuente antes de embeberlosen documentos más grandes.
- Verificar el output limpiado con una segunda inspección.
- Tratar PDFs, documentos Office, imágenes, audio, video y archivos comprimidos como diferentes clases de riesgo.
- Preservar originales por separado si la integridad de la evidencia importa.
- Considerar las capturas de pantalla y exportaciones como nuevos archivos con sus propios metadatos.

## Variantes y bypasses

Usá las 7 familias de metadatos:

### 1. EXIF y metadatos de media

Las fotos y videos pueden incluir GPS, modelo del dispositivo, lente, timestamp, orientación, número de serie y miniaturas embebidas.

### 2. Metadatos de autor de documentos

Los archivos Office y PDF pueden incluir nombres de autor, organización, rutas de template, comentarios, cambios rastreados, números de revisión y nombres de aplicación.

### 3. Metadatos de objetos embebidos

Un documento de aspecto limpio puede contener imágenes, audio, hojas de cálculo o PDFs embebidos que aún llevan sus propios metadatos.

### 4. Metadatos de sistema de archivos y archivos comprimidos

Los archivos comprimidos pueden preservar nombres de archivo, rutas, nombres de usuario, permisos, timestamps y estructura de directorios.

### 5. Metadatos añadidos por aplicaciones

Las herramientas de edición, scanners, apps de teléfono, drives en la nube y pipelines de exportación pueden añadir nuevos metadatos después de limpiar.

### 6. Metadatos visuales

Los detalles del fondo visible, reflejos, notificaciones, idioma, títulos de ventanas y rutas de archivos pueden revelar identidad incluso cuando se eliminan los metadatos técnicos.

### 7. Conflictos de preservación de evidencia

Para respuesta a incidentes, periodismo o trabajo legal, los metadatos pueden ser evidencia. Limpiar un archivo antes de preservar un original puede destruir contexto útil.

## Impacto

- Exposición de ubicación, dispositivo, empleador, software, nombre de usuario o línea de tiempo.
- Vinculación entre publicación seudónima e identidad del mundo real.
- Fuga de rutas internas de documentos, nombres de organización, comentarios o historial de edición.
- Falsa confianza cuando la privacidad del transporte oculta la ruta de subida pero el archivo revela la fuente.
- Pérdida de evidencia cuando los metadatos se limpian antes de preservar un original.

## Detección y defensa

Ordenado por efectividad:

1.
**Inspeccionar antes de compartir**
   El riesgo de metadatos debe ser visible antes de poder gestionarlo. La inspección es el primer control.

2.
**Preservar los originales cuando importa la evidencia**
   Guardar una copia intacta si el archivo puede ser evidencia. Trabajar en un duplicado para limpiar.

3.
**Usar herramientas dedicadas de limpieza de metadatos**
   Herramientas como ExifTool o Metadata Cleaner/mat2 están diseñadas para esta tarea. Los flujos de trabajo de exportación genéricos son menos confiables.

4.
**Verificar el output limpiado**
   Volver a ejecutar la inspección en el archivo limpiado. El paso de verificación detecta limitaciones de formato y errores de la herramienta.

5.
**Preferir formatos más simples cuando sea posible**
   El texto plano y las imágenes simples frecuentemente llevan menos metadatos complejos que los documentos Office, gráficos por capas o PDFs.

6.
**Revisar el contenido visible por separado**
   Eliminar los metadatos técnicos no elimina reflejos, fondos, nombres de usuario, notificaciones, estilo de escritura o timestamps mostrados en el contenido.

### Qué no funciona como defensa primaria

- **Renombrar un archivo no elimina metadatos.** Los campos ocultos permanecen.
- **Recortar o editar no garantiza la limpieza.** Los editores pueden preservar o añadir metadatos.
- **Subir a través de una VPN o Tor no limpia el archivo.** La ruta y el payload son separados.
- **Las capturas de pantalla no son automáticamente seguras.** Pueden revelar contexto visible y pueden incluir nuevos metadatos.
- **Una sola herramienta no puede limpiar de forma confiable todos los formatos complejos.** Los documentos complejos pueden contener archivos embebidos con sus propios metadatos.

## Labs prácticos

### Inspeccionar una imagen

```
exiftool sample.jpg
```

Buscar GPS, timestamp, modelo de cámara, números de serie, software, miniaturas y comentarios.

### Limpiar metadatos de imagen y verificar

```
cp sample.jpg sample-clean.jpg
exiftool -all= sample-clean.jpg
exiftool sample-clean.jpg
```

El segundo comando es el control. Sin verificación, sin confianza.

### Inspeccionar un documento

```
exiftool document.pdf
exiftool document.docx
```

Verificar campos de autor, creador, productor, revisión, template y timestamp.

### Limpiar con mat2 donde esté disponible

```
mat2 file.ext
exiftool file.cleaned.ext
```

Usar el output limpiado, no el original. Verificar porque el soporte de formato difiere.

### Construir una lista de verificación para compartir

```
Archivo:
Original preservado:
Contenido visible revisado:
Metadatos inspeccionados:
Herramienta de limpieza usada:
Output limpiado verificado:
Destinatario/contexto:
Riesgo residual:
Decisión:
```

La lista conecta la limpieza técnica con la decisión real de compartir.

## Ejemplos prácticos

- Una foto compartida bajo seudónimo incluye coordenadas GPS de la cámara del teléfono.
- Un PDF incluye el nombre de usuario real del autor del SO en el campo creador.
- Un informe de aspecto limpio embebe una imagen que aún tiene metadatos de cámara.
- Un archivo ZIP preserva una ruta de proyecto local con un empleador o nombre de usuario.
- Una captura de pantalla oculta el EXIF pero visiblemente muestra un nombre de perfil del browser y notificación.

## Notas relacionadas

- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[secure-file-sharing|Secure File Sharing]]
- [[secure-deletion-and-storage-wiping|Secure Deletion and Storage Wiping]]

## Referencias

- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/
- **Docs Oficiales:** Tails: Removing metadata from files - https://tails.net/doc/sensitive_documents/metadata/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
