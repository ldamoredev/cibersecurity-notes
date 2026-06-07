# DCSync and ntds.dit Extraction

## Definición

DCSync es un ataque de extracción de credenciales AD donde el atacante abusa de los derechos de replicación del directorio **`DS-Replication-Get-Changes-All`** y relacionados para hacer que su host actúe como un Domain Controller y solicitar copias replicadas de hashes de contraseñas para cualquier principal del dominio — incluyendo la cuenta **`krbtgt`**, cuyo hash es la clave maestra que Kerberos usa para cifrar cada Ticket Granting Ticket. **La extracción de ntds.dit** es la variante offline: copiar el archivo de la base de datos AD y el hive del registro SYSTEM desde un DC (o sus backups) para recuperar los mismos hashes sin usar el protocolo de replicación. Ambas producen una salida idéntica: los hashes NTLM y claves AES de cada cuenta en el dominio, que es el *endgame* canónico de un compromiso AD.

## Por qué importa

DCSync es lo que convierte "comprometí un admin una vez" en "control perpetuo del dominio". La recuperación del hash de `krbtgt` habilita **Golden Tickets** — TGTs falsificados por el atacante válidos para cualquier usuario en cualquier grupo, con una duración de 10 años por defecto. La recuperación de un hash de service account habilita **Silver Tickets** — falsificaciones TGS con scope de servicio. La recuperación de los hashes NTLM de cada usuario habilita movimiento lateral Pass-the-Hash a todo el dominio.

El ataque importa como nota de aprendizaje porque expone tres hechos incómodos sobre AD:

- **La replicación AD en sí misma es la superficie de ataque.** DCSync no explota una vulnerabilidad — está usando el protocolo de replicación documentado igual que dos DCs lo usan cada minuto. El bug es quién tiene los derechos, no lo que hace el protocolo.
- **`krbtgt` es el secreto más valioso en cualquier entorno AD.** La recomendación de Microsoft es rotar `krbtgt` *dos veces en secuencia* (con espera de replicación entre rotaciones) después de cualquier compromiso sospechado. La mayoría de los entornos nunca lo han rotado.
- **DCSync es el punto de conexión más limpio entre las notas AD existentes.** [[bloodhound-attack-path-analysis|BloodHound]] expone los principales con derechos DCSync; [[kerberoasting|Kerberoasting]] y [[as-rep-roasting|AS-REP Roasting]] frecuentemente aterrizan en service accounts que ya tienen derechos de replicación vía Exchange legacy u otras delegaciones.

## Cómo funciona

DCSync se reduce a **4 pasos**:

1. **Identificar un principal con derechos de replicación.** ACEs requeridas en el objeto de dominio: `DS-Replication-Get-Changes` (GUID `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`) y `DS-Replication-Get-Changes-All` (GUID `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`). Los Domain Controllers y Domain Admins los tienen por diseño; el ataque funciona cuando *otros* principales también los tienen — usualmente vía instalación de Exchange legacy, Azure AD Connect, o delegaciones por error. La consulta pre-construida de BloodHound "Find Principals with DCSync Rights" es la enumeración canónica.
2. **Autenticarse como el principal privilegiado.** Ya sea teniendo su credencial directamente, recuperando su hash vía Pass-the-Hash, o kerberoasteando/AS-REP-roasteando su cuenta (la cadena típica).
3. **Emitir el RPC de replicación.** Las herramientas llaman al opcode `IDL_DRSGetNCChanges` de la interfaz RPC `DRSUAPI` (MS-DRSR — Directory Replication Service Remote Protocol). El DC obedece porque el caller tiene las ACEs correctas.
4. **Falsificar tickets y pivotar.** Con el hash de `krbtgt` → Golden Ticket. Con un hash de service account → Silver Ticket. Con hashes de usuarios → movimiento lateral Pass-the-Hash.

Secuencia representativa de punta a punta desde un foothold Linux:

```
# Después de que Kerberoasting produjo una service account con derechos de replicación:
impacket-secretsdump LAB.LOCAL/svc_replication:'CrackedPassword!'@10.0.0.1 \
    -just-dc-user krbtgt
# Salida:
#   krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>:::
#   Kerberos keys grabbed: aes256-cts-hmac-sha1-96, aes128-cts-hmac-sha1-96, des-cbc-md5
```

**La extracción de ntds.dit** es la variante offline:

