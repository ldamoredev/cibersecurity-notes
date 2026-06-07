# Public Cloud Storage Exposure

## Definición

La exposición de almacenamiento cloud público es la condición en la que objetos de almacenamiento cloud (buckets S3, blobs Azure, buckets GCS) son alcanzables por principals no intencionados debido a políticas de recursos, ACLs de objetos, permisos de identidad, controles de red o prácticas de ciclo de vida incorrectamente configurados.

## Por qué importa

El almacenamiento de objetos cloud es frecuentemente donde las aplicaciones almacenan backups, exportaciones, logs, archivos de usuario y datos en proceso. La diferencia entre un bucket privado y uno público es con frecuencia una sola configuración, y la exposición puede ocurrir en múltiples capas que no son obvias desde el panel de control.

Un bucket "privado" puede tener objetos individuales con ACLs públicas. Un bucket sin acceso público puede compartirse ampliamente entre cuentas. Un bucket privado puede tener una URL pre-firmada con un TTL largo comprometida en el historial de git.

## Cómo funciona

El acceso al almacenamiento cloud tiene **5 puntos de decisión**:

1. **Política de recurso.** ¿La política del bucket/container permite acceso público o entre cuentas?
2. **ACLs de objetos.** ¿Los objetos individuales tienen ACLs que otorgan acceso público independientemente de la política del bucket?
3. **Permisos de identidad.** ¿Qué identidades (usuarios, roles, service accounts) tienen permiso para listar, leer o escribir?
4. **Controles de red/servicio.** ¿El acceso está restringido por VPC endpoints, restricciones de IP o condiciones de política?
5. **Ciclo de vida y ownership.** ¿Hay datos obsoletos, URLs pre-firmadas activas o cambios de ownership?

La exposición puede ocurrir en cualquier capa independientemente de las otras.

Un ejemplo trabajado, exposición en capas:

```
Bucket:
  backup-exports-prod

Política del bucket:
  privada, sin acceso público

ACL de objeto:
  el script de backup establece public-read en cada archivo .csv

Resultado:
  la URL directa del objeto es alcanzable públicamente
  a pesar de que el bucket en sí "es privado"

Decisión:
  deshabilitar ACLs de objetos, usar la configuración Block Public Access del bucket,
  revisar los scripts de backup para comportamiento de ACL
```

La exposición del almacenamiento de objetos frecuentemente vive en la intersección entre la política del bucket y las ACLs de objetos.

## Técnicas / patrones

Las revisiones analizan:

- configuración de Block Public Access por bucket y por cuenta
- ACLs de objetos en buckets que se asume son privados
- políticas de bucket que permiten principals con wildcard o cualquier principal autenticado
- sharing entre cuentas con condiciones externas débiles
- URLs pre-firmadas con TTLs largos en repos o logs
- backups, logs y exportaciones almacenados sin control de ciclo de vida
- buckets que sirven contenido estático con más permiso del necesario

## Variantes y bypasses

La exposición de almacenamiento cloud tiene **5 formas comunes**.

### 1. Bucket con acceso público de lectura

La política del bucket otorga `s3:GetObject` o equivalente a `*`.

### 2. Objeto público dentro de almacenamiento privado

ACLs de objetos individuales otorgan acceso público independientemente de la política del bucket.

### 3. Sharing entre cuentas sobre-amplio

Una política de bucket permite cualquier identidad autenticada en cualquier cuenta del provider.

### 4. URL pre-firmada con TTL largo filtrada

Una URL pre-firmada comprometida da acceso temporal sin credenciales de identidad.

### 5. Exposición de backup y log

Los backups, logs de acceso y exportaciones se almacenan en un bucket más permisivo que los datos de la aplicación.

## Impacto

Ordenado aproximadamente por severidad:

- **Exfiltración de datos.** Los buckets públicos de lectura pueden ser descargados completamente.
- **Exposición de datos de usuarios.** Los archivos de usuario, PII, exportaciones financieras o médicas pueden quedar expuestos.
- **Exposición de credenciales.** Los archivos de configuración, backups y logs pueden contener secretos o claves.
- **Daño a la reputación.** Los buckets mal configurados frecuentemente son descubiertos por escáneres y divulgados públicamente.
- **Escritura en almacenamiento.** Los buckets sobre-permisivos pueden ser objetivos de hosting malicioso o sobrescritura.

