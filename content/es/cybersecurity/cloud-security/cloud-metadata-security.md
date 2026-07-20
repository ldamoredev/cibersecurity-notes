# Cloud Metadata Security

## Definición

La seguridad de cloud metadata es la disciplina de controlar el acceso al servicio de metadatos de instancia (IMDS) que los providers cloud exponen a las VMs en ejecución, y de entender la cadena de riesgos SSRF → metadatos → credenciales de API cloud.

## Por qué importa

La mayoría de los providers cloud exponen un endpoint HTTP no ruteable (`169.254.169.254` o equivalente) accesible desde dentro de cada instancia. Este endpoint sirve credenciales de rol de instancia de corta duración, datos de user-data y configuración de la plataforma.

Si una aplicación en el host puede hacer solicitudes HTTP arbitrarias (SSRF, redirect abierto, fetch del lado del servidor), puede acceder al endpoint de metadatos y recuperar credenciales cloud de corta duración del rol de instancia adjunto.

La cadena: SSRF → endpoint de metadatos → credenciales de rol de instancia → APIs cloud con todos los permisos del rol.

## Cómo funciona

El riesgo de seguridad de metadatos cloud tiene **5 etapas**:

1. **Exposición SSRF.** La aplicación puede ser forzada a realizar una solicitud HTTP hacia una IP o hostname arbitrario.
2. **Alcanzabilidad de metadatos.** El endpoint de metadatos es alcanzable desde la instancia sin autenticación adicional (IMDSv1) o con un token de sesión (IMDSv2).
3. **Recuperación de credenciales.** La respuesta incluye `AccessKeyId`, `SecretAccessKey`, `Token` y `Expiration`.
4. **Uso de credenciales.** Las credenciales son válidas para el período de vencimiento y tienen el scope del rol adjunto.
5. **Impacto basado en rol.** El blast radius depende de qué puede hacer el rol de instancia.

La diferencia entre IMDSv1 e IMDSv2 es que IMDSv2 requiere un token de sesión obtenido a través de un PUT con TTL. Esto hace que SSRF simple sea insuficiente porque el atacante debe poder enviar una solicitud PUT con un header específico. Sin embargo, algunos frameworks de cliente hacen seguimiento de redirecciones o construyen solicitudes de manera que los headers PUT se incluyen.

Un ejemplo trabajado, cadena SSRF a credencial cloud:

```
Vulnerabilidad:
  parámetro ?url= en la aplicación de procesamiento de imágenes

Solicitud del atacante:
  GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

Respuesta (si IMDSv1):
  nombre del rol adjunto

Siguiente solicitud:
  GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/app-role

Respuesta:
  {"AccessKeyId": "ASIA...", "SecretAccessKey": "...", "Token": "...", "Expiration": "..."}

Impacto:
  cualquier acción permitida al rol app dentro del tiempo de expiración
```

El endpoint de metadatos es la versión cloud del "escalación de privilegios del host".

## Técnicas / patrones

Las revisiones analizan:

- si IMDSv1 está habilitado (sin requerir token de sesión)
- vulnerabilidades SSRF en aplicaciones corriendo en instancias cloud
- configuración del hop limit del endpoint de metadatos
- si el acceso al endpoint de metadatos está restringido a nivel del OS/contenedor
- rutas de workload-to-metadata en pods de contenedor y funciones
- el scope de permisos del rol de instancia en relación al riesgo de SSRF

## Variantes y bypasses

El riesgo de metadatos cloud tiene **4 formas comunes**.

### 1. IMDSv1 no autenticado

Sin header de token requerido, cualquier SSRF puede recuperar credenciales directamente.

### 2. SSRF a metadatos

La aplicación tiene SSRF clásico o puede ser manipulada para realizar fetches a IPs internas.

### 3. Contenedor-a-nodo

Los contenedores en un nodo compartido pueden alcanzar el endpoint de metadatos del nodo host y obtener credenciales del rol del nodo.

### 4. Workload identity sobre-privilegiada

Incluso con IMDSv2 y SSRF mitigado, un rol de instancia con permisos amplios amplifica cualquier compromiso.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de credenciales cloud.** Las credenciales recuperadas de metadatos pueden llamar APIs cloud con el scope del rol.
- **Escalación de privilegios cloud.** El rol puede tener permisos para crear usuarios, asumir roles más fuertes o modificar IAM.
- **Exfiltración de datos.** El rol puede tener acceso a S3, bases de datos u otros almacenes de datos.
- **Movimiento lateral.** Las credenciales del rol pueden ser usadas desde fuera del host original.
- **Persistencia.** El atacante puede crear claves de acceso de larga duración usando credenciales temporales del rol.

## Detección y defensa

