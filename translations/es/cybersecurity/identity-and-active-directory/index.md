# Índice de Identity and Active Directory

## Propósito

Esta rama cubre ataques y defensas de sistemas de identidad centrados en **Active Directory**, **Kerberos** y **análisis de rutas de ataque basado en grafos**. AD es el sistema de identidad autoritativo más atacado en entornos empresariales porque (a) un AD completamente comprometido equivale a compromiso total de la empresa, y (b) los protocolos que hacen útil a AD también exponen estructura atacable (derechos de replicación, claves de cifrado derivadas de contraseñas, membresías transitivas de grupos, ACEs delegadas).

Usá [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]] como fuente de verdad para las referencias en esta rama.
Volvé a [[index|Cybersecurity Index]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[index|Networking]] — Kerberos corre en UDP/TCP 88 y LDAP en 389/636; el contexto de protocolo importa.
> - [[index|Cryptography]] — todo ataque de credenciales en AD se reduce a la fortaleza del KDF + elección de cifrado simétrico (RC4 vs AES). Leé [[password-hashing|password hashing]] y [[symmetric-encryption-modes|symmetric encryption modes]] antes de esta rama.
> - **Emparejá cada nota con su contraparte de [[index|Detection Engineering]].** Los ataques a AD *no* tienen firma; solo funciona la detección de comportamiento.

---

## Posicionamiento de la rama

Esta rama se ubica en Fase 4 — **Tracks especializados** — según la clasificación del roadmap-v2: leela cuando AD es parte de tu contexto laboral (operador red-team, admin AD, analista IR, ingeniero de plataformas de identidad). Pero también es un caso de estudio profundo de Fase 2 porque cada nota en esta rama *es* un par ofensiva/defensiva. Ver [[phase-4-specialty|Phase 4 — Specialty Tracks]] para contexto.

---

## Orden de aprendizaje recomendado

### Núcleo de primer paso (11 notas)

1. [[bloodhound-attack-path-analysis]] — la capa de visibilidad. Leela primero porque dice qué ataques AD vale la pena hacer, qué cuentas vale la pena atacar y qué rutas defensivas remediar primero. El ejemplo más limpio de dualidad ofensiva/defensiva en todo el atlas.
2. [[as-rep-roasting]] — el ataque *pre-foothold*. No necesita credenciales; solo nombres de usuario y una cuenta con pre-autenticación deshabilitada. Frecuentemente el primer ataque en un dominio.
3. [[kerberoasting]] — el ataque *post-foothold*. Requiere cualquier credencial de dominio; apunta a cuentas con SPNs. Frecuentemente produce una service account con camino hacia DCSync.
4. [[dcsync-and-ntdsdit-extraction]] — el endgame. Recupera cada hash del dominio incluyendo `krbtgt`. Habilita Golden Tickets y compromiso de dominio persistente total.
5. [[pass-the-hash-and-ntlm-credential-reuse]] — lo que hacés con los hashes NTLM masivos que produce DCSync. Cierra el loop de extracción → reuso de credenciales y explica por qué la deshabilitación de NTLM es la dirección a largo plazo.
   - Sibling: [[windows-privilege-escalation]] — la primitiva local que produce el acceso a LSASS donde se originan las credenciales de Pass-the-Hash. Leela cuando la cadena llega a un host Windows que necesita elevación antes de continuar los ataques AD.
6. [[golden-ticket-and-krbtgt-compromise]] — el abuso de la raíz de confianza después de comprometer el material de `krbtgt`. Leela después de PtH para que la distinción dominio-wide vs host-específico sea concreta.
7. [[silver-ticket-and-service-account-persistence]] — falsificación de TGS con scope de servicio a partir de material de clave de service account. Leela después de Golden Ticket para mantener nítida la distinción entre alcance de dominio y de servicio.
8. [[gmsa-and-modern-service-account-hardening]] — el patrón defensivo de diseño de service accounts. Leela después de Silver Ticket para que las decisiones de hardening se mapeen a rutas de abuso concretas.
9. [[tier-zero-administration-and-paw]] — la defensa **estructural** que hace imposible toda la cadena anterior. Cada nota ofensiva anterior la referencia como "la respuesta"; leerla acá fundamenta las referencias.
10. [[krbtgt-rotation-and-tier-zero-recovery]] — la operación de recuperación de Tier 0 después de un posible compromiso de `krbtgt`. Leela al final porque el procedimiento solo tiene sentido después de que el modelo de abuso de la raíz de confianza está claro.

Leé en este orden: la primera nota te enseña a *ver* el grafo; las siguientes dos enseñan las formas más comunes de atravesar aristas; la cuarta llega al endgame de extracción de credenciales; la quinta explica qué permite el material masivo de hashes NTLM; la sexta explica por qué el compromiso de `krbtgt` no es "otra contraseña" sino compromiso de la raíz de autenticación del dominio; la séptima muestra cómo el compromiso de clave de service account crea persistencia más estrecha pero frecuentemente más silenciosa; la octava convierte ese modelo ofensivo en ingeniería de service accounts; la novena da la defensa estructural; la décima cierra el loop con la restauración de confianza.

### Notas futuras sugeridas

- dcshadow-and-rogue-dc-attacks — el sibling sigiloso de DCSync.
- exchange-ad-permission-legacy-issues — la fuente recurrente de derechos de replicación mal configurados.
- username-enumeration-against-kerberos — el paso previo al AS-REP Roasting.
- kerberos-preauth-and-encryption-types — por qué `DONT_REQ_PREAUTH` es estructuralmente peligroso.
- useraccountcontrol-flags-as-attack-surface — cada bit peligroso en `userAccountControl`.
- shadow-credentials-and-kerberos-pkinit — ruta de persistencia moderna basada en AD-CS.
- [[detect-bloodhound-collection]] — playbook del lado defensor para capturar la fase de enumeración.
- [[detect-dcsync-and-ntdsdit-access]] — playbook del lado defensor para el ataque final.

---

## Cross-links a otras ramas

- [[index|Offensive Security / Recon]] — los ataques AD usan la misma mentalidad de operador que la rama de seguridad ofensiva; las notas específicas de AD originalmente estaban allí y fueron promovidas acá una vez que el cluster alcanzó masa crítica.
- [[password-hashing|Password hashing]] — la economía fundamental de todos los ataques de credenciales AD.
- [[symmetric-encryption-modes|Symmetric encryption modes]] — RC4 vs AES en el contexto de Kerberos.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — el framing correcto para la telemetría de ataques AD.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — la contraparte defensiva del pensamiento de grafo de BloodHound.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — esta rama es el ejemplo concreto más limpio del concepto de dualidad.

---

## Notas de mantenimiento de la rama

- Cada nota en esta rama sigue la plantilla de nota atómica de 11 secciones.
- Los ataques AD *no* tienen detección útil basada en firmas. El framing de detección predeterminado aquí es siempre de comportamiento. Evitá redactar contenido del tipo "detectar por IoC X"; enrutá la narrativa de detección a través de pares Event-ID + comportamiento.
- La rama fue promovida desde `cybersecurity/offensive-security/` una vez que alcanzó 4 notas maduras (Kerberoasting + AS-REP Roasting + BloodHound + DCSync) el 2026-05-10. Las nuevas notas específicas de AD deben ir directamente aquí.
- Expansión futura: una rama sibling `cybersecurity/entra-id-and-cloud-identity/` puede eventualmente separarse una vez que el contenido de Entra ID / AAD alcance masa similar.
