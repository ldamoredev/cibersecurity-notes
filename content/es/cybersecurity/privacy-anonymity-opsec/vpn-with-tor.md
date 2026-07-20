# VPN with Tor

## Definición

VPN con Tor significa combinar una VPN y Tor en un flujo de trabajo, generalmente como Tor sobre VPN o VPN sobre Tor. Combinarlos cambia el modelo de confianza y visibilidad; no hace automáticamente a un usuario más anónimo.

## Por qué importa

Apilar herramientas se siente reconfortante, pero los sistemas de anonimato penalizan la complejidad innecesaria. Una VPN puede ocultar el uso de Tor de una red local, o puede añadir un proveedor que vea la IP de origen del usuario. Una VPN después de Tor puede ocultar el uso de la salida de Tor de un destino, o puede forzar al usuario hacia un ruteo personalizado frágil.

El Proyecto Tor generalmente no recomienda VPN-con-Tor para usuarios ordinarios a menos que entiendan la configuración y las consecuencias para la privacidad. La pregunta correcta es: ¿qué observador cambia y qué nuevos modos de falla aparecen?

## Cómo funciona

Usá el modelo de 3 rutas:

1.
**Tor solo**
   La red local ve el uso de Tor. El relay de entrada ve la IP de origen. El destino ve una salida de Tor o la ruta de servicio onion.

2.
**Tor sobre VPN**
   El usuario se conecta primero a una VPN, luego usa Tor Browser. La red local ve uso de VPN, el proveedor de VPN ve la IP de origen y la conexión al relay de entrada de Tor, y Tor ve la salida de la VPN como el origen aparente.

3.
**VPN sobre Tor**
   El usuario se conecta primero a Tor, luego rutea una VPN a través de Tor. Esto es más difícil de configurar, a menudo frágil y puede reducir las protecciones normales de Tor si se hace mal.

Boceto de visibilidad:

```
Tor solo:
  red local -> relay de entrada Tor -> red Tor -> destino

Tor sobre VPN:
  red local -> proveedor VPN -> relay de entrada Tor -> red Tor -> destino

VPN sobre Tor:
  red local -> relay de entrada Tor -> red Tor -> proveedor VPN -> destino
```

El bug no es combinar herramientas. El bug es combinar herramientas sin poder explicar la nueva tabla de observadores.

## Técnicas / patrones

- Preferir Tor Browser solo a menos que el threat model requiera claramente ocultar el uso de Tor de la red local.
- Usar Tor sobre VPN solo cuando se entiende el balance de confianza en el proveedor de VPN.
- Tratar VPN sobre Tor como avanzado y frágil.
- Evitar el login de cuenta y la personalización del browser independientemente del stack de ruteo.
- Testear DNS, IPv6 y ruteo de apps cuando hay una VPN involucrada.
- Escribir quién ve la IP de origen, el uso de Tor, el destino y la identidad de la cuenta.

## Variantes y bypasses

Usá los 5 casos de composición:

### 1. Tor solo

El modelo Tor más simple. La visibilidad local del uso de Tor puede ser aceptable en muchos lugares. Menos piezas móviles significa menos errores de ruteo accidentales.

### 2. Tor sobre VPN

Útil cuando la visibilidad local de Tor es una preocupación o el acceso a Tor está bloqueado pero se permite una VPN. El proveedor de VPN se convierte en un punto de confianza adicional y puede ver que el usuario se está conectando a Tor.

### 3. VPN sobre Tor

A veces propuesto para ocultar el uso de la salida de Tor de los destinos, pero es difícil y puede reducir el anonimato si la autenticación, el pago, la IP de salida estática o el comportamiento de ruteo crean una identidad estable.

### 4. Mal uso de VPN más Tor Browser

El usuario ejecuta Tor Browser pero hace login en cuentas personales, instala extensiones, abre archivos externamente o usa la misma persona. La composición de ruteo no puede arreglar el comportamiento de identidad.

### 5. Confusión de ruteo dividido

Parte del tráfico usa la VPN, parte usa Tor y parte usa la red normal. Esto puede exponer actividad cuando el usuario asume que todo sigue una ruta.

## Impacto

