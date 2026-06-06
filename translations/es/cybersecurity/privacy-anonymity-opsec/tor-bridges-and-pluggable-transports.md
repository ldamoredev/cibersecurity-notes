# Tor Bridges and Pluggable Transports

## Definición

Los bridges de Tor son relays de Tor que no están listados en el directorio público de relays. Los transportes pluggables transforman el tráfico de Tor para que sea más difícil que un censor o filtro de red lo reconozca y bloquee.

## Por qué importa

El uso directo de Tor puede ser visible y bloqueado. En algunas redes, el riesgo no es solo que un sitio vea tráfico de salida de Tor, sino que el ISP local, la escuela, el empleador o el firewall nacional vea un intento de conexión a Tor.

Los bridges y transportes son herramientas de evasión de censura. No hacen anónimos los logins de cuentas, no eliminan fingerprints del browser ni derrotan el compromiso del endpoint. Cambian el problema de alcanzabilidad y detectabilidad del primer hop.

## Cómo funciona

Usá el modelo de evasión de 4 etapas:

1.
**Intento directo de Tor**
   Tor Browser intenta conectarse a los relays públicos de Tor conocidos.

2.
**Bloqueo o detección**
   Una red bloquea IPs de relays públicos, detecta handshakes de Tor, filtra bridges conocidos o interfiere con los patrones de tráfico.

3.
**Selección de bridge**
   El usuario obtiene un bridge desde Tor Browser, bridges.torproject.org, un bot o una fuente privada de confianza.

4.
**Camuflaje del transporte**
   Un transporte pluggable como obfs4, Snowflake, meek o WebTunnel cambia cómo aparece el tráfico en la red local.

Boceto:

```
Sin bridge:
  usuario -> relay público de Tor -> red Tor

Con bridge/transporte:
  usuario -> bridge usando transporte -> red Tor
```

El bug no es necesitar un bridge. El bug es asumir que un bridge resuelve la fuga de identidad, browser, cuenta o comportamiento.

## Técnicas / patrones

- Probar primero el Asistente de Conexión de Tor Browser.
- Usar las opciones de bridge integradas antes de una configuración manual compleja.
- Hacer coincidir el tipo de bridge con las condiciones de bloqueo local.
- Mantener privados los bridges privados; compartirlos ampliamente los hace más fáciles de bloquear.
- Registrar qué red, país, ISP y transporte se testearon.
- Evitar tratar el éxito en la evasión como éxito en el anonimato.

## Variantes y bypasses

Usá los 5 patrones de bridge/transporte:

### 1. Bridges integrados

Tor Browser incluye opciones de bridge fáciles de probar. Son convenientes, pero el conocimiento público puede hacerlos más bloqueables en redes con censura pesada.

### 2. Bridges solicitados

BridgeDB, bots y canales de soporte pueden proveer líneas de bridge. El canal de distribución importa porque los censores también intentan descubrir bridges.

### 3. obfs4

obfs4 se usa ampliamente para hacer más difícil identificar el tráfico de Tor. Igual puede bloquearse cuando los censores descubren endpoints de bridge específicos o hacen fingerprinting de patrones de tráfico.

### 4. Snowflake

Snowflake usa proxies voluntarios para ayudar a los usuarios a alcanzar Tor. Puede ser útil donde el bloqueo estático de bridges es fuerte, pero la confiabilidad puede variar.

### 5. WebTunnel y camuflaje estilo meek

Estos transportes intentan hacer que el tráfico parezca tráfico web ordinario o usan comportamiento similar al domain fronting. Pueden ayudar en algunas regiones pero pueden ser más lentos o frágiles.

## Impacto

- Capacidad de alcanzar Tor donde el acceso directo está bloqueado.
- Visibilidad local reducida de conexiones obvias a relays públicos de Tor.
- Nueva dependencia operacional en el secreto, disponibilidad y canales de distribución del bridge.
- Posible mayor atención si se monitorean el descubrimiento de bridges, solicitudes de soporte o patrones de tráfico inusuales.
- Falsa confianza si los usuarios tratan la evasión de censura como anonimato completo.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar el camino de bridge más simple que funcione**
   Preferir la configuración menos compleja que funcione en la red del usuario. La complejidad aumenta la carga de soporte y el error del usuario.

