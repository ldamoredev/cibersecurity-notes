# Image and Location OSINT

## Definición

El Image and Location OSINT es el análisis de imágenes públicas, videos, metadatos embebidos, mapas, puntos de referencia, sombras, señales y pistas ambientales para inferir dónde, cuándo o cómo se produjo un medio. Es el modo OSINT que convierte el contexto visual — a menudo compartido casualmente — en afirmaciones estructuradas y respaldadas por evidencia sobre ubicación, tiempo o estado organizacional.

## Por qué importa

Las imágenes pueden revelar oficinas, pantallas, credenciales de acceso, equipamiento, documentos internos, patrones de viaje, diseños de instalaciones y contexto operacional que ningún canal de texto divulga. Una sola foto de conferencia puede confirmar la ubicación de una instalación; una sola captura de lanzamiento puede confirmar el hostname de una herramienta interna; una sola foto de equipo con una pizarra visible puede filtrar contenido del roadmap.

Este también es el modo OSINT donde **el riesgo de privacidad y seguridad se concentra**. Las ubicaciones revelan dónde viven y trabajan las personas; las imágenes revelan quién está en una sala juntos; los metadatos revelan el dispositivo que tomó la foto. El uso defensivo es de alto apalancamiento; el uso ofensivo contra individuos está casi siempre fuera de scope.

Las prioridades defensivas, en orden:
- **Revisión pre-publicación** — atrapar fondos sensibles antes de que el contenido salga del edificio.
- **Eliminación de metadatos** — eliminar huellas de dispositivo, GPS y edición de imágenes de salida.
- **Higiene de capturas de pantalla** — capacitar al personal en URLs visibles, nombres de cuentas, herramientas internas y títulos de documentos en capturas.
- **Geolocalización defensiva** — verificar qué puede inferir ya un atacante sobre las ubicaciones de instalaciones a partir de imágenes públicas.

## Cómo funciona

El Image/Location OSINT usa **5 capas de evidencia**. Una afirmación de ubicación defendible generalmente combina al menos tres.

1. **Metadatos.** Datos EXIF (Exchangeable Image File Format) incluyendo timestamps, información del dispositivo, coordenadas GPS, parámetros de lente y firmas de software de edición. Muy informativos cuando están presentes, pero eliminados o modificados por muchas plataformas en la carga.
2. **Contenido visual.** Puntos de referencia, señales de negocios, credenciales de acceso, pantallas, matrículas, idioma/guión, objetos de marca, diseños, características arquitectónicas.
3. **Pistas ambientales.** Condiciones climáticas, vegetación/estación, ángulo solar y longitud de sombras (cronolocalización), marcas viales (regionales), formatos de matrícula.
4. **Correlación de mapas.** Street view, imágenes satelitales, listados de negocios, características de OpenStreetMap, terreno — usado para corroborar afirmaciones de contenido visual.
5. **Contexto de fuente.** Timestamp del post, historial de cuenta, texto del caption, plataforma, posts circundantes. Provee el marco temporal y de responsabilidad.

El bug es tratar una sola pista de imagen como prueba. Las afirmaciones de ubicación y tiempo necesitan **corroboración en al menos dos capas independientes** antes de promover de "probable" a "verificado" (ver [[osint-triage]]).

Un ejemplo trabajado, uso defensivo:

```
Pregunta:    ¿Qué puede inferir un atacante sobre la HQ de Example Corp de fotos públicas?
Fuentes:     fotos oficiales del evento de lanzamiento, posts de LinkedIn públicos de empleados, tour de oficina en Glassdoor.
Capa 1 (metadatos):    GPS eliminado en todas las imágenes muestreadas; una foto de lanzamiento retiene tiempo.
Capa 2 (visual):       número de edificio visible, arte de lobby distintivo, señal de recepción de marca.
Capa 3 (ambiente):     estación + ángulo solar consistente con fotos de tarde de verano.
Capa 4 (mapa):         Google Street View coincide con número de edificio + arte de lobby.
Capa 5 (contexto):     los captions de los posts nombran explícitamente la ciudad.
Verificado:            ubicación HQ + piso aproximado visible desde fotos públicas.
Acción:                capacitación de revisión pre-publicación; revisión de posición de señal de recepción.
```

La cadena de evidencia muestra lo que concluiría un atacante con el mismo esfuerzo — que es el entregable defensivo.

## Técnicas / patrones

La disciplina es "cuál es el herramienta de menor contacto que produce una afirmación defendible".

