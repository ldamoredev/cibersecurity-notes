# Pass-the-Hash and NTLM Credential Reuse

## Definición

Pass-the-Hash (PtH) es la técnica de autenticarse a un servicio que habla NTLM usando **el hash NT de la contraseña de un usuario directamente**, sin necesitar conocer ni crackear la contraseña en texto plano. La técnica existe porque NTLM usa el hash NT en sí mismo como el secreto de autenticación de largo plazo — el hash es funcionalmente equivalente a la contraseña. PtH es el seguimiento canónico a la extracción de credenciales ([[dcsync-and-ntdsdit-extraction|DCSync]], dump de LSASS, [[kerberoasting|Kerberoasting]] cuando la cuenta recuperada usa NTLM): no necesitás crackear lo que ya extrajiste.

## Por qué importa

PtH es lo que convierte "dumpée 50.000 hashes NTLM de un DC" en "me logueé como cada usuario en el dominio". Es el *uso* más directo de las credenciales extraídas por cada otro ataque AD en esta rama. Sin entender PtH, la cadena desde foothold inicial → DCSync se detiene en "tengo un archivo lleno de hashes" y el operador se pierde toda la fase de post-explotación.

La técnica también importa como nota de aprendizaje porque expone tres hechos senior transferibles sobre la autenticación de Windows:

- **El hash NT *es* la contraseña.** No hay un paso extra de derivación en el momento de autenticación — NTLM hashea la contraseña una vez con MD4, y el valor resultante de 16 bytes es lo que se usa para cada autenticación posterior. Recuperar el hash desde cualquier fuente es equivalente a conocer la contraseña.
- **NTLM sigue siendo ubicuo.** Incluso en entornos "Kerberos-first", el fallback a NTLM ocurre en SMB hacia direcciones IP (sin SPN), aplicaciones legacy, escenarios cross-trust, cuentas locales en servidores miembro, y cualquier servicio que negocie explícitamente NTLM. La afirmación de "usamos Kerberos" casi siempre es parcial.
- **Deshabilitar NTLM es un proyecto de varios años.** Microsoft ha estado deprecando NTLM desde Windows 2000. A fecha de 2026, la deshabilitación completa es factible en entornos greenfield y aspiracional en entornos establecidos. El framing senior es que la mitigación de NTLM es un *gradiente* (Credential Guard → NTLM restringido → solo auditoría → bloqueado), no un switch.

## Cómo funciona

PtH se reduce a **3 pasos**:

1. **Obtener el hash NT.** Fuentes: [[dcsync-and-ntdsdit-extraction|DCSync]] para cualquier usuario del dominio, dump de memoria de LSASS en cualquier host donde el usuario haya iniciado sesión, extracción de la base de datos SAM en una máquina local, [[kerberoasting|Kerberoasting]] / [[as-rep-roasting|AS-REP Roasting]] *si* la contraseña recuperada se crackea para derivar el hash (raro — los operadores usualmente usan la contraseña recuperada directamente).
2. **Reemplazar la contraseña con el hash en el intercambio de autenticación.** Cada cliente que habla NTLM soporta esto; las herramientas relevantes (Impacket `psexec.py`, `smbexec.py`, `wmiexec.py`, `secretsdump.py`; CrackMapExec; Evil-WinRM) todas aceptan sintaxis `-hashes <LM>:<NT>` en lugar de `-password`.
3. **Autenticarse a un servicio que confía en la identidad del usuario.** SMB (file shares, admin shares), WinRM (PowerShell remoting), MSSQL (cuando la autenticación SQL está deshabilitada), MS-RPC (DCOM, SCM para control de servicios), HTTP (IIS con auth NTLM), y muchas aplicaciones internas. El servicio no tiene forma de distinguir PtH de un login normal — el intercambio NTLM es byte-idéntico.

Secuencia representativa de punta a punta:

```
# Después de que DCSync extrajo el hash para la cuenta de Administrador local:
impacket-psexec -hashes :ABC123...DEF456 LAB.LOCAL/Administrator@10.0.0.5
# Aterriza como NT AUTHORITY\SYSTEM en 10.0.0.5 sin conocer una contraseña en texto plano.

# Movimiento lateral vía WMI, misma sintaxis:
impacket-wmiexec -hashes :ABC123...DEF456 LAB.LOCAL/Administrator@10.0.0.10

# CrackMapExec para validación tipo spray en muchos hosts:
crackmapexec smb 10.0.0.0/24 -u Administrator -H ABC123...DEF456 --local-auth
```

