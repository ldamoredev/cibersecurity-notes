# Tor and Onion Services

## Definición

Tor es una red de anonimato que rutea el tráfico a través de múltiples relays para reducir la vinculabilidad entre un usuario y un destino. Los onion services son servicios accesibles solo a través de Tor, con direcciones criptográficas y ubicaciones de red ocultas.

## Por qué importa

Tor no es solo una VPN más lenta. Una VPN generalmente pide al usuario que confíe en un proveedor con metadatos de origen y destino. Tor distribuye esa confianza entre relays para que un único relay no deba saber ambos extremos de la conexión.

Los onion services añaden otra idea importante: el operador del servicio puede ocultar la ubicación de red del servidor, y el cliente puede autenticar el servicio a través de la propia dirección `.onion`. Esto es útil para resistencia a la censura, protección de fuentes, publicación sensible, servicios de privacidad internos y aprender cómo los sistemas de anonimato reforman los límites de confianza.

## Cómo funciona

Usá el modelo Tor de 5 partes:

1.
**El cliente construye un circuito**
   Tor Browser elige relays y construye una ruta cifrada a través de la red.

2.
**Cada relay solo conoce a su vecino**
   El relay de entrada ve la IP del usuario pero no el destino final. El relay de salida ve el destino pero no la IP del usuario para el tráfico web normal.

3.
**El destino ve la salida**
   Para sitios web ordinarios, el sitio ve el relay de salida de Tor, no la red de origen del usuario.

4.
**Los onion services evitan salidas públicas**
   Las conexiones a onion services permanecen dentro de Tor. El cliente y el servicio se encuentran a través de circuitos Tor en lugar de exponer la IP pública del servicio.

5.
**La dirección onion lleva significado criptográfico**
   Las direcciones onion modernas son largas porque codifican identidad criptográfica, no porque sean branding aleatorio.

Boceto de conexión:

```
Navegación web normal con Tor:
  usuario -> relay de entrada -> relay intermedio -> relay de salida -> sitio web

Onion service:
  usuario -> circuito Tor -> punto de encuentro <- circuito Tor <- onion service
```

El bug no es que "Tor oculta todo". El bug es olvidar que las cuentas, el mal uso del browser, los archivos descargados, el comportamiento y la poderosa correlación de tráfico pueden seguir importando.

## Técnicas / patrones

- Usar Tor Browser en lugar de rutear un browser diario a través de Tor.
- Tratar las direcciones `.onion` como identificadores de servicio criptográficos que deben copiarse exactamente.
- Preferir versiones de onion service de servicios sensibles cuando estén disponibles y sean confiables.
- Evitar hacer login en cuentas identificadoras cuando el anonimato es el objetivo.
- Evitar abrir archivos descargados fuera del contexto protegido.
- Distinguir la navegación web normal con salida Tor del tráfico de onion service.

## Variantes y bypasses

Usá las 5 distinciones de Tor/onion service:

### 1. Web normal sobre Tor

El usuario alcanza un sitio web ordinario a través de un relay de salida Tor. La salida ve metadatos de tráfico de destino y puede ver contenido HTTP no cifrado, mientras el sitio web ve el relay de salida.

### 2. Acceso a onion service

El usuario alcanza un servicio `.onion` sin un relay de salida público hacia la web normal. La ubicación del servicio está oculta y Tor Browser puede verificar la identidad del onion service a través de la dirección.

### 3. Descubrimiento de Onion-Location

Algunos sitios web normales anuncian contrapartes onion. Esto puede dar a los usuarios una ruta que preserve la privacidad hacia el mismo servicio, pero los usuarios deberían verificar que el onion service sea esperado y legítimo.

### 4. Onion services autenticados

Algunos onion services requieren autorización del cliente. Esto protege el acceso al servicio pero no hace automáticamente anónimo el comportamiento del usuario dentro de la aplicación.

### 5. Límites de relay y correlación de tráfico

Tor distribuye la confianza, pero un observador poderoso con visibilidad cerca tanto del usuario como del destino puede intentar correlación de timing. Este es un límite a entender, no una razón para tratar Tor como inútil.

## Impacto

