---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - identity-and-active-directory
  - cross-idp
  - lateral-movement
  - federation
  - cloud-security
sources:
  - "[[wiki/sources/Attack Paths Don't Stop at Identity Providers]]"
---

# Rutas de ataque de identidad entre IdPs

## Definición
Las rutas de ataque cross-IdP son cadenas de movimiento lateral que propagan el compromiso *a través de las fronteras de plataforma* atravesando las aristas de confianza — **federación, sincronización de directorio y SSO** — que atan el Active Directory on-prem, los proveedores de identidad de nube (Entra ID, Okta) y el SaaS aguas abajo (GitHub Enterprise, Google Workspace) entre sí. La unidad de análisis se mueve de un único directorio a la **cadena de dependencias anidada**, porque la seguridad de cada plataforma aguas abajo está acotada por su fuente de identidad *aguas arriba* más débil. Según el encuadre de Jared Atkinson (la única fuente sobre la que se apoya esta nota), la ruta de ataque no se detiene en el proveedor de identidad — el IdP es un hop, no un muro.

## Por qué importa
El análisis de rutas de ataque on-prem de AD es maduro; el plano SaaS al que ahora alimenta no lo es. Tres lecciones transferibles:

- **La identidad es anidada, no plana.** Okta y Entra no *crean* identidad — *traducen* identidad originada en otro lado (comúnmente AD on-prem vía sync, o un HRIS como Workday). La verdadera raíz de confianza es lo que sea que alimente al IdP, así que "aseguramos Okta" se pierde que AD es efectivamente Tier 0 para todo el estado SaaS.
- **La arista de confianza es la nueva primitiva de movimiento lateral.** Así como pass-the-hash reusa credenciales on-prem, las rutas cross-IdP reusan *confianza*: una aserción de federación, una propagación de sync o un token SSO carga el compromiso de una plataforma a la siguiente. La arista — no el host — es la unidad de movimiento en la era SaaS.
- **Los huecos entre plataformas son la superficie de ataque.** El movimiento lateral moderno es cada vez más cross-plataforma — AD → Entra/Okta → GitHub Enterprise → código fuente / CI-CD — y cada hop corre sobre un protocolo distinto con controles distintos. La costura entre dos plataformas bien aseguradas es donde vive la ruta no modelada.

> **Caveat de confianza-en-la-fuente (traído de la literature note).** Esta nota deriva de una única fuente conceptual de un ejecutivo de un vendor (SpecterOps). Su afirmación central de prevalencia — que estas rutas son *cada vez más la primaria* en compromisos reales — está aseverada, no aún demostrada con datos de incidentes. Tratá la *forma* del problema como bien argumentada y la *frecuencia* como abierta. La fuente además es ciega-al-defensor; la guía de detección de abajo está sintetizada, no sacada de ella.

## Cómo funciona
Una app SaaS confía en un IdP; el IdP confía en una fuente aguas arriba; el compromiso se propaga hacia abajo por las aristas que pueda alcanzar:

```text
AD on-prem / HRIS   ──sync──▶   Entra ID / Okta   ──SSO + federación──▶   SaaS (GitHub, Workspace)
 (raíz de confianza)              (traductor)                              (aguas abajo; acotado por el upstream)
```

La propagación corre sobre **3 tipos de arista-de-confianza**, cada uno con alcanzabilidad distinta:

1. **Federación (SAML / WS-Fed).** El IdP asevera identidad a un service provider vía aserciones *firmadas*. Comprometé la clave de firma de tokens o la configuración de federación y podés forjar una aserción para *cualquier* usuario aguas abajo (el patrón Golden SAML).
2. **Sincronización de directorio (SCIM / Entra Connect / Okta AD agent).** Los objetos de usuario y grupo, y su membresía, fluyen de AD hacia el IdP. Controlá la fuente de sync — o una cuenta de sync privilegiada — e inyectás o modificás identidades aguas abajo. Las reglas de sync que propagan un grupo que sostiene la estructura como **Domain Users** pueden crear privilegio SaaS que los admins de AD nunca se dan cuenta de que otorgaron.
3. **SSO (OIDC / OAuth).** El IdP emite tokens a las apps. El robo o replay de tokens, el abuso de OAuth app-consent y los refresh tokens de larga vida viajan por esta arista hacia la aplicación.

