# OSINT Triage

## Definición

El triaje de OSINT es el proceso de convertir pistas crudas de fuentes públicas en uno de cinco resultados: un hallazgo verificado, una afirmación probable pero no corroborada, una pista incierta que necesita más trabajo, ruido descartado o un elemento sensible que requiere manejo especial. Es la capa entre la recopilación y el informe, y la capa que separa la investigación del apilamiento de links.

## Por qué importa

Las fuentes públicas son ruidosas, obsoletas, duplicadas, atribuidas a la entidad equivocada y a veces deliberadamente engañosas. Sin triaje, una investigación se convierte en una carpeta de capturas de pantalla cuyo dueño no puede recordar qué prueba cada una. El triaje preserva la calidad de la evidencia, previene exagerar y es el artefacto que permite a un segundo analista rerecorrer el trabajo.

En OSINT adversarial (bug bounty, reconocimiento en pentest, threat intel), el mal triaje causa testing del objetivo incorrecto — un error de $0 en papel, un error legal real en la práctica. En OSINT defensivo, el mal triaje hace que un equipo persiga filtraciones fantasma y se pierda las reales.

## Cómo funciona

El triaje de OSINT asigna cada pista a uno de **5 buckets**. Cada bucket implica una próxima acción diferente.

1. **Verificado.** Respaldado por evidencia corroborante independiente. Seguro para actuar o incluir en un informe como hecho. Una afirmación es verificada, no una fuente.
2. **Probable.** Señal fuerte de fuente única pero sin corroboración independiente aún. Puede aparecer en un informe como "probable" con etiquetado de confianza. Impulsa una tarea de corroboración, no un ticket de remediación.
3. **Incierto.** Plausible pero ambiguo — colisiones de identidad, archivos obsoletos, fuentes en conflicto. Impulsa una tarea "qué evidencia resolvería esto", no una conclusión.
4. **Ruido.** Duplicado, irrelevante, falso positivo o fuera de scope. Descartado con un motivo registrado para que la misma pista no se redescubra más tarde.
5. **Sensible.** Datos personales, credenciales u otro material restringido. Requiere minimización, manejo restringido, límite de retención y a menudo escalación antes de trabajo adicional.

El bug es tratar cada resultado de búsqueda como evidencia. El triaje fuerza cada pista a través de una pregunta explícita: **¿qué prueba esta pista y qué no prueba aún?**

Un ejemplo corto trabajado: un resultado de `crt.sh` dice `api-staging.example.com`. Buckets posibles:

```
solo entrada crt.sh                                    → probable (fuente única, certs pueden emitirse sin deploy)
crt.sh + archive.org last-seen 2025-09 + DNS A         → verificado
crt.sh + DNS NXDOMAIN hoy                              → incierto (cert existe, nombre ya no resuelve)
resultado crt.sh de subsidiaria de marca hermana       → ruido (fuera de scope)
resultado crt.sh con email de empleado en CN           → sensible (minimizar)
```

La misma pista vive en distintos buckets dependiendo de qué otra evidencia existe.

## Técnicas / patrones

Las técnicas de triaje se agrupan alrededor de los tipos de falsos positivos que produce cada fuente pública:

- **Dominios duplicados, alias, URLs archivadas.** El mismo activo aparece bajo múltiples nombres en historial de DNS, certificate transparency y snapshots de archivo.
- **Páginas obsoletas y documentos en caché.** Una página en `archive.org` puede no haber respondido en años; tratala como pista histórica, no estado actual.
- **Colisiones de identidad en nombres comunes.** Nombres de usuario comunes, locales de email y nombres personales coinciden con muchas personas; corroborá rol + empleador + período de tiempo antes de vincular.
- **Menciones de brechas y emails reutilizados.** Una mención de un email corporativo en una brecha de terceros no prueba que el sistema corporativo fue vulnerado; prueba que el email fue usado en otro lado.
- **Capturas de pantalla, imágenes, metadatos.** El EXIF puede ser eliminado, falsificado u obsoleto; la búsqueda inversa de imágenes corrobora mejor que una sola captura.
- **Etiquetas de output de herramientas.** Las etiquetas de enriquecimiento ("malicioso", "vinculado al actor X") son pistas, no hechos; promoverlas a verificado solo con corroboración independiente.

## Variantes y bypasses

El triaje tiene **5 modos de falla**. Cada uno tiene un olor reconocible.

### 1. Colisión de identidad

