# Detectar DCSync y acceso a ntds.dit

## Objetivo

Detectar las dos formas de extracción masiva de credenciales de Active Directory — **DCSync** (`IDL_DRSGetNCChanges` vía la interfaz RPC DRSUAPI) y **extracción offline de `ntds.dit`** (acceso a nivel archivo, abuso de shadow-copy VSS, invocaciones de `ntdsutil`) — con fidelidad suficiente para identificar el principal origen, las cuentas afectadas y la ventana posterior a la extracción antes de que puedan usarse tickets falsificados ([[golden-ticket-and-krbtgt-compromise|Golden Ticket]] o [[silver-ticket-and-service-account-persistence|Silver Ticket]]).

## Supuestos

- recolectás Windows Security event logs de **todos los Domain Controllers** en un SIEM con retención de >= 90 días
- tenés cobertura EDR en cada Domain Controller (Sysmon, Microsoft Defender for Identity o equivalente)
- mantenés una lista autoritativa de principals con `DS-Replication-Get-Changes-All` y derechos de replicación relacionados (auditada mensualmente con [[bloodhound-attack-path-analysis|BloodHound]])
- podés deshabilitar en caliente una cuenta comprometida e iniciar el **procedimiento de rotación de `krbtgt` dos veces en secuencia** en cuestión de horas
- el objetivo es **detectar, contener y recuperar**; DCSync es el ataque de final de partida, cuando dispara ya estás en modo incident response

## Prerrequisitos

- DC audit policy: `Audit Directory Service Access: Success/Failure` habilitado (esto genera Event 4662; **no está activo por defecto** en la mayoría de defaults de Windows Server)
- parsing en SIEM para Event 4662 con el campo `Object > Properties` indexado para que los GUIDs de derechos de replicación sean consultables
- lista autoritativa de:
- cuentas de equipo de Domain Controllers (los únicos principals que deberían hacer DCSync legítimamente)
- principals con derechos efectivos de replicación vía query Cypher en [[bloodhound-attack-path-analysis|BloodHound]]
- allowlist de fuentes legítimas de acceso a ntds.dit (software de backup, tooling de recuperación de AD)
- script de rotación de `krbtgt` prearmado (Microsoft `New-KrbtgtKeys.ps1` o equivalente) probado en un ejercicio de recuperación; runbook listo, no improvisado bajo presión
- opcional: honey-principal con derechos de replicación y contraseña fuerte sin uso; cualquier intento de DCSync contra este principal es actividad adversaria de alta confianza

## Pasos de detección

> *Este playbook va en par con [[dcsync-and-ntdsdit-extraction|DCSync y extracción de ntds.dit]]. Leé offense + defense como exige la [[attacker-defender-duality-as-a-learning-tool|disciplina de lectura en pares]].*

### Fase 0 — Baseline (una vez, refrescar mensualmente)

1. **Enumerá derechos efectivos de replicación.** En [[bloodhound-attack-path-analysis|BloodHound]]:
   `cypher
   MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain)
   RETURN DISTINCT n.name AS principal, labels(n)[0] AS type`
   Solo deberían aparecer cuentas de equipo de Domain Controllers y admins Tier 0 explícitos. Cualquier otra cosa es un **hallazgo**; remedialo antes de apoyarte en la detección.

2. **Inventariá cuentas de equipo DC.** Tabla lookup del SIEM poblada con las cuentas SAM y source IPs de cada DC. Las reglas de detección hacen join contra esta lista.
3. **Inventariá acceso legítimo a `ntds.dit`.** Vendors de backup (Veeam, Commvault, Windows Backup nativo), tooling de recuperación de AD y *nada más* deberían tocar el archivo. Documentá la allowlist.
4. **Auditá la cadencia baseline de rotación de `krbtgt`.** Si `krbtgt` se rotó por última vez hace más de un año, programá una **rotación proactiva simple** antes de depender de este playbook; la ventana de password-history asume que el `krbtgt` actual es la única clave válida.

### Fase 1 — Detectar DCSync clásico (DRSUAPI)

Firma del operador: **Event 4662 en un Domain Controller con `Properties` que contiene los GUIDs de replicación, donde el `Subject` *no* es una cuenta de equipo DC**.

1.
**Regla de GUIDs de derechos de replicación (máxima fidelidad).** Alertá cuando Event 4662 contenga *cualquiera* de:
   - `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes)
   - `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes-All)
   - `89e95b76-444d-4c62-991a-0facbeda640c` (DS-Replication-Get-Changes-In-Filtered-Set)
   `text
   index=wineventlog EventCode=4662
   (Properties="*1131f6aa-9c07-11d1-f79f-00c04fc2dcd2*"
     OR Properties="*1131f6ad-9c07-11d1-f79f-00c04fc2dcd2*"
     OR Properties="*89e95b76-444d-4c62-991a-0facbeda640c*")
   | lookup dc_computer_accounts SubjectUserSid AS legitimate_dc
   | where isnull(legitimate_dc)`
   Cada match es una **alerta inmediata de severidad alta**. Prácticamente no hay falsos positivos legítimos.