1. Ejecución de código y derechos de admin en un Domain Controller (o acceso a backups DC, snapshots VSS, o una copia restaurada).
2. Copiar `C:\Windows\NTDS\ntds.dit` (la base de datos ESE que contiene todos los datos AD) más el hive del registro SYSTEM.
3. Parsear offline con `secretsdump -ntds ntds.dit -system SYSTEM LOCAL`.

## Técnicas / patrones

- **Siempre hacer BloodHound primero.** `MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. La lista de resultados debería contener Domain Controllers y Domain Admins. Cualquier otra cosa es una mala configuración Y tu ruta más corta al endgame.
- **`-just-dc` vs `-just-dc-user`.** `secretsdump.py -just-dc <target>` vuelca **cada** hash en el dominio — ruidoso y pobre en OPSEC. `-just-dc-user krbtgt` vuelca solo la cuenta nombrada. El uso avanzado extrae solo lo que se necesita para el siguiente paso.
- **Las instalaciones de Exchange son una fuente recurrente de principales DCSync no intencionados.** Instalar Exchange históricamente otorgó a `Exchange Trusted Subsystem`, `Exchange Windows Permissions` y grupos relacionados derechos AD elevados incluyendo (en versiones pre-2019) DCSync efectivo.
- **La rotación de `krbtgt` es innegociable después del compromiso.** Dos veces, en secuencia, con espera de replicación entre rotaciones.
- **La extracción de ntds.dit desde VSS es una alternativa sigilosa.** `vssadmin create shadow /for=C:` → montar shadow → copiar ntds.dit + hive SYSTEM → parsear offline. Evita el RPC DRSUAPI completamente, así que las reglas de detección de DCSync lo pasan por alto.
- **OPSEC: DCSync es ruidoso por defecto.** Cada llamada `IDL_DRSGetNCChanges` aterriza en el Event 4662 en el DC, con un GUID reconocible.

## Variantes y bypasses

La extracción de credenciales tipo DCSync tiene **4 variantes importantes**.

### 1. DCSync clásico vía DRSUAPI

El flujo descripto arriba. Mimikatz `lsadump::dcsync` (Windows) o Impacket `secretsdump.py` (Linux). La variante por defecto y más detectada.

### 2. Extracción de ntds.dit + hive SYSTEM

Offline, sin tráfico DRSUAPI. Requiere ejecución de código en un DC (o acceso a su backup). Evita la regla de detección de DCSync canónica.

### 3. DCShadow

Ataque diferente, misma familia. En lugar de *solicitar* datos replicados, el atacante *registra su host como un Domain Controller* y *empuja* cambios en AD que los DCs reales aceptan como replicación legítima. Mucho más difícil de detectar que el DCSync clásico.

### 4. DCSync cross-domain vía trusts

En forests multi-dominio con trusts de dos vías transitivos, los derechos DCSync en un dominio a veces otorgan replicación efectiva en otro.

## Impacto

Ordenado por severidad real típica:

- **Compromiso de dominio permanente vía Golden Ticket.** El impacto definitorio. El hash de `krbtgt` recuperado permite al atacante forjar TGTs válidos para cualquier principal en cualquier grupo, duración de 10 años por defecto.
- **Compromiso forest-wide vía trusts cross-domain.** Si el dominio comprometido está en un forest con un dominio raíz de confianza, los Golden Tickets en el dominio hijo frecuentemente impersonan identidades equivalentes a enterprise-admin en todo el forest.
- **Movimiento lateral Pass-the-Hash a cada endpoint.** Los hashes NTLM recuperados funcionan directamente con SMB, WinRM, RDP (vía restricted-admin), MSSQL y cualquier servicio que confíe en NTLM.
- **Silver Tickets para persistencia sigilosa específica de servicio.** Hash de service account → [[silver-ticket-and-service-account-persistence|falsificación TGS con scope de servicio]].
- **Pérdida total del suelo forense.** Una vez comprometido `krbtgt`, cada evento de autenticación en el dominio es forensicamente sospechoso.

## Detección y defensa

Ordenado por efectividad:

1.
**Auditá las ACEs `DS-Replication-Get-Changes-*` trimestralmente vía BloodHound.**
   La corrección definitiva. `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. Cada principal que no sea un Domain Controller o Domain Admin es un hallazgo.

2.
**Detección de comportamiento sobre Event ID 4662 con los GUIDs de replicación.**
   El DC loggea el Event 4662 en cada `IDL_DRSGetNCChanges`. Filtrar para `{Properties[8]}` que contenga `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` o `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`. Regla de detección: cualquier fuente que **no** sea una cuenta de computadora Domain Controller realizando estas solicitudes es una alerta de alta confianza. Los falsos positivos son esencialmente zero en un entorno saludable.