La cadena canónica (el ejemplo trabajado de la fuente): una cuenta de AD on-prem comprometida se propaga vía sync/federación hacia Okta/Entra, que hace fan-out vía SSO a GitHub Enterprise, alcanzando el código fuente y CI/CD. La seguridad de GitHub está acotada por la seguridad de lo que sea que alimente al IdP — usualmente AD on-prem.

El bug no es ninguna plataforma individual; es que las *aristas de confianza entre ellas* están sin modelar, así que un compromiso alto en la cadena alcanza todo lo que está aguas abajo de él.

## Técnicas / patrones
- **Mapeá la topología de confianza primero.** Enumerá qué alimenta al IdP (Entra Connect, Okta AD agent, HRIS), a qué apps hace fan-out el IdP, y qué reglas de sync propagan membresía de grupos. El grafo *es* la superficie de ataque.
- **Encontrá el Tier 0 real.** Cualquier cuenta que pueda escribir a la fuente de sync o alterar la configuración de federación es efectivamente Tier 0 a través de todo el estado SaaS — aunque parezca una cuenta de servicio de bajo tier on-prem.
- **Abuso de confianza-de-federación (Golden SAML).** Robá el certificado de firma de tokens (p. ej., de ADFS) para forjar aserciones SAML para identidades arbitrarias aguas abajo — independiente de contraseñas o MFA en el SP.
- **Abuso de cuenta-de-sync.** La cuenta de sync AD↔Entra es altamente privilegiada y un pivot híbrido conocido; comprometerla manipula la identidad aguas abajo directamente.
- **Abuso de token y consent de SSO.** Los grants de OAuth app-consent, la longevidad de refresh-tokens y los huecos de conditional-access extienden el acceso a las apps sin re-autenticar.
- **Tooling de enumeración cross-IdP.** BloodHound CE (Azure/Entra), AzureHound y ROADtools construyen el grafo de identidad de nube; el graphing cross-*plataforma* a escala está actualmente sesgado hacia el BloodHound Enterprise OpenGraph comercial, con solo análogos FOSS parciales (un hueco honesto, según la fuente).

## Variantes y bypasses
Las **3 aristas de confianza** son los ejes de variante; cada una es una familia de ruta-de-ataque distinta.

### 1. Arista de federación (SAML / WS-Fed)
Golden SAML, manipulación de federation-config y robo de certificado de firma de tokens le dejan a un atacante forjar aserciones para cualquier service provider aguas abajo. Sobrevive a los resets de contraseña y al MFA del lado del SP porque la confianza está en la clave de firma, no en la credencial del usuario.

### 2. Arista de sincronización de directorio (SCIM / Entra Connect / Okta AD agent)
El compromiso de la cuenta-de-sync, el abuso de reglas-de-sync y la propagación de grupos demasiado amplia (el caso Domain Users) inyectan o modifican identidades y membresía aguas abajo. El objeto on-prem se vuelve el principal SaaS.

### 3. Arista de SSO (OIDC / OAuth)
El robo/replay de tokens, el phishing de OAuth app-consent y el abuso de refresh-tokens viajan por la arista del token-emitido hacia las aplicaciones. Conditional Access *reforma* este camino (forzando al atacante a satisfacer también señales de dispositivo/riesgo) en vez de eliminarlo.

## Impacto
Ordenado por severidad:

- **Movimiento lateral cross-plataforma.** Un único punto de apoyo on-prem alcanza el estado SaaS completo vía las aristas de confianza — el resultado de radio-de-explosión más amplio.
- **Compromiso de código fuente y CI/CD.** Alcanzar GitHub Enterprise (o equivalente) rinde acceso al código fuente y al pipeline — un punto de apoyo de cadena de suministro.
- **Escalada de privilegios vía Tier 0 no reconocido.** La fuente de sync o la federation-config es efectivamente Tier 0; abusarla otorga privilegio SaaS-wide desde una posición on-prem de apariencia baja.
- **Persistencia durable.** El abuso de federación (Golden SAML) persiste a través de los resets de credenciales porque forja confianza en vez de robar una contraseña.

