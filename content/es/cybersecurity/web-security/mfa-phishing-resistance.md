---
type: concept
status: active
created: 2026-05-01
updated: 2026-05-01
tags:
  - cybersecurity
  - web-security
  - authentication
  - mfa
  - phishing-resistance
sources:
  - "https://pages.nist.gov/800-63-4/sp800-63b.html"
  - "https://www.cisa.gov/mfa"
  - "https://fidoalliance.org/passkeys/"
---

# Resistencia al phishing del MFA

## Definición
La resistencia al phishing del MFA es la propiedad de que un método de autenticación no puede producir un secreto reusable ni un resultado de autenticación válido para un origen impostor, aunque se engañe al usuario para que interactúe con ese impostor.

## Por qué importa
El MFA no es una sola cosa. Los códigos SMS, las apps TOTP, las aprobaciones push, los tokens OTP de hardware, las passkeys, WebAuthn, las smart cards y las credenciales atadas-al-dispositivo se comportan distinto bajo presión de phishing.

El modal de 6 dígitos inyectado del viejo proyecto mirror es el gancho didáctico perfecto: un código que un usuario tipea en una página puede ser relayeado. Un autenticador criptográfico correctamente configurado y atado-al-origen no puede ser reproducido a un relying party distinto.

## Cómo funciona
Usá el **test de resistencia de MFA de 4 preguntas**:

1. **¿Hay una salida legible por el usuario?**
   Si aparece un código y el usuario puede tipearlo, un proxy de phishing puede pedirlo.

2. **¿La salida está atada al origen legítimo?**
   Si el resultado no está atado al dominio real o al canal TLS, a menudo puede ser relayeado.

3. **¿El autenticador prueba la intención?**
   El usuario debería aprobar a sabiendas el login específico, no solo responder a un prompt genérico.

4. **¿La sesión resultante puede reusarse en otro lado?**
   Incluso un MFA fuerte puede socavarse si las cookies de sesión o los caminos de recuperación son débiles.

Comparación:

```text
TOTP:
  el usuario ve 123456 -> lo tipea en la página impostora -> el proxy lo relayea al servicio real

WebAuthn/passkey:
  el navegador le pide al autenticador por example.com -> impostor.test no puede obtener
  una aserción válida para example.com
```

El bug no es "el MFA falló". El bug es elegir un método de MFA cuya prueba puede relayearse a través del origen equivocado.

## Técnicas / patrones
- Inventariá los métodos de MFA por clase de cuenta: usuarios, admins, cuentas de servicio, contratistas, flujos de recuperación.
- Marcá cada método como phisheable, resistente-al-relay, resistente-al-phishing o desconocido.
- Chequeá si los flujos de alto riesgo usan autenticación más fuerte que el sign-in ordinario: enrolamiento de MFA, reset de contraseña, registro de dispositivo, consent de OAuth, creación de tokens de API.
- Distinguí el number matching del origin binding. El number matching mejora la intención del push pero no vuelve a un método equivalente a WebAuthn.
- Tratá los flujos de recuperación y helpdesk como parte de la autenticación. Los atacantes a menudo bypasean un sign-in fuerte a través de caminos de reset débiles.
- Logueá juntos el método de MFA, el dispositivo, la sesión y la acción post-autenticación.

## Variantes y bypasses
Los métodos de MFA caen en **5 clases útiles**.

### 1. Contraseña más SMS o OTP por email
Mejor que la contraseña sola, pero los códigos se tipean en una página y pueden relayearse o ser socialmente ingenierados.

### 2. App TOTP
Evita los riesgos de telco pero sigue siendo phisheable porque el usuario lee e ingresa un código basado en tiempo.

### 3. Aprobación push
Reduce el tipeo pero puede abusarse mediante prompt bombing o contexto engañoso. El number matching ayuda, pero igual se puede engañar al usuario.

### 4. Token OTP de hardware o app
Puede ser más fuerte operativamente, pero si emite un código que el usuario tipea en una página, la salida igual es relayeable.

### 5. WebAuthn / passkeys / FIDO
Usa criptografía de clave pública y binding al relying-party. El autenticador no le entrega al usuario un código reusable y no produce una aserción válida para el origen equivocado.

## Impacto
- **Radio de explosión de phishing reducido.** El MFA atado-al-origen puede frenar el phishing por proxy donde el MFA basado-en-OTP no puede.
- **Endurecimiento de cuentas de admin.** Los usuarios privilegiados se benefician más de los métodos resistentes-al-phishing.
- **Menor impacto de credential-stuffing.** El reuso de contraseñas se vuelve menos decisivo cuando la autenticación requiere un factor no-relayeable.
- **Presión sobre el flujo de recuperación.** Los atacantes se corren al helpdesk, el enrolamiento de dispositivos, el robo de tokens, el consent de OAuth y el secuestro de sesiones.
- **Complejidad de migración.** Las apps legacy, las cuentas compartidas, los contratistas y los dispositivos no soportados pueden ralentizar la adopción.

## Detección y defensa
Ordenado por efectividad:

1. **Requerí MFA resistente-al-phishing para las cuentas de alto riesgo**
   Admins, desarrolladores, usuarios de finanzas, admins de identidad y staff de soporte deberían usar WebAuthn/passkeys, smart cards o autenticadores criptográficos equivalentes primero.

