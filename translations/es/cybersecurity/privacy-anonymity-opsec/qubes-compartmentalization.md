# Qubes Compartmentalization

## Definición

La compartimentación en Qubes es la práctica de separar actividades en máquinas virtuales aisladas, llamadas qubes, para que el compromiso o la fuga en un compartimento no exponga automáticamente a todas las demás actividades en la computadora.

## Por qué importa

Muchas fallas de privacidad son fallas del endpoint. Un perfil de browser, un editor de documentos, una app de chat, un gestor de contraseñas y una cuenta personal todo se ejecutan en el mismo sistema diario y comparten silenciosamente archivos, portapapeles, red, credenciales y contexto del dispositivo.

Qubes cambia el modelo operativo. En lugar de confiar en un solo entorno de escritorio, el usuario diseña compartimentos para trabajo, uso personal, archivos riesgosos, actividad anónima, datos de vault y tareas desechables. Esto es poderoso, pero requiere planificación y disciplina.

## Cómo funciona

Usá el modelo de 5 límites:

1.
**Qubes separados**
   Cada compartimento tiene su propio sistema de archivos y espacio de procesos.

2.
**Las templates proveen la base de software**
   Los qubes basados en templates comparten una base gestionada mientras mantienen los datos del usuario separados.

3.
**Los qubes de red median la conectividad**
   Los qubes de app pueden usar diferentes rutas de red, incluyendo sin red, red normal, VPN o Tor vía Whonix.

4.
**La política controla la interacción**
   La copia, transferencia de archivos, dispositivos y servicios inter-qube están mediados en lugar de ser automáticos.

5.
**Dom0 sigue siendo especial**
   El dominio administrativo es muy sensible y no debería usarse para trabajo ordinario.

Boceto:

```
qube personal    -> red normal
qube trabajo     -> red de trabajo
qube investigación -> desechable / restringida
qube vault       -> sin red
qube anon        -> ruta Whonix/Tor
dom0             -> solo administración
```

El bug no es tener muchos compartimentos. El bug es mover datos entre ellos hasta que los límites ya no signifiquen nada.

## Técnicas / patrones

- Definir compartimentos por identidad y riesgo, no solo por aplicación.
- Usar qubes desechables para documentos no confiables y navegación puntual.
- Mantener secretos en qubes sin red o fuertemente restringidos.
- Evitar el copy/paste rutinario entre identidades.
- Usar diferentes qubes de red para diferentes modelos de confianza.
- Tratar la asignación de USB y dispositivos como de alto riesgo.
- Mantener dom0 limpio y sin uso.

## Variantes y bypasses

Usá los 6 patrones de compartimento:

### 1. Compartimentos de identidad

Las identidades personal, laboral, seudónima y anónima no deberían compartir estado del browser, archivos ni credenciales.

### 2. Compartimentos de riesgo

Los documentos no confiables, enlaces desconocidos e investigación riesgosa pertenecen a qubes desechables o restringidos.

### 3. Compartimentos de red

Algunos qubes usan red normal, algunos usan VPN, algunos usan Tor/Whonix y algunos no usan red. La ruta de red es parte de la definición del compartimento.

### 4. Compartimentos de secretos

Las bases de datos de contraseñas, claves, material de firma y documentos sensibles pueden vivir en qubes con acceso de red limitado o nulo.

### 5. Compartimentos de dispositivos

USB, cámara, micrófono y otros dispositivos deberían asignarse cuidadosamente porque los dispositivos pueden tender puentes entre compartimentos.

### 6. Bypass del flujo de trabajo humano

Los usuarios pueden derrotar los compartimentos copiando archivos, capturas de pantalla, texto, credenciales o links del browser entre límites sin pensar.

## Impacto

- Radio de explosión reducido por malware o compromiso del browser.
- Mejor separación de identidad cuando los compartimentos se diseñan y respetan.
- Manejo más seguro de archivos no confiables a través de desechables.
- Mayor complejidad y carga operacional.
- Nuevos modos de falla por mala política, movimiento descuidado de archivos y asignación de dispositivos.

