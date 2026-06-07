# Email and Phone OSINT

## Definición

El Email and Phone OSINT es la recopilación y validación de emails públicos, números de teléfono, patrones de contacto y pistas de exposición de cuentas para un propósito acotado de seguridad o investigación. Es el tejido conectivo entre [[breach-and-leak-intelligence|breach intelligence]], [[social-media-osint|Social Media OSINT]] y [[company-osint|company OSINT]] — la mayoría de las cadenas de account-takeover e ingeniería social pivotan sobre un identificador de contacto.

## Por qué importa

Los emails y números de teléfono conectan personas, cuentas, dominios, exposición de brechas, flujos de soporte y riesgo de ingeniería social. Son el identificador más reutilizado en servicios, por eso el credential-stuffing y el abuso de recuperación de cuentas dependen de ellos.

También son **datos personales** bajo la mayoría de los regímenes de protección de datos, incluso cuando los datos son técnicamente públicos. La recopilación debería ser mínima, acotada, basada en evidencia y vinculada a un propósito claro. El default es "cuál es el dataset de contacto más pequeño que responde la pregunta", no "qué datos de contacto puedo encontrar".

El caso defensivo para Email/Phone OSINT es más fuerte en tres direcciones:
- **Descubrimiento de contacto de seguridad** — encontrar la persona correcta para recibir una divulgación de vulnerabilidad.
- **Revisión de exposición de brechas de dominio** — verificar si emails de dominio propio aparecen en índices de brechas.
- **Hardening de recuperación de cuentas** — confirmar que la exposición pública de teléfono/email no es suficiente para recuperar cuentas.

## Cómo funciona

El Email/Phone OSINT procesa **5 clases de señal**. Una investigación acotada generalmente responde una o dos.

1. **Descubrimiento de contacto.** Emails públicos, números de teléfono, direcciones de soporte y formularios. Fuentes: páginas de contacto oficiales, security.txt, portales de soporte, archivos regulatorios públicos.
2. **Inferencia de patrón.** Formatos de nombres como `first.last@example.test` o `flast@example.test`. Fuentes: PDFs públicos, bios de speakers de conferencias, emails de commits públicos. **Inferencia de patrón, no cosecha de direcciones** — el objetivo es el formato, no una lista de cada dirección de empleado.
3. **Exposición de cuentas.** Indicadores de brechas o reutilización vinculados a identificadores. Manejado en [[breach-and-leak-intelligence]] con la disciplina rotation-first.
4. **Mapeo de roles.** Contactos funcionales de seguridad, soporte, ventas, ingeniería y ejecutivos. Fuentes: páginas de contacto oficiales, security.txt, alias de CRM de vendors.
5. **Verificación.** Confirmar si un contacto es actual, oficial y relevante — sin sondeos intrusivos (sin intentos de login, sin resets de contraseña, sin diálogos de verificación SMTP).

El bug es **tratar los datos de contacto como inofensivos**. Los datos de contacto son el puente más común entre OSINT y riesgo de account-takeover.

Un ejemplo trabajado, uso defensivo:

```
Pregunta:    ¿Example Corp publica un contacto de divulgación de seguridad claro?
Fuentes:     example.com/.well-known/security.txt, example.com/security, header security@example.com.
Hallazgos:   security.txt presente en /.well-known/security.txt; lista security@example.com + clave PGP.
Acción:      ninguna sobre el objetivo. La salida es un sí/no con el canal descubierto.
Almacenado:  URL de security.txt + canal recuperado. Sin datos personales de empleados recopilados.
```

La investigación respondió la pregunta sin tocar los datos de contacto personales de nadie.

## Técnicas / patrones

La disciplina es "la fuente de menor contacto que responde la pregunta".

- **Páginas de contacto oficiales y `security.txt`** para descubrimiento de contacto organizacional.
- **Documentos públicos y PDFs** para inferencia de patrón (metadatos de autor, firmas de pie de página).
- **Commits de Git, registros de paquetes, repositorios** para patrones de contacto técnicos (emails de commit, campos de maintainer).
- **Servicios de notificación de brechas** para dominios propios/autorizados únicamente, vía APIs de dominio, no listas masivas de email.
- **Perfiles sociales/profesionales** cuando la pregunta requiere corroboración de rol (con las [[social-media-osint|reglas de minimización]]).
- **Formatos de número de teléfono en páginas oficiales** para detección de suplantación.
- **Flujos de contacto de soporte y vendor** para mapeo de roles y revisión de suplantación.

