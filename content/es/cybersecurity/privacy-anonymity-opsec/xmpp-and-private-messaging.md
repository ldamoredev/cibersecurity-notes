# XMPP and Private Messaging

## Definición

XMPP es un estándar de mensajería abierto que puede soportar flujos de trabajo de mensajería privada. La mensajería privada en XMPP depende de la seguridad del transporte, la confianza en el servidor, el comportamiento del cliente y los complementos de cifrado de extremo a extremo como OMEMO.

## Por qué importa

La privacidad de la mensajería no es un solo control. El transporte puede estar cifrado, el servidor puede aún ver metadatos, el cliente puede filtrar estado y la capa de cifrado de extremo a extremo puede o no usarse correctamente. XMPP es útil porque hace visible la arquitectura en lugar de ocultarla dentro de una sola nube de app.

## Cómo funciona

Usá el modelo de mensajería de 4 capas:

1.
**Capa de transporte**
   El cliente se conecta a un servidor XMPP a través de un transporte protegido.

2.
**Capa de servidor**
   El servidor maneja la identidad de cuenta, el ruteo, la presencia y los metadatos de entrega de mensajes.

3.
**Capa de cliente**
   El cliente almacena claves, sesiones, contactos e historial local.

4.
**Capa de cifrado de extremo a extremo**
   OMEMO o protocolos similares protegen el contenido del mensaje del servidor e intermediarios.

Ejemplo:

```
cliente -> servidor XMPP -> servidor del destinatario -> cliente del destinatario
       \-> cifrado de contenido OMEMO por encima
```

El bug no es usar XMPP. El bug es tratar el cifrado de transporte como si fuera lo mismo que la privacidad de contenido y la minimización de metadatos.

## Técnicas / patrones

- Separar la identidad de cuenta de la privacidad del contenido del mensaje.
- Preferir clientes que soporten funcionalidades modernas de E2EE.
- Entender si el servidor ve contactos, presencia y timing.
- Mantener el estado de dispositivo y sesión separado cuando se usan múltiples clientes.
- Tratar los chats de grupo como más ricos en metadatos que la mensajería uno-a-uno.
- Verificar si los adjuntos y la sincronización multi-dispositivo se ajustan al threat model.

## Variantes y bypasses

Usá los 6 patrones de mensajería:

### 1. Mensajería privada solo de transporte

El contenido está protegido en tránsito, pero el servidor puede aún ver texto plano o metadatos.

### 2. Mensajería protegida con OMEMO

El contenido del mensaje está cifrado de extremo a extremo, pero los metadatos, el manejo de lista de dispositivos y el ruteo del servidor aún importan.

### 3. Mensajería multi-dispositivo

Más dispositivos mejoran la usabilidad pero aumentan la gestión de claves y la superficie de compromiso.

### 4. Mensajería de grupo

Los chats de grupo aumentan la fuga de metadatos y membresía.

### 5. Transferencia de archivos a través de mensajería

Los adjuntos pueden llevar metadatos y pueden almacenarse separadamente del cuerpo del mensaje.

### 6. Descubrimiento de contactos / exposición de presencia

Algunos servicios exponen quién está en línea, quién está contactando a quién y cuándo.

## Impacto

- Mejor mensajería privada que los sistemas de chat propietarios ad hoc cuando está bien configurado.
- Los estándares abiertos hacen el modelo de confianza más fácil de inspeccionar.
- Los metadatos siguen siendo visibles para servidores y proveedores en muchos casos.
- El compromiso del dispositivo o la mala gestión de claves puede derrotar la privacidad del contenido.
- Los flujos de trabajo de grupo y adjuntos expanden la superficie de exposición.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar cifrado de extremo a extremo donde esté soportado**
   OMEMO reduce la visibilidad del servidor en el contenido de los mensajes.

2.
**Limitar la exposición de metadatos**
   Mantener la presencia, los contactos y la membresía del grupo tan privados como lo permita el ecosistema.

3.
**Elegir clientes con comportamiento de seguridad razonable**
   El cliente es parte del threat model.

4.
**Separar dispositivos y sesiones cuando sea necesario**
   La conveniencia multi-dispositivo no debería fusionar identidades silenciosamente.

5.
**Tratar a los servidores como titulares de metadatos**
   Incluso cuando el contenido está cifrado, el servidor puede aún saber quién habla con quién y cuándo.

### Qué no funciona como defensa primaria

- **TLS solo no es cifrado de extremo a extremo.**
- **Un estándar abierto no garantiza uso seguro.**
- **El chat de grupo no es el mismo problema de privacidad que el chat uno-a-uno.**
- **Un cliente seguro no puede arreglar un dispositivo comprometido.**

## Labs prácticos

### Clasificar una ruta de mensajería

```
Servicio:
¿El servidor ve el contenido?:
¿El servidor ve los metadatos?:
¿Usa OMEMO o similar?:
Multi-dispositivo:
Chat de grupo:
Adjuntos:
Ajuste al threat model:
```

La clasificación dice qué está protegiendo realmente el servicio.

### Comparar transporte y E2EE

```
Cifrado de transporte:
Contenido del mensaje cifrado de extremo a extremo:
¿El servidor ve emisor/destinatario?:
¿El servidor ve presencia?:
¿El servidor ve adjuntos?:
¿El destinatario debe confiar en el servidor?:
```

Esto mantiene TLS y E2EE separados.

### Revisar la superficie de dispositivos

```
Cantidad de dispositivos:
Apps cliente:
Almacenamiento de claves:
Historial de mensajes:
Backups:
Exposición de notificaciones:
```

Más dispositivos generalmente significa más cosas que asegurar.

### Planificar un chat privado

```
Objetivo:
Destinatario:
Necesita anonimato:
Necesita secreto del contenido:
Necesita secreto de metadatos:
Necesita adjuntos:
Clientes permitidos:
Política de backup:
```

El plan debería guiar la elección de cliente y protocolo.

## Ejemplos prácticos

- Una app de chat segura usa OMEMO para el contenido pero aún revela metadatos de cuenta al servidor.
- Un chat de grupo filtra la membresía y el timing incluso cuando los cuerpos de mensajes están cifrados.
- Un cliente en dos dispositivos aumenta la conveniencia mientras multiplica la superficie de compromiso.
- Un archivo enviado en el chat preserva los metadatos del adjunto a menos que se limpien por separado.
- Un usuario elige XMPP porque el protocolo y las opciones de cliente son inspeccionables.

## Notas relacionadas

- [[end-to-end-encryption|End-to-End Encryption]]
- [[pgp-encryption-and-signatures|PGP Encryption and Signatures]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tls-https|TLS / HTTPS]]

## Referencias

- **Docs Oficiales:** XMPP Standards Foundation - https://xmpp.org/
- **Docs Oficiales:** OMEMO Encryption XEP-0384 - https://xmpp.org/extensions/xep-0384.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
