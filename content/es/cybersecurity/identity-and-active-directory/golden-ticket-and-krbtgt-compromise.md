# Golden Ticket and KRBTGT Compromise

## Definición

Un Golden Ticket es un **Ticket Granting Ticket** (TGT) de Kerberos falsificado creado con el material de clave de largo plazo comprometido de la cuenta `krbtgt` del dominio. No es una contraseña mágica de administrador. Es el abuso de la raíz de confianza de firma de tickets Kerberos del dominio: si un atacante puede firmar un TGT con una clave que el Key Distribution Center acepta como `krbtgt`, el atacante puede acuñar material de autenticación para principales de dominio y membresías de grupos arbitrarios.

## Por qué importa

`krbtgt` es Tier 0 porque es la raíz criptográfica de la autenticación del dominio. Los Domain Controllers usan la clave `krbtgt` para cifrar y firmar TGTs. Los servicios y KDCs no empiezan preguntando "¿ocurrió este login de contraseña?"; preguntan "¿valida este ticket bajo el modelo de confianza del dominio?". Un hash o clave AES de `krbtgt` robado por lo tanto mueve el incidente de robo de credenciales a **compromiso de confianza del sistema de identidad**.

Por eso los eventos de [[dcsync-and-ntdsdit-extraction|DCSync y extracción de ntds.dit]] son endgame. DCSync de usuarios ordinarios habilita movimiento lateral; DCSync de `krbtgt` habilita falsificación de tickets contra el tejido de autenticación del dominio mismo. Los resets de contraseña de usuarios normales, incluso los resets de contraseña de Domain Admin, no revocan un Golden Ticket falsificado con material `krbtgt` todavía válido.

La distinción senior es:

- **Compromiso de contraseña:** rotar la identidad afectada e investigar sesiones.
- **Compromiso de service account:** rotar el secreto del servicio e inspeccionar el acceso del servicio.
- **Compromiso de `krbtgt`:** tratar la raíz de firma Kerberos del dominio como no confiable hasta que el sequencing de recuperación pruebe lo contrario.

## Cómo funciona

El abuso de Golden Ticket se reduce a **5 hechos del protocolo**:

1. **Kerberos separa la autenticación del acceso al servicio.** Un usuario primero recibe un TGT del KDC a través del intercambio AS, luego presenta el TGT más tarde para solicitar tickets TGS de servicio.
2. **El TGT está protegido por `krbtgt`.** El cuerpo del ticket está cifrado y firmado con la clave de largo plazo de `krbtgt`. El cliente normalmente no puede crear uno válido.
3. **DCSync puede recuperar el material de `krbtgt`.** Un principal con derechos de replicación puede solicitar el hash NTLM y las claves AES de Kerberos de `krbtgt` desde un DC. Ver [[dcsync-and-ntdsdit-extraction|DCSync y extracción de ntds.dit]].
4. **Un TGT falsificado puede contener claims de identidad elegidos por el atacante.** Las herramientas pueden elegir nombre de usuario, RID, SID de dominio, SIDs de grupos, SIDHistory, duración del ticket, tipo de cifrado y timestamps.
5. **El KDC valida la firma, no el login original.** Cuando el TGT falsificado se usa más tarde para una solicitud TGS, el KDC lo acepta si el material criptográfico y los campos son plausibles bajo la política actual.

Flujo conceptual de lab autorizado:

```
principal con derechos de replicación comprometido
  -> DCSync hash/clave AES de krbtgt
  -> obtener SID del dominio
  -> falsificar TGT para usuario elegido + claims de grupos
  -> cargar ticket en una sesión del lab
  -> solicitar TGS para CIFS/LDAP/HTTP/MSSQL
  -> observar telemetría tipo 4769/4624/4672
```

El bug estructural no es "Kerberos está roto"; es *si la cuenta de firma de tickets del dominio está comprometida, el verificador ya no puede distinguir TGTs reales emitidos por el KDC de TGTs firmados por el atacante sin correlación y recuperación*.