## Variantes y bypasses

El Email/Phone OSINT se agrupa en **5 usos prácticos**. Cada uno implica un estándar diferente de evidencia y minimización.

### 1. Descubrimiento de contacto de seguridad

Encontrá contactos de reporte o incidentes oficiales. Sensibilidad más baja; el contacto existe explícitamente para ser encontrado. Evidencia: `security.txt`, página de seguridad dedicada o alias canónico `security@`. Acción: entregar al flujo de trabajo de divulgación.

### 2. Mapeo de patrón de email de dominio

Inferir formato probable (`first.last@`, `flast@`, `first@`) sin validar cuentas privadas de forma intrusiva. Evidencia: 3+ ejemplos públicos de fuentes independientes. **Sin sondeo SMTP, sin sondeos de reset de contraseña, sin solicitudes de validación** — el formato es el entregable, no una lista de direcciones válidas.

### 3. Revisión de exposición de brechas

Verificar si emails propios o autorizados aparecen en índices de brechas. Usar disciplina de [[breach-and-leak-intelligence]]: domain-API, no cosecha masiva de emails; rotate-first, investigate-second; nunca almacenar contraseñas crudas.

### 4. Mapeo de flujo de soporte

Entender números de soporte públicos, rutas de escalación y la superficie de suplantación. Útil para detectar números de soporte falsos en resultados de búsqueda que redirigen víctimas hacia estafadores.

### 5. Revisión de límite de datos personales

Decidir qué **no** recopilar o retener. El entregable es la decisión de minimización en sí misma, registrada en el registro de acciones. A veces la salida correcta de Email/Phone OSINT es "elegimos no recopilar esto".

## Impacto

Ordenado aproximadamente por severidad:

- **Riesgo de credential-stuffing.** Emails más señales de brechas habilitan account-takeover automatizado a escala.
- **Riesgo de ingeniería social.** Los roles y rutas de contacto agudzan el phishing y pretexting dirigidos.
- **Riesgo de recuperación de cuentas.** La exposición de teléfono/email puede ser suficiente para completar flujos de recuperación en servicios con verificación débil.
- **Mejora en reporte de seguridad.** Los contactos de seguridad descubribles reducen el tiempo de divulgación para reporteros de buena fe.
- **Detección de suplantación.** Los datos de contacto de teléfono o soporte falsos pueden encontrarse y reportarse a plataformas.

## Detección y defensa

Las defensas priorizan **minimización, canales oficiales y hardening de recuperación de cuentas**.

1.
**Minimizá la recopilación de contactos personales.**
   Recopilá solo lo que necesita la investigación. Evitá listas masivas de email personal; la decisión de minimización es el entregable, no una restricción sobre él.

2.
**Publicá contactos de seguridad y soporte claros.**
   Los canales oficiales (`security.txt`, página de seguridad dedicada, listado de teléfono de soporte) reducen la ambigüedad para reporteros de buena fe y reducen la superficie de suplantación.

3.
**Monitoreá la exposición de brechas para dominios propios.**
   Usá [[breach-and-leak-intelligence|servicios reputables]] con la disciplina rotation-first. Evitá manejar dumps de credenciales crudas.

4.
**Protegé los flujos de recuperación de cuentas.**
   Los datos públicos de teléfono/email no deberían ser suficientes para recuperar cuentas. El 2FA solo por SMS, la recuperación basada en conocimiento y la recuperación solo por email todos asumen que el identificador es privado; en términos de OSINT, ninguno lo es.

5.
**Capacitá al personal en la exposición de datos de contacto.**
   Los detalles de contacto públicos son útiles para ventas y soporte, pero no deberían revelar estructura interna innecesaria (org charts, rutas de escalación, directos privados para ejecutivos).

### Qué no funciona como defensa primaria

- **Asumir que los emails de negocio no son datos personales.** Siguen identificando personas naturales bajo la mayoría de regímenes.
- **Verificar emails con intentos de login/reset intrusivos.** Eso cruza hacia testing activo y ya no es OSINT.
- **Recopilar dumps crudos de brechas.** Usá indicadores seguros y flujos de trabajo de respuesta, no credenciales almacenadas.
- **Confiar en la obscuridad para los contactos de seguridad.** Los reporteros de buena fe necesitan una ruta clara y anunciada; la obscuridad solo ayuda a los atacantes.
- **Tratar las respuestas SMTP "no such user" como confidenciales.** Muchos servidores filtran existencia; confiar en esto es un control frágil.

