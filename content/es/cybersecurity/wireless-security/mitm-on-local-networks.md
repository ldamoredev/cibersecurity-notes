# MITM on Local Networks

## Definición

Un ataque man-in-the-middle en redes locales es el posicionamiento secreto entre dos partes que se comunican para interceptar, inspeccionar o modificar el tráfico en tránsito.

## Por qué importa

El MITM local difiere del MITM de internet en que el atacante ya está en la misma LAN o WLAN. Eso significa que la presunción de confianza de capa 2 hace que los controles de capa de red sean más difíciles de aplicar.

El modelo de amenaza hostile-LAN — asumir que cualquier red no gestionada puede tener un actor adversarial — es la respuesta defensiva correcta, especialmente para acceso remoto, trabajo en público y redes de guest.

## Cómo funciona

El MITM en redes locales tiene **5 capas**:

1. **Posicionamiento de capa 2.** El atacante inserta su dispositivo en el camino de datos usando ARP poisoning, AP rogue u otras técnicas.
2. **Captura de tráfico.** El tráfico que fluye a través del atacante está disponible para inspección.
3. **Análisis de metadatos.** DNS, SNI, tamaños de paquetes y timing se filtran incluso con cifrado.
4. **Intento de intercepción de capa de aplicación.** Los protocolos sin cifrar o con TLS débil pueden modificarse o proxificarse.
5. **Aprovechamiento del comportamiento del usuario.** Los errores de certificado ignorados, los portales de captive network y el comportamiento de reconexión amplían las oportunidades.

El bug es asumir que estar en la misma red es prueba de confianza.

Un ejemplo trabajado, MITM como evaluación de suposición de red hostile:

```
Entorno:
  evaluación de seguridad de red de café/hotel — ¿cómo se comporta un empleado remoto?

Tráfico observado (lab):
  queries DNS, SNI, peticiones HTTP en texto plano

Comportamiento del usuario:
  el usuario aceptó advertencia de certificado HTTPS para intranet corporativa

Supuesto previo:
  "TLS protege todo"

Hallazgo:
  TLS protege el payload pero los metadatos se filtran; los errores de certificado indican bypass activo

Decisión:
  requerir VPN en redes no confiables, formación en advertencias de certificado, HSTS para intranet
```

El resultado MITM es qué suposiciones de confianza fallaron, no solo si el tráfico fue capturado.

## Técnicas / patrones

El testing evalúa:

- qué tráfico es visible con solo posicionamiento pasivo
- si las aplicaciones usan HTTP en texto plano o TLS débil
- si las advertencias de certificado son habituales o investigadas
- si el DNS puede manipularse para redirigir resolución
- si la VPN está requerida en redes no confiables

## Variantes y bypasses

El MITM local tiene **5 variantes comunes**.

### 1. MITM basado en ARP

Usa ARP poisoning para redirigir tráfico de capa 2 a través del atacante en una LAN cableada o inalámbrica.

### 2. AP rogue

Un access point falso atrae a los clientes a una red controlada por el atacante.

### 3. MITM de DNS

La manipulación de respuestas DNS redirige resolución de nombres a hosts controlados por el atacante.

### 4. Portales captive y phishing de red

Los portales imitadores capturan credenciales antes de que se establezcan sesiones cifradas.

### 5. Fallo de TLS

Las advertencias de certificado ignoradas, el pinning roto o los downgrades de cifrado permiten intercepción activa.

## Impacto

Ordenado aproximadamente por severidad:

- **Intercepción de credenciales.** Los portales y el tráfico HTTP pueden filtrar contraseñas o tokens.
- **Fugas de sesión.** Los tokens y cookies en tráfico no cifrado pueden capturarse.
- **Fugas de metadatos.** El DNS y el SNI revelan patrones de uso incluso con cifrado de contenido.
- **Modificación de datos.** El tráfico HTTP puede alterarse en tránsito.
- **Cadenas de ataque.** El posicionamiento MITM habilita ataques de seguimiento como entrega de exploits o cosechar hashes NTLM.

## Detección y defensa

Ordenado por efectividad:

1.
**Asumir que las redes públicas y no gestionadas son hostiles y requerir VPN.**
   El cifrado de capa de red desde el dispositivo del usuario hasta un endpoint de confianza mitiga la mayoría de los riesgos MITM locales.

