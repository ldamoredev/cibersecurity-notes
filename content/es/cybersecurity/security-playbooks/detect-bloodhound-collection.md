# Detectar la recolección de BloodHound

> _Estructura de playbook (Objetivo / Supuestos / Prerrequisitos / Pasos de detección / Pistas de validación / Mitigación / Logging / Seguridad operativa), matcheando a los hermanos del trío [[cybersecurity/security-playbooks/detect-kerberoasting-and-as-rep-roasting|Detectar Kerberoasting y AS-REP Roasting]] y [[cybersecurity/security-playbooks/detect-dcsync-and-ntdsdit-access|Detectar DCSync y acceso a NTDS.dit]] — no la plantilla de nota atómica de 11 secciones. Esta es la tercera de las tres notas del trío de detección de AD._

## Objetivo
Detectar la enumeración de Active Directory por colectores de la familia BloodHound ([[cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis|SharpHound / BloodHound-CE]] y sucesores como SOAPHound) lo suficientemente temprano como para identificar el **host de origen, el principal de origen y el método de recolección** antes de que el operador convierta el grafo de ataque resultante en una cadena Kerberoast → DCSync → Domain Admin — y con suficiente fidelidad como para sobrevivir a las evasiones realistas de 2026 (LDAP paginado/throttleado, recolección DCOnly, abuso de AD Web Services, colectores custom en memoria).

## Supuestos
- recolectás telemetría de Domain Controller (eventos de Windows Security y/o datos del sensor de Microsoft Defender for Identity) en un SIEM con ≥ 30 días de retención
- podés desplegar al menos un objeto honeytoken (un usuario o computadora señuelo con ACLs de apariencia atractiva que ningún proceso legítimo lee nunca)
- el objetivo es **detectar, contener, investigar** — la recolección es reconocimiento, no explotación; estás corriendo una carrera contra el *próximo* paso del operador, no parcheando un bug
- la recolección de BloodHound frecuentemente es una actividad *legítima* de blue-team / IAM en tu entorno — así que la detección debe distinguir corridas de inventario autorizadas del recon adversario, lo que hace obligatoria una allowlist de hosts/cuentas de colectores sancionados

## Prerrequisitos
- **Visibilidad de queries LDAP.** O bien Defender for Identity (que modela el reconocimiento LDAP nativamente) o el logging diagnóstico de LDAP de Directory Service (Evento **1644**, gateado detrás del diagnóstico de registro `Field Engineering` / `15 Field Engineering` y los umbrales `Expensive/Inefficient`) en los DCs. El 1644 crudo es de alto volumen — preferí Defender for Identity o ETW donde esté disponible.
- **Visibilidad SAMR / SRVSVC.** Evento **4661** (se pidió un handle a un objeto SAM/DS) con el SACL correcto, más **5145** (acceso a share de red / named-pipe `\srvsvc`, `\samr`) para enumeración de sesiones/grupos locales. Ver [[cybersecurity/detection-engineering/windows-event-logs|Windows Event Logs]] para las precondiciones de audit-policy.
- **Telemetría de endpoint.** [[cybersecurity/detection-engineering/edr-network-observability-and-process-correlation|EDR / Sysmon]] para linaje de procesos, carga de assembly .NET (SharpHound es C#), y **fan-out de conexiones salientes** (la recolección Session/LoggedOn pega en muchos hosts).
- **Visibilidad de AD Web Services (ADWS).** Logging de conexiones al TCP **9389** en los DCs — el camino de evasión de SOAPHound que bypassea la detección de LDAP por puerto 389.
- **Una baseline** de quién realiza legítimamente lecturas directory-wide (tooling de IAM, escáneres de vuln, las propias corridas de BloodHound del blue team) y desde qué hosts.

## Pasos de detección

> _Este playbook es el par defensivo de [[cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis|Análisis de rutas de ataque con BloodHound]]. Leé ofensa + defensa juntas según la [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|disciplina de lectura emparejada]]. La recolección de BloodHound es el **recon** que precede a las etapas de [[cybersecurity/security-playbooks/detect-kerberoasting-and-as-rep-roasting|roasting]] y [[cybersecurity/security-playbooks/detect-dcsync-and-ntdsdit-access|DCSync]] — correlacioná a través de las tres._