Ordenado por efectividad:

1.
**Habilitá IMDSv2 (token requerido) en todas las instancias.**
   IMDSv2 requiere un token de sesión obtenido por un PUT con TTL, lo que hace SSRF simple insuficiente.

2.
**Restringí el scope de los roles de instancia.**
   Los roles de instancia con least privilege limitan el blast radius si se recuperan credenciales de metadatos.

3.
**Usá restricciones de red a nivel del OS para aislar el acceso a metadatos.**
   Las reglas de iptables o eBPF pueden restringir qué UIDs/procesos pueden acceder al endpoint.

4.
**Identificá y remediá SSRF en aplicaciones cloud-hosted.**
   Las vulnerabilidades SSRF en hosts cloud tienen un impacto más alto porque los metadatos están disponibles.

5.
**Loguiá y alertá sobre acceso inusual al endpoint de metadatos.**
   El acceso desde procesos inesperados, usuarios o patrones de tiempo puede indicar explotación.

### Qué no funciona como defensa primaria

- **Confiar solo en la restricción del endpoint de metadatos.** El acceso aún puede ser posible a través de SSRF sofisticado.
- **Ignorar IMDSv1 legacy.** Las imágenes viejas o las configuraciones de lanzamiento pueden seguir habilitando IMDSv1.
- **Asumir que los pods de contenedor están aislados del host.** Los contenedores sin restricción de red pueden alcanzar el endpoint del nodo.
- **Amplios permisos de rol de instancia para "conveniencia de desarrollo".** Los roles de instancia amplios en producción son pre-escalación esperando ser explotada.

## Labs prácticos

Usá una cuenta sandbox con una VM dedicada a pruebas de seguridad.

### Verificá el modo IMDS

```bash
# Comprobar si IMDSv1 está habilitado (desde dentro de la instancia)
curl -s --max-time 2 http://169.254.169.254/latest/meta-data/

# IMDSv2 correcto requiere un token PUT primero
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/
```

### Revisá el scope del rol de instancia

```
Rol de instancia:
Políticas adjuntas:
Acciones permitidas:
Recursos alcanzables:
¿Amplio? Sí/No:
Ruta de reducción:
```

El acceso más amplio del rol directamente amplifica el impacto de SSRF-to-metadata.

### Buscá SSRF en la aplicación

```
Parámetros que aceptan URLs:
Parámetros que aceptan IPs:
Redirecciones abiertas:
Fetches del lado del servidor (webhooks, importaciones, previews):
```

Cualquier ruta de fetch del lado del servidor en un host cloud debería ser revisada contra el acceso a metadatos.

### Probá las restricciones de red a metadatos

```bash
# Verificar si los contenedores pueden alcanzar el endpoint del nodo
# (ejecutar desde dentro de un contenedor)
curl -s --max-time 2 http://169.254.169.254/ && echo "alcanzable" || echo "bloqueado"
```

El acceso alcanzable desde contenedores debería motivar restricciones de red o política de pod.

### Construí una tarjeta de riesgo de metadatos

```
Host:
Versión IMDS:
Rol adjunto:
Scope del rol:
Rutas SSRF conocidas:
Restricciones de red:
Logging habilitado:
Nivel de riesgo:
```

Usala para priorizar la remediación de IMDSv1 y scope de rol en fleets de instancias grandes.

## Ejemplos prácticos

- Un proxy de imagen recupera el contenido de cualquier URL proporcionada por el usuario, incluyendo `169.254.169.254`.
- Un endpoint de webhooks realiza fetches del lado del servidor hacia URL enviadas por el usuario sin validación.
- Un pod de Kubernetes alcanza las credenciales de rol del nodo a través del endpoint de metadatos.
- Las credenciales del rol son exfiltradas y usadas desde fuera del provider cloud.
- IMDSv1 permanece habilitado en instancias viejas que no fueron actualizadas cuando se implementó IMDSv2.

## Notas relacionadas

- [[cloud-iam-boundaries]]
- [[cloud-network-boundaries]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-logging-and-detection]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[server-side-request-forgery|Server-Side Request Forgery]]

### Notas atómicas futuras sugeridas

- imds-hardening
- ssrf-to-cloud-credentials
- container-metadata-isolation
- workload-identity-vs-instance-roles

## Referencias

- **Docs Oficiales:** AWS IMDSv2 — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Docs Oficiales:** Google Cloud metadata server — https://cloud.google.com/compute/docs/metadata/overview
- **Investigación / Deep Dive:** AWS blog on IMDSv2 — https://aws.amazon.com/blogs/security/defense-in-depth-open-firewalls-reverse-proxies-ssrf-vulnerabilities-ec2-instance-metadata-service/
