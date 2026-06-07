# Windows Event Logs

## Definición

Windows Event Logs son la telemetría estructurada host-side que emite el sistema operativo Windows para operaciones relevantes de seguridad: autenticación, autorización, ejecución de procesos, cambios de cuentas, acceso a objetos y estado del sistema. Los logs se almacenan como archivos `.evtx` en `%SystemRoot%\System32\winevt\Logs\`, se exponen vía el servicio Event Log y se consultan con `wevtutil`, `Get-WinEvent`, la UI de Event Viewer o una copia forwardeada a un SIEM. **El cuerpo útil de telemetría de seguridad en Windows se construye casi por completo a partir de un conjunto pequeño de Event IDs** — aproximadamente 30 de los miles definidos — y los detection engineers senior internalizan ese subset en vez de tratar los Windows logs como un stream indiferenciado.

## Por qué importa

Cada ataque orientado a Windows en este vault — [[kerberoasting|Kerberoasting]] (4769 + RC4), [[as-rep-roasting|AS-REP Roasting]] (4768 + PreAuthType=0), [[dcsync-and-ntdsdit-extraction|DCSync]] (4662 + replication GUIDs), [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] (4624 LogonType=3 + NTLM), [[bloodhound-attack-path-analysis|BloodHound]] collection (patrones de LDAP query + 4662), uso de [[golden-ticket-and-krbtgt-compromise|Golden Ticket]] (4769 sin 4768 previo del mismo usuario) — produce una firma reconocible en Windows Event Logs. Sin un modelo operativo de qué significan esos Event IDs, qué campos llevan y qué audit policy los hace aparecer, las reglas de detección y las investigaciones IR son guesswork.

El framing senior es que Event Logs **no son lo que se loguea por default**; son lo que se loguea *después de configurar correctamente la audit policy*. La audit policy default de Windows es silenciosa sobre Process Creation (4688), silenciosa sobre Sensitive Privilege Use (4673), silenciosa sobre Detailed File Share access; sin embargo esos son los eventos que la mayoría de reglas de detección necesitan. Configurar audit policy es el prerrequisito para cualquier claim de detection engineering sobre hosts Windows.

La técnica también importa como nota de estudio porque expone tres hechos transferibles:

- **Los Event IDs son el alfabeto, no el idioma.** Las detecciones reales son *secuencias y conjunciones* de Event IDs ([[behavioral-detection-vs-signature-detection|detección de comportamiento]]) — por ejemplo, "4624 + LogonType=3 + AuthenticationPackage=NTLM + fuente inusual" — no alertas de un solo Event ID.
- **El field set default está incompleto a propósito.** Microsoft envía defaults seguros para controlar volumen de logs en infraestructura compartida. La detección en producción requiere opt-in: command line de proceso (`Include command line in process creation events`), PowerShell ScriptBlockLogging, DNS client logging, Sysmon para la capa siguiente.
- **Borrar logs es en sí una señal de alta fidelidad.** Event 1102 ("audit log was cleared") y 104 ("System log was cleared") se emiten *antes* de que el clear tenga efecto — y se emiten al mismo log que se está limpiando. Los atacantes lo saben; los defensores maduros forwardean logs en tiempo real para que el evento de clearing sobreviva.

## Cómo funciona

Windows Event Logs se organizan en **4 capas** que un detection engineer debe sostener simultáneamente:

1. **Los canales de log.** Los tres logs clásicos — `Security`, `System`, `Application` — más los operational logs modernos bajo `Microsoft-Windows-*/Operational` (PowerShell, Sysmon, Windows Defender, AppLocker, DNS-Client, etc.). Los clásicos vienen desde Windows NT; los operational logs son donde vive gran parte de la telemetría de seguridad moderna.
2. **La audit policy.** Configurada vía `Local Security Policy → Advanced Audit Policy Configuration` o GPO de dominio. **Ningún evento se loguea salvo que la subcategoría de auditoría correspondiente esté habilitada.** Audit Process Creation (Success) genera 4688; sin eso, los eventos 4688 nunca aparecen. La audit policy es la puerta, no el log.
3. **Event ID + field set.** Cada Event ID tiene schema fijo: 4624 lleva campos para User, LogonType, AuthenticationPackage, Source Network Address, Workstation Name, Logon ID y ~15 más. Las reglas detectan sobre estos campos, no sobre texto raw del evento. Conocer posiciones importa porque algunos SIEM indexan por field name y otros por posición ordinal.
4. **Capa de forwarding/storage.** Windows Event Forwarding (WEF) centraliza logs, muchas veces con suscripciones basadas en WinRM. Despliegues modernos empujan a SIEM vía agente (Sysmon → Splunk Universal Forwarder, Sentinel Azure Monitor Agent, Elastic Agent). El forwarder también es donde ocurren filtering y rate-limiting; las reglas deben considerar qué sobrevive al forwarder.

Query representativa contra el Security log:

```
# Find every NTLM network logon in the last 24 hours.
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    ID=4624
    StartTime=(Get-Date).AddHours(-24)
} | Where-Object {
    $_.Properties[8].Value -eq 3 -and       # LogonType 3 (Network)
    $_.Properties[10].Value -eq 'NTLM'      # AuthenticationPackage
} | Select-Object TimeCreated,
    @{n='User';e={$_.Properties[5].Value}},
    @{n='Source';e={$_.Properties[18].Value}},
    @{n='Target';e={$_.Properties[6].Value}}