### Fase 0 — Baseline y señuelos (hacelo una vez, refrescá trimestralmente)
1. **Hacé allowlist de los colectores sancionados.** Registrá los hosts/cuentas que legítimamente enumeran el directorio (IAM, escáneres, BloodHound del blue-team). Todo lo que esté fuera de esta lista leyendo el directorio entero es sospechoso.
2. **Plantá objetos honeytoken.** Creá un usuario y una computadora señuelo que *parezcan* privilegiados (membresía de grupo atractiva, un ACL jugoso, un SPN) pero que nadie usa. La recolección ACL/Default de SharpHound lee el `ntSecurityDescriptor` de cada objeto — así que cualquier lectura del security descriptor del señuelo, o cualquier TGS/auth contra él, es actividad adversaria por construcción. Esta es la señal de mayor fidelidad y casi-cero-FP del playbook.
3. **Baselineá la forma de query LDAP por principal.** Las apps normales consultan rebanadas *angostas* (unos pocos objetos, atributos específicos). BloodHound consulta rebanadas *amplias*: todos los objetos `user`/`computer`/`group` con el set de atributos relevantes para ACL (`ntSecurityDescriptor`, `member`, `memberOf`, `servicePrincipalName`, `userAccountControl`, `msDS-AllowedToActOnBehalfOfOtherIdentity`).

### Fase 1 — Detectar la firma de recolección
Firma del operador: **un principal de origen lee una sección transversal grande y ACL-pesada del directorio en una ventana corta, a menudo seguida de un fan-out SAMR/SRVSVC a muchos hosts.**

1. **Lectura / auth del honeytoken (máxima fidelidad).** Cualquier lectura LDAP del security descriptor del objeto señuelo, o cualquier autenticación a la cuenta señuelo, es severidad alta inmediata. Sin falsos positivos por diseño.
2. **Alertas de reconocimiento de Defender for Identity.** Aflorá y tuneá *Security principal reconnaissance (LDAP)*, *User and Group membership reconnaissance (SAMR)* y *Network mapping / user-and-IP reconnaissance (SMB)*. Estas son hechas a propósito y de mucho menor FP que las reglas de eventos crudos.
3. **Regla conductual de broad-LDAP.** Alertá cuando un principal/origen tira atributos relevantes para ACL a través de ≥ N clases de objeto en una ventana corta, donde el origen no está en la allowlist de la Fase 0. Tuneá N a tu baseline.
4. **Regla de fan-out SAMR + SRVSVC.** Alertá cuando una workstation no-admin enumera membresía de grupos locales (SAMR) o sesiones (`NetSessionEnum` vía `\srvsvc`) contra muchos hosts — la firma de recolección Session/LoggedOn. Clustering de Evento 4661/5145 por origen.
5. **Señal de colector .NET en memoria.** Carga de DLL/CLR de Sysmon de `System.DirectoryServices` / assemblies ADWS desde un proceso inusual, o telemetría AMSI/.NET ETW, atrapa un SharpHound renombrado o fileless que no deja ningún `SharpHound.exe` en disco.

### Fase 2 — Detectar las evasiones (la realidad de 2026)
La herramienta default es el caso fácil. El operador realista evade:

1. **LDAP paginado / throttleado / con jitter (`--Throttle`, `--Jitter`, page size chico).** Derrota los umbrales volumétricos. **Contra:** confiá en la *diversidad* (cuánto del directorio se tocó, acumulativamente) y las lecturas de honeytoken, no en eventos-por-minuto. El low-and-slow eventualmente igual lee el señuelo.
2. **Recolección DCOnly.** Saltea el toque a hosts por completo — solo LDAP + SAMR al DC, sin fan-out Session/SRVSVC. Remueve la señal de la regla-4 de la Fase 1. **Contra:** las reglas 1–3 de la Fase 1 (honeytoken, LDAP de Defender for Identity, conductual broad-LDAP) igual disparan porque la lectura del directorio igual ocurre.
3. **SOAPHound / abuso de AD Web Services.** Recolecta vía **ADWS (TCP 9389)** en vez de LDAP/389, bypasseando el Evento 1644 y la detección enfocada-en-puerto-LDAP. **Contra:** monitoreá las conexiones ADWS a los DCs desde hosts no-admin/no-management; la lectura del honeytoken dispara sin importar el transporte.
4. **Colectores custom / BOFs / `ldapsearch` + parsing offline (p. ej., bofhound).** Sin ningún binario de BloodHound. **Contra:** la detección debe basarse en el *comportamiento de acceso al directorio y el honeytoken*, nunca en el nombre o hash de la herramienta — bloquear `SharpHound.exe` se derrota con un renombre.

