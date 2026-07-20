# SUID and SGID Misconfigurations

## Definición

Las malas configuraciones SUID y SGID ocurren cuando un ejecutable corre con los privilegios del owner o grupo del archivo y expone comportamiento que un usuario con pocos privilegios puede abusar.

## Por qué importa

Los binarios SUID root son cruces intencionales de privilegios. Son poderosos, fáciles de pasar por alto y peligrosos cuando son custom, viejos o capaces de lanzar helper programs.

Para defensores, un inventario SUID known-good y chico es una baseline práctica de hardening.

## Cómo funciona

Usá 4 preguntas por cada binario privilegiado:

1. **Esperado:** este binario normalmente es SUID/SGID en esta distribución?
2. **Owner:** como qué usuario o grupo ejecuta?
3. **Comportamiento:** puede leer/escribir archivos, ejecutar comandos, cargar config o llamar helpers?
4. **Influencia:** un usuario bajo puede controlar argumentos, input files, paths, entorno o directorio de trabajo?

## Técnicas / patrones

- Compará listas SUID contra una baseline known-good.
- Priorizá rutas custom inusuales como `/opt`, `/usr/local/bin` y home directories.
- Revisá GTFOBins por comportamiento privilegiado conocido.
- Inspeccioná strings solo como pista, no como prueba.
- Buscá llamadas a helpers sin rutas absolutas.

### Ejemplo trabajado: helper SUID custom

```
Lead: /usr/local/bin/report-helper has SUID root
Expected baseline: not present on standard image
Behavior clue: strings show "tar -czf"
Influence clue: helper runs from a user-writable working directory
Minimal proof: controlled lab path proves helper lookup can be influenced
Fix: remove SUID, use a root-owned service wrapper, absolute paths, and input validation
```

Los hallazgos SUID más fuertes explican tanto por qué el binario es privilegiado como cómo un usuario bajo puede influir su comportamiento privilegiado.

## Variantes y bypasses

### 1. Utilidad peligrosa conocida

Una utilidad legítima tiene features que se vuelven peligrosas bajo SUID.

### 2. Helper binary custom

Un helper interno fue creado para resolver un problema de operaciones y carece de revisión de seguridad.

### 3. Llamada a helper dependiente de PATH

El binario llama a otro programa por nombre en vez de ruta absoluta.

### 4. Input o config escribible

El binario confía en un archivo que el usuario con pocos privilegios puede controlar.

### 5. Acceso a datos SGID

SGID puede no convertirse en root, pero puede otorgar acceso a archivos sensibles propiedad de un grupo.

## Impacto

- Ejecución de comandos como root.
- Lectura o escritura privilegiada de archivos.
- Acceso a secretos propiedad de grupos.
- Modificación persistente de rutas privilegiadas.
- Denial of service local si helpers privilegiados son inestables.

## Detección y defensa

- **Mantené una baseline de inventario SUID/SGID.** El drift es más fácil de detectar cuando se conocen los archivos privilegiados esperados.
- **Remové SUID de binarios innecesarios.** La ejecución privilegiada debería ser rara y justificada.
- **Revisá helpers custom como código sensible de seguridad.** Cualquier helper SUID es un componente de límite.
- **Usá rutas absolutas y entornos sanitizados.** Los binarios privilegiados no deben confiar en comportamiento de lookup controlado por caller.
- **Monitoreá cambios de bits privilegiados.** Cambios inesperados de chmod/chown son eventos de alta señal.

### Qué no funciona como defensa primaria

- **Asumir que los binarios estándar siempre son seguros.** El contexto y los permisos todavía importan.
- **Revisar solo `/bin`.** Los archivos SUID custom suelen vivir en otros lugares.
- **Depender de nombres de archivo.** Comportamiento, owner e influencia deciden el riesgo.

## Labs prácticos

Usá una VM propia.

### Inventariar binarios privilegiados

```
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

Etiquetá cada uno como estándar, custom, desconocido o sospechoso.

### Comparar ownership y ubicación

```
ls -la /path/to/suid-binary
file /path/to/suid-binary
```

Los binarios SUID custom propiedad de root merecen la mayor atención.

### Inspeccionar comportamiento de helper superficialmente

```
strings /path/to/suid-binary | head -80
```

Strings puede revelar nombres de helpers, rutas de archivos o referencias de config, pero no es análisis completo.

### Armar una tarjeta de hallazgo SUID

```
Binary:
Owner/group:
Path:
Expected on OS:
User-controlled input:
Privileged behavior:
Minimal proof:
Recommended fix:
```

Esto mantiene el foco en la falla de límite.

## Ejemplos prácticos

- Un helper de backup SUID root custom llama a `tar` sin ruta absoluta.
- Un binario SUID lee un config file desde un directorio escribible.
- Una herramienta SGID otorga acceso a un archivo sensible de grupo.
- Un binario estándar aparece en una ubicación no estándar y recibió SUID manualmente.
- Un helper vulnerable ya no necesita SUID después de rediseñar el workflow.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]
- [[path-hijacking|PATH Hijacking]]
- [[linux-capabilities|Linux Capabilities]]
- [[sudo-misconfigurations|Sudo Misconfigurations]]

### Futuras notas atómicas sugeridas

- suid-helper-secure-design
- linux-file-permissions
- sgid-data-access
- privileged-binary-auditing

## Referencias

- **Referencia técnica:** GTFOBins: SUID — https://gtfobins.github.io/#+suid
- **Documentación oficial:** chmod — https://man7.org/linux/man-pages/man1/chmod.1.html
- **Testing / Lab:** HackTricks SUID — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
