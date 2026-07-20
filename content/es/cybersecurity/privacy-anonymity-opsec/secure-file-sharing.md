# Secure File Sharing

## Definición

El intercambio seguro de archivos es la transferencia controlada de archivos de modo que el contenido, los metadatos, la identidad del emisor/destinatario, la vida útil del acceso y la ubicación de almacenamiento coincidan con el threat model.

## Por qué importa

Compartir un archivo no es solo un problema de transporte. El archivo puede contener metadatos. El servicio de intercambio puede retener una copia. El link de acceso puede reenviarse. El destinatario puede descargar desde una red identificadora. El emisor puede exponer su máquina si aloja el archivo directamente.

El intercambio seguro significa diseñar toda la cadena: contenido del archivo, metadatos, ruta, almacenamiento, autenticación, expiración, manejo del destinatario y eliminación.

## Cómo funciona

Usá el modelo de intercambio de 6 partes:

1.
**Preparar el archivo**
   Inspeccionar el contenido visible y los metadatos ocultos.

2.
**Elegir la ruta de transferencia**
   Decidir entre mensajero cifrado, link en la nube, OnionShare, transferencia física u otro canal controlado.

3.
**Proteger el acceso**
   Usar contraseñas, claves privadas, identidad del destinatario, links con expiración o acceso único donde sea apropiado.

4.
**Compartir los secretos por separado**
   No enviar link, contraseña y contexto a través del mismo canal débil cuando el riesgo es alto.

5.
**Controlar la vida útil**
   Detener el intercambio, expirar el link, eliminar copias en la nube y registrar la confirmación del destinatario.

6.
**Gestionar el riesgo del destinatario**
   El dispositivo, la cuenta y la red del destinatario se convierten en parte de la ruta de exposición del archivo.

Ejemplo:

```
archivo -> inspección de metadatos -> copia limpiada -> canal de intercambio -> verificación del destinatario -> acceso cerrado -> registro de eliminación/retención
```

El bug no es usar una herramienta específica de transferencia de archivos. El bug es dejar el archivo, el link, los metadatos y el comportamiento del destinatario fuera del threat model.

## Técnicas / patrones

- Limpiar metadatos antes de compartir.
- Preferir canales cifrados de extremo a extremo para archivos más pequeños cuando la identidad del destinatario es conocida.
- Usar OnionShare u onion services cuando evitar almacenamiento de terceros importa.
- Usar canales separados para link y contraseña/clave privada cuando el riesgo lo justifica.
- Establecer condiciones de expiración, descarga única o detención manual.
- Confirmar el contexto del dispositivo y la cuenta del destinatario.
- Preservar los originales por separado cuando importa la integridad de la evidencia.

## Variantes y bypasses

Usá los 7 patrones de intercambio:

### 1. Transferencia por mensajero cifrado

Bueno para destinatarios conocidos y archivos más pequeños. Los metadatos, el backup en la nube, la identidad de la cuenta y el compromiso del dispositivo aún importan.

### 2. Link de almacenamiento en la nube

Conveniente, pero el proveedor puede almacenar, escanear, registrar, retener o recibir solicitudes legales del archivo y los metadatos de acceso.

### 3. Servicio onion directo estilo OnionShare

El emisor aloja un onion service temporal desde su máquina. Esto puede evitar el almacenamiento de terceros pero depende de que el emisor permanezca en línea y comparta la dirección/clave de forma segura.

### 4. Archivo comprimido protegido por contraseña

Añade protección de contenido, pero el intercambio de contraseña, la configuración de cifrado débil, los metadatos fuera del archivo y los nombres del archivo pueden filtrarse.

### 5. Transferencia física

Evita los metadatos de transferencia de red pero introduce riesgos físicos de custodia, dispositivo, frontera, pérdida y almacenamiento.

### 6. Buzón anónimo

Permite que fuentes o destinatarios suban sin identidad de cuenta normal, pero el malware, los metadatos y el manejo operacional siguen siendo críticos.

### 7. Transferencia que preserva la evidencia

Cuando los archivos son evidencia, preservar los originales y la cadena de custodia antes de limpiar, convertir o renombrar copias.

## Impacto

- Exposición reducida de archivos sensibles a servicios de terceros.
- Menor riesgo de desanonimización por metadatos.
- Mejor control sobre quién puede acceder a un archivo y por cuánto tiempo.
- Expectativas de seguridad del lado del destinatario más claras.
- Daño de evidencia reducido por limpieza o transferencia no controlada.

