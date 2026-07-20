# Social Media OSINT

## Definición

El Social Media OSINT es la recopilación y análisis de información de plataformas sociales públicas para entender identidades, roles, relaciones, eventos, tecnologías, ubicaciones o contexto organizacional. Es el **modo de OSINT más sensible éticamente** porque el material crudo es la expresión pública voluntaria de las personas sobre sus vidas.

## Por qué importa

Las redes sociales revelan empleados, vendors, ubicaciones, tecnologías, canales de soporte, indicios de incidentes, terminología interna y relaciones de marca — contexto que agudiza tanto la postura defensiva como el pretexting de atacantes. Un único anuncio de lanzamiento puede confirmar una elección de stack; una única foto de conferencia puede confirmar una instalación; una única cuenta de soporte falsa puede ser la primera señal de una campaña activa de suplantación de marca.

También es donde el OSINT más fácilmente se vuelve invasivo. La plataforma invita a las personas a compartir, pero el trabajo del analista **no es cosechar todo lo que se comparte** — es responder una pregunta acotada con los datos personales mínimos que requiere la pregunta. La línea ética no es "¿es esto técnicamente público?" sino "¿recopilar esto hace avanzar la pregunta y el daño es proporcional?".

Para el Social Media OSINT defensivo específicamente, los casos de uso de mayor valor son:
- detectar suplantación de marca y ejecutivos
- encontrar contexto operacional filtrado accidentalmente (capturas, credenciales de acceso, hostnames internos)
- mapear opciones tecnológicas públicas que afectan la postura de seguridad
- monitorear señales de advertencia temprana de incidentes (empleados discutiendo públicamente interrupciones o brechas)

## Cómo funciona

El Social Media OSINT procesa **5 tipos de señal**. Una investigación acotada generalmente responde una de ellas, no las cinco.

1. **Señales de identidad.** Nombres, handles, roles, bios y cross-links de perfil entre plataformas. Útil para confirmar el rol y empleador de una persona; riesgoso para todo más allá de eso.
2. **Señales de relación.** Empleadores, equipos, vendors, eventos y comunidades. El tejido conectivo entre personas y organizaciones.
3. **Señales de línea temporal.** Posts, fechas, lanzamientos, incidentes, oleadas de contratación, menciones de viaje/eventos. Provee contexto temporal que la recopilación de snapshot único se pierde.
4. **Señales de medios.** Imágenes, videos, ubicaciones, credenciales de acceso, pantallas y documentos visibles. A menudo la superficie de exposición de mayor rendimiento (ver [[image-and-location-osint]]).
5. **Señales de tecnología.** Herramientas, menciones de stack, capturas de pantalla, pistas de trabajo/proyecto, commits públicos vinculados desde perfiles.

El bug es la **sobre-recopilación**. La habilidad es preguntarse "qué responde la pregunta con los menos datos personales posibles", luego detenerse cuando la pregunta está respondida.

Un ejemplo trabajado, uso defensivo:

```
Pregunta:    ¿Hay alguna cuenta falsa de "Example Corp Support" suplantándonos en Twitter/X?
Scope:       handle de marca, top 5 parecidos, top 20 menciones en los últimos 30 días.
Recopilación: handle, fecha de creación de cuenta, conteo de posts, afirmación de official-link, delta de seguidores.
Triaje:      una cuenta "examplecorp_support" creada 2026-04-22, publica estafa de redirección a DM.
Informe:     hallazgo de suplantación de marca → reporte de abuso a la plataforma + post de advertencia al cliente.
Almacenado:  handle, capturas, URLs de evidencia, registro de acciones. Sin datos personales de usuarios reales.
```

Notá lo que el ejemplo **no** recopila: handles de usuarios reales, listas de seguidores, amigos o DMs. La pregunta no requería nada de eso.

## Técnicas / patrones

La habilidad es elegir la fuente de menor contacto que responde la pregunta.

- **Cuentas oficiales de la empresa** para lanzamientos, anuncios de vendors, actualizaciones de estado.
- **Páginas de perfil público de empleados** (LinkedIn, GitHub, bios de conferencias) para corroborar rol y tecnología.
- **Posts sobre lanzamientos, incidentes, contratación, vendors** para contexto de línea temporal.
- **Capturas de pantalla e imágenes públicas** para señales de tecnología y operacionales (luego [[image-and-location-osint|image OSINT]] toma el relevo para análisis más profundo).
- **Links de perfil entre plataformas** para resolución de colisión de identidad (LinkedIn → GitHub → email de commit público es una cadena común).
- **Hashtags, páginas de eventos y posts de conferencias** para contexto de sector y asociaciones.
- **Edad de cuenta y pistas de suplantación** para casos de uso de protección de marca.

