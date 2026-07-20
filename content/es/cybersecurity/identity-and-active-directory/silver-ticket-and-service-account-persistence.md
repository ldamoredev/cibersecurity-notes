# Silver Ticket and Service Account Persistence

## Definición

Un Silver Ticket es un **ticket de servicio** (TGS) de Kerberos falsificado creado con una clave de service account comprometida en lugar de la clave `krbtgt` de todo el dominio. Es falsificación de Kerberos con scope de servicio: si un atacante conoce el hash NTLM o la clave AES para la cuenta detrás de un SPN, el atacante puede forjar un ticket para ese servicio específico sin primero pedirle al KDC un TGS legítimo.

## Por qué importa

Los Silver Tickets se ubican entre [[kerberoasting|Kerberoasting]] y el compromiso de [[golden-ticket-and-krbtgt-compromise|Golden Ticket]]. No requieren `krbtgt`, así que no son un compromiso de la raíz de autenticación de todo el dominio. Pero tampoco requieren una solicitud normal de ticket de servicio al KDC en el momento de uso, así que pueden crear persistencia durable y silenciosa con scope de servicio donde los defensores solo observan los logs del Domain Controller.

La distinción central:

- **Golden Ticket:** TGT falsificado, firmado con `krbtgt`, puede solicitar tickets de servicio ampliamente.
- **Silver Ticket:** TGS falsificado, firmado/cifrado con una clave de service account, útil solo para ese servicio/clase de SPN.

Esto hace del diseño de service accounts un límite de seguridad. Una contraseña débil de service account MSSQL no es meramente "un hallazgo de contraseña"; si se crackea, puede convertirse en una ruta de persistencia vía ticket falsificado para MSSQL, CIFS, HTTP, LDAP, HOST o acceso al tier de aplicación dependiendo de la propiedad de SPN y el privilegio de cuenta.

## Cómo funciona

El abuso de Silver Ticket se reduce a **5 hechos del protocolo**:

1. **Los servicios tienen SPNs.** Un SPN mapea una instancia de servicio (`MSSQLSvc/sql01.lab.local:1433`, `HTTP/app.lab.local`, `CIFS/fileserver.lab.local`) a una cuenta AD.
2. **El KDC normalmente emite un TGS.** Un cliente presenta un TGT al KDC y solicita un TGS para un SPN objetivo. El KDC devuelve un ticket de servicio cifrado con la clave de la service account objetivo.
3. **El servicio valida el ticket localmente.** El servicio descifra y valida el ticket con su propia clave de largo plazo. Dependiendo del servicio y la configuración, el DC puede no ser contactado para validación PAC completa en cada solicitud.
4. **Una clave de servicio comprometida puede falsificar ese ticket.** Si el atacante tiene el hash NTLM o la clave AES de la service account, puede acuñar un TGS para ese servicio directamente.
5. **El ticket falsificado está limitado a ese servicio.** No otorga acceso de dominio arbitrario a menos que el servicio mismo tenga privilegios amplios o sea un punto de pivote.

Flujo conceptual de lab autorizado:

```
service account kerberoastable
  -> crackear o de otra manera recuperar la clave del servicio
  -> identificar SPN y clase de servicio
  -> falsificar TGS para CIFS/HTTP/MSSQL/LDAP/HOST
  -> inyectar ticket en sesión del lab
  -> acceder solo al servicio del lab con scope
  -> comparar logs del DC vs logs del host/servicio
```

El bug estructural no es "Kerberos está roto"; es *las service accounts frecuentemente mantienen claves derivadas de contraseña de larga duración, y los servicios pueden aceptar tickets de servicio Kerberos localmente válidos incluso cuando el KDC no los emitió durante la sesión observada*.

## Técnicas / patrones

- **Kerberoasting es el predecesor común.** [[kerberoasting|Kerberoasting]] recupera contraseñas de service accounts; el abuso de Silver Ticket usa la clave NTLM/AES resultante para falsificación de tickets de servicio.
- **La selección del SPN define el blast radius.** `CIFS` otorga acceso a file shares en el host objetivo, `HTTP` otorga contexto de aplicación web, `MSSQLSvc` otorga acceso a base de datos, `LDAP` puede apuntar operaciones del servicio de directorio, y `HOST` puede mapear a múltiples clases de servicios locales dependiendo del entorno.
- **El privilegio de la service account es el multiplicador real de impacto.** Un ticket falsificado para una app web de bajo privilegio puede solo leer datos de la app. Un ticket falsificado para una service account que es admin local en muchos servidores se convierte en infraestructura de movimiento lateral.
- **La validación PAC cambia la detección y los modos de falla.** Algunos servicios validan el Privilege Attribute Certificate con un DC bajo condiciones específicas; otros dependen principalmente de la validación local del ticket. La falta de contacto con el DC es un punto ciego de detección, no una garantía de éxito.
- **AES vs RC4 importa de nuevo.** Los tickets RC4 falsificados usan material de hash NTLM y son sospechosos en dominios modernos. Los tickets AES encajan mejor en entornos solo-AES, pero el compromiso de clave sigue derrotando el modelo.
- **La telemetría del lado del servicio se vuelve primaria.** Si no existe `4769` del KDC para el ticket de servicio falsificado, los logs del host, logs de aplicación, EDR y logs de acceso específicos del servicio llevan la señal.

