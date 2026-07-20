# OSINT

## Definición

Open Source Intelligence (OSINT) es la recopilación, evaluación e informe disciplinados de información de fuentes públicas o legalmente accesibles. Es la práctica de convertir artefactos públicos observables — resultados de búsqueda, certificados, archivos, filtraciones, registros, imágenes, perfiles públicos — en respuestas respaldadas por evidencia a una pregunta específica.

## Por qué importa

OSINT convierte pistas públicas dispersas en contexto utilizable. En ciberseguridad, mapea empresas, dominios, tecnologías, documentos expuestos, identidades públicas, pistas de brechas y superficie de ataque sin enviar paquetes al objetivo. Es también el único modo de reconocimiento que es seguro ejecutar antes de que haya autorización: nada de esto genera carga, errores o alertas en la infraestructura del objetivo.

La distinción importante: OSINT no es "cualquier cosa encontrada online". Es análisis respaldado por evidencia con **una pregunta, fuentes acotadas, calificación de calidad de fuentes, límites éticos y una conclusión defendible**. Una carpeta de capturas de pantalla es recopilación; una respuesta triada con procedencia es inteligencia.

La misma habilidad es también la primitiva defensiva más fuerte que tiene un equipo pequeño. Ejecutar OSINT contra tu propia organización muestra lo que un atacante ya puede inferir gratis — subdominios filtrados, documentos obsoletos, source maps, buckets expuestos, directorios de empleados — antes de que ocurra cualquier testing activo.

## Cómo funciona

OSINT sigue **5 etapas** que siempre deberían ejecutarse en este orden. Saltarse cualquier etapa es la causa más común de OSINT malo.

1. **Pregunta.** Definí exactamente qué estás intentando aprender. "Mapeá la superficie de ataque pública de la empresa" es viable. "Encontrá información comprometedora sobre esta persona" no lo es — no tiene scope, ni condición de parada, ni límite ético. Una buena pregunta cabe en una oración y nombra un entregable.
2. **Recopilación.** Reuní pistas de fuentes públicas contra la pregunta. Mantenete estrictamente pasivo: sin logins, sin escaneos de puertos, sin sondeos que cambien el estado del objetivo. Registrá cada URL fuente y timestamp en el momento de la recopilación — los datos públicos se desplazan.
3. **Triaje.** Separar señal de ruido. Mové cada pista a verificado / probable / incierto / ruido / sensible (ver [[osint-triage]]). El punto del triaje es decidir qué prueba realmente cada pista y qué no prueba aún.
4. **Corroboración.** Confirmá afirmaciones importantes con al menos una fuente independiente antes de reportarlas. Las colisiones de identidad, los archivos obsoletos y la sobreconfianza en herramientas son fáciles de cometer y difíciles de notar sin este paso.
5. **Informe.** Preservá evidencia, etiquetas de confianza, URLs de fuentes, timestamps, límites de scope y próximas acciones concretas. Un informe que no puede ser rerecorrido por un segundo analista no está terminado.

No hay payload de exploit. La habilidad central es convertir datos públicos en conclusiones defendibles sin exagerar, y el entregable es un informe que otro analista puede auditar.

Un ejemplo pequeño trabajado:

```
Pregunta: ¿example.com expone subdominios olvidados?
Etapa 1: acotado al dominio apex example.com y marcas hermanas conocidas.
Etapa 2: extraer resultados de certificate transparency de crt.sh, snapshots de archive.org, DNS público.
Etapa 3: triar 47 nombres → 12 verificados vivos, 9 probable-obsoletos, 3 colisión (marca hermana), 23 ruido.
Etapa 4: corroborar "obsoleto" con HTTP head contra sonda propia + archive.org last-seen.
Etapa 5: reportar 9 nombres obsoletos con procedencia, sugerir verificación de baja o reclamación.
```

## Técnicas / patrones

Cada técnica se empareja con fuentes públicas concretas.

- **Búsqueda y archivo.** Motores de búsqueda (Google, Bing, DuckDuckGo, Yandex), operadores avanzados, [[google-dorking|Google dorking]] vía GHDB, Wayback Machine de archive.org, archive.today, common-crawl.
- **Documentos y metadatos.** PDFs/DOCs públicos encontrados vía operadores `filetype:`, metadatos EXIF vía [[image-and-location-osint|image OSINT]], registros de paquetes (npm, PyPI, Maven), búsqueda de código en GitHub/GitLab, source maps y rutas `.well-known`.
- **Personas y cuentas.** Páginas de empresa, bios de conferencias, publicaciones de trabajo de LinkedIn, emails de commits públicos, listas de speakers de conferencias; cubiertos con encuadre ético en [[social-media-osint]] y [[email-and-phone-osint]].
- **Señales de brechas y filtraciones.** Have I Been Pwned, listados de dumps públicos, paste sites y feeds de exposición de credenciales; cubiertos en [[breach-and-leak-intelligence]].
- **Imagen, video, ubicación.** Búsqueda inversa de imágenes, EXIF, georreferenciación, análisis de ángulo de sol/sombra, Mapillary; cubiertos en [[image-and-location-osint]].
- **Dominio, DNS, certificado, registro.** WHOIS/RDAP, certificate transparency (crt.sh), historial de DNS (SecurityTrails, ViewDNS), registros ASN/BGP, postura DNSSEC; cubiertos en [[company-osint]] y [[passive-recon|passive recon]].

