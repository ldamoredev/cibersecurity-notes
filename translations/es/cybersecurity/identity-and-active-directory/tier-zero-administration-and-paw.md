# Tier 0 Administration and Privileged Access Workstations

## Definición

**Tier 0** es el conjunto de identidades, hosts y componentes que tienen *control efectivo sobre el directorio mismo* — Domain Controllers, los principales con derechos de `DCSync` o equivalentes de replicación, la infraestructura de recuperación AD (backups, key servers), y las autoridades certificadoras que emiten material de confianza. **La administración Tier 0** es la disciplina de tratar esas identidades y hosts como un plano de seguridad estrictamente aislado: nunca se loguean a sistemas de menor tier, nunca ejecutan software de nivel usuario, y nunca comparten material de credencial con nada fuera del límite Tier 0. Una **Privileged Access Workstation (PAW)** es el hardware dedicado (o VM) que los admins Tier 0 usan exclusivamente para realizar trabajo Tier 0 — bloqueado, aislado de internet, sin cliente de email, sin navegador hacia destinos arbitrarios, y sin aplicaciones de uso diario.

El modelo de Microsoft tiene capas debajo de Tier 0:
- **Tier 1** = admins de servidores (servidores de aplicaciones, admins de bases de datos, admins de hypervisor).
- **Tier 2** = admins de workstations, helpdesk, IT orientado al usuario.

La regla definitoria es de una vía: un tier más alto puede administrar un tier más bajo; **un tier más bajo no puede escalar a un tier más alto**. Las credenciales, sesiones y la confianza fluyen solo hacia abajo.

## Por qué importa

Cada ataque AD en esta rama — [[kerberoasting|Kerberoasting]], [[as-rep-roasting|AS-REP Roasting]], búsqueda de rutas en [[bloodhound-attack-path-analysis|BloodHound]], [[dcsync-and-ntdsdit-extraction|DCSync]], [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] — tiene la misma forma fundamental: un atacante compromete una credencial de bajo tier y atraviesa una cadena de relaciones de confianza que termina en Tier 0. **La separación de tiers es lo que elimina la cadena.** Si las credenciales de un admin Tier 0 nunca aparecen en un host Tier 1 o Tier 2, cada ataque de robo de credenciales en esos hosts de menor tier produce credenciales que no pueden alcanzar Tier 0. El blast radius de un compromiso de workstation está acotado a la workstation.

El framing senior es que la administración de tiers es la defensa **estructural** — la que no depende de que la detección funcione, de que los behavioral analytics estén correctamente ajustados, o de que el operador cometa errores. Cambia las reglas del juego en lugar de la velocidad de un lado. La salida de BloodHound sin aislamiento Tier 0 es "mostrarse mis rutas de ataque"; la salida de BloodHound con aislamiento Tier 0 adecuado es "mostrarme que no existen rutas de ataque entre Tier 1/2 y Tier 0".

La técnica también importa como nota de aprendizaje porque forza tres hechos organizacionales difíciles a la vista:

- **La mayoría de las organizaciones tienen muchos más principales Tier 0 de lo que su org chart implica.** "Domain Admins" es el subconjunto visible. El Tier 0 efectivo incluye a cualquiera con `DCSync`, cualquiera en `Backup Operators` (puede leer `ntds.dit`), cualquiera con `Manage CA` en AD-CS, cualquiera con derechos de admin en un DC, cualquiera que pueda firmar código que los DCs confíen, y cualquiera que pueda modificar GPOs que los DCs aplican. El recuento real es rutinariamente 5-10× el recuento del org chart.
- **El trabajo de admin Tier 0 es operativamente inconveniente por diseño.** Sin email, sin navegador, sin Slack en la PAW. Los admins se oponen. El framing senior es que *la inconveniencia es el control* — cualquier cosa que haga que la administración Tier 0 se sienta como trabajo IT normal ha debilitado el límite.
- **Microsoft ha pasado de "ESAE / Red Forest" al más simple Enterprise Access Model.** Los operadores que leen documentación de 2017-2020 verán "Enhanced Security Admin Environment" (ESAE / Red Forest). Microsoft deprecó ESAE en 2020 y ahora recomienda el Enterprise Access Model con PAWs, acceso Just-In-Time y Privileged Identity Management.

## Cómo funciona

La disciplina Tier 0 se operacionaliza a través de **4 reglas**:

1.
**Definir y enumerar Tier 0 explícitamente.** Usar [[bloodhound-attack-path-analysis|BloodHound]] defensivamente: `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name` más `MATCH (n)-[:AdminTo|GenericAll|WriteDACL]->(:Computer {tier0: true}) RETURN n.name`. Etiquetar cada resultado como Tier 0 en el directorio.