- Posible reducción de la visibilidad de la red local hacia el uso de Tor.
- Superficie adicional de confianza y logging del proveedor de VPN.
- Requisitos de ruteo y testing de fugas más complejos.
- Mayor probabilidad de errores OPSEC por malentender la ruta.
- Posibles cambios de compatibilidad del servicio dependiendo de si los destinos ven salidas de Tor o VPN.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar el modelo más simple que satisfaga el threat model**
   Tor solo es a menudo más fácil de razonar que una configuración apilada. La simplicidad es un control de seguridad cuando el anonimato depende del comportamiento.

2.
**Escribir una tabla de observadores antes de combinar**
   Listar qué puede ver la red local, el ISP, el proveedor de VPN, la entrada de Tor, la salida de Tor, el destino y el proveedor de cuenta. Si la tabla no está clara, la configuración no está lista.

3.
**Evitar cuentas identificadoras y pagos estables**
   Una cuenta VPN, registro de pago o login de destino pueden convertirse en la señal de identidad más fuerte de la cadena.

4.
**Mantener las protecciones de Tor Browser intactas**
   No reemplaces Tor Browser con un browser diario a través de una ruta VPN/Tor. El comportamiento del browser es parte del modelo de anonimato.

5.
**Testear fugas después de cada cambio de ruteo**
   El DNS, IPv6, bypass de apps y comportamiento de reconexión pueden cambiar cuando se combinan VPN y Tor.

### Qué no funciona como defensa primaria

- **Más hops no significa más anonimato.** El modelo de confianza importa más que la cantidad de herramientas.
- **Tor sobre VPN no hace desaparecer la VPN.** El proveedor de VPN aún ve la IP de origen y la conexión a Tor.
- **VPN sobre Tor no es hardening para principiantes.** Puede crear una identidad VPN estable después de Tor.
- **Apilar herramientas no arregla la correlación de cuenta.** El destino aún conoce la cuenta con login.

## Labs prácticos

### Construir una tabla de observadores de composición

```
Flujo de trabajo: Tor solo / Tor sobre VPN / VPN sobre Tor

Observador             ¿IP de origen?  ¿Uso de Tor?  ¿Destino?  ¿Cuenta?
Red local
ISP
Proveedor VPN
Relay de entrada Tor
Relay de salida Tor
Servicio de destino
Proveedor de cuenta
```

Si esta tabla no puede completarse, la configuración es demasiado opaca para uso serio.

### Comparar el intento de ruta

```
Objetivo:
¿Ocultar el uso de Tor de la red local?
¿Ocultar la IP de origen del proveedor VPN?
¿Ocultar el uso de la salida Tor del destino?
¿Evitar la confianza en un único proveedor?
¿Necesita velocidad?
¿Necesita login de cuenta?
Modelo elegido:
```

El resultado debería exponer los balances, no solo elegir la configuración más complicada.

### Verificar superficies de fuga después de añadir VPN

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
dig o-o.myaddr.l.google.com TXT @ns1.google.com
```

Usar solo en tu propio dispositivo y red. Esto verifica la IP visible y la ruta del resolver, no el anonimato completo.

### Registrar modos de falla

```
Modo de falla                Estado esperado          ¿Testeado?
VPN se desconecta
Tor Browser cerrado
Dispositivo duerme/se despierta
Aparece portal cautivo
DNS cambia
Aparece ruta IPv6
App externa abre archivo
```

Apilar herramientas aumenta los modos de falla; la tabla los hace operacionales.

## Ejemplos prácticos

- Un usuario en una red que bloquea Tor usa primero una VPN, luego Tor Browser, y acepta la visibilidad del proveedor de VPN.
- Un usuario añade una VPN a Tor pero hace login en una cuenta personal, haciendo la ruta irrelevante para el servicio.
- Una configuración personalizada de VPN sobre Tor crea una identidad VPN estable visible para los destinos.
- Un investigador elige Tor solo porque el uso local de Tor no es riesgoso y menos piezas móviles son más seguras.
- Un dispositivo móvil reconecta VPN y Tor inconsistentemente después del sleep, cambiando la ruta asumida.

## Notas relacionadas

- [[vpn-vs-tor|VPN vs Tor]]
- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-leakage-risks|VPN Leakage Risks]]

## Referencias

- **Docs Oficiales:** Tor Project: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