2.
**Usar los canales oficiales de adquisición de bridges**
   Los canales oficiales de Tor reducen la posibilidad de información de bridge maliciosa o desactualizada.

3.
**Mantener privadas las líneas de bridge privadas**
   Un bridge compartido ampliamente se vuelve más fácil de enumerar y bloquear. Tratar los detalles de bridge privado como sensibles.

4.
**Documentar el comportamiento específico de la red**
   La censura varía según el ISP, el país, el tiempo y el dispositivo. Registrar condiciones en lugar de asumir que un transporte funciona en todas partes.

5.
**Mantener el OPSEC más allá del éxito de la conexión**
   Una vez que Tor se conecta, los riesgos de cuenta, archivo, browser y comportamiento aún necesitan controles separados.

### Qué no funciona como defensa primaria

- **Un bridge no es una mejora de anonimato por sí solo.** Cambia principalmente la alcanzabilidad y la detectabilidad local.
- **Publicar bridges privados públicamente frustra su propósito.** Los censores pueden recopilar la misma información de bridge.
- **Una conexión exitosa no prueba resiliencia.** Los sistemas de censura se adaptan y las condiciones de red cambian.
- **Un transporte no protege contra el login de cuenta.** El destino aún puede identificar la cuenta.

## Labs prácticos

### Construir una tarjeta de decisión de evasión

```
Red:
País/región:
Tor directo funciona:
Asistente de conexión probado:
Bridge integrado probado:
Bridge solicitado probado:
Transporte:
Mensaje de error:
Resultado:
Riesgo del uso visible de Tor:
```

La tarjeta mantiene el troubleshooting vinculado a la red real y el riesgo.

### Comparar intentos directos y con bridge

```
Intento 1: Tor directo
Resultado:
Error:

Intento 2: Bridge integrado
Transporte:
Resultado:
Error:

Intento 3: Bridge solicitado
Fuente:
Transporte:
Resultado:
Error:
```

Usar solo donde testear Tor es legal y seguro para el usuario.

### Proteger la información de bridge privado

```
Fuente del bridge:
Quién lo recibió:
Dónde se almacena:
Compartido a través de:
Expiración/rotación:
Consecuencia de filtración:
```

El manejo del bridge privado es un problema OPSEC, no solo una configuración de conexión.

### Separar la evasión del anonimato

```
Problema de conexión resuelto:
Aún con login en cuenta identificadora:
Browser cambiado/personalizado:
Archivos descargados/abiertos:
Archivos subidos:
Riesgo de vínculo de comportamiento:
```

Esto previene que "Tor conectado" se convierta en "identidad protegida."

## Ejemplos prácticos

- Un usuario en una región con censura no puede conectarse directamente y usa bridges WebTunnel.
- Una red escolar bloquea IPs de relays Tor conocidos, pero un bridge integrado se conecta.
- Un bridge privado deja de funcionar después de ser compartido en un foro público.
- Un usuario alcanza Tor a través de Snowflake pero hace login en una cuenta de nombre real.
- Un equipo de soporte recopila errores específicos de la red para identificar qué transportes funcionan en una región.

## Notas relacionadas

- [[tor-and-onion-services|Tor and Onion Services]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[vpn-with-tor|VPN with Tor]]
- [[vpn-vs-tor|VPN vs Tor]]

## Referencias

- **Docs Oficiales:** Tor Browser Censorship Circumvention - https://support.torproject.org/tor-browser/circumvention/
- **Docs Oficiales:** Tor: Using Bridges - https://support.torproject.org/little-t-tor/circumvention/using-bridges/
- **Investigación / Deep Dive:** Tor Project Anti-censorship - https://community.torproject.org/anti-censorship/
