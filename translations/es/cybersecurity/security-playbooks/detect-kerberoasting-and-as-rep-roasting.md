# Detectar Kerberoasting y AS-REP Roasting

## Objetivo

Detectar las dos familias de ataques de credenciales Kerberos en Active Directory ([[kerberoasting|Kerberoasting]] y [[as-rep-roasting|AS-REP Roasting]]) mediante análisis behavioral sobre Event IDs 4768/4769 y telemetría complementaria, con fidelidad suficiente para identificar la cuenta origen, el host atacante y el alcance en minutos, y con durabilidad suficiente para sobrevivir pequeñas variaciones de tradecraft del operador (tipo de cifrado, tasa de requests, selección de cuentas).

## Supuestos

- recolectás Windows Security event logs de todos los Domain Controllers en un SIEM (Splunk, Sentinel, Elastic o equivalente) con retención de >= 30 días
- tenés una lista autoritativa de cuentas de servicio (cuentas con atributo `servicePrincipalName` seteado) y una auditoría de cuentas con `DONT_REQ_PREAUTH` seteado
- podés deshabilitar en caliente una cuenta comprometida y exigir aprobación Tier 0 para rehabilitarla
- el objetivo es **detectar, contener, investigar**; no prevenir. Las features de protocolo que estos ataques explotan no son bugs parcheables

## Prerrequisitos

- DC audit policy: `Audit Kerberos Authentication Service: Success/Failure` y `Audit Kerberos Service Ticket Operations: Success/Failure` habilitados (generan 4768 y 4769 respectivamente); ver [[windows-event-logs|Windows Event Logs]] para la referencia completa de audit-policy + Event-ID
- tablas SIEM para Event 4768 y 4769 con el campo `TicketEncryptionType` (4769) o `PreAuthType` (4768) parseado e indexado
- baseline de comportamiento Kerberos normal por cuenta de servicio: tasa típica de requests, source IPs típicas, tipos de cifrado típicos
- lista autoritativa de cuentas que legítimamente tienen `DONT_REQ_PREAUTH` seteado (debería ser <= 1 en un entorno sano, idealmente cero)
- opcional: honey accounts con SPN seteado y/o pre-auth deshabilitada (detección asimétrica de alta confianza)

## Pasos de detección

> *Este playbook va en par con dos notas ofensivas: [[kerberoasting|Kerberoasting]] y [[as-rep-roasting|AS-REP Roasting]]. Leé offense + defense como exige la [[attacker-defender-duality-as-a-learning-tool|disciplina de lectura en pares]].*

### Fase 0 — Baseline (una vez, refrescar trimestralmente)

1. **Inventariá cuentas con SPNs.** Son tus targets de Kerberoasting. Auditá cuáles son cuentas de servicio legítimas y cuáles son malas configuraciones.
   `text
   Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName`

2. **Inventariá cuentas con `DONT_REQ_PREAUTH`.** Son tus targets de AS-REP roasting. El conteo sano es cero.
   `text
   Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth`

3. **Baselinizá tipos de cifrado por cuenta.** Corré durante 7 días y registrá el TicketEncryptionType dominante por cuenta de servicio (debería ser AES256 o AES128, valor 0x12 o 0x11, en cualquier entorno moderno).
4. **Baselinizá tasas de request por cuenta de servicio.** Una cuenta de servicio real suele pedir una cantidad chica de tickets TGS por día, desde un conjunto chico de hosts origen. Registralo por cuenta.
5. **Auditá y remediá hallazgos de Fase 0 antes de depender de la detección.** Reducir la superficie es más valioso que detectar ataques contra superficie innecesaria.

### Fase 1 — Detectar Kerberoasting

Firma del operador: **tráfico TGS-REQ en bulk desde una fuente contra muchas cuentas de servicio, frecuentemente con tipo de cifrado RC4-HMAC, frecuentemente en segundos.**