- **Metadatos EXIF** vía `exiftool` para archivos con metadatos preservados.
- **Búsqueda inversa de imágenes** (Google Lens, Yandex Images, TinEye) para coincidencias visuales en la web.
- **Comparación de mapas y street-view** (Google Maps/Earth, Bing Maps, OpenStreetMap, Mapillary) para corroboración de puntos de referencia.
- **Señales, idioma, arquitectura, marcas viales** para estrechamiento de región.
- **Análisis de sombras (cronolocalización)** para estimación de hora del día y ventana de fecha.
- **Lectura de pantallas y fondos** para exposición de herramienta interna, hostname, título de documento y credencial.
- **Contexto de carga y comportamiento de compresión de plataforma** — algunas plataformas eliminan EXIF, algunas lo mantienen; el comportamiento varía según la ruta de carga (web vs móvil vs API).

## Variantes y bypasses

El Image/Location OSINT se agrupa en **5 modos de trabajo**.

### 1. Extracción de metadatos

Lee EXIF embebido cuando las plataformas lo preservan. Útil cuando está presente, frágil cuando no. Muchas plataformas sociales eliminan GPS en la carga, pero las apps de mensajería y los compartidos directos de archivos a menudo lo preservan. Los investigadores no deben asumir "la plataforma X elimina" sin testing por ruta.

### 2. Geolocalización visual

Usa pistas de escena (puntos de referencia, señales, arquitectura, vegetación) para inferir ubicación. Más fuerte cuando múltiples pistas independientes convergen en la misma región; más débil cuando las pistas son genéricas ("cualquier lugar con palmeras").

### 3. Verificación temporal (cronolocalización)

Usa sombras, posición solar, clima, vegetación/estación o posts de eventos correlacionados para inferir tiempo. La longitud de la sombra más el azimut solar estrecha la hora del día a minutos si se conoce la ubicación.

### 4. Revisión de fondo sensible

Encuentra pantallas, credenciales, documentos internos, pizarras, números de serie de equipos o controles de acceso de instalaciones en imágenes. **Mayor valor defensivo** porque estas filtraciones son generalmente accidentales y fáciles de arreglar en la etapa de publicación.

### 5. Revisión de manipulación

Verifica si el contexto de la imagen puede estar editado, reutilizado, mal captionado o generado por IA. La búsqueda inversa de imágenes revela reutilización; el análisis de metadatos + artefactos de compresión revela edición; la inconsistencia por píxel revela manipulación. Crucial cuando las imágenes son evidencia en informes de incidentes.

## Impacto

Ordenado aproximadamente por severidad:

- **Exposición de ubicación física.** Oficinas, hogares, instalaciones y patrones de viaje pueden identificarse — tanto organizacionales como personales.
- **Filtración operacional.** Las pantallas visibles, credenciales, documentos internos y equipamiento revelan contexto interno que los atacantes no pueden observar de otra manera.
- **Contexto de ingeniería social.** Los eventos, la visibilidad de roles y la presencia física agudzan el pretexting.
- **Verificación de incidentes.** Las imágenes pueden respaldar o refutar afirmaciones sobre eventos, detalles de brechas o estado de activos.
- **Daño a la privacidad.** Las personas y ubicaciones pueden exponerse innecesariamente; este es el riesgo dominante para el Image OSINT de objetivo personal y la razón por la que la mayoría de los casos de uso de objetivo personal están fuera de scope.

## Detección y defensa

Las defensas se agrupan alrededor de **revisión pre-publicación** y **corroboración multicapa**.

1.
**Revisá las imágenes antes de postearlas públicamente.**
   Verificá fondos, pantallas, credenciales, documentos y metadatos. La mayoría de las exposiciones son accidentales y serían atrapadas por una revisión de 30 segundos por imagen.

2.
**Eliminá metadatos donde no se necesiten.**
   `exiftool -all=` elimina EXIF; muchos pipelines de publicación deberían hacer esto por defecto. La eliminación de metadatos corta la exposición accidental de dispositivo/ubicación sin afectar el contenido de la imagen.

3.
**Usá minimización para datos de personas y ubicación.**
   Evitá recopilar o publicar más de lo que requiere la investigación. La geolocalización de objetivo personal está fuera de scope para OSINT de seguridad.

4.
**Corroborá las afirmaciones de geolocalización.**
   Usá pistas independientes de al menos dos de las cinco capas antes de reportar una ubicación. Las afirmaciones de capa única permanecen en "probable" o "incierto".

5.
**Capacitá a los equipos en higiene de capturas y fotos.**
   Las URLs visibles, nombres de cuentas, pantallas de herramientas internas, títulos de documentos, detalles de credenciales y detalles revelados en reflejos son las filtraciones accidentales más comunes. La concienciación es más barata que el monitoreo.

### Qué no funciona como defensa primaria

- **Asumir que las plataformas eliminan todos los metadatos.** El comportamiento varía por plataforma, ruta de carga y tipo de archivo; testear el flujo real antes de confiar en él.
- **Recortar sin verificar reflejos, espejos o contenidos de pantalla.** Los detalles sensibles persisten en lugares no obvios.
- **Geolocalización de pista única.** Los puntos de referencia, señales y arquitectura similares confunden; la corroboración multicapa es obligatoria.
- **Publicar ubicaciones exactas innecesariamente.** Los informes defensivos pueden describir el riesgo sin exponer las coordenadas exactas que impulsaron el hallazgo.
- **Confiar solo en la búsqueda inversa de imágenes para la detección de manipulación.** Sin coincidencia no significa original; la detección de manipulación necesita metadatos + análisis visual combinados.

