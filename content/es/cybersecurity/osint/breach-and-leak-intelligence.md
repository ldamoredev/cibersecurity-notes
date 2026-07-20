# Breach and Leak Intelligence

## Definición

La Breach and Leak Intelligence es la práctica OSINT de identificar indicadores públicos de que cuentas, dominios, credenciales, documentos, código o sistemas pueden haber aparecido en brechas, paste sites, repositorios públicos o datasets expuestos. La salida es una lista triada de indicadores vinculados a **acciones de remediación específicas**, no una carpeta de datos filtrados.

## Por qué importa

Las señales de filtraciones cambian las prioridades de seguridad. Una exposición de credenciales confirmada fuerza un reset de contraseña; una exposición de API token confirmada fuerza la rotación del token y la revocación de sesiones; una exposición de documento confirmada desencadena una revisión de respuesta a incidentes. Sin breach intelligence, las organizaciones rotan credenciales reactivamente después de un compromiso en lugar de hacerlo proactivamente después de una exposición.

El movimiento peligroso es tratar los datos filtrados casualmente. Los indicadores de brechas deben ser **acotados, mínimos y manejados como material sensible**. Almacenar dumps crudos crea riesgo legal, ético y de manejo de datos mucho más allá de la exposición original. El objetivo es saber que el indicador existe y actuar en consecuencia — no recopilar el contenido.

La asimetría: las organizaciones rara vez saben sobre una brecha hasta que emergen indicadores externos. El OSINT defensivo de brechas cierra esa brecha tratando los feeds de filtraciones públicos como un canal de advertencia temprana gratuito.

## Cómo funciona

El OSINT de brechas/filtraciones procesa **5 tipos de señal**. Cada uno desencadena una pista de remediación diferente.

1. **Exposición de cuenta.** Emails o nombres de usuario aparecen en índices de brechas (HIBP, listados de dumps públicos). Desencadena reset de contraseña y aplicación de MFA para las cuentas afectadas.
2. **Exposición de credenciales.** Contraseñas, hashes, tokens, API keys o cookies de sesión se exponen en repositorios, pastes o dumps de brechas. Desencadena rotación inmediata y revocación de sesiones; **no debatir si la credencial fue usada**.
3. **Exposición de documentos.** Archivos internos, logs, backups o exportaciones se vuelven públicos vía almacenamiento mal configurado, errores indexados o dumps de terceros. Desencadena respuesta a incidentes, revisión de clasificación de datos y eliminación de la fuente.
4. **Exposición de repositorios.** Código, configs, secretos o nombres de infraestructura se filtran vía commits públicos, errores de fork o mirrors abiertos. Desencadena rotación de secretos y revisión de historial `git` (la rotación sola no elimina el secreto del historial).
5. **Exposición de terceros.** Los incidentes de vendor o SaaS exponen datos relacionados (cuentas de empleados en una herramienta de terceros, datos de clientes vía una brecha de vendor). Desencadena revisión de riesgo de vendor y rotación de credenciales downstream.

El bug no es "existe un resultado de brecha". La tarea OSINT es **decidir si la señal es relevante, actual, sensible y accionable** — y vincularla a un propietario de remediación.

Un ejemplo trabajado:

```
Indicador:    HIBP devuelve 23 emails de empleados en la colección "Cit0day" 2020.
Sensibilidad: bucket sensible — contiene hashes (según metadatos de HIBP).
Acción 1:     forzar reset de contraseña en las 23 cuentas (el riesgo de reutilización de contraseña es la amenaza).
Acción 2:     verificar si alguno de los 23 es admin/privilegiado → 2 lo son; rotar tokens de sesión.
Acción 3:     aplicar MFA para los grupos de rol afectados.
Almacenado:   nombre de brecha, fecha, conteo de cuentas, registro de acciones. Sin contraseñas crudas.
```

El artefacto OSINT es el registro de acciones, no los datos de la brecha.

## Técnicas / patrones

La disciplina es uniforme entre tipos de señal: **encontrar indicador → triar → minimizar → actuar → registrar**.

- **Indicadores de brechas de email por dominio** vía APIs `breachedaccount` y `domainsearch` de HIBP.
- **Menciones de pasta/repositorio públicos de dominios o tokens** vía scanners de secretos (gitleaks, trufflehog) contra repos propios y vía GitHub code search para menciones no propias.
- **API keys y credenciales cloud expuestas** vía firmas de patrones de secretos (`AKIA[0-9A-Z]{16}`, GitHub PATs, keys GCP, webhooks Slack).
- **Dumps y backups de documentos públicos** vía [[google-dorking|Google dorking]] y monitoreo de archivos.
- **Avisos de brechas de vendors** vía feeds de seguridad de vendors, avisos ENISA/CISA y divulgaciones de brechas públicas.
- **Señales de riesgo de reutilización de contraseñas repetidas** vía HIBP `Pwned Passwords` (API de k-anonimidad; nunca enviar contraseñas completas).

