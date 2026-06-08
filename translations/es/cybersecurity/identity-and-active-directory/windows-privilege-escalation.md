# Windows Privilege Escalation

## Definición

La escalada de privilegios en Windows es la operación post-foothold de moverse de un contexto de usuario Windows de baja integridad/bajo privilegio a uno más alto — típicamente de una cuenta de grupo `Users` estándar a `Administrators`, `SYSTEM` o una identidad Tier 0. A diferencia de la privesc por exploit de kernel (rara en Windows moderno parcheado), la superficie canónica de privesc en Windows en 2026 está **dirigida por mal configuración**: ACLs de servicios, rutas sin comillas, directorios escribibles en `PATH`, scheduled tasks, AlwaysInstallElevated, credenciales almacenadas, abuso de privilegios de token y DLL hijacking. El trabajo es disciplina de enumeración, no escritura de exploits.

## Por qué importa

La escalada de privilegios local en Windows es el puente entre un foothold inicial (phish, password spray, servicio expuesto) y la superficie de ataque AD que esta rama cubre. Una shell de usuario estándar en una workstation unida al dominio no puede Kerberoastear una service account cuyo ticket necesita `tgtdeleg`, no puede dumpear LSASS para [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]], no puede ejecutar [[bloodhound-attack-path-analysis|BloodHound]] con la colección de sesiones de SharpHound, y no puede realizar [[dcsync-and-ntdsdit-extraction|DCSync]] de forma confiable sin ya tener credenciales privilegiadas. La privesc local convierte la shell en el contexto operativo que el resto de esta rama asume.

La técnica también importa como nota de aprendizaje porque expone tres hechos senior transferibles sobre Windows:

- **Windows por defecto está lleno de malas configuraciones históricas.** Los servicios instalados por software de terceros en 2015 con ACLs débiles todavía están en cajas de producción en 2026. La enumeración de privesc es principalmente *encontrar deuda de configuración acumulada*, no encontrar nuevas vulnerabilidades.
- **`SYSTEM` no es el objetivo. La identidad correcta sí lo es.** La ofensiva moderna de Windows apunta a *la identidad que te permite hacer lo siguiente*: el admin local que ejecuta una service account, el usuario que tiene `SeBackupPrivilege`, la cuenta que es propietaria de un scheduled task con credenciales almacenadas.
- **La privesc y la detección se mueven sobre los mismos Event IDs.** Cada primitiva de privesc que tiene éxito genera una señal reconocible en Windows Event Logs — 4624 con `LogonType=2`/`5`/`10`, 4672 (privilegios especiales asignados), 4688 con un proceso padre sospechoso, 4697 (instalación de servicio), 4698 (creación de scheduled task).

## Cómo funciona

La privesc local en Windows se reduce a un **loop de 3 pasos** repetido en múltiples clases de primitivas:

1. **Enumerar.** Inventariar servicios, scheduled tasks, autoruns, ACLs de archivo en directorios del sistema, ACLs de registro en claves de control de servicios, credenciales almacenadas en Credential Manager / `cmdkey`, privilegios del usuario actual (`whoami /priv`), miembros de grupos privilegiados locales, estado del registro AlwaysInstallElevated, rutas de servicio sin comillas, directorios escribibles en `PATH`.
2. **Identificar una primitiva de alto leverage.** Hacer coincidir la salida de enumeración contra la lista canónica de clases de privesc (abajo). La mayoría de las cajas tienen múltiples primitivas encontrables; el movimiento senior es elegir la más silenciosa que produzca la identidad que necesitás.
3. **Explotar y pivotar.** Usar la primitiva elegida para: ganar derechos de administrador local, ganar la sesión de un usuario diferente (impersonación de token), o recuperar credenciales que autentican en otro lugar.

Un arranque de enumeración representativo desde una shell de bajo privilegio:

```
# Ejecutar la suite de enumeración canónica.
.\winPEASx64.exe quiet > peas.txt
.\Seatbelt.exe -group=user -outputfile=seatbelt.txt
whoami /all
net localgroup Administrators
```

## Técnicas / patrones

### El panorama de primitivas de privesc

