# gMSA and Modern Service Account Hardening

## Definición

Un group Managed Service Account (gMSA) es una identidad de servicio gestionada por Active Directory cuya contraseña es larga, aleatoria, rotada automáticamente y recuperable solo por computadoras explícitamente autorizadas. gMSA no es una característica mágica anti-Kerberoasting. Es un patrón de diseño de service account que reduce el riesgo de contraseña estática cuando la propiedad de SPN, los permisos de recuperación, la delegación, el privilegio y el monitoreo están correctamente diseñados.

## Por qué importa

Las service accounts legacy son uno de los puentes de compromiso AD más comunes: tienen SPNs, contraseñas débiles o nunca rotadas, amplios derechos locales, privilegios de aplicación y propietarios poco claros. Eso las convierte en objetivos principales de [[kerberoasting|Kerberoasting]] y predecesores directos del abuso de [[silver-ticket-and-service-account-persistence|Silver Ticket]].

gMSA cambia la economía:

- sin contraseña conocida por humanos para reutilizar
- secretos aleatorios largos que son impracticables de crackear offline
- rotación automática a través de AD
- scoping explícito de qué hosts pueden recuperar la contraseña gestionada

Pero gMSA no arregla la mala autorización. Un gMSA que es admin local en todas partes, permitido para delegar ampliamente, o recuperable por un grupo de computadoras enorme sigue siendo peligroso. El control es más fuerte cuando se combina con mínimo privilegio, inventario de SPN, revisión de delegación y telemetría.

## Cómo funciona

El hardening de gMSA se reduce a **6 hechos de diseño**:

1. **La cuenta es un principal de seguridad AD.** Un gMSA tiene un SID, puede ser propietario de SPNs, puede recibir permisos y puede autenticarse a servicios respaldados por Kerberos.
2. **AD gestiona la contraseña.** Los Domain Controllers calculan y rotan una contraseña aleatoria larga según política; los humanos no la tipean ni la almacenan.
3. **Solo las computadoras autorizadas pueden recuperarla.** La configuración `PrincipalsAllowedToRetrieveManagedPassword` define qué computadoras o grupos pueden obtener la contraseña gestionada actual.
4. **Los SPNs siguen vinculando la identidad del servicio.** El SPN debe mapear limpiamente a la identidad del servicio. Los SPNs duplicados o stale crean fallas de autenticación y superficie de ataque.
5. **La delegación sigue siendo peligrosa.** Las decisiones de delegación restringida, delegación restringida basada en recursos (RBCD) y delegación no restringida todavía definen dónde puede actuar la cuenta.
6. **El blast radius es el privilegio, no el tipo de cuenta.** gMSA reduce el riesgo de crackeo de contraseñas; no reduce las ACLs excesivas, los derechos de admin local, los roles de base de datos o los permisos de aplicación por sí mismo.

La lección estructural es *el hardening de service accounts es ingeniería de identidad, no hardening de checkbox*. gMSA elimina un secreto estático débil del sistema; el resto del modelo de confianza todavía tiene que estar diseñado correctamente.

## Técnicas / patrones

- **Preferir gMSA para servicios que lo soportan.** Servicios Windows, scheduled tasks, app pools de IIS y algunos deployments de SQL Server pueden usar gMSA. El soporte de terceros varía.
- **Usar un gMSA por límite de servicio.** No crear un `gmsa_app$` universal para cada aplicación. Una identidad compartida colapsa los límites del blast radius.
- **Mantener `PrincipalsAllowedToRetrieveManagedPassword` estrecho.** Autorizar solo los hosts que realmente ejecutan el servicio. Evitar grupos amplios como "Domain Computers".
- **Separar la propiedad del SPN.** Cada SPN debería tener un propietario de servicio claro, conjunto de hosts, propietario de negocio y proceso de retiro.
- **Denegar el logon interactivo.** Las service accounts no deberían ser identidades de uso diario. Restringir logon interactivo, RDP y shell remoto donde sea posible.
- **Remover admin local por defecto.** Otorgar los permisos mínimos de archivo, registro, base de datos y red que el servicio necesita.
- **Revisar la delegación.** Preferir sin delegación; si se requiere, usar delegación restringida a servicios específicos. Tratar las escrituras de RBCD como aristas privilegiadas en [[bloodhound-attack-path-analysis|BloodHound]].
- **Auditar los permisos de recuperación.** Quién puede recuperar la contraseña gestionada es equivalente a quién puede ejecutar como el servicio.
- **Migrar cuentas legacy por riesgo.** Empezar con cuentas que llevan SPN que son privilegiadas, de contraseña débil sospechada, con capacidad RC4, o alcanzables en rutas de BloodHound.

