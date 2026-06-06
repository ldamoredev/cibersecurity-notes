# Deanonymization Failures

## Definición

Las fallas de desanonimización son las formas en que un flujo de trabajo supuestamente anónimo vuelve a ser vinculable a través de cuentas, metadatos, estado del browser, comportamiento, errores de red o compromiso del endpoint.

## Por qué importa

Los usuarios generalmente no pierden el anonimato porque un gran control falla. Lo pierden a través de una cadena de pequeños errores que se alinean: misma cuenta, mismo browser, mismo archivo, mismo horario, mismo dispositivo, misma fuga de red, mismo destinatario, mismo email de recuperación.

## Cómo funciona

Usá la cadena de falla de 6 eslabones:

1.
**Vínculo inicial**
   El usuario introduce una señal de identidad estable, como un login, pago o nombre de usuario.

2.
**Reutilización de estado**
   Cookies, estado del browser, estado del dispositivo o rutas del sistema de archivos persisten entre actividades.

3.
**Derrame de metadatos**
   Archivos, fotos, documentos o mensajes llevan identificadores ocultos.

4.
**Coincidencia de comportamiento**
   El timing, estilo de escritura, intereses y patrones de interacción se alinean.

5.
**Desajuste de red**
   DNS, IPv6, bypass de app o comportamiento de reconexión expone una ruta normal.

6.
**Observación cruzada**
   Un servicio, proveedor u observador conecta los puntos entre sesiones o plataformas.

El bug no es un único error. El bug es una cadena de falla que nadie revisa de extremo a extremo.

## Técnicas / patrones

- Reconstruir la cadena, no solo la última fuga.
- Preguntar dónde entró el primer identificador estable.
- Verificar si el flujo de trabajo reutiliza dispositivos, browsers, cuentas o archivos.
- Buscar puntos de derrame invisibles como email de recuperación, sincronización del dispositivo y backup en la nube.
- Identificar qué observador tenía suficientes datos para correlacionar.

## Variantes y bypasses

Usá las 7 clases de falla:

### 1. Falla de login

El usuario hace login con una identidad real en un sitio que debía mantenerse seudónimo.

### 2. Falla de archivo

Un archivo, captura de pantalla, PDF o foto contiene metadatos identificadores o contexto visible.

### 3. Falla de browser

Un browser fingerprint, conjunto de extensiones o cookie jar persiste la identidad.

### 4. Falla de dispositivo

El propio dispositivo lleva una identidad estable a través de sincronización, estado del SO o software instalado.

### 5. Falla de comportamiento

El estilo de escritura, timing o rutina del usuario apunta a la misma persona.

### 6. Falla de proveedor

El servicio, VPN, proveedor de email o nube registra suficiente para correlacionar usuarios.

### 7. Falla operacional

El flujo de trabajo mezcla identidades, transfiere archivos mal o reutiliza el compartimento equivocado.

## Impacto

- Actividad seudónima vinculada a identidad real.
- Investigación sensible expuesta a través de errores ordinarios.
- Flujos de trabajo de fuente, denunciante o seguridad personal comprometidos.
- Falsa confianza en herramientas de privacidad.
- Re-identificación por un servicio de destino o proveedor.

## Detección y defensa

Ordenado por efectividad:

1.
**Rastrear la primera señal de identidad estable**
   Encontrá el momento más temprano en que el flujo de trabajo se volvió vinculable.

2.
**Romper la cadena en múltiples puntos**
   La compartimentación, limpieza de metadatos, aislamiento del browser y separación de cuentas ayudan.

3.
**Re-testear desde la vista del observador**
   No confíes en la intención del usuario; inspeccioná lo que un observador puede ver realmente.

4.
**Eliminar la persistencia innecesaria**
   Cookies, sincronización, backups y archivos guardados suelen crear la vinculación.

5.
**Usar checklists de preflight**
   Un checklist de preflight detecta muchos errores antes de la publicación o transmisión.

### Qué no funciona como defensa primaria

- **Arreglar solo la última fuga no es suficiente.**
- **Borrar un post después de la exposición no borra logs ni copias.**
- **Cambiar solo el nombre de usuario no rompe la cadena.**
- **Asumir "nadie notó" no es evidencia.**

## Labs prácticos

### Construir una cadena de falla

```
Actividad:
Señal de identidad 1:
Señal de identidad 2:
Derrame de metadatos:
Estado del browser:
Fuga de red:
Pista de comportamiento:
Observador:
Resultado de vinculación:
```

Este es el ejercicio central de desanonimización.

### Reconstruir un error

```
Qué se suponía que era anónimo:
Primer vínculo introducido:
Qué se reutilizó:
Qué metadatos filtraron:
Qué comportamiento coincidió:
Qué observador lo correlacionó:
Dónde romper antes la próxima vez:
```

El objetivo es mejorar el flujo de trabajo, no culpar al último paso.

### Checklist de anonimato de preflight

```
¿Cuenta con nombre real? sí/no
¿Mismo perfil de browser? sí/no
¿Mismo dispositivo? sí/no
¿Metadatos limpios? sí/no
¿DNS verificado? sí/no
¿IPv6 verificado? sí/no
¿Aplicaciones externas usadas? sí/no
¿Archivos transferidos? sí/no
```

Esto detecta la ruta de falla común.

### Comparar identidad intentada vs observada

```
Persona intentada:
Señales observadas:
¿Conflicto?
Razón:
Corrección:
```

Si la intentada y la observada divergen, el flujo de trabajo tiene fugas.

## Ejemplos prácticos

- Una cuenta seudónima se vincula por un email de recuperación reutilizado.
- Una sesión de Tor se desanonimiza por un documento descargado con metadatos de autor.
- Un usuario de VPN se vincula por el mismo browser fingerprint y estilo de escritura.
- La identidad de una fuente se filtra a través de un backup en la nube y una cuenta de sincronización.
- Un investigador usa el mismo perfil de browser entre personas no relacionadas y se correlaciona.

## Notas relacionadas

- [[anonymity-threat-models|Anonymity Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[account-correlation|Account Correlation]]
- [[traffic-correlation|Traffic Correlation]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Investigación / Deep Dive:** Tor Project Research - https://research.torproject.org/