2. **Llevá las poblaciones amplias de usuarios hacia passkeys/WebAuthn**
   La resistencia al phishing escala mejor cuando se vuelve el camino por defecto, no una excepción especial de admin.

3. **Protegé el enrolamiento y la recuperación**
   Un sign-in fuerte se socava si los atacantes pueden registrar un nuevo factor, resetear el MFA o recuperar una cuenta a través de un proofing de helpdesk débil.

4. **Usá number matching y contexto donde WebAuthn todavía no es posible**
   Esto reduce las aprobaciones push accidentales y la fatiga de MFA, pero debería tratarse como una mejora interina.

5. **Atá las sesiones y re-autenticá las acciones riesgosas**
   Las sesiones atadas-al-dispositivo, la protección de tokens y la autenticación step-up reducen el daño cuando una sesión es sospechosa.

6. **Monitoreá por método de MFA**
   Rastreá qué métodos se usan, dónde se agrupan las fallas y si las acciones riesgosas siguen a métodos más débiles.

### Qué no funciona como defensa primaria
- **Decir "tenemos MFA" sin nombrar el método.** La fuerza del MFA depende del método y del workflow.
- **SMS/TOTP como controles resistentes-al-phishing.** Son útiles pero relayeables.
- **Aprobación push sin contexto.** Los usuarios pueden aprobar prompts que no iniciaron.
- **Indicadores de HTTPS.** Un dominio de phishing puede tener TLS válido.
- **Solo entrenamiento.** El entrenamiento ayuda, pero la resistencia al phishing no debería depender solo de la vigilancia del usuario.

## Labs prácticos

### Clasificar métodos de MFA

```text
método | salida legible por usuario | atado-al-origen | resistente-al-replay | resistente-al-phishing | población actual
SMS    | sí                         | no              | parcial              | no                     |
TOTP   | sí                         | no              | limitado por tiempo  | no                     |
Push   | no/el código varía         | débil/no        | parcial              | usualmente no          |
WebAuthn/passkey | no               | sí              | sí                   | sí                     |
```

Este inventario convierte una postura de MFA vaga en un mapa de migración accionable.

### Mapear los flujos de alto riesgo

```text
flujo | auth actual | step-up requerido | ¿resistente-al-phishing? | dueño | hueco de migración
login de admin |
reset de MFA |
enrolamiento de dispositivo |
consent de OAuth |
creación de token de API |
cambio de pago |
```

Los atacantes apuntan al flujo más débil que puede cambiar el estado de autenticación.

### Revisar eventos de MFA sospechosos

```text
usuario:
método:
hora del prompt:
¿login iniciado por el usuario?
ASN de origen:
dispositivo:
number matching usado:
acción post-login:
```

Esto distingue la fricción ordinaria de MFA de los patrones de relay o fatiga.

### Testear el origin binding conceptualmente

```text
RP ID legítimo: example.com
origen impostor: examp1e-login.test
método: WebAuthn/passkey
resultado esperado: el autenticador no puede producir una aserción válida para example.com desde el origen impostor
```

Esta es la razón central por la que las passkeys resisten el phishing por reverse-proxy.

### Planear un anillo de migración

```text
anillo 1: admins de identidad
anillo 2: desarrolladores y finanzas
anillo 3: helpdesk y ejecutivos
anillo 4: todos los empleados
anillo 5: clientes / usuarios externos
política de fallback:
política de recuperación:
```

El MFA resistente-al-phishing funciona mejor como un programa por etapas, no un switch de un día.

## Ejemplos prácticos
- Un código TOTP ingresado en un modal falso se relayea antes de que expire.
- Un prompt push se aprueba porque el usuario espera un login, pero el login fue iniciado por un atacante.
- El number matching bloquea la aprobación push ciega pero igual depende de que el usuario entienda el contexto.
- Una passkey falla en un dominio parecido porque la identidad del relying-party no coincide.
- Un atacante que no puede phishear WebAuthn pivotea al reset de helpdesk o al enrolamiento de un nuevo dispositivo.

## Notas relacionadas
- [[cybersecurity/web-security/evilginx-and-reverse-proxy-phishing|Evilginx y phishing por reverse-proxy]]
- [[cybersecurity/web-security/auth-flaws|Fallas de autenticación]]
- [[cybersecurity/web-security/session-management|Gestión de sesiones]]
- [[cybersecurity/api-security/token-lifecycle|Ciclo de vida de tokens]]
- [[cybersecurity/privacy-anonymity-opsec/account-correlation|Correlación de cuentas]]

### Notas atómicas futuras sugeridas
- [[passkeys-and-webauthn|Passkeys y WebAuthn]]
- [[mfa-fatigue-attacks|Ataques de fatiga de MFA]]
- [[helpdesk-social-engineering|Ingeniería social al helpdesk]]
- [[session-token-protection|Protección de tokens de sesión]]
- [[oauth-consent-phishing|Phishing de consent de OAuth]]

## Referencias
- **Foundational:** NIST SP 800-63B: Authentication and Lifecycle Management — https://pages.nist.gov/800-63-4/sp800-63b.html
- **Mitigation:** CISA: More than a Password / MFA — https://www.cisa.gov/mfa
- **Foundational:** FIDO Alliance: Passkeys — https://fidoalliance.org/passkeys/
