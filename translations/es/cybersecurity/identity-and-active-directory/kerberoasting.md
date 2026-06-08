# Kerberoasting

## Definición

Kerberoasting es un ataque de credenciales de Active Directory donde un usuario autenticado del dominio solicita **tickets TGS de servicio** para cuentas que tienen un Service Principal Name (SPN) y luego intenta **crackear los tickets resultantes offline** para recuperar la contraseña en texto plano de la service account. El ataque funciona porque (a) cualquier usuario autenticado del dominio puede solicitar un TGS para cualquier SPN, y (b) la porción del TGS cifrada con la clave derivada de la contraseña de la service account es observable para el solicitante.

## Por qué importa

Kerberoasting es el ataque AD post-foothold de mayor impacto que no requiere escalada de privilegios, exploit ni malware. Cualquier usuario del dominio puede ejecutarlo. Lo único que controla el defensor es **si las contraseñas de las service accounts son lo suficientemente fuertes para sobrevivir el crackeo offline** — y históricamente, las service accounts se configuran con contraseñas débiles, nunca rotadas y elegidas por humanos porque "son service accounts, nadie las tipea". El resultado es una ruta confiable desde cualquier usuario del dominio hacia una service account, y frecuentemente desde esa service account hacia domain admin mediante movimiento lateral.

La técnica también es el puente textbook entre tres ramas del atlas que de otra manera están distantes:
- **Cryptography** — el ataque solo funciona porque la clave de cifrado se deriva de una contraseña mediante un KDF conocido. Contraseñas fuertes + AES + Kerberos PBKDF2 = impracticable de crackear; contraseñas débiles + RC4 = crackeadas en horas en una sola GPU.
- **Detection Engineering** — es el ejemplo más limpio de un ataque cuya *única* señal defensiva es de comportamiento, no de firma. Cada solicitud de TGS es una operación Kerberos normal; el ataque está en el *patrón*.
- **Offensive Security** — es el primer movimiento canónico después de obtener cualquier credencial AD.

## Cómo funciona

Kerberoasting se reduce a **5 pasos del protocolo**:

1. **Autenticarse al dominio.** Cualquier credencial de usuario del dominio válida (comprada, phished, robada, por default). No se necesitan privilegios especiales.
2. **Enumerar SPNs.** Consultar AD para cuentas de usuario que tengan el atributo `servicePrincipalName`. Cualquier usuario autenticado puede hacer esta consulta LDAP — `(&(objectClass=user)(servicePrincipalName=*))` — sin rastro de auditoría más allá de los logs de consulta LDAP estándar.
3. **Solicitar tickets TGS.** Para cada SPN, pedir al KDC un TGS mediante tráfico normal `KRB_TGS_REQ`. El KDC devuelve un TGS *cifrado con la clave de largo plazo de la service account* (que se deriva de su contraseña).
4. **Extraer la porción cifrada.** El blob cifrado del ticket TGS es observable para el solicitante. Herramientas como `GetUserSPNs.py` (Impacket), `Rubeus` o PowerShell con `KerberosRequestorSecurityToken` automatizan esto y emiten un string compatible con hashcat.
5. **Crackear offline.** Ejecutar hashcat (modo `13100` para TGS RC4-HMAC, `19700`–`19900` para TGS AES) contra el hash extraído con una wordlist o reglas. RC4 + contraseña débil = minutos. AES-256 + contraseña fuerte = años.

Secuencia representativa de punta a punta:

```
# Desde un foothold Linux, con cualquier credencial de dominio válida
impacket-GetUserSPNs DOMAIN.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request -outputfile spns.hash
hashcat -m 13100 spns.hash /usr/share/wordlists/rockyou.txt --force
```

El bug no es "Kerberos está roto"; es *la clave de cifrado de un TGS es la contraseña de una service account, y el flujo de crackeo offline opera sobre datos que cualquier usuario de dominio puede solicitar legítimamente*.