## Variantes y bypasses

El abuso de Silver Ticket tiene **5 patrones de objetivo comunes**.

### 1. Acceso a file server CIFS

Los tickets `CIFS/<host>` falsificados apuntan al acceso a archivos SMB y admin shares. La detección suele estar en el host objetivo `4624`/`5140` más actividad SMB, no en una solicitud TGS del lado del DC.

### 2. Acceso a aplicación HTTP

Los tickets `HTTP/<host>` falsificados apuntan a IIS, reverse proxies o apps web internas usando Windows Integrated Authentication. Esta variante frecuentemente se mezcla con tráfico normal de navegador/app a menos que los logs de la app preserven identidad, fuente y mecanismo de autenticación.

### 3. Acceso al servicio MSSQL

Los tickets `MSSQLSvc/<host>:<port>` falsificados apuntan a SQL Server. El impacto va desde acceso de solo-lectura a DB hasta ejecución de comandos OS si la configuración del servicio SQL es débil.

### 4. Acceso LDAP / servicio de directorio

Los tickets LDAP falsificados pueden ser poderosos cuando apuntan a servicios alojados en DC y cuando los claims de identidad mapean a permisos del directorio.

### 5. Persistencia HOST / servicio de máquina

Los tickets de clase `HOST` pueden interactuar con múltiples servicios del host y son especialmente sensibles cuando se comprometen claves de cuentas de máquina.

## Impacto

Ordenado por severidad real típica:

- **Persistencia con scope de servicio.** El atacante puede recuperar acceso a un servicio mientras la clave de la service account permanezca válida.
- **Puntos ciegos en logs del KDC.** El uso de TGS falsificado puede no producir ningún `4769` correspondiente porque no se solicitó ningún TGS al KDC.
- **Movimiento lateral a través del acceso al servicio.** Los tickets CIFS, MSSQL, HTTP y HOST pueden proporcionar movimiento práctico sin compromiso de todo el dominio.
- **Impersonación en la capa de aplicación.** Las apps internas que confían en la identidad Kerberos pueden aceptar claims de identidad falsificados y exponer datos de negocio o funciones de admin.
- **Amplificación de privilegio a través del mal diseño del servicio.** Una service account que es admin local en todas partes convierte un ticket con scope en una capacidad operacional amplia.

## Detección y telemetría

La detección necesita comparar el **flujo TGS normal** contra el **acceso del lado del servicio**.

1.
**Acceso al servicio sin `4769` correspondiente.**
   Un host objetivo registra logon Kerberos `4624` o acceso al servicio, pero la telemetría del DC carece de una solicitud TGS cercana para esa cuenta/SPN/fuente. Esta es la brecha de correlación clásica del Silver Ticket.

2.
**Claims de grupo imposibles o stale.**
   Las membresías de grupos PAC vistas en el lado del servicio no coinciden con la membresía actual del directorio.

3.
**Clase de servicio inesperada.**
   Un usuario o host accede a servicios `CIFS`, `MSSQLSvc`, `HTTP`, `LDAP` o `HOST` que nunca ha usado históricamente. Esto es de comportamiento, no basado en firma.

4.
**Tickets de servicio RC4 en dominios AES-preferidos.**
   RC4-HMAC sigue siendo una feature útil de sospecha, especialmente para service accounts que deberían soportar AES.

5.
**Precursor de Kerberoasting.**
   Una ráfaga o conjunto dirigido de solicitudes `4769` contra un SPN seguida más tarde de acceso al servicio sin solicitudes TGS del KDC es una secuencia fuerte.

6.
**Logs de endpoint y aplicación.**
   La ascendencia de proceso EDR, eventos de shares SMB, logs IIS, auditoría SQL y eventos de logon de Windows frecuentemente llevan más evidencia útil de Silver Ticket que los logs del DC solos.

## Controles defensivos

Ordenado por efectividad:

1.
**Usar gMSA o diseño moderno equivalente de service account.**
   [[gmsa-and-modern-service-account-hardening|gMSA]] reduce la exposición de contraseña estática usando secretos largos, aleatorios y rotados automáticamente.

2.
**Remover privilegio de las service accounts.**
   Las service accounts no deberían ser Domain Admins, admins locales amplios, backup operators o administradores de aplicaciones todo-propósito.

3.
**Aplicar AES y deshabilitar RC4 donde sea posible.**
   Reduce el abuso de claves débiles y convierte los tickets RC4 en una señal de mayor confianza.

