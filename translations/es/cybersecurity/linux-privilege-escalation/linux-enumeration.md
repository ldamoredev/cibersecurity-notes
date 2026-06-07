# Linux Enumeration

## Definición

Linux enumeration es la recolección estructurada de hechos locales del host que pueden explicar límites de privilegios, malas configuraciones, credenciales y rutas de escalada.

Es la primera habilidad real en Linux privilege escalation porque cada acción posterior depende de la calidad de la evidencia.

## Por qué importa

Una mala enumeración crea adivinanza ruidosa. Una buena enumeración reduce el host a pocas preguntas plausibles: quién soy, qué puedo correr, qué puedo escribir, qué corre como root, qué secretos existen y qué difiere de una baseline con hardening.

Para defensores, la enumeración enseña qué puede aprender del host un usuario con pocos privilegios.

## Cómo funciona

Usá 7 buckets de evidencia:

1. **Identidad:** usuario, grupos, uid/gid, shells, home directories.
2. **Sistema:** OS, kernel, packages, arquitectura, hostname, pistas de virtualización.
3. **Privilegios:** sudo, SUID/SGID, capabilities, grupos privilegiados.
4. **Superficies escribibles:** archivos, directorios, scripts, service units, targets de cron.
5. **Procesos y servicios:** procesos root, puertos locales, cuentas de service, timers.
6. **Secretos:** claves, configs, history, backups, tokens, variables de entorno.
7. **Contexto de red:** interfaces, rutas, servicios local-only, alcance de metadata cloud.

## Técnicas / patrones

- Empezá con comandos read-only de bajo riesgo.
- Preservá output de comandos con timestamps e identidad del host.
- Separá recolección de hechos de testing de exploit.
- Priorizá cambios locales inusuales por sobre archivos estándar del sistema.
- Compará hallazgos automatizados contra checks manuales.

### Ejemplo trabajado: una pista de enumeración se convierte en un test

```
Observed fact: user is in group backup-ops
Second fact: /opt/backups/run-backup.sh is group-writable
Privileged link: root cron executes /opt/backups/run-backup.sh
Hypothesis: backup-ops can influence root execution
Minimal proof: change only a harmless marker in a lab copy
Defensive fix: root-owned script, restricted group write, reviewed deployment path
```

El movimiento importante es conectar hechos entre buckets. La membresía de grupo sola no es un hallazgo; un script escribible solo no es un hallazgo; la ejecución programada por root crea la pregunta de límite.

## Variantes y bypasses

### 1. Enumeración con shell mínima

Shells restringidas, reverse shells y sesiones no interactivas pueden no tener TTY, PATH o herramientas comunes.

### 2. Enumeración en container

El host puede ser un container donde root dentro del container no es root en el host, pero mounts, sockets o capabilities igual pueden cruzar límites.

### 3. Enumeración de host cloud

Las instancias cloud suman metadata, roles IAM, startup scripts y volúmenes adjuntos al conjunto de preguntas locales.

### 4. Enumeración en servidor multiusuario

Los hosts compartidos exponen membresía de grupos, permisos de home directories y relaciones de confianza de servicios locales.

### 5. Enumeración de host con hardening

Un buen hardening puede ocultar poco, pero aún deja suficiente para verificar que los controles funcionan.

## Impacto

- Encuentra las pocas rutas de escalada que valen verificación manual.
- Previene intentos inseguros de exploit basados en supuestos débiles.
- Produce evidencia de hardening defensivo.
- Crea una línea de tiempo reproducible para labs, reportes y retests.

## Detección y defensa

- **Hacé hardening de visibilidad de usuarios bajos donde sea posible.** Algunos datos son inherentemente locales, pero secretos, logs y configs no deberían ser ampliamente legibles.
- **Monitoreá bursts sospechosos de enumeración.** Muchos comandos read-only en una ventana corta pueden señalar actividad post-explotación.
- **Reducí servicios locales innecesarios.** Menos servicios y usuarios significa menos relaciones locales de confianza.
- **Mantené baselines.** Listas known-good de SUID, capabilities, timers y reglas sudo vuelven visible el drift.
- **Documentá rutas esperadas de privilegios.** Las rutas admin legítimas deberían ser suficientemente claras para que las anomalías resalten.

### Qué no funciona como defensa primaria

- **Bloquear un comando.** La enumeración usa muchos comandos y archivos equivalentes.
- **Asumir que read-only significa inocuo.** Secretos y configs legibles pueden ser límites de privilegios.
- **Ignorar servicios local-only.** Un service bindeado a `127.0.0.1` todavía puede ser alcanzable desde un foothold.

## Labs prácticos

Usá una VM propia y guardá outputs en una carpeta de lab.

### Armar un snapshot del host

```
mkdir -p privesc-enum
id | tee privesc-enum/id.txt
uname -a | tee privesc-enum/uname.txt
cat /etc/os-release | tee privesc-enum/os-release.txt
```

Esto crea evidencia repetible en vez de depender de memoria.

### Enumerar pistas de privilegios

```
sudo -l 2>&1 | tee privesc-enum/sudo-l.txt
find / -perm -4000 -type f 2>/dev/null | tee privesc-enum/suid.txt
getcap -r / 2>/dev/null | tee privesc-enum/capabilities.txt
```

Clasificá cada resultado antes de testearlo.

### Enumerar superficies de ejecución escribibles

```
find / -writable -type d 2>/dev/null | head -100
find /etc/systemd /etc/cron* -writable 2>/dev/null
```

Escribible no significa explotable salvo que un proceso privilegiado lo use.

### Enumerar servicios locales

```
ss -lntup 2>/dev/null
ps aux --forest 2>/dev/null | head -80
```

Registrá qué procesos corren como root y si usuarios bajos pueden influirlos.

## Ejemplos prácticos

- `sudo -l` revela un comando restringido que vale inspección más profunda.
- `getcap` encuentra un binario con `cap_setuid+ep`.
- Un directorio escribible es inocuo hasta que un cron job de root ejecuta scripts desde ahí.
- Un panel admin local bindeado a localhost importa después de tener acceso SSH.
- Un container tiene montado el socket de Docker, cambiando la pregunta de límite del host.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[sudo-misconfigurations|Sudo Misconfigurations]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linux-capabilities|Linux Capabilities]]
- [[cron-and-timer-abuse|Cron and Timer Abuse]]
- [[cloud-metadata-security|Seguridad de metadata cloud]]

### Futuras notas atómicas sugeridas

- linux-enumeration-output-triage
- container-breakout-triage
- linux-local-service-enumeration
- linux-credential-hunting

## Referencias

- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Documentación oficial:** proc filesystem — https://man7.org/linux/man-pages/man5/proc.5.html
- **Documentación oficial:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