## Detección y defensa

Ordenado por efectividad:

1.
**Diseñar compartimentos antes del uso diario**
   Un modelo de compartimento debería describir identidades, sensibilidad de los datos, ruta de red y transferencias permitidas. Los qubes ad hoc se convierten en desorden, no en seguridad.

2.
**Usar desechables para input no confiable**
   Los qubes desechables reducen la persistencia y hacen que los documentos o links riesgosos tengan menos capacidad de contaminar compartimentos de identidad de larga vida.

3.
**Limitar el movimiento de datos entre qubes**
   Cada copia, pegado, movimiento de archivo y captura de pantalla es un posible cruce de límite. Hacer las transferencias intencionales.

4.
**Mantener secretos sin red donde sea práctico**
   Los qubes sin red son útiles para secretos de alto valor porque muchos ataques requieren comunicación saliente.

5.
**Restringir los dispositivos**
   La asignación de USB y periféricos debe ser explícita. El compromiso de dispositivos puede socavar las suposiciones de aislamiento de VM.

6.
**Auditar la deriva de compartimentos**
   Verificar periódicamente si los qubes aún coinciden con sus roles de identidad, riesgo y red previstos.

### Qué no funciona como defensa primaria

- **Muchos qubes no garantizan separación.** Los malos hábitos de transferencia pueden reconectar todo.
- **Qubes no arregla la correlación de cuentas.** Hacer login en la misma cuenta desde dos compartimentos los vincula.
- **El aislamiento de red no es saneamiento de archivos.** Los archivos aún llevan metadatos y riesgos de contenido activo.
- **Dom0 no es un espacio de trabajo.** Tratar dom0 como un escritorio normal socava la arquitectura.

## Labs prácticos

### Borrador de un mapa de compartimentos

```
Nombre del qube:
Identidad/propósito:
Ruta de red:
Secretos almacenados:
Archivos entrantes permitidos:
Archivos salientes permitidos:
Portapapeles permitido:
Desechable necesario:
```

Esto convierte los compartimentos en una arquitectura deliberada.

### Revisar las transferencias entre límites

```
Transferencia:
Del qube:
Al qube:
Tipo de dato:
Riesgo de metadatos:
Riesgo de vínculo de identidad:
Permitido por política:
Alternativa:
```

El registro de transferencias detecta la erosión de límites.

### Identificar candidatos a secretos sin red

```
Secreto:
Ubicación actual:
Necesita internet:
Necesita portapapeles:
Método de backup:
Candidato a qube sin red:
```

Los secretos que no necesitan internet no deberían vivir casualmente en compartimentos orientados a internet.

### Construir un flujo de trabajo desechable

```
Input no confiable:
Qube desechable usado:
Red habilitada:
Output necesario:
Paso de saneamiento:
Qube de larga vida tocado:
```

El objetivo es manejar input riesgoso sin contaminar los compartimentos de identidad.

## Ejemplos prácticos

- Un usuario abre PDFs desconocidos en qubes desechables antes de mover el output saneado a otro lugar.
- Un qube de trabajo y un qube personal usan browsers, archivos y rutas de red separados.
- Un qube vault almacena bases de datos de contraseñas sin acceso directo a internet.
- Un usuario copia texto de investigación anónima a un qube personal, vinculando contextos.
- Un dispositivo USB se asigna solo a un qube dedicado porque los periféricos son riesgosos.

## Notas relacionadas

- [[whonix-gateway|Whonix Gateway]]
- [[tails-operational-model|Tails Operational Model]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[file-metadata-removal|File Metadata Removal]]
- [[secrets-management|Secrets Management]]

## Referencias

- **Docs Oficiales:** Qubes OS documentation - https://doc.qubes-os.org/en/latest/
- **Docs Oficiales:** Qubes OS architecture - https://doc.qubes-os.org/en/latest/developer/system/architecture.html
- **Threat Model:** Qubes OS security design goals - https://doc.qubes-os.org/en/latest/developer/system/security-design-goals.html
