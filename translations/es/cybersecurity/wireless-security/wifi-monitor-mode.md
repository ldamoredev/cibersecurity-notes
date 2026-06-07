# Wi-Fi Monitor Mode

## Definición

El monitor mode de Wi-Fi es un modo del adaptador que captura frames 802.11 crudos del aire en lugar de solo el tráfico dirigido al cliente local después de la asociación.

## Por qué importa

El monitor mode es la base del trabajo práctico de seguridad inalámbrica. Sin él, el tester ve la red como un cliente normal. Con él, el tester puede observar beacons, probes, clientes, canales, handshakes y comportamiento de gestión.

El límite clave: el monitor mode es observación. La inyección de paquetes y la interrupción son capacidades separadas que requieren autorización más estricta.

## Cómo funciona

El flujo de trabajo en monitor mode tiene **5 pasos**:

1. **Elegir hardware compatible.** El adaptador y el driver deben soportar monitor mode.
2. **Detener los gestores en conflicto.** Los network managers pueden mantener la tarjeta en managed mode.
3. **Habilitar monitor mode.** La interfaz pasa de asociación de cliente a captura de frames.
4. **Seleccionar canales o hacer hopping.** Las capturas son sensibles al canal.
5. **Registrar frames.** Las herramientas guardan evidencia en pcap/csv para análisis posterior.

El mecanismo no es sniffing IP. Es captura de frames 802.11 antes de que el tráfico LAN normal esté disponible.

Un ejemplo trabajado, decisión de calidad de captura:

```
Objetivo:
  capturar frames para lab-ap en canal 6

Estado del adaptador:
  wlan0mon reporta monitor mode

Captura:
  beacons visibles, probes de clientes visibles, sin EAPOL durante los primeros 2 minutos

Ajuste:
  bloquear al canal 6 y reconectar el cliente de prueba propio

Decisión:
  la primera captura prueba visibilidad del AP, no presencia de handshake; se necesita una segunda captura para análisis WPA
```

La evidencia en monitor mode debería indicar qué fue visible, qué faltó y por qué.

## Técnicas / patrones

Buscar:

- chipset del adaptador y soporte del driver
- estado de la interfaz antes y después del monitor mode
- channel hopping vs captura en canal fijo
- indicadores de beacons, probes, datos, EAPOL y PMKID
- evidencia en pcap que se pueda reabrir en Wireshark

## Variantes y bypasses

El trabajo en monitor mode tiene **4 problemas comunes**.

### 1. Managed mode confundido con monitor mode

El adaptador puede seguir estando asociado como cliente y perderse los frames crudos.

### 2. Canal equivocado

Una captura en canal fijo se pierde APs o handshakes en otros canales.

### 3. Inestabilidad del driver

Algunos adaptadores parecen soportar monitor mode pero pierden frames o fallan en pruebas de inyección.

### 4. Procesos superpuestos

NetworkManager, wpa_supplicant o herramientas del vendor pueden resetear la interfaz mientras corren las pruebas.

## Impacto

Ordenado aproximadamente por severidad:

- **Calidad de evidencia.** Las buenas capturas soportan triage inalámbrico preciso.
- **Análisis de handshake.** El testing WPA/WPA2 depende de capturar el material de frames correcto.
- **Detección de APs rogues.** La visibilidad de beacons y probes expone imitadores.
- **Confiabilidad operacional.** Un estado incorrecto del adaptador crea falsos negativos.

## Detección y defensa

Ordenado por efectividad:

1.
**Tratar el monitor mode como prerequisito de lab, no como hallazgo.**
   La capacidad de un tester de capturar frames dice que el medio de radio es observable; no prueba un compromiso.

2.
**Verificar capturas en Wireshark.**
   Reabrir pcaps detecta capturas vacías, canales equivocados y clases de frames faltantes.

3.
**Documentar canal, adaptador, driver y ubicación.**
   La evidencia inalámbrica cambia con la posición física y el hardware, así que el contexto importa.

4.
**Usar captura pasiva primero.**
   La observación pasiva reduce el riesgo y establece una línea base antes de las pruebas disruptivas.

### Qué no funciona como defensa primaria

- **Asumir que el cifrado oculta los metadatos.** Los beacons, BSSIDs, canales y muchos management frames siguen siendo observables.
- **Asumir que no hay clientes visibles significa que no hay riesgo.** El timing de captura y la selección de canal pueden perderse clientes.
- **Tratar el monitor mode como autorización para inyección.** La observación y la inyección activa de frames son actividades diferentes.

## Labs prácticos

Usá un adaptador propio y red lab.

### Habilitar monitor mode

```
ip link
sudo airmon-ng check
sudo airmon-ng start wlan0
iw dev
```

Confirmar que la nueva interfaz está realmente en monitor mode.

### Capturar una línea base de canal

```
sudo airodump-ng wlan0mon
```

Registrar SSIDs cercanos, BSSIDs, canales, cifrado y RSSI.

### Guardar un pcap para Wireshark

```
sudo airodump-ng --write lab-capture --output-format pcap wlan0mon
wireshark lab-capture-01.cap
```

Verificar que los frames y canales coincidan con lo esperado.

### Registrar condiciones de captura

```
adaptador:
driver:
interfaz:
canal:
distancia:
AP BSSID:
cliente presente:
tipos de frames vistos:
```

La evidencia inalámbrica depende del contexto físico y del driver.

### Verificar visibilidad de EAPOL

```
Filtro Wireshark: eapol
Esperado: reconexión desde cliente propio
Observado:
¿Suficientemente completo para análisis?:
```

No asumir que un pcap contiene material de handshake hasta inspeccionarlo.

### Comparar capturas en channel hop y canal fijo

```
Modo: channel hop
Beacons vistos:
Clientes vistos:
EAPOL visto:

Modo: canal fijo:
Beacons vistos:
Clientes vistos:
EAPOL visto:
```

Usar channel hopping para descubrimiento, luego captura en canal fijo para calidad de evidencia.

## Ejemplos prácticos

- Un tester ve beacons pero no clientes porque la ventana de captura es demasiado corta.
- Un AP del lab se pierde porque el adaptador está bloqueado en el canal equivocado.
- Un pcap contiene frames EAPOL que soportan análisis del handshake WPA.
- La tarjeta Wi-Fi interna de un laptop soporta managed mode pero no monitor mode.
- NetworkManager resetea la interfaz durante una captura.

## Notas relacionadas

- [[wireless-security]]
- [[wpa-wpa2-handshakes]]
- [[wifi-deauthentication]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[packet-analysis|Packet Analysis]]

### Notas atómicas futuras sugeridas

- wifi-channel-and-band-planning
- adapter-chipsets-for-wireless-testing
- 80211-frame-types
- radiotap-headers

## Referencias

- **Docs Oficiales:** Aircrack-ng airmon-ng — https://www.aircrack-ng.org/doku.php?id=airmon-ng
- **Docs Oficiales:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Docs Oficiales:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
