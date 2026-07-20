# Account Correlation

## Definición

La correlación de cuentas es el proceso de vincular actividades o personas separadas a través de cuentas compartidas, datos de recuperación, identificadores, dispositivos o patrones de uso repetidos.

## Por qué importa

Muchos flujos de trabajo de privacidad fallan porque los mismos datos de cuenta aparecen en múltiples lugares. El mismo email, número de teléfono, canal de restablecimiento de contraseña, método de pago, dispositivo de login o grafo social puede tender un puente hacia una identidad que de otro modo sería separada.

## Cómo funciona

Usá los 6 anclajes de correlación:

1.
**Dirección de email**
   A menudo el identificador de cuenta más fuerte.

2.
**Número de teléfono**
   Durable y comúnmente reutilizado.

3.
**Ruta de recuperación**
   Los canales de restablecimiento pueden reconectar identidades más tarde.

4.
**Identidad de pago**
   Los datos de facturación suelen vincular cuentas.

5.
**Dispositivo y browser**
   El dispositivo de login, cookies y fingerprints correlacionan el uso.

6.
**Comportamiento y contactos**
   Los patrones de uso y el grafo social pueden tender puentes entre personas.

El bug no es tener cuentas. El bug es reutilizar suficientes de ellas hasta que las cuentas se conviertan en la misma identidad.

## Técnicas / patrones

- Separar email, recuperación y pago donde la unlinkability importa.
- Evitar hacer login en cuentas identificadoras en flujos de trabajo anónimos.
- Mantener perfiles de browser y dispositivos separados.
- Re-evaluar los vínculos de login de terceros como "Iniciar sesión con X".
- Tratar los contactos y libretas de direcciones como datos de identidad.
- Considerar el soporte y la recuperación como parte del modelo de identidad.

## Variantes y bypasses

Usá los 6 patrones de correlación:

### 1. Reutilización directa de identidad

El mismo email o nombre de usuario aparece entre personas.

### 2. Vinculación por recuperación

Diferentes cuentas están vinculadas a través del mismo email de recuperación o número de teléfono.

### 3. Vinculación por login social

El login OAuth o federado crea un puente hacia un proveedor de identidad primaria.

### 4. Vinculación por pago

Las tarjetas, facturas y suscripciones de tiendas de apps revelan titularidad.

### 5. Vinculación por dispositivo

El mismo dispositivo o perfil de browser se usa para ambas personas.

### 6. Vinculación por comportamiento

El timing, contactos y estilo de publicación conectan cuentas sin un identificador directo.

## Impacto

- Las personas separadas dejan de ser separadas.
- El seudónimato se debilita aunque la privacidad de transporte sea fuerte.
- Los pedidos de recuperación y soporte pueden revelar el puente.
- La cuenta se convierte en un anclaje de identidad durable.
- Los servicios pueden vincular perfiles internamente aunque el usuario crea que están aislados.

## Detección y defensa

Ordenado por efectividad:

1.
**Mapear los puentes antes de crear la cuenta**
   El email, recuperación, pago y dispositivo deben tratarse como rutas de identidad.

2.
**Separar los canales de recuperación**
   Un email de recuperación o número de teléfono puede destruir una separación cuidadosamente construida.

3.
**Evitar el login social para personas separadas**
   Un proveedor de identidad federada puede unificar cuentas rápidamente.

4.
**Usar diferentes dispositivos o perfiles para diferentes identidades**
   El estado compartido es un puente.

5.
**Asumir que el servicio puede correlacionar internamente**
   Aunque el usuario se mantenga separado, el proveedor puede igual inferir el vínculo.

### Qué no funciona como defensa primaria

- **Cambiar el nombre de visualización no cambia la identidad de la cuenta.**
- **Un nuevo nombre de usuario no es una nueva persona si los datos de recuperación son compartidos.**
- **Cerrar sesión no es separación si el perfil de browser sigue siendo el mismo.**
- **Eliminar una cuenta no borra toda la correlación interna.**

## Labs prácticos

### Construir un mapa de puentes de cuenta

```
Persona A:
Persona B:
Email compartido:
Teléfono compartido:
Recuperación compartida:
Pago compartido:
Dispositivo compartido:
Browser compartido:
Contactos compartidos:
```

Si alguna fila está compartida, las personas no están totalmente separadas.

### Revisar rutas de login

```
Cuenta:
Login por contraseña:
Login social:
Email de recuperación:
Teléfono de recuperación:
Dispositivo 2FA:
Compartido con otra persona:
```

La ruta de login suele ser el puente.

### Comparar vinculación de proveedor

```
Servicio A:
Servicio B:
¿Mismo proveedor?
¿Analytics compartido?
¿Pago compartido?
¿Dispositivo compartido?
¿Posible correlación interna? sí/no
```

Esto modela el riesgo de vinculación del lado del proveedor.

### Decidir si una cuenta es segura de reutilizar

```
¿Reutilización permitida?
¿Sensible a la identidad?
¿Recuperación reutilizada?
¿Pago reutilizado?
¿Dispositivo reutilizado?
¿Browser reutilizado?
```

La respuesta debería ser no generalmente para personas separadas.

## Ejemplos prácticos

- Una cuenta seudónima se vincula porque se adjunta el mismo número de teléfono de recuperación.
- Un login social tiende un puente de vuelta a un flujo de trabajo privado hacia una identidad personal de Google o Apple.
- Dos personas comparten un perfil de browser y se correlacionan por cookies e historial de login.
- La misma tarjeta de crédito y email aparecen en servicios separados.
- Un pedido de soporte revela suficiente contexto para vincular dos personas.

## Notas relacionadas

- [[deanonymization-failures|Deanonymization Failures]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[temporary-email-risks|Temporary Email Risks]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[social-media-osint|Social Media OSINT]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
