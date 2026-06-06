# Privacy vs Anonymity vs Confidentiality

## Definición

Privacy es el control sobre la exposición y el uso de información sobre una persona o grupo. Anonymity es la imposibilidad de vincular una acción a una identidad específica. Confidentiality es la protección contra la lectura no autorizada de datos.

Los tres se superponen, pero no son intercambiables.

## Por qué importa

La mayoría de los errores con herramientas de privacidad comienzan con un colapso de vocabulario. Un usuario instala un messenger cifrado y asume que es anónimo. Una empresa agrega TLS y asume que resolvió la privacidad. Una VPN oculta tráfico de la red local y el usuario asume que los sitios web no pueden reconocerlo.

La regla práctica es simple: privacy es sobre gobernanza de la información, anonymity es sobre unlinkability, y confidentiality es sobre secreto del contenido. Un control puede mejorar uno sin hacer casi nada por los otros.

## Cómo funciona

Pensá en términos de las 3 propiedades:

1.
**Privacy pregunta qué información existe y cómo se recopila, usa, retiene, comparte e infiere.**
   Un servicio puede mantener confidenciales los contenidos de los mensajes pero igual recopilar identificadores de cuenta, contactos, direcciones IP, metadatos de dispositivo, registros de facturación y patrones de comportamiento.

2.
**Anonymity pregunta si un observador puede vincular una acción a una persona, cuenta, dispositivo o persona estable.**
   Una acción puede ser confidencial en tránsito pero igual ser vinculable a través del estado de login, dirección IP, cookies, timing, estilo de escritura, metadatos de pago o comportamiento repetido.

3.
**Confidentiality pregunta si partes no autorizadas pueden leer el contenido protegido.**
   TLS, cifrado de disco, cifrado de archivos y end-to-end encryption protegen principalmente contenido, no necesariamente identidad, metadatos o comportamiento.

Ejemplo concreto:

```
Escenario: Un usuario hace login en una cuenta personal sobre HTTPS estando conectado a una VPN.

Confidentiality:
- La red local no puede leer el contenido de las páginas HTTPS.

Privacy:
- El ISP ve menos metadatos de navegación, pero el proveedor de VPN ve metadatos de conexión.
- El sitio web sigue recibiendo la identidad de la cuenta y telemetría de la aplicación.

Anonymity:
- La acción no es anónima porque el usuario hizo login en una cuenta identificable.
```

El bug no es "la VPN falló". El bug es esperar que una herramienta de ruteo resuelva problemas de cuenta, browser, comportamiento y gobernanza de datos.

## Técnicas / patrones

- Identificar al observador primero: red local, ISP, proveedor de VPN, sitio web, empleador, proveedor cloud, autoridades, operador de malware, grafo social u observador físico.
- Separar el secreto del contenido de la exposición de metadatos.
- Preguntar si el usuario es anónimo para cada observador, no anónimo en abstracto.
- Mapear identificadores estables: cuenta, dirección IP, instrumento de pago, número de teléfono, browser fingerprint, cookie jar, dirección de email, estilo de escritura, timezone, idioma y metadatos de archivos.
- Tratar los controles de privacidad como reducciones parciales de exposición, no como cambios de estado mágicos.

## Variantes y bypasses

Usá el modelo de 5 señales para evitar confusiones:

### 1. Contenido

El contenido es lo que se protege: mensajes, archivos, datos de formularios, páginas, credenciales o términos de búsqueda. El cifrado suele ser más fuerte aquí, pero solo si los endpoints y las claves están controlados correctamente.

### 2. Metadatos

Los metadatos describen la comunicación o el archivo sin ser el contenido principal: origen, destino, tiempo, tamaño, dominio, remitente, destinatario, nombre de archivo, dispositivo, campos EXIF y ruta de ruteo. Los metadatos suelen sobrevivir aunque el contenido esté cifrado.

### 3. Identidad

La identidad puede ser explícita, como un login, número de teléfono, email o tarjeta de pago. También puede ser implícita, como un browser fingerprint estable o un patrón de acceso repetido.

### 4. Comportamiento

El comportamiento vincula actividad a través de hábitos: estilo de escritura, timing, secuencia de búsqueda, patrón de navegación, reutilización de nombres de usuario, grafo social o rutina operacional. Las buenas herramientas no pueden compensar el hecho de vincular repetidamente la misma persona a los mismos ritmos del mundo real.

### 5. Retención y divulgación

La privacidad también depende de quién almacena registros, cuánto tiempo los conserva, si pueden ser compelidos y si técnicamente pueden producir logs útiles. Una afirmación de "no logs" es una afirmación de privacidad, no una prueba por sí sola.

## Impacto

- Confianza mal ubicada en herramientas que resuelven solo una parte del problema.
- Desanonimización accidental a través de login de cuenta, estado del browser, registros de pago o comportamiento repetido.
- Programas de privacidad que cifran datos pero igual recopilan en exceso, retienen en exceso o comparten información personal en exceso.
- Diseños de seguridad que protegen el contenido mientras dejan los metadatos de tráfico y la correlación de identidad sin tratar.
- Falsa confianza durante investigaciones sensibles, periodismo, respuesta a incidentes o planificación de seguridad personal.

## Detección y defensa

Ordenado por efectividad:

