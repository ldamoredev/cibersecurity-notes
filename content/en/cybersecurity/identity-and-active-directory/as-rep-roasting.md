---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# AS-REP Roasting

## Definition

AS-REP Roasting is an Active Directory credential attack where an attacker exploits accounts with **Kerberos pre-authentication disabled** by sending an `AS-REQ` *without* a pre-auth blob and receiving an `AS-REP` whose encrypted portion can be cracked offline to recover the target user's password. Unlike [[kerberoasting|Kerberoasting]], **AS-REP Roasting requires no authenticated domain credential** — only knowledge of usernames.

## Why it matters

Kerberoasting needs a valid domain user to start. AS-REP Roasting does not. That single difference makes AS-REP Roasting the canonical *pre-foothold* AD attack: if an attacker can enumerate usernames (from LinkedIn, leaked credential dumps, anonymous LDAP, OWA email format, public Git commits) and any of those accounts has pre-auth disabled, the attack proceeds without ever logging in.

The technique matters as a teaching note because it surfaces three things newcomers usually miss:

- **Kerberos pre-authentication is a security control, not a protocol formality.** Disabling it sounds like "small configuration choice" and is in fact "give me your password hash, no questions asked".
- **`userAccountControl` flags are an attack surface.** The `DONT_REQ_PREAUTH` flag (`UF_DONT_REQUIRE_PREAUTH`, value `0x400000`) is checkable from any authenticated LDAP query and, when present, defines the target list.
- **Pre-auth-disabled accounts almost always exist in old environments.** Originally added for MIT/Heimdal Kerberos integration, legacy UNIX systems, and pre-Win2003 apps. The flag persists across decades because nobody audits `userAccountControl` regularly.

## How it works

AS-REP Roasting reduces to **5 protocol steps**:

1. **Enumerate usernames.** From LinkedIn / OWA email format / leaked breaches / public Git commits / kerbrute brute-force. No authenticated context needed — username enumeration against Kerberos via timing differentials on `KRB-ERROR` responses works pre-auth.
2. **Send `AS-REQ` without pre-authentication.** Normal Kerberos clients include `PA-ENC-TIMESTAMP` (an encrypted timestamp proving you know the password) inside the `AS-REQ`. The attacker omits it.
3. **Receive the KDC's response.**
   - If the target account requires pre-auth (the default): KDC returns `KRB5KDC_ERR_PREAUTH_REQUIRED`. Not vulnerable. Move on.
   - If the target account has `DONT_REQ_PREAUTH` set: KDC returns an `AS-REP` whose `EncPart` is encrypted with the *target user's* password-derived long-term key.
4. **Extract the encrypted blob.** Tools like `GetNPUsers.py` (Impacket) and `Rubeus.exe asreproast` automate this and emit a hashcat-compatible string in the form `$krb5asrep$23$user@DOMAIN:hex:hex`.
5. **Crack offline.** Hashcat mode `18200` for RC4-HMAC AS-REP, or `33100` for AES variants. Same offline-cracking economics as Kerberoasting: weak password + RC4 = minutes, strong password + AES-256 = years.

A representative end-to-end sequence:

```
# From any host, no domain credential required.
impacket-GetNPUsers DOMAIN.LOCAL/ -dc-ip 10.0.0.1 \
    -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hash
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```

The bug is not "Kerberos is broken"; it is *an account flag turned off the cryptographic proof-of-password gate, so the KDC happily emits a crackable hash of the user's password to any caller who asks for it*.

## Techniques / patterns

- **Username enumeration is the prerequisite.** Without a username list there is nothing to roast. Build the list from: `kerbrute userenum`, `MSF auxiliary/gather/kerberos_enumusers`, OSINT (LinkedIn → first.last@corp.com), public breach corpora, anonymous SMB/RPC enumeration if open.
- **If you have *any* domain credential, dump the target list via LDAP.** With even one valid user, query AD for `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` — the bitmask filter for the `DONT_REQ_PREAUTH` flag. Returns every vulnerable account in one query.
- **Pick RC4 over AES whenever the KDC offers it.** Same trick as Kerberoasting — `GetNPUsers.py` defaults to `-format hashcat` which produces an RC4-HMAC hash when the account supports it. RC4 + weak password = orders of magnitude faster offline crack.
- **Cross-check against breach corpora.** Once you have a target list of pre-auth-disabled accounts, run their usernames against haveibeenpwned-style corpora *before* cracking. Many service accounts and forgotten legacy users reuse known-leaked passwords.
- **OPSEC: ask once, not many times.** Bulk-querying every account in the domain leaves a clear telemetry trail (many AS-REQ from one source, all without pre-auth). Senior usage queries only the pre-identified vulnerable accounts.

## Variants and bypasses

AS-REP Roasting has **3 variants** worth distinguishing.