## Técnicas / patrones

- **La enumeración de SPNs es el primer movimiento.** Sin SPNs no hay nada que roastear. Herramientas: `setspn -Q */*` (Windows nativo), `GetUserSPNs.py` (Impacket), `Rubeus.exe kerberoast /stats` (in-process Windows). Cada una deja telemetría ligeramente diferente.
- **Filtrar SPNs por interés.** Las service accounts con altos privilegios (en `Domain Admins`, `Enterprise Admins`, `Backup Operators`, grupos de admin de nivel servicio) son el objetivo. Las rutas de BloodHound muestran qué service accounts otorgan el mayor movimiento hacia adelante.
- **Elegir RC4 sobre AES cuando sea posible.** El KDC negocia el tipo de cifrado por ticket. Las herramientas pueden solicitar `RC4-HMAC` para forzar el algoritmo más débil. RC4 + GPU = órdenes de magnitud más rápido que AES-256.
- **Roasting dirigido vs no filtrado.** `GetUserSPNs.py -request-user <target>` pide un SPN específico — más silencioso que "solicitar todos los SPNs de una vez". El roasting dirigido contra SPNs de alto valor identificados previamente es la variante consciente de OPSEC.
- **Usar BloodHound para elegir objetivos.** Una vez conocidos los SPNs, el análisis de `OutboundControl` y `MemberOf` de BloodHound identifica qué cuentas roasteadas comprometidas producen el mayor blast radius.
- **Solo ejecutar en un engagement autorizado.** Kerberoasting en producción sin autorización explícita de scope es un delito grave en la mayoría de jurisdicciones.

## Variantes y bypasses

Kerberoasting tiene **4 variantes importantes**, cada una con precondiciones y perfiles de detección distintos.

### 1. Kerberoasting clásico

El flujo descripto arriba. Requiere cualquier usuario autenticado del dominio. La técnica por defecto de red-team y pentest. La detección es de comportamiento (volumen de solicitudes, selección de cuentas, tipo de cifrado) — no hay firma.

### 2. Kerberoasting dirigido (un SPN a la vez)

Mismo protocolo, restringido a uno o pocos SPNs de alto valor identificados previamente mediante BloodHound o análisis manual. Significativamente más silencioso que el roasting masivo. Los defensores que alertan sobre anomalías masivas de solicitudes TGS se pierden esta variante.

### 3. AS-REP Roasting (el ataque sibling)

Ataque diferente, frecuentemente confundido con Kerberoasting. No requiere usuario autenticado — solo conocimiento de nombres de usuario. Apunta a cuentas con el flag `DONT_REQ_PREAUTH` en `userAccountControl`. Ver [[as-rep-roasting|AS-REP Roasting]] para el tratamiento completo.

### 4. Kerberoasting cross-realm / cross-trust

En entornos multi-forest o de dos vías de confianza, un usuario autenticado en el dominio A a veces puede roastear SPNs en el dominio B. Específico del entorno; valioso en escenarios red-team contra subsidiarias adquiridas pero no integradas.

## Impacto

Ordenado por severidad real típica:

- **Movimiento lateral al contexto de la service account.** La contraseña roasteada otorga impersonación como la service account, incluyendo acceso a lo que la cuenta puede alcanzar (file shares, bases de datos, cadenas linked-server SQL Server, tier de servicio de aplicación).
- **Escalada de privilegios a domain admin.** Cuando una service account está (por error) en `Domain Admins` o tiene permisos equivalentes — común en entornos legacy. Foothold-a-DA directo en un solo paso.
- **Persistencia vía Silver Ticket.** Una vez recuperado el hash NTLM o clave AES de la service account, un atacante puede forjar tickets Kerberos específicos de servicio localmente sin más contacto con el KDC. Ver [[silver-ticket-and-service-account-persistence|Silver Ticket and Service Account Persistence]].
- **Ruta hacia compromiso de `krbtgt`.** Si la cuenta roasteada tiene derechos de replicación o puede alcanzarlos mediante una ruta en el grafo, Kerberoasting se convierte en el predecesor de [[dcsync-and-ntdsdit-extraction|DCSync]] y capacidad de [[golden-ticket-and-krbtgt-compromise|Golden Ticket]].
- **Impersonación lateral vía SQL Server / web app.** Muchas service accounts corren web apps o servicios SQL que confían en la identidad AD — la reutilización de credenciales permite al atacante acceder a interfaces admin internas, exfiltrar datos o pivotar.