1. **Regla de TGS request de alto volumen.** Alertá cuando una sola cuenta pida TGS para >= N cuentas de servicio distintas dentro de 60 s. N depende del baseline; 5-10 es un punto de partida fuerte.
   `text
   # Splunk-ish pseudocode
   index=wineventlog EventCode=4769 TicketEncryptionType IN ("0x17","0x12","0x11")
   | bin _time span=60s
   | stats dc(ServiceName) AS uniq_services BY _time, TargetUserName, IpAddress
   | where uniq_services >= 5`

2. **Regla de anomalía RC4-HMAC.** Alertá sobre TGS-REQ con `TicketEncryptionType=0x17` (RC4-HMAC) para cualquier cuenta de servicio cuyo baseline sea AES. El atacante frecuentemente degrada a RC4 para que el cracking offline sea económicamente viable.
   `text
   index=wineventlog EventCode=4769 TicketEncryptionType="0x17"
   | lookup service_account_baseline ServiceName OUTPUT baseline_enctype
   | where baseline_enctype != "0x17"`

3. **Regla de desviación behavioral de cuenta de servicio.** Alertá cuando la *fuente* de requests TGS de una cuenta de servicio se desvíe del baseline. Las cuentas de servicio reales se usan desde el mismo conjunto chico de hosts; el host atacante es nuevo.
4. **Correlación LDAP+Kerberos por fuente.** Un operador Kerberoasting suele consultar LDAP por cuentas de servicio (`(&(objectClass=user)(servicePrincipalName=*))`) inmediatamente antes de emitir TGS-REQs. Alertá sobre LDAP con filtro SPN seguido dentro de 60 s por TGS-REQ anómalo desde la misma fuente.

### Fase 2 — Detectar AS-REP Roasting

Firma del operador: **AS-REQ desde una fuente para una o más cuentas, con `Pre-Authentication Type: 0`** (sin `PA-ENC-TIMESTAMP` provisto).

1. **Regla `PreAuthType=0` (máxima fidelidad).** Event 4768 con `PreAuthType=0` es, por definición, tráfico contra una cuenta con pre-authentication deshabilitada. En un entorno donde ninguna cuenta debería tener `DONT_REQ_PREAUTH`, *cualquier* evento de este tipo es una alerta inmediata de severidad alta.
   `text
   index=wineventlog EventCode=4768 PreAuthType="0"
   | lookup preauth_disabled_allowlist TargetUserName OUTPUT allowed
   | where isnull(allowed)`

2. **Regla de diversidad de fuente AS-REQ.** Una sola fuente enviando AS-REQ contra muchos usernames (especialmente contra inexistentes, que generan `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN`) es una firma de enumeración de usernames + roasting. Alertá sobre la combinación.
3. **Patrón AS-REQ + KRB-ERROR.** Un operador de roasting suele obtener una mezcla de `KRB-AS-REP` (éxito contra cuentas con pre-auth deshabilitada) y `KRB5KDC_ERR_PREAUTH_REQUIRED` (la respuesta esperada para cuentas protegidas) desde una fuente. El patrón es distintivo.

### Fase 3 — Investigación y respuesta

Cuando dispara una alerta de Fase 1 o Fase 2:

1. **Identificá el host origen.** Extraé `IpAddress` (4769) o `Source Network Address` (4768) del evento disparador. Correlacioná con DHCP y AD computer logs para identificar el host.
2. **Traé todos los eventos Kerberos desde esa fuente en las últimas 24 horas.** Construí la línea de tiempo de actividad del operador.
3. **Hasheá la línea de tiempo.** Si la fuente también hizo enumeración LDAP, enumeración de sesiones SMB o queries ACL estilo BloodHound en la misma ventana, estás viendo un foothold autenticado haciendo reconocimiento AD ([[bloodhound-attack-path-analysis|BloodHound]]).
4. **Determiná el alcance de compromiso.**
   - Para Kerberoasting: cada cuenta cuyo TGS fue pedido en la línea de tiempo debe considerarse "hash potencialmente exfiltrado, contraseña potencialmente crackeable" hasta demostrar lo contrario. Rotá la contraseña de cada cuenta afectada.
   - Para AS-REP roasting: las cuentas objetivo nombradas deben rotarse *y* debe limpiarse el flag `DONT_REQ_PREAUTH`.