El bug no es "NTLM está roto criptográficamente" (MD4 está roto pero no de manera que importe para PtH); es *el hash es la credencial — extraerlo una vez permite reutilización perpetua durante la vida útil de la contraseña*.

## Técnicas / patrones

- **`-hashes :<NT>` es la sintaxis canónica de Impacket.** La mitad LM casi siempre está vacía en AD moderno (los hashes LM han estado deshabilitados por defecto desde Windows Vista); pasá un string vacío antes de los dos puntos.
- **Autenticación local vs de dominio es la primera decisión.** `--local-auth` (CrackMapExec) y la ausencia de un prefijo de dominio (Impacket) autentican contra la base de datos SAM local; con un prefijo de dominio autenticás contra AD. La reutilización de contraseña del admin local en una flota es la cadena clásica (un admin local comprometido = cada host con la misma contraseña).
- **CrackMapExec es la herramienta de amplitud.** `crackmapexec smb 10.0.0.0/24 -u Administrator -H <hash>` valida el hash contra cada host en un rango en segundos. Te dice exactamente en qué hosts funciona la credencial.
- **Evil-WinRM es la herramienta de profundidad.** Una vez que tenés un hash funcionando para un host con WinRM habilitado, `evil-winrm -i HOST -u user -H <hash>` da una sesión completa de PowerShell para operación hands-on.
- **PtH se encadena con Over-Pass-the-Hash para escalar a Kerberos.** Con el hash NT, podés solicitar un TGT de Kerberos (Rubeus `asktgt /user:X /rc4:<NT>`). El TGT luego maneja servicios solo-Kerberos que rechazan NTLM. Over-PtH es el puente de NTLM a Kerberos con el mismo material de credencial.
- **Las claves AES son el equivalente moderno.** Las versiones más nuevas de Windows cachean claves Kerberos AES128/AES256 en lugar de (o junto con) el hash NT. Pass-the-Key con claves AES es la técnica equivalente.
- **OPSEC: la auth NTLM en un servidor es ruidosa.** Cada PtH exitoso genera el Event 4624 con LogonType=3 (red) y AuthenticationPackage=NTLM. Los defensores maduros alertan sobre auth NTLM donde no debería ocurrir.

## Variantes y bypasses

Las técnicas de la familia PtH se agrupan en **5 variantes** por material de credencial.

### 1. Pass-the-Hash clásico (NTLM)

Usar el hash NT para autenticación NTLM directamente. La técnica original, todavía ubicua. Funciona contra SMB, WinRM, MSSQL, MS-RPC, IIS y cualquier servicio que acepte NTLM.

### 2. Over-Pass-the-Hash (NTLM → Kerberos)

Usar el hash NT (o clave AES) para solicitar un TGT de Kerberos, luego usar el TGT para servicios solo-Kerberos. El puente del material de credencial NTLM a auth Kerberos. Requerido cuando los servicios objetivo rechazan NTLM (hardening moderno) pero todavía confían en Kerberos.

### 3. Pass-the-Ticket

Saltear el paso de reutilización de credenciales completamente — usar un ticket Kerberos (TGT o ticket de servicio) directamente, exportado de la memoria de un host comprometido vía Mimikatz/Rubeus. No se requiere contraseña ni hash; el ticket en sí mismo es la credencial bearer por su duración.

### 4. Pass-the-Key (claves AES de Kerberos)

Lo mismo que Over-PtH pero usando claves AES128/AES256 cacheadas en lugar del hash NT. Windows moderno cachea claves AES; en hosts donde el hash NT no está en LSASS pero las claves AES sí están, este es el único camino hacia adelante.

### 5. Reutilización de contraseña de admin local en una flota

La variante operativamente más simple — extraer el hash del Administrador local de una workstation, hacer spray contra el resto con `crackmapexec --local-auth`. Si la organización despliega workstations desde una imagen común con la misma contraseña de admin local, toda la flota cae en minutos. LAPS es la defensa estructural.

## Impacto

Ordenado por severidad real típica:

