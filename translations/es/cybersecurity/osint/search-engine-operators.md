# Search Engine Operators

## Definición

Los operadores de motores de búsqueda son funcionalidades de sintaxis de consulta que acotan, excluyen, combinan o apuntan resultados con más precisión que las búsquedas de palabras clave ordinarias. Convierten una caja de búsqueda en un instrumento pasivo de OSINT que estrecha millones de páginas indexadas hasta los artefactos públicos específicos que responden una pregunta definida.

## Por qué importa

Los operadores de búsqueda son la herramienta OSINT de mayor apalancamiento porque son de costo cero, sin credenciales y completamente pasivos — ningún paquete llega al objetivo, solo el índice del motor de búsqueda. Sacan a la superficie documentos públicos, rutas admin indexadas, source maps expuestos, mensajes de error y contenido histórico sin ningún sondeo activo.

Los operadores también fuerzan disciplina. Una consulta de palabras clave desnuda devuelve páginas de marketing y ruido; una consulta acotada (`site:` + `filetype:` + frase exacta + términos de exclusión) devuelve el artefacto expuesto específico que saliste a encontrar. La habilidad es el **diseño de la consulta**, no memorizar nombres de operadores.

Diferentes motores indexan diferentes páginas. Google, Bing, DuckDuckGo, Yandex y Baidu tienen diferentes crawlers, filtros y políticas de desindexación; rotar motores revela contenido que un motor ha eliminado.

## Cómo funciona

Los operadores de búsqueda responden **5 preguntas de consulta** en combinación. Una consulta útil generalmente responde al menos tres de ellas.

1. **¿Dónde?** `site:example.com`, `site:*.example.com`, `inurl:` — limita a un dominio, patrón de subdominio o fragmento de URL.
2. **¿Qué texto exacto?** `"frase exacta"` — fuerza coincidencia exacta de cadena en lugar de términos derivados o relacionados; esencial para encontrar mensajes de error copiados, tokens filtrados o terminología interna específica.
3. **¿Qué tipo?** `filetype:pdf` / `ext:xlsx` — limita a una categoría de contenido. Combiná con `site:` para encontrar documentos públicos de una organización.
4. **¿Qué no?** `-excluido -término -site:ruidoso.example.com` — elimina falsos positivos. A menudo la diferencia entre una página de resultados útil y 200 páginas ruidosas.
5. **¿Qué relación?** `término1 OR término2`, paréntesis `(a OR b) -c`, `intitle:`, `intext:` — combina o relaciona términos cuando la pregunta tiene alternativas o restricciones.

El bug no es "usar búsqueda". La habilidad OSINT es **construir una consulta que responda una pregunta definida sin recopilar ruido**, luego iterarla contra el conjunto de resultados.

Un ejemplo trabajado:

```
Pregunta:  ¿example.com expone algún archivo admin o backup indexado?
Iteración 1: site:example.com (inurl:admin OR inurl:backup) → 412 hits, mayormente blog de producto
Iteración 2: + (filetype:zip OR filetype:sql OR filetype:bak) → 7 hits, todos con forma de backup
Iteración 3: + -site:blog.example.com -"product backup feature" → 3 hits, todas exposiciones reales
```

## Técnicas / patrones

El inventario de operadores es pequeño. La habilidad está en componerlos.

- `site:` y `site:*.` para acotar dominio y subdominio.
- `"frase exacta"` para coincidencia de cadena verbatim (errores, plantillas copiadas, tokens filtrados).
- `-término` y `-site:` para exclusión de ruido conocido.
- `filetype:` / `ext:` para descubrimiento de documentos (`pdf`, `xlsx`, `csv`, `sql`, `bak`, `zip`, `tar`, `log`).
- `intitle:` / `inurl:` / `intext:` para coincidir dónde aparece el término.
- Filtros de rango y fecha vía el panel Herramientas de Google o `before:` / `after:`.
- `cache:` para la copia en caché del motor cuando la página activa cambió o fue eliminada.
- Motores alternativos (Bing, DuckDuckGo, Yandex) para cubrir puntos ciegos de indexación — Yandex frecuentemente retiene contenido que Google elimina.