## Detección y defensa

Ordenado por efectividad:

1.
**Clasificar el riesgo del archivo y del destinatario**
   La ruta de intercambio correcta depende de la sensibilidad, la identidad del destinatario, el tamaño del archivo, el riesgo legal y si el almacenamiento de terceros es aceptable.

2.
**Inspeccionar y limpiar metadatos antes de compartir copias**
   La privacidad del payload importa tanto como la privacidad del transporte. Compartir copias limpias a menos que sea necesario preservar los metadatos.

3.
**Elegir el canal basado en confianza y retención**
   Los links en la nube, los mensajeros, OnionShare y la transferencia física crean diferentes rastros de almacenamiento y metadatos.

4.
**Separar el material de acceso cuando sea necesario**
   El link, la contraseña, la clave privada y las instrucciones no siempre deberían viajar por el mismo canal.

5.
**Cerrar la ventana de intercambio**
   Detener servicios, expirar links, eliminar copias temporales y registrar qué queda almacenado dónde.

6.
**Dar instrucciones de manejo al destinatario**
   Una transferencia segura puede fallar si el destinatario abre archivos en un dispositivo monitoreado, los sincroniza con almacenamiento en la nube o reenvía el link.

### Qué no funciona como defensa primaria

- **Un link privado no es control de acceso.** Cualquiera con el link puede acceder.
- **El cifrado en tránsito no elimina los metadatos del archivo.** El archivo aún puede identificar su origen.
- **La eliminación en la nube no prueba el borrado.** Los backups, logs, clientes de sincronización y destinatarios pueden retener copias.
- **OnionShare no hace seguros a los archivos inseguros.** Cambia el hosting y el ruteo, no el contenido del archivo.
- **Los archivos comprimidos protegidos con contraseña no son suficientes si la contraseña se envía mal.** El canal de intercambio importa.

## Labs prácticos

### Construir un threat model de intercambio de archivos

```
Archivo:
Sensibilidad:
Destinatario:
Necesita anonimato:
Necesita evitar terceros:
Necesita preservar evidencia:
Metadatos limpiados:
Canal:
Secreto de acceso:
Expiración:
Instrucciones al destinatario:
```

Esto debería completarse antes de seleccionar la herramienta.

### Inspeccionar antes de transferir

```
exiftool file.ext
```

Buscar autor, GPS, timestamps, software, comentarios, miniaturas embebidas y rutas.

### Verificar la copia limpiada

```
cp file.ext file-clean.ext
exiftool -all= file-clean.ext
exiftool file-clean.ext
```

Usar una herramienta y formato apropiado para el archivo. La inspección final es la evidencia.

### Planificar la separación de link y secreto

```
Canal del link:
Canal de contraseña/clave privada:
Verificación del destinatario:
Expiración:
Riesgo de reenvío:
Respaldo si lo recibe el destinatario incorrecto:
```

No improvisar la entrega de secretos para archivos de alto riesgo.

### Registrar el cierre

```
Transferencia completa:
Destinatario confirmado:
Servicio detenido:
Copia en la nube eliminada:
Copia temporal local eliminada:
Original preservado:
Copias restantes:
```

El cierre es parte del flujo de trabajo de intercambio.

## Ejemplos prácticos

- Un periodista usa OnionShare para que una fuente descargue un archivo sin almacenamiento en la nube de terceros.
- Un equipo comparte un archivo comprimido protegido con contraseña pero envía la contraseña en el mismo hilo de email, debilitando el control.
- Un usuario limpia los metadatos de la foto antes de enviarla a través de un mensajero cifrado.
- Un link en la nube se reenvía más allá del destinatario previsto porque carece de control de acceso vinculado al destinatario.
- Un respondedor de incidentes preserva el archivo de evidencia original, luego comparte una copia redactada.

## Notas relacionadas

- [[file-metadata-removal|File Metadata Removal]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[tails-operational-model|Tails Operational Model]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[secure-deletion-and-storage-wiping|Secure Deletion and Storage Wiping]]

## Referencias

- **Docs Oficiales:** OnionShare documentation - https://docs.onionshare.org/
- **Docs Oficiales:** Tails: Removing metadata from files - https://tails.net/doc/sensitive_documents/metadata/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
