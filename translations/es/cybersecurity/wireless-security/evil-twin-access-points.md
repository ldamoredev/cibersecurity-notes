# Evil Twin Access Points

## Definición

Un evil twin access point es una red inalámbrica rogue que imita un SSID legítimo para atraer a clientes a conectarse a una red controlada por un atacante.

## Por qué importa

Los ataques de evil twin explotan la confianza del cliente, el hábito del usuario y las señales débiles de identidad de red. El nombre del access point solo no es prueba de que la red sea legítima.

Este tema pertenece entre la seguridad inalámbrica y la ingeniería social: la capa de radio atrae al dispositivo, mientras que la capa humana o de aplicación puede exponer credenciales o tráfico.

## Cómo funciona

El riesgo de evil twin tiene **5 pasos**:

1. **Elegir un SSID objetivo.** La red rogue imita un nombre familiar.
2. **Transmitir un AP imitador.** El atacante usa potencia de señal, ubicación o timing para atraer clientes.
3. **El cliente se conecta.** La unión automática o la selección del usuario envía el dispositivo a la red rogue.
4. **El tráfico es controlado.** La red rogue puede rutar, bloquear, inspeccionar o redirigir el tráfico.
5. **Ocurre el ataque de seguimiento.** Los captive portals, la manipulación de DNS, errores TLS o MITM local se vuelven posibles.

El bug es confiar en el texto del SSID como identidad en lugar de usar autenticación fuerte y protección en la capa de aplicación.

Un ejemplo trabajado, lab de concienciación sin captura de credenciales:

```
Lab:
  SSID "Guest-Lab" duplicado en AP aislado

Comportamiento del cliente:
  teléfono de prueba muestra dos redes con el mismo nombre

Portal:
  muestra página de formación sin campos de credenciales

Observación:
  el usuario no puede distinguir legitimidad solo por el nombre del SSID

Decisión:
  deshabilitar auto-join para SSIDs públicos, monitorear BSSIDs duplicados, y evitar ingresar credenciales en portales Wi-Fi
```

Los labs de evil twin deberían enseñar el fallo de confianza sin cosechar secretos.

## Técnicas / patrones

El testing evalúa:

- si los dispositivos se unen automáticamente a SSIDs conocidos
- si la red legítima usa certificados Enterprise o solo PSK
- si los usuarios aceptan captive portals o advertencias de certificado
- si el tráfico DNS y HTTP puede manipularse después de la conexión
- si el monitoreo detecta SSIDs duplicados o BSSIDs rogues

## Variantes y bypasses

Los ataques de evil twin tienen **4 variantes comunes**.

### 1. Imitador de red abierta

Imita un nombre de Wi-Fi público o guest y se basa en la familiaridad del usuario.

### 2. Señuelo con captive portal

Muestra una página falsa de login o registro después de la conexión.

### 3. Atracción por señal más fuerte

Ubica el AP rogue suficientemente cerca para parecer más confiable que el AP real.

### 4. Atracción asistida por deauth

Fuerza a los clientes fuera del AP real para que se reconecten al rogue.

## Impacto

Ordenado aproximadamente por severidad:

- **Captura de credenciales.** Los portales falsos pueden engañar a los usuarios para ingresar contraseñas.
- **Manipulación de tráfico.** El DNS y el tráfico no cifrado pueden modificarse.
- **Compromiso de sesión.** La seguridad de aplicación débil puede filtrar tokens o cookies.
- **Entrega de malware.** Los captive portals o redirecciones pueden llevar a contenido hostil.
- **Erosión de confianza.** Los usuarios aprenden hábitos inseguros alrededor de los prompts y advertencias de Wi-Fi.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar WPA-Enterprise con validación de certificado para redes confiables.**
   La validación correcta de certificado da a los clientes una verificación real de identidad de red más allá del texto del SSID.

2.
**Deshabilitar auto-join para redes públicas riesgosas.**
   Reducir la conexión automática limita la atracción silenciosa.

3.
**Monitorear BSSIDs rogues y SSIDs duplicados.**
   Los controladores inalámbricos y los surveys pueden detectar APs no autorizados usando nombres familiares.

4.
**Formar a usuarios para no ingresar credenciales en portales Wi-Fi para acceso corporativo.**
   El comportamiento del usuario importa porque los evil twins frecuentemente cruzan hacia el phishing.

5.
**Mantener TLS de capa de aplicación fuerte.**
   TLS previene muchas manipulaciones en la misma red incluso después de que un cliente se une a una red mala.

### Qué no funciona como defensa primaria

- **Reconocer el nombre del SSID.** Los nombres son fáciles de copiar.
- **Asumir que un ícono de candado en la configuración Wi-Fi prueba seguridad.** Puede que solo muestre cifrado de enlace local.
- **Usar VPN como único control.** VPN ayuda después de la conexión pero no arregla el phishing de credenciales ni la mala confianza del cliente.
- **Ignorar advertencias de certificado.** Las advertencias son frecuentemente la primera señal visible de intercepción.

## Labs prácticos

Usar un lab cerrado con tu propio cliente. No recolectar credenciales reales.

### Inventariar SSIDs duplicados

```
sudo airodump-ng wlan0mon
```

Buscar el mismo ESSID con diferentes BSSIDs, canales y cifrado.

### Crear un lab de concienciación sin credenciales

```
SSID:
Comportamiento del cliente:
Texto del captive portal:
Sin campos de contraseña:
Punto de educación del usuario:
```

Demostrar el riesgo de reconocimiento sin cosechar secretos.

### Validar la detección de AP rogue

```
Lista de BSSIDs esperados:
Lista de BSSIDs detectados:
Duplicados desconocidos:
Fuente de alerta:
Acción tomada:
```

Convertir el lab en una verificación de monitoreo.

### Crear un inventario de auto-join de clientes

```
dispositivo | SSIDs guardados | ¿auto-join? | ¿público/abierto? | propietario | cambio necesario
```

El auto-join es la mitad del lado del cliente del riesgo de evil twin.

### Revisar seguridad del portal

```
el portal pide credenciales:
advertencia de certificado mostrada:
dominio mostrado:
texto de formación:
prueba de no-secreto:
```

Los labs de concienciación deberían evitar recolectar credenciales o normalizar la entrada insegura.

## Ejemplos prácticos

- Un SSID falso de cafetería atrae laptops configurados para auto-join.
- Un AP rogue cerca de una oficina transmite el nombre de la red guest corporativa.
- Los usuarios ingresan credenciales VPN en un captive portal falso.
- Un dispositivo acepta una red con el mismo SSID pero seguridad más débil.
- Un controlador inalámbrico marca un BSSID desconocido transmitiendo un SSID protegido.

## Notas relacionadas

- [[wireless-security]]
- [[wifi-deauthentication]]
- [[mitm-on-local-networks]]
- [[osint|OSINT]]
- [[oauth-security|OAuth Security]]

### Notas atómicas futuras sugeridas

- captive-portal-security
- enterprise-wifi-8021x
- phishing-kill-chain
- [[mfa-phishing-resistance]]

## Referencias

- **Docs Oficiales:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Docs Oficiales:** Aircrack-ng airbase-ng — https://www.aircrack-ng.org/doku.php?id=airbase-ng
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
