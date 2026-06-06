# Private Email Threat Models

## Definición

Los threat models de email privado describen qué observadores pueden ver el contenido, los metadatos, la identidad de la cuenta y el patrón de acceso de un flujo de trabajo de email, y qué controles reducen realmente cada una de esas exposiciones.

## Por qué importa

El email se usa frecuentemente para cuentas, recuperación, alertas, contacto y comunicación sensible. Incluso si el contenido del mensaje está cifrado, la cuenta, las cabeceras, el emisor, el destinatario, la línea de asunto, el timing y los logs del proveedor pueden aún revelar mucho.

## Cómo funciona

Usá las 5 capas de exposición:

1.
**Contenido**
   El cuerpo y los adjuntos del mensaje.

2.
**Cabeceras y metadatos**
   Emisor, destinatario, asunto, timestamp, ruteo e IDs de mensaje.

3.
**Identidad de cuenta**
   La dirección, el email de recuperación, el teléfono, el método de login y el dispositivo usados.

4.
**Registros del proveedor**
   Logs, manejo de abuso, retención, registros de autenticación y metadatos almacenados por el servicio de email.

5.
**Comportamiento**
   Timing, cadencia de respuesta, patrones de asunto y estilo de escritura.

El bug no es usar email. El bug es pensar que el email tiene las mismas propiedades de privacidad que un tablón de anuncios anónimo.

## Técnicas / patrones

- Separar el cifrado de contenido de la privacidad de metadatos.
- Usar diferentes identidades de email para diferentes propósitos.
- Evitar usar email personal para registros sensibles cuando importa la identidad de la cuenta.
- Asumir que el proveedor puede ver más que lo que ve el destinatario.
- Tratar los canales de recuperación como parte del modelo de identidad.
- Preferir flujos de trabajo de cuenta mínima cuando sea posible.

## Variantes y bypasses

Usá los 6 patrones de email:

### 1. Buzón personal

Conveniente pero muy identificador.

### 2. Buzón seudónimo separado

Útil para compartimentación si los datos de recuperación y los hábitos de login también están separados.

### 3. Email cifrado

Protege los contenidos, no necesariamente las cabeceras, las líneas de asunto, la identidad del emisor ni los logs del proveedor.

### 4. Dirección alias o de reenvío

Reduce la exposición del buzón principal pero puede vincular de vuelta a través de registros del proveedor.

### 5. Buzón temporal

Útil para registros únicos, pero frecuentemente débil en persistencia, recuperación y tolerancia al abuso.

### 6. Flujo de trabajo de email centrado en Tor

Puede reducir la visibilidad de la red local o del ISP, pero el proveedor de email y el comportamiento de login siguen siendo relevantes.

## Impacto

- Las direcciones de email se convierten en anclas de identidad duraderas.
- Las líneas de asunto y las cabeceras pueden revelar contexto sensible.
- Los proveedores pueden retener metadatos incluso cuando el contenido está protegido.
- Los flujos de trabajo de recuperación pueden revincular identidades seudónimas y reales.
- El timing de respuesta y el estilo pueden correlacionar actividades.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar identidades separadas para propósitos separados**
   Una identidad privada no debería compartir canales de recuperación, contactos ni rutinas de login con una pública.

2.
**Minimizar los datos de la cuenta**
   Cuantos menos datos de recuperación y perfil estén almacenados, menos hooks de identidad existen.

3.
**Cifrar los contenidos cuando el modelo de destinatario lo soporta**
   El cifrado de contenido ayuda, pero solo cuando la clave correspondiente y el flujo de trabajo operacional se manejan de forma segura.

4.
**Reducir la exposición de metadatos**
   Evitar revelar líneas de asunto innecesarias, adjuntos visibles o contexto de ruteo.

5.
**Tratar a los proveedores como titulares de datos**
   Elegir proveedores por arquitectura y retención, no por eslóganes.

### Qué no funciona como defensa primaria

- **Un nuevo buzón no es una nueva identidad si los datos de recuperación se comparten.**
- **El cifrado no oculta los metadatos de emisor y destinatario por sí solo.**
- **El email temporal no es privacidad robusta.**
- **Eliminar mensajes del buzón no borra los logs del proveedor ni las copias de los destinatarios.**

## Labs prácticos

### Construir un threat model de email

```
Cuenta:
Destinatario:
Contenido sensible:
Metadatos sensibles:
Email de recuperación:
Teléfono adjunto:
Logs del proveedor:
Pistas de comportamiento:
```

Esto hace concreta la superficie de identidad del email.

### Separar personas

```
Email persona A:
Email persona B:
Recuperación compartida:
Browser compartido:
Dispositivo compartido:
Contactos compartidos:
¿Permitido superponer?:
```

El resultado debería decirte si la separación es real.

### Revisar los metadatos del mensaje

```
Para:
De:
Asunto:
Nombres de adjuntos:
Timestamp:
Cadena de respuesta:
Logs del proveedor:
```

Los metadatos frecuentemente revelan más que el cuerpo del mensaje.

### Decidir si el email es el canal correcto

```
Necesita confidencialidad del mensaje:
Necesita anonimato del emisor:
Necesita anonimato del destinatario:
Necesita persistencia:
Necesita recuperación:
Necesita almacenamiento de terceros:
¿Usar email? sí/no
Alternativa:
```

La respuesta correcta a veces es "no email."

## Ejemplos prácticos

- Un informante usa un buzón separado pero olvida que la info de recuperación vincula de vuelta a su identidad principal.
- Un formulario de contacto usa email y líneas de asunto que revelan contexto sensible.
- Un proveedor puede aún correlacionar el timing de mensajes incluso cuando el contenido está cifrado.
- Un email de restablecimiento de contraseña se convierte en una ruta de recuperación de identidad.
- Una dirección de newsletter seudónima permanece separada hasta que se reutiliza el mismo dispositivo y browser.

## Notas relacionadas

- [[temporary-email-risks|Temporary Email Risks]]
- [[end-to-end-encryption|End-to-End Encryption]]
- [[pgp-encryption-and-signatures|PGP Encryption and Signatures]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
