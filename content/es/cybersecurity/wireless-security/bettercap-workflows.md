# Bettercap Workflows

## Definición

Bettercap es un framework de pruebas de red que combina reconocimiento inalámbrico y de capa 2, ARP spoofing, captura de tráfico y análisis de protocolo en una sola plataforma.

## Por qué importa

Bettercap sirve como un ejemplo concreto de cómo las capacidades de red de lab se combinan en flujos de trabajo: descubrimiento, posicionamiento y observación. Los tests son contenidos, nombrados y limitados a alcance.

La herramienta también aparece en assessments defensivos para verificar qué es observable desde dentro de un segmento de red local y para ayudar a encontrar brechas de visibilidad antes de que lo hagan los atacantes.

## Cómo funciona

Un flujo de trabajo bettercap tiene **5 pasos**:

1. **Iniciar la herramienta con el alcance correcto.** Seleccionar la interfaz y modo.
2. **Reconocer el segmento.** Descubrir hosts, redes inalámbricas o gestión de capa 2.
3. **Definir el scope de la prueba.** Especificar targets, limitar el impacto y documentar la autorización.
4. **Ejecutar la acción de la prueba.** Captura pasiva, ARP spoofing controlado u otra acción del módulo.
5. **Analizar y reportar.** Convertir las observaciones en hallazgos, no en interrupción.

El patrón principal es que cada prueba tenga un nombre, targets nombrados y un punto de parada definido.

Un ejemplo trabajado, spoofing ARP acotado:

```
Interfaz: eth0 (lab switch)
Target: 192.168.100.50 (cliente de prueba propio)
Gateway: 192.168.100.1 (router lab propio)
Módulo: arp.spoof
Duración: 60 segundos
Registrado: sí
Rollback: arp -d en cliente; bettercap detenido

Observado durante:
  queries DNS en texto plano visibles
  HTTP en texto plano visible
  tráfico HTTPS presente pero cifrado

Conclusión:
  el DNS no está cifrado, HTTP legacy usado para recurso X, TLS aplicado en otro lugar
```

## Técnicas / patrones

Las pruebas basadas en bettercap evalúan:

- qué hosts y servicios son visibles en un segmento dado
- si el ARP poisoning de capa 2 es posible en ausencia de ARP inspection dinámica
- qué protocolos son visibles en el plano inalámbrico
- si existen SSIDs no autorizados en el entorno
- si el comportamiento de los clientes puede observarse pasivamente

## Variantes y bypasses

Los flujos de trabajo bettercap tienen **4 modos comunes**.

### 1. Reconocimiento pasivo

Descubrimiento de hosts y observación de tráfico sin posicionamiento activo.

### 2. Reconocimiento inalámbrico

Escaneo de SSIDs, BSSIDs, clientes y canales en monitor mode.

### 3. ARP spoofing controlado

Posicionamiento bidireccional en un lab cerrado con targets nombrados y duración limitada.

### 4. Concienciación sobre rogue AP

Detección y documentación de SSIDs anómalos y BSSIDs no autorizados.

## Impacto

Lo que la ejecución de bettercap sin controles puede revelar:

- tráfico en texto plano completo incluyendo credenciales
- queries DNS revelando patrones de actividad de host
- errores de TLS o certificados débiles
- datos de sesión no cifrados
- presencia de protocolos legacy

## Detección y defensa

Ordenado por efectividad:

1.
**Habilitar ARP inspection dinámica y DHCP snooping.**
   Bloquea la mecánica de posicionamiento de capa 2 de arp.spoof en redes correctamente configuradas.

2.
**Cifrar DNS (DoH o DoT).**
   Reduce los metadatos visibles incluso cuando el posicionamiento tiene éxito.

3.
**Deshabilitar HTTP en texto plano en todos los servicios internos.**
   Elimina el protocolo más fácil de interceptar del camino.

4.
**Detectar reconocimiento activo con WIDS y monitoreo de switches.**
   El ARP spoofing y el escaneo inalámbrico son visibles para el monitoreo de red.

### Qué no funciona como defensa primaria

- **Solo contraseña Wi-Fi.** Bettercap trabaja desde dentro de la red, no desde afuera de ella.
- **Endpoints cifrados sin control de red.** El cifrado de capa de aplicación protege el contenido pero no la visibilidad de metadatos.
- **Confiar en el aislamiento de red.** Si el acceso a segmentos es demasiado amplio, bettercap puede hacer mucho desde un único punto de acceso.
- **Ignorar el tráfico de capa 2.** Los problemas de ARP y DHCP son señales de posicionamiento activo.

## Labs prácticos

Ejecutar bettercap solo en redes lab propias con hosts de prueba propios.

### Iniciar bettercap con logging

```bash
sudo bettercap -iface eth0 -caplet http-ui
```

Verificar que la interfaz es correcta y que el alcance es solo el segmento del lab.

### Reconocimiento pasivo acotado

```
net.probe on
net.show
```

Observar hosts descubiertos. Documentar el alcance antes de seguir adelante.

### Módulo arp.spoof con scope estricto

```
set arp.spoof.targets 192.168.100.50
arp.spoof on
net.sniff on
```

Parar después de 60 segundos. Registrar solo lo que los hosts propios producen.

### Reconocimiento inalámbrico

```bash
sudo bettercap -iface wlan0mon
wifi.recon on
wifi.show
```

Documentar SSIDs, BSSIDs y canales visibles. Buscar anomalías y BSSIDs no autorizados.

### Bloque de scope antes de cada módulo

```
Módulo:
Interfaz:
Target(s):
Propietario de los targets:
Duración:
Punto de parada:
Logging:
Propósito:
```

Este bloque se completa antes de habilitar cualquier módulo activo.

### Observación de protocolo post-posicionamiento

```
Protocolo | observable | contenido expuesto | acción defensiva
HTTP | sí | credenciales, cookies | migrar a HTTPS
DNS | sí | queries, dominios | usar DoH/DoT
HTTPS | sí (metadatos) | SNI, tamaños | aceptable con TLS fuerte
SSH | no | — | sin acción
```

Convertir las observaciones en recomendaciones de configuración, no en capturas de tráfico.

## Ejemplos prácticos

- Un reconocimiento pasivo encuentra un host legacy transmitiendo en HTTP en texto plano.
- Un ARP spoof controlado confirma que ARP inspection dinámica no está habilitada en el switch del lab.
- El módulo wifi.recon detecta un SSID no autorizado con el mismo nombre que la red corporativa.
- Las queries DNS son visibles durante el spoofing aunque el contenido de la aplicación esté cifrado.
- Un caplet de bettercap limita el scope del test a un único host de prueba.

## Notas relacionadas

- [[mitm-on-local-networks]]
- [[arp-poisoning]]
- [[evil-twin-access-points]]
- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wireshark-workflows|Wireshark Workflows]]

### Notas atómicas futuras sugeridas

- network-sniffing-tools
- caplet-scripting
- passive-reconnaissance
- dhcp-snooping

## Referencias

- **Docs Oficiales:** bettercap documentation — https://www.bettercap.org/
- **Docs Oficiales:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Docs Oficiales:** bettercap ARP module — https://www.bettercap.org/modules/ethernet/arp/
