# Evilginx and Reverse Proxy Phishing

## Definición

El phishing con reverse proxy (también llamado AiTM — Adversary-in-The-Middle) es una técnica donde el atacante pone un proxy inverso entre la víctima y el sitio legítimo. El proxy retransmite el tráfico en tiempo real — incluyendo credenciales, respuestas MFA de un solo uso, y cookies de sesión — permitiendo al atacante capturar sesiones autenticadas incluso cuando MFA está habilitado.

## Por qué importa

El phishing AiTM invierte el threat model de MFA estándar. Los equipos de seguridad frecuentemente asumen que el phishing de credenciales está mitigado por MFA — "incluso si un usuario entrega su contraseña, el segundo factor protege la cuenta." El reverse proxy phishing falsifica esta suposición porque:

- El atacante no captura la contraseña para usarla después — **retransmite la sesión en tiempo real**, incluyendo el challenge de MFA que el usuario completa voluntariamente.
- El segundo factor (OTP, push de autenticación, SMS) se usa en la sesión del atacante, no en la de la víctima.
- El usuario completa el flujo de autenticación normalmente. Desde su perspectiva, el login fue exitoso en el sitio correcto.
- La sesión capturada es válida, completamente autenticada, con todos los scopes y privilegios del usuario víctima.

Evilginx es el framework más conocido que implementa este ataque. Es open source, activamente mantenido, y utilizado tanto por pentesters como por actores de amenaza reales (campañas de BEC, compromisos de tenant de M365, operaciones APT).

## Cómo funciona

El ataque tiene **5 componentes en movimiento**:

1. **Infraestructura del atacante** — un servidor controlado por el atacante con un dominio tipoquiat o similar que se hace pasar por el objetivo (por ejemplo, `login.micros0ft-sso.com`), con TLS válido (obtenido automáticamente por Evilginx o configurado manualmente).

2. **Proxy inverso en tiempo real** — Evilginx actúa como proxy HTTP que reenvía requests de la víctima al servidor legítimo y responses del servidor legítimo de vuelta a la víctima, reescribiendo hostnames en el camino (para que todos los links dentro del sitio del objetivo apunten al proxy).

3. **OTP relay** — cuando el servidor legítimo responde con el challenge de MFA, el proxy lo reenvía a la víctima. La víctima ingresa su OTP/aprueba el push — y esa respuesta pasa por el proxy al servidor legítimo, completando el flujo de autenticación **en la sesión del atacante**.

4. **Captura de cookie de sesión** — una vez que el servidor legítimo establece una cookie de sesión autenticada, el proxy la intercepta antes de reenviarla a la víctima (o captura una copia). El atacante tiene ahora la cookie de sesión post-autenticación.

5. **Uso de la sesión robada** — el atacante importa la cookie en su propio navegador o herramienta y tiene acceso completo a la cuenta, sin necesitar la contraseña ni el segundo factor.

Flujo de tiempo real:

```
Víctima → proxy Evilginx → sitio legítimo
                ↑ reescritura en tiempo real de hostnames
                ↑ captura de cookies de sesión
                ↑ relay de OTP
```

La víctima ve un sitio funcionalmente idéntico con TLS válido. Todas las interacciones se comportan normalmente. El único indicador es el hostname incorrecto en la barra de direcciones.

## Técnicas / patrones

### "Phishlets" de Evilginx

Evilginx usa archivos de configuración YAML llamados "phishlets" que definen:
- Los hostnames que reescribir (el servidor de autenticación del objetivo, subdominio de API, etc.)
- Qué cookies capturar (por nombre, dominio, flags)
- Los "lures" — URLs de phishing configuradas para víctimas específicas

Hay phishlets públicamente disponibles para Microsoft 365, Google Workspace, LinkedIn, Twitter, GitHub, Okta, y docenas de targets adicionales.

### Cadena completa con lure personalizado

1. El atacante configura Evilginx con el phishlet del objetivo.
2. Genera un "lure" — una URL de aterrizaje en el dominio proxy que redirige a la página de login real del objetivo (pero a través del proxy).
3. Entrega la URL de lure vía phishing de email, mensaje directo, o SMS.
4. La víctima hace click, pasa por el flujo de autenticación completo incluyendo MFA.
5. Evilginx captura la cookie de sesión y la muestra en la consola del atacante.
6. El atacante usa la cookie en su navegador.

