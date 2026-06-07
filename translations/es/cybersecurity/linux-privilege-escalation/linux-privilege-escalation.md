# Linux Privilege Escalation

## Definición

Linux privilege escalation es el proceso de pasar de una cuenta local con menos privilegios a una cuenta o capability con más privilegios en el mismo host Linux.

En esta rama, el alcance de aprendizaje seguro son labs propios, targets CTF y hosts explícitamente autorizados.

## Por qué importa

El initial access rara vez llega como root. El impacto real depende de si el host local permite que un usuario con pocos privilegios lea secretos, controle servicios, abuse delegación administrativa o se convierta en root.

Para defensores, Linux privesc también es un mapa de hardening. Cada ruta de escalada apunta a un límite corregible: reglas sudo, ownership de archivos, bits SUID, capabilities, permisos de servicios, jobs programados, patching de kernel o almacenamiento de credenciales.

## Cómo funciona

Usá un loop de 5 etapas:

1. **Contexto:** identificar usuario, grupos, hostname, OS, kernel, shell, entorno y rol de red.
2. **Inventario:** enumerar privilegios, rutas escribibles, servicios, schedules, credenciales y binarios inusuales.
3. **Hipótesis:** elegir una ruta plausible y declarar por qué podría cruzar un límite.
4. **Prueba mínima:** probar el issue de límite con la acción menos destructiva.
5. **Evidencia de remediación:** registrar owner, root cause, fix y verificación.

La meta-regla: una ruta de privesc no está "encontrada" hasta que explica qué límite falló.

### Ejemplo trabajado: de foothold a prueba segura

```
Foothold: app user on owned lab VM
Context: app user belongs to deploy group
Lead: deploy group can write /opt/app/restart.sh
Privileged link: root systemd service runs the script during restart
Minimal proof: lab-only marker file showing effective root execution
Fix: root-owned deployment scripts, separate writable release directory, service restart through audited sudo rule
Retest: app user can deploy artifacts but cannot modify root-executed script
```

Este es el patrón de la rama en miniatura: contexto local, una hipótesis de límite, prueba mínima y después evidencia de remediación.

## Técnicas / patrones

- **Revisión de delegación administrativa:** inspeccionar reglas sudo, membresías de grupos, derechos de control de service y privileged helper programs.
- **Revisión de permisos de archivos:** encontrar scripts escribibles, directorios world-writable, binarios SUID/SGID y service files con ownership incorrecto.
- **Descubrimiento de credenciales:** identificar claves expuestas, config files, shell history, tokens y backups sin exfiltrar datos innecesarios.
- **Revisión de ejecución programada:** inspeccionar cron jobs, timers de systemd y cadenas de ejecución escribibles.
- **Triage de kernel y packages:** comparar versiones de kernel/package contra riesgo conocido mientras se trata la ejecución de exploit como último recurso.

## Variantes y bypasses

### 1. Abuso de configuración

El sistema funciona como está configurado, pero la configuración otorga demasiado poder.

Los ejemplos incluyen reglas sudo amplias, scripts de service escribibles y membresía peligrosa de grupos.

### 2. Abuso de comportamiento de binario

Un binario legítimo tiene features que se vuelven peligrosas cuando corre con privilegios elevados.

GTFOBins es útil acá porque documenta comportamientos de ejecución privilegiada.

### 3. Influencia del entorno

La acción privilegiada confía en input controlado por el atacante como PATH, library paths, variables o directorios de trabajo escribibles.

### 4. Secretos como privilegio

Un usuario con pocos privilegios encuentra credenciales que desbloquean legítimamente un usuario o service con más privilegios.

### 5. Explotación de vulnerabilidad

El kernel, service o package tiene una vulnerabilidad que permite privilege escalation.

Esta clase tiene el mayor riesgo de crash y ética, y debería triagearse con cuidado.

## Impacto

- Shell root o ejecución de comandos como root.
- Lectura de archivos sensibles como claves privadas, credenciales de services o configuración de aplicaciones.
- Modificación de services, logs, jobs programados o archivos de aplicación.
- Pivot desde un solo host hacia metadata cloud, redes internas o cuentas de mayor valor.
- Prueba de que el compromiso local tiene blast radius a nivel host o entorno.

## Detección y defensa

- **Parcheá y reducí primero la exposición de kernel.** Los bugs a nivel kernel son de alto impacto y suelen ser difíciles de testear con seguridad; patching y visibilidad de versión reducen rutas de emergencia.
- **Limitá sudo por comando y argumento.** Las reglas sudo de menor privilegio son más fáciles de auditar que NOPASSWD amplio o binarios capaces de abrir shell.
- **Remové SUID/SGID y capabilities innecesarios.** Los bits privilegiados deberían ser raros, justificados y monitoreados.
- **Bloqueá rutas de ejecución escribibles.** Scripts, service files, targets de cron y directorios usados por tareas privilegiadas no deben ser escribibles por usuarios no confiables.
- **Protegé credenciales por diseño.** Archivos, variables de entorno, backups y logs deberían evitar almacenar secretos reutilizables.
- **Logueá cruces de límites administrativos.** sudo, cambios de service, instalaciones de packages y cambios de archivos relevantes para privilegios deberían dejar evidencia.

### Qué no funciona como defensa primaria

- **Confiar en nombres de usuario.** Un usuario "normal" igual puede heredar grupos, reglas sudo o rutas escribibles peligrosas.
- **Ocultar archivos.** La oscuridad no arregla permisos ni ubicación de secretos.
- **Correr LinPEAS una vez.** El output automatizado es input de triage, no prueba ni remediación.
- **Asumir que kernel parcheado significa host seguro.** La mayoría de rutas privesc son malas configuraciones, no kernel exploits.

## Labs prácticos

Usá una VM Linux propia.

### Armar la primera tarjeta de contexto

```
id
hostnamectl 2>/dev/null || hostname
uname -a
pwd
echo "$PATH"
```

Registrá quién sos, en qué sistema estás y qué entorno puede influir comandos.

### Crear una tabla de ranking de rutas

```
Candidate:
Evidence:
Boundary crossed:
Likely impact:
Risk of testing:
Minimal proof:
Remediation:
```

Esto previene el comportamiento de "probar todo" y fuerza razonamiento.

### Comparar tres clases de rutas

```
sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```

Tratá el output como pistas. Cada pista necesita verificación manual.

### Registrar prueba mínima

```
Target host:
Authorized scope:
Finding:
Proof action:
Observed result:
What was not done:
Rollback/remediation evidence:
```

Buenas notas de privesc dicen qué se evitó intencionalmente.

## Ejemplos prácticos

- Un usuario puede correr un comando de backup con sudo, pero el comando acepta un config file escribible.
- Un helper SUID custom llama a `tar` sin ruta absoluta.
- Una cuenta de service puede leer un config de aplicación que contiene una contraseña de base de datos.
- Un kernel parece vulnerable por versión, pero la distribución tiene patches backporteados.
- LinPEAS resalta muchos items, pero solo uno cruza un límite real de privilegios.

## Notas relacionadas

- [[linux-enumeration|Linux Enumeration]]
- [[sudo-misconfigurations|Sudo Misconfigurations]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linux-capabilities|Linux Capabilities]]
- [[kernel-exploit-triage|Kernel Exploit Triage]]
- [[recon-to-testing-handoff|Handoff de recon a testing]]

### Futuras notas atómicas sugeridas

- linux-file-permissions
- linux-groups-and-users
- linux-credential-hunting
- linux-post-exploitation-cleanup

## Referencias

- **Referencia técnica:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
