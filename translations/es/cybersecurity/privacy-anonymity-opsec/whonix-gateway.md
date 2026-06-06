# Whonix Gateway

## Definición

Whonix Gateway es el componente de ruteo Tor de Whonix. Está diseñado para separar el ruteo de red de Tor de las aplicaciones del usuario, de modo que el tráfico de la aplicación desde la workstation sea forzado a través de la ruta Tor del gateway.

## Por qué importa

Muchas fallas de anonimato ocurren porque las aplicaciones se filtran alrededor del proxy o VPN previsto. Whonix aborda esto dividiendo el entorno en un modelo gateway y workstation: las aplicaciones se ejecutan en una VM, mientras que el ruteo Tor ocurre en otra.

Esto es más fuerte que pedirle a cada aplicación que se comporte correctamente, pero aún no resuelve la identidad de cuenta, los metadatos de archivos, el mal uso del browser, el compromiso del host ni el comportamiento del usuario.

## Cómo funciona

Usá el modelo Whonix de 4 partes:

1.
**VM Gateway**
   Whonix Gateway se conecta a Tor y actúa como la ruta de red.

2.
**VM Workstation**
   Las aplicaciones del usuario se ejecutan en una workstation separada que rutea a través del gateway.

3.
**Aislamiento de red**
   La workstation no debería tener acceso directo a internet fuera de la ruta del gateway.

4.
**Dependencia del host**
   El SO host o el hypervisor aún importan. Un host comprometido puede socavar la privacidad a nivel de VM.

Boceto:

```
aplicación -> Whonix Workstation -> Whonix Gateway -> red Tor -> destino
```

El bug no es usar un gateway. El bug es asumir que el ruteo del gateway arregla la identidad de la aplicación y el OPSEC de archivos.

## Técnicas / patrones

- Mantener el tráfico de la workstation ruteado solo a través del gateway.
- Usar Whonix con Qubes cuando se necesita compartimentación más fuerte.
- Evitar instalar software innecesario en workstations de anonimato.
- Mantener el comportamiento del browser cerca de las expectativas de Tor Browser.
- Separar identidades en workstations separadas donde sea necesario.
- Tratar el host/hypervisor como parte del threat model.
- Usar bridges donde importa la visibilidad local de Tor.

## Variantes y bypasses

Usá las 6 clases de límites de Whonix:

### 1. División gateway/workstation

El límite de diseño principal separa el ruteo de las aplicaciones. Esto reduce las conexiones directas accidentales de las aplicaciones.

### 2. Compromiso del host

El host puede observar o manipular las VMs si está comprometido. Whonix no es una defensa contra todos los atacantes a nivel de host.

### 3. Identidad a nivel de aplicación

Las aplicaciones aún pueden revelar identidad a través de logins, telemetría, archivos y comportamiento. El ruteo no puede eliminar esa capa.

### 4. Browser fingerprinting

Usar browsers no estándar o añadir extensiones puede hacer que el usuario se destaque incluso cuando el tráfico rutea a través de Tor.

### 5. Compartimentación multi-workstation

Las workstations separadas pueden aislar identidades y tareas, especialmente con Qubes-Whonix. La separación solo funciona si el movimiento de datos está controlado.

### 6. Visibilidad local de Tor

La red local puede ver el uso de Tor a menos que se configuren bridges o transportes.

## Impacto

- Mejor contención contra fugas de red directas de aplicaciones.
- Mejor separación entre ruteo y aplicaciones del usuario.
- Integración útil con la compartimentación de Qubes.
- Riesgo continuo de compromiso del host, login de cuenta, archivos y comportamiento.
- Mayor complejidad operacional que solo Tor Browser o Tails.

## Detección y defensa

Ordenado por efectividad:

1.
**Preservar la ruta solo-gateway**
   La workstation no debería tener una ruta de red directa alternativa. La arquitectura importa solo si el tráfico no puede evitarla.

2.
**Separar identidades en workstations separadas**
   Las diferentes identidades no deberían compartir archivos, estado del browser ni datos de aplicación cuando importa la no-vinculabilidad.

3.
**Usar Qubes-Whonix para compartimentos más fuertes**
   Qubes añade un modelo de compartimento más amplio alrededor del ruteo Whonix, que puede reducir el radio de explosión cuando se usa cuidadosamente.

4.
**Mantener la seguridad del host en el alcance**
   Parchear el host, limitar la actividad riesgosa del host y entender que el aislamiento de VM depende del host y el hypervisor.

5.
**Mantener la disciplina de browser y archivos**
   Usar el comportamiento de Tor Browser, evitar logins identificadores e inspeccionar archivos. El ruteo del gateway no puede arreglar las fugas en la capa de payload.

### Qué no funciona como defensa primaria

- **El ruteo del gateway no es eliminación de identidad.** Las cuentas y el comportamiento aún identifican a los usuarios.
- **Whonix no es protección contra compromiso del host.** El host sigue siendo un punto crítico de confianza.
- **Las múltiples workstations no son separación si los archivos se comparten libremente.** Las transferencias pueden reconectar identidades.
- **El ruteo Tor no limpia metadatos.** La inspección y limpieza de archivos siguen siendo tareas separadas.

## Labs prácticos

### Mapear los límites de Whonix

```
SO Host:
Hypervisor:
Gateway:
Workstation:
Ruta de red:
¿Posible ruta directa a internet?:
Cuentas usadas:
Archivos movidos hacia/desde:
```

Esto hace explícito el límite de confianza.

### Construir un plan de workstation de identidad

```
Identidad/tarea:
Workstation:
Gateway:
Carpetas compartidas:
Política de portapapeles:
Archivos importados:
Archivos exportados:
Cambios del browser:
```

El plan evita que todas las identidades colapsen en una sola workstation.

### Revisar supuestos de bypass

```
Aplicación:
Necesita red:
¿Puede alcanzar solo el gateway?:
¿Usa proxy del sistema?:
¿Tiene telemetría?:
¿Almacena datos de cuenta?:
Riesgo de metadatos de archivos:
```

Esto separa la contención de red del comportamiento de la aplicación.

### Comparar Whonix con VPN

```
Pregunta                         VPN              Whonix
Confianza en proveedor único:
Ruteo Tor:
Resistencia a fuga directa de app:
Fingerprint del browser resuelto:
Login de cuenta resuelto:
Compromiso del host resuelto:
```

La tabla mantiene a Whonix en el lugar correcto del threat model.

## Ejemplos prácticos

- Un usuario rutea una workstation de investigación a través de Whonix Gateway para prevenir conexiones directas de apps.
- Un usuario de Qubes ejecuta workstations Whonix separadas para identidades separadas.
- Una app que no es browser envía telemetría a través de Tor pero aún incluye identificadores de cuenta.
- Un host comprometido observa la actividad de la VM a pesar del ruteo Whonix.
- Un usuario copia archivos entre workstations, vinculando identidades que de otro modo estaban separadas.

## Notas relacionadas

- [[qubes-compartmentalization|Qubes Compartmentalization]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[tor-bridges-and-pluggable-transports|Tor Bridges and Pluggable Transports]]
- [[file-metadata-removal|File Metadata Removal]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

## Referencias

- **Docs Oficiales:** Whonix documentation - https://www.whonix.org/wiki/Documentation
- **Docs Oficiales:** Whonix Gateway - https://www.whonix.org/wiki/Whonix-Gateway
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