- **Movimiento lateral a cada host que el usuario puede alcanzar.** PtH contra domain admin da acceso admin a cada host unido al dominio. PtH contra una service account da lo que la service account puede alcanzar. PtH contra un usuario de workstation da la sesión de ese usuario en todos lados.
- **Persistencia Silver Ticket desde un hash de service account.** Hash de service account recuperado → forjar tickets TGS de Kerberos con scope de servicio → acceso persistente específico de servicio que no requiere más contacto con el KDC. Ver [[silver-ticket-and-service-account-persistence]].
- **Pivot cross-domain en escenarios de trust.** Hacer PtH del hash de un domain admin en un dominio, usar Over-PtH para solicitar un TGT para un dominio de confianza, pivotar al dominio de confianza.
- **Cadena de impersonación MSSQL.** Hacer PtH de una service account que es dueña de una cadena linked-server SQL Server → ejecutar como la identidad del linked-server en el siguiente hop → enumerar más.
- **Pérdida de ground-truth forense.** Cada evento PtH parece un logon legítimo desde la perspectiva del usuario. Sin behavioral analytics, la atribución después del compromiso es difícil.

## Detección y defensa

Ordenado por efectividad:

1.
**Deshabilitar NTLM en hosts que puedan tolerarlo (solo-Kerberos).**
   La corrección estructural. Los hosts AD modernos que solo se comunican con clientes Windows actuales usualmente pueden correr con NTLM deshabilitado (GPO `Network security: Restrict NTLM`). Modo auditoría primero para encontrar dependencias, luego enforcement.

2.
**Microsoft Credential Guard en cada endpoint.**
   Credential Guard aísla LSASS en un contenedor Virtual Secure Mode (VSM), haciendo que la extracción de hashes en memoria (`mimikatz sekurlsa::logonpasswords`) falle. No detiene PtH contra hashes obtenidos vía DCSync, pero detiene la precondición de extracción LSASS en cada endpoint que lo tiene.

3.
**Detección de comportamiento sobre Event 4624 LogonType=3 con AuthenticationPackage=NTLM.**
   Cada evento PtH es un logon de red exitoso autenticado vía NTLM. Reglas de detección: (a) auth NTLM a hosts que deberían usar solo Kerberos; (b) auth NTLM desde pares fuente/destino inesperados; (c) auth NTLM usando admin local desde un host que no debería tener esa cuenta en uso.

4.
**Grupo Protected Users para cuentas sensibles.**
   Agregar un usuario al grupo Protected Users deshabilita NTLM, LM, DES y RC4 para ese usuario; fuerza Kerberos con AES; previene que las credenciales cacheadas de largo plazo se almacenen en hosts miembro. El hardening por-cuenta de mayor impacto para admins Tier 0 / Tier 1. Ver [[tier-zero-administration-and-paw]].

5.
**LAPS para romper la reutilización de contraseña del admin local.**
   LAPS rota la contraseña del Administrador local por-host a un valor único aleatorio almacenado en AD. Elimina la variante "un hash de admin local → toda la flota". Microsoft Windows LAPS (incorporado en Windows 11 / Server 2022+) reemplaza la herramienta legacy MS LAPS.

6.
**NTLMv1 debe bloquearse completamente.**
   NTLMv1 está criptográficamente roto — filtra el hash NT vía el challenge/response de red. Bloquear NTLMv1 en la política de dominio (`LmCompatibilityLevel = 5`); cualquier intento NTLMv1 es un indicador que vale alerta.

### Qué no funciona como defensa primaria

- **Cambiar contraseñas frecuentemente** sin abordar la primitiva de extracción de hashes. El hash es la credencial; la rotación de contraseñas *sí* invalida hashes previamente extraídos, pero solo al ritmo de la rotación.
- **Políticas de contraseñas fuertes** como defensa PtH. El atacante tiene el hash, no la contraseña.
- **Políticas de lockout de cuenta.** PtH usa credenciales válidas y no dispara lockout.
- **Segmentación de red sola.** Útil para limitar el blast radius, pero no previene PtH dentro de un segmento.
- **Confiar en que "usamos Kerberos".** Auditá los paquetes de auth reales en capturas de red reales.

## Labs prácticos

Ejecutar solo contra entornos lab propios o engagements autorizados.

```
# Lab 1 — Recuperar un hash de un DC lab autorizado vía DCSync (precondición).
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 \
    -just-dc-user testuser
# Línea de salida para el hash a usar:
#   testuser:1234:aad3b435b51404eeaad3b435b51404ee:ABC...XYZ:::
```

```
# Lab 2 — Pass-the-Hash vía SMB a objetivo lateral.
impacket-psexec -hashes aad3b435b51404eeaad3b435b51404ee:ABCXYZ \
    LAB.LOCAL/testuser@10.0.0.10
# Debería aterrizar como testuser en 10.0.0.10 sin proveer una contraseña.
```

