# AS-REP Roasting

## Definición

AS-REP Roasting es un ataque de credenciales de Active Directory donde un atacante explota cuentas con **pre-autenticación Kerberos deshabilitada** enviando un `AS-REQ` *sin* un blob de pre-auth y recibiendo un `AS-REP` cuya porción cifrada puede crackearse offline para recuperar la contraseña del usuario objetivo. A diferencia de [[kerberoasting|Kerberoasting]], **AS-REP Roasting no requiere ninguna credencial autenticada del dominio** — solo conocimiento de nombres de usuario.

## Por qué importa

Kerberoasting necesita un usuario válido del dominio para empezar. AS-REP Roasting no. Esa única diferencia hace que AS-REP Roasting sea el ataque AD canónico *pre-foothold*: si un atacante puede enumerar nombres de usuario (de LinkedIn, dumps de credenciales filtradas, LDAP anónimo, formato de email OWA, commits públicos en Git) y cualquiera de esas cuentas tiene pre-auth deshabilitada, el ataque procede sin nunca iniciar sesión.

La técnica importa como nota de aprendizaje porque expone tres cosas que los recién llegados suelen perderse:

- **La pre-autenticación Kerberos es un control de seguridad, no una formalidad del protocolo.** Deshabilitarla suena a "pequeña elección de configuración" y es en realidad "dame tu hash de contraseña, sin preguntas".
- **Los flags de `userAccountControl` son una superficie de ataque.** El flag `DONT_REQ_PREAUTH` es consultable desde cualquier consulta LDAP autenticada y, cuando está presente, define la lista de objetivos.
- **Las cuentas con pre-auth deshabilitada casi siempre existen en entornos antiguos.** Originalmente añadido para integración MIT/Heimdal Kerberos, sistemas UNIX legacy y apps pre-Win2003. El flag persiste a través de décadas porque nadie audita `userAccountControl` regularmente.

## Cómo funciona

AS-REP Roasting se reduce a **5 pasos del protocolo**:

1. **Enumerar nombres de usuario.** Desde LinkedIn / formato de email OWA / breaches filtradas / commits públicos en Git / kerbrute brute-force. No se necesita contexto autenticado — la enumeración de nombres de usuario contra Kerberos mediante diferenciales de timing en respuestas `KRB-ERROR` funciona pre-auth.
2. **Enviar `AS-REQ` sin pre-autenticación.** Los clientes Kerberos normales incluyen `PA-ENC-TIMESTAMP` (un timestamp cifrado que prueba que conocés la contraseña) dentro del `AS-REQ`. El atacante lo omite.
3. **Recibir la respuesta del KDC.**
   - Si la cuenta objetivo requiere pre-auth (el default): el KDC devuelve `KRB5KDC_ERR_PREAUTH_REQUIRED`. No vulnerable. Siguiente.
   - Si la cuenta objetivo tiene `DONT_REQ_PREAUTH` configurado: el KDC devuelve un `AS-REP` cuya `EncPart` está cifrada con la *clave de largo plazo derivada de la contraseña del usuario objetivo*.
4. **Extraer el blob cifrado.** Herramientas como `GetNPUsers.py` (Impacket) y `Rubeus.exe asreproast` automatizan esto y emiten un string compatible con hashcat en la forma `$krb5asrep$23$user@DOMAIN:hex:hex`.
5. **Crackear offline.** Hashcat modo `18200` para AS-REP RC4-HMAC, o `33100` para variantes AES. La misma economía de crackeo offline que Kerberoasting: contraseña débil + RC4 = minutos, contraseña fuerte + AES-256 = años.

Secuencia representativa de punta a punta:

```
# Desde cualquier host, sin credencial de dominio requerida.
impacket-GetNPUsers DOMAIN.LOCAL/ -dc-ip 10.0.0.1 \
    -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hash
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```

El bug no es "Kerberos está roto"; es *un flag de cuenta desactivó la puerta de prueba-criptográfica-de-contraseña, así que el KDC felizmente emite un hash crackeable de la contraseña del usuario a cualquier caller que lo pida*.

## Técnicas / patrones