## Variantes y elecciones de diseño

El diseño moderno de service accounts tiene **5 patrones comunes**.

### 1. Service account de usuario legacy

Objeto de usuario con SPN y contraseña establecida por un humano. Mayor riesgo de roasting y reutilización. Aceptable solo como estado temporal con contraseña aleatoria larga, solo-AES, propietario, rotación y privilegio restringido.

### 2. Standalone Managed Service Account

Contraseña gestionada pero vinculada a un host. Útil en patrones legacy de servidor único; menos flexible que gMSA para clusters y farms.

### 3. gMSA por servicio

Predeterminado preferido. Una identidad gestionada por límite de servicio, permisos de recuperación estrechos, SPNs estrechos, derechos locales/de aplicación estrechos.

### 4. gMSA por tier o familia de app

A veces usado por simplicidad operacional. Mayor blast radius porque el compromiso o la mala configuración afecta múltiples servicios.

### 5. gMSA con delegación

gMSA con delegación restringida o RBCD. Alto riesgo si el objetivo de delegación es amplio o si el acceso de escritura a los atributos de delegación es débil. Debe representarse como una arista de ruta de ataque.

## Impacto

Ordenado por valor para el defensor:

- **La economía del Kerberoasting mejora dramáticamente.** Las contraseñas aleatorias largas gestionadas hacen que el crackeo offline sea impracticable en condiciones normales.
- **La reutilización de contraseñas desaparece.** El secreto gMSA no es una contraseña humana reutilizada para RDP, SMB, portales de admin o cuentas de break-glass.
- **La rotación se vuelve operativamente normal.** La organización ya no depende de ventanas manuales de interrupción del servicio para la rotación rutinaria de contraseñas.
- **El inventario se vuelve aplicable.** La propiedad del SPN, los hosts de recuperación permitidos y la identidad del servicio pueden representarse en AD y monitorearse.
- **El blast radius se vuelve medible.** Un gMSA por servicio permite a los defensores razonar exactamente sobre qué sistemas y datos puede acceder una identidad de servicio.

## Detección y telemetría

La detección debería enfocarse en inventario de service accounts, uso y deriva de permisos:

1.
**Inventario de cuentas legacy con SPN.**
   Consultar cuentas de usuario con `servicePrincipalName` y clasificarlas por gMSA vs cuenta legacy, tipos de cifrado, privilegio y propietario.

2.
**Permisos de recuperación de contraseña anómalos.**
   Monitorear `PrincipalsAllowedToRetrieveManagedPassword`. Los grupos amplios o las computadoras inesperadas son hallazgos de alto riesgo.

3.
**Logon de service account fuera de hosts de servicio.**
   Una identidad de servicio gMSA o legacy autenticándose desde un host que no es de servicio es sospechosa. Correlacionar `4624`, inventario de hosts y registros de deployment de servicio.

4.
**Intentos de logon interactivo o remoto.**
   El logon RDP/WinRM/consola como service account indica mal uso o compromiso. Los servicios legítimos no deberían comportarse como usuarios.

5.
**Deriva de delegación.**
   Los cambios en la delegación restringida, los atributos RBCD o la propiedad del SPN pueden crear rutas de movimiento lateral. Alimentar estos en [[bloodhound-attack-path-analysis|BloodHound]] y correlación de detección.

6.
**Presión de Kerberoasting contra service accounts legacy.**
   Los patrones del Event `4769` contra SPNs identifican qué cuentas apuntan los atacantes y qué cuentas legacy deberían migrar primero.

## Controles defensivos

Ordenado por efectividad:

1.
**Por defecto nuevos servicios a gMSA donde sea soportado.**
   Hacer de gMSA el camino estándar, no la excepción.

2.
**Scope de recuperación estrecho.**
   `PrincipalsAllowedToRetrieveManagedPassword` debería nombrar solo las computadoras o grupos de computadoras estrechamente controlados que ejecutan el servicio.

3.
**Mínimo privilegio en cada capa.**
   Grupos de dominio, grupos locales, roles SQL, file shares, roles de aplicación y conectores cloud todos necesitan revisión separada.

4.
**Restringir derechos de logon.**
   Denegar el logon interactivo, RDP y patrones de logon de red que no son necesarios.

5.
**Usar AES y deshabilitar RC4 para service accounts donde sea posible.**
   Esto mejora la postura de seguridad Kerberos y convierte el uso de RC4 en una anomalía más significativa.

6.
**Inventariar continuamente SPNs y delegación.**
   Tratar los SPNs y la configuración de delegación como configuración de producción, no como configuración AD de una sola vez.