```

El bug no es "Windows logs son demasiado verbosos" ni "Windows logs son demasiado escasos"; es que *Windows logs son configurados-no-default, schema-driven y field-positional — y detection engineering requiere sostener audit policy, semántica de Event IDs, field schema y pipeline de forwarding como cuatro capas que interactúan*.

## Técnicas / patrones

### Los Event IDs que importan (el subset senior)

| Categoría | Event ID | Qué significa | Señal de telemetría |
| --- | --- | --- | --- |
| **Logon / logoff** | 4624 | Logon exitoso | LogonType + AuthenticationPackage + Source IP — evento fundacional |
|  | 4625 | Logon fallido | Razón de falla — brute-force, locked-out, expired-pwd, bad-user |
|  | 4634 | Logoff | Fin de sesión |
|  | 4647 | Logoff iniciado por usuario | Distingue cierre voluntario de inducido por sistema |
|  | 4648 | Logon con credenciales explícitas | `runas /netonly` y similares — delegación de credenciales |
|  | 4672 | Privilegios especiales asignados a un nuevo logon | Indica derechos equivalentes a Administrator en esa sesión |
| **Kerberos** | 4768 | Request TGT | Campo Pre-Auth Type — `PreAuthType=0` = indicador AS-REP roasting |
|  | 4769 | Request TGS | Campo TicketEncryptionType — `0x17` (RC4) contra baseline AES = indicador Kerberoasting |
|  | 4770 | TGT renovado | Renovaciones de TGT de larga vida pueden indicar Golden Ticket si `krbtgt` fue rotado |
|  | 4771 | Kerberos pre-auth failed | Failure-code diferencia "wrong password" de "account locked" |
| **Process / command** | 4688 | Proceso creado | Command line (solo si se habilita explícitamente) + proceso padre |
|  | 4689 | Proceso terminó | Pair con 4688 para duración de proceso |
| **Privilege use** | 4673 | Privilegio sensible usado | Alto volumen en config default — suele filtrarse |
|  | 4674 | Operación intentada sobre objeto privilegiado | Relevante para SeDebugPrivilege y credential dumping |
| **Account management** | 4720 | Cuenta creada | Principal nuevo — alertar siempre |
|  | 4722 | Cuenta habilitada | Re-enable puede ser persistencia |
|  | 4724 | Intento de reset de contraseña | Indicador de escalada de privilegios |
|  | 4725 | Cuenta deshabilitada | Telemetría operacional |
|  | 4726 | Cuenta eliminada | Indicador anti-forense |
|  | 4738 | Cuenta modificada | Catch-all para cambios de propiedades |
| **Group management** | 4728 | Miembro agregado a global group security-enabled | Vigilar Tier 0 especialmente |
|  | 4732 | Miembro agregado a local group security-enabled | Escalada local admin |
|  | 4756 | Miembro agregado a universal group security-enabled | Enterprise Admins, Schema Admins viven acá |
| **Object access** | 4662 | Operación sobre un objeto | Detector DCSync — filtrar replication GUIDs `1131f6aa-*` y `1131f6ad-*` |
|  | 4663 | Intento de acceso a objeto | File / registry / kernel object access |
|  | 4670 | Permisos de un objeto cambiados | Rastro de modificación AdminSDHolder |
| **System / integrity** | 1100 | Event log service shutting down | Indicador pre-clear o pre-shutdown |
|  | 1102 | Audit log cleared | Indicador adversario de alta fidelidad |
|  | 104 | System log cleared | Compañero de 1102 |
| **PowerShell** | 4103 | Module logging | Detalle de ejecución PowerShell a nivel función |
|  | 4104 | ScriptBlock logging | Contenido de script de-ofuscado — telemetría PowerShell más valiosa |
|  | 4105 / 4106 | ScriptBlock start / stop | Bracketing de lifecycle |

### Patrones

- **Siempre habilitá Audit Process Creation con command line.** GPO: `Computer Configuration → Administrative Templates → System → Audit Process Creation → Include command line in process creation events = Enabled`. Sin eso, 4688 está medio ciego.
- **Habilitá PowerShell ScriptBlock Logging.** GPO `Turn on PowerShell Script Block Logging`. Captura contenido de-ofuscado en Event 4104, incluyendo strings construidos dinámicamente.
- **Forwardeá en tiempo real, no por pull programado.** Suscripciones WEF con `Minimize Latency` hacen fútil el log-clearing: los eventos ya llegaron al collector antes de que el atacante pueda limpiar la fuente.
- **Pair 4624 LogonType con AuthenticationPackage e IP fuente.** `4624 + LogonType=3 + AuthenticationPackage=NTLM` es señal clásica de Pass-the-Hash en entornos que deberían usar Kerberos.
- **Vigilá drift de encryption-type en 4769.** Un 4769 con `TicketEncryptionType=0x17` (RC4-HMAC) para una cuenta con baseline AES es firma de Kerberoasting.
- **`PreAuthType=0` en Event 4768 es detección single-event de alta confianza.** En entornos sin integración legacy MIT/Heimdal, ninguna cuenta debería tener `DONT_REQ_PREAUTH`.
- **Cross-join 4662 con replication-rights GUIDs.** Solo DCs deberían generar esos eventos desde sus computer accounts. Cualquier otra fuente = alerta DCSync.

### Qué agrega Sysmon encima

El logging built-in de Windows captura lo que el OS observa sobre sí mismo. **Sysmon** ([[edr-network-observability-and-process-correlation|EDR / correlación de procesos]]) es un driver Microsoft Sysinternals que captura lo adyacente: conexiones de red por proceso, file creates, modificaciones de registry, image loads, named pipes, raw access reads. El par `4688 + Sysmon Event 1` da la telemetría canónica de process creation que casi toda regla de detección necesita.

## Variantes y bypasses

Windows logging se divide en **4 variantes de fuente de telemetría** con tradeoffs distintos.

### 1. Auditoría built-in de Windows

Logs Security/System/Application con audit policy habilitada. Cero software extra. Field set limitado por Event ID. Adecuado para detecciones fundacionales; insuficiente para command-line process telemetry por default hasta habilitar la policy.

### 2. Sysmon

Microsoft Sysinternals. Gratis, basado en kernel driver, configurable con XML. Agrega joins proceso-red, file creation telemetry, image loads. Es la capa de facto sobre la auditoría default.

### 3. Telemetría de vendor EDR

CrowdStrike, Microsoft Defender for Endpoint, SentinelOne, etc. Captura lo de Sysmon más acceso a memoria, child-process telemetry, behavioral analytics y backend cloud resistente a apagado local.

### 4. Auditd-style en Windows

Algunas organizaciones usan ETW directamente con consumidores custom. Máxima fidelidad, menor abstracción, mayor costo operativo. Suele verse en research o CIRT.

## Impacto

Ordenado por severidad típica de mal uso defensivo:

- **Ceguera por audit policy default.** Organizaciones que creen "tenemos Windows logs" sin verificar subcategorías.
- **Telemetría de procesos sin command lines.** 4688 dice que se creó un proceso sin decir qué comando se ejecutó.
- **Sin PowerShell ScriptBlock logging.** Los atacantes ofuscan; 4104 captura el script final de-ofuscado.
- **Retención solo local.** Logs que viven solo en el host son borrados por atacantes; WEF o equivalente es no negociable.
- **Tradeoff volumen vs retención.** Habilitar todo hace inmanejables los logs; habilitar poco hace imposible detectar.

## Detección y defensa

Esta nota *es* una defensa. El framing relevante es **qué monitorear en Windows Event Logs** para los ataques AD y de credenciales del vault.

Ordenado por valor de detección:

1. **Configurá primero la audit policy.**
   `auditpol /set /subcategory:` para Logon, Logoff, Process Creation, Kerberos Authentication Service, Kerberos Service Ticket Operations, Account Management, Directory Service Access, Security State Change. Habilitá command line en process creation y PowerShell Module + ScriptBlock + Transcription logging.

2. **Forwardeá a un SIEM en tiempo real.**
   Windows Event Forwarding con suscripciones WinRM, o agente EDR/SIEM. Logs solo locales son forénsicamente poco confiables; forwarded logs sobreviven Event 1102.

3. **Construí reglas de comportamiento desde secuencias de Event IDs, no eventos únicos.**
   Patrones:
   - [[kerberoasting|Kerberoasting]]: alto volumen de 4769 con `TicketEncryptionType=0x17` desde una fuente en 60s.
   - [[as-rep-roasting|AS-REP Roasting]]: 4768 con `PreAuthType=0` contra cualquier cuenta no allowlisted.
   - [[dcsync-and-ntdsdit-extraction|DCSync]]: 4662 con replication GUIDs desde una computer account no-DC.
   - [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]]: 4624 LogonType=3 + AuthenticationPackage=NTLM en un entorno Kerberos/AES.
   - Log clearing: 1102 o 104 — alerta high-severity, causa legítima casi nula.
   - Cambios de grupos Tier 0: 4728 / 4732 / 4756 donde el grupo pertenece al set Tier 0.

4. **Pair con Sysmon para telemetría de procesos.**
   SwiftOnSecurity Sysmon config es un buen punto de partida. Sysmon Event 1, 3, 7, 11 y 13 cubren gran parte de detección comportamental host-side.

5. **Auditá y tuneá trimestralmente.**
   Volumen y baselines de falsos positivos derivan. Una revisión trimestral del pipeline mantiene signal-to-noise alto.

### Qué no funciona como defensa primaria

- **Habilitar toda subcategoría de auditoría.** Produce volumen inmanejable y degrada el SIEM.
- **Retención solo local.** Los atacantes limpian logs; los timelines forenses mueren.
- **Detectar sobre texto raw del evento.** El texto cambia por versión e idioma. Las reglas deben ser field-based.
- **Confiar en "sin log = no pasó nada".** Verificá audit policy y forwarder por separado.

## Labs prácticos

```
# Lab 1 — Audit your current audit policy.
auditpol /get /category:*
```

```
# Lab 2 — Enable Process Creation with command-line logging (test in a lab).
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit" `
    /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f
