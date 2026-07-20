---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Linux Privilege Escalation

## Definition

Linux privilege escalation is the process of moving from a lower-privileged local account to a higher-privileged account or capability on the same Linux host.

In this branch, the safe learning scope is owned labs, CTF targets, and explicitly authorized hosts.

## Why it matters

Initial access rarely lands as root. Real impact depends on whether the local host allows a low-privileged user to read secrets, control services, abuse administrative delegation, or become root.

For defenders, Linux privesc is also a hardening map. Each escalation path points to a fixable boundary: sudo rules, file ownership, SUID bits, capabilities, service permissions, scheduled jobs, kernel patching, or credential storage.

## How it works

Use a 5-stage loop:

1. **Context:** identify user, groups, hostname, OS, kernel, shell, environment, and network role.
2. **Inventory:** enumerate privileges, writable paths, services, schedules, credentials, and unusual binaries.
3. **Hypothesis:** choose one plausible path and state why it may cross a boundary.
4. **Minimal proof:** prove the boundary issue with the least destructive action.
5. **Remediation evidence:** record owner, root cause, fix, and verification.

The meta-rule: a privesc path is not "found" until it explains which boundary failed.

### Worked example: from foothold to safe proof

```
Foothold: app user on owned lab VM
Context: app user belongs to deploy group
Lead: deploy group can write /opt/app/restart.sh
Privileged link: root systemd service runs the script during restart
Minimal proof: lab-only marker file showing effective root execution
Fix: root-owned deployment scripts, separate writable release directory, service restart through audited sudo rule
Retest: app user can deploy artifacts but cannot modify root-executed script
```

This is the branch pattern in miniature: local context, one boundary hypothesis, minimal proof, then remediation evidence.

## Techniques / patterns

- **Administrative delegation review:** inspect sudo rules, group memberships, service-control rights, and privileged helper programs.
- **File permission review:** find writable scripts, world-writable directories, SUID/SGID binaries, and misowned service files.
- **Credential discovery:** identify exposed keys, config files, shell history, tokens, and backup files without exfiltrating unnecessary data.
- **Scheduled execution review:** inspect cron jobs, systemd timers, and writable execution chains.
- **Kernel and package triage:** compare kernel/package versions to known risk while treating exploit execution as a last resort.

## Variants and bypasses

### 1. Configuration abuse

The system is functioning as configured, but the configuration grants too much power.

Examples include broad sudo rules, writable service scripts, and dangerous group membership.

### 2. Binary behavior abuse

A legitimate binary has features that become dangerous when run with elevated privileges.

GTFOBins is useful here because it documents privileged execution behaviors.

### 3. Environment influence

The privileged action trusts attacker-controlled input such as PATH, library paths, variables, or writable working directories.

### 4. Secrets as privilege

A low-privileged user finds credentials that legitimately unlock a higher-privileged user or service.

### 5. Vulnerability exploitation

The kernel, service, or package has a vulnerability that permits privilege escalation.

This class has the highest crash and ethics risk and should be triaged carefully.

## Impact

- Root shell or root-command execution.
- Reading sensitive files such as private keys, service credentials, or application config.
- Modifying services, logs, scheduled jobs, or application files.
- Pivoting from a single host to cloud metadata, internal networks, or higher-value accounts.
- Proving that local compromise has host-level or environment-level blast radius.

## Detection and defense

- **Patch and reduce kernel exposure first.** Kernel-level bugs are high-impact and often hard to safely test; patching and version visibility reduce emergency paths.
- **Constrain sudo by command and argument.** Least-privilege sudo rules are easier to audit than broad NOPASSWD or shell-capable binaries.
- **Remove unnecessary SUID/SGID and capabilities.** Privileged bits should be rare, justified, and monitored.
- **Lock down writable execution paths.** Scripts, service files, cron targets, and directories used by privileged tasks must not be writable by untrusted users.
- **Protect credentials by design.** Files, environment variables, backups, and logs should avoid storing reusable secrets.
- **Log administrative boundary crossings.** sudo, service changes, package installs, and privilege-relevant file changes should leave evidence.

### What does not work as a primary defense

- **Relying on user names.** A "normal" user can still inherit dangerous groups, sudo rules, or writable paths.
- **Hiding files.** Obscurity does not fix permissions or secret placement.
- **Running LinPEAS once.** Automated output is a triage input, not proof and not remediation.
- **Assuming patched kernel means safe host.** Most privesc paths are misconfigurations, not kernel exploits.

## Practical labs

Use an owned Linux VM.

### Build the first context card

```
id
hostnamectl 2>/dev/null || hostname
uname -a
pwd
echo "$PATH"
```

Record who you are, what system you are on, and what environment can influence commands.

### Create a path ranking table

```
Candidate:
Evidence:
Boundary crossed:
Likely impact:
Risk of testing:
Minimal proof:
Remediation:
```

This prevents "try everything" behavior and forces reasoning.

### Compare three path classes

```
sudo -l
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```

Treat the output as leads. Each lead needs manual verification.

### Record minimal proof

```
Target host:
Authorized scope:
Finding:
Proof action:
Observed result:
What was not done:
Rollback/remediation evidence:
```

Good privesc notes say what was intentionally avoided.

## Practical examples

- A user can run one backup command with sudo, but the command accepts a writable config file.
- A custom SUID helper calls `tar` without an absolute path.
- A service account can read an application config containing a database password.
- A kernel appears vulnerable by version, but the distribution has backported patches.
- LinPEAS highlights many items, but only one crosses a real privilege boundary.

## Related notes

- [[linux-enumeration]]
- [[sudo-misconfigurations]]
- [[suid-sgid-misconfigurations]]
- [[linux-capabilities]]
- [[kernel-exploit-triage]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

### Suggested future atomic notes

- linux-file-permissions
- linux-groups-and-users
- linux-credential-hunting
- linux-post-exploitation-cleanup

## References

- **Technique Reference:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