7.
**Retirar service accounts compartidas.**
   Las identidades compartidas hacen que los logs sean ambiguos y multiplican el blast radius.

### Qué no funciona como defensa primaria

- **"Usamos gMSA, así que Kerberoasting está resuelto."** gMSA ayuda fuertemente, pero los SPNs legacy, la delegación, los grupos de recuperación amplios y el sobre-privilegio todavía importan.
- **Contraseñas largas en cuentas legacy sin propiedad.** Útil pero frágil.
- **Un gMSA para cada servicio.** Operativamente fácil, pobre en seguridad. Recrea el patrón de service account todo-poderosa.
- **Ocultar nombres de service accounts.** Los SPNs y la configuración del servicio revelan la identidad del servicio.
- **Bloquear herramientas de roasting.** El roasting es uso normal del protocolo TGS.

## Labs prácticos

Ejecutar solo en un lab AD privado, rango intencionalmente vulnerable o entorno empresarial autorizado.

```
# Lab 1 — Inventariar service accounts con SPN.
Get-ADUser -LDAPFilter "(servicePrincipalName=*)" `
  -Properties servicePrincipalName,msDS-SupportedEncryptionTypes,memberOf,lastLogonTimestamp |
  Select-Object SamAccountName, Enabled, servicePrincipalName, msDS-SupportedEncryptionTypes
# Las cuentas de usuario legacy con SPNs son candidatas a roasting.
# La membresía en grupos privilegiados sube la prioridad de migración.
```

```
# Lab 2 — Crear un gMSA lab con scope de recuperación estrecho.
# Precondición: dominio lab con KDS root key ya creada en el lab.
New-ADServiceAccount -Name gmsa_web `
  -DNSHostName gmsa_web.lab.local `
  -ServicePrincipalNames HTTP/web01.lab.local `
  -PrincipalsAllowedToRetrieveManagedPassword WEB01$

# En WEB01 en el lab:
Install-ADServiceAccount gmsa_web
Test-ADServiceAccount gmsa_web
```

```
# Lab 3 — Auditar permisos de recuperación de contraseña gestionada.
Get-ADServiceAccount -Filter * -Properties PrincipalsAllowedToRetrieveManagedPassword |
  Select-Object Name, PrincipalsAllowedToRetrieveManagedPassword
# Ejercicio del analista:
# - marcar grupos amplios
# - marcar computadoras que no alojan el servicio
# - comparar contra inventario CMDB/deployment
```

```
# Lab 4 — Detectar logon anómalo de service account.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 200 |
  Where-Object {
    $_.Properties[5].Value -match 'gmsa_|svc_' -and
    $_.Properties[8].Value -notin @('5')
  }
# Ejercicio del defensor:
# - mapear hosts de servicio esperados
# - alertar en identidades de servicio autenticándose desde workstations
```

## Ejemplos prácticos

- **Reducción de riesgo de Kerberoasting.** `svc_sql` con `Winter2020!` se convierte en `gmsa_sql$` con secreto aleatorio largo gestionado. Las solicitudes TGS pueden seguir ocurriendo, pero el crackeo offline se vuelve antieconómico.
- **Mala configuración de rollout gMSA.** `PrincipalsAllowedToRetrieveManagedPassword` está configurado a `Domain Computers`. Cualquier host unido al dominio comprometido puede recuperar el secreto del servicio.
- **Arista de delegación persiste.** Un gMSA migrado conserva la delegación no restringida de la cuenta legacy. El riesgo de roasting mejora, pero el riesgo de movimiento lateral permanece.
- **Colapso de identidad compartida.** Un gMSA sirve web, SQL jobs y scripts de backup. Los logs son ambiguos y el blast radius es amplio.

## Notas relacionadas

- [[kerberoasting]] — el ataque que gMSA cambia más directamente económicamente.
- [[silver-ticket-and-service-account-persistence]] — el compromiso de clave de service account se convierte en falsificación de ticket de servicio.
- [[golden-ticket-and-krbtgt-compromise]] — contraste el hardening de service account con el compromiso de la raíz de confianza del dominio.
- [[bloodhound-attack-path-analysis]] — modelar el privilegio, delegación y aristas de admin local de service accounts.
- [[tier-zero-administration-and-paw]] — el marco de administración Tier 0 que complementa el hardening de service accounts.

## Referencias

- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
- **Hardening:** Microsoft Learn — Get started with group Managed Service Accounts — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/getting-started-with-group-managed-service-accounts
- **Fundamental:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Active Directory Security Tip #14: Group Managed Service Accounts (GMSAs) — https://adsecurity.org/?p=4904
