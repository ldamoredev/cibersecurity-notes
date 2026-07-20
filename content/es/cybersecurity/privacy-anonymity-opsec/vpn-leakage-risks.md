# VPN Leakage Risks

## Definición

Los riesgos de fuga de VPN son señales de identidad, ruteo, resolver, browser, aplicación, archivo y comportamiento que escapan o eluden el modelo de privacidad esperado de la VPN.

## Por qué importa

El túnel VPN puede estar funcionando correctamente mientras el usuario sigue filtrando identidad a través del browser, sistema operativo, cuentas, archivos o comportamiento.

Una fuga no siempre es un túnel roto. A veces es un túnel correcto rodeado de identificadores no controlados: un login con nombre real, browser fingerprint, desajuste del resolver DNS, ruta IPv6, candidato WebRTC, app con split-tunnel, metadatos de documentos subidos o patrón de publicación repetido.

## Cómo funciona

Usá el modelo de fuga de 7 capas:

1.
**Fugas de ruta**
   El tráfico toma la ruta de red normal en lugar de la ruta de la VPN.

2.
**Fugas del resolver**
   Las búsquedas DNS salen a través de un resolver inesperado, a menudo el ISP, red local o ruta DNS específica del browser.

3.
**Fugas de familia de direcciones**
   IPv4 va por la VPN mientras IPv6 usa la ruta de red normal.

4.
**Fugas del browser**
   Cookies, fingerprints, WebRTC, timezone, idioma y extensiones identifican o correlacionan al usuario.

5.
**Fugas de aplicación**
   Apps de escritorio o móviles eluden las expectativas del proxy/VPN, usan su propio DNS o se reconectan durante transiciones sleep/wake.

6.
**Fugas de archivos**
   Los archivos subidos llevan metadatos como autor, GPS, dispositivo, software y timestamps.

7.
**Fugas de comportamiento**
   Las cuentas, estilo de escritura, horario, contactos y hábitos recurrentes conectan la sesión VPN a una identidad real.

Ejemplo de cadena de fuga:

```
Estado VPN: conectada
IP del browser: salida VPN
DNS: resolver del ISP
IPv6: dirección residencial
Cuenta: login con nombre real
Archivo: campo de autor del PDF contiene nombre de usuario del SO

Resultado:
  La VPN está conectada, pero el flujo de trabajo no es privado contra los observadores previstos.
```

El bug no es solo el túnel. El bug es asumir que el túnel define todo el límite de privacidad.

## Técnicas / patrones

- Testear IPv4, IPv6 y DNS por separado.
- Testear el browser, app y dispositivo exactos usados en el flujo de trabajo.
- Inspeccionar el browser fingerprint y el estado de cuenta antes de la actividad sensible.
- Verificar las reglas de split-tunnel y las exclusiones de apps.
- Verificar el comportamiento de reconexión y sleep/wake en móviles.
- Inspeccionar archivos antes de subir o compartir.
- Tratar cada test de fuga como una instantánea, no como una garantía permanente.

## Variantes y bypasses

Usá las 10 clases de fuga:

### 1. Fugas DNS

El browser o el SO resuelve dominios a través del ISP, red local, resolver del empleador u otro resolver inesperado mientras el tráfico usa la VPN de otra manera.

### 2. Fugas IPv6

La VPN maneja IPv4 pero deja IPv6 habilitado en la interfaz normal. Los sitios que soportan IPv6 pueden ver la ruta de red real del usuario.

### 3. Fugas WebRTC

Las APIs del browser pueden exponer direcciones de candidato locales o públicas dependiendo de la configuración del browser y el estado de la red. Los browsers modernos han mejorado, pero el testing sigue siendo útil.

### 4. Errores de split-tunnel

El split tunneling excluye intencionalmente rutas o apps. Un error en la lista de exclusiones puede enviar tráfico sensible fuera de la VPN.

### 5. Bypass a nivel de app

Algunas apps usan su propio stack de red, DNS, configuración de proxy o comportamiento de reconexión. Que el browser pase un test de fuga no prueba que todas las apps estén contenidas.

### 6. Race conditions de reconexión

Cuando el Wi-Fi cambia, el dispositivo se despierta o la VPN se reconecta, el tráfico puede salir brevemente por la red normal a menos que la contención del firewall funcione.

### 7. Browser fingerprinting

El destino puede correlacionar el browser a través de fuentes, extensiones, canvas/WebGL, tamaño de pantalla, idioma, timezone y otros atributos.

### 8. Correlación de login

El usuario hace login en una cuenta que lo identifica directamente o vincula a sesiones anteriores, haciendo irrelevante el enmascaramiento de la IP de origen.

### 9. Fuga de metadatos de archivos

Las imágenes, PDFs, documentos de Office y archivos comprimidos pueden llevar metadatos identificadores después de la subida.

### 10. Correlación de comportamiento

El estilo de escritura, timing, grafo social y patrones repetidos vinculan la sesión VPN a identidades existentes.

## Impacto

