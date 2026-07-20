# Wi-Fi Deauthentication

## Definición

La deautenticación Wi-Fi es el uso o abuso de management frames 802.11 para desconectar clientes de un access point.

## Por qué importa

La deautenticación muestra que la disponibilidad y la autenticación son preguntas separadas. Una red puede usar cifrado fuerte y seguir siendo vulnerable a interrupciones si los management frames no están protegidos.

También aparece en cadenas de ataque: forzar la reconexión puede ayudar a capturar handshakes o empujar a los clientes hacia un access point rogue. Eso hace que los límites estrictos de lab sean importantes.

## Cómo funciona

El abuso de deautenticación tiene **4 pasos**:

1. **Identificar AP y cliente.** El atacante observa BSSID, canal y estaciones.
2. **Enviar management frames falsificados.** Los frames afirman que el cliente o AP está terminando la asociación.
3. **El cliente se desconecta.** La estación cae y usualmente intenta reconectarse.
4. **Ocurre el efecto de seguimiento.** La reconexión puede producir un handshake o crear una oportunidad para atracción hacia un AP rogue.

El bug no es el routing de capa IP. Es la confianza en el plano de gestión en frames no autenticados o débilmente protegidos.

Un ejemplo trabajado, deauth como validación de control:

```
Setup del lab:
  AP propio, laptop cliente propio, canal 11

Línea base:
  cliente conectado y transmitiendo ping al gateway

Prueba controlada:
  5 frames deauth enviados en ventana del lab

Observado:
  el cliente se desconecta, reconecta, EAPOL aparece en pcap

Decisión:
  PMF no está requerido o no es soportado por este par cliente/AP; habilitar PMF requerido donde sea compatible
```

El resultado útil es el hallazgo de resiliencia/control, no la interrupción en sí.

## Técnicas / patrones

El testing evalúa:

- si los frames deauth afectan clientes en un lab propio
- si PMF está soportado, es opcional o requerido
- si los logs del controlador muestran picos de deauth
- si los dispositivos críticos hacen roaming o se reconectan de forma insegura
- si los dispositivos de usuarios eligen señales rogues más fuertes

## Variantes y bypasses

La deautenticación tiene **4 variantes prácticas**.

### 1. Deauth broadcast

Apunta a todos los clientes de un BSSID y es ruidosa.

### 2. Deauth específica por cliente

Apunta a una estación específica y es más controlada en labs.

### 3. Interrupción periódica

Repite frames para causar pérdida de disponibilidad sostenida.

### 4. Cadena hacia handshake o evil twin

Usa el comportamiento de desconexión/reconexión como paso de preparación para otra prueba.

## Impacto

Ordenado aproximadamente por severidad:

- **Pérdida de disponibilidad.** Los clientes se desconectan del servicio inalámbrico.
- **Oportunidad de captura de handshake.** La reconexión puede generar frames EAPOL.
- **Coerción hacia AP rogue.** Los clientes pueden conectarse a una red imitadora.
- **Riesgo operacional.** Los dispositivos médicos, industriales o de pago pueden ser sensibles a breves interrupciones.

## Detección y defensa

Ordenado por efectividad:

1.
**Requerir protected management frames donde sea posible.**
   PMF apunta directamente a la debilidad de confianza en management frames detrás del abuso común de deauth.

2.
**Usar alertas de controlador inalámbrico o WIDS.**
   Las inundaciones de deauth y los patrones anómalos de management frames deberían ser visibles.

3.
**Evitar la unión automática a redes imitadoras no confiables.**
   La configuración del cliente y la formación de usuarios reducen el riesgo de seguimiento hacia AP rogue.

4.
**Diseñar sistemas críticos con rutas cableadas o redundantes.**
   La disponibilidad inalámbrica puede interrumpirse; las operaciones críticas no deberían asumir continuidad de radio perfecta.

### Qué no funciona como defensa primaria

- **Solo contraseña WPA2 fuerte.** Protege la unión, no todos los management frames.
- **Ocultar el SSID.** Los clientes y BSSIDs siguen siendo observables.
- **Ignorar desconexiones breves.** Las ráfagas cortas pueden ser suficientes para capturar handshakes.
- **Culpar al enlace de internet.** La deauth es interrupción de capa de radio local.

## Labs prácticos

Testear solo contra un AP lab propio y cliente de prueba.

### Observar frames deauth

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write deauth-lab wlan0mon
```

Usar Wireshark para inspeccionar management frames durante una prueba controlada.

### Ejecutar una deauth controlada corta

```
sudo aireplay-ng --deauth 5 -a LAB_BSSID wlan0mon
```

Detener inmediatamente y registrar el impacto solo en el cliente de prueba.

### Verificar la configuración de PMF

```
Modelo de AP:
PMF deshabilitado / opcional / requerido:
Soporte del cliente:
Comportamiento observado:
```

Usar la prueba para impulsar la configuración, no la interrupción.

### Registrar los límites de la prueba deauth

```
BSSID autorizado:
Cliente autorizado:
Canal:
Cantidad de frames:
Hora de inicio/fin:
Impacto observado:
Rollback:
```

Las pruebas deauth deberían ser pequeñas, nombradas y reversibles.

### Monitorear la recuperación del cliente

```
desconexión observada:
tiempo de reconexión:
red incorrecta unida:
handshake capturado:
impacto visible para el usuario:
```

El comportamiento de recuperación importa tanto como si los frames fueron aceptados.

### Comparar modos PMF en un lab

```
Resultado con PMF deshabilitado:
Resultado con PMF opcional:
Resultado con PMF requerido:
Compatibilidad del cliente:
Configuración recomendada:
```

Usar solo dispositivos propios; la compatibilidad decide si PMF puede requerirse inmediatamente.

## Ejemplos prácticos

- Un teléfono del lab se reconecta y produce un handshake visible.
- Una red con PMF requerido resiste una prueba básica de deauth.
- Un lugar público tiene ondas de desconexión repetidas durante un evento.
- Un ataque de AP rogue empieza forzando a los clientes fuera del AP legítimo.
- Un dispositivo IoT crítico falla gravemente después de una breve pérdida de Wi-Fi.

## Notas relacionadas

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wpa-wpa2-handshakes]]
- [[evil-twin-access-points]]
- [[packet-analysis|Packet Analysis]]

### Notas atómicas futuras sugeridas

- protected-management-frames
- wireless-intrusion-detection
- wpa3-sae
- wifi-roaming-security

## Referencias

- **Docs Oficiales:** Aircrack-ng aireplay-ng — https://www.aircrack-ng.org/doku.php?id=aireplay-ng
- **Docs Oficiales:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
