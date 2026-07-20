# Anonymity Threat Models

## Definición

Un anonymity threat model es un relato estructurado de quién intenta vincular una acción a una persona, qué puede observar y qué controles de privacidad realmente reducen esa vinculación.

## Por qué importa

El anonimato es específico del adversario. Una herramienta puede ser suficiente contra un operador de red local, insuficiente contra un sitio web e inútil contra un compromiso del dispositivo. Si no se nombra al observador, la elección de herramientas se convierte en una suposición.

## Cómo funciona

Usá el modelo de 5 preguntas:

1.
**¿Quién es el observador?**
   Red local, ISP, proveedor de VPN, sitio web, empleador, proveedor cloud, o adversario de red poderoso.

2.
**¿Qué puede ver?**
   Contenido, metadatos, identidad de cuenta, browser fingerprints, comportamiento del dispositivo, metadatos de archivos o timing de tráfico.

3.
**¿Qué puede correlacionar?**
   Logs, IPs, cookies, nombres de usuario, horarios, estilo de escritura y comportamientos repetidos.

4.
**¿Qué consecuencia sigue si ocurre la vinculación?**
   Vigilancia, acoso, impacto laboral, exposición legal, exposición de fuente o simple rastreo.

5.
**¿Qué control cambia la vista de ese observador?**
   Tor, VPN, compartimentación, limpieza de metadatos, mensajería cifrada o controles de política.

El bug no es carecer de una herramienta. El bug es no definir primero al observador y la consecuencia.

## Técnicas / patrones

- Empezar con el observador más severo realista, no el más fácil.
- Separar confidentiality de anonimato.
- Tratar los metadatos y el comportamiento como señales de identidad de primera clase.
- Escribir el threat model antes de combinar herramientas.
- Re-evaluar cada vez que el flujo de trabajo cambie.

## Variantes y bypasses

Usá los 5 modelos comunes de anonimato:

### 1. Privacidad en red local

Objetivo: ocultar actividad de operadores de redes de café, hotel, escuela u oficina.

### 2. Privacidad del ISP

Objetivo: reducir lo que un ISP puede ver sobre destinos y comportamiento.

### 3. Unlinkability del destino

Objetivo: evitar que el sitio web vincule actividad a una identidad persistente.

### 4. Protección de fuente

Objetivo: ocultar la ubicación o red del operador del destino.

### 5. Resistencia multi-observador

Objetivo: evitar correlación por un proveedor, servicio u observador poderoso a través de múltiples puntos de ventaja.

## Impacto

- Mejor elección de herramientas para Tor, VPN, mensajería y compartimentación.
- Menos afirmaciones demasiado amplias como "anónimo" o "privado" sin contexto.
- Mejor separación entre privacidad en red local y unlinkability del destino.
- Expectativas más realistas sobre lo que logs, archivos y comportamiento pueden revelar.
- Mejores decisiones operacionales sobre login, archivos y reutilización de cuentas.

## Detección y defensa

Ordenado por efectividad:

1.
**Nombrar al observador y la consecuencia**
   Si esas dos piezas faltan, el resto del modelo probablemente no está fundamentado.

2.
**Reducir señales que llevan identidad**
   La reutilización de cuentas, metadatos, cookies, estado del browser y comportamiento suelen ser más importantes que el transporte.

3.
**Elegir controles por observador**
   VPN para privacidad en red local, Tor para anonimato, compartimentación para aislamiento de dispositivo, limpieza de metadatos para fuga en archivos.

4.
**Evitar apilar herramientas en exceso**
   La complejidad puede crear más rutas de fuga de las que elimina.

### Qué no funciona como defensa primaria

- **"Privado" no es un threat model.**
- **El cifrado solo no es anonimato.**
- **Cambiar la IP solo no es unlinkability.**
- **Más herramientas no garantizan más seguridad.**

## Labs prácticos

### Escribir una matriz de observadores

```
Observador:
Puede ver contenido:
Puede ver metadatos:
Puede ver identidad:
Puede correlacionar entre sesiones:
Consecuencia si se vincula:
Mejor control:
```

Hacé esto una vez por actividad sensible.

### Comparar objetivos de anonimato

```
Objetivo:
Ocultar de red local:
Ocultar del ISP:
Ocultar del destino:
Ocultar ubicación de fuente:
Resistir correlación:
```

El objetivo te dice qué familia de controles importa.

### Separar clases de señal

```
Contenido:
Metadatos:
Identidad:
Comportamiento:
Dispositivo:
Sistema de archivos:
```

El control debe abordar la clase correcta.

### Revisar después de un cambio en el flujo de trabajo

```
¿Cambió la cuenta?
¿Cambió el dispositivo?
¿Cambió el browser?
¿Cambió la red?
¿Cambió el tipo de archivo?
¿Cambió el destinatario?
```

Cualquier respuesta sí puede cambiar el modelo de anonimato.

## Ejemplos prácticos

- Un periodista usa Tor para reducir el riesgo de correlación de destino y red local.
- Un viajero usa una VPN para reducir la visibilidad del ISP y del Wi-Fi del café.
- Un flujo de trabajo de compartición de fuentes también elimina metadatos porque el anonimato se pierde por archivos, no solo por IPs.
- Un flujo de trabajo de seguridad personal separa dispositivos y cuentas para evitar vinculación.
- Un usuario combina herramientas sin nombrar al observador y termina con una falsa sensación de seguridad.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[qubes-compartmentalization|Qubes Compartmentalization]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
