---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Windows Event Logs

## Definition

Windows Event Logs are the structured host-side telemetry that the Windows operating system emits for security-relevant operations (authentication, authorization, process execution, account changes, object access, system state). Logs are stored as `.evtx` files in `%SystemRoot%\System32\winevt\Logs\`, exposed via the Event Log service, and queryable through `wevtutil`, `Get-WinEvent`, the Event Viewer UI, or a forwarded copy in a SIEM. **The body of useful security telemetry on Windows is built almost entirely from a small set of Event IDs** — roughly 30 out of the thousands defined — and senior detection engineers internalize that subset rather than treating Windows logs as an undifferentiated stream.

## Why it matters

Every Windows-targeted attack in this atlas — [[kerberoasting|Kerberoasting]] (4769 + RC4), [[as-rep-roasting|AS-REP Roasting]] (4768 + PreAuthType=0), [[dcsync-and-ntdsdit-extraction|DCSync]] (4662 + replication GUIDs), [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] (4624 LogonType=3 + NTLM), [[bloodhound-attack-path-analysis|BloodHound]] collection (LDAP query patterns + 4662), [[golden-ticket-and-krbtgt-compromise|Golden Ticket]] use (4769 without preceding 4768 from the same user) — produces a recognizable signature in Windows Event Logs. Without a working model of what those Event IDs mean, what fields they carry, and what audit policy makes them appear, detection rules and IR investigations are guesswork.

The senior framing is that Event Logs are **not what gets logged by default**; they are what gets logged *after the audit policy is configured correctly*. Default Windows audit policy is silent about Process Creation (4688), silent about Sensitive Privilege Use (4673), silent about Detailed File Share access — yet these are the events most detection rules need. Configuring audit policy is the prerequisite to every other detection-engineering claim about Windows hosts.

The technique also matters as a teaching note because it surfaces three transferable senior facts:

- **Event IDs are the alphabet, not the language.** Real detections are *sequences and conjunctions* of Event IDs ([[behavioral-detection-vs-signature-detection|behavioral detection]]) — e.g., "4624 + LogonType=3 + AuthenticationPackage=NTLM + unusual source" — not single-Event-ID alerts.
- **The default field set is incomplete on purpose.** Microsoft ships safe defaults to control log volume on shared infrastructure. Production detection requires opt-in: process command line (`Include command line in process creation events` policy), PowerShell ScriptBlockLogging, DNS client logging, Sysmon for the next layer.
- **Log clearing is itself a high-fidelity signal.** Event 1102 ("audit log was cleared") and 104 ("System log was cleared") are emitted *before* the clearing takes effect — and they're emitted to the same log that's being cleared. Attackers know this; mature defenders forward logs in real time so the clearing event survives.

## How it works

Windows Event Logs are organized into **4 layers** that a detection engineer must hold simultaneously:

1. **The log channels.** The three classic logs — `Security`, `System`, `Application` — plus the modern operational logs under `Microsoft-Windows-*/Operational` (PowerShell, Sysmon, Windows Defender, AppLocker, DNS-Client, etc.). The classic logs follow Windows since NT; the operational logs are where most modern security telemetry lives.
2. **The audit policy.** Configured via `Local Security Policy → Advanced Audit Policy Configuration` or domain GPO. **No event is logged unless the corresponding audit subcategory is enabled.** Audit Process Creation (Success) generates 4688; without it, 4688 events never appear. The audit policy is the gate, not the log.
3. **The Event ID + field set.** Each Event ID has a fixed schema: 4624 carries fields for User, LogonType, AuthenticationPackage, Source Network Address, Workstation Name, Logon ID, and ~15 others. Detection rules pattern-match on these fields, not on the raw event text. Knowing field positions matters because some SIEMs index by field name (Splunk, Sentinel) and some index by ordinal position (older agents).
4. **The forwarding/storage layer.** Windows Event Forwarding (WEF) collects logs centrally, often via the WinRM-based subscription model. Modern deployments push to a SIEM via an agent (Sysmon → Splunk Universal Forwarder, Sentinel Azure Monitor Agent, Elastic Agent). The forwarder is also where filtering and rate-limiting happen; detection rules must account for what survives the forwarder.

A representative end-to-end query against the Security log:

```
# Find every NTLM network logon in the last 24 hours.
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    ID=4624
    StartTime=(Get-Date).AddHours(-24)
} | Where-Object {
    $_.Properties[8].Value -eq 3 -and       # LogonType 3 (Network)
    $_.Properties[10].Value -eq 'NTLM'      # AuthenticationPackage
} | Select-Object TimeCreated,
    @{n='User';e={$_.Properties[5].Value}},
    @{n='Source';e={$_.Properties[18].Value}},
    @{n='Target';e={$_.Properties[6].Value}}