5. **Deshabilitá la cuenta origen.** Hasta poder demostrar que la fuente es legítima o remediarla, tratala como hostil.
6. **Abrí un ticket IR** con: eventos disparadores, host/IP/user origen, lista de cuentas de servicio afectadas, estado de rotación de cada una, snapshot de output de BloodHound.

## Claves de validación

- **Kerberoasting de alta confianza:** una cuenta origen pide TGS para >= 5 cuentas de servicio distintas dentro de 60s, con tipo de cifrado RC4-HMAC contra un entorno con baseline AES.
- **AS-REP roasting de alta confianza:** Event 4768 con `PreAuthType=0` contra cualquier cuenta que *no* esté en la allowlist explícita.
- **Honey account disparada:** TGS-REQ o AS-REQ contra el honey SPN/account. Falso positivo casi cero; investigalo inmediatamente como actividad adversaria confirmada.
- **Cluster behavioral:** la misma source IP que disparó la alerta Kerberos también hizo enumeración LDAP con filtro SPN o queries ACL estilo BloodHound en la misma ventana. Confirma actividad de fase recon.
- **Evidencia de cracking:** si el operador crackeó exitosamente la contraseña de una cuenta de servicio, podés ver un éxito `4768` (TGT request) desde una source IP *distinta* usando la credencial de esa misma cuenta dentro de horas. Listo para detección.

## Mitigación / remediación

Del lado defensor, estos son controles durables (no fixes por alerta):

- **Migrá todas las cuentas de servicio a Group Managed Service Accounts (gMSA).** Las contraseñas gMSA son valores random de 240 bytes rotados por AD con una cadencia, lo que vuelve inviable el cracking offline sin importar el tipo de cifrado. Ver [[gmsa-and-modern-service-account-hardening|gMSA y hardening moderno de cuentas de servicio]] para la disciplina de migración.
- **Forzá tipos de cifrado AES-only en todo el domain** (`KerberosEncryptionTypes` GPO seteado solo a AES128/AES256). Elimina la ventaja de cracking de RC4. Incluso una contraseña débil se vuelve impracticable de crackear en tiempos reales contra AES-PBKDF2.
- **Remové `DONT_REQ_PREAUTH` de cada cuenta.** La query de bitmask (`(userAccountControl:1.2.840.113556.1.4.803:=4194304)`) devuelve la lista. Rehabilitá pre-auth o deshabilitá la cuenta. El estado saludable a largo plazo es cero cuentas con pre-auth deshabilitada.
- **Remové cuentas de servicio privilegiadas de grupos Tier 0.** Las cuentas de servicio no deberían estar en `Domain Admins`. Punto. Ver [[tier-zero-administration-and-paw|Administración Tier 0]] para el encuadre estructural.
- **Honey accounts.** Plantá una cuenta de servicio falsa con SPN seteado y otra con `DONT_REQ_PREAUTH`. Ambas con contraseñas random fuertes que nadie usa. Cualquier TGS-REQ o AS-REQ para cualquiera de ellas es, por definición, actividad adversaria.
- **Deshabilitá NTLMv1 en todo el domain.** Los hashes AS-REP y TGS a veces pueden degradarse a NTLMv1 en escenarios cross-trust. Bloqueá NTLMv1 directamente.

### Qué no funciona como defensa primaria

- **Bloquear Kerberos outbound.** Kerberos *es* el protocolo de autenticación; no podés bloquearlo sin romper AD.
- **Renombrar cuentas de servicio con nombres oscuros.** LDAP devuelve el atributo canónico. Security by obscurity.
- **Confiar en que "auditamos hace un año".** Los flags `userAccountControl` drift-ean; se crean nuevas cuentas de servicio con contraseñas débiles; nuevas instalaciones de Exchange otorgan permisos inesperados. La cadencia de auditoría debe ser trimestral.
- **Deshabilitar binarios Mimikatz / Impacket.** El protocolo es la superficie de ataque, no la herramienta. Blocklistear tools es una táctica de demora, no una defensa.
- **Confiar en bajo volumen de alertas.** Un *solo* TGS-REQ para `krbtgt` o un *solo* evento `PreAuthType=0` es la firma. Los umbrales volumétricos pierden al operador quirúrgico.