## Detección y defensa

Ordenado por efectividad:

1.
**Habilitá Block Public Access a nivel de cuenta y de bucket.**
   Esto previene que políticas de bucket o ACLs de objetos otorguen acceso público.

2.
**Deshabilitar ACLs de objetos donde sea posible.**
   Las ACLs de objetos crean un segundo mecanismo de exposición que puede divergir de la política del bucket.

3.
**Auditá regularmente las políticas de bucket.**
   Las políticas con principals `*`, condiciones débiles o acceso entre cuentas sin restricciones deberían ser revisadas.

4.
**Controlá los TTLs de las URLs pre-firmadas.**
   Las URLs pre-firmadas deberían tener TTLs cortos e inventariarse cuando se generan para propósitos de auditoría.

5.
**Aplicá retención, vencimiento y propiedad a los buckets.**
   Los datos obsoletos sin control de ciclo de vida se convierten en pasivo de exposición.

### Qué no funciona como defensa primaria

- **Confiar en que el nombre del bucket sea oscuro.** Los nombres de buckets se filtran en logs, URLs y referencias de configuración.
- **Verificar solo la política del bucket sin ACLs de objetos.** Los dos mecanismos de acceso operan independientemente.
- **Generar URLs pre-firmadas de larga duración para conveniencia.** Los TTLs largos no caducan antes que los incidentes.
- **Asumir que el acceso autenticado significa acceso mínimo.** El "cualquier usuario autenticado" en el ecosistema del provider puede incluir millones de cuentas.

## Labs prácticos

Usá una cuenta sandbox con un bucket de prueba.

### Auditá el estado de acceso público del bucket

```bash
# AWS
aws s3api get-bucket-acl --bucket NOMBRE_BUCKET
aws s3api get-bucket-policy --bucket NOMBRE_BUCKET
aws s3api get-public-access-block --bucket NOMBRE_BUCKET
```

### Revisá los ACLs de objetos

```bash
# Listar objetos con ACLs públicas
aws s3api list-objects --bucket NOMBRE_BUCKET \
  --query 'Contents[].Key' --output text | while read key; do
  acl=$(aws s3api get-object-acl --bucket NOMBRE_BUCKET --key "$key" 2>/dev/null)
  echo "$key: $(echo $acl | python3 -c 'import json,sys; d=json.load(sys.stdin); print([g for g in d.get("Grants",[]) if "AllUsers" in str(g)])')"
done
```

### Construí una tarjeta de riesgo de bucket

```
Bucket | Block Public Access | Política | ACLs de objetos | Sharing entre cuentas | Contiene | Propietario | Revisión
```

### Revisá URLs pre-firmadas activas

```
Generadas dónde:
TTL:
Alcanzables desde repos o logs:
Proceso de revocación:
```

Las URLs pre-firmadas de larga duración que existen en repos o logs deberían ser revocadas.

### Buscá buckets con datos sensibles inadvertidamente expuestos

```
Tipo de datos: backup / log / exportación / PII / credenciales
Nombre del bucket:
Política de acceso:
¿Alcanzable públicamente?:
Proceso de remediación:
```

Los buckets con datos sensibles merecen auditorías de acceso más frecuentes.

## Ejemplos prácticos

- Un bucket de backup se crea con acceso de lectura público para "facilitar la recuperación".
- Un script de exportación establece ACLs public-read en cada archivo generado.
- Un bucket de staging es compartido con cualquier cuenta AWS autenticada.
- Una URL pre-firmada con expiración de un año se almacena en el historial de git.
- Los logs de acceso se almacenan en el mismo bucket que los datos de la aplicación con permisos más amplios.

## Notas relacionadas

- [[cloud-security-basics]]
- [[cloud-iam-boundaries]]
- [[cloud-logging-and-detection]]
- [[exposed-storage|Exposed Storage]]
- [[sensitive-data-exposure|Sensitive Data Exposure]]

### Notas atómicas futuras sugeridas

- audit-public-cloud-storage
- cloud-data-classification
- s3-policy-hardening
- cloud-lifecycle-management

## Referencias

- **Docs Oficiales:** AWS S3 blocking public access — https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- **Docs Oficiales:** Google Cloud storage access control — https://cloud.google.com/storage/docs/access-control
- **Mitigación:** AWS presigned URL security — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