- **La enumeración de nombres de usuario es el prerrequisito.** Sin lista de nombres de usuario no hay nada que roastear. Construir la lista desde: `kerbrute userenum`, `MSF auxiliary/gather/kerberos_enumusers`, OSINT (LinkedIn → nombre.apellido@corp.com), corpora de breaches públicas, enumeración SMB/RPC anónima si está abierta.
- **Si tenés *cualquier* credencial de dominio, volcá la lista objetivo vía LDAP.** Con incluso un usuario válido, consultá AD por `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` — el filtro de bitmask para el flag `DONT_REQ_PREAUTH`. Devuelve cada cuenta vulnerable en una consulta.
- **Elegir RC4 sobre AES cuando el KDC lo ofrece.** `GetNPUsers.py` por defecto con `-format hashcat` produce un hash RC4-HMAC cuando la cuenta lo soporta. RC4 + contraseña débil = órdenes de magnitud más rápido de crackear offline.
- **OPSEC: preguntá una vez, no muchas.** La consulta masiva de cada cuenta en el dominio deja un rastro de telemetría claro (muchos AS-REQ desde una fuente, todos sin pre-auth). El uso avanzado solo consulta las cuentas vulnerables pre-identificadas.

## Variantes y bypasses

AS-REP Roasting tiene **3 variantes** que vale distinguir.

### 1. AS-REP Roasting clásico (sin credenciales)

El flujo descripto arriba. El atacante tiene zero autenticación de dominio. Requiere nombres de usuario + al menos una cuenta con `DONT_REQ_PREAUTH`. La variante que hace que este ataque sea únicamente peligroso comparado con Kerberoasting.

### 2. AS-REP Roasting con credenciales

El atacante ya tiene cualquier credencial de dominio válida. Usa LDAP autenticado para enumerar el conjunto exacto de cuentas con pre-auth deshabilitada (sin adivinanzas, sin kerbrute), luego ejecuta el protocolo contra solo esas. Más silencioso y confiable.

### 3. AS-REP Roasting dirigido (usuario único)

Objetivo único pre-identificado de alto valor (por ejemplo, una cuenta admin legacy conocida desde un org chart filtrado). Un único `AS-REQ` produce un único `AS-REP`. Telemetría mínima; señal de detección más baja.

## Impacto

Ordenado por severidad real típica:

- **Foothold desde zero autenticación.** La propiedad definitoria. Una sola cuenta con pre-auth deshabilitada convierte una posición de "sabemos el nombre de la empresa y algunos emails" en "tenemos un hash de contraseña crackeable".
- **Escalada de privilegios si la cuenta con pre-auth deshabilitada es privilegiada.** La pre-auth se deshabilitaba históricamente en service accounts de integración UNIX y en algunas cuentas admin. El crackeo da acceso privilegiado directo.
- **Persistencia y pivote.** La contraseña recuperada funciona para SMB, WinRM, RDP, MSSQL — cualquier servicio que confíe en la identidad AD. El movimiento lateral sigue inmediatamente.
- **Contexto de dominio para ataques posteriores.** Incluso un crackeo sin privilegios establece una credencial de dominio real, desbloqueando todo el toolkit de Kerberoasting / BloodHound / enumeración SMB.
- **Las cuentas olvidadas persisten por años.** El hallazgo más común en la realidad: una cuenta de la era de 2009 con pre-auth deshabilitada por una integración UNIX desmantelada en 2013 y nunca re-asegurada.

## Detección y defensa

Ordenado por efectividad:

1.
**Auditá y remové `DONT_REQ_PREAUTH` de cada cuenta.**
   La corrección definitiva. Consultá AD con `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` y o bien volvé a habilitar pre-auth o deshabilitá la cuenta. Programá la auditoría.

2.
**Aplicá contraseñas fuertes, largas y aleatorias en cualquier cuenta que deba mantener pre-auth deshabilitada.**
   Si una integración legacy genuinamente lo requiere, aumentá la longitud y entropía de la contraseña hasta que el crackeo offline sea impracticable (25+ caracteres aleatorios). Emparejá con tipos de cifrado solo-AES.

3.
**Detección de comportamiento sobre Event ID 4768.**
   Windows genera el Event 4768 (Kerberos Authentication Ticket Request) en cada `AS-REQ`. La señal de detección: eventos con `Pre-Authentication Type: 0` (PA-ENC-TIMESTAMP no presente). En un dominio donde ninguna cuenta debería tener pre-auth deshabilitada, *cualquier* evento así es una alerta de alta confianza.

4.
**Detección de comportamiento sobre la diversidad de fuentes AS-REQ.**
   Una única IP fuente intentando AS-REQ contra muchos nombres de usuario en rápida sucesión es una firma textbook de AS-REP-roasting independientemente de los flags de pre-auth.

