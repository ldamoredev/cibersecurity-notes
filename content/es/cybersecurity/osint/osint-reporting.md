# OSINT Reporting

## Definición

El informe OSINT es el proceso de convertir la recopilación, el triaje y el análisis en un informe claro y respaldado por evidencia con **hechos e inferencias separados, niveles de confianza, manejo de sensibilidad, scope y limitaciones, y próximas acciones concretas**. Es el artefacto de cierre de toda investigación OSINT — el entregable que decide si el trabajo cambia algo.

## Por qué importa

OSINT solo es útil cuando alguien puede confiar en él y actuar en consecuencia. Sin disciplina de informe, una investigación se convierte en una carpeta de links y capturas de pantalla que nadie puede rerecorrer, auditar o escalar. Los buenos informes previenen exagerar, preservan la procedencia, separan hechos verificados de inferencias, documentan los límites de privacidad y scope, y rutar los hallazgos hacia validación, remediación, monitoreo o descarte.

Un informe que otro analista puede rerecorrer es el artefacto cargado de todo el pipeline OSINT. También es el artefacto que protege al analista — las etiquetas de confianza explícitas, las declaraciones de scope y las decisiones de minimización son lo que aguanta bajo revisión cuando se cuestionan las conclusiones.

Los tres modos de falla que el buen informe previene:
- **Exagerar** — afirmaciones de fuente única promovidas a "verificado" sin corroboración.
- **Daño a la privacidad** — los datos sensibles se acumulan en el workspace e informe en lugar de minimizarse en la ingesta.
- **Inercia** — los hallazgos sin enrutamiento de próxima acción se vuelven obsoletos en semanas.

## Cómo funciona

Un informe OSINT tiene **7 partes**. Saltarse cualquiera de ellas crea un modo de falla conocido.

1. **Pregunta.** Qué intentó responder la investigación. Una oración, acotada, con un entregable. Saltarse → los informes derivan en dossiers sin foco.
2. **Scope.** Sujetos permitidos, fuentes permitidas, límites estrictos, límites éticos/legales. Saltarse → trabajo fuera de scope y sobre-recopilación de datos personales.
3. **Método.** Cómo se recopiló la información, incluyendo la disciplina (solo pasivo, sin sondas SMTP, etc.). Saltarse → los hallazgos no pueden replicarse o auditarse.
4. **Hallazgos.** Afirmaciones respaldadas por evidencia. Cada hallazgo empareja una afirmación con fuentes, timestamps y una etiqueta de confianza. Saltarse → narrativa sin trazabilidad.
5. **Confianza.** Qué tan fuertemente está respaldado cada hallazgo (verificado / probable / incierto / obsoleto). Saltarse → los lectores no pueden calibrar las decisiones.
6. **Sensibilidad.** Datos personales, datos filtrados o riesgo operacional que requiere manejo restringido. Saltarse → los informes se convierten en vectores de filtración secundaria.
7. **Acciones.** Qué validar, remediar, monitorear o descartar. Saltarse → los hallazgos se pudren en dashboards.

El bug es **reportar links crudos sin análisis**. Un informe debería explicar qué significa la evidencia, qué no significa y qué hacer al respecto.

Un esqueleto de ejemplo trabajado:

```
Pregunta:    Mapeá la superficie externa de Example Corp y marcá activos obsoletos/expuestos.
Scope:       solo scope propio/autorizado; fuentes pasivas; sin sondas activas.
Método:      cert transparency, snapshots de archivo, inspección CNAME, crosscheck del campo "O=" del cert.
Hallazgos:   23 nombres primarios verificados, 9 hosted por vendor, 4 probable-obsoletos, 2 propiedad desconocida.
Confianza:   filas verificadas ≥3 fuentes; filas probables = 2 fuentes; incierto = 1 fuente.
Sensibilidad: baja (solo mapa de activos; sin datos personales; sin credenciales manejadas).
Acciones:    [validar 4 obsoletos → equipo de propiedad], [scope-check 2 desconocidos → legal], [sin acción en verificados].
```

El esqueleto cabe en una sola página; la profundidad vive en las tablas de hallazgos que indexa.

## Técnicas / patrones

La disciplina es uniforme en todos los tipos de informe.

- **URLs fuente, timestamps, capturas de pantalla** capturadas en el momento de la recopilación (los datos públicos se desplazan).
- **Tablas afirmación/evidencia/confianza** como formato canónico de hallazgos.
- **Decisiones de minimización de datos sensibles** registradas en el informe (qué no se recopiló y por qué).
- **Estado actual vs histórico** etiquetado explícitamente — la evidencia de archive.org es histórica a menos que sea corroborada el estado actual.
- **Suposiciones e incógnitas** declaradas explícitamente (p.ej., "la propiedad de `legacy.example.io` no pudo confirmarse vía fuentes públicas").
- **Próximos pasos recomendados** enrutados a un propietario nombrado con un artefacto de seguimiento.
- **Pasos de reproducción seguros** para los defensores, para que la misma investigación pueda volver a ejecutarse con una cadencia.

