# VPN vs Tor

## Definición

Las VPN son herramientas de ruteo de privacidad que desplazan la confianza de la ruta de red hacia un proveedor. Tor es una red de anonimato diseñada para distribuir la confianza entre relays y reducir la vinculabilidad entre origen y destino.

Las VPN y Tor se superponen, pero no son equivalentes.

## Por qué importa

La frase "ocultar mi IP" hace que las VPN y Tor suenen similares. Sus threat models son diferentes.

Una VPN generalmente confía en un proveedor que puede ver la IP de origen del usuario y los metadatos de tráfico. Tor está diseñado para que ningún relay único deba saber tanto quién es el usuario como qué destino está visitando, aunque Tor tiene sus propios límites de rendimiento, bloqueo, usabilidad y correlación.

Frase contundente: Las VPN son herramientas de privacidad. Tor es una red de anonimato.

## Cómo funciona

Usá la comparación de 4 observadores:

1.
**Red local e ISP**
   Tanto VPN como Tor pueden reducir la visibilidad directa de los destinos finales. Siguen revelando que el usuario se está conectando a un servidor VPN o a una entrada/bridge de Tor a menos que se camufle con otros mecanismos.

2.
**Proveedor de ruteo**
   Un proveedor de VPN generalmente puede ver la IP de origen del usuario y los metadatos de destino. Tor distribuye la confianza entre relays de entrada, medio y salida para que un relay no deba ver toda la ruta.

3.
**Sitio web de destino**
   Un sitio web ve la IP de salida de la VPN o de Tor. Aún puede identificar al usuario a través de login, cookies, browser fingerprinting, comportamiento o contenido enviado.

4.
**Observador global o poderoso**
   Tor es más fuerte que una VPN contra un único observador proveedor, pero la correlación de tráfico por un observador poderoso que vigila ambos extremos sigue siendo un límite conocido del anonimato.

Tabla de comparación:

```
Propiedad                  VPN                           Tor
Objetivo principal         ruteo de privacidad           red de anonimato
Modelo de confianza        un proveedor                  relays distribuidos
IP de origen en primer hop el proveedor VPN la ve        el relay de entrada/bridge la ve
Destino en la salida       el proveedor VPN puede verlo  la salida ve el destino, no el origen
Velocidad                  generalmente más rápida       generalmente más lenta
Bloqueo                    menos bloqueada               más bloqueada por algunos servicios
Disciplina en el browser   sigue siendo importante       esencial
Mejor ajuste               Wi-Fi hostil, privacidad ISP  anonimato y unlinkability
```

El bug no es elegir la herramienta equivocada universalmente. El bug es elegir sin nombrar al observador.

## Técnicas / patrones

- Usar VPN cuando la principal preocupación es la red local, la visibilidad del ISP, el Wi-Fi hostil o el acceso a red corporativa/privada.
- Usar Tor Browser cuando la principal preocupación es el anonimato de los servicios de destino y la confianza en un único proveedor.
- Evitar hacer login en cuentas identificadoras cuando el anonimato importa.
- No personalizar Tor Browser casualmente; la unicidad debilita el conjunto de anonimato.
- Tratar VPN más Tor como un modelo de confianza cambiado, no como una mejora automática.
- Separar los objetivos de velocidad/conveniencia de los objetivos de anonimato.

## Variantes y bypasses

Usá las 6 dimensiones de comparación:

### 1. Concentración de confianza

Una VPN concentra la confianza en un proveedor. Tor distribuye la confianza entre relays para que ningún relay único deba ver tanto el origen como el destino.

### 2. Browser fingerprinting

Una VPN cambia la ruta de red pero deja el browser mayormente sin cambios. Tor Browser está diseñado para reducir la unicidad del fingerprint, pero los cambios del usuario y los logins de cuentas pueden derrotarlo.

### 3. Reputación de salida

Las salidas de VPN pueden ser aceptadas por más servicios, dependiendo de la reputación del proveedor. Las salidas de Tor suelen estar bloqueadas, con rate limiting o con desafíos porque son infraestructura de anonimato pública.

### 4. Rendimiento

Las VPN son generalmente más rápidas porque el tráfico toma una ruta más corta a través de un proveedor. Tor es más lento porque el tráfico se rutea a través de múltiples relays y prioriza las propiedades de anonimato.

### 5. Censura y bloqueo

Las VPN pueden eludir algunos bloqueos de red pero también pueden ser bloqueadas. Los bridges y transportes pluggables de Tor están diseñados para la resistencia a la censura, pero la configuración y el riesgo local importan.

### 6. Contexto legal y organizacional

Las VPN corporativas suelen ser infraestructura de control de acceso monitoreada. El uso de Tor puede ser sospechoso en algunos entornos. La elección de herramienta debería considerar las reglas locales, la seguridad y la autorización.

## Impacto

