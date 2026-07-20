# Metadata and Identity Leakage

## Definición

La fuga de metadatos e identidad ocurre cuando información alrededor de una acción, archivo, cuenta, request o dispositivo revela quién la realizó o la vincula a otra actividad, incluso cuando el contenido principal está oculto.

## Por qué importa

La mayoría de las fallas de privacidad no son roturas criptográficas dramáticas. Son fallas de correlación: una dirección IP aquí, un login allá, un patrón de timestamp, una propiedad de archivo, un browser fingerprint, un nombre de usuario reutilizado, una configuración de idioma y un rastro de pago.

El túnel VPN, el messenger cifrado o el browser privado pueden estar funcionando correctamente mientras la identidad igual se filtra a través de señales circundantes. Esta nota enseña el modelo operacional para detectar esas señales antes de que se conviertan en cadenas de evidencia.

## Cómo funciona

La fuga de metadatos sigue una cadena de 6 capas:

1.
**Metadatos de red**
   Dirección IP, ruta del resolver, dominio de destino, timing, volumen, protocolo y observador de ruteo.

2.
**Metadatos de browser y aplicación**
   Cookies, local storage, user agent, fuentes, comportamiento canvas/WebGL, extensiones, timezone, idioma, tamaño de pantalla y soporte de funcionalidades.

3.
**Metadatos de cuenta**
   Identidad de login, email de recuperación, número de teléfono, método de pago, sesiones previas, grafo de contactos y dispositivos vinculados.

4.
**Metadatos de archivos**
   EXIF, campos de autor en documentos, nombres de software, historial de edición, thumbnails, coordenadas GPS, modelo de dispositivo, timestamps del sistema de archivos y comentarios embebidos.

5.
**Metadatos de comportamiento**
   Estilo de escritura, horario de actividad, secuencia de navegación, errores repetidos, patrones de nombres de usuario, grafo social y rutina operacional.

6.
**Metadatos del proveedor**
   Logs, registros de facturación, tickets de soporte, reportes de abuso, rastros de auditoría, pedidos legales y telemetría de infraestructura.

Cadena de fuga de ejemplo:

```
Acción:
  Subir imagen "anónima" a través de una VPN.

Todavía visible:
  Cuenta del sitio web: dirección de email reutilizada
  Browser: fingerprint estable y timezone
  Archivo: modelo de cámara EXIF y timestamp GPS
  Comportamiento: mismo estilo de descripción que cuenta con nombre real
  Proveedor: pago de cuenta VPN y timestamps de conexión

Resultado:
  La ruta de red cambió, pero la correlación de identidad siguió siendo posible.
```

El bug no es una única fuga. El bug es dejar que pequeñas señales independientes se alineen en una identidad estable.

## Técnicas / patrones

- Hacer inventario de identificadores antes de la actividad sensible, no después de la publicación.
- Separar las fugas de ruta de red de las fugas de cuenta, browser, archivo y comportamiento.
- Testear desde la aplicación y dispositivo exactos que se usarán, porque las apps pueden saltarse las suposiciones del browser o la VPN.
- Inspeccionar archivos antes de compartir, especialmente imágenes, PDFs, documentos de Office, archivos comprimidos y capturas de pantalla.
- Tratar los timestamps, timezone, idioma y rutina como señales de identidad.
- Registrar qué puede ver cada observador y qué señales pueden unirse.

## Variantes y bypasses

Usá las 7 familias de fuga:

### 1. Fuga de ruta de red

La IP de origen del usuario, ruta del resolver DNS, ruta IPv6, candidato WebRTC, ruta de split-tunnel o bypass de proxy a nivel de app expone una ruta fuera de la ruta de privacidad prevista.

### 2. Fuga de browser fingerprint

El browser presenta suficientes atributos estables para distinguir a un usuario entre sesiones. Una VPN cambia la IP de origen, pero no normaliza automáticamente fuentes, extensiones, comportamiento canvas, timezone, idioma o dimensiones de ventana.

### 3. Fuga de cuenta y sesión

Hacer login en una cuenta identificadora colapsa el anonimato. El email de recuperación, verificación por teléfono, dispositivos vinculados, conexiones OAuth, carga de contactos y metadatos de pago pueden ser tan identificadores como un nombre de usuario.

### 4. Fuga de archivos y documentos

Los documentos e imágenes pueden llevar nombres de autor, coordenadas GPS, modelo de dispositivo, historial de edición, thumbnails embebidos, versiones de software y timestamps. Eliminar el texto visible no elimina los metadatos ocultos.

### 5. Correlación de comportamiento

El estilo de escritura, horario de publicación, reutilización de frases, intereses, patrón de navegación e interacciones sociales pueden vincular personas incluso sin un identificador técnico compartido.

### 6. Fuga de infraestructura y proveedor

Los proveedores de VPN, proveedores de email, plataformas de hosting, servicios de mensajería y plataformas cloud pueden retener logs o metadatos de cuenta. Una afirmación de privacidad no es lo mismo que la incapacidad técnica de producir registros.

### 7. Fuga física y ambiental

Fotos, capturas de pantalla, audio, reflexiones, vistas de ventanas, disposiciones de teclado, SSIDs de Wi-Fi, nombres de archivos locales y notificaciones de escritorio pueden revelar ubicación, empleador, dispositivo o contexto social.

## Impacto

- Cuentas seudónimas vinculadas a identidades reales.
- Navegación sensible vinculada a través de login de cuenta, browser fingerprint o ruta DNS.
- Archivos compartidos que revelan ubicación, empleador, dispositivo, autor o software de edición.
- Flujos de trabajo con VPN o Tor derrotados por el comportamiento ordinario de browser/cuenta.
- Consecuencias legales, laborales, sociales o de seguridad personal derivadas de metadatos, no de contenido.

