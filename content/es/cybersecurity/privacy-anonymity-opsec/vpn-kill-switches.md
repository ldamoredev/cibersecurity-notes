# VPN Kill Switches

## Definición

Un kill switch de VPN bloquea el tráfico cuando la VPN se desconecta o no está disponible para que el sistema no caiga silenciosamente de vuelta a la ruta de red normal.

## Por qué importa

Sin un kill switch, una breve desconexión puede exponer la IP real del usuario, el resolver DNS o el tráfico de la aplicación exactamente en el momento en que el usuario asume que la VPN sigue protegiéndolo. Esto es especialmente riesgoso durante sleep/wake, roaming, portales cautivos y cambios de red móvil.

## Cómo funciona

Usá el modelo de 4 estados:

1.
**VPN conectada**
   El tráfico debería seguir la ruta del túnel.

2.
**VPN desconectada**
   El tráfico debería bloquearse en lugar de enviarse por la interfaz normal.

3.
**Reconexión en progreso**
   El sistema puede temporalmente no tener una ruta válida. El control debería fallar de forma cerrada.

4.
**Túnel restaurado**
   El tráfico se reanuda solo cuando la ruta VPN vuelve.

Política de ejemplo:

```
si vpn_activa:
  permitir tráfico saliente solo por el túnel
si no:
  bloquear tráfico saliente
```

El bug no es usar un kill switch. El bug es asumir que el ícono de la app VPN presente significa que el tráfico está contenido.

## Técnicas / patrones

- Preferir la contención del firewall a nivel del sistema sobre los toggles solo de la app.
- Testear el kill switch durante condiciones reales de desconexión.
- Verificar el tráfico del browser, terminal y apps por separado.
- Verificar el comportamiento después de sleep/wake y handoff de red.
- Documentar qué apps con split-tunnel pueden eludir el switch.
- Asegurarse de que DNS e IPv6 no estén silenciosamente exentos.

## Variantes y bypasses

Usá los 5 patrones de kill switch:

### 1. Toggle de la app

El cliente VPN bloquea el tráfico por sí mismo. Es conveniente pero puede fallar si el cliente se bloquea o no gestiona cada ruta de app.

### 2. Bloqueo basado en firewall

El firewall previene que el tráfico no perteneciente al túnel salga. Esto es generalmente más fuerte porque está más cerca de la capa de ruteo del sistema.

### 3. Contención completa del dispositivo

Todo el dispositivo está bloqueado a menos que el túnel esté activo. Esta es a menudo la opción más segura para un flujo de trabajo sensible.

### 4. Excepción de split-tunnel

Algunas apps o subredes están exentas. Esto debería ser explícito porque las excepciones pueden convertirse en rutas de fuga.

### 5. Contención de reconexión en móviles

El dispositivo duerme, se despierta o cambia de red. El kill switch debe seguir fallando de forma cerrada a través de esas transiciones.

## Impacto

- Menor probabilidad de fallback accidental a la ruta de red normal.
- Mejor contención durante transiciones inestables de Wi-Fi o móvil.
- Menor probabilidad de fugas de DNS o IPv6 cuando cae el túnel.
- Postura de privacidad más predecible durante flujos de trabajo sensibles.
- Posible fricción de usabilidad si el túnel es inestable.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar control de fail-closed a nivel de firewall**
   Una política del sistema que bloquea el tráfico cuando el túnel está caído es más difícil de eludir que un toggle de la UI del cliente.

2.
**Testear explícitamente la ruta de desconexión**
   El caso de falla relevante no es el estado normal conectado. Tirá el túnel abajo y observá qué ocurre.

3.
**Cubrir DNS e IPv6 en la política**
   Un buen kill switch debe bloquear todas las rutas de red relevantes, no solo el tráfico IPv4 más obvio del browser.

4.
**Auditar las excepciones de split-tunnel**
   Si ciertas apps tienen acceso directo, esas excepciones deben documentarse y monitorearse.

5.
**Re-testear después de actualizaciones del cliente o del SO**
   Los cambios en el stack de red pueden cambiar el comportamiento de fail-open/fail-closed.

### Qué no funciona como defensa primaria

- **La insignia de conectado no es prueba.** Solo indica el estado de la app.
- **Un kill switch que solo vigila la app VPN puede fallar si la app se bloquea.**
- **El split tunneling no es equivalente a la contención.** Crea bypasses intencionales.
- **Testear solo cuando la VPN está conectada no prueba nada sobre el comportamiento ante desconexión.**

## Labs prácticos

### Simular el estado de desconexión

```
1. Conectar VPN.
2. Registrar IP visible y DNS.
3. Desconectar VPN.
4. Registrar si todavía sale algún tráfico.
5. Reconectar VPN.
6. Repetir las verificaciones.
```

Este es el test central del kill switch.

### Verificar la contención de rutas

```
netstat -rn | sed -n '1,120p'
```

Comparar las tablas de rutas mientras está conectado y desconectado para ver si una ruta por defecto persiste.

### Verificar el DNS después de la caída

```
dig whoami.cloudflare @1.1.1.1
curl -4 https://ifconfig.me
```

Ejecutar después de desconectar. Una fuga significa que la política no es realmente fail-closed.

### Escribir un registro de falla

```
Dispositivo:
VPN:
Estado conectado:
Disparador de desconexión:
Tráfico bloqueado:
Tráfico filtrado:
DNS filtrado:
IPv6 filtrado:
Retestear después de reinicio:
```

Esto convierte una vaga afirmación de "kill switch activado" en un registro testeable.

## Ejemplos prácticos

- Un laptop pierde Wi-Fi y el switch bloquea el tráfico hasta que la VPN se reconecta.
- Un dispositivo móvil se despierta del sleep y el firewall previene el tráfico de fallback.
- Una excepción de split-tunnel está documentada para una subred de impresora pero no para el tráfico del browser.
- Una app VPN se bloquea y el firewall del sistema sigue bloqueando el egreso.
- Se detecta una race condition de reconexión porque el test incluyó sleep/wake, no solo desconexión manual.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[tls-https|TLS / HTTPS]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** WireGuard - https://www.wireguard.com/
- **Docs Oficiales:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