2.
**Perfil de targeting por cuenta.** Si múltiples eventos 4662 con GUIDs de replicación disparan desde una fuente contra muchas cuentas objetivo distintas, el operador está haciendo `-just-dc` (dump completo) en vez de `-just-dc-user krbtgt` (quirúrgico). La variante full-dump es más ruidosa pero más usada por operadores menos cuidadosos; la variante quirúrgica exige respuesta más rápida porque el objetivo suele ser una sola cuenta (`krbtgt`).

3.
**Correlación de procesos en host origen vía EDR.** Cruzá la source IP del evento 4662 con telemetría EDR de procesos en ese host. Buscá `secretsdump.py`, `mimikatz.exe`, `Rubeus.exe`, firmas Python de Impacket o binarios unsigned ejecutándose durante la ventana de alerta. Un host Windows corriendo `secretsdump.py` es adversario confirmado; una fuente Linux con Impacket es la firma canónica de Kali/host de operador.

### Fase 2 — Detectar extracción offline de ntds.dit

Firma del operador: **acceso directo a `C:\Windows\NTDS\ntds.dit`** en un DC, o **creación de shadow-copy VSS** seguida de acceso al archivo, o **invocación de `ntdsutil`** con subcomandos `ifm` / `IFM`.

1.
**Sysmon Event 11 (file create) en rutas shadow-copy.**
   `text
   index=sysmon EventCode=11
   TargetFilename="\\GLOBALROOT\Device\HarddiskVolumeShadowCopy*\Windows\NTDS\ntds.dit"`
   Cualquier match es una **alerta de alta fidelidad**. El software de backup legítimo usa VSS pero no extrae archivos individuales de esta manera.

2.
**Creación de procesos: `ntdsutil`, `vssadmin create shadow`, `wbadmin start backup`.**
   `text
   index=wineventlog EventCode=4688 (NewProcessName="*\\ntdsutil.exe" OR
     (NewProcessName="*\\vssadmin.exe" AND CommandLine="*create shadow*") OR
     (NewProcessName="*\\wbadmin.exe" AND CommandLine="*ntds*"))`
   Alertá con supresión por allowlist para parent processes conocidos de software de backup legítimo.

3.
**Sysmon Event 1 con patrón de argumentos `ntdsutil` + `IFM`.** `ntdsutil "ac i ntds" "ifm" "create full c:\extract" q q` es el comando canónico del operador. El string de argumentos es reconocible; alertá específicamente sobre eso.

4.
**Telemetría EDR de file-handle sobre `ntds.dit`.** Productos EDR modernos (Defender for Endpoint, CrowdStrike, SentinelOne) emiten eventos de apertura de file handles para rutas sensibles de la base AD. Cruzalo con la allowlist de backup legítimo; todo lo demás alerta.

### Fase 3 — Detectar DCShadow (registro de DC rogue)

Firma del operador: **cambios anómalos a objetos del configuration container de AD**; un host no-DC registrándose como DC y luego revirtiendo el registro después de empujar cambios.

1. **Event 4929 / 4928** (replication source replica agregada/removida) fuera de la ventana de change-management.
2. **Event 5136** (directory service object modified) sobre objetos en `CN=Sites,CN=Configuration,...` con `SubjectUserSid` que no es un DC ni servicio de scheduled task.
3. **Conexiones de red Sysmon a TCP 135 (RPC) + puertos altos dinámicos** desde un host no-DC hacia un DC; la firma de inbound replication DRSUAPI cuando *la fuente está impersonando un DC*.

DCShadow es más raro y sigiloso que DCSync clásico; la detección suele depender de la regla específica de Microsoft Defender for Identity más que de queries raw de Event Log.

### Fase 4 — Investigación y respuesta

Cuando dispare cualquier alerta de Fase 1-3:

1. **Tratala como compromiso confirmado hasta demostrar lo contrario.** La tasa de falsos positivos de estas reglas es casi cero; la postura de respuesta debería reflejarlo.
2. **Identificá el host y principal origen.** Fase 1: extraé `SubjectUserSid` y source IP del evento 4662. Fase 2: extraé el parent process tree desde EDR. Construí la línea de tiempo del operador de las últimas 24 horas desde esa fuente.
3. **Determiná el alcance de extracción.**
   - `-just-dc-user <target>` -> solo el hash de la cuenta nombrada está comprometido. Respuesta quirúrgica: rotar la contraseña de esa cuenta.
   - `-just-dc` (dump completo) -> **todas las cuentas del domain** están comprometidas, incluido `krbtgt`. Respuesta de domain completo.
   - ntds.dit + hive SYSTEM copiados -> igual que dump completo.
