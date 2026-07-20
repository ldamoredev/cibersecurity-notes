# PHAR Deserialization

## Definición

La deserialización PHAR es una clase de vulnerabilidad específica de PHP donde cualquier operación del sistema de archivos que acepte un stream `phar://` implícitamente deserializa los metadatos del archivo PHAR — invocando métodos mágicos (`__wakeup`, `__destruct`) en cualquier objeto almacenado en esos metadatos, sin ninguna llamada a `unserialize()`.

## Por qué importa

Este es el vector de deserialización más subestimado en PHP porque la cadena de explotación no parece una deserialización:

- La "subida" y la "operación del sistema de archivos" son primitivos de funcionalidades separados que muchos threat models tratan como aislados.
- El trigger puede estar completamente en código de librería de terceros — la aplicación propia no llama a nada relacionado con serialización.
- Más de 50 funciones PHP nativas pueden actuar como triggers, muchas de las cuales se usan en comprobaciones de validación de entrada completamente inócuas (`file_exists`, `getimagesize`).
- La divulgación de Sam Thomas en Black Hat USA 2018 cambió el threat model de "subida de archivo" de forma permanente. Antes de ella, el consenso era que una subida sin ejecución directa estaba contenida. Después de ella, cualquier ruta de código que toca archivos subidos es potencialmente un trigger de deserialización.

## Cómo funciona

PHP Archive (PHAR) es un formato de empaquetado de PHP (análogo a JAR de Java). Un archivo PHAR contiene:
1. Un stub (código PHP ejecutable con `<?php ... __HALT_COMPILER();`)
2. Un manifiesto (metadatos serializados con PHP)
3. Los archivos contenidos
4. Una firma opcional

El manifiesto se **deserializa** (usando `unserialize` internamente) cada vez que PHP abre el archivo a través del wrapper de stream `phar://`. No importa qué función PHP realiza la apertura.

Cualquier objeto en el manifiesto cuyos métodos mágicos hagan algo peligroso con sus propiedades serializadas actúa como kick-off de gadget chain — exactamente igual que si `unserialize()` se hubiera llamado explícitamente.

Cadena de explotación completa:

1. **Construir** un PHAR con un manifiesto que contenga un objeto de gadget chain serializado (usando PHPGGC u objetos artesanales).
2. **Disfrazar** el PHAR como un tipo de archivo aceptado (JPEG, GIF, PDF, ZIP) para pasar la validación de subidas — los archivos PHAR políglotas comienzan con bytes mágicos válidos del formato objetivo.
3. **Subir** el polígloita vía cualquier funcionalidad de subida de archivo que no desnaturalice el contenido.
4. **Disparar** cualquier ruta de código que llame a una función sensible al sistema de archivos en el path del archivo con un stream `phar://`.

El trigger no requiere que la aplicación "ejecute" el archivo. Solo requiere que la aplicación *mencione el archivo* en una llamada a función PHP que soporte wrappers de stream.

## Técnicas / patrones

### Identificar la superficie de trigger

El primer paso es identificar dónde el código de la aplicación llama a funciones del sistema de archivos con input derivado del usuario (IDs de upload, nombres de archivo en base de datos, paths en parámetros de query):

```php
file_exists($path)
is_file($path)
file_get_contents($path)
fopen($path, 'r')
getimagesize($path)
imagecreatefromjpeg($path)
```

Más de 50 funciones nativas PHP soportan wrappers de stream. Una búsqueda de grep para `file_exists\|fopen\|getimagesize\|imagecreatefrom` en rutas de código que usan input del sistema de archivos encontrará los candidatos.

### Construir el polígloita PHAR

Las herramientas automatizan esto:
- **PHPGGC** — genera objetos de gadget chain serializados apropiados para el framework de la aplicación, con soporte integrado para generación de archivos PHAR y políglotas (JPEG, GIF, PNG, PDF, ZIP).

