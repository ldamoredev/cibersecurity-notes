# Cloud Logging and Detection

## Definición

El cloud logging and detection es la disciplina de habilitar, centralizar, retener y accionar los logs de auditoría cloud para detectar acceso no autorizado, cambios de configuración riesgosos e incidentes en curso en entornos cloud.

## Por qué importa

Los entornos cloud son configurados a través de APIs. Las APIs crean logs. Sin logs, los cambios de configuración riesgosos, el acceso no autorizado y el movimiento lateral son invisibles hasta después de que ocurre daño.

Los logs de auditoría cloud son frecuentemente la única evidencia de qué API fue llamada, por qué identity, desde dónde y con qué resultado. Esto los hace fundamentales tanto para la respuesta a incidentes como para la detección proactiva.

## Cómo funciona

La detección cloud tiene **5 capas**:

1. **Logs del plano de control/auditoría.** Cada llamada API al plano de gestión: CreateInstance, AttachPolicy, DeleteBucket, etc.
2. **Logs de acceso a datos.** Acceso a objetos de almacenamiento, registros de base de datos, lectura de secretos.
3. **Logs de red y workload.** VPC flow logs, logs de aplicación, eventos del OS del host.
4. **Reglas de detección.** Alertas que se disparan sobre patrones: acceso no autorizado, escalación de privilegios, creación masiva de recursos.
5. **Retención protegida.** Los logs deberían estar almacenados donde un atacante no pueda modificarlos o eliminarlos.

La ausencia de cualquier capa crea un punto ciego. Los atacantes sofisticados intentan deshabilitar o alterar los logs como uno de sus primeros pasos después del compromiso inicial.

Un ejemplo trabajado, detección de escalación de privilegios IAM:

```
Evento:
  iam:AttachUserPolicy llamada por access key AKIA...

Context:
  el access key pertenece a ci-deploy-user
  la política adjunta es AdministratorAccess
  la llamada ocurrió a las 03:47 UTC desde una IP no habitual

Log source:
  CloudTrail Management Events

Detección:
  alerta: iam:Attach*Policy por identidad no-admin

Acción:
  revocar credencial, revisar recursos creados desde el timestamp, evaluar blast radius
```

Los logs son solo útiles si son consultados, monitoreados o alertados activamente.

## Técnicas / patrones

Las revisiones analizan:

- CloudTrail / Cloud Audit Logs / Azure Activity Log: ¿habilitados en todas las regiones?
- logs de acceso a datos: ¿habilitados para almacenamiento, bases de datos, secretos?
- destino de logs: ¿pueden ser eliminados o modificados por la identidad comprometida?
- retención de logs: ¿cuánto historial está disponible para la investigación?
- alertas: ¿qué eventos disparan notificaciones?
- integraciones SIEM: ¿los logs están centralizados o solo disponibles por servicio?
- gaps de cobertura: ¿qué acciones cloud no están logueadas?

## Variantes y bypasses

Los logs cloud fallan de **5 formas comunes**.

### 1. Punto ciego del plano de control

Los management events no están habilitados, creando invisibilidad total para cambios de configuración.

### 2. Punto ciego del plano de datos

Los eventos de acceso a datos para almacenamiento, bases de datos o secretos no están habilitados.

### 3. Logs alterables

Los logs viven en el mismo scope de permisos que el workload comprometido, permitiendo la supresión o alteración.

### 4. Alert fatigue

Las reglas de detección producen tantos falsos positivos que las alertas reales son ignoradas o atrasadas.

### 5. Sin ruta de respuesta

Los logs y alertas existen pero no hay un proceso documentado de triaje, escalación y respuesta.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso no detectado.** Sin logs, el atacante puede moverse lateralmente y persistir sin ser detectado.
- **Imposibilidad de respuesta.** Sin evidencia, no es posible determinar el scope del compromiso.
- **Oportunidad de evasión.** Los logs alterables o ausentes dan ventaja al atacante.
- **Exposición prolongada.** El tiempo medio de permanencia aumenta cuando la detección es tardía o ausente.

## Detección y defensa

Ordenado por efectividad:

1.
**Habilitá los logs del plano de control antes de los experimentos.**
   CloudTrail Management Events, GCP Admin Activity Logs y Azure Activity Log deberían habilitarse antes de crear recursos.