4. **Iniciá rotación de `krbtgt` si `krbtgt` estuvo en alcance.** Usá el script `New-KrbtgtKeys.ps1` de Microsoft. **Dos veces en secuencia**, con >= 10 horas entre rotaciones para dejar que repliquen los cambios y avance la ventana de password-history. Una sola rotación es insuficiente porque el hash anterior de `krbtgt` sigue siendo válido.
5. **Deshabilitá la cuenta origen.** Forzá reautenticación para cada admin Tier 0 (asumí que sus credenciales pueden haber habilitado la cadena de ataque). Auditá cada evento de autenticación desde la source IP en los últimos 30 días.
6. **Auditá uso de Golden / Silver Ticket.** Cualquier TGT o TGS para `krbtgt` o cuentas de servicio emitido entre el momento de extracción y el fin de la rotación puede ser falsificado. Cruzalo con alertas de [[detect-kerberoasting-and-as-rep-roasting]] en la misma ventana.
7. **Abrí un ticket IR** con: eventos disparadores, host + principal + IP origen, lista de cuentas extraídas (si se conoce), estado de rotación de `krbtgt`, hallazgos de auditoría de Golden/Silver Ticket, snapshot completo de BloodHound antes y después de la extracción sospechada.

## Claves de validación

- **DCSync de alta confianza:** Event 4662 con GUIDs de replicación desde un `SubjectUserSid` no-DC. Un solo evento es suficiente.
- **Extracción de ntds.dit de alta confianza:** Sysmon Event 11 en una ruta shadow-copy que termina en `ntds.dit`, o invocación de `ntdsutil` con argumentos `IFM`/`ifm` fuera de la ventana de change-management.
- **Honey-principal disparado:** cualquier intento de DCSync contra el honey-principal con derechos de replicación. Falso positivo casi cero; investigalo como actividad adversaria confirmada.
- **Evidencia de cadena:** la misma source IP/principal que disparó una alerta Kerberos ([[detect-kerberoasting-and-as-rep-roasting]]) en las horas previas ahora hace DCSync. Confirma una cadena Kerberoasting -> cuenta de servicio crackeada -> DCSync, el final de partida canónico en AD.
- **Evidencia de ticket falsificado post-rotación:** Event 4769 (TGS issued) donde el tipo de cifrado del ticket `krbtgt` no coincide con la clave `krbtgt` actual ni anterior. Indica un Golden Ticket falsificado con un hash viejo filtrado de `krbtgt` todavía en uso después de una rotación simple insuficiente.

## Mitigación / remediación

Del lado defensor, estos son controles durables (no fixes por alerta):

