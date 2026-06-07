# PATH Hijacking

## Definición

PATH hijacking es privilege escalation mediante la influencia sobre qué ejecutable o librería carga un proceso privilegiado.

El caso clásico es un script o binario privilegiado llamando a `cp`, `tar` u otro helper sin ruta absoluta mientras el atacante controla la ruta de búsqueda o el directorio de trabajo.

## Por qué importa

PATH hijacking convierte un atajo chico de código en una falla de límite de privilegios. Es común en scripts custom, helpers SUID, cron jobs, service wrappers y reglas sudo.

Para defensores, recuerda que el código privilegiado debe tratar el comportamiento de lookup como input no confiable.

## Cómo funciona

Usá 4 preguntas de lookup:

1. **Caller:** qué proceso privilegiado ejecuta el helper?
2. **Lookup:** el helper se referencia por ruta absoluta o se busca por PATH?
3. **Control:** el usuario bajo puede influir PATH, directorio de trabajo, library path o archivo helper?
4. **Privilegio:** el helper corre como root u otra cuenta privilegiada?

## Técnicas / patrones

- Inspeccioná scripts por nombres de helpers no calificados.
- Inspeccioná binarios por strings de helpers, pero verificá el comportamiento con cuidado.
- Revisá reglas sudo por `SETENV` o preservación de entorno.
- Revisá cron y jobs de systemd por definiciones de PATH.
- Usá `namei -l` para verificar ownership de directorios a lo largo de cada ruta.

### Ejemplo trabajado: falla de lookup de helper

```
Privileged caller: root cron script
Command in script: tar -czf /backup/app.tgz /srv/app
PATH in job: /opt/app/bin:/usr/bin:/bin
Attacker control: /opt/app/bin is group-writable
Minimal proof: lab-only harmless helper logs its effective user
Fix: /usr/bin/tar plus root-owned PATH directories
```

PATH hijacking no es "PATH es raro". Es lookup controlado por atacante más ejecución privilegiada.

## Variantes y bypasses

### 1. Hijack de PATH en shell

Un shell script privilegiado llama a un helper por nombre.

### 2. Confianza en directorio actual

El proceso busca o ejecuta desde un directorio de trabajo escribible.

### 3. Influencia de library path

El dynamic loader o una ruta de plugins específica del programa carga código controlado por atacante.

### 4. Preservación de variables de entorno

Sudo o configuración de service preserva variables que influyen en lookup.

### 5. Ruta relativa en service o cron

Un comando programado o de service asume un directorio de trabajo que puede cambiarse.

## Impacto

- Ejecución privilegiada de comandos.
- Modificación de archivos propiedad de root.
- Persistencia mediante rutas de helpers modificadas.
- Compromiso de tareas programadas o service restarts.
- Comportamiento confuso porque el nombre del comando parece legítimo.

## Detección y defensa

- **Usá rutas absolutas en scripts privilegiados.** El comportamiento de búsqueda no debería decidir ejecución privilegiada.
- **Definí explícitamente un PATH seguro.** Contextos de cron, sudo y service deberían definir rutas confiables.
- **Evitá preservación peligrosa del entorno.** Variables de loader y path no deberían cruzar a contextos privilegiados.
- **Protegé directorios padre.** Un archivo seguro en un directorio escribible no es una cadena de ejecución segura.
- **Preferí helpers privilegiados más simples.** Helpers más chicos y auditados tienen menos probabilidad de hacer lookup inseguro.

### Qué no funciona como defensa primaria

- **Confiar en el PATH actual.** El entorno actual pertenece al caller salvo que se resetee.
- **Revisar solo permisos de archivo.** Los permisos de directorio y el orden de lookup también importan.
- **Depender de la legibilidad del script.** Helpers compilados pueden cometer el mismo error.

## Labs prácticos

Usá un lab propio con un script de prueba privilegiado inocuo.

### Encontrar comandos no calificados en scripts

```
grep -R "tar\\|cp\\|mv\\|sh\\|bash" /opt /usr/local/bin 2>/dev/null
```

La revisión manual es obligatoria porque grep solo encuentra pistas.

### Revisar la cadena de path

```
echo "$PATH"
which tar
namei -l "$(which tar)"
```

El ejecutable y cada directorio padre deben ser confiables.

### Revisar comportamiento de entorno en sudo

```
sudo -l
sudo -V | grep -i "env" | head
```

Buscá `SETENV`, `secure_path` y variables preservadas.

### Armar una tarjeta de riesgo PATH

```
Privileged caller:
Helper command:
Absolute path used:
Attacker-controlled lookup component:
Privilege level:
Minimal proof:
Fix:
```

Esto mantiene concreto el hallazgo.

## Ejemplos prácticos

- Un cron script de root llama a `tar` sin `/usr/bin/tar`.
- Un helper SUID llama a `service` por nombre.
- Una regla sudo preserva PATH y permite un script que llama a helpers comunes.
- Un service de systemd lee un environment file escribible que contiene PATH.
- Un programa privilegiado carga un plugin desde un directorio escribible.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[cron-and-timer-abuse|Cron and Timer Abuse]]
- [[sudo-misconfigurations|Sudo Misconfigurations]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linux-enumeration|Linux Enumeration]]

### Futuras notas atómicas sugeridas

- ld-preload-abuse
- secure-path-in-sudoers
- privileged-script-hardening
- library-search-path-risk

## Referencias

- **Documentación oficial:** Bash command search and execution — https://www.gnu.org/software/bash/manual/bash.html#Command-Search-and-Execution
- **Documentación oficial:** ld.so dynamic linker — https://man7.org/linux/man-pages/man8/ld.so.8.html
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
