# OPSEC Failure Chains

## Definición

Una cadena de falla OPSEC es una secuencia de pequeños errores que juntos revelan una identidad, relación o actividad sensible.

## Por qué importa

La mayoría de las fallas de privacidad operacional no son dramáticas. Son ordinarias: un número de teléfono reutilizado, un archivo con metadatos, un perfil de browser, una elección de palabras descuidada, una cuenta de sincronización, un patrón de timing, una captura de pantalla filtrada, una respuesta descuidada. El peligro está en la cadena.

## Cómo funciona

Usá la cadena de 6 pasos:

1.
**Semilla de identidad**
   Un identificador real entra en el flujo de trabajo.

2.
**Persistencia**
   El identificador se almacena en el estado del browser, archivos, backups o contactos.

3.
**Exposición**
   El identificador se vuelve visible para otro servicio, destinatario u observador.

4.
**Correlación**
   Pistas separadas se vinculan a través de timing, contenido, red o comportamiento.

5.
**Escalada**
   El observador ahora tiene suficiente evidencia para conectar identidades o actividades.

6.
**Consecuencias**
   La eliminación o negación suele llegar demasiado tarde porque copias, logs y capturas de pantalla ya existen.

El bug no es el último error. El bug es que la cadena nunca fue revisada como un todo.

## Técnicas / patrones

- Construir checklists de preflight.
- Separar identidades, dispositivos y rutas de red.
- Preguntar dónde existen copias antes de compartir.
- Eliminar la persistencia innecesaria.
- Reconstruir una falla como una cadena, no como un bug único.
- Escribir qué observador puede conectar qué señales.

## Variantes y bypasses

Usá los 5 tipos de cadena:

### 1. Cadena de identidad

La misma cuenta, teléfono o ruta de recuperación vincula actividades.

### 2. Cadena de archivos

Un documento o imagen lleva metadatos o contexto visible que vincula al usuario.

### 3. Cadena de browser

Cookies, fingerprints, extensiones y estado del perfil reutilizan identidad.

### 4. Cadena de red

DNS, IP, IPv6 o el comportamiento de ruteo expone el mismo entorno.

### 5. Cadena de comportamiento

Estilo de escritura, horario, hábitos y relaciones forman el eslabón faltante.

## Impacto

- Un único error se compone en una atribución confiante.
- El trabajo seudónimo se vuelve vinculable entre servicios.
- La actividad sensible se expone mucho después de que el usuario cree que terminó.
- El usuario obtiene una falsa sensación de que cada paso individual era inofensivo.
- La recuperación suele ser imposible una vez que la cadena está completa.

## Detección y defensa

Ordenado por efectividad:

1.
**Revisar toda la cadena antes de actuar**
   Pensá en pasos, no en eventos.

2.
**Cortar la persistencia**
   Menos estados guardados significa menos vínculos futuros.

3.
**Separar identidades por defecto**
   Los dispositivos, cuentas y contextos no deberían compartirse casualmente.

4.
**Hacer preflight de acciones sensibles**
   Un checklist detecta errores simples que construyen cadenas.

5.
**Asumir que existen copias**
   Planificá para logs, backups, capturas de pantalla, reenvíos y cachés.

### Qué no funciona como defensa primaria

- **Arreglar un solo paso no borra los vínculos anteriores.**
- **Borrar evidencia después del hecho no garantiza su eliminación.**
- **"Nadie notó" no es una estrategia de privacidad.**
- **Las buenas intenciones no rompen la correlación.**

## Labs prácticos

### Mapear una cadena

```
Actividad:
Semilla de identidad:
Persistencia:
Exposición:
Pista de correlación:
Observador:
Resultado:
```

Esta es la revisión OPSEC básica.

### Escribir un checklist de preflight

```
¿Se usó identidad real?
¿Mismo dispositivo?
¿Mismo browser?
¿Misma ruta de recuperación?
¿Metadatos limpios?
¿Se esperan copias?
¿Destinatario seguro?
¿Necesita reinicio?
```

El checklist es el control.

### Reconstruir una falla

```
Qué ocurrió:
Primer eslabón:
Segundo eslabón:
Tercer eslabón:
¿Podría haberse cortado algún eslabón antes?
```

Usá esto después de un error, no solo antes.

### Comparar estado intentado y observado

```
Separación intentada:
Reutilización observada:
Qué eslabón hizo posible la cadena:
```

Esto muestra si el flujo de trabajo realmente se mantuvo separado.

## Ejemplos prácticos

- Una cuenta seudónima se vincula a través del mismo número de recuperación.
- Un archivo fuente contiene metadatos y un backup en la nube compartida.
- Un perfil de browser y cookie jar conectan actividades entre sitios.
- Un estilo de escritura y patrón de timing vinculan dos personas separadas.
- Una captura de pantalla expone una notificación que completa la cadena.

## Notas relacionadas

- [[deanonymization-failures|Deanonymization Failures]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[account-correlation|Account Correlation]]
- [[traffic-correlation|Traffic Correlation]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
