---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Linux Enumeration

## Definition

Linux enumeration is the structured collection of local host facts that can explain privilege boundaries, misconfigurations, credentials, and escalation paths.

It is the first real skill in Linux privilege escalation because every later action depends on the quality of the evidence.

## Why it matters

Bad enumeration creates noisy guessing. Good enumeration narrows the host to a few plausible questions: who am I, what can I run, what can I write, what runs as root, what secrets exist, and what is different from a hardened baseline.

For defenders, enumeration teaches what a low-privileged user can learn from the host.

## How it works

Use 7 evidence buckets:

1. **Identity:** user, groups, uid/gid, shells, home directories.
2. **System:** OS, kernel, packages, architecture, hostname, virtualization hints.
3. **Privileges:** sudo, SUID/SGID, capabilities, privileged groups.
4. **Writable surfaces:** files, directories, scripts, service units, cron targets.
5. **Processes and services:** root processes, local ports, service accounts, timers.
6. **Secrets:** keys, configs, history, backups, tokens, environment variables.
7. **Network context:** interfaces, routes, local-only services, cloud metadata reachability.

## Techniques / patterns

- Start with low-risk read-only commands.
- Preserve command output with timestamps and host identity.
- Separate fact collection from exploit testing.
- Prioritize unusual local changes over standard system files.
- Compare automated findings against manual checks.

### Worked example: one enumeration lead becomes one test

```
Observed fact: user is in group backup-ops
Second fact: /opt/backups/run-backup.sh is group-writable
Privileged link: root cron executes /opt/backups/run-backup.sh
Hypothesis: backup-ops can influence root execution
Minimal proof: change only a harmless marker in a lab copy
Defensive fix: root-owned script, restricted group write, reviewed deployment path
```

The important move is connecting facts across buckets. Group membership alone is not a finding; a writable script alone is not a finding; root scheduled execution creates the boundary question.

## Variants and bypasses

### 1. Minimal shell enumeration

Restricted shells, reverse shells, and non-interactive sessions may lack TTY, PATH, or common tools.

### 2. Container enumeration

The host may be a container where root inside the container is not root on the host, but mounts, sockets, or capabilities may still cross boundaries.

### 3. Cloud-host enumeration

Cloud instances add metadata, IAM roles, startup scripts, and attached volumes to the local question set.

### 4. Multi-user server enumeration

Shared hosts expose group membership, home directory permissions, and local service trust relationships.

### 5. Hardened host enumeration

Good hardening may hide little, but still leaves enough to verify that controls are working.

## Impact

- Finds the few escalation paths worth manual verification.
- Prevents unsafe exploit attempts based on weak assumptions.
- Produces defensive hardening evidence.
- Creates a reproducible timeline for labs, reports, and retests.

## Detection and defense

- **Harden low-privileged visibility where possible.** Some data is inherently local, but secrets, logs, and configs should not be broadly readable.
- **Monitor suspicious enumeration bursts.** Many read-only commands in a short window can signal post-exploitation activity.
- **Reduce unnecessary local services.** Fewer services and users means fewer local trust relationships.
- **Keep baselines.** Known-good SUID lists, capabilities, timers, and sudo rules make drift visible.
- **Document expected privilege paths.** Legitimate admin paths should be clear enough that anomalies stand out.

### What does not work as a primary defense

- **Blocking one command.** Enumeration uses many equivalent commands and files.
- **Assuming read-only means harmless.** Readable secrets and configs can be privilege boundaries.
- **Ignoring local-only services.** A service bound to `127.0.0.1` may still be reachable from a foothold.

## Practical labs

Use an owned VM and save outputs into a lab folder.

### Build a host snapshot

```
mkdir -p privesc-enum
id | tee privesc-enum/id.txt
uname -a | tee privesc-enum/uname.txt
cat /etc/os-release | tee privesc-enum/os-release.txt
```

This creates repeatable evidence instead of relying on memory.

### Enumerate privilege leads

```
sudo -l 2>&1 | tee privesc-enum/sudo-l.txt
find / -perm -4000 -type f 2>/dev/null | tee privesc-enum/suid.txt
getcap -r / 2>/dev/null | tee privesc-enum/capabilities.txt
```

Classify each result before testing it.

### Enumerate writable execution surfaces

```
find / -writable -type d 2>/dev/null | head -100
find /etc/systemd /etc/cron* -writable 2>/dev/null
```

Writable does not mean exploitable unless a privileged process uses it.

### Enumerate local services

```
ss -lntup 2>/dev/null
ps aux --forest 2>/dev/null | head -80
```

Record which processes run as root and whether low users can influence them.

## Practical examples

- `sudo -l` reveals one restricted command worth deeper inspection.
- `getcap` finds a binary with `cap_setuid+ep`.
- A writable directory is harmless until a root cron job executes scripts from it.
- A local admin panel bound to localhost matters after SSH access.
- A container has a mounted Docker socket, changing the host boundary question.

## Related notes

- [[linux-privilege-escalation]]
- [[sudo-misconfigurations]]
- [[suid-sgid-misconfigurations]]
- [[linux-capabilities]]
- [[cron-and-timer-abuse]]
- [[cloud-metadata-security|Cloud Metadata Security]]

### Suggested future atomic notes

- linux-enumeration-output-triage
- container-breakout-triage
- linux-local-service-enumeration
- linux-credential-hunting

## References

- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Official Docs:** proc filesystem — https://man7.org/linux/man-pages/man5/proc.5.html
- **Official Docs:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