## Variantes y bypasses

El informe OSINT se agrupa en **5 tipos de informe**. Cada uno tiene un perfil diferente de audiencia y profundidad.

### 1. Informe de superficie de ataque

Activos públicos, vendors, endpoints y desplazamiento de exposición. Audiencia: ingeniería de seguridad y propietarios de gestión de activos. Longitud: 2-10 páginas dependiendo del tamaño de la superficie. La tabla de hallazgos es el artefacto dominante.

### 2. Informe de perfil de empresa

Marcas, dominios, propiedad, vendors y pistas públicas de tecnología. Audiencia: scope/legal y liderazgo de seguridad. Output de [[company-osint]]. Usado para acotar el testing activo y el scope de cumplimiento.

### 3. Informe de exposición de filtraciones

Indicadores de brechas, secretos públicos y prioridades de remediación. Audiencia: respuesta a incidentes y equipo de identidad. Crítico: separa indicadores de contenidos (ver [[breach-and-leak-intelligence]]). El registro de acciones es obligatorio.

### 4. Informe de verificación de medios

Hallazgos de imagen, ubicación, línea temporal y contexto de fuente. Audiencia: equipo de incidentes, comunicaciones o investigativo. La corroboración multicapa es obligatoria; las afirmaciones de ubicación de capa única deben etiquetarse "probable" como máximo.

### 5. Memo de triaje

Informe corto (una a dos páginas) que enruta pistas hacia validación o descarta ruido. Audiencia: la propia cola del analista. Usado entre investigaciones más profundas para mantener el pipeline de pistas en movimiento.

## Impacto

Ordenado aproximadamente por severidad:

- **Remediación accionable.** Los defensores pueden arreglar la exposición cuando los hallazgos llevan evidencia y confianza.
- **Mejores decisiones de scope.** Las etiquetas de propiedad y confianza hacen los límites de scope revisables.
- **Riesgo de privacidad reducido.** Las decisiones de minimización documentadas muestran a los revisores que el analista eligió qué no recopilar.
- **Investigación repetible.** Las fuentes, timestamps y método preservan la trazabilidad de auditoría.
- **Compounding de conocimiento.** Los informes se convierten en material de wiki/fuente futuro; un informe bien escrito es un artefacto duradero, no de un solo uso.

## Detección y defensa

Las defensas aquí se tratan de **preservar la honestidad y forzar el cierre**.

1.
**Separar hecho, inferencia y recomendación.**
   Tres columnas o tres secciones, nunca mezcladas. Un lector debería poder estar en desacuerdo con la inferencia sin disputar el hecho.

2.
**Incluir confianza y limitaciones.**
   La incertidumbre no es debilidad. Una afirmación etiquetada "probable" con limitaciones declaradas impulsa una tarea de corroboración; una afirmación "verificado" exagerada impulsa una decisión incorrecta.

3.
**Minimizá los datos sensibles en el informe mismo.**
   Registrá suficiente para actuar, no suficiente para crear una nueva filtración. Indicadores y registros de acciones, no credenciales crudas ni dossiers personales completos.

4.
**Preservá la procedencia de las fuentes.**
   URL, timestamp, método de captura y contexto por afirmación. Una afirmación sin procedencia no es evidencia.

5.
**Terminá con próximas acciones.**
   Cada informe termina con una decisión de enrutamiento: validar, remediar, monitorear o descartar. Los hallazgos sin enrutamiento se vuelven obsoletos en semanas y se redescubren más tarde como si fueran nuevos.

### Qué no funciona como defensa primaria

- **Solo capturas de pantalla.** Necesitan URL fuente, timestamp y método de captura; las capturas sin procedencia no pueden ser rerecorridas.
- **Dumps de links.** No explican la significancia y no sobreviven la revisión.
- **Certeza exagerada.** Los datos públicos son a menudo obsoletos o ambiguos; las etiquetas de confianza calibradas son honestas, la sobreconfianza es una responsabilidad.
- **Incluir secretos filtrados crudos en el informe.** Los informes nunca deben convertirse en artefactos sensibles secundarios.
- **Hallazgos abiertos "para tu conciencia".** Si no hay acción recomendada, el hallazgo no pertenece al informe.

## Labs prácticos

Usá una pequeña auto-auditoría o una investigación OSINT real que ya hayas hecho.

### Escribí una tabla afirmación/evidencia