## Variantes y bypasses

El Social OSINT se agrupa en **5 límites éticos**. Cada uno tiene una prueba diferente de "¿está esto en scope?".

### 1. Análisis de cuenta oficial

Los posts y anuncios controlados por la empresa son generalmente de baja sensibilidad. La cuenta habla públicamente en nombre de la empresa. Prueba en-scope: ¿es este contenido publicado por la organización misma? Si sí, tratarlo como input OSINT estándar.

### 2. Análisis de perfil profesional público

Roles, historial de empleador y tecnologías declaradas en plataformas profesionales (LinkedIn, GitHub, bios de conferencias). Prueba en-scope: ¿responde esta pista una pregunta de seguridad (stack, scope, vendor) sin agregar contexto personal? Detente en rol + empleador + tecnología relevante; no construyas un dossier personal.

### 3. Análisis de medios/contexto

Las imágenes pueden revelar ubicaciones, pantallas, credenciales, documentos internos o detalles de diseño. Prueba en-scope: ¿se analiza la imagen por una señal organizacional (herramienta interna visible, patrón de acceso de credencial) o personal (dónde vive alguien)? Solo lo primero está en scope.

### 4. Revisión de suplantación y fraude

Cuentas falsas, suplantación de marca, handles de soporte falsos, suplantación de ejecutivos. **Este es el caso de uso defensivo más fuerte** — protege a usuarios, empleados y la marca. Prueba en-scope: ¿está el análisis apuntado al suplantador, no a los usuarios reales que interactúan con ellos?

### 5. Apuntado personal de alto riesgo

Vida personal, familia, recopilación adyacente al acoso, recopilación adyacente al doxxing. **Fuera de scope por defecto** para OSINT de seguridad. Prueba en-scope: no hay prueba en-scope; si la pregunta requiere esto, la pregunta en sí misma está mal.

## Impacto

Ordenado aproximadamente por severidad:

- **Contexto de ingeniería social.** Los roles públicos, relaciones con vendors y flujos de trabajo agudzan el pretexting.
- **Pistas de tecnología y vendors.** Los posts públicos y stacks declarados revelan herramientas, plataformas y proveedores SaaS.
- **Contexto de ubicación/evento.** Las imágenes y posts de eventos revelan pistas físicas u operacionales.
- **Detección de suplantación de marca.** Las cuentas falsas pueden dañar a usuarios y la marca; el Social OSINT defensivo las atrapa.
- **Contexto de scope.** Los perfiles públicos confirman qué productos, equipos y dominios pertenecen a la organización.

## Detección y defensa

Las defensas priorizan **minimización primero, preferencia por fuentes oficiales segundo**.

1.
**Definí una regla de minimización de datos de personas antes de la recopilación.**
   Recopilá solo lo que responde la pregunta de seguridad. Por defecto, usá señales organizacionales (cuentas oficiales, monitoreo de marca) sobre señales personales (perfiles de empleados).

2.
**Preferí fuentes oficiales y profesionales.**
   Evitá la recopilación de vida personal a menos que haya una razón autorizada clara. Las charlas de conferencias y los roles declarados son apropiados; los posts de vacaciones no lo son.

3.
**Capacitá al personal en riesgos de oversharing público.**
   Las capturas de herramientas internas, credenciales de conferencias, detalles de incidentes y posts de lanzamiento con demasiado detalle filtran contexto operacional. La concienciación es más barata que el monitoreo.

4.
**Monitoreá la suplantación de marca y cuentas de soporte falsas.**
   Este es el caso de uso de Social OSINT ofensivo más defendible — protege a los usuarios, no los amenaza. Vinculá los hallazgos a los flujos de trabajo de reporte de abuso de la plataforma.

5.
**Separar el contexto social del scope técnico.**
   El perfil de una persona no es permiso para testear sistemas. Incluso al corroborar que un empleado posee un dominio, el scope técnico debe autorizarse por separado.

### Qué no funciona como defensa primaria

