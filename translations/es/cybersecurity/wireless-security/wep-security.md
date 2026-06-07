# WEP Security

## Definición

WEP security es el esquema de cifrado Wi-Fi legacy que intentó proteger el tráfico inalámbrico con RC4 e initialization vectors pero ahora se considera roto.

## Por qué importa

WEP es importante como lección histórica y como riesgo real cuando todavía existe equipo viejo. Su fracaso muestra por qué importan el diseño del modo de cifrado, la reutilización de nonces y el ciclo de vida del protocolo.

Para práctica, los labs WEP son útiles porque enseñan captura de paquetes y acumulación de IVs, pero WEP nunca debería aceptarse como control de producción.

## Cómo funciona

El fallo de WEP tiene **4 mecánicas centrales**:

1. **Clave estática compartida.** Clientes y APs usan el mismo secreto de larga duración.
2. **Espacio de IV pequeño.** Los initialization vectors se repiten bajo tráfico.
3. **Key scheduling débil.** El uso de RC4 filtra información cuando se capturan suficientes frames.
4. **Recuperación offline.** Los frames capturados pueden analizarse sin interactuar con el AP después de la colección.

El bug no es "la contraseña es débil". La construcción de WEP es débil incluso antes de considerar la calidad de la contraseña del usuario.

Un ejemplo trabajado, WEP como hallazgo de migración:

```
Observación:
  SSID warehouse-legacy publica WEP

Razón de negocio:
  el escáner de mano viejo no puede unirse a WPA2

Ubicación en la red:
  la misma VLAN puede alcanzar la base de datos de inventario

Control compensatorio:
  ninguno; sin client isolation ni restricción de firewall

Decisión:
  problema crítico de migración: reemplazar/bridge el escáner y aislar la red legacy hasta su eliminación
```

Para WEP, la salida madura es un plan de eliminación, no una configuración WEP más fuerte.

## Técnicas / patrones

El testing evalúa:

- si algún AP publica WEP o soporte mixto legacy
- recuento de IVs en capturas
- si el tráfico del cliente genera naturalmente suficientes paquetes
- si se está usando inyección de paquetes en un lab autorizado
- si dispositivos críticos para el negocio dependen de Wi-Fi legacy

## Variantes y bypasses

El riesgo WEP tiene **3 formas comunes**.

### 1. WEP estático

El deployment roto clásico: una clave WEP compartida entre clientes.

### 2. Red legacy oculta

Un SSID viejo sigue activo para impresoras, escáneres, cámaras o dispositivos industriales.

### 3. Excepción de migración

WEP permanece porque un dispositivo legacy bloquea la modernización.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso de red.** Los atacantes pueden recuperar la clave y unirse a la LAN.
- **Exposición de tráfico.** El tráfico inalámbrico capturado puede descifrarse.
- **Movimiento lateral.** Unirse a una red inalámbrica plana expone servicios internos.
- **Fallo de cumplimiento.** WEP es incompatible con las expectativas modernas de seguridad.

## Detección y defensa

Ordenado por efectividad:

1.
**Eliminar WEP completamente.**
   No existe una configuración WEP segura. El reemplazo es la corrección real.

2.
**Reemplazar o aislar dispositivos legacy.**
   Si un dispositivo no puede soportar Wi-Fi moderno, aislarlo detrás de un bridge, segmento cableado o plan de reemplazo.

3.
**Usar WPA2/WPA3 con autenticación fuerte.**
   La seguridad Wi-Fi moderna desplaza el riesgo del diseño de protocolo roto hacia la calidad de las credenciales y la configuración.

4.
**Escanear periódicamente por beacons WEP.**
   Los surveys inalámbricos detectan APs olvidados y dispositivos no gestionados.

### Qué no funciona como defensa primaria

- **Cambiar la clave WEP ocasionalmente.** El protocolo sigue estando roto.
- **Ocultar el SSID.** El tráfico WEP todavía filtra suficiente señal para descubrimiento y análisis.
- **Allowlists de MAC.** No arreglan el fallo de cifrado y pueden ser bypasseadas.
- **Solo bajo poder de transmisión.** El rango de radio no es un límite de seguridad confiable.

## Labs prácticos

Usar solo un AP lab construido intencionalmente.

### Identificar redes WEP

```
sudo airodump-ng wlan0mon
```

Buscar valores `ENC` que indiquen WEP.

### Capturar crecimiento de IVs

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write wep-lab wlan0mon
```

Rastrear el recuento de `#Data` o IVs a lo largo del tiempo.

### Documentar bloqueadores de migración

```
SSID:
Dispositivo que requiere WEP:
Propietario de negocio:
Ruta de reemplazo:
Aislamiento temporal:
Plazo:
```

Tratar WEP como un problema de planificación de remediación, no de tuning.

### Verificar segmentación alrededor del Wi-Fi legacy

```
subred SSID legacy:
gateway alcanzable:
hosts sensibles alcanzables:
regla de firewall:
propietario de excepción temporal:
```

Si WEP no puede eliminarse inmediatamente, la segmentación se convierte en el control de emergencia.

### Verificar preparación para la eliminación

```
dispositivo de reemplazo testeado:
WPA2/WPA3 soportado:
fecha de apagado del SSID viejo:
propietario del rollback:
scan post-apagado:
```

El estado final es que no haya beacon WEP.

### Confirmar que no hay WEP después de la migración

```
sudo airodump-ng wlan0mon
```

Después del apagado, el survey del lab/oficina no debería mostrar redes WEP de tu propiedad.

## Ejemplos prácticos

- Un escáner de depósito solo soporta WEP y mantiene vivo un SSID viejo.
- Un router lab se configura con WEP para practicar captura de paquetes de forma segura.
- Un survey del edificio encuentra un AP no gestionado transmitiendo una red legacy.
- Una red de impresoras usa WEP porque el deployment original nunca fue revisado.
- Una LAN plana convierte el compromiso WEP en acceso a servicios internos.

## Notas relacionadas

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wifi-wordlist-attacks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[internal-attack-surface|Internal Attack Surface]]

### Notas atómicas futuras sugeridas

- legacy-protocol-risk
- wifi-migration-planning
- wireless-intrusion-detection
- radio-frequency-basics

## Referencias

- **Docs Oficiales:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Docs Oficiales:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