## Variantes y bypasses

OSINT tiene **5 modos de trabajo**. Elegí el modo que coincida con la pregunta; no los mezclés.

### 1. Cyber OSINT

Foco: activos, tecnologías, exposición, secretos filtrados, superficie de ataque. Las entradas son dominios, certificados, source maps, metadatos de paquetes, filtraciones de GitHub, snapshots de archivo. La salida es un inventario de activos clasificado por evidencia y una lista de exposición. El handoff es hacia [[external-attack-surface|external attack surface]] y [[recon-to-testing-handoff|active recon]].

### 2. Company OSINT

Foco: marca, propiedad, subsidiarias, vendors, productos, entidades legales, huella pública. Las entradas son registros corporativos, comunicados de prensa, publicaciones de trabajo, anuncios de vendors, campos de organización de certificados. La salida es un mapa de propiedad que impulsa la validación de scope — saber quién posee un dominio o activo importa antes de que cualquier test entre en producción (ver [[scope-validation|scope validation]]).

### 3. People OSINT

Foco: pistas de identidad pública que conectan a una persona con un rol, cuenta o capacidad. Las entradas son bios de conferencias, commits públicos, perfiles públicos, listados de brechas vinculados a emails. **Aquí se aplican los límites éticos más fuertes**: propósito claro, base legal, minimización, límite de retención y sin agregación que cree daño más allá de la pregunta original. Por defecto, usá la evidencia de menor contacto que responda la pregunta.

### 4. Media y ubicación OSINT

Foco: dónde, cuándo y quién a partir de imágenes, video, audio o pistas ambientales. Las entradas son metadatos EXIF, búsqueda inversa de imágenes, puntos de referencia, pistas de idioma/matrícula, posición solar e imágenes de calles. La salida es una afirmación de tiempo/lugar/persona corroborada con confianza y límites, nunca una afirmación de fuente única.

### 5. Threat intelligence OSINT

Foco: rastrear infraestructura adversaria, indicadores y campañas a través de fuentes públicas. Las entradas son blogs de vendors, feeds de IOC públicos, mapeos MISP/ATT&CK, reutilización de certificados, DNS pasivo y resultados de sandbox públicos. La salida son indicadores contextuales vinculados a la exposición de la organización, no un dump genérico de IOC.

## Impacto

Ordenado aproximadamente por severidad:

- **Descubrimiento de superficie de ataque.** OSINT revela activos, endpoints y propiedad antes de cualquier sonda activa — a menudo la mayor fuente individual de exposición para equipos con pocos recursos.
- **Claridad de scope.** Las pistas de empresa y propiedad previenen el testing del objetivo incorrecto durante pentests y trabajo de bug bounty.
- **Descubrimiento de exposición.** Los documentos públicos, filtraciones, source maps y metadatos revelan contexto sensible (hostnames internos, datos de clientes, credenciales) que la organización no sabía que era público.
- **Mejor estrategia de testing.** Las pistas de stack y ruta del reconocimiento pasivo hacen el testing activo posterior más rápido y silencioso.
- **Conciencia defensiva.** Los equipos aprenden qué pueden inferir los externos gratis, lo que agudiza las prioridades de hardening y la postura de respuesta a incidentes.

## Detección y defensa

OSINT contra tu propia organización es en sí misma una defensa. El orden es por lo que cambia más la exposición con menos esfuerzo.

1.
**Ejecutá OSINT contra tu propia organización.**
   El OSINT defensivo muestra qué exponen las fuentes públicas antes de que los atacantes lo usen. Repetilo con una cadencia (mínimo trimestral) porque los datos públicos se desplazan; nuevos certs, nuevos repos, nuevos vendors, nuevos docs cambian el panorama.

2.
**Calificá la confiabilidad de las fuentes y la confianza.**
   Las pistas públicas son desiguales. Marcá cada afirmación como verificada, probable, incierta, obsoleta o ruido, y requerí corroboración antes de actuar sobre conclusiones sensibles. La etiqueta es el payload educativo — una afirmación verificada y una probable impulsan decisiones diferentes.

3.
**Minimizá la recopilación de datos personales.**
   El OSINT enfocado en personas debe tener un propósito claro, base legal, regla de minimización y límite de retención. Por defecto, usá la evidencia de menor contacto que responda la pregunta; no agregués más allá del scope.

4.
**Limpiá la exposición pública evitable.**
   Subdominios obsoletos, docs obsoletos, EXIF eliminado en imágenes de salida, source maps eliminados, metadatos redactados en PDFs, secret-scanning en repos públicos y rotación de credenciales después de menciones de brechas son correcciones concretas y acotadas.