- Reducción de la vinculabilidad entre la IP de origen del usuario y los servicios de destino.
- Ocultamiento de la ubicación del servicio para los operadores de onion service.
- Mayor resistencia a la censura donde Tor es alcanzable o los bridges están disponibles.
- Mayor fricción del servicio, bloqueos, CAPTCHAs y compromisos de velocidad.
- Riesgo de desanonimización a través de login de cuenta, cambios en el browser, manejo de archivos y comportamiento.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar Tor Browser como el límite de acceso**
   Tor Browser combina ruteo, hardening del browser, aislamiento y comportamiento anti-fingerprinting. Un browser diario ruteado a través de Tor generalmente carece de esas protecciones.

2.
**Mantener las identidades compartimentadas**
   No mezclar cuentas con nombre real, perfiles de browser diario, archivos personales e investigación anónima. Tor no puede deshacer la identidad a nivel de aplicación.

3.
**Verificar las direcciones onion y el contexto del servicio**
   Las direcciones onion son largas y sensibles a errores tipográficos. Usar fuentes confiables, bookmarks o avisos de Onion-Location de servicios esperados.

4.
**Preferir HTTPS para tráfico web normal con salida**
   Tor oculta la IP de origen del destino, pero los relays de salida siguen estando en la ruta hacia sitios HTTP ordinarios. HTTPS sigue siendo importante.

5.
**Evitar descargas inseguras y apps externas**
   Los documentos abiertos fuera de Tor Browser pueden hacer requests de red o exponer metadatos locales. Tratar las descargas como un evento de cruce de límite.

6.
**Entender la visibilidad local**
   Una red local o un ISP puede ver el uso de Tor a menos que se usen bridges o transportes. Esa visibilidad en sí misma puede importar en algunos entornos.

### Qué no funciona como defensa primaria

- **Tor más login con nombre real no es anonimato.** El destino conoce la cuenta.
- **Un browser diario a través de Tor no es Tor Browser.** El fingerprinting del browser y el aislamiento de estado son capas diferentes.
- **Una dirección onion no hace confiable a un servicio.** Autentica la ubicación del servicio, no el comportamiento del operador.
- **Tor no protege contra el compromiso del endpoint.** El malware o el monitoreo de dispositivos gestionados puede observar la actividad antes o después de Tor.

## Labs prácticos

### Construir una tabla de observadores de Tor

```
Observador                Web normal sobre Tor          Onion service
Red local/ISP
Relay de entrada
Relay intermedio
Relay de salida
Sitio web de destino
Operador del onion service
Capa de browser/cuenta
```

La tabla debería mostrar por qué los onion services y la navegación Tor normal tienen diferentes modelos de observadores.

### Verificar el manejo de la dirección onion

```
Servicio:
Fuente de la dirección onion:
Longitud de la dirección:
¿Guardada en bookmark?:
Estado del ícono onion de Tor Browser:
Cuenta usada:
Archivos descargados:
```

Esto previene errores de copiar/pegar y confusión de capa de cuenta.

### Comparar conceptualmente el ruteo normal y el de onion service

```
Sitio normal:
  ¿Necesita relay de salida?: sí
  ¿El sitio web ve la salida Tor?: sí
  ¿IP del servidor es pública?: sí

Onion service:
  ¿Necesita relay de salida?: no
  ¿El sitio web ve la salida Tor?: no
  ¿IP del servidor es pública?: no
```

La comparación es suficiente para la mayoría de las notas defensivas sin ejecutar sondeos activos.

### Registrar una decisión de descarga segura

```
Archivo descargado:
Fuente:
¿Abrir dentro del contexto Tor?:
¿Abrir fuera del contexto Tor?:
Riesgo de acceso a red:
Riesgo de metadatos:
Decisión:
```

Los archivos descargados son una de las formas más fáciles de cruzar accidentalmente un límite de anonimato.

## Ejemplos prácticos

- Una organización de noticias ofrece un onion service para reducir la censura y proteger el acceso de fuentes.
- Un usuario visita un sitio web ordinario sobre Tor pero hace login en una cuenta personal, eliminando el anonimato de ese sitio.
- Un operador aloja un servicio sensible como onion service para evitar exponer su IP de origen.
- Un usuario abre un documento descargado en una suite de oficina normal, permitiendo que recursos externos o metadatos escapen del contexto Tor.
- Una red local bloquea los relays Tor públicos, empujando al usuario hacia bridges o transportes pluggables.

## Notas relacionadas

- [[vpn-vs-tor|VPN vs Tor]]
- [[vpn-with-tor|VPN with Tor]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tls-https|TLS / HTTPS]]

## Referencias

- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Docs Oficiales:** Tor Browser: Onion Services - https://support.torproject.org/tor-browser/features/onion-services/
- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
