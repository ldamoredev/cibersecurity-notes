# Attack Path Correlation and Kill Chain Observability

## Definición

La correlación de attack paths es la detección y reconstrucción de relaciones entre eventos a lo largo de una secuencia adversaria, como recon, explotación, persistencia, escalada de privilegios, movimiento lateral, recolección y exfiltración.

## Por qué importa

La detección moderna suele detectar relaciones entre eventos, no eventos aislados. Un único login fallido, scan, lanzamiento de PowerShell, llamada a una API cloud o conexión TLS saliente puede ser débil. La secuencia puede ser decisiva.

Los modelos de kill chain y ATT&CK son útiles porque obligan a los defensores a preguntarse cómo un evento cambia el significado de otro. Son limitados porque los ataques reales hacen loops, saltean etapas, usan workflows legítimos y cruzan límites de identidad, endpoint, red, cloud y SaaS.

## Cómo funciona

La observabilidad de attack paths usa **6 capas de correlación**:

1. **Mapeo de etapas.** Agrupar eventos por propósito: recon, acceso inicial, ejecución, persistencia, escalada de privilegios, evasión de defensas, acceso a credenciales, discovery, movimiento lateral, recolección, exfiltración.
2. **Costura de entidades.** Rastrear usuarios, dispositivos, árboles de procesos, IPs, sesiones, recursos cloud, tokens y service accounts.
3. **Correlación por ventana temporal.** Vincular señales débiles dentro de un tempo de ataque plausible.
4. **Joins multisensor.** Combinar EDR, Zeek, Suricata, NetFlow, identidad, cloud, proxy, DNS, aplicación y datos de tickets/cambios.
5. **Razonamiento de grafo.** Modelar relaciones: user -> host -> process -> destination -> credential -> cloud role -> data store.
6. **Reconstrucción de timeline.** Construir una cadena cronológica de evidencia que explique qué pasó y qué sigue incierto.

Ejemplo:

```
09:00 external scan finds /admin
09:12 web exploit probe returns 500
09:14 web process launches shell
09:16 host contacts metadata endpoint
09:22 new cloud API calls enumerate storage
09:40 unusual egress to external host
```

Ningún evento por sí solo prueba todo el incidente. El path sí.

## Técnicas / patrones

- **Acumulación de señales débiles.** Elevar combinaciones que solas son de baja severidad pero juntas tienen alto significado.
- **Encadenamiento de alertas.** Conectar alertas por host, usuario, proceso, IP, recurso cloud o sesión compartida.
- **Seguimiento de pivots de identidad.** Seguir el uso de cuentas a través de hosts, VPN, cloud, SaaS y acciones privilegiadas.
- **Timelines de linaje de procesos.** Rastrear cadenas padre-hijo y efectos laterales de red/archivo.
- **Detección basada en grafos.** Detectar recorridos inusuales por grafos de identidad, red, host y acceso a datos.
- **Mapeo de cobertura de kill chain.** Identificar qué etapas tienen telemetría y cuáles están ciegas.

## Perspectiva del atacante

Los atacantes piensan en paths. Pueden empezar con recon, explotar un servicio, obtener credenciales, moverse lateralmente, escalar privilegios, persistir, recolectar y exfiltrar. También hacen loops: un exploit fallido lleva a más recon; credenciales descubiertas abren paths nuevos; la identidad cloud cambia la ruta.

Intentan romper la correlación estirando el tiempo, cambiando cuentas, moviéndose por infraestructura compartida, usando herramientas legítimas y cruzando límites de telemetría.

## Perspectiva del defensor

Los defensores necesitan reconstruir paths bajo incertidumbre. Un buen programa de detección no requiere que cada etapa dispare. Acumula señales débiles y le da al analista un timeline, entidades, evidencia faltante y pivots siguientes.

## Tradeoffs de detección e ingeniería

1. **Precisión de evento único vs recall de secuencia.**
   Los eventos únicos pueden ser precisos pero perder cadenas lentas. Las secuencias capturan más pero arriesgan joins falsos.

2. **Ventanas cortas vs dwell time del atacante.**
   Las ventanas cortas reducen ruido; las largas capturan tempos de ataque realistas.

3. **Riqueza de grafo vs complejidad operacional.**
   Los modelos de grafo revelan paths pero requieren fuerte resolución de entidades y calidad de datos.

4. **Modelos de etapa vs ataques reales.**
   Kill chains y ATT&CK ayudan a estructurar el pensamiento, pero los atacantes no obedecen un orden limpio.

5. **Automatización vs criterio del analista.**
   El chaining automatizado puede priorizar, pero los analistas deben validar causalidad y scope.

## Detección y defensa

Ordenado por efectividad:

1. **Definí los attack paths que vale la pena detectar.**
   Empezá con paths de alto riesgo: exploit público a shell, phishing a abuso de token, scan interno a movimiento lateral, metadata cloud a acceso a storage.

2. **Instrumentá joins antes de escribir reglas de cadena.**
   La correlación necesita usuarios, hosts, process IDs, cloud IDs, flow IDs, timestamps y contexto de assets estables.

3. **Usá señales débiles como componentes de cadena.**
   Las alertas de baja confianza se vuelven útiles cuando preceden o siguen comportamiento relacionado.

4. **Construí salidas tipo timeline.**
   Las detecciones deberían producir evidencia legible para un analista: eventos ordenados, entidades, confianza, gaps y pivots recomendados.