2.
**Las identidades Tier 0 usan credenciales Tier 0 solo en sistemas Tier 0.** Los admins Tier 0 tienen una cuenta de admin dedicada (`svc-ad-admin-alice`) que es *separada* de su cuenta de uso diario (`alice@corp.com`). La cuenta de admin se usa solo cuando se está logueado en la PAW; nunca se usa en workstations, servidores, jump boxes o en ningún otro lugar. Aplicar esto requiere restricciones GPO ("Deny logon locally" / "Deny logon as a service" en hosts de menor tier) y alertas de auditoría para violaciones.

3.
**Las PAWs son físicamente (o lógicamente) separadas de la máquina de uso diario del usuario.** La PAW tiene: hardware dedicado o una VM aislada por hypervisor; egress de internet restringido (allowlist a Microsoft Update + Azure AD + nada más); sin Office, sin email, sin Slack, sin navegador de propósito general; Credential Guard + Device Guard habilitados; AppLocker o WDAC aplicando allowlists de ejecutables; BitLocker en cada unidad.

4.
**La administración Tier 0 usa acceso Just-In-Time donde sea posible.** La cuenta de admin del usuario *no* es un miembro permanente de `Domain Admins`; en cambio, solicita elevación a través de Privileged Identity Management (PIM, en Entra ID / Microsoft Identity Manager). La membresía se otorga por una ventana acotada (típicamente ≤ 4 horas) y requiere MFA en el momento de elevación.

```cypher
// Consulta BloodHound para enumeración defensiva del Tier 0 efectivo.
MATCH (n)-[:DCSync|GetChanges|GetChangesAll|AdminTo|CanRDP|GpLink|WriteDACL]->(t)
WHERE t.tier = 0 OR t.name CONTAINS 'DC' OR t.name CONTAINS 'DOMAIN CONTROLLERS'
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
ORDER BY type, n.name
```

El bug no es "AD tiene demasiados privilegios"; es *las relaciones de confianza fluyen transitivamente a través de hosts cuando las credenciales están cacheadas, y cualquier credencial Tier 0 cacheada en un host no-Tier-0 extiende el límite Tier 0 a donde sea que ese host viva*.

## Técnicas / patrones

- **Ejecutar BloodHound mensualmente *en tu propio AD* para monitorear la deriva del Tier 0.** Una resultado limpio de BloodHound un trimestre no significa limpio el siguiente — nuevas delegaciones, nuevas instalaciones de Exchange, nuevas creaciones de service accounts, todas añaden aristas.
- **Usar el grupo `Protected Users` para cada cuenta de admin Tier 0.** Fuerza Kerberos con AES, deshabilita NTLM/LM/DES/RC4 para ese usuario, previene el cacheo de credenciales de largo plazo en hosts miembro. El multiplicador defensivo más importante para cuentas Tier 0. Ver [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] §Detección y defensa ítem 4.
- **Authentication Policies and Silos.** Más allá de Protected Users, las Authentication Policies permiten restringir *en qué hosts* puede usarse una credencial (por ejemplo, "las cuentas `svc-ad-admin-*` solo pueden autenticarse a computadoras `paw-*` y `dc-*`"). La aplicación estructural de las reglas por-cuenta.
- **Restringir membresías de grupos Tier 0 con auditoría de `AdminSDHolder` + alertas.** Los grupos Tier 0 tienen sus ACLs templadas por `AdminSDHolder`. Los cambios se propagan cada 60 minutos. Alertar sobre cualquier modificación a `AdminSDHolder` o a la membresía de cualquier grupo Tier 0.
- **Deshabilitar RDP para admins Tier 0 a cualquier lugar que no sea PAWs y DCs.** GPO: denegar logon vía Remote Desktop para el grupo de admins Tier 0 en cada host Tier 1/2.
- **No olvidar la autoridad certificadora.** AD-CS es Tier 0. Auditar permisos AD-CS con aristas AD-CS de [[bloodhound-attack-path-analysis|BloodHound]] y nivelar los admins CA en consecuencia.

## Variantes y bypasses

La arquitectura Tier 0 tiene **3 variantes de implementación** en entornos reales.

### 1. Microsoft Enterprise Access Model (guía actual, post-2020)

La recomendación actual de Microsoft. Tres tiers, PAWs para Tier 0, Privileged Identity Management para elevación Just-In-Time, Authentication Policies y Silos aplicando el límite. El punto de partida predeterminado para nuevos deployments.

### 2. ESAE / Red Forest (deprecado, pero todavía deployado)

El patrón 2014-2020: un *forest administrativo* dedicado confiado por el forest de producción. Aislamiento fuerte pero operativamente pesado. Microsoft lo deprecó en 2020; los entornos que ya lo deployaron no son aconsejados a migrar solo para migrar.

