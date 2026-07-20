# PGP Encryption and Signatures

## Definición

Los flujos de trabajo estilo PGP usan cifrado de clave pública y firmas para proteger la confidencialidad del contenido y verificar el origen o la integridad. En la práctica, el flujo de trabajo depende de la gestión de claves, las decisiones de confianza y el manejo cuidadoso de metadatos y endpoints.

## Por qué importa

PGP puede ser muy útil para el cifrado de archivos, releases firmados y relaciones de confianza de larga duración. También es fácil de usar mal: mala verificación de claves, malos hábitos de backup, claves desactualizadas, confianza excesiva y confundir cifrado con anonimato generan riesgo real.

## Cómo funciona

Usá el modelo OpenPGP de 4 pasos:

1.
**Generación de claves**
   Cada usuario crea un par de clave pública/privada.

2.
**Distribución de claves**
   Las claves públicas se comparten a través de un canal que el usuario debe confiar o verificar.

3.
**Cifrado o firma**
   El cifrado protege el contenido para una clave de destinatario. La firma prueba el control de la clave de firma.

4.
**Verificación y rotación**
   Las claves deben verificarse, renovarse, revocarse, rotarse y respaldarse correctamente.

Ejemplo:

```
emisor -> cifrar con clave pública del destinatario -> ciphertext
emisor -> firmar con clave privada -> firma
destinatario -> verificar firma y descifrar localmente
```

El bug no es PGP en sí. El bug es confundir la corrección criptográfica con la identidad, la confianza y la seguridad del flujo de trabajo.

## Técnicas / patrones

- Verificar fingerprints fuera de banda cuando importa la confianza.
- Mantener las claves de firma y cifrado protegidas separadamente donde sea posible.
- Usar revocación y expiración intencionalmente.
- Respaldar claves de forma segura y testear la recuperación.
- Cifrar archivos, no solo texto de email, cuando el caso de uso lo requiere.
- Tratar los servidores de claves y directorios como ayudas de descubrimiento, no como fuentes de confianza.

## Variantes y bypasses

Usá los 6 casos PGP:

### 1. Cifrado de archivos

Útil para proteger contenido en reposo o en transferencia.

### 2. Artefactos de release firmados

Útil para autenticidad de software o documentos.

### 3. Email firmado

Provee autenticidad pero puede aún exponer metadatos y contexto de ruteo de correo.

### 4. Web of trust

Puede funcionar, pero la gestión de confianza es operacionalmente exigente y frecuentemente malentendida.

### 5. Claves descubiertas en keyservers

Conveniente para descubrimiento, pero la presencia en el keyserver no prueba confianza.

### 6. Falla de revocación y rotación

Las claves expiradas, revocadas o reemplazadas deben manejarse cuidadosamente o las relaciones de confianza se deterioran.

## Impacto

- Fuerte confidencialidad e autenticidad del contenido cuando la gestión de claves es sólida.
- Protección para archivos y releases firmados.
- Carga operacional en torno a confianza, backups, revocación y verificación de fingerprints.
- Los metadatos y la identidad de cuenta aún permanecen fuera de la protección de contenido de PGP.
- Falsa confianza cuando los usuarios creen que PGP los hace anónimos.

## Detección y defensa

Ordenado por efectividad:

1.
**Verificar fingerprints fuera de banda**
   La comparación de fingerprints es más fuerte que confiar en una página web o listado de directorio.

2.
**Usar expiración y revocación**
   Las claves deberían ser reemplazables y las claves antiguas no deberían vivir para siempre.

3.
**Respaldar claves de forma segura**
   Perder una clave privada puede significar perder acceso a datos cifrados o identidad de firma.

4.
**Separar confianza de conveniencia**
   Que una clave sea fácil de encontrar no es lo mismo que ser de confianza.

5.
**Mantener explícita la distinción contenido/metadatos**
   PGP protege el contenido, no necesariamente quién lo envió, cuándo o a través de qué proveedor.

### Qué no funciona como defensa primaria

- **PGP no es anonimato.**
- **Un listado verificado en un keyserver no es verificación de identidad.**
- **Cifrar el correo no oculta las cabeceras ni el asunto.**
- **Firmar un archivo no prueba que el dispositivo que lo firmó no estaba comprometido.**

## Labs prácticos

### Inspeccionar un flujo de trabajo de claves

```
Fingerprint de clave:
Cómo se verificó:
Expiración:
Método de revocación:
Ubicación de backup:
Usada para firma:
Usada para cifrado:
```

Esto hace explícito el modelo de confianza.

### Clasificar un caso de uso

```
Caso de uso:
Cifrado de archivo:
Firma de email:
Release de software:
Archivo a largo plazo:
Uso anónimo:
Herramienta adecuada:
```

PGP no es la respuesta a todos los problemas de comunicación privada.

### Revisar la higiene de claves

```
Ubicación de clave privada:
Passphrase:
Token hardware:
Backup:
Certificado de revocación:
Expiración:
```

La higiene de claves es el control que más gente olvida.

### Comparar PGP con E2EE

```
Propiedad                PGP               E2EE moderno
Confidencialidad del contenido:
Verificación de identidad:
Conveniencia multi-dispositivo:
Privacidad de metadatos:
Facilidad de recuperación:
```

La comparación ayuda a colocar PGP en el nicho correcto.

## Ejemplos prácticos

- Un desarrollador firma un tarball de release para que los usuarios puedan verificar la autenticidad.
- Un periodista cifra un documento para un destinatario conocido.
- Un equipo gestiona la revocación cuando se rota una clave.
- Un usuario confía en una clave sin verificar el fingerprint y obtiene la identidad incorrecta.
- Un email está cifrado pero la línea de asunto aún revela el tema.

## Notas relacionadas

- [[end-to-end-encryption|End-to-End Encryption]]
- [[secure-file-sharing|Secure File Sharing]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

## Referencias

- **Docs Oficiales:** GnuPG Manual - https://gnupg.org/documentation/manuals/gnupg/
- **Docs Oficiales:** OpenPGP RFC 9580 - https://www.rfc-editor.org/rfc/rfc9580
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
