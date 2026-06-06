# Secure Deletion and Storage Wiping

## Definición

El borrado seguro y el wipeo de almacenamiento son las prácticas de eliminar datos de modo que no puedan recuperarse fácilmente desde capas lógicas, del sistema de archivos o de almacenamiento, sujeto a las limitaciones del medio y el threat model.

## Por qué importa

Eliminar un archivo generalmente solo elimina un puntero, no los datos subyacentes. Los backups, snapshots, journals, wear leveling, sincronización en la nube, cachés del dispositivo y herramientas forenses pueden preservar copias o trazas mucho después de que el usuario crea que el archivo desapareció.

## Cómo funciona

Usá el modelo de eliminación de 5 capas:

1.
**Eliminación lógica**
   El archivo se elimina de la vista del sistema de archivos.

2.
**Limpieza de metadatos y journal**
   Las estructuras del sistema de archivos, logs y journals pueden aún retener trazas.

3.
**Comportamiento del medio**
   Los SSDs, el almacenamiento flash y los sistemas copy-on-write pueden preservar bloques de maneras que la eliminación normal no controla.

4.
**Copias y backups**
   Los servicios de sincronización, backups en la nube, snapshots y copias de destinatarios pueden sobrevivir al original.

5.
**Coincidencia con el threat model**
   El método correcto de wipeo depende de si el medio es magnético, basado en flash, cifrado, reutilizado o simplemente saliendo de tu control.

El bug no es eliminar. El bug es asumir que eliminar significa lo mismo en todos los medios de almacenamiento.

## Técnicas / patrones

- Clasificar el medio de almacenamiento antes de decidir cómo eliminar.
- Preferir cifrado de disco completo para que la disposición sea más segura que intentar rastrear cada bloque.
- Eliminar o expirar copias en backups, carpetas de sincronización y servicios en la nube.
- Verificar si el dispositivo soporta borrado seguro o funciones de wipeo integradas.
- Separar la limpieza lógica de la destrucción física.
- Mantener un registro de auditoría cuando los datos deben retenerse por evidencia o cumplimiento.

## Variantes y bypasses

Usá los 6 casos de almacenamiento:

### 1. Eliminación del sistema de archivos

Funciona para limpieza visible por el usuario pero deja oportunidades de recuperación dependiendo del medio y el estado del sistema.

### 2. Comando de borrado seguro

Puede ser efectivo cuando el dispositivo lo soporta y se ejecuta correctamente.

### 3. Destrucción de clave de cifrado

Si el disco está fuertemente cifrado, destruir las claves puede ser más práctico que sobreescribir cada bloque.

### 4. Eliminación de snapshots y backups

Los snapshots y backups en la nube necesitan flujos de trabajo de eliminación separados.

### 5. SSD y medios flash

El wear leveling y el comportamiento del controlador hacen que las suposiciones simples de sobreescritura sean poco confiables.

### 6. Destrucción física

A veces la única opción aceptable para medios retirados con alta sensibilidad.

## Impacto

- Recuperabilidad reducida de datos sensibles.
- Menor riesgo de dispositivos desechados o sistemas compartidos.
- Mejor control sobre remanentes de backup y nube.
- Decisiones de disposición más realistas para SSDs y medios flash.
- Evitar la falsa confianza de la eliminación simple de archivos.

## Detección y defensa

Ordenado por efectividad:

1.
**Cifrar primero**
   El cifrado fuerte reduce la necesidad de confiar en el comportamiento de sobreescritura después de la disposición.

2.
**Usar borrado apropiado para el medio**
   Seguir la guía de saneamiento estilo NIST y el soporte del proveedor donde esté disponible.

3.
**Eliminar copias en todos los lugares**
   Los backups, carpetas de sincronización, snapshots, exportaciones y copias de destinatarios importan todos.

4.
**Verificar la ruta de wipeo**
   Confirmar que el método previsto realmente se aplica al medio en uso.

5.
**Usar destrucción física para la mayor sensibilidad**
   Cuando el threat model es suficientemente alto, la destrucción puede ser más confiable que el saneamiento.

### Qué no funciona como defensa primaria

- **Vaciar la papelera no es borrado seguro.**
- **Sobreescribir una vez no es universalmente suficiente.**
- **Eliminar de un dispositivo no elimina las copias en la nube.**
- **El cifrado sin gestión de claves no resuelve la disposición por sí solo.**

## Labs prácticos

### Clasificar el medio

```
Almacenamiento:
HDD / SSD / flash / nube / backup / snapshot:
Cifrado:
Compartido con otros:
Datos sensibles presentes:
Método de wipeo soportado:
```

El medio determina la estrategia de eliminación.

### Mapear copias

```
Original:
Caché local:
Backup:
Sincronización en la nube:
Copia del destinatario:
Exportación:
¿Wipear cada una? sí/no
```

La eliminación debe cubrir todas las copias.

### Decidir la ruta de disposición

```
Sensibilidad:
Tiempo disponible:
Tipo de medio:
Cifrado en su lugar:
Necesita retener evidencia:
Wipear / destruir / retener:
```

Esto convierte la disposición en una decisión documentada.

### Verificar el resultado

```
Método usado:
Método de verificación:
Recuperabilidad restante:
Remanentes en la nube:
Backups eliminados:
```

Si no podés verificar, no sabés el resultado de la eliminación.

## Ejemplos prácticos

- Un laptop se retira después de la destrucción de claves en un disco fuertemente cifrado.
- Una carpeta en la nube se vacía, pero el snapshot de backup aún contiene los archivos.
- Un SSD se sanea según la guía del proveedor en lugar de sobreescritura ciega.
- Una foto del teléfono se elimina localmente pero persiste en backups sincronizados.
- Un archivo sensible se destruye físicamente porque el threat model es alto.

## Notas relacionadas

- [[file-metadata-removal|File Metadata Removal]]
- [[secure-file-sharing|Secure File Sharing]]
- [[tails-operational-model|Tails Operational Model]]
- [[end-to-end-encryption|End-to-End Encryption]]

## Referencias

- **Docs Oficiales:** NIST SP 800-88 Rev. 1 - https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final
- **Docs Oficiales:** Tails: Secure Deletion - https://tails.net/doc/encryption_and_privacy/secure_deletion/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
