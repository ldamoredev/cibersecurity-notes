# NSE `vuln` Category Audit

## Definición

La categoría `vuln` del Nmap Scripting Engine contiene aproximadamente **150 scripts** que afirman detectar vulnerabilidades. No todos son iguales: algunos son verificaciones conductuales confiables, muchos son heurísticas de strings de versión, y unos pocos están directamente obsoletos. Auditar la categoría — saber qué scripts producen señal confiable en 2026, cuáles requieren confirmación manual y cuáles deshabilitar — es la disciplina que convierte "corrí `--script vuln` y obtuve 50 alertas" en "produje 4 hallazgos validados".

## Por qué importa

El uso por defecto del operador es `nmap -sV --script vuln target`. El output parece impresionante — páginas de bloques `VULNERABLE:`. Los operadores junior los pegan en los reportes. Los operadores senior reconocen que **la mayoría del output del script `vuln` es ruido heurístico no validado**: comparaciones de strings de versión contra firmas que eran válidas hace cinco años, contra software que desde entonces fue parcheado in-place por el vendor sin cambiar el string del banner.

La categoría también importa como nota educativa porque concretiza tres ideas transferibles de nivel senior:

- **Una vulnerabilidad no es un hallazgo.** Una *vulnerabilidad* es "esta versión de software tuvo un CVE". Un *hallazgo* es "confirmé que esta instancia es explotable en este entorno". NSE `vuln` produce lo primero; el trabajo del operador es la conversión.
- **La detección por heurística de banner es el nivel más bajo en la Pirámide del Dolor de Bianco.** Se bypasea trivialmente vía banner shaping — y muchos stacks de producción configuran banners como hardening estándar.
- **El output de la herramienta es un input al razonamiento, no el razonamiento.** Cada hallazgo NSE `vuln` merece un paso de validación manual antes de convertirse en contenido de reporte.

## Cómo funciona

Los scripts NSE `vuln` se agrupan en **4 tiers de detección** por confiabilidad, y una auditoría senior asigna cada script usado a un tier explícitamente:

1. **Conductual / basado en probe (alta confiabilidad).** El script envía una request elaborada a la que *solo un objetivo vulnerable responde* y observa la response. Ejemplos: `smb-vuln-ms17-010`, `ssl-poodle`, `http-shellshock`. Estos producen hallazgos, no heurísticas.

2. **Autenticado / state-aware (alta confiabilidad).** El script se autentica al servicio y consulta el estado real. Menos común en scans externos no autenticados pero de alta señal cuando el scope lo permite.

3. **Heurísticas de banner de versión (baja confiabilidad — el grueso de la categoría).** El script lee el banner de versión del servicio y compara contra una tabla de CVEs. **Modos de falla:** (a) las defensas de banner shaping producen falsos negativos, (b) los vendors backportean parches sin cambiar el banner produciendo falsos positivos, (c) la tabla de CVEs en el script es de cuando el script fue actualizado por última vez.

4. **Obsoleto / deprecado (no confiar).** Scripts que verifican CVEs suficientemente viejos como para que cualquier instancia no parcheada fue parcheada, desmantelada o ya comprometida hace mucho. Ejemplos: muchos `http-vuln-cve2010-*`, `http-vuln-cve2011-*`.

Un flujo de auditoría representativo:

```
# 1) Enumerate vuln-category scripts on the host.
nmap --script-help "vuln" | grep -E '^[a-z]' | head -40

# 2) Filter by date of last-update if maintained (not all scripts have it).
ls /usr/share/nmap/scripts/ | grep -E 'vuln|cve' | xargs -I{} stat -f "%Sm %N" /usr/share/nmap/scripts/{} 2>/dev/null |
    sort | head -20

# 3) Pick a tighter Boolean than just `vuln`.
nmap -sV --script "vuln and not (http-vuln-cve2010-* or http-vuln-cve2011-*)" target
```

## Técnicas / patrones

- **Siempre pará `--script vuln` con `-sV`.** Muchos scripts `vuln` se condicionan en la detección de versión. Sin `-sV`, los scripts se saltean silenciosamente y te perdés hallazgos reales.
- **Usá expresiones Boolean para acotar el scope.** `--script "vuln and (http-* or ssl-*)"` corre solo scripts vuln de HTTP y SSL. Más tranquilo, más rápido, más fácil de triar.
- **Actualizá NSE antes de cada engagement.** `sudo nmap --script-updatedb`. Los scripts y sus tablas de CVEs se actualizan.
- **Tratá cada bloque `VULNERABLE:` como una hipótesis.** El próximo movimiento del operador es verificación manual.
- **Deshabilitá scripts que consistentemente producen falsos positivos.** `--script "vuln and not http-cookie-flags and not http-csrf"` para engagements donde estos scripts ya probaron ser poco confiables.
- **`--script-args` es obligatorio para algunos scripts.** `smb-vuln-*` acepta `smbport=`, `unsafe=1` (correr probes peligrosos), credenciales.
- **La estrategia de dos pasadas supera a una sola.** Primera pasada: `--script "vuln" -sV` para enumerar hipótesis. Segunda pasada: herramienta de confirmación manual por hipótesis.

## Variantes y bypasses

La auditoría NSE `vuln` se divide en **3 patrones de uso**, cada uno con diferentes características de evasión de defensor.