## Técnicas / patrones

- **DCSync a `krbtgt` es el predecesor común.** Los Golden Tickets suelen aparecer después de DCSync, extracción de ntds.dit, compromiso de DC o compromiso de backup. El ataque está downstream del acceso Tier 0, no es un primer foothold.
- **El SID del dominio es requerido.** El PAC falsificado necesita el SID del dominio más RIDs/SIDs de grupos. Los operadores usualmente lo obtienen desde LDAP, `whoami /user`, datos de BloodHound o lookup de Impacket. SID incorrecto = ticket inutilizable o anómalo.
- **La manipulación de RID y grupo importa.** Falsificar el RID 500 del `Administrator` es ruidoso. Los operadores maduros pueden elegir una identidad de usuario existente e inyectar SIDs de grupos privilegiados. Los defensores deberían comparar los claims de grupos observados contra la membresía del directorio.
- **SIDHistory puede contrabandear privilegio.** Un PAC falsificado puede incluir valores `SIDHistory` inesperados, incluyendo SIDs privilegiados históricos o de dominio extranjero.
- **Las anomalías de duración son una superficie de detección.** Las herramientas antiguas por defecto hacían tickets de 10 años. Los operadores modernos ajustan las duraciones más cerca de la política del dominio, pero los `StartTime`, `EndTime`, `RenewTill` desajustados y los patrones de logon todavía crean oportunidades de correlación.
- **AES vs RC4 cambia tanto la economía de crackeo como la de detección.** Los tickets RC4-HMAC son sospechosos en dominios AES modernos. Los tickets AES falsificados son menos obviamente anómalos pero requieren material de clave AES, no solo el hash NTLM.
- **Los Golden Tickets todavía necesitan acceso al servicio.** Un TGT falsificado usualmente tiene que obtener tickets TGS para servicios. Esa interacción con el KDC crea telemetría `4769` incluso cuando la solicitud AS original nunca ocurrió.
- **Los resets de contraseña normales no revocan la raíz de confianza.** Resetear la contraseña del usuario impersonado cambia las claves derivadas de contraseña del usuario real, no la clave `krbtgt` que valida el TGT falsificado.

## Variantes y bypasses

El uso de Golden Ticket tiene **4 variantes operacionales** que vale separar.

### 1. Golden Ticket clásico de alto privilegio

El atacante falsifica un TGT para una identidad privilegiada como `Administrator` con SIDs de grupos tipo Domain Admin. Alto impacto, alto riesgo de telemetría porque aparecen logons privilegiados desde hosts y servicios inusuales.

### 2. Impersonación de usuario existente de bajo ruido

El atacante falsifica un TGT para una cuenta existente cuyo acceso normal se asemeja a la acción objetivo. Más difícil de detectar con reglas solo de nombre de usuario; la correlación debe comparar claims de grupos, historial de hosts y secuencia de emisión de tickets.

### 3. Abuso de SIDHistory / cross-domain

El PAC falsificado incluye SIDHistory o SIDs de dominio de confianza para obtener acceso a través de límites de trust. Depende fuertemente de la configuración de trust y el SID filtering.

### 4. Ticket de persistencia de largo plazo

El atacante falsifica tickets con campos de duración y renovación extendidos para persistencia. Ahora es una señal de detección fuerte en dominios donde la política Kerberos es conocida centralmente y la telemetría está normalizada.

## Impacto

Ordenado por severidad real típica:

- **Compromiso de la raíz de autenticación Tier 0.** El material de `krbtgt` le permite al atacante impersonar cualquier principal del dominio desde la capa Kerberos.
- **Persistencia más allá de la remediación de cuenta ordinaria.** Los resets de contraseña de usuarios, admins y service accounts no invalidan tickets firmados por una clave `krbtgt` sin cambiar.
- **Fabricación de privilegio en todo el dominio.** El PAC falsificado puede reclamar membresía en grupos privilegiados incluso si el directorio no contiene esa membresía.
- **Ambigüedad forense.** Los logs de autenticación pueden mostrar un nombre de usuario real aunque la contraseña del usuario real nunca fue usada.
- **Completación de la ruta de ataque.** Las rutas de [[bloodhound-attack-path-analysis|BloodHound]] que terminan en DCSync se convierten efectivamente en rutas hacia la capacidad de Golden Ticket.

## Detección y telemetría

La detección es correlacional, no un IOC único. Señales útiles:

1.
**Solicitud TGS sin una solicitud AS precedente plausible.**
   El Event ID `4769` aparece cuando se solicita un TGS. Si no hay un `4768` correspondiente de solicitud de TGT para esa cuenta, host y ventana de tiempo, el TGT puede haber sido inyectado o falsificado. Esto requiere telemetría DC alineada en tiempo.

2.
**Anomalías de duración y renovación del ticket.**
   Comparar los campos de ticket observados con la política Kerberos del dominio. Los valores `EndTime` o `RenewTill` anormalmente largos son útiles, pero los atacantes modernos pueden ajustarlos; tratar la duración como una feature, no toda la detección.

3.
**Tipo de cifrado inesperado.**
   `0x17` RC4-HMAC en un entorno moderno solo-AES o AES-preferido es sospechoso, especialmente para cuentas privilegiadas.

4.
**Desajuste PAC / membresía de grupo.**
   Los SIDs privilegiados en eventos de logon (`4624`, `4672`) que no coinciden con la membresía actual en grupos AD son señales de alto valor. Esto requiere enriquecimiento desde el estado del directorio.

5.
**Comportamiento de cuenta privilegiada desde hosts inusuales.**
   El uso de Golden Ticket usualmente produce acceso a servicios: SMB, LDAP, WinRM, MSSQL, HTTP. Correlacionar `4624`, `4672`, `4769`, ascendencia de proceso EDR y baselines de host/servicio.

6.
**Telemetría precursora.**
   La detección de Golden Ticket debería empezar antes del ticket: GUIDs de replicación `4662` de DCSync, acceso a `ntds.dit`, acceso a LSASS, colección de BloodHound, o uso anormal de derechos de replicación.

## Controles defensivos

Ordenado por efectividad:

1.
**Prevenir derechos de replicación en non-DCs.**
   Auditar `DS-Replication-Get-Changes*` y aristas DCSync efectivas con [[bloodhound-attack-path-analysis|BloodHound]]. Si los atacantes no pueden recuperar `krbtgt`, el riesgo de Golden Ticket colapsa.

2.
**Tratar `krbtgt` como material secreto Tier 0.**
   Incluir `krbtgt` en revisiones de acceso privilegiado, playbooks de compromiso de dominio, asunciones de protección de backup y hardening de DC.

3.
**Rotar `krbtgt` dos veces después del compromiso sospechado.**
   Un reset usualmente no es suficiente porque la clave anterior permanece utilizable durante la ventana de historial de contraseñas y duración de tickets. Combinar con [[krbtgt-rotation-and-tier-zero-recovery|KRBTGT Rotation and Tier Zero Recovery]].

4.
**Aplicar AES y retirar RC4 donde sea operativamente posible.**
   Esto reduce la ambigüedad de clave débil y detección legacy. No previene Golden Tickets si las claves AES de `krbtgt` son robadas.

5.
**Normalizar telemetría Kerberos, logon, EDR y directorio.**
   Las detecciones de Golden Ticket dependen de claves de correlación: cuenta, SID, dirección de cliente, DC, SPN de servicio, ID de logon, proceso, rol de host y snapshot de membresía de grupo.

6.
**Aislamiento Tier 0 y PAWs.**
   Prevenir la cadena de robo de credenciales que lleva a DCSync: los admins Tier 0 no deberían loguearse a sistemas de menor tier donde las credenciales pueden ser cosechadas.