- Mejor selección de herramientas para privacidad del ISP, redes hostiles, censura, anonimato y acceso corporativo.
- Reducción de la falsa confianza al tratar las VPN como herramientas de anonimato.
- Mejor comprensión de por qué importa el comportamiento de Tor Browser.
- Evitación de complejidad innecesaria al apilar VPN y Tor sin una razón clara.
- Comunicación más clara en informes, labs y threat models personales.

## Detección y defensa

Ordenado por efectividad:

1.
**Elegir basándose en el observador y la consecuencia**
   Si el principal observador es una red local hostil o un ISP, una VPN de confianza puede ser suficiente. Si el problema principal es la unlinkability de los servicios de destino o la confianza en un único proveedor, Tor es generalmente la herramienta más relevante.

2.
**Usar Tor Browser como fue diseñado cuando el anonimato importa**
   El conjunto de anonimato de Tor depende de que los usuarios se vean similares. Las extensiones, el redimensionamiento, las fuentes personalizadas, la configuración inusual y los logins con nombre real pueden socavar eso.

3.
**Usar VPN para privacidad de ruteo, no para borrado de identidad**
   Una VPN puede ocultar los metadatos de destino de la red local o el ISP, pero las señales del proveedor y del servicio de destino siguen importando.

4.
**Evitar la vinculación de cuenta y comportamiento**
   Ni VPN ni Tor protegen el anonimato si el usuario hace login en cuentas identificadoras, sube archivos identificadores o repite comportamiento vinculable.

5.
**Documentar las elecciones de herramientas combinadas**
   Tor sobre VPN y VPN sobre Tor cambian quién ve qué. La complejidad puede crear errores operacionales, así que escribí el modelo de confianza.

### Qué no funciona como defensa primaria

- **VPN no es Tor-lite.** Desplaza la confianza hacia un proveedor y no proporciona el modelo de relay distribuido de Tor.
- **Tor no es invisibilidad mágica.** El mal uso del browser, las cuentas, los archivos, el comportamiento y la poderosa correlación de tráfico pueden seguir importando.
- **Combinar VPN y Tor no es automáticamente más fuerte.** Puede añadir complejidad y nuevos modos de falla.
- **Cambiar la IP no es unlinkability.** Las cookies, logins, fingerprints y comportamiento pueden aún conectar sesiones.

## Labs prácticos

### Construir una tabla de observadores

```
Escenario:
Herramienta: VPN / Tor / ninguna

Observador              Qué ven                         Riesgo residual
Wi-Fi local
ISP
Proveedor VPN
Relay de entrada/bridge de Tor
Relay de salida de Tor
Sitio web de destino
Proveedor de cuenta
Dispositivo/browser
```

La tabla hace visible el modelo de confianza antes de que la elección de herramientas se convierta en hábito.

### Comparar la IP de origen aparente

```
curl -4 https://ifconfig.me
```

Ejecutar sin VPN, con VPN y desde dentro de un entorno capaz de Tor donde sea apropiado. No tratar el cambio de IP de origen como prueba de anonimato.

### Comparar el riesgo de identidad del browser

```
Abrir un test de fingerprinting en:
1. browser diario sobre VPN
2. perfil de browser limpio sobre VPN
3. Tor Browser

Comparar:
- estado de login de cuenta
- timezone/idioma
- tamaño de pantalla
- lista de extensiones
- advertencia de fingerprint o resultado de unicidad
```

La lección es que la VPN y el anonimato del browser son capas diferentes.

### Decidir entre VPN y Tor

```
Objetivo:
Observador principal:
Consecuencia si se vincula:
¿Necesita velocidad?
¿Necesita login?
¿Necesita anonimato del destino?
Riesgo si Tor es visible:
Herramienta recomendada:
Razón:
```

Esto previene que "más herramientas" reemplace el razonamiento del threat model.

### Registrar la compatibilidad del servicio

```
Servicio:
VPN permitida:
Tor permitida:
CAPTCHAs/desafíos:
Riesgo de bloqueo de cuenta:
Problema de términos o política:
Flujo de trabajo alternativo:
```

Las herramientas de anonimato interactúan con los sistemas anti-abuso de los servicios; esa realidad operacional pertenece al plan.

## Ejemplos prácticos

- Un viajero usa una VPN en el Wi-Fi del hotel para reducir la exposición de metadatos de la red local.
- Un investigador usa Tor Browser para evitar confiar en un único proveedor de VPN con metadatos de origen y destino.
- Un usuario hace login en una cuenta personal sobre Tor, haciendo la sesión identificable para el servicio.
- Una VPN corporativa rutea todo el tráfico a través de la infraestructura corporativa monitoreada para control de acceso.
- Un usuario apila VPN y Tor pero crea errores porque no puede explicar quién ve ahora qué tráfico.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Docs Oficiales:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