### 3. Tier 0 cloud-native (Entra ID / Azure AD)

Para organizaciones cuyo plano de identidad es Entra ID en lugar de AD on-prem. Tier 0 es `Global Administrator`, `Privileged Role Administrator` y los administradores de políticas de Conditional Access.

## Impacto

Ordenado por frecuencia en compromisos AD reales:

- **La mayoría de los compromisos AD exitosos terminan en Tier 0 vía una cadena que la separación de Tier habría eliminado.** Este es el impacto primario — no tener la disciplina es *el* habilitador del compromiso total del dominio.
- **Admins Tier 0 logueándose a workstations.** La cadena más común: admin se loguea a una workstation para arreglar algo → credencial cacheada en LSASS → workstation comprometida más tarde → operador extrae la credencial de admin cacheada → la usa para DCSync.
- **Service accounts en grupos Tier 0.** Service accounts en `Domain Admins` porque alguien-una-vez-necesitó-DCSync-para-un-script-de-migración-en-2014. Kerberoastear la service account → ser Tier 0.
- **Principales Tier 0 olvidados de instalaciones legacy.** La instalación de Exchange en 2015 añadió `Exchange Trusted Subsystem` con DCSync efectivo. Exchange fue desmantelado en 2020. El grupo todavía existe.

## Detección de violaciones del límite Tier 0

Ordenado por valor de detección:

1.
**Cuenta de admin Tier 0 autenticándose en un host no-Tier-0.**
   Event 4624 en una workstation o servidor Tier 1 con la cuenta de usuario en el conjunto de admins Tier 0. Esto nunca debería ocurrir bajo el modelo. Generar una alerta de alta severidad inmediata.

2.
**Cambios de membresía de grupo Tier 0.**
   Events 4728/4732/4756 (miembro añadido a un grupo con seguridad habilitada) donde el grupo está en el conjunto Tier 0. Alertar sobre cada cambio; los cambios legítimos de grupo Tier 0 ocurren raramente (≤ una vez por mes).

3.
**Modificación de AdminSDHolder.**
   Event 4670 (permisos en un objeto fueron cambiados) donde el objeto es `AdminSDHolder`. Frecuentemente el primer paso de una backdoor Tier 0.

4.
**Autenticación NTLM desde una cuenta de admin Tier 0.**
   Los admins Tier 0 deberían estar en `Protected Users` y por lo tanto ser incapaces de autenticarse vía NTLM. Cualquier Event 4624 con LogonType=3, AuthenticationPackage=NTLM y usuario en el conjunto Tier 0 es una mala configuración o un ataque activo.

5.
**Sesiones activas concurrentes para una cuenta de admin Tier 0.**
   Un admin real usa una sesión a la vez. Dos sesiones simultáneas en diferentes hosts es casi siempre un robo de credencial.

### Qué no funciona como defensa primaria

- **"Solo decirle a los admins que no se logueen a workstations."** Sin aplicación de GPO, la regla se honra cuando es conveniente y se rompe cuando no lo es.
- **MFA en la cuenta de admin Tier 0 sin limitar *dónde* puede usarse.** MFA previene fuerza bruta/phishing de la contraseña; no previene la extracción de credenciales desde LSASS en una workstation donde el admin ya autenticó.
- **Confiar en que "eliminamos Domain Admin de esas cuentas".** Ejecutar BloodHound. Domain Admin es uno de muchos caminos para ser Tier 0.
- **Una sola auditoría en el momento del deployment.** La deriva del Tier 0 es continua.

## Labs prácticos

```cypher
# Lab 1 — Enumerar el Tier 0 efectivo en un AD lab.
MATCH (n)-[:DCSync|GetChanges|GetChangesAll|AdminTo|CanRDP|WriteDACL]->(t)
WHERE t.name CONTAINS 'DC' OR t.name CONTAINS 'DOMAIN CONTROLLERS'
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
ORDER BY type, n.name
# Cada resultado que NO sea una cuenta de computadora Domain Controller es un hallazgo Tier 0.
```

```powershell
# Lab 2 — Auditar membresías de grupos Tier 0 en un AD lab.
$tier0Groups = @('Domain Admins', 'Enterprise Admins', 'Schema Admins',
                  'Administrators', 'Backup Operators', 'Account Operators',
                  'Server Operators', 'Print Operators', 'Domain Controllers',
                  'Group Policy Creator Owners', 'Cryptographic Operators')
foreach ($g in $tier0Groups) {
    Get-ADGroupMember -Identity $g 2>$null |
        Select-Object @{n='Group';e={$g}}, SamAccountName, ObjectClass
}
# Cualquier cosa que no sea un pequeño número de cuentas de admin dedicadas + cuentas de computadora DC es un hallazgo.
```