### Qué no funciona como defensa primaria

- **Resetear contraseñas de Domain Admin.** Esto no cambia `krbtgt` y por lo tanto no invalida TGTs falsificados firmados con material `krbtgt` robado.
- **Deshabilitar o borrar al usuario impersonado.** Arreglar usuarios, no la raíz de confianza.
- **Bloquear Mimikatz por nombre de archivo.** La creación de Golden Ticket existe en múltiples herramientas.
- **Un solo reset de `krbtgt` como cierre del incidente.** La clave antigua puede permanecer válida suficientemente tiempo para que los tickets falsificados sobrevivan.

## Labs prácticos

Ejecutar solo en un lab AD privado, rango intencionalmente vulnerable o evaluación autorizada.

```
# Lab 1 — Mapear las precondiciones del Golden Ticket.
# Objetivo: probar que el Golden Ticket está downstream de material Tier 0.
# En BloodHound Cypher:
MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name
# Cualquier ruta hasta aquí es una ruta a capacidad Golden Ticket.
```

```
# Lab 2 — Flujo conceptual de Golden Ticket en lab autorizado.
# Solo contra tu propio dominio lab con permiso explícito.

# 1. Recuperar solo el material krbtgt del lab.
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 -just-dc-user krbtgt

# 2. Obtener el SID del dominio lab.
impacket-lookupsid LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1

# 3. Falsificar un TGT del lab con configuraciones de duración realistas.
impacket-ticketer -aesKey <LAB_KRBTGT_AES256_KEY> \
  -domain-sid S-1-5-21-<LAB-SID> -domain LAB.LOCAL labuser

# 4. Usar el ticket solo contra servicios del lab y observar logs del DC + host.
export KRB5CCNAME=labuser.ccache
impacket-smbclient LAB.LOCAL/labuser@dc01.lab.local -k -no-pass
```

```
# Lab 3 — Razonamiento de detección sobre logs del DC.
$tgs = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 200
$as  = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 200
# Ejercicio del analista:
# - agrupar por AccountName + ClientAddress
# - buscar actividad TGS sin actividad AS cercana
# - comparar tipos de cifrado contra la política del dominio
```

## Ejemplos prácticos

- **Cadena DCSync-a-Golden-Ticket.** Kerberoasting produce `svc_replication`, BloodHound muestra derechos DCSync, DCSync recupera `krbtgt`, y un TGT falsificado impersona a un usuario privilegiado. El problema real fue la arista de derecho de replicación.
- **Falso cierre post-incidente.** El IR resetea todas las contraseñas de Domain Admin pero no rota `krbtgt`. El atacante continúa usando un TGT previamente falsificado. La organización arregló usuarios, no la raíz de confianza.
- **Abuso de SIDHistory en un trust legacy.** Un trust de era de migración deja el SID filtering débil. El SIDHistory falsificado otorga acceso que la membresía de grupo actual no explica.

## Notas relacionadas

- [[dcsync-and-ntdsdit-extraction]] — la forma más común de recuperar material de `krbtgt`.
- [[bloodhound-attack-path-analysis]] — las rutas del grafo hacia DCSync son rutas hacia la capacidad de Golden Ticket.
- [[kerberoasting]] — predecesor común cuando las service accounts crackeadas llevan a derechos de replicación.
- [[silver-ticket-and-service-account-persistence]] — el caso de contraste con scope de servicio para tickets Kerberos falsificados.
- [[krbtgt-rotation-and-tier-zero-recovery]] — la operación de recuperación que invalida el material `krbtgt` robado cuando se secuencia correctamente.

## Referencias

- **Fundamental:** MITRE ATT&CK T1558.001 — Steal or Forge Kerberos Tickets: Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Recuperación:** Microsoft Learn — Active Directory Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz Golden Ticket Usage, Exploitation, and Detection — https://adsecurity.org/?p=1515