### Fase 3 — Investigación y respuesta
1. **Identificá el origen.** Traé el host/IP y principal de origen del evento que disparó (entidad de Defender for Identity, `SubjectUserName`/`IpAddress` de 4661/5145, o log de conexión ADWS).
2. **Construí la línea de tiempo.** Traé todos los eventos de acceso al directorio de ese origen en las últimas 24–72h. Determiná el método de recolección (DCOnly vs Session vs ACL vs ADWS) según qué señales dispararon.
3. **Mirá aguas abajo buscando la próxima etapa.** Si el mismo origen luego realiza [[cybersecurity/security-playbooks/detect-kerberoasting-and-as-rep-roasting|Kerberoasting / AS-REP roasting]] o toca derechos de replicación ([[cybersecurity/security-playbooks/detect-dcsync-and-ntdsdit-access|DCSync]]), tenés una kill chain recon→escalación confirmada, no ruido aislado.
4. **Dimensioná lo que se aprendió.** Asumí que el operador ahora tiene el grafo de ataque completo: todo camino a Tier 0 visible desde el principal recolector ahora le es conocido. Priorizá cerrar los caminos *más cortos* que el grafo habría revelado.
5. **Contené.** Deshabilitá/contené el principal y host de origen pendiente de investigación; si se comprometió una cuenta de colector sancionado, tratá sus credenciales como quemadas.

## Pistas de validación
- **El honeytoken disparó:** cualquier lectura del security descriptor del señuelo o auth a la cuenta señuelo — adversario confirmado, investigá de inmediato.
- **Recolección de alta confianza:** un principal fuera-de-allowlist lee atributos ACL a través de users+computers+groups+GPOs+trusts en una ventana.
- **Firma DCOnly:** LDAP amplio + SAMR al DC con *ningún* fan-out de host-session correspondiente.
- **Firma SOAPHound:** conexión ADWS (9389) desde una workstation que no tiene rol de management, con volumen de lectura directory-wide.
- **Confirmación de kill-chain:** el origen recolector luego roastea cuentas de servicio o pide replicación — recon seguido de acceso a credenciales desde el mismo origen.

## Mitigación / remediación
Controles durables, ordenados por efectividad:

- **Honeytokens como control permanente.** Los objetos señuelo son la detección más barata y de casi-cero-FP para la enumeración basada en ACL y deberían ser permanentes, no solo-en-incidente.
- **Reducí el grafo de ataque mismo.** La defensa más durable es tener menos caminos peligrosos que encontrar: remové ACLs excesivos, colapsá la proliferación de grupos anidados, e imponé [[cybersecurity/identity-and-active-directory/tier-zero-administration-and-paw|separación de Tier 0]] para que incluso una recolección completa no revele ningún camino corto a Domain Admin. Detectar la recolección importa menos si el grafo está limpio.
- **Habilitá y tuneá Defender for Identity** (o equivalente) las alertas de reconocimiento en vez de construir reglas crudas de 1644 desde cero.
- **Restringí la exposición de ADWS.** Limitá qué hosts pueden alcanzar el puerto 9389 del DC; es una interfaz de management, no una necesidad de workstation.
- **Auditoría de queries LDAP en Tier 0** donde Defender for Identity no esté disponible, aceptando el costo de volumen.