### 1. Classic AS-REP Roasting (no creds)

The flow described above. The attacker has zero domain authentication. Requires usernames + at least one account with `DONT_REQ_PREAUTH`. The variant that makes this attack uniquely dangerous compared to Kerberoasting.

### 2. Credentialed AS-REP Roasting

The attacker already has any valid domain credential. Uses authenticated LDAP to enumerate the exact set of pre-auth-disabled accounts (no guessing, no kerbrute), then runs the protocol against just those. Quieter, more reliable, and lets you skip the username-enumeration noise.

### 3. Targeted (single-user) AS-REP Roasting

Pre-identified single high-value target (e.g., a known legacy admin account from leaked org chart). Single `AS-REQ` produces single `AS-REP`. Minimal telemetry; lowest detection signal. The variant for engagement-style operators where stealth matters.

## Impact

Ordered by typical real-world severity:

- **Foothold from zero authentication.** The defining property. A single pre-auth-disabled account turns a "we know the company name and a few emails" position into "we have a crackable password hash". This is rare for any other AD attack.
- **Privilege escalation if the disabled-pre-auth account is privileged.** Pre-auth was historically disabled on UNIX-integration service accounts and on some admin accounts. Cracking yields direct privileged access.
- **Persistence and pivot.** Recovered password works for SMB, WinRM, RDP, MSSQL — any service that trusts AD identity. Lateral movement follows immediately.
- **Domain context for further attacks.** Even an unprivileged crack establishes a real domain credential, unlocking the full Kerberoasting / BloodHound / SMB enumeration toolkit.
- **Forgotten accounts persist for years.** The most common real-world finding: a 2009-era account with pre-auth disabled because of a UNIX integration that was decommissioned in 2013 and never re-secured.

## Detection and defense

Ordered by effectiveness:

1.
**Audit and remove `DONT_REQ_PREAUTH` from every account.**
   The hard fix. Query AD with `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` and either re-enable pre-auth or disable the account. Schedule the audit; this is the only durable defense because once the flag is cleared, the attack is structurally impossible.

2.
**Enforce strong, long, random passwords on any account that must keep pre-auth disabled.**
   If a legacy integration genuinely requires it, raise the password length and entropy until offline cracking is impractical (25+ random characters). Pair with AES-only encryption types so the cracking economics shift further toward the defender.

3.
**Behavioral detection on Event ID 4768.**
   Windows generates Event 4768 (Kerberos Authentication Ticket Request) on every `AS-REQ`. The detection signal: events with `Pre-Authentication Type: 0` (PA-ENC-TIMESTAMP not present). On a domain where no account should have pre-auth disabled, *any* such event is a high-confidence alert. On a domain with one or two legitimate exceptions, baseline those and alert on everything else.

4.
**Behavioral detection on AS-REQ source diversity.**
   A single source IP attempting AS-REQ against many usernames (especially in quick succession, or to non-existent usernames) is a textbook AS-REP-roasting signature regardless of pre-auth flags. Pair with [[behavioral-detection-vs-signature-detection|behavioral detection]] thinking from Phase 2.

5.
**Username enumeration mitigations.**
   Kerberos pre-auth itself leaks the existence of usernames via `KRB-ERROR` codes (different errors for "no such user" vs "wrong password"). Reduce this by setting the lockout-on-failed-auth policy and by treating user-not-found and bad-password the same in the response timing.

6.
**Honey accounts with `DONT_REQ_PREAUTH` set.**
   Plant a fake account with pre-auth disabled and a strong random password that nobody knows. Any `AS-REQ` against it is an AS-REP-roasting attempt by definition. Asymmetric defense — high-fidelity alert, near-zero false positive.

### What does not work as a primary defense

- **Blocking outbound Kerberos.** AS-REP Roasting is performed *against* the KDC by anyone who can reach it; the defender does not control the attacker's host. Network-level blocks only help on the perimeter.
- **Disabling RC4 alone.** If pre-auth is still disabled, AES-encrypted AS-REPs are still issued — just slower to crack. The root defense is the flag, not the algorithm.
- **Renaming pre-auth-disabled accounts.** Security by obscurity. LDAP queries return the canonical attribute regardless of display name.
- **Trusting "we don't have any pre-auth-disabled accounts" without verifying.** Always confirm with the LDAP bitmask query above; the manual GUI checkbox is unreliable at scale.

## Practical labs

Run only against owned lab environments or authorized engagements.

```
# Lab 1 — Create a pre-auth-disabled account in a lab AD.
New-ADUser -Name "legacy_user" -SamAccountName "legacy_user" `
    -AccountPassword (ConvertTo-SecureString "Spring2019!" -AsPlainText -Force) `
    -Enabled $true
Set-ADAccountControl -Identity legacy_user -DoesNotRequirePreAuth $true
# This account is now AS-REP-roastable from any unauthenticated host on the network.
```

