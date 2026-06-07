# Reference Registry — Identity and Active Directory

## Propósito

Esta nota estandariza las referencias para la rama identity-and-active-directory.

Usala para:
- mantener notas AD/Kerberos vinculadas a fuentes primarias canónicas
- evitar posts viejos o de baja señal cuando MITRE / Microsoft / SpecterOps cubren el mismo tema
- mantener esta rama centrada en AD, Kerberos y análisis graph-based de attack paths, dejando espacio para contenido Entra ID / hybrid identity más adelante

## Regla de fuente de verdad

Para notas de identity-and-active-directory, este registry es la fuente de verdad primaria.

Usalo junto con:
- `<a href="identity-and-active-directory/index.html">Identity and Active Directory Index</a>`
- `<a href="reference-registry-offensive-security.html">Reference Registry — Offensive Security</a>` cuando las notas AD entren en territorio recon / enumeration
- `<a href="reference-registry-detection-engineering.html">Reference Registry — Detection Engineering</a>` cuando las notas AD entren en telemetría / contenido de detección behavioral

---

## Política de selección de referencias

### Prioridad de fuentes

1. taxonomías **Fundamentales** (MITRE ATT&CK, documentación Microsoft)
2. fuentes primarias de **Investigación / Deep Dive** (posts y charlas canónicas de SpecterOps / harmj0y / Sean Metcalf)
3. **Tool docs** (BloodHound CE, Impacket, Mimikatz)
4. fuentes **Secundarias** solo cuando agregan valor claro (raro en esta rama; sobran fuentes primarias)

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias

### Etiquetas

Usar:
- **Fundamental**
- **Investigación / Deep Dive**
- **Docs oficiales de herramienta**

---

# Mapa de temas Identity / AD

## kerberoasting

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Cracking Kerberos TGS Tickets — https://adsecurity.org/?p=2293
- **Investigación / Deep Dive:** Tim Medin — Attacking Microsoft Kerberos (DerbyCon 2014, original talk) — https://www.youtube.com/watch?v=PUyhlN-E5MU

## as-rep-roasting

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Investigación / Deep Dive:** Will Schroeder (harmj0y) — Roasting AS-REPs — https://blog.harmj0y.net/activedirectory/roasting-as-reps/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458

## bloodhound-attack-path-analysis

Referencias preferidas:
- **Docs oficiales de herramienta:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Investigación / Deep Dive:** Robbins, Schroeder, Vazarkar — An ACE Up The Sleeve (Black Hat USA 2017) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Investigación / Deep Dive:** Robbins & Schroeder — Six Degrees of Domain Admin (DEF CON 24) — https://www.youtube.com/watch?v=lxd2rerVsLo

## dcsync-and-ntdsdit-extraction

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Fundamental:** Microsoft — AD DS replication permissions documentation — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864

## golden-ticket-and-krbtgt-compromise

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Detección:** MITRE ATT&CK DET0144 — Detect Forged Kerberos Golden Tickets — https://attack.mitre.org/detectionstrategies/DET0144/
- **Recovery:** Microsoft Learn — AD Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz Golden Ticket Usage, Exploitation, and Detection — https://adsecurity.org/?p=1515

## silver-ticket-and-service-account-persistence

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1558.002 — Silver Ticket — https://attack.mitre.org/techniques/T1558/002/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — How Attackers Use Kerberos Silver Tickets to Exploit Systems — https://adsecurity.org/?p=2011
- **Fundamental:** Microsoft Learn — Kerberos authentication overview — https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview

## gmsa-and-modern-service-account-hardening

Referencias preferidas:
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
- **Hardening:** Microsoft Learn — Get started with group Managed Service Accounts — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/getting-started-with-group-managed-service-accounts
- **Fundamental:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Active Directory Security Tip #14: Group Managed Service Accounts (GMSAs) — https://adsecurity.org/?p=4904

## krbtgt-rotation-and-tier-zero-recovery

Referencias preferidas:
- **Recovery:** Microsoft Learn — AD Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Recovery:** Microsoft Learn — AD Forest Recovery Guide — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide
- **Fundamental:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts now available for customers — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/

## pass-the-hash-and-ntlm-credential-reuse

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1550.002 — Use Alternate Authentication Material: Pass the Hash — https://attack.mitre.org/techniques/T1550/002/
- **Hardening:** Microsoft — Mitigating Pass-the-Hash and Other Credential Theft, version 2 — https://www.microsoft.com/en-us/download/details.aspx?id=54095
- **Hardening:** Microsoft Learn — Credential Guard overview — https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/

## tier-zero-administration-and-paw

Referencias preferidas:
- **Hardening:** Microsoft Learn — Enterprise Access Model — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
- **Hardening:** Microsoft Learn — Privileged Access Workstations deployment — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-deployment
- **Hardening:** Microsoft Learn — Protected Users security group — https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers to Improve Active Directory Security — https://adsecurity.org/?p=3299

## windows-privilege-escalation

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK TA0004 — Privilege Escalation tactic — https://attack.mitre.org/tactics/TA0004/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — LAPS and Windows privilege escalation patterns — https://adsecurity.org/?p=4063
- **Docs oficiales de herramienta:** Microsoft Sysinternals Suite (accesschk, autoruns, procmon, sysmon) — https://learn.microsoft.com/en-us/sysinternals/
- **Hardening:** Microsoft Learn — Securing privileged access in Windows — https://learn.microsoft.com/en-us/security/privileged-access-workstations/overview

---

## Reglas de uso del registry

- elegí el set más chico de referencias fuertes para la nota exacta
- preferí una referencia ATT&CK + un post canónico SpecterOps/Metcalf por nota cuando sea posible
- mantené las referencias centradas en ataques AD, defensas y telemetría de detección; ruteá detalles crypto de protocolo Kerberos / NTLM por el registry de cryptography
