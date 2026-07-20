---
type: concept
status: active
created: 2026-04-29
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - command-injection
  - injection
sources:
  - "[[wiki/sources/Szsecurity Courses]]"
---

# Inyección de comandos

## Definición
La inyección de comandos (command injection) ocurre cuando una aplicación construye un comando del sistema operativo a partir de input controlado por el atacante y lo ejecuta a través de un shell o una API de proceso sin separación estricta entre los datos y la sintaxis del comando.

## Por qué importa
La inyección de comandos cruza de la lógica de aplicación al sistema operativo del host. El impacto puede saltar de una sola feature web a lectura de archivos, robo de credenciales, movimiento lateral, acceso a metadata de nube o ejecución remota de código.

Es la versión de comandos-de-SO de la lección de inyección más amplia: el input no confiable no debe volverse sintaxis del intérprete.

## Cómo funciona
La inyección de comandos tiene **4 partes en movimiento**:

1. **Input.** Dato controlado por el usuario llega a una feature como ping, conversión de PDF, procesamiento de imágenes, backup o tooling de Git.
2. **Construcción del comando.** El servidor concatena el input en un comando de shell.
3. **Frontera del intérprete.** El shell interpreta metacaracteres como `;`, `&&`, `|`, `$()` o backticks.
4. **Ejecución.** El comando corre con los privilegios de SO de la aplicación.

Patrón inseguro:

```js
exec("ping -c 1 " + req.query.host)
```

Ejemplo con forma de payload:

```text
host=127.0.0.1; id
```

El bug no es "ping existe". El bug es que dato controlado por el atacante cruza hacia la sintaxis del shell.

## Técnicas / patrones
Los atacantes testean:

- herramientas de red: ping, nslookup, curl, traceroute
- herramientas de archivos: convert, ffmpeg, tar, zip, grep
- herramientas de deploy/tools: git, docker, kubectl, scripts de backup
- separadores: `;`, `&&`, `||`, `|`, newline
- sustitución de comandos: `$()`, backticks
- indicadores ciegos: delay de tiempo, callbacks DNS/HTTP, salida cambiada

## Variantes y bypasses
La inyección de comandos aparece en **5 contextos**.

### 1. Inyección de salida directa
La salida del comando aparece en la response HTTP.

### 2. Inyección de comandos ciega
La response no muestra salida, así que el timing o los callbacks out-of-band prueban la ejecución.

### 3. Inyección de argumentos
El input no puede agregar un comando nuevo pero puede agregar flags que cambian el comportamiento de la herramienta invocada.

### 4. Inyección de entorno
Variables de entorno, paths o nombres de archivo controlados por el usuario influyen en la ejecución.

### 5. Mal uso de proceso sin-shell
Incluso sin un shell, argumentos inseguros igual pueden disparar comportamiento peligroso a nivel de herramienta.

## Impacto
Ordenado aproximadamente por severidad:

- **Ejecución remota de código.** Los comandos corren como el usuario de la aplicación.
- **Robo de credenciales y secretos.** Variables de entorno, archivos, metadata de nube o credenciales de servicio se filtran.
- **Movimiento lateral.** Las herramientas de red interna se vuelven alcanzables desde el servidor.
- **Destrucción o alteración de datos.** Los comandos borran, sobrescriben o exfiltran datos.
- **Reconocimiento del host.** Los atacantes aprenden usuarios, paths, procesos y acceso de red.

## Detección y defensa
Ordenado por efectividad:

1. **Evitá hacer shell-out para trabajo dirigido por requests.**
   Usá APIs de librería o implementaciones internas seguras en vez de invocar comandos de shell.

2. **Si se requiere un proceso, pasá los argumentos como un array a una API sin-shell.**
   Mantené el ejecutable y los argumentos estructuralmente separados para que los metacaracteres queden como datos.

3. **Hacé allowlist del input por dominio esperado.**
   Validá hostnames, nombres de archivo, IDs o elecciones de enum antes de que lleguen a cualquier comando.

4. **Corré con mínimo privilegio y aislamiento.**
   Contenedores, sandboxing, usuarios de bajo privilegio y límites de egress de red reducen el radio de explosión.

5. **Logueá las invocaciones de comandos y rechazá metacaracteres sospechosos.**
   El logging ayuda a la detección, pero el filtrado es secundario a evitar la interpretación del shell.

### Qué no funciona como defensa primaria

- **Hacer blacklist de unos pocos caracteres.** La sintaxis del shell tiene muchos separadores, encodings y diferencias de plataforma.
- **Escapar sin entender el shell.** Las reglas de escaping varían y son fáciles de aplicar mal.
- **Ocultar la salida.** La inyección ciega igual puede usar timing o callbacks.
- **Firmas de WAF.** La frontera peligrosa es la construcción del comando del lado del servidor.

## Labs prácticos
Usá solo labs locales o targets intencionalmente vulnerables.

### Encontrar sinks de ejecución de comandos

```bash
rg -n "exec\\(|spawn\\(|system\\(|popen\\(|Runtime\\.getRuntime|ProcessBuilder|subprocess" src
```

Revisá si el input del usuario llega al sink.

### Testear el comportamiento de separadores benigno

```bash
curl -i 'https://app.example.test/ping?host=127.0.0.1%3Bid'
```

Corré solo contra labs propios.

### Testear timing ciego de forma segura

```bash
curl -w "%{time_total}\n" -o /dev/null -s 'https://app.example.test/ping?host=127.0.0.1%3Bsleep%205'
```

Las diferencias de timing pueden indicar ejecución cuando no se muestra salida.

## Ejemplos prácticos
- Una página de diagnóstico de red hace shell-out a `ping`.
- Una feature de conversión de PDF pasa nombres de archivo a través de un shell.
- Un endpoint de backup construye comandos `tar` a partir de datos de la request.
- Un procesador de imágenes acepta argumentos que se vuelven flags del comando.
- Un webhook de Git invoca comandos de shell con nombres de branch.

## Notas relacionadas
- [[sql-injection|Inyección SQL]]
- [[ssrf|SSRF]]
- [[path-traversal|Path traversal]]
- [[file-upload-abuse|Abuso de subida de archivos]]
- [[cybersecurity/offensive-security/recon-to-testing-handoff|Traspaso de recon a testing]]

### Notas atómicas futuras sugeridas
- [[blind-command-injection|Inyección de comandos ciega]]
- [[argument-injection|Inyección de argumentos]]
- [[shell-metacharacters|Metacaracteres del shell]]
- [[safe-process-execution|Ejecución segura de procesos]]
- [[out-of-band-command-injection|Inyección de comandos out-of-band]]

## Referencias
- **Foundational:** OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OS command injection — https://portswigger.net/web-security/os-command-injection
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
