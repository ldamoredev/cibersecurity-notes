# Cloud Lab Infrastructure

## Definición

La infraestructura de lab cloud es un entorno cloud deliberadamente aislado, con presupuesto limitado y descartable para aprender, testear y construir ejercicios de seguridad.

## Por qué importa

Los labs cloud son útiles porque permiten practicar hosting real, SSH, DNS, TLS, almacenamiento, IAM y logging. También son riesgosos porque los errores pueden exponer servicios, filtrar credenciales o generar costos.

La mentalidad del lab seguro es: aislar primero, otorgar least privilege, loguear temprano, controlar el presupuesto con rigor y hacer teardown intencionalmente.

## Cómo funciona

Un lab cloud seguro tiene **6 barreras de seguridad**:

1. **Cuenta/proyecto/suscripción separada.** Los labs no deberían tocar activos críticos de producción o personales.
2. **Presupuesto y alertas.** Los límites de gasto y notificaciones existen antes de crear recursos.
3. **Identidad con least-privilege.** El trabajo diario de lab evita root o global admin.
4. **Exposición de red mínima.** Solo los puertos requeridos son alcanzables, preferentemente desde IPs conocidas.
5. **Línea base de logging.** Los logs de auditoría existen antes de los experimentos.
6. **Plan de teardown.** Cada recurso tiene un propietario y fecha de eliminación.

El bug en muchos labs no es el ejercicio vulnerable. Es el entorno cloud no controlado a su alrededor.

Un ejemplo trabajado, límite seguro del lab:

```
Objetivo:
  practicar SSH + HTTPS + DNS en una VM

Sandbox:
  cuenta separada, alerta de presupuesto con bajo gasto, sin peering a producción

Identidad:
  el usuario diario puede crear una VM y un registro DNS, no administrar IAM ampliamente

Red:
  SSH limitado a la IP actual del hogar, HTTPS público

Teardown:
  VM, disco, IP estática, registro DNS, par de claves y renovación de cert todos listados

Decisión:
  el lab es aceptable porque los límites de costo, identidad, exposición y limpieza son explícitos
```

Los labs cloud deberían diseñarse como sistemas de producción temporales con un blast radius más pequeño.

## Técnicas / patrones

Construí labs alrededor de:

- un provider y una región a la vez
- una cuenta/proyecto sandbox con alertas de facturación
- recursos etiquetados para limpieza
- comandos de inventario de solo lectura antes de cambios
- claves SSH, no contraseñas
- reglas explícitas de security groups/firewall
- snapshots y buckets tratados como sensibles

## Variantes y bypasses

Los labs cloud fallan de **4 formas comunes**.

### 1. Lab de cuenta compartida

Los experimentos corren en la misma cuenta que los workloads reales.

### 2. Lab público por defecto

Las VMs, buckets o dashboards son alcanzables desde internet sin revisión.

### 3. Lab sin control de costos

Los recursos siguen corriendo después del ejercicio.

### 4. Lab de secret-sprawl

Las claves se copian en notas, repos, historial de shell o imágenes.

## Impacto

Ordenado aproximadamente por severidad:

- **Exposición de credenciales.** Las claves de lab pueden convertirse en acceso real a la cuenta.
- **Exposición inesperada a internet.** Los servicios públicos pueden ser indexados o atacados.
- **Picos de costos.** El cómputo, ancho de banda, almacenamiento y snapshots pueden persistir.
- **Malos hábitos.** Los patrones de lab inseguros se transfieren a producción.

## Detección y defensa

Ordenado por efectividad:

1.
**Usá un límite sandbox dedicado.**
   La separación previene que los errores de lab se conviertan en incidentes de producción.

2.
**Creá alertas de presupuesto antes del cómputo.**
   Los controles de costos son preventivos solo cuando existen antes de crear recursos.

3.
**Usá tags y checklists de teardown.**
   La limpieza es más fácil cuando cada recurso lleva metadatos de propietario, propósito y vencimiento.

4.
**Restringí el acceso entrante por defecto.**
   SSH, paneles admin, bases de datos y dashboards no deberían ser alcanzables mundialmente a menos que el lab lo requiera.

5.
**Almacená secretos en secret stores del provider o password managers locales.**
   La conveniencia del lab no debería normalizar claves en texto plano en archivos.

### Qué no funciona como defensa primaria

- **Confiar en el marketing del free tier.** Los tiers gratuitos tienen límites y excepciones.
- **Depender de la memoria para limpiar.** Los recursos persisten más que la atención.
- **Usar credenciales root por conveniencia.** El acceso root/admin hace cada error más grande.
- **Publicar IPs y claves de lab en notas.** Las notas de Obsidian no son un secret store.

## Labs prácticos

Usá solo una cuenta sandbox.

### Creá un preflight del lab

```
Provider:
Cuenta/proyecto:
Alerta de presupuesto:
Región:
Identidad de admin:
Identidad diaria:
Logging habilitado:
Fecha de teardown:
```

Hacé esto antes de crear cómputo.

### Etiquetá los recursos

```
owner=ldamore
purpose=cloud-security-lab
expires=2026-05-06
environment=lab
```

Los tags hacen posible la limpieza y la revisión de costos.

### Revisión de teardown

```
Instancias:
Volúmenes:
Snapshots:
Buckets:
IPs elásticas/estáticas:
Registros DNS:
Secretos:
Logs retenidos:
```

Ejecutá esto al final de cada lab.

### Creá un checklist de kill-switch de costos

```
Alerta de presupuesto configurada:
Quotas de cómputo verificadas:
Auto-scaling deshabilitado o limitado:
Inventario de IPs estáticas:
Snapshots/volúmenes revisados:
Recordatorio de calendario de teardown:
```

La seguridad de costos es un control de seguridad en labs cloud descartables.

### Revisá los permisos de identidad del lab

```
Acción necesaria | Permiso otorgado | ¿Más amplio de lo necesario? | Alternativa más segura
crear VM         | compute admin    | sí                          | rol VM acotado
editar DNS       | DNS zone admin   | aceptable                   | hosted zone limitada
```

Los usuarios del lab no deberían normalizar permisos de admin amplios.

## Ejemplos prácticos

- Una VM olvidada sigue facturando durante un mes.
- Una IP estática permanece asignada después de eliminar la instancia.
- Un bucket de lab se vuelve público durante una prueba y no se revierte.
- Un par de claves se copia en una nota markdown.
- Las alertas de presupuesto atrapan un bucle accidental de recursos.

## Notas relacionadas

- [[cloud-security-basics]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-logging-and-detection]]
- [[cloud-secrets-management]]
- [[secrets-management|Secrets Management]]

### Notas atómicas futuras sugeridas

- build-safe-cloud-lab
- cloud-cost-security
- cloud-tagging-strategy
- cloud-account-organization

## Referencias

- **Docs Oficiales:** AWS Free Tier — https://aws.amazon.com/free/
- **Docs Oficiales:** AWS Budgets — https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- **Docs Oficiales:** AWS IAM security best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
