# Cloud Security Basics

## Definición

La seguridad cloud es la disciplina de proteger identidades, recursos, redes, datos, workloads, logs y operaciones del plano de control hosted en la nube.

## Por qué importa

El cloud cambia el modelo de seguridad porque la infraestructura se vuelve impulsada por APIs. Un solo permiso de identidad, regla de almacenamiento público, security group expuesto, clave filtrada o ruta de metadatos puede crear impacto amplio.

La idea central es la responsabilidad compartida: el provider asegura el cloud subyacente, mientras el cliente sigue siendo propietario de las decisiones de configuración, identidad, datos, workloads, acceso y monitoreo.

## Cómo funciona

La seguridad cloud tiene **6 planos de control**:

1. **Identidad.** Usuarios, roles, service accounts y políticas deciden quién puede hacer qué.
2. **Red.** VPCs, subredes, security groups, firewalls y rutas deciden la alcanzabilidad.
3. **Datos.** Los permisos de almacenamiento, cifrado, retención y sharing deciden la exposición.
4. **Cómputo.** Las instancias, contenedores, funciones e imágenes ejecutan workloads.
5. **Metadatos y secretos.** Los workloads a menudo reciben credenciales a través de canales de la plataforma.
6. **Logging.** Las trazas de auditoría y las detecciones deciden si los cambios riesgosos son visibles.

No hay un único payload de vulnerabilidad cloud. La mayoría de los fallos cloud son malas configuraciones del plano de control o rutas de identidad que hacen posibles acciones peligrosas.

Un ejemplo trabajado, riesgo cloud como límites combinados:

```
Recurso:
  VM lab-web-01

Identidad:
  el rol adjunto puede leer todo el almacenamiento de objetos

Red:
  SSH abierto a 0.0.0.0/0 y HTTPS público

Datos:
  la app escribe exportaciones a un bucket privado

Logging:
  logs del plano de control habilitados, eventos de datos de storage deshabilitados

Decisión:
  el riesgo inmediato no es "existe una VM"; es alcanzabilidad pública de admin más identidad amplia del workload
  más visibilidad incompleta de acceso a datos
```

La madurez en seguridad cloud viene de leer identidad, red, datos, cómputo, secretos y logs juntos.

## Técnicas / patrones

Las revisiones cloud analizan:

- estructura de cuenta/proyecto/suscripción
- identidades de administrador y workload
- IPs públicas, security groups abiertos y puertos admin expuestos
- acceso público al almacenamiento de objetos y sharing entre cuentas
- configuración de metadatos de instancia
- secretos en variables de entorno, repos, imágenes y CI/CD
- logging de auditoría, alertas y retención

## Variantes y bypasses

El riesgo cloud tiene **5 formas recurrentes**.

### 1. Identidad sobre-privilegiada

Una identidad puede realizar acciones mucho más allá de su trabajo.

### 2. Exposición pública

El almacenamiento, hosts, paneles admin o APIs son alcanzables desde internet.

### 3. Filtración de credenciales

Las claves, tokens o credenciales de rol escapan hacia código, logs, imágenes o abuso de metadatos.

### 4. Confusión de límites

Los equipos malentienden VPCs, security groups, cuentas, proyectos o la responsabilidad compartida.

### 5. Cambio invisible

Los cambios de configuración riesgosos ocurren sin logs ni alertas útiles.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso de cuenta.** El abuso de identidad puede crear nuevos usuarios, roles, claves y persistencia.
- **Exposición de datos.** El almacenamiento público o entre cuentas puede filtrar datos sensibles.
- **Compromiso de workload.** Los hosts expuestos o el acceso a metadatos pueden llevar a credenciales.
- **Movimiento lateral.** Un rol o subred puede alcanzar otros servicios.
- **Costo descontrolado.** El compromiso puede crear recursos costosos.

## Detección y defensa

Ordenado por efectividad:

