# Cron and Timer Abuse

## Definición

El abuso de cron y timers ocurre cuando un usuario con pocos privilegios puede influir sobre una tarea programada que corre con privilegios más altos.

Esto incluye cron jobs clásicos, timers de systemd, scripts escribibles, directorios escribibles, valores de PATH inseguros y workflows de mantenimiento ejecutados por root.

## Por qué importa

Las tareas programadas son cruces de privilegios silenciosos. Suelen correr como root, repetirse automáticamente y ejecutar scripts que no fueron revisados como código de producción.

Para defensores, revisar la ejecución programada detecta una clase grande de rutas prevenibles de escalada local.

## Cómo funciona

Hacé 5 preguntas:

1. **Quién lo corre:** root, una cuenta de servicio o un usuario?
2. **Qué corre:** binario, shell script, intérprete o command string?
3. **Desde dónde:** ruta absoluta, ruta relativa, wildcard o directorio escribible?
4. **Qué input:** archivos, directorios, entorno, expansión de glob, configuración o logs?
5. **Quién puede escribir:** un usuario bajo puede modificar algo en la cadena de ejecución?

## Técnicas / patrones

- Inspeccioná `/etc/crontab`, `/etc/cron.*`, crontabs de usuario y timers de systemd.
- Revisá permisos sobre scripts y directorios padre.
- Buscá expansión de wildcards y rutas relativas de comandos.
- Identificá jobs que procesan archivos escribibles por usuarios.
- Verificá el comportamiento de tareas programadas en un lab sin esperar ciclos de producción.

### Ejemplo trabajado: cadena de backup escribible

```text
Schedule: root runs /opt/backup/run.sh every 5 minutes
Script owner: root:backup-ops
Script mode: group-writable
User context: low user belongs to backup-ops
Boundary question: can the low user change root-executed code?
Minimal proof: in lab, write a harmless timestamp marker to /tmp
Fix: root-owned immutable deployment path and separate writable data directory
```

Los hallazgos de tareas programadas deberían trazar la cadena completa desde el schedule hasta la identidad y el componente escribible.

## Variantes y bypasses

### 1. Script escribible

Un cron job de root ejecuta un script escribible por un usuario con pocos privilegios.

### 2. Directorio escribible

El script está protegido, pero su directorio padre o archivos incluidos son escribibles.

### 3. PATH o comando relativo

El job programado llama a un programa por nombre y confía en un valor de PATH.

### 4. Expansión de wildcard

El job procesa archivos desde un directorio escribible de una forma que cambia el comportamiento del comando.

### 5. Cadena de timer systemd

Un timer dispara un service cuyo unit file, environment file o script es escribible.

## Impacto

- Ejecución demorada de comandos como root.
- Modificación persistente a nivel root.
- Robo de credenciales desde scripts de backup o mantenimiento.
- Manipulación de servicios mediante workflows programados de restart o cleanup.
- Compromiso recurrente difícil de depurar.

## Detección y defensa

- **Usá rutas absolutas en tareas programadas.** Eliminá ambigüedad de la ejecución privilegiada.
- **Protegé scripts y directorios padre.** Toda la cadena de ejecución tiene que ser propiedad de root o estar fuertemente controlada.
- **Evitá procesar directorios escribibles por atacantes como root.** Usá staging seguro, ownership estricto y manejo defensivo de globs.
- **Inventariá timers y cron jobs.** La ejecución programada debería ser parte de la revisión de baseline.
- **Logueá actividad de jobs programados.** Fallas y cambios inesperados de archivos deberían ser observables.

### Qué no funciona como defensa primaria

- **Revisar solo `/etc/crontab`.** También importan crontabs de usuario, `/etc/cron.*`, timers de systemd y schedulers de apps.
- **Proteger el script pero no el directorio.** El acceso de escritura al directorio padre todavía puede ser peligroso.
- **Asumir que los jobs infrecuentes son seguros.** Un job diario de root sigue siendo un límite de root.

## Labs prácticos

Usá una VM propia con un job de prueba deliberadamente seguro.

### Enumerar tareas programadas

```bash
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.* 2>/dev/null
systemctl list-timers --all 2>/dev/null
```

Registrá quién es dueño de cada job y qué ejecuta.

### Revisar permisos de script y directorio

```bash
ls -la /path/to/script
namei -l /path/to/script
```

`namei -l` muestra todos los directorios en la ruta.

### Armar una tabla de cadena de ejecución

```text
Schedule:
Runs as:
Command:
Script owner:
Directory owners:
User-writable inputs:
Risk:
Fix:
```

Esto vuelve visible toda la cadena.

### Verificar remediación

```bash
sudo chown root:root /path/to/script
sudo chmod 755 /path/to/script
namei -l /path/to/script
```

En sistemas reales, usá control de cambios antes de modificar jobs programados.

## Ejemplos prácticos

- Un cron job de root corre `/opt/backup.sh`, y `/opt` es escribible por un grupo de soporte.
- Un script de cleanup procesa archivos desde `/tmp` con comportamiento inseguro de wildcard.
- Un timer de systemd dispara un service que lee un environment file escribible por un usuario de app.
- Un script llama a `tar` sin ruta absoluta bajo un PATH modificado.
- Un job de backup expone credenciales en logs legibles por usuarios bajos.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]
- [[path-hijacking|PATH Hijacking]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linpeas-workflow|LinPEAS Workflow]]

### Futuras notas atómicas sugeridas

- systemd-service-permissions
- cron-wildcard-abuse
- writable-service-files
- scheduled-job-hardening

## Referencias

- **Documentación oficial:** crontab file format — https://man7.org/linux/man-pages/man5/crontab.5.html
- **Documentación oficial:** systemd timers — https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- **Documentación oficial:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
