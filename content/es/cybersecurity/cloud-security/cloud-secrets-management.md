# Cloud Secrets Management

## Definición

El cloud secrets management es la disciplina de crear, almacenar, acceder, rotar y retirar credenciales, claves de API, certificados y parámetros de configuración sensibles en entornos cloud.

## Por qué importa

Los secretos son credenciales de acceso. Una clave de API, contraseña de base de datos, clave privada o token filtrado puede dar a un atacante permisos equivalentes a los del servicio que los creó.

Los secretos cloud falllan de manera diferente a las contraseñas de usuario: se copian en archivos de configuración, variables de entorno, historial de shell, imágenes de contenedor, repos, CI/CD pipelines, logs y endpoints de metadatos.

## Cómo funciona

Los secretos cloud tienen **5 etapas de ciclo de vida**:

1. **Creación.** El secreto existe con un scope de acceso específico, vencimiento y propietario.
2. **Almacenamiento.** El secreto vive en un secret store, no en código, archivos de config ni variables de entorno del sistema.
3. **Acceso.** El secreto se recupera en tiempo de ejecución a través de una llamada API autenticada o una ruta de identidad del workload.
4. **Rotación.** El secreto se reemplaza periódicamente o después de un evento de compromiso.
5. **Retiro.** El secreto se revoca y elimina cuando el workload que lo necesita deja de existir.

El patrón de fallo más común no es ninguna etapa de forma aislada. Es el secreto hardcodeado que llega al almacenamiento y nunca se rota.

Un ejemplo trabajado, ruta de filtración de secreto:

```
Secreto:
  cadena de conexión a base de datos de producción

Almacenamiento:
  variable de entorno en Docker Compose, commiteada al repo

Acceso:
  cualquier desarrollador con acceso de lectura al repo

Rotación:
  ninguna — es difícil rotar porque está en el repo

Retiro:
  nunca — el workload usa la credencial original de tres años atrás

Decisión:
  mover a secret store + inyección de runtime + política de rotación + auditoría de acceso
```

La seguridad de secretos en cloud es principalmente diseño del ciclo de vida, no solo cifrado en reposo.

## Técnicas / patrones

Las revisiones analizan:

- secretos hardcodeados en archivos de configuración, código fuente o IaC
- secretos en variables de entorno expuestos por endpoints de salud
- imágenes de contenedor con secretos baked
- pipelines CI/CD con secretos en variables de texto plano
- service account keys o access keys de larga duración
- secretos sin rotación, vencimiento ni auditoría de acceso
- logs que contienen valores de secretos

## Variantes y bypasses

Los secretos cloud fallan de **5 formas comunes**.

### 1. Secreto hardcodeado

La credencial vive directamente en el código o en archivos de config trackeados.

### 2. Secreto baked en imagen

La clave o credencial se incluye en una imagen de contenedor o snapshot de VM.

### 3. Acceso sobre-amplio

Un secreto otorga acceso a más recursos de los que necesita el workload que lo usa.

### 4. Secreto logueado

El valor del secreto aparece en la salida de la aplicación, solicitudes HTTP, trazas de error o acceso a metadatos.

### 5. Secreto sin rotar

Una credencial de larga duración persiste mucho después de que su scope útil terminó.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de cuenta cloud.** Las claves de acceso pueden crear backdoors, eliminar controles o exfiltrar datos.
- **Compromiso de base de datos.** Las cadenas de conexión otorgan acceso a datos de aplicación.
- **Compromiso de pipelines.** Los secretos de CI/CD pueden llevar a código de producción.
- **Movimiento lateral.** Los secretos compartidos conectan workloads y cuentas.
- **Filtración sigilosa.** Los secretos viejos sin rotación son difíciles de detectar como comprometidos.

## Detección y defensa

Ordenado por efectividad:

1.
**Usá workload identity en lugar de credenciales estáticas donde sea posible.**
   Los roles de instancia, service accounts e identidades de pod/función obtienen credenciales de corta duración sin secretos estáticos.

2.
**Almacená secretos en secret managers del provider.**
   AWS Secrets Manager, Google Secret Manager, Azure Key Vault y HashiCorp Vault son diseñados para este ciclo de vida.

3.
**Rotá los secretos de forma regular y después de eventos de compromiso.**
   La rotación limita la ventana de exposición de secretos comprometidos no detectados.

4.
**Auditá el acceso a secretos.**
   Los logs de acceso a secretos deberían generar alertas para comportamientos inusuales.

5.
**Escaneá repos, imágenes y pipelines en busca de secretos.**
   La detección temprana previene la promoción de secretos filtrados a producción.

### Qué no funciona como defensa primaria

- **Ofuscar secretos en código.** La codificación base64, los comentarios o el renombramiento no son seguridad.
- **Confiar en que el repo es privado.** El acceso al repo no es equivalente al acceso necesario al secreto.
- **Crear nuevos secretos sin eliminar los viejos.** Los secretos obsoletos siguen siendo válidos.
- **Solo cifrar en reposo.** El cifrado en reposo no previene que los secretos se filtren en tiempo de ejecución.

## Labs prácticos

Usá una cuenta sandbox.

### Construí un inventario de secretos

```
Secreto | Servicio | Propietario | Tipo | Dónde almacenado | Último uso | Rotación
```

El objetivo es detectar secretos de larga duración sin auditoría.

### Comparar workload identity vs credenciales estáticas

```
Workload:
¿Workload identity disponible?:
Secret store actual:
Tipo de credencial actual:
Lifetime de credencial:
Ruta de migración:
```

El movimiento hacia workload identity reduce el inventario de secretos que necesitan rotación.

### Auditá las variables de entorno del workload

```
# Enumerá variables que parezcan credenciales
env | grep -iE 'key|secret|password|token|credential|api' | cut -d= -f1
```

El objetivo es detectar dónde los secretos viven como variables de entorno en lugar de recuperación en tiempo de ejecución.

### Revisá el historial de logs para secretos filtrados

```
Patrón de secreto:
Fuente de log:
Rango de tiempo:
Ocurrencias:
Acción: rotar inmediatamente si se encuentra
```

Los secretos logueados deberían tratarse como comprometidos.

### Construí una tarjeta de rotación de secretos

```
secreto | owner | última rotación | siguiente rotación | método de rotación | riesgo si no rota
```

La rotación es solo efectiva si está rastreada y ejecutada.

## Ejemplos prácticos

- Una clave de API está commiteada en el historial de git.
- Una imagen Docker incluye una variable de entorno con una contraseña de base de datos.
- Un pipeline CI imprime variables de entorno en la salida del build.
- Un endpoint de salud de la aplicación devuelve variables de entorno en JSON.
- Una service account key tiene tres años y nunca fue rotada.

## Notas relacionadas

- [[cloud-iam-boundaries]]
- [[cloud-metadata-security]]
- [[cloud-lab-infrastructure]]
- [[cloud-logging-and-detection]]
- [[secrets-management|Secrets Management]]

### Notas atómicas futuras sugeridas

- cloud-kms-boundaries
- workload-identity-federation
- secret-scanning-in-ci
- secret-manager-integration-patterns

## Referencias

- **Docs Oficiales:** AWS Secrets Manager — https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- **Docs Oficiales:** Google Cloud Secret Manager — https://cloud.google.com/secret-manager/docs/overview
- **Docs Oficiales:** Azure Key Vault — https://learn.microsoft.com/en-us/azure/key-vault/general/overview
- **Investigación / Deep Dive:** GitGuardian State of Secrets Sprawl — https://www.gitguardian.com/state-of-secrets-sprawl