5. **Testeá contra paths simulados.**
   Usá logs generados o ejercicios de lab para verificar si cada etapa es observable y si la cadena dispara.

### Qué no funciona como defensa primaria

- **Solo detección de evento único.** Muchos ataques parecen benignos evento por evento.
- **Orden rígido de kill chain.** Las intrusiones reales hacen loops, saltean etapas y paralelizan.
- **Mapeo ATT&CK sin telemetría.** Los nombres de técnicas no crean visibilidad.
- **Graph analytics con malos joins de identidad.** Los joins incorrectos producen narrativas falsas convincentes.
- **Ignorar etapas faltantes.** Un timeline parcial debería nombrar gaps de telemetría en vez de fingir certeza.

### Malentendidos operacionales

- **"Una alerta equivale a un incidente."** Los incidentes suelen ser clusters de eventos.
- **"Sin alerta de exploit significa sin compromiso."** El acceso inicial puede haberse perdido mientras el comportamiento posterior es visible.
- **"Kill chain significa lineal."** Es un modelo de pensamiento, no una ley física del ataque.
- **"La detección por grafo es contexto automático."** Los grafos son tan buenos como la resolución de entidades y los timestamps.

### Limitaciones modernas

- Los logs de cloud, SaaS, endpoint y red tienen distintos delays e identificadores.
- Los dwell times largos desafían la retención y las ventanas de correlación.
- Los atacantes usan identidades y herramientas admin legítimas, creando paths ambiguos.
- Las restricciones de privacidad y costo pueden limitar la reconstrucción completa del timeline.

### Puntos ciegos de telemetría

- Logs de identidad faltantes, ausencia de cobertura de endpoint, sin visibilidad east-west, retención corta.
- Sin process IDs o cloud resource IDs estables.
- Colapso por NAT/proxy que oculta la identidad fuente.
- Logs de auditoría SaaS que omiten detalle del objeto de datos.
- Clock skew entre sensores.

## Labs prácticos

Usá solo datos de timeline generados.

### Lab 1 - Reconstruir un timeline de ataque

Objetivo: Construir una secuencia desde logs simulados.

```
cat > /tmp/attack-path.jsonl <<'EOF'
{"ts":"2026-05-11T09:00:00Z","stage":"recon","entity":"198.51.100.10","event":"scan /admin on web-1"}
{"ts":"2026-05-11T09:12:00Z","stage":"exploit","entity":"web-1","event":"POST /upload returns 500 then web process spawns sh"}
{"ts":"2026-05-11T09:16:00Z","stage":"credential_access","entity":"web-1","event":"curl 169.254.169.254 metadata token"}
{"ts":"2026-05-11T09:22:00Z","stage":"discovery","entity":"cloud-role-web","event":"ListBuckets and GetCallerIdentity"}
{"ts":"2026-05-11T09:40:00Z","stage":"exfiltration","entity":"cloud-role-web","event":"large object reads then external upload"}
EOF
jq -r '[.ts,.stage,.entity,.event] | @tsv' /tmp/attack-path.jsonl | sort
```

Telemetría esperada: el timeline muestra un path desde recon hasta acceso a datos cloud. Los defensores observarían relaciones entre etapas, no solo eventos aislados. Limitación: la causalidad simulada debe validarse en logs reales. Malentendido corregido: "las alertas únicas son suficientes."

### Lab 2 - Encadenar señales débiles por entidad

Objetivo: Mostrar acumulación de señales débiles.

```
cat > /tmp/weak-signals.jsonl <<'EOF'
{"host":"web-1","signal":"rare 500 after upload","score":1}
{"host":"web-1","signal":"web process spawned shell","score":3}
{"host":"web-1","signal":"metadata endpoint access","score":3}
{"host":"web-1","signal":"new cloud API sequence","score":2}
{"host":"dev-1","signal":"single 404 on admin path","score":1}
EOF
jq -s 'group_by(.host)[] | {host:.[0].host,total:(map(.score)|add),signals:map(.signal)} | select(.total>=5)' /tmp/weak-signals.jsonl
```

Telemetría esperada: las señales débiles se vuelven de alta prioridad cuando se acumulan en una entidad. Limitación: el scoring debe calibrarse. Malentendido corregido: "baja severidad significa ignorar."

## Ejemplos prácticos

- Scan externo seguido de intentos de exploit y spawn de shell por EDR en el mismo servidor web.
- Login VPN desde geografía inusual seguido de discovery SMB interno y cambios de grupos privilegiados.
- Acceso a metadata cloud seguido de nueva enumeración de storage y lecturas grandes de objetos.
- Click de phishing seguido de OAuth consent, creación de regla de mailbox y forwarding externo.
- Scan de Nmap seguido de paths de exploit específicos de versión desde el mismo linaje de proceso.

## Notas relacionadas

- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y tradeoffs de detección]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[golden-ticket-and-krbtgt-compromise|Golden Ticket and KRBTGT Compromise]]
- [[krbtgt-rotation-and-tier-zero-recovery|KRBTGT Rotation and Tier Zero Recovery]]
- [[active-recon|Active Recon]]
- [[run-scan-pipeline|Ejecutar pipeline de scan externo de recon]]

### Notas atómicas futuras sugeridas

- attack-graph-detection
- identity-pivot-tracking
- timeline-reconstruction-for-incident-response
- weak-signal-correlation

## Referencias

- **Fundamental:** MITRE ATT&CK Tactics - https://attack.mitre.org/tactics/enterprise/
- **Fundamental:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Investigación / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
