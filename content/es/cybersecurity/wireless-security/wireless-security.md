# Wireless Security

## Definición

Wireless security es la protección y testing de redes cuyo primer límite de confianza es la comunicación por radio en lugar de un cable, ruta o endpoint web.

## Por qué importa

Wi-Fi cambia el modelo de seguridad porque los dispositivos cercanos pueden observar management frames, descubrir redes, impersonar access points, y unirse al mismo segmento local si la autenticación es débil.

La lección central es que la seguridad inalámbrica empieza antes de que exista tráfico IP. La asociación, autenticación, cifrado, rango de señal, comportamiento del cliente y los management frames definen lo que un atacante o defensor puede observar.

## Cómo funciona

La seguridad inalámbrica tiene **5 partes móviles**:

1. **Medio de radio.** Los dispositivos transmiten por canales que adaptadores cercanos pueden observar.
2. **Descubrimiento.** Los access points publican SSIDs y capacidades a través de management frames.
3. **Asociación.** Los clientes eligen y se unen a un access point.
4. **Autenticación y claves.** WEP, WPA/WPA2-PSK, WPA/WPA2-Enterprise o WPA3 deciden quién puede unirse y cómo se protege el tráfico.
5. **Comportamiento en la red local.** Una vez unidos, los clientes todavía enfrentan riesgos de ARP, DNS, TLS, segmentación y exposición de servicios.

No existe un único payload inalámbrico. El bug suele ser una elección de protocolo débil, passphrase débil, confianza insegura del cliente, falta de segmentación o ausencia de monitoreo.

Un ejemplo trabajado, hallazgo inalámbrico a decisión de riesgo:

```
Observación:
  SSID lab-office usa WPA2-PSK, red guest habilitada

Captura:
  survey en monitor-mode muestra tráfico de clientes y un WPA handshake natural

Config del router:
  WPS deshabilitado, PMF opcional, guest isolation deshabilitado

Verificación en red local:
  el cliente guest puede hacer ping a otro guest y llegar a la página admin de la impresora

Decisión:
  el riesgo principal no es "existe WPA2"; es segmentación débil y alcance a admin local
```

La seguridad inalámbrica debería conectar hechos de la capa de radio con el blast radius en las capas de red y aplicación.

## Técnicas / patrones

El testing inalámbrico evalúa:

- SSID, BSSID, canal, banda, cifrado y cantidad de clientes
- si un adaptador soporta monitor mode e inyección de paquetes
- captura de handshakes y fortaleza de passphrase en labs propios
- resiliencia ante deautenticación y access points rogues
- aislamiento de clientes, segmentación de guest y exposición de servicios locales
- si TLS y los controles de aplicación siguen funcionando en redes locales hostiles

## Variantes y bypasses

La seguridad inalámbrica tiene **6 dominios prácticos**.

### 1. Observación pasiva

Los management frames, beacons, probes y datos de señal pueden observarse sin unirse a una red.

### 2. Cifrado legacy débil

WEP está estructuralmente roto y debería tratarse como sin protección significativa.

### 3. Fortaleza de WPA/WPA2-PSK

WPA/WPA2-PSK falla comúnmente por passphrases débiles, no por romper AES directamente.

### 4. Interrupción de management frames

Los ataques de deautenticación y desasociación abusan del comportamiento de gestión no autenticado o débilmente protegido.

### 5. Access points rogues

Los clientes pueden conectarse a redes similares o de señal más fuerte si las decisiones de confianza son laxas.

### 6. Ataques en la misma LAN