```
# Lab 2 — Enumerate pre-auth-disabled accounts WITHOUT credentials.
# Username list (build from OSINT, kerbrute, leaks).
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
# Output contains $krb5asrep$23$* lines — one per vulnerable account.
```

```
# Lab 3 — Enumerate the vulnerable list via authenticated LDAP (if you have any cred).
impacket-GetNPUsers LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request
# This automatically queries LDAP for the flag bitmask and roasts every match.
```

```
# Lab 4 — Crack offline.
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
# Mode 18200 = AS-REP RC4-HMAC. Use 33100 for AES variants.
```

```
# Lab 5 — Audit your own AD for pre-auth-disabled accounts (defender side).
Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName, Enabled, DistinguishedName, LastLogonDate
# Every row is a candidate finding. Either re-enable pre-auth or harden the password.
```

```
# Lab 6 — Validate detection from the defender side.
# After running the roasting against an authorized lab, check the DC's Security log:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 50 |
    Where-Object { $_.Properties[10].Value -eq '0' }   # PreAuthType = 0
# Every result is an AS-REP-roasting attempt by definition.
# Build a SIEM detection rule from this filter.
```

## Practical examples

- **OSINT-only initial compromise.** Attacker gathers ten employee email addresses from LinkedIn. One of them (`legacy_user@corp.com`) is a 2011-era account whose owner left the company in 2014. AS-REP roast returns a crackable hash; the password is the user's first name plus their start year. Domain context established without ever interacting with the target as an authenticated user.
- **Post-merger forest enumeration.** Newly-merged subsidiary domain has a transitive trust. Attacker (authenticated in parent forest) queries the subsidiary's LDAP, finds 12 accounts with `DONT_REQ_PREAUTH`, roasts all 12, cracks two with rockyou.txt — pivot into the subsidiary domain follows.
- **UNIX-integration ghost account.** Account `unix_kdc_proxy` was created in 2008 to bridge an MIT Kerberos realm. The realm was decommissioned in 2012. The account remained, with pre-auth disabled and the original password (`Welcome123`). Recovered in seconds.
- **Service account hardening miss.** A defender claims "we have no pre-auth-disabled accounts". LDAP query returns 7. Three are legacy admins. One is in `Backup Operators`. The audit step took 90 seconds and immediately yields a major finding.
- **Honey-account catches red team.** Defender plants `svc_legacy_unix2` with pre-auth disabled and a 40-character random password. Six months later a red team performs unauthenticated AS-REP roasting from a beachhead; the only account that responds to their queries is the honey account, triggering a high-confidence alert that ends the engagement.

## Related notes

- [[kerberoasting]] — the sister attack; same offline-cracking economics, different protocol step, different precondition (needs a credential).
- [[silver-ticket-and-service-account-persistence]] — one downstream use of recovered service-account key material when a roasted account owns SPNs.
- [[password-hashing|Password hashing]] — the KDF strength is what determines crack cost on both AS-REP and TGS hashes.
- [[symmetric-encryption-modes|Symmetric encryption modes]] — RC4 vs AES in the Kerberos context.
- [[kdf-and-key-stretching|KDF and key stretching]] — offline cracking economics 101.
- [[cia-triad-and-what-it-actually-decides|CIA triad]] — AS-REP roasting is primarily an integrity + authenticity breach (impersonation enabled by recovered password).
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — pair this note with detection-side counterparts before claiming you understand it.
- [[behavioral-detection-vs-signature-detection|Behavioral vs signature detection]] — the only useful detection framing here.
- [[attack-path-correlation-and-kill-chain-observability|Attack path correlation]] — AS-REP roasting chained with later auth attempts produces high-confidence telemetry.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] — the defender-side playbook pair for this note.
- [[enumeration|Enumeration]] — username enumeration is the prerequisite step.
- [[passive-recon|Passive recon]] — where username lists come from.

### Suggested future atomic notes

- username-enumeration-against-kerberos — `kerbrute userenum`, `KRB-ERROR` timing differentials, lockout-policy implications.
- kerberos-preauth-and-encryption-types — the `PA-ENC-TIMESTAMP` mechanism, encryption-type negotiation, and why `DONT_REQ_PREAUTH` is structurally dangerous.
- useraccountcontrol-flags-as-attack-surface — every dangerous bit in `userAccountControl` (kerberos delegation, password-not-required, smartcard-required quirks, etc.).

## References

- **Foundational:** MITRE ATT&CK T1558.004 — Steal or Forge Kerberos Tickets: AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Research / Deep Dive:** Will Schroeder (harmj0y) — Roasting AS-REPs — https://blog.harmj0y.net/activedirectory/roasting-as-reps/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