## Variantes y bypasses

La breach intelligence tiene **5 clases de manejo**. Cada clase implica una disciplina diferente de evidencia y almacenamiento.

### 1. Señal pública de índice de brechas

Un servicio reputado informa que una cuenta o dominio aparece en una brecha conocida. Evidencia: nombre de brecha, fecha, clases de datos, confiabilidad de la fuente. Almacenamiento: indicador + registro de acciones, nunca contraseñas crudas. Acción: reset de contraseña + aplicación de MFA acotada a las cuentas afectadas.

### 2. Exposición pública de secretos

Tokens, API keys o credenciales aparecen en repositorios públicos, pastes o documentos. Evidencia: URL fuente, hash de commit, timestamp, el patrón del secreto (no el secreto completo en almacenamiento de largo plazo). Acción: **rotación inmediata, luego revisión forense** — rotación primero, limpieza del historial segundo, investigación "¿alguien lo usó?" tercero.

### 3. Filtración histórica

Los datos viejos pueden seguir siendo relevantes si las contraseñas, emails o patrones de nombres persisten. Evidencia: antigüedad de la brecha, indicadores de persistencia (convenciones de nombres aún actuales, cuentas aún activas). Acción: tratar como exposición actual si cualquier indicador sigue siendo relevante; no descartar porque la brecha sea antigua.

### 4. Filtración de terceros

Un incidente de vendor afecta datos o cuentas del objetivo. Evidencia: divulgación del vendor, clases de datos afectados, indicador de que el objetivo está en scope. Acción: revisión de riesgo de vendor, rotación de credenciales downstream para cuentas que usaron el vendor, notificación al cliente si aplica.

### 5. Afirmación no verificada

Un foro, paste o post afirma una filtración pero carece de corroboración. Evidencia: ubicación de la afirmación, timestamp, cualquier muestra provista. Acción: **corroborar antes de escalar**; muchas afirmaciones de "filtración" son recicladas, falsas o agregaciones de datos más antiguos. No descargar muestras casualmente.

## Impacto

Ordenado aproximadamente por severidad:

- **Riesgo de account-takeover.** Las contraseñas reutilizadas o credenciales activas en dumps habilitan compromiso directo.
- **Compromiso de cloud o API.** Los tokens expuestos pueden otorgar acceso programático directo; el impacto depende del scope del token.
- **Divulgación de datos sensibles.** Los documentos, exportaciones y backups filtran información de clientes o interna.
- **Habilitación de ingeniería social.** El contexto filtrado (org charts, terminología interna, relaciones con vendors) agudza el phishing y pretexting.
- **Desencadenador de respuesta a incidentes.** Incluso las filtraciones obsoletas requieren verificación, registro de acciones y limpieza.

## Detección y defensa

Las defensas priorizan **rotation-first, investigation-second** y minimización a lo largo.

1.
**Tratá las credenciales y tokens filtrados como comprometidos.**
   Rotá secretos y revocá sesiones antes de debatir si fueron usados. La investigación puede correr en paralelo; la rotación no puede esperar a que la investigación termine.

2.
**Usá monitoreo de dominio y secret scanning.**
   El monitoreo de brechas a nivel dominio (HIBP, feeds de vendors) y el secret scanning en repositorios (integrado en CI, programado) alimentan indicadores directamente a la respuesta a incidentes. Los sweeps manuales no capturan nada en tiempo real.

3.
**Minimizá el manejo de datos filtrados crudos.**
   Almacená el indicador y el registro de acciones; evitá almacenar contraseñas crudas, dumps completos o documentos sensibles. Aplicá límites de retención. Cifrá en reposo.

4.
**Corroborá afirmaciones no verificadas antes de escalar.**
   Los rumores de filtraciones son comunes. La calidad de la evidencia importa; un post de foro sin muestra es una pista, no un incidente.

5.
**Conectá los hallazgos de filtraciones a MFA, reset de contraseñas y capacitación.**
   La breach intelligence solo es útil cuando cambia controles. Vinculá cada indicador confirmado a un cambio de control rastreado, no a una captura de pantalla de Slack.

### Qué no funciona como defensa primaria