5.
**Convertí los hallazgos en inventario, capacitación o remediación.**
   OSINT solo es útil cuando cambia decisiones. Vinculá los informes a un elemento de inventario rastreado, un cambio de capacitación o un ticket de remediación — no a una captura de pantalla de Slack.

### Qué no funciona como defensa primaria

- **Asumir que "público" significa "inofensivo".** Las pistas públicas se componen; un org chart más una publicación de trabajo más un SAN de cert es sensible aunque cada pieza no lo sea.
- **Asumir que los datos viejos son inútiles.** Los archivos y registros obsoletos a menudo exponen patrones aún verdaderos hoy (convenciones de nombres, relaciones con vendors, terminología interna).
- **Recopilar todo.** El OSINT sin foco crea ruido, riesgo de privacidad y fatiga del analista. Cada elemento recopilado debería responder la pregunta.
- **Conclusiones de fuente única.** Las afirmaciones importantes necesitan al menos una fuente de corroboración independiente.
- **Robots.txt y noindex.** Reducen la presión de indexación, no la exposición. El activo sigue siendo público.

## Labs prácticos

Usá tu propio nombre/dominio/empresa, un engagement autorizado o un objetivo público de entrenamiento deliberadamente elegido. Mantenete estrictamente pasivo — ninguno de estos labs debería enviar paquetes a infraestructura no propia.

### Definí la pregunta OSINT primero

```
Pregunta:          "Mapeá la huella pública de subdominios de example.com y marcá entradas obsoletas."
Fuentes permitidas: crt.sh, archive.org, DNS público, WHOIS/RDAP público.
Fuera de scope:    cualquier petición HTTP a hosts no propios; cualquier intento de login.
Estándar de evidencia: >=2 fuentes independientes para cualquier afirmación "activo".
Condición de parada: todos los nombres de certificate-transparency triados en 5 buckets.
```

Una pregunta acotada es la diferencia entre una investigación y un montón de links.

### Extraé nombres de certificate transparency

```
curl -s 'https://crt.sh/?q=%25.example.com&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sort -u
```

Certificate transparency es la fuente pasiva de mayor señal para el descubrimiento de subdominios — cada cert TLS público aparece aquí.

### Capturá DNS público sin escaneo activo

```
dig +short ANY example.com
dig +short txt example.com
dig +short mx example.com
```

Inspeccioná desde tu propio resolver. Esto es una búsqueda pasiva, no un sondeo autoritativo del objetivo.

### Inspeccioná snapshots de archivo para activos obsoletos

```
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&output=json&limit=200" \
  | jq -r '.[1:] | .[] | [.[1], .[2]] | @tsv'
```

Archive.org revela rutas y subdominios que ya no responden. Los activos obsoletos a menudo sobreviven al equipo que los construyó.

### Tabulá cada afirmación antes de reportar

```
afirmación                      | fuente               | timestamp           | confianza | corroboración       | próxima acción
api-staging.example.com existe  | crt.sh cert #98231   | 2026-04-29T18:00Z  | probable  | archive.org 2024-08 | http-head probe (scope propio)
old-blog.example.com existe     | archive.org snapshot | 2026-04-29T18:01Z  | obsoleto  | ninguna             | triar como ruido
```

Este es el artefacto que convierte "encontré algo" en un informe que otro analista puede auditar.

### Comparar pasivo vs activo antes de cada acción

```
Lectura de resultados de búsqueda:    pasivo
Búsqueda de certificate transparency: pasivo
Consulta WHOIS/RDAP:                  pasivo
Petición HTTP a host objetivo:        activo
Escaneo de puertos / banner grab:     activo
Intento de login o uso de credenciales: activo e intrusivo
```

Manté el OSINT estrictamente pasivo; la frontera hacia el reconocimiento activo es el momento en que le debés una notificación al objetivo.

## Ejemplos prácticos

- Los certificados públicos revelan subdominios de staging o admin olvidados mucho después de que termina el proyecto original.
- Las publicaciones de trabajo revelan opciones de cloud provider, framework y herramientas que estrechan el reconocimiento activo.
- Los documentos públicos (PDF, DOCX) llevan nombres de autores, etiquetas de proyectos internos y artefactos de plantillas en metadatos.
- Los operadores de búsqueda (`filetype:`, `inurl:`, `intitle:`) sacan a la superficie documentos internos expuestos y páginas admin antiguas.
- Los indicadores de brechas vinculados a emails corporativos sugieren prioridades de rotación de credenciales y aplicación de MFA.
- Los source maps públicos de frontends de producción revelan nombres de rutas, rutas de API y nombres de módulos internos.

## Notas relacionadas

- [[osint-triage]]
- [[search-engine-operators]]
- [[google-dorking]]
- [[breach-and-leak-intelligence]]
- [[company-osint]]
- [[passive-recon|Passive Recon]]
- [[external-attack-surface|External Attack Surface]]

### Notas atómicas futuras sugeridas

- osint-opsec
- source-reliability-grading
- historical-internet-artifacts
- public-document-metadata
- threat-intelligence-osint
- osint-legal-and-ethical-framework

## Referencias

- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