Construcción manual: el archivo debe comenzar con los magic bytes del formato objetivo (por ejemplo, `FFD8FF` para JPEG) antes de cualquier stub PHAR, para que tanto el parser de imagen como el wrapper PHAR lo acepten.

### Disparar la deserialización

El trigger más común en aplicaciones del mundo real es una ruta de procesamiento de imágenes:

```php
// Validación de "seguridad" que es en sí misma el trigger
if (getimagesize("uploads/" . $filename)) {
    // ...
}
```

Pasar `phar://uploads/avatar.jpg` (o controlar el valor de `$filename` hacia `phar://...`) dispara la deserialización durante la llamada a `getimagesize`.

En aplicaciones donde el path viene de la base de datos o de otro almacenamiento, el atacante puede no controlar directamente el argumento del stream. El vector secundario son las funcionalidades de "preview" o "thumbnail" que leen archivos subidos usando el ID como parte del path.

## Variantes y bypasses

### Confusión de `phar.readonly`

La INI `phar.readonly = On` (valor por defecto) previene **crear** archivos PHAR con `PharData` — pero no previene **leer** o **disparar** archivos PHAR existentes vía el wrapper de stream `phar://`. Los equipos a veces asumen que `phar.readonly` mitiga los ataques PHAR; no lo hace.

### PHAR como JPEG / GIF / PDF / ZIP polígloita

Los formatos de imagen/documento más comunes tienen firmas de cabecera o áreas de comentarios que pueden coexistir con el stub PHAR:
- **GIF** — `GIF89a` seguido del stub PHAR antes del fin de cabecera es la variante más confiable.
- **JPEG** — los datos JFIF permiten datos arbitrarios después de los magic bytes iniciales.
- **PDF** — el `%PDF-1.x` puede preceder al stub en muchos parsers.
- **ZIP** — dado que PHAR puede empaquetarse como ZIP, los PHARs legítimos basados en ZIP tienen firmas de ZIP.

### Trigger a través de librerías de terceros

La cadena `file_exists → phar deserialize` puede estar enteramente dentro de una librería de terceros (un SDK de procesamiento de imágenes, un wrapper de almacenamiento de archivos, un ORM que valida adjuntos). La aplicación ni siquiera necesita llamar a funciones del sistema de archivos directamente.

### Inyección de wrapper de stream

En algunos casos, el atacante puede controlar el prefijo del path o el wrapper de stream completo a través de path traversal, manipulación de configuración, o configuración insegura (por ejemplo, `allow_url_fopen`).

### Eludir `stream_wrapper_unregister`

Las aplicaciones que intentan desregistrar el wrapper `phar://` como defensa a veces solo lo hacen al inicio, y las librerías o plugins pueden volver a registrarlo. La unregistration también falla si se ejecuta después de que cualquier carga de clase de autoloader haya resuelto archivos usando el wrapper.

## Impacto

- **Ejecución remota de código** — el gadget sink alcanza `exec`/`eval`/`proc_open`/equivalente. Techo por defecto cuando hay una gadget chain viable en el framework de la aplicación.
- **Lectura / escritura arbitraria de archivos** — los sinks de gadget chain que no alcanzan RCE completo aún pueden alcanzar ops de filesystem.
- **SSRF** — gadget chains con sinks de network request (Guzzle, Curl wrappers).
- **Escalada de privilegios / bypass de auth** — gadget chains que modifican estado de sesión o permisos.

El daño directo de la sola subida sin trigger de sistema de archivos es cero. El impacto viene del trigger.

## Detección y defensa

Ordenado por efectividad:

1.
**Nunca pasar paths controlados por el usuario directamente a funciones del sistema de archivos.**
   Si el path que llega a `file_exists`, `getimagesize`, `fopen`, etc. puede ser influenciado por el atacante (directamente o vía IDs almacenados en base de datos derivados de input del usuario), esa es la vulnerabilidad. Canonicalizar y validar contra una allowlist de directorio base antes de cualquier llamada al sistema de archivos.

