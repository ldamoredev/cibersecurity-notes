# Índice de Linux Privilege Escalation

## Propósito

Este índice es el punto de entrada raíz para la rama de Linux privilege escalation del vault de ciberseguridad.

Usalo para:

- entender límites de privilegios locales en Linux después de un foothold autorizado
- practicar enumeración de hosts estilo OSCP en labs propios
- separar pruebas de mala configuración de ejecución imprudente de exploits
- conectar hallazgos de host con offensive-security, cloud-security y hardening defensivo

Usá [[reference-registry-linux-privilege-escalation|Registro de referencias — Linux Privilege Escalation]] como fuente de verdad para las referencias de esta rama.
Volvé a [[index|Índice de ciberseguridad]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[index|Redes]] — incluso el privesc local suele depender de servicios alcanzables por red.

## Orden de aprendizaje recomendado

### Fase 1 — Modelo mental y enumeración

1. [[linux-privilege-escalation|Linux Privilege Escalation]]
2. [[linux-enumeration|Linux Enumeration]]

### Fase 2 — Clases comunes de mala configuración

1. [[sudo-misconfigurations|Sudo Misconfigurations]]
2. [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
3. [[linux-capabilities|Linux Capabilities]]
4. [[path-hijacking|PATH Hijacking]]

### Fase 3 — Riesgo programado y a nivel plataforma

1. [[cron-and-timer-abuse|Cron and Timer Abuse]]
2. [[kernel-exploit-triage|Kernel Exploit Triage]]

### Fase 4 — Automatización como asistente

1. [[linpeas-workflow|LinPEAS Workflow]]

## Cluster central de Linux Privilege Escalation

### Madurez de la rama

Esta rama tiene profundidad madura al 2026-04-30.
Las 9 notas atómicas siguen el template canónico de 11 secciones, incluyen labs prácticos y tienen ejemplos trabajados que conectan pistas locales del host con prueba mínima, remediación y límites seguros de lab.

### Fundamentos

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]

### Rutas de mala configuración

- [[sudo-misconfigurations|Sudo Misconfigurations]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linux-capabilities|Linux Capabilities]]
- [[path-hijacking|PATH Hijacking]]

### Rutas programadas y de kernel

- [[cron-and-timer-abuse|Cron and Timer Abuse]]
- [[kernel-exploit-triage|Kernel Exploit Triage]]

### Workflow de herramienta

- [[linpeas-workflow|LinPEAS Workflow]]

## Cross-links a otras ramas

### Ofensiva / recon

- [[recon-to-testing-handoff|Handoff de recon a testing]]
- [[service-validation|Validación de servicios]]
- [[scope-validation|Validación de alcance]]

### Cloud security

- [[ssh-access-to-cloud-hosts|Acceso SSH a hosts cloud]]
- [[cloud-iam-boundaries|Límites de IAM cloud]]
- [[cloud-metadata-security|Seguridad de metadata cloud]]
- [[cloud-secrets-management|Gestión de secretos cloud]]

### Redes y playbooks

- [[ports-and-services|Puertos y servicios]]
- [[index|Security Playbooks]]

## Futuras notas sugeridas

- linux-file-permissions
- linux-groups-and-users
- writable-service-files
- nfs-privilege-escalation
- docker-group-privilege-escalation
- linux-credential-hunting
- linux-log-review-for-privesc
- linux-post-exploitation-cleanup

### Posibles playbooks futuros

- linux-privesc-enumeration-checklist
- validate-sudo-privesc-in-lab
- audit-suid-binaries
- review-linux-capabilities
- triage-kernel-exploit-risk

## Notas de mantenimiento de la rama

- Mantené esta rama enfocada en límites locales de privilegios Linux después de que ya existe un foothold.
- Mantené initial access, recon, explotación web y rutas de identidad cloud en sus ramas existentes.
- Cada lab debería nombrar autorización, host objetivo, efecto esperado, límite de prueba y rollback o evidencia de remediación.
- Preferí prueba mínima sobre compromiso completo cuando el objetivo de aprendizaje es validación defensiva.
- Usá wikilinks no resueltos para futuras notas atómicas así Obsidian puede seguir la expansión de la rama.
- Mantené el patrón enumeration-first: identificar contexto, rankear rutas, verificar manualmente una ruta, registrar remediación.

## Referencias

- **Referencia técnica:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