```

The bug is not "Windows logs are too verbose" or "Windows logs are too sparse"; it is *Windows logs are configured-not-default, schema-driven, and field-positional — and detection engineering requires holding the audit policy, the Event ID semantics, the field schema, and the forwarding pipeline as four interacting layers simultaneously*.

## Techniques / patterns

### The Event IDs that matter (the senior subset)

| Category | Event ID | What it means | Telemetry signal |
| --- | --- | --- | --- |
| **Logon / logoff** | 4624 | Successful logon | LogonType + AuthenticationPackage + Source IP — the foundational event |
|  | 4625 | Failed logon | Failure reason — brute-force, locked-out, expired-pwd, bad-user |
|  | 4634 | Logoff | End of a session |
|  | 4647 | User-initiated logoff | Distinguishes voluntary from system-induced |
|  | 4648 | Logon with explicit credentials | `runas /netonly` and similar — credential delegation |
|  | 4672 | Special privileges assigned to a new logon | Indicates Administrator-equivalent rights on this session |
| **Kerberos** | 4768 | TGT (Authentication Service) request | Pre-Auth Type field — `PreAuthType=0` = AS-REP roasting indicator |
|  | 4769 | TGS (Service Ticket) request | TicketEncryptionType field — `0x17` (RC4) against AES baseline = Kerberoasting indicator |
|  | 4770 | TGT renewed | Long-lived TGT renewals can indicate Golden Ticket if `krbtgt` was rotated |
|  | 4771 | Kerberos pre-auth failed | Failure-code differentiates "wrong password" from "account locked" — bruteforce telemetry |
| **Process / command** | 4688 | Process created | Command line (only if explicitly enabled in audit policy) + parent process — the bedrock of host-side behavioral detection |
|  | 4689 | Process exited | Pair with 4688 for process duration |
| **Privilege use** | 4672 | Special privileges assigned at logon | (see Logon) |
|  | 4673 | Sensitive privilege used | High-volume in default config — usually filtered |
|  | 4674 | Operation attempted on a privileged object | Tied to SeDebugPrivilege use, often relevant for credential dumping detection |
| **Account management** | 4720 | User account created | New principal — alert always |
|  | 4722 | User account enabled | Re-enable can be persistence |
|  | 4724 | Password reset attempt | Privilege escalation indicator |
|  | 4725 | User account disabled | Operational telemetry |
|  | 4726 | User account deleted | Anti-forensic indicator |
|  | 4738 | User account changed | Catch-all for property modification |
| **Group management** | 4728 | Member added to security-enabled global group | Watch Tier 0 groups especially |
|  | 4732 | Member added to security-enabled local group | Local admin escalation |
|  | 4756 | Member added to security-enabled universal group | Enterprise Admins, Schema Admins lives here |
| **Object access** | 4662 | An operation was performed on an object | The DCSync detector — filter for replication GUIDs `1131f6aa-*` and `1131f6ad-*` |
|  | 4663 | An attempt was made to access an object | File / registry / kernel object access |
|  | 4670 | Permissions on an object were changed | AdminSDHolder modification trail |
| **System / integrity** | 1100 | Event log service shutting down | Pre-clear or pre-shutdown indicator |
|  | 1102 | Audit log was cleared | High-fidelity adversary indicator — never legitimate in production |
|  | 104 | System log was cleared | Companion to 1102 |
| **PowerShell** | 4103 | Module logging | Function-level PowerShell execution detail |
|  | 4104 | ScriptBlock logging | The de-obfuscated script content — the most valuable PowerShell telemetry |
|  | 4105 / 4106 | ScriptBlock start / stop | Lifecycle bracketing |

### Patterns

- **Always enable Audit Process Creation with command line.** GPO: `Computer Configuration → Administrative Templates → System → Audit Process Creation → Include command line in process creation events = Enabled`. Without it, 4688 is half-blind.
- **Enable PowerShell ScriptBlock Logging.** `Turn on PowerShell Script Block Logging` GPO. Captures the de-obfuscated script content in Event 4104, including dynamically-built strings. The single highest-value PowerShell detection telemetry.
- **Forward in real time, do not pull on a schedule.** WEF subscriptions with `Minimize Latency` (push events as they occur) make log-clearing futile — the events are already at the collector before the attacker can clear the source.
- **Pair 4624 LogonType with AuthenticationPackage and source IP.** A single `4624 + LogonType=3 + AuthenticationPackage=NTLM` is a textbook Pass-the-Hash signal in environments that should use Kerberos. See [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] §Detection.
- **Watch encryption-type drift in 4769.** Service accounts have a baseline encryption type (almost always AES256 = `0x12` or AES128 = `0x11` in modern AD). A 4769 with `TicketEncryptionType=0x17` (RC4-HMAC) for an AES-baseline account is the Kerberoasting signature.
- **`PreAuthType=0` on Event 4768 is a single-event high-confidence detection.** In any environment without legacy MIT/Heimdal integration, no account should ever have `DONT_REQ_PREAUTH` set. Every 4768 with `PreAuthType=0` is an AS-REP roasting attempt by definition.
- **Cross-join 4662 with the replication-rights GUIDs.** `MATCH AccessMask containing 1131f6aa-9c07-11d1-f79f-00c04fc2dcd2 OR 1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`. Only DCs should generate these from their own computer accounts. Any other source = DCSync.

### What Sysmon adds on top

Built-in Windows logging captures what the OS observes about itself. **Sysmon** ([[edr-network-observability-and-process-correlation|EDR / process correlation]]) is a Microsoft Sysinternals driver that captures what's adjacent: network connections per process, file creates, registry modifications, image loads, named pipe activity, raw access reads. The pair `4688 + Sysmon Event 1` (process creation, both from Microsoft sources) provides the canonical Windows process-creation telemetry that almost every detection rule depends on.

## Variants and bypasses

Windows logging splits into **4 telemetry-source variants** with different defender tradeoffs.

### 1. Built-in Windows audit (default OS logs)

The Security/System/Application logs with audit policy enabled. Zero extra software. Limited field set per Event ID. Adequate for foundational detections (logons, account changes, Kerberos events); inadequate for command-line process telemetry by default until the command-line policy is enabled.

### 2. Sysmon

Microsoft Sysinternals. Free, kernel-driver-based, configurable via XML rule files (the SwiftOnSecurity / Olaf Hartong configurations are community standards). Adds process-network joins, file creation telemetry, image loads. The de-facto next layer above default audit on any defender stack worth running.

### 3. EDR-vendor telemetry

CrowdStrike, Microsoft Defender for Endpoint, SentinelOne, etc. Captures everything Sysmon does plus memory access, child-process telemetry, behavioral analytics, and (importantly) ships the data to a cloud backend the attacker cannot turn off from the host. Where Windows logging is auditable-but-tamperable, EDR is opinionated-but-tamper-resistant.

### 4. Auditd-style on Windows (rare)

Some organizations use ETW (Event Tracing for Windows) sessions directly with custom consumers — a Windows analog of Linux auditd. Highest fidelity, lowest abstraction, highest operational cost. Generally only seen in security-research and CIRT-team environments.

## Impact

Ordered by typical real-world severity (of *defensive misuse* — the technique is defensive):

- **Detection blindness from default audit policy.** Organizations that rely on "we have Windows logs" without verifying the audit subcategories are enabled. The most common defender failure mode for Windows.
- **Process telemetry without command lines.** 4688 events that say "a process was created" without identifying *what command line* was executed. Halts most malware-detection use cases.
- **No PowerShell ScriptBlock logging.** Attackers obfuscate; the Event 4104 ScriptBlock log captures the post-obfuscation script — without it, every PowerShell-based attack is half-invisible.
- **Local-only retention.** Logs that live only on the host get cleared by attackers (Event 1102) and are no longer available for forensics. WEF or equivalent forwarding is non-negotiable for any environment that needs forensic evidence.
- **Volume vs retention tradeoffs.** Enabling everything makes logs unmanageable; enabling too little makes detection impossible. The audit-policy tuning curve is real engineering work, not a one-time configuration.

## Detection and defense

This note *is* a defense — it does not have a target-side defender section in the usual sense. The relevant framing is **what to monitor in Windows Event Logs** for the canonical AD and credential attacks elsewhere in the atlas.

Ordered by detection value across the atlas's existing attack notes:

1.
**Configure the audit policy first.**
   `auditpol /set /subcategory:` for Logon, Logoff, Process Creation, Kerberos Authentication Service, Kerberos Service Ticket Operations, Account Management, Directory Service Access, Security State Change. Enable "Include command line in process creation events" GPO. Enable PowerShell Module + ScriptBlock + Transcription logging. Without this, every later step is moot.

2.
**Forward to a SIEM in real time.**
   Windows Event Forwarding with WinRM subscriptions, or an EDR/SIEM agent. Local-only logs are forensically unreliable; forwarded logs survive Event 1102. Tag the forwarder pipeline so detection rules know what was filtered out at the source.

3.
**Build behavioral detection rules from Event-ID sequences, not single events.**
   Detection patterns:
   - [[kerberoasting|Kerberoasting]]: high volume of 4769 with `TicketEncryptionType=0x17` from one source in 60s.
   - [[as-rep-roasting|AS-REP Roasting]]: 4768 with `PreAuthType=0` against any non-allowlisted account.
   - [[dcsync-and-ntdsdit-extraction|DCSync]]: 4662 with replication GUIDs from a non-DC computer account.
   - [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]]: 4624 LogonType=3 + AuthenticationPackage=NTLM in an AES-only / Kerberos-only environment.
   - Log clearing: 1102 or 104 — high-severity alert, near-zero legitimate cause.
   - Tier 0 group changes: 4728 / 4732 / 4756 where the group is in the Tier 0 set ([[tier-zero-administration-and-paw|Tier 0 Administration]]).
4.
**Pair with Sysmon for process telemetry.**
   The community-standard SwiftOnSecurity Sysmon config is a solid starting point. Sysmon Event 1 (process creation with hashes, parent process, command line) plus 3 (network connection), 7 (image load), 11 (file create), 13 (registry value set) cover the bulk of host-side behavioral detection.

5.
**Audit and tune quarterly.**
   Log-volume and false-positive baselines drift. Quarterly review of the alert pipeline keeps the signal-to-noise ratio high.

### What does not work as a primary defense

- **Enabling every audit subcategory.** Produces unmanageable volume and degrades the SIEM. Tune for the events you actually detect on; everything else is noise.
- **Local-only retention.** Attackers clear logs; forensic timelines die.
- **Detecting on raw event text.** Event-text strings change across Windows versions and language packs. Detection rules must be field-based, not regex-on-Message.
- **Trusting "no log = nothing happened".** The most common failure mode. Verify the audit policy and the forwarder *separately* — both must be working.

## Practical labs

```
# Lab 1 — Audit your current audit policy.
auditpol /get /category:*
# Look for "Success and Failure" on critical subcategories:
#   Logon, Logoff, Account Lockout, Process Creation, Kerberos Authentication Service,
#   Kerberos Service Ticket Operations, Audit Policy Change, Security State Change.
```

```
# Lab 2 — Enable Process Creation with command-line logging (test in a lab).
auditpol /set /subcategory:"Process Creation" /success:enable /failure:enable
# Then enable command-line capture via Registry (or GPO):
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System\Audit" `
    /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f
