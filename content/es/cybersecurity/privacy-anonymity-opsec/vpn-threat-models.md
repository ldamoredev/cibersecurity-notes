# VPN Threat Models

## Definición

Una VPN no es anonimato. Una VPN cambia quién puede observar partes del tráfico de red desplazando la ruta de red aparente del usuario a través de un proveedor de VPN.

## Por qué importa

El marketing de VPN a menudo colapsa privacidad, anonimato, seguridad y anti-rastreo en una sola promesa de producto. En realidad, una VPN generalmente desplaza la confianza de la red local o el ISP hacia el proveedor de VPN.

Ese desplazamiento puede ser útil. Puede proteger los metadatos de tráfico de Wi-Fi hostil, reducir la visibilidad del ISP, rutear alrededor de bloqueos de red o alcanzar una red privada corporativa. Pero no borra la identidad de cuenta, los browser fingerprints, las cookies, los patrones de comportamiento, los metadatos de archivos, el compromiso del endpoint o los logs del lado del proveedor.

Las VPN protegen la exposición de la ruta de transporte. No hacen desaparecer la identidad.

## Cómo funciona

Usá el modelo de 4 observadores:

1.
**Red local**
   El café, hotel, escuela, oficina o red doméstica ve un túnel cifrado hacia el servidor VPN en lugar de conexiones directas a cada destino.

2.
**ISP o red upstream**
   El ISP ve que el usuario se conecta a un endpoint de VPN y puede observar timing y volumen, pero no debería ver cada dominio o IP de destino si el tráfico y el DNS se rutean a través del túnel.

3.
**Proveedor de VPN**
   El proveedor de VPN generalmente puede ver la IP de origen del usuario, cuenta, tiempo de conexión, IP de salida asignada, timing de tráfico, volumen de tráfico y metadatos de destino a menos que la arquitectura prevenga o minimice la recopilación.

4.
**Sitio web o servicio de destino**
   El sitio web ve la IP de salida de la VPN en lugar de la IP residencial del usuario, pero aun puede ver el login de cuenta, cookies, browser fingerprint, telemetría de la app, comportamiento del request y contenido enviado al servicio.

Tabla de visibilidad concreta:

```
Observador             Antes de la VPN                        Después de la VPN
Wi-Fi local            metadatos de destino, timing            endpoint VPN, timing, volumen
ISP                    metadatos de destino, timing            endpoint VPN, timing, volumen
Proveedor de VPN       sin vista privilegiada de ruta          IP de origen, timing, metadatos de destino
Sitio web              IP residencial + señales del browser    IP de la VPN + señales del browser/cuenta
```

El bug no es que las VPN sean inútiles. El bug es tratar un desplazamiento de confianza como anonimato.

## Técnicas / patrones

- Nombrar al observador que la VPN pretende reducir: Wi-Fi local, ISP, red escolar, red del empleador, límite geo/de red o servicio de destino.
- Verificar si DNS, IPv6 y tráfico de apps realmente siguen el túnel.
- Separar la privacidad de VPN de consumidor del control de acceso de VPN corporativa.
- Evaluar la confianza en el proveedor a través de logs, auditorías, jurisdicción, propiedad, infraestructura, metadatos de pago/cuenta e incentivos de negocio.
- Identificar qué siguen recibiendo los sitios web: cuenta, cookie, fingerprint, idioma, timezone, comportamiento y archivos subidos.
- Evitar apilar VPN y Tor a menos que se entienda el modelo de confianza cambiado.

## Variantes y bypasses

Usá los 6 casos de threat model de VPN:

### 1. Red local hostil

Una VPN puede reducir lo que ve un café, aeropuerto, hotel o LAN compartida. Esto es útil cuando la red local no es de confianza, pero el HTTPS moderno ya protege la mayoría del contenido. La VPN principalmente cambia la exposición de metadatos.

### 2. Privacidad del ISP

Una VPN puede reducir la visibilidad del ISP sobre metadatos de destino, especialmente cuando el DNS también va por el túnel. Reemplaza la confianza en el ISP con la confianza en el proveedor de VPN.

### 3. Censura o bloqueos de red

Una VPN puede rutear alrededor de algunas restricciones locales haciendo que el tráfico parezca salir de una red diferente. Puede fallar donde los endpoints de VPN están bloqueados, son legalmente riesgosos o están siendo sometidos a fingerprinting.

### 4. Acceso corporativo

Las VPN corporativas generalmente existen para alcanzar recursos privados de la empresa. Son conscientes de la identidad, gestionadas, monitoreadas y registradas por diseño. Su objetivo de seguridad es el control de acceso, no el anonimato del consumidor.

### 5. Cambio de IP de cara al destino

Los sitios web ven la IP de salida de la VPN en lugar de la IP de origen del usuario. Esto puede reducir la exposición de ubicación aproximada, pero no previene la correlación de login, fingerprinting, puntuación de fraude o vinculación basada en comportamiento.

### 6. Modo de falsa confianza

El túnel VPN funciona, pero el usuario filtra a través de cuentas, DNS, IPv6, WebRTC, split tunneling, bypass de app, browser fingerprinting, metadatos de archivos o malware en el endpoint.

## Impacto