## Detección y defensa
La fuente no provee contenido de detección; lo siguiente está sintetizado y debería validarse contra un entorno híbrido real. Ordenado por efectividad:

1. **Mapeá y minimizá la topología de confianza; extendé Tier 0 a la fuente de sync y la federation-config.**
   Tratá cualquier cuenta o sistema que pueda escribir la fuente de sync o alterar la federación como Tier 0, y aplicale [[tier-zero-administration-and-paw|disciplina de PAW/Tier-0]]. La mayor parte del riesgo cross-IdP se reduce a "un Tier 0 no reconocido era alcanzable".

2. **Acotá la sincronización estrechamente.**
   No propagues Domain Users ni grupos amplios aguas abajo; filtrá el scope de sync exactamente a los objetos que cada plataforma SaaS necesita. La sobre-propagación es la mala-configuración que sostiene la estructura en el ejemplo trabajado.

3. **Protegé las claves de firma de federación.**
   Guardá los certificados de firma de tokens en un HSM, rotalos y monitoreá su exportación — la defensa estructural contra Golden SAML.

4. **Endurecé la arista de SSO.**
   Vidas de token cortas, Conditional Access con gating de dispositivo + riesgo, y gobernanza de OAuth app-consent encogen el camino de ataque de SSO (y lo reforman para que un único token robado sea insuficiente).

5. **Construí detección cross-IdP (el hueco actual de la literatura).**
   Monitoreá y correlacioná los audit logs de IdP/SaaS — Okta System Log, sign-in/audit de Entra, audit de GitHub — buscando anomalías de SCIM-sync, cambios de federation-config, reuso de tokens e impossible-travel *entre plataformas*. Esta es la extensión al plano-SaaS de la detección de BloodHound on-prem y está actualmente subespecificada — una dirección de investigación abierta, no un playbook resuelto.

### Qué no funciona como defensa primaria
- **Asegurar cada plataforma en aislamiento.** "Endurecimos Okta" se pierde que AD (vía sync) es la raíz de confianza real. El punto central de la fuente: la unidad de análisis debe ser la cadena, no la plataforma.
- **Tratar el IdP como la frontera de confianza.** El IdP es un hop. Su seguridad aguas abajo está acotada por su fuente aguas arriba.
- **Asumir que Conditional Access cierra el camino.** CA *reforma* el camino a "comprometer la credencial *y* la señal de device-trust"; sube el costo pero no elimina la arista de confianza.

## Labs prácticos
Restricción honesta: a diferencia de un tema de un-solo-binario o una-sola-app-web, las rutas de ataque cross-IdP necesitan un *entorno híbrido propio* (AD + Entra/Okta + una app SaaS) para ejercitarse end-to-end. Los labs de abajo son ejercicios de topología/enumeración de solo-lectura contra un tenant que sea tuyo o que estés autorizado a evaluar.

### Enumerar el grafo de identidad de nube (tenant propio)
```bash
# AzureHound recolecta identidades, roles y relaciones de app de Entra ID en un
# grafo importable a BloodHound-CE. Solo tenant autorizado.
azurehound -u "<user>" -p "<pass>" --tenant "<tenant-id>" list --output azure.json
# Después importá azure.json a BloodHound CE y buscá caminos desde principals de
# bajo-tier a nodos de app/rol privilegiados.
```

### Inventariar las aristas de confianza que alimentan tu IdP
```text
Para un tenant propio, documentá:
  - Sync:        Entra Connect / Okta AD agent — ¿qué OUs/grupos están en scope?
  - Federación:  qué dominios están federados; ¿dónde viven los certs de firma?
  - Apps SSO:    qué apps SaaS confían en el IdP; ¿cuáles usan provisioning SCIM?
Las cuentas que pueden escribir cualquiera de estas son tu Tier 0 cross-IdP.
```

### Revisar el scope de propagación de grupos
```text
Chequeá si Domain Users (u otros grupos amplios) se propaga aguas abajo vía reglas
de sync a cualquier asignación de rol SaaS. La ruta de ataque del ejemplo trabajado depende
exactamente de esta sobre-propagación; los tenants maduros la filtran.
```