5.
**Cuentas honeypot con `DONT_REQ_PREAUTH` configurado.**
   Plantar una cuenta falsa con pre-auth deshabilitada y una contraseña aleatoria fuerte que nadie conoce. Cualquier `AS-REQ` contra ella es un intento de AS-REP-roasting por definición. Defensa asimétrica — alerta de alta fidelidad, casi zero falsos positivos.

### Qué no funciona como defensa primaria

- **Bloquear Kerberos saliente.** AS-REP Roasting se realiza *contra* el KDC por cualquiera que pueda alcanzarlo.
- **Deshabilitar solo RC4.** Si pre-auth sigue deshabilitada, los AS-REPs cifrados con AES igualmente se emiten — solo más lentos de crackear. La defensa raíz es el flag, no el algoritmo.
- **Renombrar cuentas con pre-auth deshabilitada.** Seguridad por oscuridad.
- **Confiar en "no tenemos cuentas con pre-auth deshabilitada" sin verificar.** Siempre confirmá con la consulta bitmask LDAP mencionada arriba.

## Labs prácticos

Ejecutar solo contra entornos lab propios o engagements autorizados.

```
# Lab 1 — Crear una cuenta con pre-auth deshabilitada en un AD lab.
New-ADUser -Name "legacy_user" -SamAccountName "legacy_user" `
    -AccountPassword (ConvertTo-SecureString "Spring2019!" -AsPlainText -Force) `
    -Enabled $true
Set-ADAccountControl -Identity legacy_user -DoesNotRequirePreAuth $true
```

```
# Lab 2 — Enumerar cuentas con pre-auth deshabilitada SIN credenciales.
cat > users.txt <<EOF
administrator
legacy_user
backup_admin
svc_legacy_unix
random_user
EOF

impacket-GetNPUsers LAB.LOCAL/ -dc-ip 10.0.0.1 \
    -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hash
cat asrep.hash
```

```
# Lab 3 — Enumerar la lista vulnerable vía LDAP autenticado (si tenés alguna credencial).
impacket-GetNPUsers LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request
```

```
# Lab 4 — Crackear offline.
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```

```
# Lab 5 — Auditar tu propio AD para cuentas con pre-auth deshabilitada (lado defensor).
Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName, Enabled, DistinguishedName, LastLogonDate
```

```
# Lab 6 — Validar la detección desde el lado defensor.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 50 |
    Where-Object { $_.Properties[10].Value -eq '0' }   # PreAuthType = 0
# Cada resultado es un intento de AS-REP-roasting por definición.
```

## Ejemplos prácticos

- **Compromiso inicial solo con OSINT.** El atacante reúne diez direcciones de email de empleados de LinkedIn. Una de ellas (`legacy_user@corp.com`) es una cuenta de la era de 2011 cuyo propietario se fue de la empresa en 2014. AS-REP roast devuelve un hash crackeable; la contraseña es el nombre del usuario más su año de inicio. Contexto de dominio establecido sin nunca interactuar con el objetivo como usuario autenticado.
- **Cuenta fantasma de integración UNIX.** La cuenta `unix_kdc_proxy` fue creada en 2008 para hacer de puente con un realm MIT Kerberos. El realm fue desmantelado en 2012. La cuenta permaneció, con pre-auth deshabilitada y la contraseña original (`Welcome123`). Recuperada en segundos.
- **Honeypot atrapa al red team.** El defensor planta `svc_legacy_unix2` con pre-auth deshabilitada y una contraseña aleatoria de 40 caracteres. Seis meses después un red team realiza AS-REP roasting sin autenticación desde una cabecera de playa; la única cuenta que responde a sus consultas es la cuenta honeypot, disparando una alerta de alta confianza que termina el engagement.

## Notas relacionadas

- [[kerberoasting]] — el ataque sibling; misma economía de crackeo offline, diferente paso del protocolo, diferente precondición.
- [[silver-ticket-and-service-account-persistence]] — un uso downstream del material de clave de service account recuperado cuando una cuenta roasteada posee SPNs.
- [[password-hashing|Password hashing]] — la fortaleza del KDF es lo que determina el costo de crackeo.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — el único framing de detección útil aquí.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] — el playbook del lado defensor para esta nota.

## Referencias

- **Fundamental:** MITRE ATT&CK T1558.004 — Steal or Forge Kerberos Tickets: AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Investigación / Deep Dive:** Will Schroeder (harmj0y) — Roasting AS-REPs — https://blog.harmj0y.net/activedirectory/roasting-as-reps/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
