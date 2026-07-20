# End-to-End Encryption

## Definición

El cifrado de extremo a extremo protege el contenido de modo que solo los endpoints que se comunican puedan descifrarlo. No oculta automáticamente los metadatos, la identidad de la cuenta, el estado del dispositivo ni el comportamiento.

## Por qué importa

E2EE es uno de los controles de privacidad más importantes disponibles, pero también uno de los más malentendidos. Los usuarios frecuentemente escuchan "cifrado" y asumen "privado" o "anónimo", aunque el servidor puede aún ver quién habló con quién, cuándo y desde qué dispositivo o cuenta.

## Cómo funciona

Usá el modelo E2EE de 4 capas:

1.
**Acuerdo de claves**
   Los endpoints establecen un secreto compartido o material de clave.

2.
**Cifrado del mensaje**
   El contenido se cifra antes de salir del emisor y se descifra solo en el destinatario.

3.
**Actualización de sesión**
   El ratcheting o la actualización de sesión limita el efecto del compromiso de claves con el tiempo.

4.
**Límites de confianza**
   Los servidores, relays y proveedores de transporte no deberían poder leer el cuerpo del mensaje, pero pueden aún ver metadatos.

Ejemplo conceptual:

```
App emisor -> cifrar localmente -> servidor retransmite ciphertext -> app receptor descifra localmente
```

El bug no es la ausencia de cifrado. El bug es esperar que el cifrado borre los metadatos y las señales de identidad.

## Técnicas / patrones

- Cifrar antes de subir o enviar.
- Mantener las claves en los endpoints, no en servidores compartidos.
- Usar protocolos con forward secrecy y buena gestión de sesiones.
- Minimizar los metadatos en los flujos de trabajo de contacto y grupo.
- Separar el cifrado de contenido del cifrado de transporte.
- Inspeccionar qué puede aún ver el servidor.

## Variantes y bypasses

Usá los 6 casos E2EE:

### 1. E2EE de mensajería

Protege el contenido del chat, pero los metadatos de cuenta y timing pueden permanecer.

### 2. E2EE de archivos

Protege el contenido del archivo, pero los nombres de archivo, metadatos y contexto de entrega aún importan.

### 3. E2EE de backups

Protege los backups si la clave se controla correctamente, pero el diseño de recuperación se vuelve crucial.

### 4. E2EE de grupo

Protege el contenido para el grupo, pero la membresía y el fanout de mensajes aún pueden filtrar metadatos.

### 5. E2EE multi-dispositivo

Conveniente, pero más dispositivos significan más claves y superficie de compromiso.

### 6. Cifrado solo de transporte

TLS protege en tránsito pero no es E2EE. Es un control diferente.

## Impacto

- Visibilidad del servidor o relay reducida en el contenido de los mensajes.
- Mejor protección contra observadores de red pasivos.
- Mejor protección si un proveedor es comprometido pero los endpoints permanecen seguros.
- Exposición continua de metadatos, identidad y comportamiento.
- Riesgo de falsa confianza si los usuarios confunden TLS con E2EE.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar un protocolo diseñado para E2EE**
   Los protocolos estilo Signal y la mensajería moderna estilo OMEMO son mejores puntos de partida que el cifrado ad hoc.

2.
**Mantener las claves en endpoints de confianza**
   El contenido solo es privado si las claves privadas no están expuestas casualmente en otro lugar.

3.
**Separar el pensamiento de metadatos y contenido**
   Preguntar qué permanece visible incluso cuando el cuerpo está cifrado.

4.
**Usar gestión de sesiones segura**
   El forward secrecy y el ratcheting reducen el radio de explosión con el tiempo.

5.
**Minimizar la dispersión de dispositivos y backups**
   Cada copia o dispositivo adicional expande la superficie de ataque.

### Qué no funciona como defensa primaria

- **TLS no es E2EE.**
- **E2EE no oculta los metadatos de emisor/destinatario.**
- **E2EE no arregla los endpoints comprometidos.**
- **Una política del proveedor que dice "no podemos leer los mensajes" no prueba la privacidad de metadatos.**

## Labs prácticos

### Separar contenido de metadatos

```
Cuerpo del mensaje:
Adjunto:
Identidad del emisor:
Identidad del destinatario:
Timestamp:
Cantidad de dispositivos:
Logs del servidor:
```

Esto separa el objetivo real del cifrado de los metadatos circundantes.

### Clasificar un protocolo

```
Protocolo:
¿Cifra el cuerpo antes del servidor?:
¿El servidor ve destinatarios?:
¿El servidor ve timing?:
Forward secrecy:
Multi-dispositivo:
Soporte de grupos:
```

Esto dice si el sistema es realmente E2EE o solo cifrado de transporte.

### Revisar el almacenamiento de claves

```
Claves almacenadas dónde:
Respaldadas dónde:
Compartidas entre dispositivos:
Ruta de recuperación de pérdida:
Radio de explosión de compromiso:
```

Si las claves están en todas partes, la privacidad no lo está.

### Comparar E2EE con TLS

```
Propiedad                TLS                E2EE
Privacidad de contenido:
El servidor lee el cuerpo:
El observador de red ve el cuerpo:
Privacidad de metadatos:
Resistencia al compromiso del endpoint:
```

La diferencia entre los dos es toda la nota.

## Ejemplos prácticos

- La mensajería estilo Signal protege el contenido mientras el servidor aún ve metadatos a nivel de cuenta.
- Una transferencia de archivo usa cifrado pero el nombre del archivo aún revela contexto.
- Un backup está cifrado pero la clave de recuperación se almacena en un lugar inseguro.
- Un usuario asume que HTTPS significa que solo el destinatario puede leer el mensaje.
- Un chat E2EE de grupo aún filtra la membresía y el timing de mensajes.

## Notas relacionadas

- [[xmpp-and-private-messaging|XMPP and Private Messaging]]
- [[pgp-encryption-and-signatures|PGP Encryption and Signatures]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tls-https|TLS / HTTPS]]

## Referencias

- **Investigación / Deep Dive:** Signal Technical Information - https://signal.org/docs
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
