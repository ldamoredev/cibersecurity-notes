# Tails Operational Model

## Definición

Tails es un sistema operativo portátil diseñado para rutear la actividad de internet a través de Tor y reducir las trazas en la computadora donde se ejecuta. Su modelo de seguridad es operacional: ayuda a crear una sesión temporal centrada en Tor, pero no es magia.

## Por qué importa

Tails es útil cuando el entorno operativo importa tanto como el browser. Puede reducir trazas en una computadora prestada o compartida, proveer un conjunto de herramientas consistente orientado a Tor, y ayudar a evitar usar el SO diario para trabajo sensible.

Pero Tails no protege contra todas las amenazas. No puede arreglar el comportamiento inseguro de cuentas, los metadatos de archivos, el firmware comprometido, el hardware malicioso, la vigilancia física ni a un usuario que mezcla múltiples identidades en una sesión.

## Cómo funciona

Usá el modelo Tails de 5 partes:

1.
**Arrancar en un sistema operativo separado**
   Tails se ejecuta de forma independiente del SO instalado normalmente.

2.
**Usar Tor por defecto**
   Las aplicaciones de internet están diseñadas para usar Tor en lugar de la ruta de red normal.

3.
**Dejar menos estado local**
   Tails está construido para sesiones temporales. La persistencia es opcional y debe configurarse intencionalmente.

4.
**Incluir herramientas de privacidad**
   Tails incluye herramientas para navegación Tor, manejo de archivos, cifrado, limpieza de metadatos y flujos de trabajo de borrado seguro.

5.
**Depender de la disciplina del usuario**
   El límite de sesión falla si el usuario hace login en cuentas identificadoras, reutiliza archivos o mezcla propósitos.

Boceto de sesión:

```
SO usual apagado
Tails arranca desde USB
red se conecta
Tor se conecta
actividad ocurre dentro de la sesión temporal
el apagado limpia el estado no persistente
```

El bug no es usar persistencia o archivos. El bug es usarlos sin reconocer que se convierten en vínculos de identidad.

## Técnicas / patrones

- Usar una sesión Tails para un solo propósito cuando importa la no-vinculabilidad.
- Reiniciar entre identidades o actividades no relacionadas.
- Limpiar metadatos antes de compartir archivos.
- Evitar conectar el USB de Tails a un SO no confiable en ejecución para transferir archivos.
- Tratar el Almacenamiento Persistente como sensible y vinculable.
- Verificar la instalación y actualizaciones de Tails desde fuentes confiables.
- Recordar que los observadores locales pueden ver el uso de Tor o Tails.

## Variantes y bypasses

Usá los 6 límites operacionales:

### 1. Límite de sesión temporal

Tails reduce el estado residual después del apagado. Esto ayuda con las trazas locales pero no borra la actividad registrada por sitios web, cuentas, redes o destinatarios.

### 2. Límite de Almacenamiento Persistente

La persistencia es útil para claves, documentos y configuraciones, pero puede vincular sesiones e identidades si se reutiliza descuidadamente.

### 3. Límite de visibilidad de Tor

Tails rutea a través de Tor, pero la red local puede ver el uso de Tor a menos que se usen bridges. Los sitios de destino pueden ver tráfico de salida de Tor.

### 4. Límite de archivos

Los archivos pueden llevar metadatos hacia o desde Tails. Limpiar y verificar los archivos sigue siendo necesario.

### 5. Límite de hardware

Tails no puede proteger de forma confiable contra firmware comprometido, periféricos maliciosos, implantes de hardware u observación física.

### 6. Límite de actividad

Usar la misma sesión para múltiples identidades puede vincularlas a través de circuitos, archivos, timing, cuentas o estado del browser.

## Impacto