4.
**Rotar claves de service accounts comprometidas inmediatamente.**
   Un Silver Ticket permanece viable mientras la clave del servicio permanezca válida. La rotación de contraseña/clave es la acción de revocación directa.

5.
**Inventariar SPNs y propiedad.**
   Rastrear cada SPN, su cuenta propietaria, política de contraseñas, propietario del servicio, hosts que lo usan y asignaciones de privilegio. Los SPNs sin dueño se convierten en deuda de persistencia.

6.
**Correlacionar logs del DC, endpoint y servicio.**
   La detección de Silver Ticket falla cuando el SIEM solo ingesta eventos de Domain Controller.

### Qué no funciona como defensa primaria

- **Solo monitorear eventos `4769` del Domain Controller.** Los tickets de servicio falsificados pueden no solicitar un TGS al KDC durante el uso.
- **Asumir que "no es Domain Admin" significa baja severidad.** Una service account con admin local en 200 servidores es un compromiso importante sin membresía DA.
- **Renombrar SPNs o service accounts.** La enumeración de SPNs y la configuración del servicio exponen el mapping.
- **Confiar en la validación PAC como protección universal.** El comportamiento de validación PAC depende del servicio y la configuración.

## Labs prácticos

Ejecutar solo en un lab AD privado, rango intencionalmente vulnerable o evaluación autorizada.

```
# Lab 1 — Modelar el scope del ticket de servicio.
# Objetivo: probar que el impacto del Silver Ticket está acotado por SPN y privilegio de service account.
# En BloodHound, buscar la service account y ver sus aristas AdminTo/CanRDP.
# Comparar el scope de acceso con y sin la service account comprometida.
```

```
# Lab 2 — Flujo conceptual de Silver Ticket en lab autorizado.
# Solo contra tu propio dominio lab con autorización explícita.
impacket-ticketer -nthash <LAB_SERVICE_NTLM_HASH> \
  -domain-sid S-1-5-21-<LAB-SID> \
  -domain LAB.LOCAL \
  -spn CIFS/fileserver.lab.local \
  labuser

export KRB5CCNAME=labuser.ccache
impacket-smbclient LAB.LOCAL/labuser@fileserver.lab.local -k -no-pass
# Vista del defensor esperada: logon Kerberos del host objetivo + acceso SMB, pero posiblemente sin `4769` coincidente del KDC.
```

```powershell
# Lab 3 — Contraste de detección: flujo TGS normal vs comportamiento de ticket de servicio falsificado.
# En el DC del lab:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 100 |
  Select-Object TimeCreated, ProviderName, Id

# En el servidor lab objetivo:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 100 |
  Where-Object { $_.Properties[8].Value -match 'Kerberos' }

# Ejercicio del analista:
# - hacer coincidir cuenta + cliente + servicio entre DC y host objetivo
# - marcar logons del objetivo que carecen de un evento TGS del DC cercano
```

## Ejemplos prácticos

- **Persistencia Kerberoast-a-MSSQL.** Una contraseña débil de `svc_sql` se crackea. El atacante falsifica tickets `MSSQLSvc/sql01` durante meses hasta que la service account rota.
- **Acceso CIFS sin TGS del DC.** Un file server registra logons Kerberos SMB desde una identidad, pero los logs del DC no muestran ninguna solicitud TGS cercana. El evento del DC faltante es la pista.
- **Impersonación de aplicación HTTP.** Un portal de admin interno confía en Windows Integrated Authentication. El ticket `HTTP/app` falsificado otorga acceso a funciones de admin de la app aunque el dominio no esté completamente comprometido.
- **Service account con sobre-privilegio.** `svc_web` es admin local en todo un tier web. Un Silver Ticket con scope a HTTP/HOST en esos servidores se convierte en infraestructura de movimiento lateral.

## Notas relacionadas

- [[kerberoasting]] — la forma más común de recuperar material de clave de service account.
- [[golden-ticket-and-krbtgt-compromise]] — comparar la falsificación TGS con scope de servicio con la falsificación TGT de todo el dominio.
- [[dcsync-and-ntdsdit-extraction]] — DCSync puede recuperar claves de servicio además de `krbtgt`.
- [[gmsa-and-modern-service-account-hardening]] — el patrón defensivo de service accounts que reduce las precondiciones del Silver Ticket.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — la detección de Silver Ticket depende de vincular el roasting precursor con el acceso posterior al servicio.

## Referencias

- **Fundamental:** MITRE ATT&CK T1558.002 — Steal or Forge Kerberos Tickets: Silver Ticket — https://attack.mitre.org/techniques/T1558/002/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — How Attackers Use Kerberos Silver Tickets to Exploit Systems — https://adsecurity.org/?p=2011
- **Fundamental:** Microsoft Learn — Kerberos authentication overview — https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