cmd /c "whoami"
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4688} -MaxEvents 5 |
    Select-Object TimeCreated, @{n='CmdLine';e={$_.Properties[8].Value}}
```

```
# Lab 3 — Query Kerberos events for Kerberoasting signature.
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    ID=4769
    StartTime=(Get-Date).AddHours(-24)
} | Where-Object {
    $_.Properties[6].Value -eq '0x17'
} | Select-Object TimeCreated,
    @{n='Target';e={$_.Properties[0].Value}},
    @{n='Service';e={$_.Properties[2].Value}},
    @{n='Source';e={$_.Properties[6].Value}},
    @{n='EncType';e={$_.Properties[5].Value}}
```

```
# Lab 4 — Detect AS-REP Roasting signature.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 200 |
    Where-Object { $_.Properties[10].Value -eq '0' } |
    Select-Object TimeCreated,
        @{n='Target';e={$_.Properties[0].Value}},
        @{n='Source';e={$_.Properties[9].Value}}
```

```
# Lab 5 — Detect DCSync signature (Event 4662 + replication GUIDs).
$dcsyncGuids = @(
    '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2',
    '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'
)
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 500 |
    Where-Object {
        $msg = $_.Message
        $dcsyncGuids | ForEach-Object { if ($msg -match $_) { return $true } }
    } |
    Select-Object TimeCreated, @{n='Subject';e={$_.Properties[3].Value}}