## Detección y defensa

Ordenado por efectividad:

1.
**Usá Managed Service Accounts (gMSA) con contraseñas de solo AES, autorotadas.**
   La corrección definitiva. Las contraseñas gMSA son valores aleatorios de 240 bytes rotados por AD según un schedule. La precondición "contraseña de service account débil elegida por humanos" desaparece. Las service accounts nuevas deben ser gMSA por defecto; las legacy deben migrar.

2.
**Aplicá tipos de cifrado solo-AES mediante group policy.**
   `KerberosEncryptionTypes` configurado a solo AES128/AES256. Elimina la ventaja de crackeo de RC4 — incluso una contraseña débil se vuelve imposible de crackear en tiempos prácticos.

3.
**Auditá y remové service accounts privilegiadas.**
   Las service accounts no deben estar en `Domain Admins`. Punto. La mitigación de Kerberoasting de mayor leverage *no es técnica* — es remover el objetivo. Usá BloodHound desde el lado defensor para enumerar qué service accounts otorgan acceso de alto impacto y revocá membresías innecesarias.

4.
**Detección de comportamiento sobre Event ID 4769.**
   Windows genera el Event 4769 (Kerberos Service Ticket Operations) en cada solicitud TGS. Reglas de detección: (a) alto volumen de tickets de servicio distintos solicitados por una cuenta en una ventana corta; (b) tickets solicitados con `Ticket Encryption Type 0x17` (RC4-HMAC) cuando AES está configurado en otros lugares — señal fuerte de roasting; (c) tickets de servicio solicitados para SPNs a los que el usuario nunca accedió históricamente.

5.
**Contraseñas fuertes, largas y aleatorias en cada service account.**
   Si gMSA no está disponible, el bar es 25+ caracteres verdaderamente aleatorios con rotación cada 30–90 días.

6.
**Honey SPNs.**
   Plantar service accounts falsas con SPNs y monitorear solicitudes TGS contra ellas. Los usuarios legítimos no tienen razón de solicitar estos SPNs — cualquier solicitud es un indicador de alta confianza de Kerberoasting. Defensa asimétrica.

### Qué no funciona como defensa primaria

- **"No tenemos service accounts en Domain Admins."** Afirmación común que resulta ser falsa en la inspección. Auditá, no asumas.
- **Bloquear Kerberos en la capa de red.** Kerberos es el protocolo de autenticación; no podés bloquearlo sin romper el directorio.
- **Remover el derecho `Logon as a service`.** No previene las solicitudes TGS.
- **Deshabilitar la consulta LDAP.** Los usuarios autenticados pueden enumerar SPNs mediante varios otros canales incluyendo `setspn`.
- **Renombrar service accounts a nombres oscuros.** Seguridad por oscuridad. La enumeración de SPNs devuelve el samAccountName canónico.

## Labs prácticos

Ejecutar **solo** contra entornos lab propios o engagements autorizados.

```
# Lab 1 — Crear un AD lab con una service account kerberoastable.
# En un DC lab:
New-ADUser -Name "svc_sql" -SamAccountName "svc_sql" -AccountPassword (ConvertTo-SecureString "Summer2024!" -AsPlainText -Force) -Enabled $true
setspn -A MSSQLSvc/sqlhost.lab.local:1433 LAB\svc_sql
# Esta cuenta ahora es kerberoastable desde cualquier usuario del dominio.
```