2.
**Enviá logs a un destino protegido.**
   El bucket S3, el proyecto GCS o el storage account que recibe los logs debería tener acceso de escritura restringido y acceso de eliminación bloqueado.

3.
**Habilitá logs de acceso a datos para recursos sensibles.**
   Los eventos de acceso a datos de S3, GCS, Azure Blob, Secrets Manager y bases de datos deben habilitarse por separado.

4.
**Definí alertas para eventos de alto riesgo.**
   El root login, las modificaciones de políticas IAM, la creación de nuevos usuarios de acceso programático y los cambios de configuración de seguridad deberían disparar notificaciones inmediatas.

5.
**Revisá los logs periódicamente, no solo después de incidentes.**
   Las revisiones regulares identifican patrones anómalos antes de que se conviertan en incidentes confirmados.

### Qué no funciona como defensa primaria

- **Habilitar logs pero no revisarlos.** Los logs no examinados no son defensas.
- **Almacenar logs en el mismo bucket que el workload comprometido puede modificar.** La integridad de los logs requiere acceso separado.
- **Alertas sin respuesta documentada.** Una alerta que no tiene un proceso de respuesta es teatro de seguridad.
- **Solo logs de plano de control sin logs de datos.** Los accesos a datos sensibles pueden ser invisibles sin los logs de datos correctos.

## Labs prácticos

Usá una cuenta sandbox.

### Verificá el estado de habilitación de logs

```bash
# AWS CloudTrail
aws cloudtrail describe-trails
aws cloudtrail get-trail-status --name NOMBRE_TRAIL

# Verificar si los management events están habilitados
aws cloudtrail get-event-selectors --trail-name NOMBRE_TRAIL
```

### Consultá los logs de CloudTrail para un evento específico

```bash
# Buscar eventos de iam:CreateUser en las últimas 24h
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateUser \
  --start-time "$(date -u -d '24 hours ago' '+%Y-%m-%dT%H:%M:%S')" \
  --query 'Events[*].{Time:EventTime,User:Username,Source:EventSource,IP:SourceIPAddress}'
```

### Construí una tabla de cobertura de logs

```
Servicio | Tipo de log | Estado | Destino | Retención | Alertas | Revisión
CloudTrail | Management | habilitado | S3 protegido | 90 días | sí | 2026-05-01
S3 data access | Data | deshabilitado | — | — | no | pendiente
```

### Revisá el destino de logs por alterabilidad

```
Bucket/storage de logs:
¿Puede ser eliminado por la identidad comprometida?:
¿S3 Object Lock o WORM?:
Retención de log:
¿Cross-account replication habilitado?:
```

### Creá una lista de alertas de alta prioridad

```
Evento | Riesgo | Alerta configurada | Canal | Propietario
iam:CreateUser | compromiso de cuenta | sí | PagerDuty | equipo-seguridad
s3:DeleteBucket | pérdida de datos | no | — | pendiente
```

Las alertas de alta prioridad deberían existir antes del primer evento riesgoso, no después.

## Ejemplos prácticos

- CloudTrail está deshabilitado en regiones secundarias donde los atacantes crean recursos.
- Los logs de acceso a datos de S3 no están habilitados; la exfiltración de datos es invisible.
- El bucket de logs puede ser eliminado por la misma identidad que podría comprometerse.
- Las alertas de IAM generan cientos de notificaciones por día, creando fatiga.
- Un incidente requiere dos semanas de investigación porque los logs solo tienen retención de siete días.

## Notas relacionadas

- [[cloud-security-basics]]
- [[cloud-iam-boundaries]]
- [[cloud-metadata-security]]
- [[cloud-network-boundaries]]
- [[cloud-secrets-management]]

### Notas atómicas futuras sugeridas

- cloud-logging-baseline
- cloudtrail-analysis
- cloud-siem-integration
- cloud-alert-tuning

## Referencias

- **Docs Oficiales:** AWS CloudTrail — https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- **Docs Oficiales:** Google Cloud Audit Logs — https://cloud.google.com/logging/docs/audit
- **Docs Oficiales:** Microsoft Azure Monitor activity log — https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/activity-log
- **Mitigación:** CIS AWS Foundations Benchmark — https://www.cisecurity.org/benchmark/amazon_web_services