## Detección y defensa

Ordenado por efectividad:

1.
**Minimizar la actividad que lleva identidad**
   No hacer login en cuentas identificadoras ni reutilizar emails personales, números de teléfono, métodos de pago, listas de contactos o perfiles de browser cuando el objetivo es la unlinkability.

2.
**Compartimentar browsers, cuentas, archivos y dispositivos**
   Mantener las personas separadas por contexto. Un perfil de browser compartido, carpeta de descargas, cuenta cloud o gestor de contraseñas puede tender un puente entre identidades que de otro modo serían separadas.

3.
**Normalizar o reducir las superficies de browser fingerprint**
   Usá browsers diseñados para resistencia al fingerprinting cuando el anonimato importa. Los ajustes aleatorios pueden hacer que un browser sea más único; la consistencia con un gran conjunto de anonimato suele ser más fuerte que el hardening personalizado.

4.
**Inspeccionar y eliminar metadatos de archivos antes de compartir**
   Usá herramientas de inspección de metadatos y verificá el output después de limpiar. Tratá imágenes, PDFs, archivos de Office y archivos comprimidos como riesgosos hasta inspeccionarlos.

5.
**Rutear DNS, IPv6 y tráfico de apps intencionalmente**
   Verificar la ruta del resolver y el comportamiento de la familia de direcciones. Una VPN que rutea IPv4 pero filtra IPv6 o DNS puede exponer la visibilidad de la red local o del ISP.

6.
**Controlar el tiempo, idioma y patrones de comportamiento**
   Evitá publicar desde el mismo horario, estilo y cluster de temas entre identidades. La vinculación de comportamiento es más difícil de "parchear" después de la publicación.

7.
**Preferir proveedores con arquitectura clara de minimización de datos**
   Los límites de retención, documentación pública, auditorías, informes de transparencia y diseños técnicos que evitan recopilar registros sensibles son más fuertes que promesas vagas.

### Qué no funciona como defensa primaria

- **Borrar el contenido visible no es eliminación de metadatos.** Los campos ocultos, thumbnails, historial de edición y EXIF pueden persistir.
- **Una VPN no elimina los browser fingerprints.** El destino puede ver características estables a nivel de aplicación.
- **El modo de navegación privada no es unlinkability.** No oculta IP, login de cuenta, fingerprinting, logs de proveedor o comportamiento.
- **Cambiar nombres de usuario no es separación de identidad.** El email, teléfono, estilo, horario, contactos o archivos reutilizados pueden tender puentes entre personas.
- **Un test de fuga no es una garantía permanente.** Las actualizaciones del SO, cambios de browser, configuración de VPN y comportamiento de apps pueden cambiar el perfil de fuga.

## Labs prácticos

### Inspeccionar metadatos de imágenes

```
exiftool sample.jpg
```

Comparar modelo de dispositivo, timestamp, GPS, software y campos de thumbnail con lo que el usuario tenía intención de divulgar.

### Eliminar y re-verificar metadatos

```
cp sample.jpg sample-clean.jpg
exiftool -all= sample-clean.jpg
exiftool sample-clean.jpg
```

La segunda inspección importa. La eliminación de metadatos debe verificarse, no asumirse.

### Comparar IP visible en dos contextos

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Ejecutar antes y después de habilitar la ruta prevista. Una discrepancia entre el comportamiento IPv4 e IPv6 puede exponer una fuga.

### Inspeccionar la ruta del resolver DNS

```
dig whoami.cloudflare @1.1.1.1
dig o-o.myaddr.l.google.com TXT @ns1.google.com
```

Usar tests de resolver para razonar sobre qué ruta maneja las búsquedas DNS. Comparar resultados antes y después de cambios de VPN o DNS.

### Construir una tabla de vinculación de personas

```
Señal              Persona A              Persona B              Riesgo de vínculo
Email de recuperación  inbox personal    inbox nuevo            alto/medio/bajo
Número de teléfono     mismo              ninguno                alto/medio/bajo
Perfil de browser      perfil diario      perfil separado        alto/medio/bajo
Timezone               America/Argentina  America/Argentina      alto/medio/bajo
Estilo de escritura    posts técnicos largos  posts técnicos largos  alto/medio/bajo
Origen del archivo     cámara del laptop   cámara del laptop      alto/medio/bajo
```

La tabla fuerza que la vinculación operacional salga a la luz antes de que se convierta en evidencia accidental.

### Testear unicidad del browser conservadoramente

```
Abrí un sitio de test de fingerprinting en:
1. perfil de browser diario
2. perfil de browser limpio
3. Tor Browser u otro browser anti-fingerprinting

Registrá:
- timezone
- idioma
- tamaño de pantalla
- fuentes/plugins/extensiones
- resultado canvas/WebGL
- si el browser advierte contra redimensionar/personalizar
```

El objetivo no es perseguir un puntaje perfecto. El objetivo es entender si la personalización crea unicidad.

## Ejemplos prácticos

- Un PDF compartido bajo un seudónimo incluye el nombre de usuario real del SO del autor en las propiedades del documento.
- Un usuario de VPN filtra DNS a través del resolver del sistema operativo mientras el tráfico web va por el túnel.
- Una captura de pantalla incluye una notificación de escritorio, nombre de archivo interno, ícono de perfil de browser o timezone local.
- Un usuario de Tor Browser hace login en una cuenta con nombre real, colapsando el anonimato a nivel de aplicación.
- Una "nueva" persona reutiliza el mismo estilo de escritura, calendario de publicación e intereses de nicho que una identidad pública existente.

## Notas relacionadas

- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[vpn-threat-models|VPN Threat Models]]
- [[dns-resolution|DNS Resolution]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[image-and-location-osint|Image and Location OSINT]]

## Referencias

- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