# Generate a test event:
cmd /c "whoami"
# Verify 4688 events now carry command-line data:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4688} -MaxEvents 5 |
    Select-Object TimeCreated, @{n='CmdLine';e={$_.Properties[8].Value}}
```

```
# Lab 3 — Query Kerberos events for Kerberoasting signature.
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    ID=4769
    StartTime=(Get-Date).AddHours(-24)
} | Where-Object {
    $_.Properties[6].Value -eq '0x17'   # TicketEncryptionType = RC4-HMAC
} | Select-Object TimeCreated,
    @{n='Target';e={$_.Properties[0].Value}},
    @{n='Service';e={$_.Properties[2].Value}},
    @{n='Source';e={$_.Properties[6].Value}},
    @{n='EncType';e={$_.Properties[5].Value}}
# Every result is a candidate Kerberoasting event.
```

```
# Lab 4 — Detect AS-REP Roasting signature.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 200 |
    Where-Object { $_.Properties[10].Value -eq '0' } |   # PreAuthType = 0
    Select-Object TimeCreated,
        @{n='Target';e={$_.Properties[0].Value}},
        @{n='Source';e={$_.Properties[9].Value}}
# Any non-allowlisted result is an AS-REP roasting attempt.
```

```
# Lab 5 — Detect DCSync signature (Event 4662 + replication GUIDs).
$dcsyncGuids = @(
    '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2',  # DS-Replication-Get-Changes
    '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'   # DS-Replication-Get-Changes-All
)
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 500 |
    Where-Object {
        $msg = $_.Message
        $dcsyncGuids | ForEach-Object { if ($msg -match $_) { return $true } }
    } |
    Select-Object TimeCreated, @{n='Subject';e={$_.Properties[3].Value}}