Dos personas, empresas, cuentas o dominios parecen relacionados pero no lo están. Los nombres comunes y los dominios similares a marcas impulsan la mayoría de estos. Olor: la evidencia es "coincidencia de nombre" sin corroboración de rol, período de tiempo o propiedad. Resolvé agregando un segundo eje (empleador + período, ASN + propiedad, registrador + historial WHOIS).

### 2. Desplazamiento de fuente obsoleta

Las páginas viejas, los archivos y los certificados históricos describen un estado pasado como si fuera actual. Olor: la única evidencia tiene un timestamp mayor a 12 meses y no tiene confirmación DNS o HTTP actual. Resolvé etiquetando explícitamente como "pista histórica" y requiriendo una corroboración de estado actual antes de promover a verificado.

### 3. Sobreconfianza en output de herramientas

Las etiquetas de enriquecimiento automatizado (etiquetas de Shodan, puntuaciones de threat-intel, puntuaciones de correlación de brechas) se tratan como verdad en lugar de pistas. Olor: la única evidencia del informe es "la herramienta lo dice". Resolvé exigiendo la observación subyacente detrás de la etiqueta y corroborando con una fuente independiente.

### 4. Scope creep

La investigación recopila datos interesantes-pero-irrelevantes porque es fácil encontrarlos. Olor: la tabla de fuentes contiene afirmaciones que no mapean de vuelta a la pregunta original. Resolvé releyendo la pregunta y descartando pistas que no la hacen avanzar.

### 5. Mal manejo de datos sensibles

Los datos personales o filtrados se recopilan sin necesidad ni controles. Olor: el workspace contiene información personal más allá de lo que requiere la pregunta, o contiene credenciales en texto plano. Resolvé minimizando en la recopilación (redactá en la ingesta), aplicando límites de retención y escalando antes de trabajo adicional en el subconjunto sensible.

## Impacto

Ordenado aproximadamente por severidad:

- **Conclusiones falsas.** El mal triaje crea informes incorrectos, atribución incorrecta, prioridades de remediación incorrectas.
- **Testing del objetivo incorrecto.** La propiedad ambigua combinada con triaje débil lleva a testing fuera de scope — una exposición legal real en pentests y trabajo de bug bounty.
- **Daño a la privacidad.** Los datos enfocados en personas mal manejados crean daño real a los sujetos y riesgo reputacional/legal para la organización del analista.
- **Tiempo del analista desperdiciado.** El ruido consume esfuerzo que debería ir a corroborar pistas reales.
- **Mejor evidencia.** Por el contrario, el buen triaje hace los informes defendibles, repetibles y accionables — el lado positivo que paga toda la disciplina.

## Detección y defensa

Las defensas aquí se tratan de preservar la trazabilidad, no de bloquear atacantes.

1.
**Rastreá afirmaciones separadas de fuentes.**
   Una fuente contiene datos; una afirmación es tu interpretación. Las tablas que conflactan los dos crean informes que no pueden ser rerecorridos. Dos columnas, siempre: URL fuente + timestamp, y la afirmación derivada de ella.

2.
**Requerí corroboración para afirmaciones importantes.**
   Usá fuentes independientes antes de promover una pista de "probable" a "verificado". "Independiente" significa un origen de datos diferente, no la misma fuente reflejada en otro lugar — una entrada `crt.sh` y una entrada SSL Labs ambas leen certificate transparency.

3.
**Usá etiquetas de confianza.**
   Marcá cada afirmación verificada, probable, incierta, obsoleta o ruido. La etiqueta es el artefacto cargado: una afirmación verificada impulsa remediación, una probable impulsa una tarea de corroboración, una obsoleta impulsa una verificación de obsolescencia.

4.
**Minimizá datos sensibles.**
   Quedate solo con lo que responde la pregunta. Redactá lo que no se necesita. Cifrá en reposo. Aplicá un límite de retención. Escalá antes de trabajar con credenciales filtradas, independientemente de cómo ocurrió el acceso.

5.
**Registrá timestamps y contexto de acceso.**
   Los datos públicos se desplazan en horas. El timestamp de la recopilación, el resolver utilizado y el user agent importan cuando una afirmación se disputa más tarde — sin ellos, la evidencia no puede reproducirse.

### Qué no funciona como defensa primaria

- **Capturas de pantalla sin URLs fuente.** La evidencia necesita procedencia; una captura sola no puede ser rerecorrida.
- **Output de herramientas sin validación.** Las herramientas producen pistas, no verdad. La confianza de la herramienta no es tu confianza.
- **Asumir nombres únicos.** Nombres, handles y dominios colisionan. Siempre corroborá en un segundo eje.
- **Guardar todo "por si acaso".** La retención crea riesgo legal y de privacidad y esconde señal en ruido.
- **Triaje en tiempo real.** Triá al final de una ráfaga de recopilación, no durante; el triaje en vuelo se pierde duplicados.