Las clases canónicas de privesc de Windows — lo que las herramientas de enumeración exponen y lo que los operadores buscan:

| # | Clase | Mecanismo | Señal de telemetría |
| --- | --- | --- | --- |
| 1 | **Permisos de servicio débiles** | Un servicio cuyo binario o config de registro es escribible por el usuario actual. Reemplazar el binario o cambiar `ImagePath`, reiniciar, ganar `SYSTEM`. | Event 4697 (servicio instalado), 4688 (padre sospechoso) |
| 2 | **Ruta de servicio sin comillas** | Un servicio `ImagePath` como `C:\Program Files\My App\bin\service.exe` sin comillas. Si existe un directorio escribible a lo largo de la ruta, Windows puede ejecutar el binario colocado por el atacante. | Event 7045, 4688 |
| 3 | **DLL hijacking** | Un servicio o scheduled task carga una DLL por nombre sin una ruta completamente calificada; el usuario actual puede depositar una DLL maliciosa en un directorio anterior en el orden de búsqueda. | Event 4688, Sysmon Event 7 (imagen cargada) |
| 4 | **AlwaysInstallElevated** | Ambas claves de registro `HKLM` y `HKCU` configuradas a `1`. Cualquier usuario puede instalar un MSI como `SYSTEM`. | Event 1033 (MSI instalado) + 4624 LogonType=5 |
| 5 | **Impersonación de token / `SeImpersonatePrivilege`** | Las service accounts (app pools IIS, SQL Server, etc.) frecuentemente tienen `SeImpersonatePrivilege`. Herramientas como *PrintSpoofer*, *RoguePotato*, *GodPotato*, *EfsPotato* desencadenan una autenticación forzada, capturan el token, impersonan `SYSTEM`. | Event 4673 (privilegio sensible usado), 4624 LogonType=9 |
| 6 | **Credenciales almacenadas** | Contraseñas en: Credential Manager (`cmdkey /list`), Group Policy Preferences `cpassword` (legacy), archivos de instalación desatendida (`Unattend.xml`, `sysprep.inf`), claves de registro para AutoLogon. | Event 4663 (acceso a archivo) si el auditor lo habilitó |
| 7 | **Scheduled tasks** | Un task corriendo como un usuario diferente con permisos débiles: el operador modifica la línea de comando del task, el task corre como ese usuario. | Event 4698 (task creado), 4702 (task actualizado), 4688 (ejecución del task) |
| 8 | **Directorios `PATH` escribibles** | Un directorio temprano en el `PATH` del sistema que el usuario actual puede escribir. Depositar un binario con un nombre común; el próximo comando del administrador sombrea el binario real. | Event 4688 con proceso padre inesperado |
| 9 | **Bypass de UAC** | Cuando el usuario actual está en `Administrators` pero corre con token dividido (UAC restringido). Varias primitivas de bypass existen (fodhelper, computerdefaults, sdclt). | Event 4688 con padre auto-elevado |
| 10 | **Exploit de kernel** | Los kernels Windows parcheados usualmente son inexplotables; las cajas legacy / sin parches todavía tienen exploits de kernel viables (Print Nightmare, HiveNightmare). Raro en producción pero real. | Event 4624 LogonType=2, luego comportamiento anómalo |

### Patrones

- **`whoami /priv` es el one-liner de mayor señal.** Si la salida incluye `SeImpersonatePrivilege`, `SeAssignPrimaryTokenPrivilege`, `SeBackupPrivilege` o `SeRestorePrivilege`, la ruta de privesc usualmente tiene 1 paso.
- **Los contextos de service account son más fáciles que los contextos de usuario.** Comprometer un app pool de IIS o una service account de SQL Server es frecuentemente una ruta más rápida hacia `SYSTEM` que escalar desde un usuario de workstation — `SeImpersonatePrivilege` es el regalo que sigue dado.
- **Enumerar, no explotar primero.** Los operadores nuevos ejecutan un exploit de kernel porque es interesante. Los operadores senior ejecutan `winPEAS` → grep para los cuatro hallazgos canónicos (servicios escribibles, rutas sin comillas, credenciales almacenadas, AlwaysInstallElevated) → explotar el match más silencioso.
- **AppLocker / WDAC cambian el juego.** En endpoints endurecidos, el allowlisting de aplicaciones bloquea binarios soltados completamente. Los operadores cambian a primitivas basadas en PowerShell, abuso de binarios firmados (LOLBAS), o explotación en memoria.
- **Admin local raramente es el objetivo real.** El objetivo real es usualmente uno de: credenciales de dominio cacheadas en LSASS para [[pass-the-hash-and-ntlm-credential-reuse|PtH]], un ticket de service account para profundidad de [[kerberoasting|Kerberoasting]], o admin local en un servidor que aloja un servicio privilegiado.
- **OPSEC: Sysmon y EDR ven las primitivas canónicas.** La mayoría de las herramientas de privesc nombradas (winPEAS, PowerUp, la familia Potato, bypass fodhelper) son detectadas por firmas EDR predeterminadas.