## Variantes y bypasses

El uso de operadores se agrupa en **5 modos prácticos**. La mayoría de las investigaciones encadenan al menos tres de ellos.

### 1. Acotado de dominio

Encontrá contenido bajo un dominio o subdominio específico. `site:example.com`, `site:*.example.com`, o `site:example.com -site:blog.example.com`. El primer movimiento en cualquier OSINT apuntado a una organización.

### 2. Descubrimiento de documentos

Encontrá PDFs, hojas de cálculo, presentaciones y exportaciones. `site:example.com (filetype:pdf OR filetype:xlsx OR filetype:csv)`. Los documentos públicos a menudo llevan metadatos de autor, etiquetas de proyectos internos y artefactos de plantillas que impulsan [[company-osint]].

### 3. Descubrimiento de endpoints

Encontrá URLs con rutas API, admin, login, callback o de versión. `site:example.com (inurl:api OR inurl:v1 OR inurl:admin OR "redirect_uri")`. Entregá los hallazgos vivos a [[endpoint-discovery|endpoint discovery]] para validación activa.

### 4. Descubrimiento de errores y exposición

Encontrá errores indexados, listados de directorio o páginas públicas accidentales. `site:example.com (intitle:"index of" OR "Application error" OR "stack trace")`. Trata la búsqueda como un lint defensivo contra la huella pública.

### 5. Exclusión y limpieza

Eliminá el ruido que generaron los cuatro modos anteriores. `-site:blog-ruidoso.example.com -"product changelog" -"job posting"`. La exclusión es iterativa — cada consulta refina basándose en el ruido que produjo la anterior.

## Impacto

Ordenado aproximadamente por severidad:

- **Descubrimiento de documentos públicos.** Los archivos sacan a la superficie términos internos, nombres y etiquetas de proyectos vía metadatos.
- **Descubrimiento de rutas ocultas.** Las URLs indexadas revelan endpoints que no están en ninguna especificación pública.
- **Pistas de scope y propiedad.** Los resultados de dominio cruzado conectan marcas, vendors y adquisiciones.
- **Detección de exposición.** Los listados de directorio, páginas de error y source maps emergen como señal.
- **Reducción de ruido.** Las mejores consultas reducen pistas falsas y fatiga del analista.

## Detección y defensa

Las defensas aquí se tratan de revisar tu propia huella indexada, no de bloquear búsquedas.

1.
**Revisá qué indexan los motores de búsqueda para tus dominios.**
   Los resultados de búsqueda son parte de tu superficie pública. Ejecutá consultas operadoras defensivas con una cadencia trimestral; tratá el nuevo contenido indexado como nueva exposición.

2.
**Eliminá el contenido público sensible en la fuente.**
   La desindexación solo ayuda después de que el contenido ya no es públicamente accesible. De lo contrario, la URL sigue funcionando para cualquiera que la conozca.

3.
**Usá robots y noindex como controles de indexación, no controles de seguridad.**
   Reducen la descubribilidad pero no restringen el acceso. Un crawler que ignore `robots.txt` igualmente extraerá la página, y `robots.txt` en sí mismo es frecuentemente el mapa de mayor señal de rutas que no deberían ser públicas.

4.
**Monitoreá patrones de consulta de riesgo contra tu huella pública.**
   Los backups, exportaciones y páginas de error deberían ser encontrados por tus propias consultas programadas primero. Vinculá los hallazgos a una cola de remediación rastreada.

5.
**Evitá publicar metadatos innecesarios.**
   Eliminá EXIF y propiedades de documentos antes de la publicación. Los PDFs públicos que llevan nombres de autor internos y rutas de plantillas son exposiciones indexadas comunes.