### Escalada post-compromiso

Con una sesión de Microsoft 365 o Google Workspace capturada, los atacantes frecuentemente proceden a:
- Persistencia por OAuth: registrar una app OAuth maliciosa con permisos amplios para mantener acceso después de que la cookie expire o el usuario revoque la sesión.
- Exfiltración de email: leer o redirigir mensajes.
- Lateral movement: usar la sesión comprometida para phishing interno ("el CEO" enviando links maliciosos a empleados).
- Business Email Compromise (BEC): interceptar comunicaciones financieras.

## Variantes y bypasses

### AiTM sin Evilginx

Cualquier proxy inverso puede implementar el mismo patrón. Modlishka, Muraena, y Caido (con scripting) pueden realizar ataques AiTM. Evilginx es el más conocido pero no es el único.

### AiTM contra apps SAML / SSO

El mismo patrón aplica a flujos de SAML y OIDC donde el proxy se sienta delante del IdP (proveedor de identidad). El SP (service provider) recibe una aserción SAML legítima porque fue emitida por el IdP real — el proxy solo la retransmitió.

### Proxies residenciales para evasión de detección

Los defensores frecuentemente detectan campañas AiTM mirando el país/IP de origen de los requests de autenticación. Los atacantes usan proxies residenciales para que el request al IdP parezca originarse desde la IP residencial de la víctima.

### Combinación con adversarial ML para evasión de brand protection

Las herramientas de brand protection detectan páginas de phishing por similitud visual con sitios de destino conocidos. Los dominios de phishing AiTM pueden usar el sitio legítimo real como contenido (porque es un proxy), haciendo que la detección por similitud visual sea más difícil.

## Impacto

- **Bypass completo de MFA para factores OTP, push, y SMS.** Cualquier MFA que se complete a través del browser puede ser relayado. Esto incluye TOTP (Google Authenticator), Authy, SMS OTP, y notificaciones push (Microsoft Authenticator en modo "approve/deny").
- **Sesión post-autenticación con todos los permisos del usuario.**
- **Persistencia vía OAuth** después de la captura inicial de sesión.
- **Acceso al tenant completo** en escenarios de M365/Google Workspace comprometidos.
- **Fraude financiero / BEC** con acceso a email.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar WebAuthn / Passkeys (FIDO2) en lugar de OTP o push.**
   Esta es la única defensa que cierra el vector AiTM por diseño. WebAuthn hace una **aserción bound al origen**: durante el registro, la clave se asocia al origin exacto (`https://accounts.google.com`). Durante la autenticación, el navegador verifica el origin y se niega a firmar si no coincide con el dominio registrado. Un proxy AiTM en `login.g00gle-sso.com` recibe un origin diferente — la autenticación falla criptográficamente. El atacante no puede retransmitir el challenge porque la firma del autenticador es específica al dominio legítimo. **Ningún otro segundo factor aborda esto por diseño** — TOTP, SMS, y push son retransmisibles.

2.
**Implementar atado de sesión a fingerprint de dispositivo / IP.**
   Detectar y revocar sesiones que son usadas desde IPs, zonas horarias, o fingerprints de navegador dramáticamente diferentes del login inicial. Esto no previene el compromiso inicial pero acorta el tiempo de uso de la sesión robada. Microsoft y Google Workspace implementan esto como "Conditional Access" / "context-aware access".

3.
**Monitorear señales AiTM en los logs de autenticación.**
   Señales específicas: login exitoso seguido inmediatamente de uso de sesión desde una IP diferente a la del login; acceso a aplicaciones OAuth inusuales justo después del login; patrón de "login desde país A, uso de sesión desde país B dentro de los mismos minutos"; logins exitosos con OTP donde el usuario reporta no haber iniciado sesión.

4.
**Aplicar Conditional Access con controles de dispositivo.**
   Requerir que los dispositivos estén registrados y en estado saludable (MDM enrolled, endpoint compliance). Las cookies robadas no pueden usarse en un dispositivo no registrado si el Conditional Access enforce compliance de dispositivo.