- **Auditoría mensual de BloodHound sobre derechos efectivos de replicación.** Query `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. El resultado sano es "solo DCs y admins Tier 0 explícitos". Cualquier otra cosa es un hallazgo a remediar. Ver [[dcsync-and-ntdsdit-extraction|DCSync]] §Detection-and-defense item 1.
- **Rotación proactiva trimestral de `krbtgt`.** Dos veces en secuencia, con cadencia trimestral, incluso sin sospecha de compromiso. Acorta la peor ventana de Golden Ticket de "décadas" a "<= 3 meses".
- **Disciplina de [[tier-zero-administration-and-paw|administración Tier 0]].** PAWs, Authentication Policies, membresía Protected Users para todos los admins Tier 0. Es la defensa estructural que impide que la cadena de robo de credenciales termine en DCSync.
- **Auditá `Exchange Trusted Subsystem` y grupos relacionados instalados por Exchange.** Instalaciones históricas de Exchange otorgan DCSync efectivo a múltiples grupos. Descomisionar Exchange no elimina automáticamente estos permisos; hace falta auditoría y remoción explícita.
- **Deshabilitá NTLMv1 en todo el domain.** Existen cadenas NTLM-relay-to-DCSync; eliminar la superficie de relay fuerza a los operadores hacia caminos Kerberos-only que este playbook detecta mejor.
- **Plantá honey-principals.** Una cuenta falsa con `DS-Replication-Get-Changes-All` y una contraseña fuerte sin uso es, por definición, tráfico adversario-only cuando se accede.

### Qué no funciona como defensa primaria

- **Bloquear DRSUAPI a nivel red.** Los DCs deben replicar; bloquear el protocolo rompe el directorio.
- **Confiar en que "solo los DCs tienen derechos de replicación".** Verificalo con BloodHound. Permisos legacy de instalaciones de Exchange suelen producir principals sorpresa.
- **Rotación simple de `krbtgt`.** Password history conserva el hash previo; una rotación no invalida material filtrado.
- **Confiar en bajo volumen de alertas.** Un *solo* evento 4662 con un GUID de replicación desde una fuente no-DC es la firma. Los umbrales volumétricos pierden al operador quirúrgico.
- **Confiar solo en EDR.** Operadores modernos usan binarios Microsoft firmados (Impacket vía Python, variantes in-memory de secretsdump) que evaden firmas por nombre de binario. La detección del lado Event Log es estructural; EDR es la capa de corroboración.

## Logging / forensics

- **Retené DC Security logs por >= 90 días.** DCSync seguido de uso de Golden Ticket suele abarcar semanas; la retención es el piso para reconstrucción forense de línea de tiempo.
- **Etiquetá cada alerta con:** source IP, `SubjectUserSid` origen, cuentas objetivo, GUIDs de replicación usados, estado de allowlist (¿la fuente era un DC legítimo?), estado de rotación de `krbtgt` al momento de la alerta, alertas Kerberoasting/AS-REP correlacionadas en los 30 días previos.
- **Capturá el tráfico RPC DRSUAPI completo desde la fuente si es posible.** La telemetría de red (Zeek `dce_rpc.log`, Sysmon Event 3) desde la source IP durante la ventana de alerta suele revelar el fingerprint de herramienta del operador (Impacket vs Mimikatz vs custom).
- **Sacá snapshot de BloodHound antes *y* después del compromiso sospechado.** Comparar estados del graph revela si el operador agregó derechos DCSync a otros principals post-compromise (movimiento común de persistencia).
- **Cruzalo con [[attack-path-correlation-and-kill-chain-observability|correlación de attack paths]].** Una sola alerta DCSync es de alta confianza; una alerta DCSync precedida por Kerberoasting, collection de BloodHound y actividad SMB lateral es una kill chain confirmada lista para handoff a incident response.

## Seguridad operativa

- **nunca** autodeshabilites replicación en una cuenta de equipo DC como respuesta a una alerta; el DC debe replicar para mantenerse en el directorio.
- **nunca** rotes `krbtgt` una sola vez después de sospecha de compromiso; siempre dos veces en secuencia con espera de replicación entre ambas.
- **siempre** mantené una allowlist documentada de fuentes legítimas de acceso a ntds.dit (software de backup, tooling de recuperación de AD) antes de depender de las reglas de detección de Fase 2.
- **siempre** probá las reglas de detección contra un lab interno autorizado ejecutando [[dcsync-and-ntdsdit-extraction|DCSync]] antes de depender de ellas en producción. Las reglas sin probar son teatro.
- **siempre** tratá una alerta de Fase 1 como compromiso confirmado hasta demostrar lo contrario; la tasa de falsos positivos es casi cero y el costo de una respuesta lenta es compromiso total del domain.

## Notas relacionadas

- [[dcsync-and-ntdsdit-extraction|DCSync y extracción de ntds.dit]] — el playbook ofensivo que este replica.
- [[golden-ticket-and-krbtgt-compromise|Golden Ticket y compromiso de krbtgt]] — el ataque inmediatamente posterior a DCSync; la razón por la que la rotación de `krbtgt` es prioridad de respuesta.
- [[silver-ticket-and-service-account-persistence|Silver Ticket y persistencia de cuenta de servicio]] — el equivalente acotado a cuenta de servicio después de que DCSync recupera un hash de cuenta de servicio.
- [[krbtgt-rotation-and-tier-zero-recovery|Rotación de krbtgt y recuperación Tier 0]] — el procedimiento canónico de recuperación después de sospecha de compromiso de `krbtgt`.
- [[bloodhound-attack-path-analysis|BloodHound]] — la herramienta tanto para enumeración ofensiva de derechos de replicación como para auditoría defensiva.
- [[tier-zero-administration-and-paw|Administración Tier 0]] — la defensa estructural que vuelve imposible la cadena hacia DCSync.
- [[detect-kerberoasting-and-as-rep-roasting]] — la detección upstream que frecuentemente precede una alerta DCSync en la misma cadena.
- [[windows-event-logs|Windows Event Logs]] — referencia de Event 4662 + GUIDs de replicación; Event 4929 / 5136 (indicadores DCShadow).
- [[behavioral-detection-vs-signature-detection|Detección behavioral vs detección por firmas]] — el encuadre correcto para detección de DCSync; no existe una firma útil en la capa de clase de bug.
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths]] — correlación multi-stage entre recon + Kerberoast + DCSync + Golden Ticket.
- [[run-scan-pipeline]] / [[detect-external-scan-pipeline]] — el patrón paralelo de playbooks offense/defense que este playbook sigue.
- [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]] — el metaprincipio.

## Referencias

- **Fundacional:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Fundacional:** Microsoft Learn — AD DS replication permissions and audit guidance — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
- **Research / Deep Dive:** Microsoft Defender for Identity — DCSync attack detection — https://learn.microsoft.com/en-us/defender-for-identity/credential-access-alerts
