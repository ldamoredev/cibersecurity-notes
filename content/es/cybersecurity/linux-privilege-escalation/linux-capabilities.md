# Linux Capabilities

## Definición

Linux capabilities dividen privilegios de root en unidades más chicas que se pueden asignar a procesos o archivos.

Una mala configuración de capabilities ocurre cuando un binario recibe una capability que permite que un usuario con pocos privilegios cruce un límite sensible.

## Por qué importa

Las capabilities suelen introducirse para evitar root completo, pero siguen otorgando partes de root. Una sola capability peligrosa puede ser equivalente a root en la práctica.

Para defensores, las capabilities son una herramienta de precisión que requiere inventario y justificación.

## Cómo funciona

Usá 5 preguntas de riesgo sobre capabilities:

1. **Qué capability:** qué poder exacto se otorga?
2. **A qué:** process, service o file capability?
3. **Quién puede ejecutar:** qué usuarios pueden correr el binario?
4. **Qué comportamiento:** el binario puede usar la capability para leer, escribir, bindear, tracear o cambiar identidad?
5. **Puede encadenarse:** la capability se combina con ejecución de comandos o escritura de archivos?

## Técnicas / patrones

- Enumerá file capabilities con `getcap -r /`.
- Priorizá `cap_setuid`, `cap_setgid`, `cap_dac_read_search`, `cap_dac_override`, `cap_sys_admin`, `cap_net_raw` y `cap_net_bind_service`.
- Revisá si el binario se comporta como intérprete o puede abrir shell.
- Compará el uso de la capability contra la necesidad operativa.
- Remové file capabilities que ya no estén justificadas.

### Ejemplo trabajado: capability que supera su propósito

```
Lead: /usr/local/bin/net-helper = cap_net_raw+ep
Business purpose: collect packet diagnostics for support
Who can execute: all local users
Boundary question: can any user now perform packet-level activity?
Minimal proof: show capability-bearing execution path without capturing unrelated traffic
Fix: restrict execution to admin group or move diagnostics behind an audited service
```

Las capabilities no son automáticamente malas. El hallazgo aparece cuando se combinan capability, comportamiento del ejecutable y derechos amplios de ejecución.

## Variantes y bypasses

### 1. Capability de cambio de identidad

`cap_setuid` o `cap_setgid` puede permitir transición de usuario o grupo.

### 2. Capability de acceso a archivos

Capabilities de DAC override/read pueden saltear permisos normales de archivos.

### 3. Capability de red

Capabilities de red pueden habilitar packet capture, raw sockets o binding de puertos privilegiados.

### 4. Capability amplia de sistema

`cap_sys_admin` es notoriamente amplia y suele estar demasiado cerca de root.

### 5. Drift de capabilities en containers

Los containers pueden correr con capabilities que debilitan más de lo esperado los límites del host.

## Impacto

- Lectura o escritura privilegiada de archivos.
- Cambio de identidad o ejecución equivalente a root.
- Packet capture o manipulación de red.
- Precondiciones de escape de container.
- Expansión de privilegios de servicio más allá del diseño previsto.

## Detección y defensa

- **Inventariá file capabilities.** Las capabilities son menos visibles que bits SUID y necesitan su propia baseline.
- **Otorgá la capability más estrecha posible.** Evitá capabilities amplias como `cap_sys_admin`.
- **Limitá acceso de ejecución.** Un binario con capability no debería ser ejecutable por usuarios que no lo necesitan.
- **Preferí gestión de privilegios a nivel service.** Evitá dispersar file capabilities en herramientas custom.
- **Monitoreá cambios de `setcap`.** La asignación de capabilities es un cambio de límite de privilegios.

### Qué no funciona como defensa primaria

- **Decir "no es SUID".** Las capabilities pueden ser igual de peligrosas.
- **Otorgar capabilities amplias por comodidad.** El límite se vuelve poco claro.
- **Ignorar containers.** Las capabilities de container pueden cambiar el significado de "root dentro del container".

## Labs prácticos

Usá una VM propia o un container descartable.

### Enumerar file capabilities

```
getcap -r / 2>/dev/null
```

Clasificá resultados como esperados, desconocidos o peligrosos.

### Inspeccionar un binario

```
ls -la /path/to/binary
getcap /path/to/binary
file /path/to/binary
```

El riesgo de capability depende tanto de la capability como del comportamiento del binario.

### Armar una tabla de riesgo de capability

```
Binary:
Capability:
Who can execute:
Normal purpose:
Dangerous behavior:
Minimal proof:
Safer alternative:
```

Esto convierte output de capability en una decisión.

### Verificar remoción en un lab

```
sudo setcap -r /path/to/binary
getcap /path/to/binary
```

Solo remové capabilities en sistemas de lab propios o con aprobación de cambios.

## Ejemplos prácticos

- Python con `cap_setuid+ep` puede volverse equivalente a root.
- Una herramienta de packets con `cap_net_raw` puede estar justificada para un grupo admin específico, pero ser riesgosa para todos los usuarios.
- Un binario de service custom conserva una capability vieja después de que el service ya no la necesita.
- Un container corre con capabilities excesivas y debilita supuestos de aislamiento del host.
- Un helper de backup tiene DAC override cuando un diseño más estrecho usaría permisos de grupo.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[kernel-exploit-triage|Kernel Exploit Triage]]
- [[cloud-lab-infrastructure|Infraestructura de lab cloud]]

### Futuras notas atómicas sugeridas

- container-capabilities
- cap-sys-admin-risk
- linux-file-capability-inventory
- capability-hardening-baseline

## Referencias

- **Documentación oficial:** Linux capabilities — https://man7.org/linux/man-pages/man7/capabilities.7.html
- **Documentación oficial:** setcap — https://man7.org/linux/man-pages/man8/setcap.8.html
- **Referencia técnica:** GTFOBins: capabilities — https://gtfobins.github.io/#+capabilities
