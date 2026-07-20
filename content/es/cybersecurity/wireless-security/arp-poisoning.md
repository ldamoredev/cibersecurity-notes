# ARP Poisoning

## Definición

El ARP poisoning es la manipulación de la cache ARP de un host para redirigir tráfico de capa 2 a través de una máquina controlada por el atacante.

## Por qué importa

El ARP poisoning es la base de muchos ataques MITM en redes locales. Es efectivo contra herramientas defensivas comunes porque opera por debajo de donde el cifrado de capa de aplicación se aplica normalmente.

La lección defensiva se generaliza: confiar en la dirección MAC de un vecino o en el mapping ARP es confiar en un protocolo sin autenticación incorporada.

## Cómo funciona

El ARP poisoning tiene **5 pasos**:

1. **Observar la red local.** El atacante identifica el gateway y los hosts objetivo.
2. **Enviar respuestas ARP falsas.** Se envían replies no solicitados que afirman que la MAC del atacante corresponde a una IP de destino.
3. **Las caches de los hosts se contaminan.** El gateway cree que el cliente es el atacante; el cliente cree que el gateway es el atacante.
4. **El tráfico fluye a través del atacante.** Con forwarding habilitado, ambas partes siguen comunicándose mientras el atacante intercepta.
5. **La inspección o modificación ocurre.** El tráfico no cifrado puede leerse; el tráfico cifrado puede inspeccionarse por metadatos o errores de certificado.

El bug no es el cifrado de datos. Es la ausencia de autenticación de identidad a nivel de capa de red local.

Un ejemplo trabajado, ARP en un lab de concienciación:

```
Entorno:
  switch lab, gateway propio, laptop cliente propia

Observado:
  el tráfico del cliente fluye a través del atacante incluso con HTTPS habilitado

Lección:
  el cifrado de capa de aplicación sobrevive; los metadatos no cifrados (DNS, SNI) todavía se filtran

Control defensivo:
  DHCP snooping, ARP inspection dinámica en el switch, e isolation de cliente inalámbrico en el AP
```

## Técnicas / patrones

El testing evalúa:

- si los switches soportan ARP inspection dinámica y si está habilitada
- si los hosts usan entradas ARP estáticas para gateways críticos
- si el DNS puede manipularse una vez que el tráfico fluye a través del atacante
- si el tráfico de texto plano es visible después de la contaminación
- si los clientes inalámbricos tienen isolation habilitada

## Variantes y bypasses

El ARP poisoning tiene **3 variantes prácticas**.

### 1. Suplantación de gateway

El atacante impersona el gateway para capturar tráfico de salida.

### 2. MITM bidireccional

Ambos lados están contaminados para intercepción silenciosa con forwarding.

### 3. DoS

La contaminación rompe el routing sin forwarding, causando pérdida de disponibilidad.

## Impacto

Ordenado aproximadamente por severidad:

- **Intercepción MITM.** El tráfico no cifrado puede leerse o modificarse.
- **Degradación de sesión.** Los proxies HTTPS visibles pueden causar advertencias de certificado.
- **Fugas de metadatos.** DNS, SNI y headers HTTP se filtran incluso con cifrado.
- **DoS de capa de red.** La contaminación sin forwarding causa pérdida de conectividad.
- **Pivoting.** El acceso de capa 2 puede usarse para alcanzar hosts que no son routeables directamente.

## Detección y defensa

Ordenado por efectividad:

1.
**Habilitar ARP inspection dinámica en switches gestionados.**
   Valida bindings IP-a-MAC usando la tabla DHCP snooping, bloqueando replies ARP falsificados.

2.
**Usar DHCP snooping como base.**
   ARP inspection depende de los datos de binding de DHCP snooping; ambos controles trabajan juntos.

3.
**Habilitar client isolation en APs inalámbricos.**
   Previene que los clientes inalámbricos envíen tráfico de capa 2 entre sí directamente.

4.
**Entregar TLS fuerte en la capa de aplicación.**
   HTTPS, HSTS y certificate pinning limitan lo que el atacante puede leer o modificar incluso si el tráfico es redirigido.

5.
**Monitorear respuestas ARP duplicadas para la misma IP.**
   Las inundaciones de ARP o los cambios frecuentes de binding son señales de envenenamiento activo.

### Qué no funciona como defensa primaria

- **Solo VLAN.** El ARP poisoning opera dentro de una VLAN/subred; no cruza segmentos de red.
- **Filtrado de firewall.** Los firewalls operan en capa 3 y no ven el envenenamiento de capa 2.
- **Solo cifrado.** El cifrado protege el payload pero no el routing subyacente.
- **Ignorar advertencias de certificado.** Las advertencias son frecuentemente la señal visible de intercepción TLS activa.

## Labs prácticos

Usar una red completamente aislada con dispositivos propios.

### Observar las caches ARP antes y después

```
# En el cliente de prueba (Linux/Mac):
arp -n

# Registrar la MAC del gateway
# Después de una prueba de contaminación controlada, volver a verificar
arp -n
```

Confirmar el cambio en la entrada de la cache ARP del gateway.

### Verificar el soporte de ARP inspection dinámica

```
Switch:
DHCP snooping habilitado:
ARP inspection dinámica habilitada:
Puertos confiables configurados:
Cobertura de VLAN:
```

La mayoría de los switches gestionados soportan ambas funciones; verificar que estén activas.

### Revisar el isolation de clientes inalámbricos

```
Modelo de AP:
Client isolation habilitada:
Alcance: solo tráfico inalámbrico / también cableado:
Red guest vs corporativa:
```

El isolation puede habilitarse independientemente por SSID.

### Construir una checklist de defensa de ARP

```
ARP inspection dinámica en switches:
DHCP snooping habilitado:
Client isolation en APs:
TLS fuerte + HSTS en servicios:
Monitoreo de anomalías ARP:
Segmentación de red local:
```

El objetivo es múltiples capas, no un solo control.

### Verificar la visibilidad de metadatos post-contaminación

```
DNS queries visibles:
SNI visible:
HTTP en texto plano visible:
Contenido cifrado expuesto:
```

Incluso en redes bien cifradas, los metadatos de capa de red se filtran.

## Ejemplos prácticos

- Un atacante en una red de cafetería contamina caches ARP y ve queries DNS de otros clientes.
- Una red de oficina sin ARP inspection es vulnerable a envenenamiento de capa 2 interno.
- Client isolation en un AP inalámbrico previene que los dispositivos guest se contaminen entre sí.
- DHCP snooping + ARP inspection bloquean un intento de envenenamiento en un lab controlado.
- Una advertencia de certificado aparece en un navegador cuando un HTTPS proxy activo intercepta tráfico.

## Notas relacionadas

- [[wireless-security]]
- [[mitm-on-local-networks]]
- [[bettercap-workflows]]
- [[network-fundamentals|Network Fundamentals]]
- [[evil-twin-access-points]]

### Notas atómicas futuras sugeridas

- dhcp-snooping
- dynamic-arp-inspection
- network-segmentation-controls
- tls-interception

## Referencias

- **Docs Oficiales:** bettercap ARP module — https://www.bettercap.org/modules/ethernet/arp/
- **Mitigación:** Cisco DAI configuration guide — https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst6500/ios/12-2SX/configuration/guide/book/dynarp.html
- **Fundamental:** RFC 826 (ARP) — https://datatracker.ietf.org/doc/html/rfc826