1.
**Diseñá identidad con least-privilege primero.**
   Los planos de control cloud son impulsados por identidad. Los permisos estrechos reducen el blast radius de cada otro error.

2.
**Mantené la exposición pública intencional e inventariada.**
   Las IPs públicas, buckets, load balancers y puertos admin deberían tener propietarios, motivos y fechas de revisión.

3.
**Segmentá cuentas, redes y entornos.**
   Producción, dev, labs y experimentos personales no deberían compartir un límite de confianza plano.

4.
**Habilitá logs de auditoría antes de los experimentos.**
   Los logs son más útiles cuando existen antes del evento riesgoso.

5.
**Establecé presupuestos y hábitos de teardown.**
   La seguridad cloud incluye la seguridad de costos porque la creación de recursos es parte de la superficie de ataque.

### Qué no funciona como defensa primaria

- **Asumir que "gestionado por el provider" significa "asegurado por el provider".** La configuración del cliente sigue importando.
- **Usar una cuenta admin para todo.** La conveniencia se convierte en blast radius.
- **Confiar solo en IPs privadas.** SSRF, peering, VPNs y workloads comprometidos pueden cruzar límites "privados".
- **Activar logs después de un incidente.** El historial faltante no puede reconstruirse.

## Labs prácticos

Usá una cuenta sandbox personal sin acceso a producción.

### Dibujá la división de responsabilidad compartida

```
El provider es responsable de:
El cliente es responsable de:
Ambiguo/compartido:
Fuente de evidencia:
```

Aplicarlo a un servicio como almacenamiento de objetos, cómputo VM o base de datos gestionada.

### Construí un inventario de riesgo cloud

```
Identidad:
Endpoints públicos:
Almacenamiento:
Cómputo:
Secretos:
Logs:
Presupuesto:
Fecha de teardown:
```

Mantenelo aburrido y seguro en el primer lab.

### Identificá recursos públicos

```
IPs públicas:
Buckets públicos:
Nombres DNS públicos:
Puertos admin abiertos:
Propietario:
Motivo:
```

Esto convierte los conceptos cloud en evidencia de superficie de ataque.

### Construí una tarjeta de riesgo de seis planos

```
Recurso:
Riesgo de identidad:
Riesgo de red:
Riesgo de datos:
Riesgo de cómputo:
Riesgo de metadatos/secretos:
Riesgo de logging:
Próxima acción principal:
```

Usala cuando un hallazgo cloud se sienta demasiado amplio para triar.

### Separar controles del provider y del cliente

```
Control | Responsabilidad del provider | Responsabilidad del cliente | Evidencia
diseño de rol IAM | no | sí | revisión de política
acceso físico al datacenter | sí | no | docs del provider
política pública de bucket | no | sí | config de almacenamiento
```

La responsabilidad compartida solo es útil cuando se mapea a controles concretos.

## Ejemplos prácticos

- Una VM de lab expone SSH a internet sin restricción de IP.
- Un bucket público contiene backups que se pensaba eran internos.
- Un rol de CI puede crear políticas de admin.
- Una instancia comprometida lee credenciales de rol desde los metadatos.
- CloudTrail o los logs de auditoría nunca fueron habilitados en una cuenta pequeña.

## Notas relacionadas

- [[cloud-iam-boundaries]]
- [[cloud-network-boundaries]]
- [[public-cloud-storage-exposure]]
- [[cloud-metadata-security]]
- [[external-attack-surface|External Attack Surface]]

### Notas atómicas futuras sugeridas

- cloud-asset-inventory
- cloud-account-organization
- cloud-cost-security
- cloud-tagging-strategy

## Referencias

- **Fundamental:** AWS Shared Responsibility Model — https://aws.amazon.com/compliance/shared-responsibility-model/
- **Fundamental:** Google Cloud shared responsibility and shared fate — https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
- **Fundamental:** Microsoft Cloud Adoption Framework security — https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/