1.
**Empezar con un threat model**
   Nombrá al observador, sus capacidades y las consecuencias de la exposición. Esto evita apilar herramientas genéricamente "más privadas" y enfoca los controles en el riesgo real.

2.
**Separar contenido, metadatos, identidad, comportamiento y retención**
   Escribilos como filas separadas al evaluar una herramienta o flujo de trabajo. Si una fila sigue expuesta, toda la actividad puede seguir siendo vinculable.

3.
**Minimizar la recopilación y retención**
   La privacidad mejora cuando existe menos datos sensibles en primer lugar. Los logs, telemetría, carga de contactos y datos de recuperación de cuentas se convierten en superficies de divulgación futuras.

4.
**Usar controles de confidentiality donde el secreto del contenido es el problema**
   TLS, cifrado de disco y end-to-end encryption son poderosos, pero deben nombrarse como controles de confidentiality. No dejes que silenciosamente representen al anonimato.

5.
**Usar compartimentación donde la vinculabilidad es el problema**
   Cuentas separadas, perfiles de browser, dispositivos, redes y contextos operacionales reducen la vinculación cruzada accidental. El límite debe mantenerse operacionalmente, no solo crearse una vez.

6.
**Preferir sistemas transparentes y controles verificables**
   Arquitectura, documentación, auditorías, builds reproducibles, protocolos públicos y políticas claras de retención de datos dan más evidencia que slogans.

### Qué no funciona como defensa primaria

- **El cifrado solo no es privacidad.** Puede ocultar contenidos mientras deja expuestos la identidad, los metadatos, la retención y el comportamiento del endpoint.
- **Una VPN no es anonimato.** Desplaza la visibilidad de la ruta de red de un observador a otro y no elimina cuentas, cookies, fingerprints o comportamiento.
- **El modo privado no es un límite OPSEC.** Principalmente cambia el comportamiento de almacenamiento local del browser y no oculta actividad de sitios web, redes, empleadores o proveedores.
- **El lenguaje de política no es una garantía técnica.** Las políticas de privacidad y las afirmaciones de "no logs" importan, pero la arquitectura y los incentivos determinan cuánta confianza merecen.

## Labs prácticos

### Dividir un flujo de trabajo en las 5 señales

```
Flujo de trabajo: Hacer login en una cuenta de email personal sobre HTTPS desde una red Wi-Fi de hotel.

Contenido:
Metadatos:
Identidad:
Comportamiento:
Retención:

Observadores:
- red del hotel
- ISP/backbone
- proveedor de email
- servicios de destino vinculados desde emails
- dispositivo/browser
```

El resultado debería mostrar qué exposiciones persisten aunque HTTPS funcione correctamente.

### Comparar confidentiality y anonimato

```
Control: HTTPS
Protege contenido de observadores pasivos locales: sí
Oculta el dominio de todos los observadores de red: no
Oculta el login de cuenta del sitio web: no
Oculta el browser fingerprint del sitio web: no
Previene logs del lado del proveedor: no
```

Esta tabla previene el error común de tratar un control fuerte como una solución universal de privacidad.

### Construir una matriz de observadores

```
Actividad: investigar un tema sensible

Observador              ¿Ve contenido?   ¿Ve metadatos?   ¿Puede vincular identidad?
Operador de Wi-Fi local  no, si HTTPS     sí, dominios/timing  quizás, dispositivo/pago/ubicación
ISP                       no, si HTTPS     sí, metadatos de destino  titular de la cuenta
Proveedor de VPN          no, si HTTPS     sí, metadatos de destino  cuenta/pago/IP
Sitio web                 sí, datos de página/app  sí, telemetría de app  login/cookies/fingerprint
Dispositivo gestionado por empleador  quizás  sí  frecuentemente sí
```

La matriz hace que la selección de herramientas sea concreta en lugar de ideológica.

### Verificar la vinculación de cuentas antes de afirmar anonimato

```
Lista de verificación:
- ¿Estoy logueado en una cuenta con nombre real?
- ¿Este perfil de browser se reutiliza?
- ¿Hay el mismo email o número de teléfono asociado?
- ¿Hay el mismo método de pago asociado?
- ¿Se reutiliza el mismo estilo de escritura o calendario de publicación?
- ¿Se están subiendo archivos desde mi dispositivo normal?
```

Si alguna respuesta es sí, la actividad puede seguir siendo vinculable aunque la privacidad de transporte sea fuerte.

## Ejemplos prácticos

- Una VPN oculta dominios de navegación de una red de café pero no del proveedor de VPN ni del sitio web de destino.
- El end-to-end encryption oculta el contenido de los mensajes del proveedor de servicio pero no necesariamente el timing de remitente/destinatario ni el grafo social.
- Una foto puede estar cifrada durante la carga mientras igual lleva metadatos EXIF que revelan modelo de dispositivo, timestamp o ubicación.
- Una cuenta seudónima puede volverse identificable a través de nombres de usuario reutilizados, estilo de escritura, email de recuperación o calendario de publicación.
- Una VPN corporativa puede proteger el acceso a recursos internos mientras intencionalmente registra identidad de usuario, postura del dispositivo, destinos e historial de sesión.

## Notas relacionadas

- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[vpn-threat-models|VPN Threat Models]]
- [[tls-https|TLS / HTTPS]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[osint|OSINT]]

## Referencias

- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