- Menor dependencia del SO diario para actividades sensibles.
- Menor riesgo de trazas locales después del apagado cuando no se usa persistencia.
- Mejor disciplina de flujo de trabajo para tareas centradas en Tor.
- Riesgo de falsa confianza si Tails se trata como anonimato completo.
- Riesgo de vinculación a través de persistencia, login de cuenta, metadatos y sesiones de propósito mixto.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir el propósito antes de arrancar**
   Una sesión Tails debería tener un solo propósito operacional. Mezclar email de trabajo, cuentas personales e investigación sensible en una sesión debilita el límite.

2.
**Reiniciar entre actividades no vinculables**
   Reiniciar es un control de separación simple y fuerte. Limpia el estado de sesión que los usuarios frecuentemente olvidan que existe.

3.
**Usar el Almacenamiento Persistente con moderación**
   Persistir solo lo que el flujo de trabajo necesita. Tratar los archivos, claves y configuraciones persistentes como posibles vínculos entre sesiones.

4.
**Limpiar y verificar archivos**
   Tails incluye flujos de trabajo de limpieza de metadatos, pero los usuarios aún deben inspeccionar y verificar los outputs.

5.
**Usar bridges cuando importa la visibilidad local de Tor**
   Tails usando Tor puede ser visible para la red local. Los bridges abordan ese observador específico.

6.
**Respetar los límites del hardware**
   Usar hardware de confianza cuando el adversario podría afectar el firmware, los periféricos o la observación física.

### Qué no funciona como defensa primaria

- **Tails no es magia.** No puede proteger contra todos los riesgos de software, hardware, red y comportamiento.
- **La persistencia no es neutral.** Mejora la usabilidad mientras crea riesgo de vinculación y almacenamiento.
- **El ruteo Tor no limpia los archivos.** Los metadatos permanecen a menos que se manejen por separado.
- **Una sesión para muchas identidades debilita la compartimentación.** Reiniciar o usar medios separados cuando las identidades deben permanecer separadas.

## Labs prácticos

### Planificar una sesión Tails

```
Propósito:
Cuentas necesarias:
Archivos necesarios:
Almacenamiento Persistente necesario:
Bridge necesario:
Limpieza de metadatos necesaria:
Criterios de apagado:
No mezclar con:
```

El plan evita que un SO temporal se convierta en un entorno diario improvisado.

### Revisar el riesgo de persistencia

```
Elemento persistente:
Por qué es necesario:
Podría vincular identidades:
Podría exponer nombre real:
Ubicación de backup:
Plan de eliminación:
```

La persistencia debería ganarse su lugar.

### Construir un registro de movimiento de archivos

```
Archivo:
Dispositivo origen:
Destino:
Metadatos inspeccionados:
Metadatos limpiados:
Abierto fuera de Tails:
Riesgo residual:
```

El movimiento de archivos es un lugar común donde los límites de Tails se difuminan.

### Separar dos actividades

```
Actividad A:
Actividad B:
Cuentas compartidas:
Archivos compartidos:
Persistencia compartida:
Necesita reinicio entre ellas:
Necesita USB separado:
```

El resultado debería hacer explícita la vinculación de identidad.

## Ejemplos prácticos

- Un usuario arranca Tails para una sola tarea de investigación sensible y apaga después.
- Un periodista usa el Almacenamiento Persistente para claves pero mantiene las identidades de fuentes en medios Tails separados.
- Un usuario sube un documento a través de Tails pero olvida eliminar los metadatos del autor.
- Una red local ve el uso de Tor desde Tails, lo que lleva a usar bridges en un entorno de mayor riesgo.
- Un usuario hace login en cuentas personales y seudónimas en una sesión, debilitando la separación.

## Notas relacionadas

- [[qubes-compartmentalization|Qubes Compartmentalization]]
- [[whonix-gateway|Whonix Gateway]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[file-metadata-removal|File Metadata Removal]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

## Referencias

- **Docs Oficiales:** Tails documentation - https://tails.net/doc/
- **Docs Oficiales:** Tails: warnings - https://tails.net/doc/about/warnings/
- **Docs Oficiales:** Tor Browser User Manual - https://tb-manual.torproject.org/