## Variantes y bypasses

Las operaciones de privesc de Windows se dividen por **4 categorías de superficie de ataque**.

### 1. Primitivas de control de servicio / permisos de archivo

La mayor parte de la privesc del mundo real — ACLs de servicio débiles, rutas sin comillas, directorios escribibles, DLL hijacking. Descubribles por enumeración, corregibles por configuración.

### 2. Primitivas de privilegio de token

`SeImpersonatePrivilege`, `SeAssignPrimaryToken`, `SeBackupPrivilege`, `SeDebugPrivilege`. Existen para operación legítima del servicio; se convierten en privesc cuando se otorgan a un contexto que el atacante controla.

### 3. Primitivas de recuperación de credenciales

Dump de LSASS (Mimikatz `sekurlsa::logonpasswords`), extracción de bóveda DPAPI, stores de credenciales del navegador, GPP `cpassword`, registro AutoLogon, texto plano en scripts. Las credenciales recuperadas impulsan ataques AD posteriores.

### 4. Primitivas de kernel / bypass de UAC

Exploits de kernel (raros en sistemas parcheados pero siempre reapareciendo), bypasses de UAC (frecuentemente re-divulgados vía binarios auto-elevados con referencias hijackables).

## Impacto

Ordenado por severidad real típica:

- **Admin local / `SYSTEM` en una workstation.** Resultado directo de la mayoría de las primitivas. Habilita dump de LSASS, persistencia vía scheduled task, manipulación de registro, intentos de evasión de EDR.
- **Extracción de credenciales cacheadas → movimiento lateral AD.** `SYSTEM` en una workstation donde se logueó un domain admin = las credenciales del domain admin en LSASS. Esta es *la* cadena canónica de una workstation de usuario a compromiso de dominio. Ver [[tier-zero-administration-and-paw|Administración Tier 0]] para la ruptura estructural de esta cadena.
- **Contexto de service account → compromiso de SQL o tier de app.** La privesc en un servidor de aplicaciones (IIS, SQL Server, Exchange) produce contexto de service account que frecuentemente tiene acceso de linked-server o relación de confianza a otros hosts Tier 1.
- **Persistencia y sigilo.** Admin local habilita instalación de servicio, scheduled tasks, persistencia vía registry-run, y (con `SYSTEM`) manipulación de agentes de telemetría/EDR.

## Detección y defensa

Ordenado por efectividad:

1.
**LAPS para rotación de contraseña del admin local.**
   Windows LAPS (incorporado en Windows 11 / Server 2022+) rota las contraseñas del Administrador local por-host a valores únicos aleatorios almacenados en AD. Elimina el modo de falla de "un hash de admin local = toda la flota".

2.
**Credential Guard en cada endpoint.**
   Aísla LSASS en Virtual Secure Mode (VSM). Hace que la extracción de hashes en memoria falle. La primitiva de privesc que produjo `SYSTEM` sigue teniendo éxito; el *valor* de `SYSTEM` (hashes extraídos) colapsa.