```
afirmación                               | evidencia                      | timestamp           | confianza | limitación                            | acción
api-staging.example.com está activo      | respuesta dig A + match cert SAN | 2026-04-29T18:00Z  | verificado | ninguna                               | ninguna (en scope)
legacy.example.io es adquisición-obsoleta| archive.org solo 2019-2024     | 2026-04-29T18:01Z  | probable   | propiedad actual no confirmada        | enrutar a equipo de propiedad
support.example.com hosted por vendor    | CNAME → zendesk + cert SAN     | 2026-04-29T18:02Z  | verificado | límite de tenant dentro del vendor opaco | marcar en mapa de terceros
post foro "filtración example"           | URL foro + timestamp           | 2026-04-29T18:03Z  | incierto   | no se proveyó muestra                 | corroborar, no descargar
```

Cada afirmación tiene evidencia y una etiqueta de confianza. Las inferencias viven en una columna separada.

### Marcá la sensibilidad a nivel del informe

```
clase                          | sensibilidad | almacenamiento          | retención
datos públicos de negocio      | baja         | workspace compartido    | indefinida (pública)
contacto funcional de empleado | baja         | workspace compartido    | fin de investigación
contacto personal de empleado  | media        | workspace restringido   | fin de investigación
indicador de brecha (solo count) | media      | workspace restringido   | fin de investigación + 30d
material de credenciales       | alta         | rotar-no-almacenar      | NUNCA almacenar crudo
datos de ubicación personal    | alta         | minimizar en ingesta    | solo si acotado + justificado
```

La sensibilidad afecta el almacenamiento y el intercambio; la tabla es el artefacto que verifican los revisores.

### Terminá cada informe con enrutamiento de acciones

```
hallazgo                                  | acción                                  | propietario       | seguimiento
4 dominios de propiedad desconocida       | scope-validar contra entidad legal      | legal/asset-mgmt  | TICKET-A
subdominio de legacy-brand sigue resolviendo | descomisionar o documentar como legacy | sre/network       | TICKET-B
3 cuentas de empleados en brecha de 2020  | reset de contraseña + aplicación de MFA | equipo de identidad | INC-C
1 source map expuesto en producción       | eliminar del pipeline de build          | equipo de plataforma | TICKET-D
```

Un informe sin acciones enrutadas es un borrador, no un entregable.

### Recorrido del informe con un revisor par

```
preguntas del revisor para responder
- ¿puedo distinguir qué oraciones son hechos vs inferencias?
- ¿puedo rerecorrer cada afirmación desde las fuentes citadas?
- ¿está la etiqueta de confianza justificada por la evidencia mostrada?
- ¿hay algo sensible en el informe que no debería estar?
- ¿tiene cada hallazgo una acción enrutada con un propietario?
```

La revisión por pares atrapa los modos de falla que el analista no verá en su propio trabajo.

### Archivá el informe y el material fuente correctamente

```
archivo del informe:        compartir con acceso adecuado a la audiencia (solo lectura)
capturas de evidencia:      guardar originales con timestamp (URL + headers si HTTP)
subconjunto sensible:       workspace restringido, límite de retención aplicado
registro de acciones:       rastreado en sistema IR/ticketing, no solo el informe
plan de eliminación:        qué se elimina en el vencimiento de retención, quién confirma
```

La disciplina de archivo es lo que separa una investigación única de un artefacto de conocimiento duradero.

## Ejemplos prácticos

- Un informe de huella pública mapea dominios, vendors y activos de staging, con etiquetas de confianza enrutando 4 entradas de propiedad desconocida a legal.
- Un memo de exposición de filtraciones registra 23 cuentas afectadas y recomienda aplicación de MFA acotada y rotación de tokens, con un registro de acciones de 30 días.
- Una nota de verificación de imagen lista la confianza de ubicación como "probable" con limitaciones declaradas, negándose a publicar coordenadas exactas.
- Un informe de company OSINT separa dominios primarios verificados de superficies hosted por vendors y activos legacy de desplazamiento de adquisición.
- Un memo de triaje descarta 23 endpoints ruidosos solo-de-archivo con códigos de motivo registrados para que no se redescubran más tarde.
- Un recorrido de revisión por pares atrapa una etiqueta "verificado" exagerada que debería haber sido "probable" y una URL fuente obsoleta sin corroboración actual.

## Notas relacionadas

- [[osint]]
- [[osint-triage]]
- [[company-osint]]
- [[breach-and-leak-intelligence]]
- [[image-and-location-osint]]
- [[email-and-phone-osint]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

### Notas atómicas futuras sugeridas

- osint-case-file
- evidence-screenshots
- confidence-language
- sensitive-report-redaction
- public-footprint-reporting
- osint-peer-review
- report-retention-policy

## Referencias

- **Fundamental:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OSINT Framework — https://osintframework.com/