5.
**Usar Certificate-based Authentication (CBA) o certificados de dispositivo.**
   Similar a WebAuthn, los certificados de cliente están bound al dispositivo, no son retransmisibles por un proxy. Más complejo de desplegar que WebAuthn pero efectivo contra AiTM.

6.
**Capacitación de usuarios enfocada en verificación de URL.**
   WebAuthn es la solución técnica; mientras se implementa, los usuarios que verifican el hostname antes de ingresar credenciales son más resistentes. Los indicadores específicos de Evilginx incluyen dominios typosquatted y el hecho de que la URL nunca muestra el dominio legítimo.

7.
**Monitorear registros de dominios typosquatted.**
   Servicios como DomainTools, PhishLabs, y Cloudflare Brand Protection monitorean registros de nuevos dominios por similitud con la marca. Los dominios de Evilginx frecuentemente se registran días antes de una campaña.

### Qué no funciona como defensa primaria

- **TOTP (Google Authenticator, Authy, etc.)** — el código de 6 dígitos se retransmite en tiempo real. El atacante lo ingresa en el sitio legítimo dentro de los 30 segundos de vigencia del TOTP. Esta es la demostración más clara de por qué TOTP no es resistente a phishing.
- **SMS OTP** — igual que TOTP, retransmisible.
- **Push de autenticación (Microsoft Authenticator "Approve/Deny")** — el servidor legítimo envía la notificación push cuando el proxy retransmite las credenciales. El usuario ve una notificación legítima de su app de autenticación y la aprueba. La aprobación es la señal de que la autenticación fue exitosa en la sesión del atacante.
- **Number matching en push** — parcialmente más resistente porque requiere que el usuario compare el número mostrado en la pantalla del login con el de la notificación push. Un proxy AiTM puede retransmitir el número correcto. No es una defensa robusta.
- **Bloquear IPs de Evilginx conocidas** — la infraestructura del atacante cambia. No es una estrategia.
- **Solo detección basada en similitud de phishing page** — el proxy sirve el sitio legítimo real; la detección visual es difícil.

## Ejemplos prácticos

- Un empleado recibe un email de phishing con un link que parece ser el portal de login de M365 de la empresa. Ingresa credenciales y aprueba la notificación push de Microsoft Authenticator. Evilginx captura la cookie de sesión. El atacante usa la cookie para acceder al email, registra una app OAuth maliciosa, y mantiene acceso después de que la sesión expire.
- Un pentest muestra que el cliente tiene MFA habilitado con TOTP para todos los usuarios. El equipo de red team usa Evilginx con el phishlet de Okta, genera un lure, y lo envía a un usuario objetivo. La sesión capturada proporciona acceso completo al tenant Okta — demostrando que "MFA habilitado" no equivale a "resistente a phishing".
- Una campaña de BEC usa AiTM para comprometer el email del CFO. El atacante redirige todas las comunicaciones con el departamento financiero durante días, interceptando una transferencia bancaria en curso.

## Notas relacionadas

- [[mfa-and-auth-factors]] — las limitaciones de TOTP/push vs. la solidez de WebAuthn.
- [[oauth-security]] — la escalada post-AiTM vía OAuth es la técnica de persistencia más común.
- [[session-management]] — la cookie de sesión robada es el artefacto principal de explotación.
- [[phishing]] — el AiTM es la variante de phishing más sofisticada; el delivery del lure usa técnicas de phishing estándar.

## Referencias

- **Investigación / Deep Dive:** Microsoft blog "From cookie theft to BEC: Attackers use AiTM phishing sites as entry point to further financial fraud" — https://www.microsoft.com/en-us/security/blog/2022/07/12/from-cookie-theft-to-bec-attackers-use-aitm-phishing-sites-as-entry-point-to-further-financial-fraud/
- **Docs Oficiales:** Evilginx — https://github.com/kgretzky/evilginx2
- **Fundamental:** FIDO Alliance WebAuthn overview — https://fidoalliance.org/fido2/
- **Investigación / Deep Dive:** PortSwigger Research — FIDO2 / WebAuthn phishing resistance — https://portswigger.net/research
