# WPA/WPA2 Handshakes

## Definición

Los WPA/WPA2 handshakes son intercambios de autenticación que permiten que un cliente y un access point prueben material de clave compartido y deriven claves de sesión sin enviar la passphrase en sí misma.

## Por qué importa

La captura de handshakes es el puente clásico entre la observación inalámbrica y la evaluación del riesgo de credenciales. Un WPA/WPA2-PSK handshake capturado no revela la contraseña directamente, pero puede habilitar el guessing offline si la passphrase es débil.

La lección defensiva es clara: la seguridad de WPA2-PSK depende fuertemente de la entropía de la passphrase y la higiene de configuración.

## Cómo funciona

La ruta de riesgo de WPA/WPA2-PSK tiene **5 pasos**:

1. **El cliente se asocia.** Una estación se conecta al AP.
2. **Ocurre el handshake.** El AP y el cliente intercambian mensajes EAPOL.
3. **El tester captura el material del handshake.** El monitor mode registra los frames relevantes.
4. **Las passphrases candidatas se testean offline.** Las herramientas derivan claves y comparan contra el intercambio capturado.
5. **Solo una passphrase que coincida tiene éxito.** Las passphrases fuertes hacen que la captura sea inútil para el guessing.

El bug no es la presencia de un handshake. El bug es un PSK adivinable o controles operacionales débiles a su alrededor.

Un ejemplo trabajado, handshake a conclusión defensiva:

```
Captura:
  EAPOL handshake desde cliente de prueba propio en lab-ap

Política de contraseñas:
  frase humana de 12 caracteres basada en el nombre de la empresa

Verificación acotada:
  lista de palabras pequeña del lab encuentra el PSK rápidamente

Diseño de red:
  mismo PSK usado por staff y guests

Decisión:
  rotar a PSK generado, separar guest/staff, y planificar autenticación Enterprise para dispositivos de alta confianza
```

El hallazgo no es "handshake capturado"; es si el secreto compartido y el diseño de red sobreviven a la captura.

## Técnicas / patrones

El testing evalúa:

- PSK vs autenticación Enterprise
- indicadores de captura EAPOL y PMKID
- SSID, BSSID, canal y presencia de clientes
- si la deautenticación es necesaria o está prohibida por las reglas del engagement
- política de passphrase, rotación, separación de guest e inventario de dispositivos

## Variantes y bypasses

El testing de WPA/WPA2 handshakes tiene **4 variantes prácticas**.

### 1. Captura de handshake natural

Un cliente se reconecta normalmente mientras el tester captura pasivamente.

### 2. Captura asistida por deauth

Una prueba en lab autorizado desconecta brevemente a un cliente para forzar la reautenticación.

### 3. Captura de PMKID

Algunos APs exponen material de clave útil para guessing offline sin un cliente conectado.

### 4. Autenticación Enterprise

WPA/WPA2-Enterprise cambia el modelo hacia configuración de certificado, identidad y EAP.

## Impacto

Ordenado aproximadamente por severidad:

- **Recuperación del PSK.** Las passphrases débiles pueden recuperarse offline.
- **Unión a la red.** Un PSK recuperado permite acceso hasta que se rote.
- **Exposición lateral.** Los clientes unidos pueden alcanzar servicios internos.
- **Expansión del scope del incidente.** Los PSKs compartidos hacen que la atribución y revocación sean más difíciles.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar passphrases de alta entropía o WPA-Enterprise.**
   El guessing offline solo es práctico cuando las contraseñas candidatas son plausibles. Los PSKs aleatorios largos o la autenticación por usuario cambian la economía.

2.
**Usar WPA3-SAE donde sea soportado.**
   WPA3-Personal mejora la resistencia al guessing offline por diccionario comparado con WPA2-PSK.

3.
**Segmentar clientes inalámbricos.**
   Incluso si se recupera un PSK, la segmentación limita el alcance del atacante.

4.
**Monitorear deauth y comportamiento de asociación inusual.**
   Los picos de management frames pueden indicar forzado activo de handshakes.

### Qué no funciona como defensa primaria

- **Ocultar el SSID.** El comportamiento del handshake y el cliente todavía filtra datos útiles.
- **Contraseñas cortas con muchos símbolos.** La longitud y la imprevisibilidad importan más que la complejidad decorativa.
- **Depender del filtrado de MAC.** Las direcciones MAC son visibles y suplantables.
- **No rotar nunca los PSKs compartidos.** Los secretos compartidos se vuelven más difíciles de confiar con el tiempo.

## Labs prácticos

Usar un AP lab propio y un cliente de prueba.

### Capturar un handshake natural

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write wpa-lab wlan0mon
```

Reconectar tu propio cliente de prueba y confirmar que EAPOL aparece en la captura.

### Inspeccionar el pcap

```
wireshark wpa-lab-01.cap
```

Filtrar por frames EAPOL y confirmar que la captura está suficientemente completa para análisis.

### Registrar calidad de passphrase

```
SSID:
Autenticación:
Longitud de passphrase:
Generada o elegida por humano:
Proceso de rotación:
Aislamiento de guest:
```

La salida defensiva es la evaluación del control, no el intento de crackeo.

### Construir una tarjeta de evidencia de handshake

```
BSSID:
canal:
cliente:
método de captura:
EAPOL/PMKID presente:
wordlist testeada:
resultado:
qué prueba esto:
qué no prueba esto:
```

El análisis de handshake necesita límites tanto como resultados.

### Revisar el blast radius del PSK

```
SSID | PSK compartido por | dispositivos | acceso guest | propietario de rotación | última rotación
```

Los PSKs compartidos se convierten en riesgo operacional cuando muchos usuarios y dispositivos dependen de un secreto.

### Decidir si la autenticación Enterprise está justificada

```
entorno:
número de usuarios:
propiedad de dispositivos:
frecuencia de offboarding:
dolor del PSK compartido:
preparación para 802.1X:
```

WPA-Enterprise es una decisión operacional tanto como criptográfica.

## Ejemplos prácticos

- Una pequeña oficina usa un PSK memorable para todo el staff y los guests.
- Una captura del lab registra EAPOL cuando un teléfono de prueba se reconecta.
- Un router expone material PMKID que puede testearse offline.
- Un PSK aleatorio largo resiste el guessing práctico incluso cuando el handshake está capturado.
- Un PSK compartido debe rotarse después de que se va un contratista.

## Notas relacionadas

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wifi-deauthentication]]
- [[wifi-wordlist-attacks]]
- [[wireshark-workflows|Wireshark Workflows]]

### Notas atómicas futuras sugeridas

- wpa3-sae
- enterprise-wifi-8021x
- pmkid-attacks
- wireless-key-rotation

## Referencias

- **Docs Oficiales:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Docs Oficiales:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Fundamental:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