### Inspeccionar señales de audit de federación/sync
```text
En los audit logs de Entra / Okta System Log, ubicá los tipos de evento para:
  - cambios de configuración de federación, updates de certs de firma
  - nuevo provisioning SCIM / cambios de reglas de sync
  - grants de OAuth app-consent
Estos son la materia prima para la detección cross-IdP que a la literatura todavía le falta.
```

## Ejemplos prácticos
- **AD → Okta → GitHub Enterprise → código fuente.** La cadena trabajada de la fuente: una cuenta on-prem se propaga a través de sync/federación al IdP, después SSO hacia GitHub, alcanzando código y CI/CD. (Los detalles de Domain-Users-a-GitHub dependen de que la org haya propagado Domain Users a través del scope de sync — las orgs maduras lo filtran.)
- **Golden SAML.** Un certificado de firma de tokens de ADFS robado se usa para forjar aserciones SAML para usuarios arbitrarios, otorgando acceso cloud-SaaS independiente de contraseñas o MFA del lado del SP — la técnica de la arista-de-federación demostrada a escala en las intrusiones de SolarWinds/SUNBURST.
- **Abuso de cuenta-de-sync de Entra Connect.** El compromiso de la cuenta de sync híbrida manipula la identidad y membresía aguas abajo directamente, escalando de on-prem a nube.
- **Phishing de OAuth app-consent.** Se engaña a un usuario para que consienta a una app OAuth maliciosa, otorgando al atacante acceso SaaS persistente basado-en-token que sobrevive a los resets de contraseña — la variante de la arista-de-SSO.

## Notas relacionadas
- [[bloodhound-attack-path-analysis|Análisis de rutas de ataque con BloodHound]] — el padre del grafo-de-ruta-de-ataque on-prem que este concepto extiende a través de las fronteras de IdP.
- [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-hash y reuso de credenciales NTLM]] — el análogo on-prem de reuso-de-credenciales; las rutas cross-IdP son el equivalente de la era SaaS (reuso de confianza/token).
- [[golden-ticket-and-krbtgt-compromise|Golden Ticket y compromiso de krbtgt]] — Golden Ticket es a Kerberos lo que Golden SAML es a la federación: forjar el artefacto de confianza en vez de robar una credencial.
- [[tier-zero-administration-and-paw|Administración de Tier 0 y PAW]] — la disciplina de Tier 0 que debe extenderse a la fuente de sync y la federation-config.
- [[dcsync-and-ntdsdit-extraction|DCSync y extracción de NTDS.dit]] — el endgame de credenciales on-prem que a menudo siembra el compromiso aguas arriba que alimenta la cadena.
- [[cybersecurity/cloud-security/index|Seguridad en la Nube]] — las rutas cross-IdP abarcan identidad y nube; el branch de nube es la mitad aguas abajo.
- [[cybersecurity/security-playbooks/detect-bloodhound-collection|Detectar la recolección de BloodHound]] — el par de detección on-prem; el equivalente de detección del plano-SaaS es el hueco abierto notado arriba.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — ofensa (traversal de arista-de-confianza) vs defensa (minimización de topología-de-confianza).

### Notas atómicas futuras sugeridas
- [[golden-saml-and-federation-abuse|Golden SAML y abuso de federación]]
- [[entra-connect-and-hybrid-identity-attacks|Entra Connect y ataques de identidad híbrida]]
- [[oauth-token-and-consent-abuse|Abuso de tokens y consent de OAuth]]
- [[detect-cross-idp-attack-paths|Detectar rutas de ataque cross-IdP]]
- [[saas-identity-tier-zero|Tier 0 de identidad SaaS]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Research / Deep Dive:** Jared Atkinson (SpecterOps) — Attack Paths Don't Stop at Identity Providers — https://specterops.io/blog/2026/03/24/attack-paths-dont-stop-at-identity-providers/
- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps; models Entra/Azure attack paths) — https://bloodhound.specterops.io/
- **Foundational:** MITRE ATT&CK T1199 — Trusted Relationship — https://attack.mitre.org/techniques/T1199/
- **Foundational:** MITRE ATT&CK T1556 — Modify Authentication Process — https://attack.mitre.org/techniques/T1556/