## Labs prácticos

Usá tus propias fotos, contenido propio o imágenes de entrenamiento públicas. No analicés imágenes de terceros identificables sin autorización.

### Inspeccioná metadatos EXIF

```
# Dump completo de metadatos
exiftool image.jpg

# Solo los campos relevantes para seguridad
exiftool -GPSLatitude -GPSLongitude -DateTimeOriginal -Make -Model -Software image.jpg

# Eliminá todos los metadatos antes de publicar
exiftool -all= -overwrite_original image.jpg
```

Registrá solo los campos relevantes. Evitá almacenar metadatos personales innecesarios en el informe mismo.

### Construí una tabla de pistas visuales

```
pista                 | observación                          | posible significado               | confianza | corroboración
idioma                | escritura latina, palabras español   | región de habla hispana           | baja       | necesita match de contenido de señal
arquitectura          | fachada art-deco, ladrillo claro     | edificio urbano de principios s.XX | media      | match a imágenes de mapas
señal de negocio      | "Café Mirador" en frente de negocio  | nombre de negocio específico      | media      | búsqueda inversa del nombre
ángulo solar          | razón de sombra ~0.6                 | mañana si se conoce la ubicación  | baja       | necesita estimación de latitud
punto de referencia visible | torre campanario distintiva    | coincide con Catedral X           | alta       | coincidencia directa en mapa
```

Este es el artefacto que convierte una intuición en una afirmación defendible.

### Búsqueda inversa de imágenes en múltiples motores

```
Google Lens   → 0 coincidencias
Yandex Images → 3 coincidencias, todas en blog de viajes (2023-08)
TinEye        → 1 coincidencia, fecha de publicación original 2023-08-12
Conclusión: la imagen es reutilizada de 2023-08; no es una foto original reciente.
```

La cobertura de motores difiere significativamente; rotá motores para cualquier verificación de manipulación significativa.

### Revisá filtraciones en capturas de pantalla

```
URL visible:       https://internal-tools.example.test/admin/users
nombre de cuenta:  visible en pestaña del navegador — "j.smith@example.test"
herramienta interna: branding "MetricMon v3" visible
título de documento: "Q3 Roadmap.docx" en pestaña adyacente
credencial/sala:   credencial de acceso al edificio con foto visible
ítem de calendario: "Negociación Vendor X" visible en barra lateral
```

Este tipo de auditoría aplicada a una captura de lanzamiento atrapa el 90% de las filtraciones operacionales accidentales.

### Auditá tu propia exposición de detalles visibles

```
tipo de contenido    | última revisión            | hallazgo
fotos de equipo      | 2026-04-15                | eliminar EXIF, difuminar credenciales, verificar pizarra
capturas de lanzamiento | 2026-04-20             | redactar hostnames internos, ítems de barra lateral
fotos de eventos     | 2026-04-22                | verificar número de edificio, señalización, seriales de equipo
posts de viaje de exec | no revisado (fuera de scope) | marcar para capacitación de OPSEC personal, no para análisis
```

El Image OSINT defensivo contra tu propio contenido atrapa lo que verán los atacantes.

## Ejemplos prácticos

- Una foto pública de oficina revela una URL de dashboard en una pantalla, exponiendo un hostname de herramienta interna.
- Los metadatos EXIF en una imagen compartida por un partner incluyen coordenadas GPS, exponiendo el hogar del fotógrafo.
- Una credencial de acceso en el fondo de una foto de lanzamiento revela un patrón de acceso a instalaciones (tarjeta de proximidad con número de empleado visible).
- Las señales de calles y la arquitectura combinadas con un número de edificio y un match de negocio por búsqueda inversa identifican una oficina satélite no anunciada.
- Una captura de equipo expone un hostname interno en la pestaña del navegador y un título de documento en la ventana adyacente.
- El análisis de sombras de una foto de conferencia confirma que fue tomada a la hora que afirma el post (cronolocalización como verificación de autenticidad).

## Notas relacionadas

- [[social-media-osint]]
- [[osint-triage]]
- [[osint-reporting]]
- [[email-and-phone-osint]]
- [[exposed-storage|Exposed Storage]]
- [[passive-recon|Passive Recon]]

### Notas atómicas futuras sugeridas

- exif-metadata
- visual-geolocation
- screenshot-hygiene
- reverse-image-search
- shadow-analysis
- chronolocation
- image-manipulation-review

## Referencias

- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Docs Oficiales:** ExifTool by Phil Harvey — https://exiftool.org/
- **Fundamental:** OSINT Framework — https://osintframework.com/
