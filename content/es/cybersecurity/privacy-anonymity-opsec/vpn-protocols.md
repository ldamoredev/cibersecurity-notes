# VPN Protocols

## Definición

Los protocolos VPN definen cómo se negocia, cifra, autentica, rutea y mantiene un túnel VPN. Determinan la forma del túnel, no si el usuario es anónimo.

## Por qué importa

Elegir un protocolo VPN es una decisión de ingeniería de seguridad, pero a menudo se trata como una decisión de branding. WireGuard, OpenVPN, IKEv2/IPsec, L2TP/IPsec y PPTP no tienen las mismas suposiciones de diseño, superficie de auditoría, comportamiento de roaming, complejidad de despliegue o riesgo legacy.

La pregunta práctica no es "¿cuál protocolo es mejor?". Es "¿cuál protocolo se adapta a este dispositivo, red, modelo de confianza y restricción operacional sin crear falsa confianza?"

## Cómo funciona

Usá el modelo de túnel de 5 partes:

1.
**Autenticación de pares**
   El cliente y el servidor demuestran quiénes son a través de claves, certificados, credenciales o material pre-compartido.

2.
**Acuerdo de claves**
   El protocolo establece claves de cifrado para la sesión. Los protocolos modernos deberían soportar forward secrecy y evitar primitivas obsoletas.

3.
**Encapsulación**
   El tráfico original se envuelve dentro de paquetes de túnel para poder cruzar la red exterior.

4.
**Política de ruteo**
   El sistema operativo decide qué tráfico va por el túnel: todo el tráfico, subredes seleccionadas, apps seleccionadas o rutas divididas.

5.
**Mantenimiento de sesión**
   El túnel maneja reconexiones, roaming, keepalives, pérdida de paquetes, cambios de red y comportamiento ante fallas.

Comparación conceptual:

```
WireGuard:
  moderno, compacto, rápido, basado en claves, con opiniones

OpenVPN:
  maduro, flexible, ampliamente desplegado, más complejo

IKEv2/IPsec:
  común en móviles, buen comportamiento de roaming, integrado en muchos SOs

L2TP/IPsec:
  wrapper legacy alrededor de IPsec, históricamente común, usualmente no es la primera opción

PPTP:
  obsoleto, roto para seguridad seria, solo histórico
```

El bug no es usar un protocolo más antiguo en un lab. El bug es tratar la compatibilidad legacy como una postura seria de privacidad o seguridad.

## Técnicas / patrones

- Identificar el protocolo desplegado antes de juzgar un producto VPN.
- Verificar si el cliente usa ruteo de túnel completo o split tunnel.
- Buscar soporte de protocolo obsoleto, especialmente PPTP.
- Confirmar si DNS e IPv6 siguen la misma política de ruteo que el tráfico de aplicaciones.
- Tratar el roaming en móviles, sleep/wake y portales cautivos como casos de falla reales.
- Separar la elección de protocolo criptográfico de la confianza en el proveedor. Un túnel fuerte hacia un proveedor no confiable sigue siendo un flujo de trabajo no confiable.

## Variantes y bypasses

Usá las 5 familias de protocolo:

### 1. WireGuard

WireGuard es un protocolo VPN moderno con un diseño pequeño y con opiniones e identidades de clave pública estáticas. Es rápido y comparativamente fácil de razonar, pero los despliegues deben manejar cuidadosamente la rotación de claves, la privacidad del endpoint y la política de ruteo.

### 2. OpenVPN

OpenVPN es maduro y flexible, con amplio soporte de plataformas y muchos modos de despliegue. Su flexibilidad es útil en entornos enterprise y con alta compatibilidad, pero también crea más superficie de configuración.

### 3. IKEv2/IPsec

IKEv2/IPsec es común en despliegues móviles y nativos del sistema operativo. Maneja bien los cambios de red, pero los despliegues de IPsec pueden ser complejos y dependen en gran medida de una configuración correcta de cifrado, certificados e identidad.

### 4. L2TP/IPsec

L2TP/IPsec es mayormente legacy. Puede encontrarse en entornos más antiguos y clientes integrados, pero los despliegues modernos usualmente prefieren WireGuard, OpenVPN o IKEv2/IPsec.

### 5. PPTP

PPTP está deprecado y no debería usarse para seguridad seria. Si PPTP aparece en un entorno moderno, tratalo como un hallazgo de migración, no como una opción normal.

## Impacto