## Labs prácticos

Usá tu propio dominio, una organización autorizada o tus propias cuentas personales. Nunca consultes identificadores de terceros sin autorización.

### Encontrá contactos oficiales de seguridad y soporte

```
# Ubicación canónica security.txt (RFC 9116)
curl -s https://example.test/.well-known/security.txt

# Alternativas comunes
curl -s https://example.test/security.txt
curl -s https://example.test/security
```

```
site:example.test "security contact"
site:example.test "responsible disclosure"
```

Registrá solo el canal canónico. Este es trabajo defensivo de baja sensibilidad y alto valor.

### Construí una tabla mínima de evidencia de contactos

```
contacto               | fuente                  | rol      | sensibilidad | acción            | retención
security@example.test  | /.well-known/security.txt | seg     | baja         | usar para divulgación | indefinida (pública)
support@example.test   | /support page            | soporte  | baja         | ninguna           | indefinida (pública)
hire-eng@example.test  | publicación LinkedIn     | contratación | baja    | ninguna           | fin de investigación
```

Evitá columnas como "teléfono personal" a menos que la pregunta los justifique explícitamente.

### Inferí formato de email sin sondeo intrusivo

```
Fuente 1: metadatos de autor PDF       → "John Smith <john.smith@example.com>"
Fuente 2: email de commit público      → "j.smith@example.com" (¡formato diferente!)
Fuente 3: bio de speaker de conferencia → "smith@example.com" (¡tercer formato!)
Decisión: el formato es incierto; reportar múltiples patrones en lugar de uno.
```

Nunca sondes SMTP para "validar" el formato — eso es testing activo, no OSINT.

### Verificá exposición de brechas autorizada (a nivel dominio)

```
# La búsqueda de dominio HIBP requiere propiedad verificada; devuelve counts, no texto plano.
curl -s -H "hibp-api-key: $HIBP_API_KEY" -H "user-agent: example-sec-eng" \
  "https://haveibeenpwned.com/api/v3/breaches?domain=example.com"
```

Registrá nombre de brecha, fecha, clases de datos expuestos y acción de remediación — no credenciales crudas.

### Auditá la exposición de recuperación de cuentas

```
servicio  | identificador        | método de recuperación     | ¿OSINT-descubrible? | mitigación
SaaS A    | john@example.com     | solo email                 | sí                  | aplicar recuperación TOTP
SaaS B    | +1-555-0142          | SMS                        | sí                  | aplicar TOTP, deshabilitar SMS
SaaS C    | john@example.com     | email + KBA                | parcialmente        | fortalecer preguntas KBA
```

La auditoría muestra dónde la exposición de identificadores públicos se convierte directamente en riesgo de account-takeover.

## Ejemplos prácticos

- Los PDFs públicos revelan formatos de email de empleados vía metadatos de autor.
- El descubrimiento de contacto de seguridad encuentra `security@example.test` más una clave PGP publicada, habilitando la divulgación.
- Los resultados de brechas indican emails de empleados viejos en filtraciones de terceros, desencadenando aplicación de MFA acotada a esas cuentas.
- Un número de teléfono de soporte falso aparece en resultados de búsqueda, redirigiendo usuarios a un estafador; el OSINT defensivo lo atrapa.
- Los commits públicos de Git exponen emails personales vinculados a repositorios de la empresa, sugiriendo limpieza de los defaults de `git config user.email`.
- Una auditoría de recuperación de cuentas SaaS revela recuperación solo por SMS en un servicio con datos sensibles, desencadenando un cambio de método 2FA.

## Notas relacionadas

- [[breach-and-leak-intelligence]]
- [[social-media-osint]]
- [[company-osint]]
- [[osint-triage]]
- [[auth-flaws|Auth Flaws]]
- [[broken-authentication|Broken Authentication]]

### Notas atómicas futuras sugeridas

- security-txt
- email-pattern-inference
- phone-number-osint
- account-recovery-osint-risk
- contact-data-minimization
- security-contact-discoverability

## Referencias

- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Docs Oficiales:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Ética / Seguridad:** EFF Surveillance Self-Defense — https://ssd.eff.org/