## Labs prácticos

Usá un sujeto público propio o seleccionado deliberadamente. Ninguno de estos labs envía paquetes al objetivo — son disciplina de hoja de cálculo/cuaderno.

### Construí un tablero de triaje

```
pista            | fuente                   | timestamp           | afirmación                      | confianza | sensibilidad | próxima acción
api-staging.x.y  | crt.sh #98231            | 2026-04-29T18:00Z   | api-staging.x.y tenía cert emitido | probable  | ninguna     | corroborar vía dig + archive
old-blog.x.y     | archive.org 2021-03      | 2026-04-29T18:01Z   | old-blog.x.y existía en 2021    | obsoleto  | ninguna      | marcar ruido, registrar motivo
admin@x.y        | HIBP Pwned Passwords     | 2026-04-29T18:02Z   | email corporativo en 3rd-party  | probable  | sensible     | minimizar, escalar a IR
```

Mové cada pista a una decisión. Una pista que vive sin bucket se convierte en una conclusión incorrecta.

### Corroborá una afirmación de propiedad de dominio

```
# Fuente 1: certificate transparency
curl -s 'https://crt.sh/?q=example.com&output=json' | jq '.[0:5]'

# Fuente 2: WHOIS/RDAP para campo de organización
whois example.com | grep -iE 'organization|registrant|registrar'

# Fuente 3: archive.org last-seen
curl -s "http://archive.org/wayback/available?url=example.com" | jq .
```

Tres orígenes independientes → "verificado". Dos del mismo origen → sigue siendo "probable".

### Marcá datos obsoletos explícitamente

```
Página archivada de 2020:         pista histórica, no prueba actual
Cert emitido 2019, nunca renovado: existencia histórica, NXDOMAIN hoy
Publicación de trabajo de 2018:   rol histórico, puede no reflejar stack actual
```

Los datos viejos son útiles, pero no deben hacerse pasar por estado actual en el informe.

### Resolvé una colisión de identidad

```
Pista:  "John Smith @ ExampleCorp" aparece en tres foros.
Eje 1 (nombre):     colisiona con miles de personas
Eje 2 (empleador):  un rol de LinkedIn corroborador 2022-presente
Eje 3 (log de commits): email GitHub coincide con perfil público, repos coinciden con foco del equipo
Decisión:           probable (dos ejes corroboran, tercero es fuente única)
```

Las coincidencias de identidad de eje único permanecen en "incierto" hasta que un segundo eje corrobore.

### Marcá elementos sensibles en la ingesta

```
Campo       | ¿Recopilado? | ¿Almacenado? | Retención
Nombre      | sí           | sí           | fin de la investigación
Email       | sí           | hasheado     | fin de la investigación
Contraseña  | NUNCA        | NUNCA        | NUNCA
Texto plano | redactar     | redactado    | escalar antes del almacenamiento
```

El triaje de sensibilidad ocurre antes de que los datos lleguen al workspace, no después.

## Ejemplos prácticos

- Un perfil de LinkedIn sugiere una elección de tecnología, pero una publicación de trabajo y una charla pública la corroboran antes de que aparezca en el informe.
- Un endpoint archivado existe históricamente pero ya no resuelve; es una pista obsoleta, no un activo actual.
- Un nombre de usuario común pertenece a múltiples personas; sin empleador + período de tiempo, la coincidencia es "incierta".
- Una mención de brecha nombra a una empresa pero no expone credenciales actuales; la afirmación es "exposición de terceros", no "sistema vulnerado".
- Un nombre de certificado sugiere una marca adquirida que necesita validación de scope antes de que cualquier reconocimiento activo se acerque.
- La coordenada GPS EXIF de una foto ubica la imagen en una instalación específica, corroborada por una estimación de ángulo solar de hora del día; ambos ejes promueven la afirmación de "probable" a "verificado".

## Notas relacionadas

- [[osint]]
- [[osint-reporting]]
- [[search-engine-operators]]
- [[breach-and-leak-intelligence]]
- [[company-osint]]
- [[scope-validation|Scope Validation]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

### Notas atómicas futuras sugeridas

- source-reliability-grading
- osint-evidence-handling
- sensitive-data-minimization
- false-positive-triage
- osint-confidence-levels
- corroboration-axes

## Referencias

- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
