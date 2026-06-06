# RustScan and NSE Pipeline

## Definición

El pipeline RustScan + NSE es un flujo de trabajo en dos etapas en el que RustScan realiza un descubrimiento de puertos asíncrono y rápido sobre un objetivo y pasa la lista de puertos descubiertos directamente a Nmap, que luego maneja el Nmap Scripting Engine (NSE) para detección de servicios, sondeo de versiones y verificaciones de vulnerabilidades con scope acotado por categoría.

## Por qué importa

Correr `nmap -A -p- target` contra un único host puede tardar 10–30 minutos — y la mayor parte de ese tiempo se gasta en puertos que resultaron cerrados. Dividir el trabajo en "descubrí puertos rápido → enumerá puertos en profundidad" corta un scan de rango completo en un único host de minutos a segundos sin perder nada del poder de enumeración de Nmap, porque la etapa profunda corre solo sobre los puertos abiertos.

El framing senior es que este es *el mismo patrón de dos fases que Masscan + Nmap*, simplemente reducido: RustScan reemplaza la capa de descubrimiento masivo para hosts únicos y subredes pequeñas, mientras que Masscan tiene ese mismo rol para trabajo a escala de AS. Entender las categorías de scripts NSE determina si la segunda fase es segura, útil o accidentalmente ruidosa/destructiva.

## Cómo funciona

El pipeline tiene **3 etapas**:

1. **Descubrimiento (RustScan).** El runtime async Tokio abre hasta `--ulimit` sockets half-open concurrentes, barre el conjunto de puertos configurado y emite una lista de puertos abiertos. El aprendizaje adaptivo ajusta el tamaño del batch según los patrones de respuesta tempranos.
2. **Handoff.** Todo lo que va después de `--` en la línea de comando de RustScan se pasa verbatim a Nmap. RustScan invoca a Nmap con `-p <puertos_descubiertos>` y los flags del usuario.
3. **Enumeración (Nmap + NSE).** Nmap corre detección de versión, OS fingerprinting y cualquier script NSE seleccionado sobre los puertos abiertos únicamente.

Ejemplo:

```
rustscan -a target --ulimit 5000 -- -sV -sC --script "default,safe,vuln"
```

Interpretación:
- `--ulimit 5000` sube el límite de file-descriptors para que 5000 puertos puedan probarse concurrentemente.
- Todo lo que va después de `--` es de Nmap: `-sV` (versión), `-sC` (NSE default), `--script "default,safe,vuln"` (Boolean de categoría).
- RustScan exec()a Nmap con `-p <puertos que encontró>` automáticamente. Nmap entonces ignora todos los puertos cerrados que RustScan ya descartó.

El problema que RustScan resuelve *no* está en Nmap; está en *cómo típicamente se usa Nmap* (`-p-` contra un host completo donde 65.500 puertos siempre iban a estar cerrados). El pipeline es una optimización, no un reemplazo.

Las categorías de scripts NSE son la **segunda** parte de la historia senior:

- `auth`, `broadcast`, `brute`, `default`, `discovery`, `dos`, `exploit`, `external`, `fuzzer`, `intrusive`, `malware`, `safe`, `version`, `vuln`.
- Default seguro para engagements: `--script "default,safe"` más selectivamente `discovery` y `version`.
- Agregá `vuln` solo con autorización explícita.
- `intrusive`, `exploit`, `brute`, `dos` requieren consentimiento explícito y una evaluación documentada del blast-radius.

## Técnicas / patrones

- **Dominá el divisor `--`.** Todo lo que va después de `--` es Nmap. Si no podés articular qué hace `-A -sC --script vuln` a nivel de Nmap, RustScan te está ocultando bugs, no ahorrándote tiempo.
- **`--ulimit` ≥ batch size, siempre.** Modo de falla por defecto: RustScan se throttlea al ulimit y silenciosamente reporta `filtered` falsos. `ulimit -n` en el shell y `--ulimit` en el CLI deben concordar.
- **Usá `--scripts None`** cuando solo querés la lista de puertos (por ejemplo, para alimentar un pipeline custom).
- **La selección Boolean de scripts** supera a las listas largas de scripts: `--script "(default or safe) and not (brute or dos)"`.
- **Selectividad NSE por puerto.** `--script "http-*" -p 80,443` corre solo scripts HTTP; evitá traer scripts SMB a puertos HTTP.
- **Los script arguments** son obligatorios para verificaciones `vuln` que necesitan credenciales o paths: `--script-args 'http.useragent="custom",userdb=users.txt'`.
- **Actualizá los scripts NSE** antes de cualquier engagement serio: `nmap --script-updatedb`.
- **Encadenamiento con stdin** para pipelines: `subfinder -d target.com | dnsx -a -resp-only | rustscan -a - -- -sV -sC`.