3.
**Auditar y remediar las primitivas canónicas de privesc.**
   Escaneo trimestral con `accesschk.exe`, `PowerUp.ps1` en modo auditoría, o equivalentes comerciales:
   - Permisos de servicio débiles (`accesschk -uwcqv "Users" *`)
   - Rutas de servicio sin comillas (`wmic service get name,pathname /format:list | findstr /v "\""`)
   - Estado del registro AlwaysInstallElevated (debería ser `0` o ausente)
   - Directorios escribibles en `PATH`
   - Scheduled tasks con ACLs débiles

4.
**AppLocker o WDAC allowlisting de ejecutables.**
   Bloquea binarios soltados de ejecutar completamente. Derrota la mayoría de las primitivas de privesc basadas en herramientas.

5.
**Restricted admin mode y Just-Enough-Administration (JEA).**
   Para administración remota: `mstsc /restrictedadmin` no cachea credenciales en el objetivo. JEA restringe las sesiones PowerShell a cmdlets/parámetros específicos.

6.
**Detección en los Event IDs canónicos.**
   Ver [[windows-event-logs|Windows Event Logs]] para la referencia completa. Las reglas relevantes para privesc:
   - **4697** (instalación de servicio) desde un proceso padre no estándar
   - **4698 / 4702** (scheduled task creado / actualizado) desde fuentes inusuales
   - **4672** (privilegios especiales asignados) para cuentas de usuario no baseline
   - **4673** (uso de privilegio sensible — `SeImpersonatePrivilege` etc.) fuera de service accounts baseline
   - **4624 LogonType=9** (NewCredentials — la firma de la familia Potato)
   - **4688** con anomalías en el proceso padre (una shell de comandos parenteada a un binario de servicio)

### Qué no funciona como defensa primaria

- **Confiar en que "los usuarios no-admin no pueden escapar."** Windows por defecto incluye múltiples primitivas de privesc disponibles para usuarios estándar out of the box. Auditá, no asumas.
- **Depender solo de UAC.** La mayoría de los bypasses modernos de UAC no son vulnerabilidades — son comportamientos de auto-elevación documentados.
- **Solo parchear.** La mayoría de las primitivas de privesc son configuración, no CVEs.
- **Firma de antivirus.** Las herramientas de privesc nombradas son detectadas; las herramientas renombradas o recompiladas no lo son.

## Labs prácticos

Ejecutar solo contra entornos lab propios o engagements autorizados.

```powershell
# Lab 1 — Inventariar privilegios actuales y membresías de grupo.
whoami /priv
whoami /groups
net localgroup Administrators
net user $env:USERNAME
# Buscar SeImpersonatePrivilege, SeAssignPrimaryToken, SeBackupPrivilege.
```

```powershell
# Lab 2 — Encontrar permisos de servicio débiles.
.\accesschk.exe -uwcqv "Users" * 2>$null
.\accesschk.exe -uwcqv "Authenticated Users" * 2>$null
Get-WmiObject Win32_Service | ForEach-Object {
    $path = $_.PathName -replace '"', '' -replace ' .*', ''
    if (Test-Path $path) {
        $acl = Get-Acl $path
        $writable = $acl.Access | Where-Object {
            $_.IdentityReference -match 'Users|Everyone|Authenticated' -and
            $_.FileSystemRights -match 'Write|Modify|FullControl'
        }
        if ($writable) {
            "{0}  ->  escribible por: {1}" -f $_.Name, ($writable.IdentityReference -join ', ')
        }
    }
}
```

```powershell
# Lab 3 — Buscar rutas de servicio sin comillas.
Get-WmiObject Win32_Service |
    Where-Object {
        $_.PathName -notmatch '^"' -and
        $_.PathName -match ' '
    } |
    Select-Object Name, PathName, StartName, StartMode
```

```powershell
# Lab 4 — Verificar el estado de AlwaysInstallElevated.
$hklm = (Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\Installer' -EA 0).AlwaysInstallElevated
$hkcu = (Get-ItemProperty 'HKCU:\Software\Policies\Microsoft\Windows\Installer' -EA 0).AlwaysInstallElevated
"HKLM AlwaysInstallElevated: $hklm"
"HKCU AlwaysInstallElevated: $hkcu"
# Ambos = 1 significa que cualquier usuario puede instalar MSI como SYSTEM.
```