# Only Domain Controllers should appear. Any other source is a DCSync alert.
```

```
# Lab 6 — Enable PowerShell ScriptBlock logging and verify capture.
# GPO (or registry):
reg add "HKLM\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
    /v EnableScriptBlockLogging /t REG_DWORD /d 1 /f
# Generate a test obfuscated script:
powershell -enc cwBlAHQALQBsAG8AYwBhAHQAaQBvAG4AIABDADoAXAA=
# Inspect the resulting 4104 event:
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 10 |
    Where-Object { $_.Id -eq 4104 } |
    Select-Object TimeCreated, @{n='Script';e={$_.Properties[2].Value}}
# Expected: the de-obfuscated `set-location C:\` content in the Script field.
```

## Practical examples

- **SOC catches Kerberoasting in 90 seconds.** Detection rule on 4769 + `TicketEncryptionType=0x17` against an AES-baseline environment fires on the operator's first roasting attempt. Source IP traced to a workstation that should not be issuing Kerberos service-ticket requests at that scale. Account disabled within five minutes.
- **DCSync caught by Event 4662.** Detection rule on 4662 + replication GUIDs from non-DC subjects fires on the operator's first `secretsdump.py -just-dc-user krbtgt`. The single event is high-confidence; SOC pivots to the source IP, finds the operator's beachhead, ends the engagement.
- **PowerShell obfuscation defeated by ScriptBlockLogging.** Operator runs a 14-layer-encoded PowerShell payload. Event 4104 captures the final-stage de-obfuscated script. Detection rule matches on the inner content; the outer encoding was irrelevant.
- **Audit-policy gap discovered post-incident.** IR investigation finds attacker activity from three weeks ago. Process Creation auditing was never enabled on the affected hosts; the SIEM has no command-line telemetry. The intrusion is reconstructable only by inference. Audit-policy verification becomes a quarterly check after this.
- **Log-clearing alert catches anti-forensics.** Attacker, mid-engagement, runs `wevtutil cl Security`. The clearing operation generates Event 1102 *before* the log is purged — and the WEF subscription has already forwarded it to the SIEM. The clearing event itself is the high-fidelity finding.

## Related notes

- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — Event-ID *sequences* (behavior) beat Event-ID *thresholds* (rate) for Windows attack detection.
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — host-side log telemetry pairs with network telemetry for the full picture.
- [[edr-network-observability-and-process-correlation|EDR / process correlation]] — Sysmon and EDR sit on top of the Event-Log foundation.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — Event IDs are the atoms; chains are the molecules.
- [[false-positives-false-negatives-and-detection-tradeoffs|False Positives and Negatives]] — the audit-volume / signal tradeoff curve applied here.
- [[kerberoasting|Kerberoasting]] — primary 4769-based detection consumer.
- [[as-rep-roasting|AS-REP Roasting]] — primary 4768-based detection consumer.
- [[dcsync-and-ntdsdit-extraction|DCSync]] — primary 4662-based detection consumer.
- [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] — primary 4624-LogonType-3-NTLM detection consumer.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting + AS-REP Roasting]] — operational playbook that orchestrates these Event-ID detections.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — Windows Event Logs are the canonical host-side defender telemetry; pair with every Windows offensive technique.

### Suggested future atomic notes

- sysmon-configuration-and-tuning — the SwiftOnSecurity / Olaf Hartong config patterns plus how to write custom Sysmon rules.
- powershell-logging-deep-dive — Module / ScriptBlock / Transcription logging tradeoffs and tuning.
- etw-event-tracing-for-windows — the layer below the Event Log API; basis for advanced EDR telemetry.
- windows-event-forwarding-architecture — WEF subscriptions, collector design, scaling considerations.
- ad-logging-versus-application-logging-tradeoffs — domain-controller-only logs vs member-server logs vs workstation logs.
- detect-windows-log-clearing — playbook for the 1102 / 104 detection pattern.

## References

- **Foundational:** Microsoft Learn — Advanced security audit policy settings — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/advanced-security-audit-policy-settings
- **Foundational:** Microsoft Learn — Events to Monitor — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/appendix-l-events-to-monitor
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Windows Security Event Log Categories — https://adsecurity.org/?p=3299
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