## Variantes y bypasses

### 1. Scan profundo de host único

`rustscan -a host -r 1-65535 --ulimit 65535 -- -A -sC --script vuln`. El caso de uso original — rango completo de puertos, enumeración completa, en aproximadamente el tiempo que tomaría solo la detección de versión de Nmap.

### 2. Sweep de subred con NSE selectivo

`rustscan -a 10.0.0.0/24 --ulimit 5000 -- -sV --script "(default or safe) and not (brute or intrusive)"`. Descubrimiento a escala de subred con NSE conservador.

### 3. Modo solo lista de puertos

`rustscan -a host --scripts None -g`. Lista de puertos greppable, sin Nmap. Para pipelines custom (Nuclei, scanners custom) que no quieren el overhead de Nmap.

### 4. Enumeración enfocada en HTTP

`rustscan -a host -p 80,443,8080,8443 -- -sV --script "http-title,http-headers,http-methods,http-enum,http-server-header"`. NSE HTTP dirigido sin traer categorías de scripts no relacionadas.

### 5. Categoría vuln autenticada

`rustscan -a host -- -sV --script vuln --script-args "creds.global=user:pass"`. Scripts NSE `vuln` que verifican condiciones solo accesibles autenticado. Requiere scope de engagement explícito autorizando credenciales.

### 6. Scan containerizado

`docker run --rm rustscan/rustscan:latest -a target -- -sV -sC`. El deployment oficial — evita peleas con ulimit del host, reproducible entre operadores.

## Impacto

- **Reducción de 10–100× en wall-clock** vs. `nmap -p- -A` ingenuo.
- **Riesgo operacional si la categoría NSE está mal elegida.** `--script "default"` incluye algunos scripts que envían intentos de autenticación — revisá el contenido de la categoría antes de asumir que "default = seguro".
- **Falsos positivos de NSE `vuln`.** Muchos scripts `vuln` verifican versiones de banners y se pierden parches — cada alerta requiere validación manual antes de reportar.
- **Las categorías `exploit` y `dos` pueden crashear servicios.** Se excluyen de `default` por una razón; optar por incluirlas necesita aprobación de change-management en cualquier engagement que toque producción.
- **Huella de detección.** RustScan + NSE es más ruidoso que Nmap solo — el mismo fingerprint por IP más los probes específicos de los scripts NSE son fácilmente agrupados por reglas de SIEM comportamentales.

## Detección y defensa

1. **Reglas IDS conscientes de NSE.**
   Las firmas Snort/Suricata para los scripts NSE más ruidosos (`http-enum`, `smb-vuln-*`, `ssl-enum-ciphers` contra un cluster cerrado) están disponibles públicamente y bien ajustadas. Los defensores deberían suscribirse.

2. **Rate limits de inspección profunda por puerto.**
   El handoff de RustScan significa que Nmap golpeará un conjunto pequeño de puertos con muchos probes NSE en rápida sucesión. Los rate limits por-puerto-por-fuente en el WAF/IDS capturan esto de manera diferenciada.

3. **Banner shaping de versiones.**
   Muchos scripts `vuln` NSE deciden basándose en strings de versión. Los defensores que eliminan o aleatorizan banners de versión reducen la superficie de falsos positivos en engagements *y* reducen el valor de verdaderos positivos para los atacantes — dos razones para hacerlo.

4. **Honeypots que responden a `http-enum`.**
   Una tabla de paths que devuelve 200 a cada directorio que NSE sondea vuelve inútil el output del script sin afectar a usuarios reales. Defensa asimétrica.