```powershell
# Lab 3 — Añadir un usuario de prueba a Protected Users y verificar que NTLM está bloqueado.
Add-ADGroupMember -Identity 'Protected Users' -Members 'testadmin'
# Luego desde un host miembro intentar auth NTLM:
$cred = Get-Credential testadmin
Invoke-Command -ComputerName lab-srv-01 -Credential $cred -Authentication Negotiate -ScriptBlock { whoami }
# Esperado con NTLM negociado: falla. Con Kerberos: éxito.
```

```powershell
# Lab 4 — GPO: denegar logon de admin Tier 0 a hosts Tier 1/2.
# Crear un GPO vinculado a OUs para Tier 1 y Tier 2:
#   Computer Configuration -> Policies -> Windows Settings -> Security Settings ->
#     Local Policies -> User Rights Assignment ->
#       Deny log on locally:         añadir grupo 'Tier 0 Admins'
#       Deny log on through Remote Desktop Services: añadir grupo 'Tier 0 Admins'
#       Deny log on as a batch job:  añadir grupo 'Tier 0 Admins'
#       Deny log on as a service:    añadir grupo 'Tier 0 Admins'
```

```powershell
# Lab 5 — Detectar logon de admin Tier 0 en un host no-Tier-0 (regla del lado defensor).
$tier0Users = @('alice-adm', 'bob-adm', 'carol-adm')
Get-WinEvent -ComputerName lab-srv-01 -FilterHashtable @{
    LogName='Security'; ID=4624; StartTime=(Get-Date).AddHours(-24)
} |
    Where-Object { $tier0Users -contains $_.Properties[5].Value } |
    Select-Object TimeCreated, @{n='User';e={$_.Properties[5].Value}}, @{n='Host';e={$_.Properties[1].Value}}
# Cada resultado es una alerta de violación del límite Tier 0.
```

## Ejemplos prácticos

- **Auditoría trimestral BloodHound elimina 312 rutas de ataque.** La revisión del defensor muestra que el grupo `IT Helpdesk` tiene `ForceChangePassword` sobre 47 service accounts, varias de las cuales están en `Domain Admins`. La eliminación de una ACE corta 312 rutas distintas hacia DA. Reduce el recuento total de rutas Tier 0 en ~80% en un cambio.
- **Deployment de PAW después de hallazgo de IR.** Una investigación IR revela que el breach empezó cuando un admin Tier 0 hizo RDP a una workstation de desarrollador para "arreglar rápido" algo; la workstation ya estaba comprometida, el operador cosechó la credencial cacheada, y DA fue alcanzado en 90 segundos. Tres meses después: PAWs deployadas, GPOs de deny-logon aplicados.
- **Auditoría de service accounts atrapa el principal DCSync legacy.** La auditoría de derechos efectivos Tier 0 encuentra que `svc_exchange_2014` todavía tiene DCSync efectivo vía permisos de instalación Exchange heredados de un deployment de Exchange 2015 desmantelado en 2020.
- **Acceso Just-In-Time PIM reduce el footprint Tier 0 en un 95%.** Antes de PIM: 12 cuentas de admin Tier 0 permanentes. Después de PIM: 0 admins Tier 0 permanentes; los mismos 12 humanos pueden solicitar elevación, MFA en el momento de elevación, ventana de membresía ≤ 4 horas.

## Notas relacionadas

- [[bloodhound-attack-path-analysis]] — la herramienta canónica para enumerar el Tier 0 efectivo e identificar cadenas de violación de límites.
- [[kerberoasting]] — las service accounts en Tier 0 son los objetivos de Kerberoasting de mayor impacto.
- [[dcsync-and-ntdsdit-extraction]] — los derechos DCSync son *el* límite Tier 0; auditarlos es la auditoría Tier 0.
- [[pass-the-hash-and-ntlm-credential-reuse]] — las cadenas PtH terminan en Tier 0; esta nota es la ruptura estructural para esas cadenas.
- [[gmsa-and-modern-service-account-hardening]] — las cuentas gMSA eliminan el patrón "service account en Tier 0 con contraseña débil".
- [[krbtgt-rotation-and-tier-zero-recovery]] — cuando el aislamiento Tier 0 falla y se requiere recuperación.

## Referencias

- **Hardening:** Microsoft Learn — Enterprise Access Model — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
- **Hardening:** Microsoft Learn — Privileged Access Workstations (PAW) — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-deployment
- **Hardening:** Microsoft Learn — Protected Users security group — https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers to Improve Active Directory Security — https://adsecurity.org/?p=3299