- Reducción útil de la visibilidad de la red local y del ISP cuando se configura correctamente.
- Desplazamiento de confianza hacia un proveedor de VPN que puede registrar, vender, retener o ser compelido a divulgar registros.
- Rastreo persistente del lado del sitio web a pesar del cambio de dirección IP.
- Exposición accidental por DNS, IPv6, WebRTC, split-tunnel, reconexión durante sleep/wake de dispositivo móvil o bypass de app.
- Exceso de confianza durante investigaciones sensibles o flujos de trabajo de seguridad personal.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir el trabajo de la VPN antes de elegir una**
   Una VPN para Wi-Fi hostil, privacidad del ISP, acceso corporativo, elusión de censura y cambio de IP de cara al destino tiene diferentes criterios de éxito. Sin un objetivo, cualquier afirmación de marketing suena relevante.

2.
**Evaluar la confianza en el proveedor como un sistema**
   Las afirmaciones de no-log no son garantías técnicas por sí solas. Evaluar arquitectura, auditorías, jurisdicción, propiedad, control de infraestructura, historial de incidentes, modelo de negocio e incentivos.

3.
**Verificar el comportamiento de ruteo**
   Testear IP visible IPv4, IPv6, resolver DNS y comportamiento de apps desde el dispositivo y las apps reales. La deriva de configuración puede convertir una VPN que funciona en un túnel parcial.

4.
**Mantener los controles de browser y cuenta separados**
   Usar perfiles separados, evitar logins identificadores cuando la unlinkability importa y entender que las cookies y fingerprints sobreviven a un cambio de IP.

5.
**Usar kill switches y reglas de firewall para contención**
   Un kill switch debería prevenir el fallback accidental a la ruta de red normal cuando la VPN se desconecta. Los controles de firewall a nivel del sistema suelen ser más fuertes que los toggles solo de la app.

6.
**Preferir HTTPS y seguridad de endpoint independientemente de la VPN**
   Una VPN no reemplaza TLS, actualizaciones, autenticación fuerte, cifrado de disco o resistencia al malware. El compromiso del endpoint derrota la privacidad de la ruta de red.

### Qué no funciona como defensa primaria

- **El marketing de "no logs" no es prueba.** Es una afirmación de confianza que necesita arquitectura, auditorías, jurisdicción e historial.
- **VPN más login con nombre real no es anonimato.** El destino puede identificar la cuenta independientemente de la IP de origen.
- **La navegación privada más VPN no es un límite OPSEC.** Las señales del browser y de cuenta aún cruzan el límite.
- **Una VPN no protege contra el compromiso del endpoint.** El malware o el monitoreo de dispositivos gestionados puede ver la actividad antes del cifrado o después del descifrado.
- **Una VPN no arregla automáticamente las fugas de DNS, IPv6 o WebRTC.** Esos son comportamientos de configuración y aplicación que necesitan testing.

## Labs prácticos

### Comparar direcciones IP visibles

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Ejecutar antes y después de habilitar la VPN. Si IPv6 aún muestra la ruta sin VPN, el threat model ha cambiado menos de lo esperado.

### Comparar la visibilidad del resolver DNS

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Registrar la vista del resolver/origen antes y después de habilitar la VPN. Las fugas DNS son sobre dónde salen las búsquedas, no si la página web carga.

### Mapear observadores para una sesión VPN

```
Actividad:
Proveedor de VPN:
Cuenta usada:
Metadatos de pago/cuenta:
Observador de red local:
Observador ISP:
Servicios de destino:
Perfil de browser:
Ruta DNS:
Comportamiento IPv6:
Archivos subidos:
```

La planilla completada debería mostrar si la VPN está resolviendo el problema del observador previsto.

### Testear el riesgo de bypass a nivel de app

```
Plan de test:
1. Habilitar la VPN.
2. Verificar la IP visible del browser.
3. Verificar un segundo perfil de browser.
4. Verificar una app de escritorio con su propia red.
5. Verificar una app móvil después de sleep/wake.
6. Registrar cualquier app que exponga la ruta de red normal.
```

Algunas aplicaciones no se comportan como el browser. El objetivo es testear el flujo de trabajo real.

### Simular la contención ante desconexión

```
Comportamiento esperado del kill switch:
- VPN conectada: tráfico permitido
- VPN se desconecta: tráfico bloqueado
- VPN se reconecta: tráfico reanuda por el túnel
- apps con split-tunnel: comportamiento documentado
- mobile sleep/wake: comportamiento documentado
```

Hacé esto solo en un dispositivo y red que controlés. El resultado te dice si la desconexión crea un fallback accidental.

## Ejemplos prácticos

- Un periodista usa una VPN de confianza en el Wi-Fi del hotel para reducir la exposición de metadatos de la red local, pero evita el login de cuenta personal para investigación sensible.
- Un desarrollador usa una VPN corporativa para alcanzar sistemas internos; la empresa registra identidad, postura del dispositivo y actividad de sesión por diseño.
- Un usuario cambia el país aparente con una VPN pero sigue siendo rastreable a través de las mismas cookies del browser y cuenta.
- Una VPN rutea el tráfico del browser pero una app usa DNS directo o IPv6 fuera del túnel.
- Un usuario asume que "no logs" significa registros imposibles de divulgar, pero el proveedor aún tiene telemetría de cuenta, pago, IP de origen, abuso o infraestructura.

## Notas relacionadas

- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS / HTTPS]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