### Qué no funciona como defensa primaria

- **Bloquear la IP fuente de RustScan** — misma trampa que con Masscan: termina su trabajo en segundos.
- **Deshabilitar probes específicos de Nmap** — Nmap controla su biblioteca de probes, no el objetivo.
- **Esperar que los reportes de `--script vuln` sean precisos** — la mayoría son heurísticas de strings de versión. Los defensores no deberían tratar la ausencia de alertas NSE-`vuln` como evidencia de seguridad.

## Labs prácticos

```
# Lab 1 — pipeline baseline contra un host de lab autorizado.
rustscan -a LAB --ulimit 5000 -- -sV -sC --script "default,safe"
# Cronometralo. Compará con `nmap -p- -sV -sC LAB`.
# Esperá reducción de 5–20× en wall-clock.
```

```
# Lab 2 — modo de falla por mismatch de ulimit.
ulimit -n 1024
rustscan -a LAB -b 5000 -- -sV 2>&1 | grep -i ulimit
# Reproduce el error "Too many open files". La solución es `--ulimit 65535` (y el ulimit del shell coincidente).
```

```
# Lab 3 — Boolean de categoría NSE.
nmap --script "(default or vuln) and not (intrusive or dos)" --script-help | head -40
nmap -sV --script "(default or vuln) and not (intrusive or dos)" -p 22,80,443 LAB
# Inspeccioná qué scripts corrieron. Cotejá la lista de categorías con el scope del engagement.
```

```
# Lab 4 — pipeline desde enumeración de subdominios.
subfinder -d target.tld -silent |
  dnsx -a -resp-only -silent |
  rustscan -a - --ulimit 5000 -- -sV --script "default,safe"
# Una sola cadena que va de un dominio a servicios enumerados.
# Correr solo contra scope autorizado.
```

```
# Lab 5 — modo solo lista de puertos para downstream custom.
rustscan -a LAB --scripts None -g
# El output es una línea por host: "10.0.0.5 -> [22,80,443]".
# Pasarlo a Nuclei, gowitness, ffuf, o tooling custom en lugar de Nmap.
```

```
# Lab 6 — actualización NSE y auditoría de scripts.
sudo nmap --script-updatedb
locate nse_main.lua  # encontrar path de scripts
ls $(nmap --script-help default 2>/dev/null | awk '/^Categories:/{exit} {print $1}' | head -5)
# Siempre saber qué contiene `default` antes de afirmar "solo corrí scripts seguros".
```

## Ejemplos prácticos

- **Deep dive en target único de bug bounty.** RustScan + NSE contra un host en scope completa la detección de versión en rango completo en 30–60 segundos en lugar de 15–30 minutos — permitiéndole al operador revisar 10× más targets en una sesión.
- **Superficie de ataque externa manejada por CI.** RustScan + NSE `default,safe` nocturnos contra una lista de subdominios propios, con resultados diff-eados contra la noche anterior. Los puertos/servicios nuevos o cambios de versión disparan una alerta.
- **Pivote red team interno.** Desde un foothold, `rustscan -a internal-subnet/24 --ulimit 5000 -- -sV --script "default,safe and not brute"` encuentra servicios de alto valor (Jenkins, GitLab, Confluence interno) en minutos.
- **Auditoría de workloads cloud.** Desde un scanner controlado dentro de una VPC, RustScan + NSE valida que la exposición de security-groups prevista coincide con la alcanzabilidad real para cada workload.
- **Smoke test previo al engagement.** Antes de arrancar el engagement real, una pasada `--script default,safe` confirma que el tooling funciona end-to-end y produce un baseline de diff.

## Notas relacionadas

- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]
- [[ports-and-services|Ports and Services]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[service-validation|Service Validation]]
- [[active-recon|Active Recon]]
- [[enumeration|Enumeration]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[nse-vuln-category-audit|NSE Vuln Category Audit]]

## Referencias

- **Docs Oficiales:** RustScan repository y docs — https://github.com/RustScan/RustScan
- **Docs Oficiales:** Nmap Scripting Engine — https://nmap.org/book/nse.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