- **Asumir que los datos personales públicos son válidos para cualquier uso.** Los límites éticos y legales siguen aplicando (GDPR, ToS de plataformas, marcos de acoso).
- **Recopilar grandes dossiers personales "por si acaso".** Esto aumenta el daño y reduce la relación señal-ruido.
- **Tratar las pistas sociales como prueba.** Un rol de LinkedIn es una afirmación, no empleo verificado; corroborá antes de actuar.
- **Ignorar las cuentas sociales oficiales.** A menudo revelan lanzamientos, acuerdos con vendors y señales de adquisición antes que cualquier otra fuente.
- **Leer contenido borrado-pero-archivado como actual.** Los snapshots de archivo muestran estado pasado; el scope actual requiere verificación actual.

## Labs prácticos

Usá tu propia huella pública, una empresa que seas dueño o una marca pública benigna. Mantenete estrictamente pasivo; no interactúes con cuentas objetivo.

### Construí un plan de recopilación mínima

```
Pregunta:           "¿Hay cuentas de soporte falsas suplantando a Example Corp?"
Cuentas a revisar:  @ExampleCorp oficial + top 5 parecidos + top 20 menciones de marca.
Datos personales:   ninguno más allá del handle del suplantador. Sin datos de usuarios reales recopilados.
Evidencia necesaria: handle, fecha de creación, patrón de posts, afirmación de official-link, capturas.
Condición de parada: todos los 5 parecidos triados + ventana de mención de 30 días escaneada.
```

La línea de minimización es explícita y aplicable.

### Rastreá una cuenta oficial para pistas técnicas

```
post de lanzamiento → nombre de producto  → link a docs → dominio → certificate transparency check
post de vendor      → nombre de vendor    → verificación CNAME en subdominios propios
post de contratación → stack declarado    → corroborar vía descripción de trabajo
post de incidente   → nombre de servicio  → verificación de página de status + DNS
```

Mové las pistas técnicas a [[company-osint]] y [[external-attack-surface|external attack surface]].

### Detectá suplantación de marca

```
plataforma | cuenta              | creada    | afirmación                    | evidencia | ruta de reporte
twitter  | @examplecorp_support | 2026-04-22 | suplanta soporte             | patrón DM scam | abuso a plataforma + post al cliente
linkedin | "Example Corp Inc"   | 2026-04-15 | página de empresa falsa      | robo de logo  | formulario de takedown
```

Uso defensivo; nunca interactúes con el suplantador desde cuentas de analistas.

### Resolvé colisión de identidad vía links entre plataformas

```
Perfil LinkedIn → dice rol en Example Corp
Perfil GitHub (vinculado desde LinkedIn) → commits públicos a repos example-corp/*
Bio de conferencia (vinculada desde LinkedIn) → coincide nombre + empleador + período
Decisión: probable (3 ejes corroboran, todos de fuentes profesionales)
```

Tres ejes profesionales promueven una afirmación de "incierto" a "probable". Los ejes de vida personal no pertenecen aquí.

### Auditá tu propia huella social

```
cuenta oficial                 | última fecha de revisión pública
perfiles públicos de empleados (muestra) | última fecha de capacitación
capturas públicas en posts      | última revisión de higiene
monitoreo de menciones de marca | feed activo
```

El Social Media OSINT defensivo contra tu propia marca atrapa lo que verán los atacantes.

## Ejemplos prácticos

- Un post de lanzamiento de empresa revela un nuevo dominio de producto, luego certificate transparency confirma el patrón de subdominio.
- Una captura de pantalla de empleado durante un lanzamiento muestra un nombre de dashboard interno visible en la pestaña del navegador.
- Un post de conferencia menciona una plataforma de vendor, exponiendo una relación de confianza de terceros.
- Una cuenta falsa `@examplecorp_support` publica estafas de redirección a DM; el OSINT defensivo la atrapa en 24 horas.
- Los links de perfil LinkedIn → GitHub conectan los commits públicos de un desarrollador con repos internos que coinciden con el nombrado de paquetes públicos de la empresa.
- Un post de vacaciones de un ejecutivo revela fechas aproximadas de viaje; esto **no** está en scope para OSINT de seguridad y no debería recopilarse.

## Notas relacionadas

- [[osint]]
- [[osint-triage]]
- [[company-osint]]
- [[email-and-phone-osint]]
- [[image-and-location-osint]]
- [[company-mapping|Company Mapping]]

### Notas atómicas futuras sugeridas

- brand-impersonation-monitoring
- social-media-minimization
- employee-profile-osint
- event-osint
- screenshot-leakage
- platform-abuse-reporting

## Referencias

- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Ética / Seguridad:** EFF Surveillance Self-Defense — https://ssd.eff.org/