```powershell
# Lab 5 — Recuperar credenciales almacenadas.
cmdkey /list
Get-ChildItem 'C:\Windows\Panther\Unattend.xml','C:\sysprep.inf' -EA 0
reg query 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' 2>$null |
    findstr /i 'DefaultUserName DefaultPassword AutoAdminLogon'
```

```powershell
# Lab 6 — Detectar primitivas canónicas de privesc (lado defensor).
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4697} -MaxEvents 50 |
    Select-Object TimeCreated,
        @{n='User';e={$_.Properties[1].Value}},
        @{n='ServiceName';e={$_.Properties[4].Value}}
# Event 4697 = un servicio fue instalado. Desde un contexto de usuario, este es un indicador de privesc de alta fidelidad.
```

## Ejemplos prácticos

- **App pool IIS → SYSTEM vía PrintSpoofer.** El operador gana ejecución de código como `IIS APPPOOL\DefaultAppPool`. `whoami /priv` muestra `SeImpersonatePrivilege`. `PrintSpoofer.exe -i -c cmd.exe` desencadena una autenticación forzada vía el servicio Print Spooler e impersona `SYSTEM`. Tiempo total desde foothold de app web hasta `SYSTEM`: menos de un minuto.
- **Ruta de servicio sin comillas en una aplicación legacy de 2014.** El binario del servicio es `C:\Program Files\Acme\My Service\service.exe`, instalado sin comillas. Los usuarios tienen acceso de escritura a `C:\`. El operador deposita `C:\Program.exe`, reinicia el servicio, gana `SYSTEM`. La corrección es un carácter de comilla en el valor del registro `ImagePath`.
- **Credencial AutoLogon almacenada.** Workstation construida desde un script de imaging de 2018 que configuró `DefaultPassword` en la clave del registro Winlogon. Cualquiera con acceso de lectura (incluyendo el usuario local) recupera la contraseña del admin en el momento de construcción. La misma contraseña está en uso en 1.200 otras workstations en la flota. LAPS eliminaría la reutilización.
- **Domain admin hizo RDP a una workstation.** Un miembro del helpdesk se logueó a una workstation como domain admin para arreglar algo hace tres meses. `runas` cacheó la credencial. El operador compromete la workstation, dumpea LSASS con Mimikatz, recupera el hash del domain admin cacheado, realiza DCSync. La cadena completa que la administración Tier 0 está diseñada para prevenir — ver [[tier-zero-administration-and-paw|Administración Tier 0]].

## Notas relacionadas

- [[kerberoasting]] — precursor frecuente cuando el operador tiene una credencial de usuario de dominio pero no admin local.
- [[pass-the-hash-and-ntlm-credential-reuse]] — el seguimiento canónico: privesc produce acceso a LSASS, LSASS produce hashes, hashes producen movimiento lateral.
- [[bloodhound-attack-path-analysis]] — las aristas `AdminTo` y `CanRDP` de BloodHound identifican en qué hosts Windows debería hacer privesc un operador para ganar el mayor alcance hacia adelante.
- [[tier-zero-administration-and-paw]] — la defensa estructural que hace imposible la cadena privesc → credencial cacheada → AD.
- [[dcsync-and-ntdsdit-extraction]] — endgame típico dos hops downstream de privesc de Windows en una workstation que aloja una credencial Tier 0 cacheada.
- [[gmsa-and-modern-service-account-hardening]] — el espejo defensivo para la mala configuración de "service account en Administrators" que da poder a tantas rutas de privesc.
- [[windows-event-logs|Windows Event Logs]] — la referencia canónica para los Event IDs citados en la sección de Detección.

## Referencias

- **Fundamental:** MITRE ATT&CK TA0004 — Privilege Escalation (táctica) — https://attack.mitre.org/tactics/TA0004/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Local Administrator Password Solution and Windows Privilege Escalation Patterns — https://adsecurity.org/?p=4063
- **Docs Oficiales:** Microsoft Sysinternals Suite (accesschk, autoruns, procmon, sysmon) — https://learn.microsoft.com/en-us/sysinternals/
- **Hardening:** Microsoft Learn — Securing privileged access in Windows — https://learn.microsoft.com/en-us/security/privileged-access-workstations/overview