- Diseño de túnel criptográfico más fuerte cuando se usan protocolos modernos correctamente.
- Riesgo operacional reducido cuando el protocolo se adapta al entorno de dispositivo y red.
- Mayor exposición por protocolos legacy, cifrados débiles o comportamiento de reconexión frágil.
- Falsa garantía cuando la solidez del protocolo se confunde con la confianza en el proveedor o el anonimato.
- Fugas difíciles de depurar cuando la política de ruteo, DNS, IPv6 o split tunneling están mal configurados.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar protocolos modernos por defecto**
   Preferir WireGuard, OpenVPN o IKEv2/IPsec según las necesidades del entorno. Tienen ecosistemas activos y suposiciones de diseño más seguras que los protocolos VPN legacy.

2.
**Deshabilitar PPTP y retirar el fallback legacy**
   El fallback legacy puede convertir silenciosamente una postura fuerte en una débil. Eliminar protocolos sin soporte es más fuerte que simplemente documentar que no deberían usarse.

3.
**Verificar la política de ruteo independientemente de la elección de protocolo**
   Un protocolo seguro puede igual filtrar tráfico si el SO rutea DNS, IPv6 o apps seleccionadas fuera del túnel.

4.
**Fortalecer el material de autenticación**
   Proteger claves privadas, certificados, perfiles y claves pre-compartidas. La seguridad del túnel falla si las credenciales del cliente se copian, reutilizan o se dejan en dispositivos no gestionados.

5.
**Testear el comportamiento de reconexión y roaming**
   Los cambios de red móvil, transiciones sleep/wake, portales cautivos y handoff de Wi-Fi pueden exponer race conditions que los chequeos normales de "conectado" no detectan.

6.
**Documentar la elección de protocolo y la ruta de migración**
   Un despliegue de VPN debería indicar por qué se eligió el protocolo, qué clientes lo requieren y cuándo terminará la compatibilidad legacy.

### Qué no funciona como defensa primaria

- **El nombre del protocolo solo no es una garantía.** Un despliegue de WireGuard, OpenVPN o IPsec puede igual estar mal ruteado, con exceso de logs o con mala autenticación.
- **La compatibilidad con PPTP no vale el riesgo de seguridad serio.** Conservalo solo para labs históricos aislados o descubrimiento de migración.
- **El cifrado no resuelve la confianza en el proveedor.** El proveedor de VPN termina el túnel y puede igual observar metadatos.
- **El split tunneling no es conveniencia inocua.** Es una política de ruteo que puede crear fugas accidentales.

## Labs prácticos

### Hacer inventario de perfiles VPN locales

```
scutil --nc list 2>/dev/null || true
nmcli connection show 2>/dev/null | rg -i 'vpn|wireguard|openvpn|ipsec|l2tp|pptp' || true
```

Usar el output para identificar la familia de protocolo y si existen perfiles legacy.

### Verificar el estado de WireGuard

```
wg show 2>/dev/null || echo "Herramientas WireGuard o interfaz no disponibles"
```

Para sistemas propios, confirmar claves públicas de par, endpoint, último handshake y IPs permitidas.

### Buscar protocolos legacy en la configuración

```
rg -i 'pptp|l2tp|ms-chap|mppe|ikev1|ikev2|openvpn|wireguard' .
```

Ejecutar esto en un repositorio de infraestructura o perfiles de dispositivo para encontrar configuración VPN legacy.

### Comparar la forma de ruta de túnel completo y split-tunnel

```
netstat -rn | sed -n '1,80p'
```

Capturar tablas de ruteo antes y después de la conexión VPN. Buscar rutas por defecto, rutas de interfaz VPN y rutas solo de subred privada.

### Registrar evidencia de decisión de protocolo

```
Caso de uso de VPN:
Protocolo elegido:
Plataformas de cliente:
Modelo de autenticación:
Túnel completo o split tunnel:
Manejo de DNS:
Manejo de IPv6:
Comportamiento de reconexión testeado:
Protocolo legacy deshabilitado:
```

El registro llenado convierte "usamos una VPN" en una elección de ingeniería auditable.

## Ejemplos prácticos

- Una VPN de consumidor usa WireGuard por defecto para velocidad, pero el DNS sigue filtrando por el resolver del SO.
- Una empresa mantiene IKEv2/IPsec para clientes móviles porque la confiabilidad de roaming importa más que la moda del protocolo.
- Un appliance legacy solo soporta L2TP/IPsec, creando un requisito de migración.
- Un perfil PPTP olvidado permanece en un laptop después de que la VPN oficial se mudó a un protocolo moderno.
- Un despliegue OpenVPN es criptográficamente correcto pero usa split tunneling que deja el tráfico del browser fuera del túnel.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[tcp-ip-basics|TCP/IP Basics]]

## Referencias

- **Docs Oficiales:** WireGuard - https://www.wireguard.com/
- **Docs Oficiales:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
- **Docs Oficiales:** strongSwan documentation - https://docs.strongswan.org/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