### 1. Primera pasada de descubrimiento masivo

`nmap -sV --script "vuln" -iL hosts.txt -oA vuln-scan`. Ruidoso. Detectado por firmas IDS orientadas a patrones de probe NSE específicos.

### 2. Pasada con scope acotado dirigido

`nmap -sV --script "vuln and (http-* or ssl-*)" -p 80,443,8080,8443 target`. Más tranquilo. Patrón estándar de engagement.

### 3. Pasada de verificación de script único

`nmap -p 445 --script smb-vuln-ms17-010 --script-args smbport=445 target`. El tercer paso en el pipeline de validación — correr solo el script que confirma o refuta una hipótesis específica.

## Impacto

Ordenado por severidad real típica (del *mal uso*, ya que la técnica en sí es defensiva):

- **Reportes de engagement rechazados por revisores.** Presentar output crudo de `vuln` sin validación es una forma confiable de que los hallazgos sean rebajados o eliminados.
- **Costo de triage de falsos positivos del lado defensor.** Un defensor que trata cada alerta NSE `vuln` como real pasa la mayor parte del tiempo en hipótesis que no existen en su entorno.
- **Falsos negativos enmascarados como "sin hallazgo".** Un scan con scripts obsoletos o incorrectos produce un reporte *limpio* que se pierde la exposición real.
- **La dependencia excesiva en herramientas enmascara la brecha de habilidad del engagement.**

## Detección y defensa

Esta nota es inusual: el framing de "detección y defensa" aplica más a la **disciplina de auditoría del operador** que a un control del lado del objetivo:

1. **Adoptá la disciplina de dos pasadas como regla dura.**
   Primera pasada: categoría `vuln` como generador de hipótesis. Segunda pasada: confirmación manual por hallazgo.

2. **Mantené un allowlist de scripts por engagement.**
   No corras `--script vuln` ciegamente. Mantené una lista escrita de scripts que produjeron señal confiable contra el stack tecnológico del objetivo.

3. **Actualizá NSE antes de cada engagement.**
   `sudo nmap --script-updatedb` es barato y reduce la tasa de falsos positivos de manera medible.

4. **Para el lado defensor: dar forma a banners y publicar versiones estratégicamente.**
   La misma debilidad de heurística de banner que hace poco confiables los resultados de `vuln` para los atacantes es la palanca que usan los defensores.

### Qué no funciona como defensa primaria

- **Deshabilitar scripts NSE específicos del lado del objetivo.** No se puede — el operador elige qué scripts correr.
- **Confiar en "sin output vuln" como evidencia de seguridad.** Los falsos negativos son comunes.
- **Confiar en un bloque `VULNERABLE:` como hallazgo listo para reportar.** Es una hipótesis. Validar antes de reportar.

## Labs prácticos

```
# Lab 1 — Inventory the vuln category your installation ships.
nmap --script-help "vuln" 2>/dev/null | grep -E '^http-|^ssl-|^smb-|^smtp-|^ftp-' | sort -u | wc -l
nmap --script-help "vuln" 2>/dev/null | grep -E '^[a-z]' | head -30
```

```
# Lab 2 — Run the first pass with a conservative Boolean against an authorized lab.
sudo nmap -sV --script "(default or vuln) and not (intrusive or dos or brute)" \
     -p 21,22,80,443,3306,3389,5432 -oA pass1 LAB_TARGET
# Review pass1.nmap for VULNERABLE: blocks. Each is a hypothesis.
```

```
# Lab 3 — Build a reliability table for what you found.
grep -B1 "VULNERABLE:" pass1.nmap | grep -E "^\| [a-z-]+:" | sort -u
# For each script in the output, classify:
#   - Behavioral probe? (high reliability)
#   - Version-banner only? (low reliability)
#   - Authenticated? (high reliability, scope-dependent)
#   - Stale? (do not trust)
```

```
# Lab 4 — Single-script verification on one finding.
sudo nmap -p 445 --script smb-vuln-ms17-010 -d LAB_TARGET
# The -d flag shows the probe traffic.
```

```
# Lab 5 — Inspect a stale script.
cat /usr/share/nmap/scripts/http-vuln-cve2010-2861.nse | head -30
# Old CVE. Check the last-modified date.
```

## Ejemplos prácticos

- **Triage en bug bounty.** El operador presenta un reporte citando `http-vuln-cve-2017-5638` (Struts2) basado en output NSE crudo. El triager rechaza: el objetivo está en una versión parcheada. El paso de validación omitido le costó el reporte.
- **Agotamiento del presupuesto de ruido del engagement.** El operador corre `--script vuln` contra un /16, genera 8.000 hits de hipótesis, el SOC defensor alerta en 90 segundos. Boolean dirigido (`vuln and ssl-*`) en un /24 produce 40 hipótesis, de las cuales 12 se validan.

## Notas relacionadas

- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]
- [[attacker-defender-duality-as-a-learning-tool|Dualidad Atacante-Defensor como Herramienta de Aprendizaje]]

## Referencias

- **Docs Oficiales:** Nmap Scripting Engine — Categories — https://nmap.org/book/nse-usage.html#nse-categories
- **Docs Oficiales:** NSE script library — `vuln` category index — https://nmap.org/nsedoc/categories/vuln.html
- **Investigación / Deep Dive:** David Bianco — The Pyramid of Pain — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html
