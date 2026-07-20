# False Positives, False Negatives, and Detection Tradeoffs

## Definición

Los falsos positivos son eventos benignos clasificados como sospechosos; los falsos negativos son eventos maliciosos o relevantes para una política que la detección no identifica.

## Por qué importa

La detección de seguridad es ingeniería estadística y operacional, no verdad binaria. Un detector opera dentro de un entorno real con telemetría desigual, baselines cambiantes, analistas limitados, logs demorados, labels incompletos y adversarios que se adaptan.

"Detectar todo" es imposible. "Sin alerta" no prueba seguridad. Un programa maduro gestiona deliberadamente precision, recall, costo, fatiga de alertas y riesgo residual.

## Cómo funciona

Los tradeoffs de detección son un **sistema de 6 variables**:

1. **Base rate.** Los ataques raros producen muchos falsos positivos cuando el entorno genera enorme volumen benigno.
2. **Precision.** De las alertas que disparan, ¿cuántas son útiles?
3. **Recall.** De los eventos maliciosos que ocurrieron, ¿cuántos fueron detectados?
4. **Thresholds.** Conteos, scores, cortes de rareza y ventanas temporales deciden qué lado del tradeoff se favorece.
5. **Capacidad de triage.** Una detección que excede la capacidad del analista se convierte en una denegación de servicio contra el SOC.
6. **Calidad de feedback.** Sin labels, resultados de incidentes y contexto del entorno, el tuning deriva hacia guesswork.

Ejemplo:

```
Rule: alert when one source contacts more than 20 hosts on 445/tcp in 10 minutes.
High recall: threshold 5, many admin scripts alert.
High precision: threshold 200, slow lateral discovery is missed.
Better: threshold varies by host role, time window, and approved scanner list.
```

La pregunta útil no es "¿este threshold es correcto?", sino "¿qué riesgo y carga de trabajo elige este threshold?"

## Técnicas / patrones

- **Medición de precision/recall.** Rastrear alertas útiles, alertas benignas, incidentes perdidos y near misses.
- **Baselines conscientes de rol.** Tunear por rol fuente, clase de destino, tipo de usuario, subnet, service account, workload cloud y ventana de mantenimiento.
- **Barridos de thresholds.** Testear múltiples thresholds contra datos etiquetados o simulados antes de elegir uno.
- **Ventanas de correlación.** Tunear ventanas temporales según tempo de ataque y ruido del entorno.
- **Higiene de supresión.** Suprimir con owner, razón, expiración y señal compensatoria.
- **Calibración de severidad.** La severidad debería reflejar impacto, confianza, criticidad del asset y urgencia de respuesta, no ansiedad del autor de la regla.

## Perspectiva del atacante

Los atacantes explotan la presión de falsos positivos. Se mezclan con patrones admin ruidosos, operan lento, usan herramientas comunes, disparan detecciones de bajo valor para desensibilizar analistas o actúan durante ventanas de cambio.

También explotan gaps de falsos negativos: subnets no monitoreadas, endpoints no gestionados, flow sampleado, logging deshabilitado, servicios cloud sin audit logs o detecciones tuneadas demasiado estrechamente después de incidentes ruidosos.

## Perspectiva del defensor

Los defensores deben decidir qué errores son aceptables. Una detección ruidosa sobre credential dumping en domain controllers puede valer tuning lento. Una detección ruidosa sobre comportamiento común del navegador puede necesitar supresión o rediseño. Un falso negativo en exfiltración puede costar más que diez alertas benignas, pero mil alertas benignas pueden esconder el evento real.

## Tradeoffs de detección e ingeniería

1. **Recall vs precision.**
   Las detecciones amplias capturan más variantes pero crean más trabajo de triage. Las estrechas reducen trabajo pero pierden adaptación.

2. **Ventanas cortas vs largas.**
   Las cortas capturan bursts y reducen joins no relacionados. Las largas capturan comportamiento lento pero elevan riesgo de falsa correlación.

3. **Thresholds globales vs baselines locales.**
   Las reglas globales son portables. Los baselines locales son más precisos pero requieren ownership y mantenimiento.

4. **Supresión vs ceguera.**
   La supresión protege analistas del ruido pero puede ocultar ataques futuros que reutilicen el path suprimido.

5. **Inflación de severidad vs confianza.**
   No todo puede ser high severity. La severidad inflada entrena a los analistas a ignorar severidad.

## Detección y defensa

Ordenado por efectividad:

1. **Definí el costo de ambos tipos de error.**
   Un falso positivo cuesta tiempo y confianza del analista. Un falso negativo cuesta dwell time, scope e impacto de incidente. El costo relativo cambia por técnica y clase de asset.

2. **Medí resultados de alertas.**
   Rastreá labels de true positive, benign true positive, false positive, duplicado, unresolved e incidentes perdidos. Tunear sin outcomes es vibes.

3. **Tuneá por rol de entidad.**
   Hosts scanner, jump boxes admin, máquinas de developers, servidores de producción, service accounts y workstations de usuarios necesitan thresholds distintos.

