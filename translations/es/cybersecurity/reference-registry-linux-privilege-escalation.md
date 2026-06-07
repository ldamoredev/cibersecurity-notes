# Reference Registry — Linux Privilege Escalation

## Propósito

Esta nota estandariza las referencias para la rama linux-privilege-escalation.

Usala para:
- mantener notas de host privesc vinculadas a referencias fuertes de Linux y herramientas
- evitar sprawl random de checklists
- separar práctica de lab autorizada de actividad insegura
- ayudar a agentes futuros a elegir referencias consistentes

## Regla de fuente de verdad

Para notas de linux-privilege-escalation, este registry es la fuente de verdad primaria.

Usalo junto con:
- [[index|Linux Privilege Escalation Index]]
- [[index|Offensive Security / Recon Index]]
- [[index|Security Playbooks Index]]

---

## Política de selección de referencias

### Prioridad de fuentes

1. documentación oficial de Linux, sudo, systemd y proyectos
2. documentación oficial de herramientas
3. material de training/checklist de alta señal
4. bases curadas de técnicas
5. fuentes secundarias solo cuando sean claramente útiles

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar listas largas de referencias en notas atómicas

### Etiquetas

Usar:
- **Fundamental**
- **Docs oficiales**
- **Testing / Lab**
- **Referencia de técnica**
- **Investigación / Deep Dive**
- **Mitigación**

---

# Mapa de temas Linux privilege escalation

## linux-privilege-escalation

Referencias preferidas:
- **Referencia de técnica:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html

## linux-enumeration

Referencias preferidas:
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Docs oficiales:** proc filesystem — https://man7.org/linux/man-pages/man5/proc.5.html
- **Docs oficiales:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## suid-sgid-misconfigurations

Referencias preferidas:
- **Referencia de técnica:** GTFOBins: SUID — https://gtfobins.github.io/#+suid
- **Docs oficiales:** chmod — https://man7.org/linux/man-pages/man1/chmod.1.html
- **Testing / Lab:** HackTricks SUID — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid

## sudo-misconfigurations

Referencias preferidas:
- **Docs oficiales:** sudoers manual — https://www.sudo.ws/docs/man/sudoers.man/
- **Referencia de técnica:** GTFOBins: sudo — https://gtfobins.github.io/#+sudo
- **Docs oficiales:** sudo manual — https://www.sudo.ws/docs/man/sudo.man/

## linux-capabilities

Referencias preferidas:
- **Docs oficiales:** Linux capabilities — https://man7.org/linux/man-pages/man7/capabilities.7.html
- **Docs oficiales:** setcap — https://man7.org/linux/man-pages/man8/setcap.8.html
- **Referencia de técnica:** GTFOBins: capabilities — https://gtfobins.github.io/#+capabilities

## cron-and-timer-abuse

Referencias preferidas:
- **Docs oficiales:** crontab file format — https://man7.org/linux/man-pages/man5/crontab.5.html
- **Docs oficiales:** systemd timers — https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- **Docs oficiales:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## path-hijacking

Referencias preferidas:
- **Docs oficiales:** Bash command search and execution — https://www.gnu.org/software/bash/manual/bash.html#Command-Search-and-Execution
- **Docs oficiales:** ld.so dynamic linker — https://man7.org/linux/man-pages/man8/ld.so.8.html
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/

## kernel-exploit-triage

Referencias preferidas:
- **Docs oficiales:** Linux kernel security bugs — https://www.kernel.org/doc/html/latest/admin-guide/security-bugs.html
- **Docs oficiales:** uname — https://man7.org/linux/man-pages/man1/uname.1.html
- **Investigación / Deep Dive:** MITRE ATT&CK Privilege Escalation — https://attack.mitre.org/tactics/TA0004/

## linpeas-workflow

Referencias preferidas:
- **Docs oficiales de herramienta:** PEASS-ng / LinPEAS — https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
- **Referencia de técnica:** GTFOBins — https://gtfobins.github.io/

---

## Reglas de uso del registry

- Usá explotación activa solo en labs propios, CTFs u hosts explícitamente autorizados.
- Preferí encuadre de enumeración, evidencia y remediación antes que ejecución de exploit.
- No trates scripts automatizados como fuente de verdad; usalos para priorizar verificación manual.
- Las notas de kernel exploit deben enfatizar patching, validación de versión, snapshotting y riesgo de crash.
- Mantené initial access web, caminos de acceso cloud y recon en sus ramas existentes; esta rama empieza después de que existe un foothold Linux local.