2.
**Aplicar TLS fuerte, HSTS y certificate pinning en servicios.**
   La intercepción de TLS requiere que el usuario acepte un certificado no confiable; HSTS y el pinning hacen eso más visible.

3.
**Tratar las advertencias de certificado como incidentes de seguridad.**
   Los usuarios que ignoran las advertencias son el pathway más confiable para el bypass activo de TLS.

4.
**Deshabilitar protocolos en texto plano para servicios sensibles.**
   HTTP, telnet y FTP revelan credenciales y contenido sin necesidad de bypass de cifrado.

5.
**Usar entradas ARP estáticas para gateways críticos y ARP inspection dinámica.**
   Reduce la superficie del vector de envenenamiento ARP de capa 2.

### Qué no funciona como defensa primaria

- **Confiar en la seguridad Wi-Fi sola.** WPA2 cifra el enlace de radio; no previene MITM entre clientes en la misma red.
- **Solo VLAN.** El MITM de capa 2 opera dentro de VLANs.
- **Ignorar resolución DNS no cifrada.** El DNS revela metadatos de intención incluso cuando el contenido está cifrado.
- **Confiar en el nombre de la red.** Los SSIDs y nombres de red no están autenticados.

## Labs prácticos

Usar solo redes y dispositivos propios del lab.

### Registrar qué es observable sin descifrado

```
queries DNS:
campos SNI:
peticiones HTTP en texto plano:
metadatos de tamaño y timing:
```

El posicionamiento pasivo revela más de lo que la mayoría de los usuarios esperan.

### Verificar TLS en servicios internos

```
Servicio:
Versión TLS:
HSTS habilitado:
Certificate pinning:
¿El certificado es de confianza en clientes del lab?
¿El navegador muestra advertencia?
```

La verificación de certificado es la defensa del usuario más visible contra el MITM activo de TLS.

### Crear una guía de evaluación de redes hostiles

```
¿La red es de confianza?
VPN requerida antes de conectar:
Servicios que necesitan TLS verificado:
Servicios que usan HTTP en texto plano:
Comportamiento esperado del usuario en advertencias:
```

Tratar las redes no gestionadas como hostile-by-default es la actitud correcta, no el caso especial.

### Construir un checklist de supuestos MITM

```
¿Tráfico DNS está cifrado o expuesto?
¿Las aplicaciones usan HTTP?
¿Las advertencias de certificado son ignoradas habitualmente?
¿La VPN es requerida en redes no confiables?
¿Los gateways críticos tienen entradas ARP estáticas?
¿ARP inspection dinámica está habilitada?
```

### Verificar la aplicación del modelo hostile-LAN

```
Política de VPN:
Excepciones conocidas:
Servicios sin TLS:
Comportamiento de usuario en advertencias de cert:
Monitoreo de anomalías de red local:
```

## Ejemplos prácticos

- Una laptop en un hotel tiene queries DNS expuestas antes de que se establezca el túnel VPN.
- Un servicio interno usa HTTP para un endpoint legacy y filtra tokens de sesión.
- Un usuario acepta una advertencia de certificado "de costumbre" en un captive portal.
- ARP inspection dinámica bloquea un intento de envenenamiento de capa 2 en un lab.
- Una VPN requerida en redes no confiables elimina la mayor parte de la superficie de ataque MITM local.

## Notas relacionadas

- [[wireless-security]]
- [[arp-poisoning]]
- [[evil-twin-access-points]]
- [[bettercap-workflows]]
- [[tls-security|TLS Security]]
- [[network-fundamentals|Network Fundamentals]]

### Notas atómicas futuras sugeridas

- hostile-lan-model
- vpn-security
- dns-over-https
- tls-certificate-validation

## Referencias

- **Docs Oficiales:** bettercap documentation — https://www.bettercap.org/
- **Fundamental:** OWASP Transport Layer Protection — https://owasp.org/www-community/controls/Transport_Layer_Protection_Cheat_Sheet
- **Mitigación:** NIST SP 800-52 TLS guidelines — https://csrc.nist.gov/publications/detail/sp/800-52/rev-2/final