3.
**Rotar `krbtgt` dos veces anualmente como higiene estándar — y dos veces en secuencia inmediatamente después de cualquier compromiso sospechado.**

4.
**Detectar acceso a ntds.dit en Domain Controllers.**
   La variante offline saltea DRSUAPI pero requiere acceso a nivel de archivo a `ntds.dit` o operaciones VSS shadow. Reglas EDR sobre `vssadmin create shadow`, sobre aperturas directas de `C:\Windows\NTDS\ntds.dit`, y sobre invocaciones de `ntdsutil` capturan esta variante.

5.
**Implementar administración Tier 0 y Privileged Access Workstations.**
   La defensa estructural. Si las cuentas capaces de DCSync nunca se loguean a hosts de menor tier, sus credenciales no pueden ser robadas vía Pass-the-Hash, Mimikatz desde LSASS, o Kerberoasting.

### Qué no funciona como defensa primaria

- **Confiar en que "solo los DCs tienen derechos de replicación."** Verificar con la consulta BloodHound arriba.
- **Rotar `krbtgt` una vez.** El historial de contraseñas mantiene el hash anterior válido.
- **Bloqueos a nivel de red en DRSUAPI.** Los DCs deben poder replicar; bloquear el protocolo rompe el directorio.
- **Renombrar `krbtgt`.** No puede renombrarse; el sam account name es estructural.

## Labs prácticos

Ejecutar solo contra entornos lab propios o engagements autorizados.

```
# Lab 1 — Identificar principales capaces de DCSync en un AD lab vía BloodHound Cypher.
MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain)
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
# Los DCs y Domain Admins deberían aparecer. Cualquier otro principal es un hallazgo.
```

```
# Lab 2 — DCSync del hash krbtgt desde un host Linux con credenciales de admin.
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 \
    -just-dc-user krbtgt
```

```
# Lab 3 — Forjar un Golden Ticket desde el hash krbtgt del lab.
impacket-ticketer -nthash <KRBTGT_NTLM_HASH> \
    -domain-sid S-1-5-21-<LAB-DOMAIN-SID> \
    -domain LAB.LOCAL Administrator
export KRB5CCNAME=Administrator.ccache
impacket-psexec LAB.LOCAL/Administrator@DC01.lab.local -k -no-pass
```

```
# Lab 4 — Extracción de ntds.dit vía VSS (ejecutar en un DC lab con admin).
vssadmin create shadow /for=C:
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\extract\
reg save HKLM\SYSTEM C:\extract\SYSTEM
impacket-secretsdump -ntds C:\extract\ntds.dit -system C:\extract\SYSTEM LOCAL
```

```
# Lab 5 — Detección del lado defensor: Event 4662 con GUIDs de replicación.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 200 |
    Where-Object {
        $_.Properties[8].Value -match '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2' -or
        $_.Properties[8].Value -match '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'
    } |
    Select-Object TimeCreated, @{n='Subject';e={$_.Properties[3].Value}}
```

## Ejemplos prácticos

- **Endgame de engagement desde Kerberoasting.** El operador kerberoastea `svc_replication` (una service account de 2017 con `GenericAll` en el objeto de dominio otorgado por error). Crackea la contraseña, realiza DCSync de `krbtgt`, forja un Golden Ticket para `Domain Admin`. Cadena total: phish → Kerberoast → DCSync → Golden Ticket. 6 horas.
- **Detección DCSync atrapa a un red team.** El defensor alerta sobre `Event 4662` con los GUIDs de replicación desde una IP no-DC. En minutos el SOC rastrea la fuente a una workstation en el departamento IT, bloquea la cuenta del usuario y termina el engagement.

## Notas relacionadas

- [[kerberoasting]] — el ataque *predecesor* típico.
- [[bloodhound-attack-path-analysis]] — la herramienta de targeting; su consulta "Principals with DCSync Rights" es el paso de enumeración canónico.
- [[golden-ticket-and-krbtgt-compromise]] — la ruta de abuso post-DCSync de la raíz de confianza Kerberos.
- [[krbtgt-rotation-and-tier-zero-recovery]] — la operación de recuperación requerida cuando DCSync puede haber expuesto `krbtgt`.
- [[pass-the-hash-and-ntlm-credential-reuse]] — la ruta de reutilización de credenciales directa después de que DCSync devuelve hashes NTLM.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — la detección DCSync es puramente de comportamiento.

## Referencias

- **Fundamental:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Fundamental:** Microsoft — AD DS Replication permissions and how to audit them — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