### Qué no funciona como defensa primaria

- **`robots.txt` como control de acceso.** Es una instrucción para crawlers, no autorización; muchos crawlers y todos los atacantes lo ignoran.
- **Eliminar el resultado de búsqueda mientras se deja el archivo público.** La exposición persiste; el próximo crawl lo reindexará.
- **Asumir que un motor de búsqueda ve todo.** La cobertura difiere; Yandex frecuentemente retiene contenido que Google elimina.
- **Consultas amplias sin triaje.** Crean ruido, no inteligencia — cada resultado debe triarse en [[osint-triage|verificado / probable / incierto / ruido / sensible]].
- **Confiar en el nombre literal del operador.** Los motores reinterpretan silenciosamente los operadores; verificá el conjunto de resultados, no la sintaxis.

## Labs prácticos

Usá tu propio dominio, o un objetivo de entrenamiento público deliberadamente elegido. Ninguna de estas consultas sondea al objetivo — solo leen el índice del motor de búsqueda.

### Encontrá documentos públicos

```
site:example.test (filetype:pdf OR filetype:xlsx OR filetype:csv OR filetype:docx)
```

Revisá si cada documento es intencionalmente público; los metadatos de documentos son a menudo donde se filtran los términos internos.

### Encontrá pistas de rutas indexadas

```
site:example.test (inurl:api OR inurl:v1 OR inurl:admin)
site:example.test "redirect_uri"
site:example.test inurl:.well-known
```

Mové las pistas de rutas a [[endpoint-discovery|endpoint discovery]] para validación de scope propio.

### Encontrá contenido con forma de exposición

```
site:example.test intitle:"index of"
site:example.test ("Application error" OR "stack trace" OR "DEBUG")
site:example.test (filetype:bak OR filetype:sql OR filetype:zip OR filetype:tar)
```

El contenido con forma de exposición es donde el dorking defensivo paga más por minuto.

### Iterá la exclusión

```
site:example.test "login" -support -docs -site:blog.example.test
```

Ejecutá primero la consulta desnuda, listá fuentes de ruido, luego excluí. Dos iteraciones generalmente reducen el conteo de resultados a la mitad.

### Comparar motores

```
site:example.test "internal" → verificar en Google, Bing, Yandex, DuckDuckGo
```

Diferentes motores eliminan, retienen o rankean contenido diferente. Un resultado limpio en Google no significa exposición limpia.

### Usá copias en caché para páginas cambiadas

```
cache:example.test/old-admin
```

Cuando una página ha sido cambiada o eliminada, la copia en caché puede mostrar aún el contenido original durante horas a semanas.

## Ejemplos prácticos

- `site:` revela docs viejos, subdominios deprecated y páginas de marcas adquiridas aún indexadas.
- `filetype:pdf` encuentra informes públicos cuyos metadatos de autor nombran miembros internos del equipo.
- `inurl:api` encuentra documentación de API indexada que expone rutas que nunca se anunciaron públicamente.
- La búsqueda de frase exacta para una cadena de stack trace conocida encuentra cada página que alguna vez imprimió ese error.
- Yandex retiene contenido que Google eliminó; rotar motores revela exposiciones obsoletas-pero-aún-públicas.

## Notas relacionadas

- [[google-dorking]]
- [[osint-triage]]
- [[company-osint]]
- [[breach-and-leak-intelligence]]
- [[endpoint-discovery|Endpoint Discovery]]
- [[passive-recon|Passive Recon]]

### Notas atómicas futuras sugeridas

- advanced-search-pages
- search-result-triage
- search-engine-cache
- public-document-discovery
- historical-internet-artifacts
- engine-coverage-blind-spots

## Referencias

- **Docs Oficiales:** Google Search Help: refine searches — https://support.google.com/websearch/answer/2466433/refine-web-searches
- **Docs Oficiales:** Google Advanced Search Help — https://support.google.com/websearch/answer/35890
- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