```
# Lab 2 — Enumerar cuentas kerberoastables desde un host Linux con credenciales válidas.
impacket-GetUserSPNs LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1
# Cada línea de resultado es un SPN cuya cuenta puede ser roasteada.
```

```
# Lab 3 — Solicitar un TGS y volcar el hash crackeable.
impacket-GetUserSPNs LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request -outputfile tgs.hash
cat tgs.hash
# La salida es una línea $krb5tgs$23$* lista para hashcat.
```

```
# Lab 4 — Crackear offline.
hashcat -m 13100 tgs.hash /usr/share/wordlists/rockyou.txt --force
# Modo 13100 = TGS-REP / RC4-HMAC. Usá 19700/19800/19900 para variantes AES.
```

```
# Lab 5 — AS-REP roast contra una cuenta lab con pre-auth deshabilitada.
# En el DC lab, marcar una cuenta con "Do not require Kerberos preauthentication":
Set-ADAccountControl -Identity legacy_user -DoesNotRequirePreAuth $true
# Desde el host atacante:
impacket-GetNPUsers LAB.LOCAL/ -dc-ip 10.0.0.1 -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hash
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```

```
# Lab 6 — Validar la detección desde el lado defensor.
# Después de ejecutar lo anterior, revisar el log de seguridad del DC lab:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 50 |
  Where-Object { $_.Properties[5].Value -eq '0x17' }  # filtrar por RC4-HMAC
# Cada línea es un evento candidato de roasting. Construí reglas de detección desde esta señal.
```

## Ejemplos prácticos

- **Foothold inicial vía usuario bajo privilegio phished.** El atacante phishea `lowpriv@corp.com`, roastea el dominio, recupera la contraseña de `svc_backup` ("Backup2023!"), usa la membresía de `svc_backup` en `Backup Operators` para acceder a la base de datos SAM remotamente, recupera el hash de `krbtgt`, forja un Golden Ticket — dominio comprometido en pocas horas del phish inicial.
- **Forest de empresa adquirida con service accounts débiles.** La confianza de forest post-fusión otorga acceso de usuario autenticado del dominio padre al dominio adquirido. Kerberoasting revela que las service accounts del dominio adquirido son palabras de diccionario de 8 caracteres. El compromiso del forest adquirido sigue.
- **Honeypot defiende.** El defensor planta `svc_honeypot` con un SPN. Seis meses después, una solicitud TGS desde una workstation que nunca accede a nada más dispara la alerta. La workstation era una cabecera de playa que el SOC no sabía que existía.

## Notas relacionadas

- [[password-hashing|Password hashing]] — Kerberoasting tiene éxito porque la clave de cifrado TGS se deriva de una contraseña; la fortaleza del KDF determina el costo de crackeo.
- [[symmetric-encryption-modes|Symmetric encryption modes]] — RC4 vs AES en el contexto de Kerberos.
- [[as-rep-roasting]] — el ataque sibling sin credenciales.
- [[bloodhound-attack-path-analysis]] — muestra qué cuentas kerberoastables valen la pena atacar.
- [[golden-ticket-and-krbtgt-compromise]] — el abuso de la raíz de confianza cuando Kerberoasting lleva al DCSync de `krbtgt`.
- [[silver-ticket-and-service-account-persistence]] — la ruta de persistencia con scope de servicio después de recuperar la clave de la service account.
- [[gmsa-and-modern-service-account-hardening]] — el patrón defensivo que cambia la economía del Kerberoasting.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — el framing defensivo correcto.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] — el playbook del lado defensor para esta nota.

## Referencias

- **Fundamental:** MITRE ATT&CK T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Cracking Kerberos TGS Tickets Using Kerberoast — https://adsecurity.org/?p=2293
- **Investigación / Deep Dive:** Tim Medin — Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades (DerbyCon 2014) — https://www.youtube.com/watch?v=PUyhlN-E5MU