```

```
# Lab 6 — Enable PowerShell ScriptBlock logging and verify capture.
reg add "HKLM\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
    /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f
powershell -enc cwBlAHQALQBsAG8AYwBhAHQAaQBvAG4AIABDADoAXAA=
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 10 |
    Where-Object { $_.Id -eq 4104 } |
    Select-Object TimeCreated, @{n='Script';e={$_.Properties[2].Value}}
```

## Ejemplos prácticos

- **SOC detecta Kerberoasting en 90 segundos.** Regla sobre 4769 + `TicketEncryptionType=0x17` en un entorno AES-baseline dispara en el primer intento.
- **DCSync detectado por Event 4662.** Regla sobre 4662 + replication GUIDs desde sujetos no-DC dispara en el primer `secretsdump.py -just-dc-user krbtgt`.
- **Ofuscación PowerShell derrotada por ScriptBlockLogging.** Event 4104 captura el script final de-ofuscado aunque el payload tenga muchas capas de encoding.
- **Gap de audit policy descubierto post-incidente.** Process Creation nunca estuvo habilitado; el SIEM no tiene command-line telemetry y el timeline queda incompleto.
- **Alerta de log-clearing captura anti-forensics.** `wevtutil cl Security` genera 1102 antes de purgarse; WEF ya lo forwardeó.

## Notas relacionadas

- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[edr-network-observability-and-process-correlation|EDR / process correlation]]
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]]
- [[false-positives-false-negatives-and-detection-tradeoffs|False Positives and Negatives]]
- [[kerberoasting|Kerberoasting]]
- [[as-rep-roasting|AS-REP Roasting]]
- [[dcsync-and-ntdsdit-extraction|DCSync]]
- [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]]
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting + AS-REP Roasting]]
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]]

### Notas atómicas futuras sugeridas

- sysmon-configuration-and-tuning
- powershell-logging-deep-dive
- etw-event-tracing-for-windows
- windows-event-forwarding-architecture
- ad-logging-versus-application-logging-tradeoffs
- detect-windows-log-clearing

## Referencias

- **Fundamental:** Microsoft Learn — Advanced security audit policy settings — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/advanced-security-audit-policy-settings
- **Fundamental:** Microsoft Learn — Events to Monitor — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/appendix-l-events-to-monitor
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Windows Security Event Log Categories — https://adsecurity.org/?p=3299
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