- **Ignorar brechas antiguas.** Las contraseñas, emails y patrones de nombres viejos pueden seguir habilitando ataques hoy.
- **Descargar dumps completos casualmente.** Eso crea riesgo legal, ético y de manejo de datos mucho más allá de la exposición original.
- **Confiar solo en cambios de contraseña de usuarios.** Los tokens, API keys, OAuth refresh tokens y sesiones activas necesitan rotación separada.
- **Tratar todas las afirmaciones de filtraciones como verdaderas.** Las afirmaciones necesitan corroboración; las filtraciones recicladas y falsas son comunes.
- **Almacenar el contenido de la brecha para "investigar más tarde".** Los plazos de investigación se alargan; los datos sensibles se acumulan; el próximo incidente es tu propio fallo de manejo de datos.

## Labs prácticos

Usá tus propias cuentas, dominios propios o monitoreo defensivo autorizado. Nunca consultes emails o dominios de terceros sin autorización.

### Construí una tabla de triaje de filtraciones

```
indicador         | fuente       | timestamp           | sensibilidad | confianza | acción               | propietario
admin@example.com | HIBP Cit0day | 2026-04-29T18:00Z  | sensible     | verificado | reset+MFA+sesión     | sec-eng
AKIA... en repo   | gitleaks CI  | 2026-04-29T18:01Z  | sensible     | verificado | rotar token ahora    | sre
"filtración example" | afirmación foro | 2026-04-29T18:02Z | sensible  | incierto   | corroborar, no DL    | sec-eng
```

Separar el indicador crudo (sensible) del registro de acciones (operacional).

### Verificá un dominio en HIBP de forma segura

```
# La búsqueda de dominio requiere propiedad verificada y una API key.
# Devuelve solo nombre-de-brecha + conteos de lista-de-emails — sin contraseñas en texto plano.
curl -s -H "hibp-api-key: $HIBP_API_KEY" -H "user-agent: example-sec-eng" \
  "https://haveibeenpwned.com/api/v3/breaches?domain=example.com"
```

Registrá nombre de brecha, fecha, clases de datos y acción de remediación — nunca credenciales crudas.

### Verificá una contraseña contra `Pwned Passwords` con k-anonimidad

```
# Hashear localmente, enviar solo los primeros 5 caracteres hex (k-anonimidad).
HASH=$(printf '%s' 'somepassword' | shasum -a 1 | awk '{print toupper($1)}')
PREFIX="${HASH:0:5}"
SUFFIX="${HASH:5}"
curl -s "https://api.pwnedpasswords.com/range/$PREFIX" | grep -i "^$SUFFIX"
```

Nunca envíes una contraseña completa a un servicio remoto. La API de k-anonimidad existe precisamente para que no tengas que hacerlo.

### Buscá secretos en repos propios

```
# sweep ripgrep
rg -nP '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|api_key\s*=\s*["\x27])' .

# gitleaks (consciente del historial)
gitleaks detect --source . --redact --report-format json --report-path gitleaks.json
```

Rotá cada hit real antes de limpiar el historial. Rotación primero; `git filter-repo` segundo; investigación tercero.

### Verificá que la rotación realmente invalidó la credencial vieja

```
# Después de rotar, el token viejo debería fallar ahora.
curl -i -H "Authorization: Bearer $OLD_TOKEN" https://api.example.com/v1/whoami
# Esperá 401 Unauthorized.
```

Una rotación que no invalida la credencial vieja no es una rotación.

## Ejemplos prácticos

- Un dominio de empresa aparece en resultados HIBP para una brecha reciente; 23 emails de empleados están afectados, desencadenando reset de contraseña y aplicación de MFA acotada a esas cuentas.
- Un repo público contiene una AWS access key `AKIA` en `.env.example`; la rotación es inmediata, la limpieza del historial sigue y la revisión de CloudTrail verifica el uso.
- Un paste antiguo contiene hostnames internos que coinciden con una convención de nombres actual, sugiriendo que los atacantes pueden predecir nuevos nombres.
- Una brecha de vendor incluye datos de contacto de empleados; la revisión de riesgo de vendor identifica todos los empleados con cuentas de vendor y rota credenciales downstream.
- Un documento filtrado revela nombres de proyectos internos que coinciden con canales actuales de Slack internos, agudizando el pretexting del atacante.
- Una afirmación de "filtración example" en un foro no tiene muestra; el indicador permanece en "incierto" hasta que emerja una muestra o pasen 90 días.

## Notas relacionadas

- [[osint-triage]]
- [[email-and-phone-osint]]
- [[company-osint]]
- [[google-dorking]]
- [[secrets-management|Secrets Management]]
- [[passive-recon|Passive Recon]]

### Notas atómicas futuras sugeridas

- secret-scanning
- credential-reuse-risk
- paste-site-monitoring
- vendor-breach-triage
- leak-data-handling
- rotation-playbooks

## Referencias

- **Docs Oficiales:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