Después de unirse, ARP spoofing, manipulación de DNS, descubrimiento de servicios y apps locales inseguras se convierten en la siguiente capa.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso a la red.** Las credenciales débiles o protocolos legacy permiten al atacante unirse a la LAN.
- **Exposición de credenciales.** Los trucos de evil twin y captive portal pueden capturar secretos en entornos inseguros.
- **Intercepción de tráfico.** Los atacantes en la misma LAN pueden observar o manipular tráfico no protegido.
- **Interrupción de disponibilidad.** La deautenticación puede forzar desconexiones de clientes.
- **Reconocimiento.** Los SSIDs, clientes, vendedores y comportamiento de probes revelan la estructura del entorno.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar WPA3 o WPA2 con passphrases fuertes o autenticación Enterprise.**
   La autenticación moderna y los secretos de alta entropía eliminan el camino más común desde material capturado hacia acceso a la red.

2.
**Deshabilitar WEP, WPS PIN y modos mixtos obsoletos.**
   La compatibilidad legacy mantiene viva la seguridad rota. Eliminarla es más fuerte que monitorearla.

3.
**Segmentar redes inalámbricas.**
   Los dispositivos guest, IoT, lab y admin no deberían compartir una LAN plana. La segmentación limita el alcance de un compromiso inalámbrico.

4.
**Habilitar protected management frames donde sea soportado.**
   PMF reduce el abuso común de management frames, especialmente la interrupción estilo deautenticación.

5.
**Monitorear access points rogues y tráfico de gestión inusual.**
   Los IDS inalámbricos, alertas de controlador y surveys periódicos ayudan a detectar redes falsificadas y disrupciones activas.

### Qué no funciona como defensa primaria

- **Ocultar el SSID.** Los clientes y frames siguen revelando el comportamiento de la red.
- **Solo allowlists de MAC.** Las direcciones MAC son observables y suplantables.
- **Contraseñas cortas de apariencia compleja.** El guessing offline premia la longitud y la imprevisibilidad.
- **Confiar en que el cifrado Wi-Fi protege los secretos de aplicación.** TLS y los controles de capa de aplicación siguen siendo importantes.

## Labs prácticos

Usá solo un access point propio o router lab aislado.

### Inventariar señales inalámbricas cercanas

```
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon
```

Registrar SSID, BSSID, canal, cifrado y cantidad de clientes.

### Comparar capas Wi-Fi e IP

```
ip addr
ip route
arp -a
```

Mapear cómo la asociación inalámbrica se convierte en alcanzabilidad IP local.

### Revisar la postura de seguridad del router

```
Cifrado:
Modo WPA:
WPS:
Red guest:
Client isolation:
Exposición de interfaz admin:
```

Convertir observaciones inalámbricas en verificaciones de control.

### Construir una tarjeta de riesgo inalámbrico

```
SSID:
Autenticación:
Client isolation:
Superficie admin:
PMF:
Separación guest/IoT:
Evidencia:
Próxima acción principal:
```

La salida de una revisión inalámbrica debería ser una decisión de control, no solo un archivo de captura.

### Comparar alcanzabilidad en red confiable vs guest

```
ip route
arp -a
ping -c 2 192.168.1.1
```

Ejecutar desde clientes lab propios; comparar qué puede alcanzar cada SSID.

## Ejemplos prácticos

- Un router doméstico usa WPA2-PSK con una contraseña corta reutilizada.
- Una red guest carece de client isolation, exponiendo impresoras y paneles admin.
- Un dispositivo legacy fuerza un modo de compatibilidad mixto WPA/WPA2.
- Un access point falso usa un SSID familiar en un espacio público.
- Una ráfaga de deautenticación hace que los dispositivos se reconecten a través de un AP rogue más fuerte.

## Notas relacionadas

- [[wifi-monitor-mode]]
- [[wpa-wpa2-handshakes]]
- [[wifi-deauthentication]]
- [[evil-twin-access-points]]
- [[packet-analysis|Packet Analysis]]

### Notas atómicas futuras sugeridas

- wpa3-sae
- enterprise-wifi-8021x
- wps-security
- wireless-intrusion-detection
- radio-frequency-basics

## Referencias

- **Fundamental:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
- **Docs Oficiales:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Docs Oficiales:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