```
# Lab 3 — Spray de hash en una subred (amplitud de validación).
crackmapexec smb 10.0.0.0/24 \
    -u Administrator -H ABCXYZ --local-auth
# Salida: líneas verdes Pwn3d! para cada host donde funciona el hash de admin local.
```

```
# Lab 4 — Over-Pass-the-Hash para obtener un TGT de Kerberos.
# En host operador Windows con Rubeus:
Rubeus.exe asktgt /user:testuser /rc4:ABCXYZ /domain:LAB.LOCAL /nowrap
# Luego usar el TGT base64 resultante con /ptt para inyectar y acceder a servicios solo-Kerberos.
```

```
# Lab 5 — Detección del lado defensor: auditoría de eventos de auth NTLM.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 200 |
    Where-Object {
        $_.Properties[8].Value -eq 3 -and           # LogonType 3 (Red)
        $_.Properties[10].Value -eq 'NTLM'          # AuthenticationPackage
    } |
    Select-Object TimeCreated,
        @{n='User';e={$_.Properties[5].Value}},
        @{n='SourceIP';e={$_.Properties[18].Value}},
        @{n='Target';e={$_.Properties[6].Value}}
# Cada línea es un evento candidato de PtH. Construí alertas en pares anómalos (User, SourceIP).
```

```
# Lab 6 — Verificar que Credential Guard bloquea el dump de LSASS.
# En un endpoint lab con Credential Guard habilitado:
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
# Esperado: hashes NTLM mostrados como `n.s. (NULL)` o vacíos — LSASS aislado en VSM previene la extracción.
# Sin Credential Guard: los hashes se muestran en hex claro.
```

## Ejemplos prácticos

- **DCSync → compromiso de flota en minutos.** El operador hace DCSync de `Domain Admin` y una OU llena de service accounts. `crackmapexec smb 10.0.0.0/16 -u svc_replication -H <hash> --local-auth` aterriza en 2.400 hosts en tres minutos.
- **PtH encadenado de service account a impersonación SQL.** Kerberoasting produce la contraseña de `svc_appdb`. El operador usa la contraseña (o su hash NT derivado) para autenticarse al SQL Server que aloja la cadena linked-server → `xp_cmdshell` como la service account SQL → lateral al host que corre otro objetivo linked-server.
- **Reutilización de admin local contra una flota con imagen.** El pentester recupera el hash del Administrador local de una workstation. La organización desplegó workstations desde una imagen de 2019 con la misma contraseña de admin local. CrackMapExec confirma: 800 de 850 workstations aceptan el hash. LAPS habría eliminado esto en un cambio de configuración.
- **Credential Guard salva el día.** Misma flota, 18 meses después, después del rollout de Credential Guard. El operador compromete una workstation pero no puede extraer ningún hash de LSASS. El movimiento lateral requiere volver a AD (DCSync desde una cuenta privilegiada) — mucho más ruidoso, mucho más detectable.

## Notas relacionadas

- [[kerberoasting]] — PtH es una de las principales formas de usar una credencial kerberoasteada cuando el servicio objetivo habla NTLM en lugar de Kerberos.
- [[as-rep-roasting]] — igual: la credencial recuperada frecuentemente aterriza en flujos de trabajo PtH.
- [[bloodhound-attack-path-analysis]] — las aristas `AdminTo` y `CanRDP` de BloodHound describen exactamente qué hosts alcanza una credencial PtH.
- [[dcsync-and-ntdsdit-extraction]] — DCSync produce la salida de hash NTLM masiva que PtH consume; esta nota es "qué hacés con la salida de DCSync".
- [[silver-ticket-and-service-account-persistence]] — Silver Tickets y PtH usan el mismo hash de service account recuperado; la elección es "persistir vía Silver Ticket" vs "reutilizar activamente vía PtH".
- [[gmsa-and-modern-service-account-hardening]] — las cuentas gMSA mitigan PtH de service accounts rotando sus contraseñas automáticamente.
- [[tier-zero-administration-and-paw]] — la defensa estructural contra PtH que termina en Tier 0.

## Referencias

- **Fundamental:** MITRE ATT&CK T1550.002 — Use Alternate Authentication Material: Pass the Hash — https://attack.mitre.org/techniques/T1550/002/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Pass the Hash and Windows Authentication — https://adsecurity.org/?p=3278
- **Hardening:** Microsoft Learn — Mitigating Pass-the-Hash and other credential theft techniques — https://www.microsoft.com/en-us/download/details.aspx?id=36036
