# Sudo Misconfigurations

## Definición

Una mala configuración de sudo es una falla de delegación administrativa donde un usuario puede correr un comando como otro usuario, muchas veces root, de una forma que otorga más poder del previsto.

## Por qué importa

Sudo es una herramienta normal de operaciones, así que su riesgo suele estar oculto dentro de workflows legítimos de mantenimiento. Una sola regla amplia puede convertir un foothold menor en compromiso completo del host.

Para defensores, la revisión de sudo es una de las actividades de hardening Linux de mayor valor porque describe directamente quién puede cruzar límites de privilegios.

## Cómo funciona

Hacé 5 preguntas sobre sudo:

1. **Quién:** qué usuario o grupo recibe delegación?
2. **Como quién:** en qué usuario target pueden convertirse?
3. **Qué:** qué comando, ruta y argumentos están permitidos?
4. **Cómo:** se requiere contraseña, se preserva entorno, se usan wildcards?
5. **Escape:** el comando permitido puede abrir shell, editar archivos, cargar plugins o escribir rutas propiedad de root?

## Técnicas / patrones

- Inspeccioná `sudo -l` antes de leer supuestos desde `/etc/sudoers`.
- Tratá los argumentos del comando como parte del permiso.
- Revisá GTFOBins por comportamiento de shell escape o escritura de archivos.
- Buscá `NOPASSWD`, `SETENV`, wildcards amplios, intérpretes, editores, pagers, herramientas de archivo y package managers.
- Probá con comandos mínimos en un lab propio.

### Ejemplo trabajado: de regla sudo a root cause

```
sudo -l lead: (root) NOPASSWD: /usr/bin/vim /var/log/app.log
Boundary question: can the user use the editor to write outside the intended file?
Minimal lab proof: demonstrate root-owned file write in a disposable path
What not to do: modify real logs or plant persistence
Root cause: shell-capable/editor binary delegated as root
Fix: replace editor sudo with a narrow log-view command or controlled support workflow
```

El reporte no debería quedarse en "vim puede escapar". Tiene que explicar por qué el workflow delegado le dio al usuario un editor root de propósito general.

## Variantes y bypasses

### 1. Binario capaz de abrir shell

El comando permitido puede spawnear una shell o ejecutar otro comando.

### 2. Escritura de archivos como root

El comando puede sobrescribir archivos propiedad de root o poner contenido en ubicaciones confiables.

### 3. Wildcard de argumentos

Una regla sudo restringe el binario pero permite argumentos controlados por atacante.

### 4. Preservación de entorno

La regla permite influencia peligrosa del entorno mediante `SETENV`, `env_keep` o variables de loader.

### 5. Ruta de comando relativa o escribible

La regla apunta a una ruta que el usuario puede reemplazar o influir.

## Impacto

- Ejecución de comandos como root.
- Lectura o escritura de archivos como root.
- Modificación persistente de service o cron.
- Extracción de secretos desde archivos legibles por root.
- Movimiento lateral mediante claves, tokens o configuración.

## Detección y defensa

- **Usá rutas exactas de comandos y argumentos exactos.** Las reglas sudo deberían ser lo bastante estrechas para que el comportamiento del comando sea predecible.
- **Evitá herramientas capaces de abrir shell donde sea posible.** Editores, pagers, intérpretes y herramientas de archivo suelen tener comportamiento de escape.
- **Requerí autenticación para rutas sensibles.** `NOPASSWD` debería ser raro y justificado.
- **Deshabilitá preservación peligrosa del entorno.** Evitá `SETENV` y reglas amplias de `env_keep` salvo que el riesgo esté entendido.
- **Revisá logs de sudo.** La ejecución sudo debería ser observable y estar ligada a un usuario.

### Qué no funciona como defensa primaria

- **Confiar en que un comando "no es una shell".** Muchas herramientas pueden ejecutar comandos indirectamente.
- **Depender de capacitación de usuarios.** La policy debería prevenir extralimitación accidental.
- **Usar wildcards por comodidad.** Los wildcards suelen mover la decisión de seguridad desde la policy hacia input controlado por atacante.

## Labs prácticos

Usá un usuario de lab propio con una regla sudo deliberadamente segura.

### Leer la superficie sudo del usuario

```
sudo -l
```

Copiá el comando exacto, usuario target, estado de contraseña y opciones.

### Clasificar el comando

```
Allowed command:
Target user:
Password required:
Can read files:
Can write files:
Can execute commands:
Environment influence:
GTFOBins class:
```

Esto hace explícito el comportamiento riesgoso.

### Testear límites de argumentos con seguridad

```
sudo /allowed/command --help
sudo /allowed/command --version
```

Usá documentación y flags inocuos antes de intentar prueba de impacto.

### Registrar una decisión de prueba mínima

```
Finding:
Allowed sudo rule:
Potential escape:
Proof chosen:
Why this proof is minimal:
Fix:
Retest:
```

El reporte debería explicar la falla de policy, no solo "got root".

## Ejemplos prácticos

- Un usuario puede correr `vim` como root y puede editar archivos propiedad de root.
- Un comando de backup acepta una ruta destino que escribe dentro de `/etc`.
- Una regla sudo permite `/usr/bin/find *`, y el control de argumentos cambia el comportamiento.
- `SETENV` permite que un comando privilegiado cargue comportamiento no confiable.
- Una regla otorga restart de service, pero el service file es escribible por el usuario.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]
- [[path-hijacking|PATH Hijacking]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[linpeas-workflow|LinPEAS Workflow]]

### Futuras notas atómicas sugeridas

- sudoers-policy-design
- sudo-environment-risk
- gtfobins-workflow
- writable-service-files

## Referencias

- **Documentación oficial:** sudoers manual — https://www.sudo.ws/docs/man/sudoers.man/
- **Referencia técnica:** GTFOBins: sudo — https://gtfobins.github.io/#+sudo
- **Documentación oficial:** sudo manual — https://www.sudo.ws/docs/man/sudo.man/