### Qué no funciona como defensa primaria
- **Bloquear `SharpHound.exe` / hashes conocidos.** La recolección renombrada, recompilada, en-memoria, BOF y basada-en-`ldapsearch` lo derrotan todas. El comportamiento de lectura del directorio es la superficie, no el binario.
- **Bloquear LDAP.** LDAP *es* cómo funciona AD; no podés bloquearlo. (Y SOAPHound de todos modos no usa el puerto 389.)
- **Umbrales solo-volumétricos.** La recolección throttleada/con-jitter/low-and-slow se cuela bajo cualquier rate limit; la diversidad-de-objetos-leídos y los honeytokens son las señales durables.
- **Confiar en que "BloodHound necesita admin".** No lo necesita — cualquier usuario de dominio autenticado puede correr la mayoría de los métodos de recolección. "Solo los admins pueden enumerar" es falso.
- **Prevenir la recolección del todo.** Cualquier principal autenticado puede leer la mayoría del directorio por diseño. La postura realista es *detectar recolección + encoger el grafo*, no *prevenir lecturas*.

## Logging / forense
- **Retené los datos de acceso al directorio del DC y de Defender for Identity ≥ 90 días.** Las cadenas recolección → análisis del grafo → escalación a menudo abarcan días/semanas.
- **Etiquetá cada alerta con:** host/principal de origen, método de recolección inferido (DCOnly/Session/ACL/ADWS), estado de allowlist, y si se tocó un honeytoken.
- **Capturá la metadata de conexión ADWS/LDAP** (origen, duración, volumen de bytes) — útil para distinguir una corrida de inventario completo sancionada del recon adversario.
- **Correlacioná a través del trío** vía [[cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability|correlación de rutas de ataque]]: recolección desde el host X, después roasting desde el host X horas después, después una cuenta de servicio crackeada autenticándose desde el host Y es una kill chain, no tres alertas.

## Seguridad operativa
- **siempre** mantené la allowlist de colectores-sancionados — sin ella, cada corrida legítima de BloodHound de IAM/blue-team es un falso positivo y la regla se deshabilita.
- **siempre** validá las detecciones de honeytoken end-to-end en un lab antes de confiar en ellas; un señuelo que nadie monitorea no vale nada.
- **nunca** trates "no se encontró SharpHound.exe" como "no ocurrió recolección" — asumí recolección fileless/custom y pivoteá a evidencia de comportamiento + honeytoken.
- **siempre** testeá las detecciones contra las evasiones de la Fase 2 (DCOnly, throttleado, SOAPHound) en un lab interno autorizado — una regla que solo atrapa el SharpHound default es teatro contra un operador real.
- **nunca** confíes en una sola regla; honeytoken + alerta de recon de Defender-for-Identity + conductual broad-LDAP juntas producen mucha más fidelidad que cualquiera sola.

## Notas relacionadas
- [[cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis|Análisis de rutas de ataque con BloodHound]] — la mitad ofensiva que este playbook detecta.
- [[cybersecurity/security-playbooks/detect-kerberoasting-and-as-rep-roasting|Detectar Kerberoasting y AS-REP Roasting]] — hermano del trío; la etapa de acceso a credenciales que suele seguir a la recolección.
- [[cybersecurity/security-playbooks/detect-dcsync-and-ntdsdit-access|Detectar DCSync y acceso a NTDS.dit]] — hermano del trío; el endgame después de que el grafo revela un camino a derechos de replicación.
- [[cybersecurity/identity-and-active-directory/tier-zero-administration-and-paw|Administración de Tier 0 y PAW]] — la defensa estructural que vuelve de bajo valor a una recolección completa.
- [[cybersecurity/detection-engineering/windows-event-logs|Windows Event Logs]] — las precondiciones de audit-policy de 1644/4661/5145.
- [[cybersecurity/detection-engineering/edr-network-observability-and-process-correlation|EDR / Correlación de procesos]] — telemetría del lado del host de procesos y fan-out para colectores en memoria.
- [[cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability|Correlación de rutas de ataque]] — coser recolección → roasting → DCSync en una cadena.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — el meta-principio detrás del emparejamiento ofensa/defensa.

## Referencias
- **Foundational:** MITRE ATT&CK T1087 — Account Discovery (con T1069 Permission Groups Discovery y T1482 Domain Trust Discovery) — https://attack.mitre.org/techniques/T1087/
- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Research / Deep Dive:** Robbins, Schroeder, Vazarkar — An ACE Up The Sleeve (Black Hat USA 2017) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Telemetry / Detection:** Microsoft Defender for Identity — Reconnaissance and discovery alerts — https://learn.microsoft.com/en-us/defender-for-identity/reconnaissance-discovery-alerts
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