- Exposición de la dirección IP real, resolver DNS, red del empleador, ISP, ubicación o contexto del dispositivo.
- Correlación del lado del sitio web a pesar del cambio de IP de salida.
- Desanonimización accidental a través de cuentas o archivos subidos.
- Falsa confianza durante investigaciones sensibles, reporteo o flujos de trabajo de seguridad personal.
- Evidencia de incidente incompleta cuando un equipo registra "VPN habilitada" sin testear la ruta completa.

## Detección y defensa

Ordenado por efectividad:

1.
**Tratar las fugas como un problema de flujo de trabajo**
   Testear red, DNS, browser, app, cuenta, archivo y comportamiento juntos. El estado de la VPN solo no es suficiente evidencia.

2.
**Usar ruteo de túnel completo cuando la privacidad depende de la contención**
   El túnel completo es más fácil de razonar que el split tunneling. El split tunneling debería ser explícito, documentado y testeado.

3.
**Deshabilitar o rutear correctamente IPv6 cuando no sea soportado**
   Si la VPN no soporta IPv6, ya sea rutearlo por el túnel o deshabilitarlo para ese flujo de trabajo. El fallback silencioso de IPv6 es una discrepancia común.

4.
**Forzar el DNS a través de la ruta del resolver prevista**
   El comportamiento del DNS debe coincidir con el threat model. El DNS-over-HTTPS del browser, los resolvers del SO y el DNS del proveedor de VPN pueden diferir.

5.
**Usar compartimentación del browser**
   Los perfiles separados, los browsers anti-fingerprinting y el comportamiento disciplinado de la cuenta son necesarios cuando la correlación de destino importa.

6.
**Usar kill switches o contención con firewall**
   Un kill switch reduce el fallback accidental durante desconexiones y reconexiones. Los controles a nivel del sistema son más fuertes que los indicadores de estado solo de la app.

7.
**Inspeccionar archivos y eliminar metadatos antes de compartir**
   La eliminación de metadatos debe verificarse después de la limpieza, no asumirse de un flujo de exportación o captura de pantalla.

### Qué no funciona como defensa primaria

- **Un ícono verde de VPN no es prueba de privacidad.** Usualmente dice que el túnel está conectado, no que todo el tráfico y los identificadores estén contenidos.
- **Un sitio web de verificación de IP no es un test completo de fugas.** No prueba que DNS, IPv6, apps, archivos o identidad del browser sean seguros.
- **El modo de navegación privada no es prevención de fugas.** No oculta IP, DNS, browser fingerprint, tráfico de apps ni identidad de cuenta.
- **Cambiar el país de salida no detiene el rastreo.** Las cookies, cuentas y fingerprints pueden igual correlacionar sesiones.

## Labs prácticos

### Testear IPv4 e IPv6 por separado

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Ejecutar antes y después de conectar. Registrar si ambas familias de direcciones siguen la ruta esperada.

### Verificar la ruta del resolver

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Comparar la visibilidad del resolver antes y después de la conexión VPN.

### Comparar las rutas del browser y del terminal

```
1. Verificar la IP visible en el browser.
2. Ejecutar curl IP checks en el terminal.
3. Ejecutar verificaciones del resolver DNS.
4. Repetir en un segundo perfil de browser.
5. Registrar discrepancias.
```

El comportamiento del browser y el terminal puede divergir debido al DNS-over-HTTPS, configuración del proxy, extensiones o permisos de apps.

### Inspeccionar suposiciones de split-tunnel

```
App o ruta       Ruta esperada      Ruta observada      Notas
Browser          VPN                desconocida         testear
App de mensajería VPN               desconocida         testear
Actualizador     normal/VPN         desconocida         testear
Subred privada   directa/VPN        desconocida         testear
DNS              resolver VPN       desconocida         testear
```

La tabla hace el split tunneling explícito en lugar de accidental.

### Inspeccionar metadatos de archivos antes de subir

```
exiftool document.pdf
exiftool image.jpg
```

Si aparecen campos de autor, GPS, software, timestamp o dispositivo, limpiar y re-verificar antes de compartir.

### Construir una tarjeta de incidente de fuga

```
Ruta de privacidad esperada:
Fuga observada:
Observador que podría verla:
Señal de identidad expuesta:
Causa raíz:
Retestear:
Cambio de control:
```

Esto mantiene el manejo de fugas concreto y retesteable.

## Ejemplos prácticos

- Una VPN rutea el tráfico del browser, pero las consultas DNS aún van al resolver del ISP.
- IPv4 muestra la salida de la VPN mientras IPv6 expone la red doméstica.
- Una app de trabajo se reconecta antes de la VPN después de que el laptop se despierta.
- Un usuario sube una foto a través de la VPN pero deja los metadatos GPS intactos.
- Un usuario cambia la IP de salida pero hace login en la misma cuenta personal con el mismo perfil de browser.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[dns-resolution|DNS Resolution]]
- [[cookies-and-sessions|Cookies and Sessions]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/