## Logging / forensics

- **Retené DC Security logs por >= 90 días.** Cadenas roasting -> cracking -> reuse suelen abarcar días o semanas. Sin retención, la cadena queda invisible.
- **Etiquetá cada alerta con:** cuenta origen, source IP, cuentas de servicio objetivo, tipo de cifrado, estado de allowlist (¿era una cuenta esperada con pre-auth deshabilitada?). Estos tags alimentan análisis de tendencias.
- **Capturá el intercambio TGS-REQ / TGS-REP completo cuando sea posible.** Wireshark en un Domain Controller durante una alerta activa te da el payload exacto del request del operador; útil para fingerprinting de herramienta y forensics.
- **Correlacioná con [[attack-path-correlation-and-kill-chain-observability|correlación de attack paths]] a través de la cadena.** Un evento Kerberoast aislado es sospechoso; un evento Kerberoast seguido días después por una credencial crackeada autenticando desde otra source IP es una kill chain confirmada.

## Seguridad operativa

- **nunca** deshabilites una cuenta de servicio "por las dudas" sin coordinar con el equipo de la aplicación. Cuentas de servicio en runners de producción pueden causar outages.
- **nunca** dependas de una sola regla de detección. Alerta de Fase 1 + correlación de enumeración LDAP + desviación behavioral produce hallazgos de mucha mayor fidelidad que cualquier regla aislada.
- **siempre** mantené una allowlist escrita de cuentas con configuraciones legítimas de pre-auth deshabilitada o tipo de cifrado débil. Sin eso, cada alerta puede ser un falso positivo.
- **siempre** rotá la contraseña de cada cuenta de servicio Kerberoasteada como parte de la remediación, incluso si creés que el operador no pudo crackearla. El hash fue exfiltrado; la única respuesta durable es rotación.
- **siempre** probá las reglas de detección contra un lab interno autorizado ejecutando los ataques ofensivos antes de depender de ellas. Las reglas sin probar son teatro.

## Notas relacionadas

- [[kerberoasting|Kerberoasting]] — la mitad ofensiva del playbook de Fase 1.
- [[as-rep-roasting|AS-REP Roasting]] — la mitad ofensiva del playbook de Fase 2.
- [[bloodhound-attack-path-analysis|BloodHound]] — la herramienta de recon que el operador suele combinar con estos ataques; la correlación de alertas encuentra ambas cosas.
- [[dcsync-and-ntdsdit-extraction|DCSync]] — el final de partida después de que una contraseña crackeada de cuenta de servicio entrega derechos DCSync.
- [[gmsa-and-modern-service-account-hardening|Hardening gMSA]] — la mitigación estructural referenciada repetidamente arriba.
- [[tier-zero-administration-and-paw|Administración Tier 0]] — la defensa estructural que vuelve imposible la cadena de escalada post-Kerberoast.
- [[behavioral-detection-vs-signature-detection|Detección behavioral vs detección por firmas]] — el encuadre correcto para telemetría de ataques AD.
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths]] — correlación multi-stage entre recon + Kerberoast + reuse de credencial crackeada.
- [[run-scan-pipeline]] y [[detect-external-scan-pipeline]] — el patrón paralelo de pares offense/defense que este playbook sigue.
- [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]] — el metaprincipio.

## Referencias

- **Fundacional:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Fundacional:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
- **Research / Deep Dive:** Microsoft Threat Intelligence — How attacks abuse Kerberos: detection and mitigations — https://www.microsoft.com/en-us/security/blog/2022/01/26/evolving-kerberos-attack-detection/