4. **Usá severidad escalonada.**
   Las señales únicas débiles pueden ser baja severidad hasta unirse con comportamiento adicional, criticidad de asset o riesgo de identidad.

5. **Revisá supresiones como deuda técnica.**
   Toda supresión debería tener owner, expiración, justificación y monitoreo alternativo si el riesgo permanece.

### Qué no funciona como defensa primaria

- **"Detectar todo."** Recall ilimitado crea ruido ilimitado e igual pierde gaps de telemetría.
- **Allowlists permanentes.** Se convierten silenciosamente en puntos ciegos a medida que assets y usuarios cambian.
- **Un threshold para todos los assets.** Ignora rol, baseline y función de negocio.
- **Severidad como motivación.** Marcar todo como crítico no acelera la respuesta; destruye priorización.
- **Cerrar por ausencia de alerta.** La ausencia de alerta solo significa algo si se conoce la cobertura de telemetría y detección.

### Malentendidos operacionales

- **"Los falsos positivos son solo malas reglas."** Algunos son inevitables porque comportamiento benigno y malicioso se superponen.
- **"Los falsos negativos son solo firmas perdidas."** Muchos son telemetría faltante, malos joins, gaps de retención o supuestos de scope.
- **"Tunear significa suprimir ruido."** Tunear puede significar agregar contexto, cambiar ventanas, dividir detecciones, mejorar enrichment o pasar a correlación.
- **"Más datos siempre mejora accuracy."** Más datos ruidosos o no normalizados pueden reducir accuracy.

### Limitaciones modernas

- Los labels son incompletos: muchas alertas nunca son concluyentemente true o false.
- Logs cloud y SaaS pueden llegar tarde, haciendo incompletos los thresholds en tiempo real.
- Los baselines derivan con despliegues, trabajo remoto, autoscaling y ciclos de negocio.
- Los adversarios eligen deliberadamente comportamientos parecidos a administración.

### Puntos ciegos de telemetría

- Logs deshabilitados o demorados durante el evento.
- Ejemplos negativos faltantes para training/tuning.
- Deduplicación de eventos que oculta comportamiento repetido.
- Retención corta que impide análisis de incidentes perdidos.
- Logs cloud agregados que colapsan detalle de eventos.

## Labs prácticos

Usá datos locales generados.

### Lab 1 - Tunear un threshold ruidoso

Objetivo: Observar tradeoffs precision/recall.

```
cat > /tmp/scan-labels.csv <<'EOF'
source,distinct_hosts,label
scanner-approved,250,benign
admin-script,35,benign
dev-laptop,28,benign
compromised-1,42,malicious
compromised-2,12,malicious
db-server,8,malicious
EOF
for t in 5 10 20 40 100; do
  awk -F, -v t=$t 'NR>1 {alert=($2>t); if(alert&&$3=="malicious") tp++; if(alert&&$3=="benign") fp++; if(!alert&&$3=="malicious") fn++} END {print "threshold",t,"TP",tp+0,"FP",fp+0,"FN",fn+0}' /tmp/scan-labels.csv
done
```

Telemetría esperada: thresholds bajos capturan más filas maliciosas pero crean más alertas benignas. Thresholds altos pierden ataques lentos o más chicos. Los defensores tunearían por rol en vez de elegir un número global. Malentendido corregido: "el threshold perfecto existe."

### Lab 2 - Testear deuda de supresión

Objetivo: Mostrar cómo una allowlist puede ocultar compromiso posterior.

```
cat > /tmp/suppressions.csv <<'EOF'
entity,reason,expires
scanner-approved,monthly vuln scan,2026-06-01
admin-script,legacy maintenance,never
EOF
cat > /tmp/events.csv <<'EOF'
source,distinct_hosts,label
admin-script,120,malicious
scanner-approved,250,benign
EOF
awk -F, 'NR==FNR {s[$1]=$3; next} {print $0,"suppression_expires="s[$1]}' /tmp/suppressions.csv /tmp/events.csv
```

Telemetría esperada: una supresión sin expiración oculta riesgo. Limitación: los sistemas reales necesitan owner y contexto de cambio. Malentendido corregido: "allowlist equivale a resuelto."

## Ejemplos prácticos

- Un detector de scans es ruidoso en vulnerability scanners pero de alto valor en servidores de base de datos.
- Una regla de PowerShell se vuelve útil recién después de excluir jump hosts admin aprobados y agregar parentage sospechoso.
- Una anomalía de API cloud dispara en cada deploy hasta que se agregan ventanas de release y roles de service account.
- Una categoría de alerta high severity pierde confianza del analista porque la mayoría de alertas son ruido de policy de bajo impacto.

## Notas relacionadas

- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[gmsa-and-modern-service-account-hardening|gMSA and Modern Service Account Hardening]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]

### Notas atómicas futuras sugeridas

- precision-and-recall-for-security-detections
- suppression-debt
- severity-calibration
- detection-regression-testing

## Referencias

- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Fundamental:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Investigación / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Fundamental:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/
