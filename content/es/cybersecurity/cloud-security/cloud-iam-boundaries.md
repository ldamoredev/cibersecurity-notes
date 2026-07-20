# Cloud IAM Boundaries

## Definición

Los Cloud IAM Boundaries son los controles de identidad, rol, política, confianza y organización que deciden qué principals cloud pueden realizar qué acciones sobre qué recursos.

## Por qué importa

Los entornos cloud son controlados por APIs, y las APIs son controladas por identidad. Los usuarios, service accounts, roles de instancia o trusts entre cuentas sobre-privilegiados pueden convertir una pequeña cabeza de playa en control total de la cuenta.

El modelo mental importante no es "quién inició sesión". Es "qué principal puede llamar a qué API bajo qué condiciones".

## Cómo funciona

Cloud IAM tiene **5 inputs de decisión**:

1. **Principal.** Usuario, rol, grupo, service account, workload identity o identidad externa.
2. **Acción.** La operación API que se solicita.
3. **Recurso.** El objeto, servicio, cuenta, proyecto, suscripción o scope.
4. **Condición.** Contexto como MFA, IP, tags, tiempo, dispositivo u organización.
5. **Ruta de confianza.** Relaciones de assumption, impersonación, federación o delegación.

El bug generalmente no es una sola línea de política de forma aislada. Es el grafo efectivo de permisos creado por identidad más confianza más políticas de recursos.

Un ejemplo trabajado, ruta de rol de aspecto inofensivo:

```
Principal:
  ci-deploy-role

Permisos directos:
  actualizar código de función, pasar rol app-runtime-role

Confianza:
  el provider CI puede asumir ci-deploy-role

Escalación oculta:
  si ci-deploy-role puede pasar un runtime role más privilegiado, el deployment se convierte en expansión de privilegios

Decisión:
  revisar rutas iam:PassRole / impersonación de service account, no solo las políticas admin obvias
```

La madurez IAM es entender en qué puede convertirse un principal, no solo qué puede hacer directamente.

## Técnicas / patrones

Las revisiones analizan:

- uso de root/admin y estado de MFA
- access keys de larga duración
- acciones y recursos con wildcards
- role assumption e impersonación de service accounts
- identidades externas y trusts entre cuentas
- workload identities adjuntas al cómputo
- identidades no utilizadas y permisos obsoletos

## Variantes y bypasses

Los fallos IAM tienen **5 formas comunes**.

### 1. Sobre-permiso directo

Una identidad tiene más acciones de las que requiere su trabajo.

### 2. Ruta de escalación de privilegios

Un principal puede modificar políticas, pasar roles, crear claves o asumir identidades más fuertes.

### 3. Confianza confundida

El acceso entre cuentas, externo o federado confía en la parte o condición incorrecta.

### 4. Abuso de rol de workload

Una VM, contenedor o función comprometidos pueden usar su identidad adjunta.

### 5. Identidad obsoleta

Usuarios viejos, service accounts y claves permanecen válidos después de que su propósito terminó.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de cuenta.** Los permisos equivalentes a admin pueden persistir, exfiltrar o destruir recursos.
- **Acceso a datos.** IAM otorga lecturas directas a almacenamiento, bases de datos, logs y secretos.
- **Persistencia.** Los atacantes pueden crear claves, usuarios, roles o backdoors de política.
- **Movimiento lateral.** Las relaciones de confianza conectan cuentas, proyectos y workloads.
- **Evasión de auditoría.** Algunos permisos pueden deshabilitar o alterar el logging.

## Detección y defensa

Ordenado por efectividad:

1.
**Diseñá least privilege alrededor de tareas.**
   Los permisos más pequeños reducen tanto el blast radius accidental como el malicioso.

2.
**Eliminá credenciales de larga duración donde sea posible.**
   Las credenciales de rol de corta duración y la federación son más fáciles de revocar y monitorear.

3.
**Requerí MFA y condiciones fuertes para acciones privilegiadas.**
   Las condiciones hacen que las decisiones de identidad dependan del contexto, no solo de la posesión de una credencial.

4.
**Analizá permisos efectivos y rutas de escalación.**
   La revisión de políticas debe incluir confianza, políticas de recursos y comportamiento de role-passing.

5.
**Revisá identidades y claves no utilizadas.**
   El acceso obsoleto es riesgo silencioso.

### Qué no funciona como defensa primaria

- **Nombrar un rol `readonly`.** La política efectiva importa, no la etiqueta.
- **Un rol admin para toda la automatización.** Destruye el control del blast radius.
- **Eliminar usuarios pero dejar claves o roles.** El acceso cloud puede sobrevivir a través de otros principals.
- **Solo revisión manual de políticas enormes.** Los permisos efectivos necesitan herramientas y consultas.

## Labs prácticos

Usá una cuenta sandbox y verificaciones de solo lectura donde sea posible.

### Construí una tabla de inventario IAM

```
Principal | Tipo | Propósito | Nivel de privilegio | Último uso | Tipo de credencial | Propietario
```

El objetivo es ver el sprawl de identidad.

### Revisá permisos con wildcards

```
Política:
Acción con wildcard:
Recurso con wildcard:
Condición:
Motivo de negocio:
Scope más seguro:
```

Los wildcards necesitan justificación explícita.

### Mapeá una ruta de confianza

```
El principal A puede asumir/impersonar:
Rol/service account objetivo:
Condiciones:
Permisos resultantes:
Riesgo de escalación:
```

Las rutas de confianza son frecuentemente donde IAM se vuelve sorprendente.

### Revisá role-passing e impersonación

```
Principal | Puede pasar/impersonar | A servicio | Permisos objetivo | ¿Justificado? | Condición
```

El role-passing es una de las verificaciones de límite de privilegio cloud más importantes.

### Construí una cola de credenciales obsoletas

```
principal | credencial key/service-account | último uso | propietario | rotar/eliminar | riesgo
```

Las credenciales no utilizadas deberían convertirse en candidatas a eliminación, no en excepciones permanentes.

## Ejemplos prácticos

- Un rol de CI puede adjuntar políticas de administrador.
- Un rol de VM puede leer todos los buckets de almacenamiento.
- Un usuario contratista mantiene acceso después del offboarding.
- Una clave de service account está almacenada en un repositorio.
- Un trust entre cuentas carece de una condición externa fuerte.

## Notas relacionadas

- [[cloud-security-basics]]
- [[cloud-metadata-security]]
- [[cloud-secrets-management]]
- [[cloud-logging-and-detection]]
- [[broken-function-level-authorization|Broken Function-Level Authorization]]

### Notas atómicas futuras sugeridas

- cloud-iam-policy-analysis
- cloud-service-account-keys
- cloud-role-assumption
- cloud-privilege-escalation-paths

## Referencias

- **Docs Oficiales:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Docs Oficiales:** Google Cloud IAM best practices — https://cloud.google.com/iam/docs/using-iam-securely
- **Docs Oficiales:** Microsoft Entra security operations for privileged accounts — https://learn.microsoft.com/en-us/entra/architecture/security-operations-privileged-accounts
