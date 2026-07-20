# LinPEAS Workflow

## Definición

LinPEAS workflow es el uso disciplinado del script de enumeración LinPEAS como asistente de triage para Linux privilege escalation, seguido por verificación manual y reporting enfocado en remediación.

LinPEAS no es el hallazgo. La falla de límite verificada manualmente es el hallazgo.

## Por qué importa

La automatización ayuda a estudiantes y testers a no perder rutas comunes, pero también puede producir output ruidoso, falsos positivos y reportes superficiales.

Un buen workflow usa LinPEAS para priorizar dónde mirar, y después prueba una ruta con claridad.

## Cómo funciona

Usá 5 fases:

1. **Preparar:** confirmar autorización, rol del host, política de upload y expectativas de cleanup.
2. **Correr:** ejecutar el script de forma controlada y guardar output.
3. **Triar:** agrupar hallazgos por sudo, SUID, capabilities, rutas escribibles, credenciales, servicios y kernel.
4. **Verificar:** testear manualmente un candidato con prueba mínima.
5. **Reportar:** explicar root cause, impacto, fix y evidencia de retest.

## Técnicas / patrones

- Corré tooling después de recolectar contexto manual básico.
- Guardá el output crudo, pero no lo pegues entero en notas.
- Tratá colores y severidad como disparadores, no como verdad.
- Verificá comandos manualmente y leé archivos relevantes.
- Limpiá scripts y outputs según las reglas del lab o engagement.

### Ejemplo trabajado: de output de herramienta a hallazgo verificado

```text
LinPEAS highlight: possible writable service file
Manual check: namei -l and systemctl cat confirm writable drop-in
Boundary question: does root/systemd consume this file?
Minimal proof: lab-only service override writes a harmless marker
Finding: low user can influence root service configuration
Fix: root-owned service path, deployment controls, alert on unit changes
```

El valor de LinPEAS es la priorización. El valor del operador es convertir un highlight en prueba o rechazarlo.

## Variantes y bypasses

### 1. Entorno sin upload

La política o los controles técnicos pueden prohibir subir scripts; la enumeración manual igual tiene que funcionar.

### 2. Shell restringida

La sesión puede no tener TTY, directorios escribibles o intérpretes comunes.

### 3. Host de producción ruidoso

Correr scripts amplios puede ser inapropiado en sistemas sensibles.

### 4. Modo velocidad CTF

En labs, LinPEAS puede apuntar rápido a la ruta esperada, pero aprender todavía requiere entender la ruta.

### 5. Output con muchos falsos positivos

Muchos items resaltados son informativos o no explotables sin otra condición.

## Impacto

- Enumeración más rápida.
- Mejor cobertura de categorías comunes de Linux privesc.
- Riesgo de ruido, recolección accidental de datos o overclaiming.
- Reportes mejores cuando el output se convierte en evidencia verificada.

## Detección y defensa

- **Asumí que los scripts de enumeración son observables.** Ejecución, creación de archivos y muchas lecturas locales pueden aparecer en logs o EDR.
- **Restringí upload y ejecución de scripts donde corresponda.** Los controles deberían estar guiados por política, no ser ad hoc.
- **Reducí hallazgos mediante hardening.** Reglas sudo limpias, SUID, capabilities, rutas escribibles y secretos reducen la señal automatizada.
- **Usá LinPEAS defensivamente en labs.** Blue teams pueden correrlo contra golden images para encontrar drift.
- **Combiná automatización con baselines.** Un host known-good hace que el output sea más fácil de evaluar.

### Qué no funciona como defensa primaria

- **Bloquear LinPEAS por nombre.** La enumeración puede hacerse manualmente o con herramientas modificadas.
- **Tratar ausencia de output rojo como seguridad.** Los scripts son incompletos y dependen del contexto.
- **Aceptar output de script como prueba.** La verificación manual es obligatoria.

## Labs prácticos

Usá una VM propia.

### Correr contexto manual primero

```
id
uname -a
sudo -l
```

Esto te da anclas antes del output automatizado.

### Guardar output de LinPEAS

```
./linpeas.sh | tee linpeas-output.txt
```

Corré scripts descargados solo cuando el lab lo permita y entiendas la fuente.

### Triar por categoría

```
Sudo:
SUID/SGID:
Capabilities:
Writable paths:
Credentials:
Services/timers:
Kernel:
Top manual check:
```

Convertí el output en una lista chica de acciones.

### Verificar un candidato manualmente

```
LinPEAS line:
Manual command:
Observed evidence:
Boundary crossed:
Minimal proof:
Fix:
```

Este es el paso que transforma output de herramienta en conocimiento.

## Ejemplos prácticos

- LinPEAS resalta un binario SUID; la revisión manual de GTFOBins explica si importa.
- LinPEAS reporta un directorio escribible; el trazado manual muestra que ningún proceso privilegiado lo usa.
- LinPEAS encuentra una regla sudo; el issue real es el comportamiento de escritura de archivos del comando.
- LinPEAS marca versiones de kernel; la metadata de patches del vendor rechaza la ruta.
- Un equipo defensivo corre LinPEAS en una imagen de lab y remueve capabilities innecesarias.

## Notas relacionadas

- [[linux-privilege-escalation|Linux Privilege Escalation]]
- [[linux-enumeration|Linux Enumeration]]
- [[sudo-misconfigurations|Sudo Misconfigurations]]
- [[suid-sgid-misconfigurations|SUID y SGID Misconfigurations]]
- [[kernel-exploit-triage|Kernel Exploit Triage]]

### Futuras notas atómicas sugeridas

- linpeas-output-triage
- manual-privesc-verification
- linux-privesc-reporting
- authorized-tool-upload-policy

## Referencias

- **Documentación oficial de herramienta:** PEASS-ng / LinPEAS — https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
- **Referencia técnica:** GTFOBins — https://gtfobins.github.io/