2.
**Re-encodear o desnaturalizar archivos subidos en el momento de la subida.**
   Re-encodear imágenes a través de la librería de imágenes (GD, Imagick en modo de re-renderizado) descarta los bytes del stub PHAR y destruye cualquier polígloita. Hacer esto durante la subida, antes de que el archivo alcance almacenamiento permanente. No re-encodear después del almacenamiento — el trigger puede ocurrir antes del procesamiento.

3.
**Validar con magia de bytes y parseo, no con extensión.**
   Verificar que el contenido real del archivo coincide con el tipo declarado usando parseo real (no solo lectura de los primeros bytes, sino decodificación completa). Un JPEG válido que se decodifica como imagen no contiene un stub PHAR viable.

4.
**Desregistrar el wrapper de stream `phar://` si la aplicación no usa PHARs.**
   `stream_wrapper_unregister('phar')` al inicio del ciclo de request previene que cualquier ruta de código en el request use wrappers PHAR. Hacer esto temprano, antes de cargar plugins o librerías que puedan re-registrarlo. Esta es una defensa en profundidad útil, no una defensa primaria.

5.
**Almacenar archivos subidos en una ubicación sin path traversal al código de la aplicación.**
   Usar un bucket de storage separado, filesystem, o prefijo de directorio que no pueda resolverse de vuelta al árbol fuente de la app o al almacenamiento de configuración.

6.
**Auditar paths de archivos que llegan a funciones PHP del sistema de archivos.**
   Instrumentar o revisar estáticamente todas las rutas de código donde el input del usuario (incluyendo IDs almacenados en base de datos) puede influenciar argumentos de funciones del sistema de archivos. Esta es la superficie de ataque real — no los endpoints de subida.

### Qué no funciona como defensa primaria

- **`phar.readonly = On`** — previene crear PHARs, no disparar PHARs existentes vía stream.
- **Validación de extensión solamente** — los polígloitas pasan la validación de extensión por diseño.
- **Verificación de MIME/Content-Type solamente** — el Content-Type es controlado por el atacante; el MIME detectado por magic bytes puede confundirse con el inicio del archivo que es válido para el tipo objetivo.
- **Solo almacenar fuera del webroot** — el trigger no requiere ejecución HTTP directa. Requiere cualquier llamada al sistema de archivos PHP en el path del archivo.

## Ejemplos prácticos

- Un campo de avatar acepta JPEGs; la app llama a `getimagesize("uploads/" . $id)` para generar thumbnails. El atacante sube un PHAR polígloita disfrazado de JPEG. El ID queda en la base de datos. La próxima vez que se llame a `getimagesize` en ese path, la gadget chain del manifiesto PHAR se deserializa y el `__destruct` de Monolog alcanza `proc_open`.
- Una app de gestión de documentos almacena paths de archivo en la base de datos y los pasa a `file_exists` para validación. La ruta puede comenzar con `phar://` si el almacenamiento de la base de datos no normaliza los valores. El atacante modifica su path almacenado (vía IDOR o SQLi) para apuntar al archivo subido con un prefijo `phar://`.
- Un plugin de WordPress acepta subidas de ZIP para instalación de temas. El plugin llama a `file_exists` en las entradas del archivo durante la extracción. El ZIP es a su vez un PHAR válido con un manifiesto malicioso.

## Notas relacionadas

- [[deserialization]] — el mecanismo subyacente; la deserialización PHAR es un trigger alternativo del mismo bug de deserialización.
- [[gadget-chains]] — las cadenas que se ejecutan una vez que el PHAR dispara el kick-off son cadenas de gadgets estándar.
- [[file-upload-abuse]] — mecanismo de entrega primario; el threat model de subida de archivo debe incluir el trigger PHAR.
- [[path-traversal]] — el control del path que llega a funciones del sistema de archivos es la condición previa de explotación.

## Referencias

- **Investigación / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
- **Docs Oficiales:** PHPGGC — https://github.com/ambionics/phpggc
- **Testing / Lab:** PortSwigger Insecure deserialization — https://portswigger.net/web-security/deserialization
- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
