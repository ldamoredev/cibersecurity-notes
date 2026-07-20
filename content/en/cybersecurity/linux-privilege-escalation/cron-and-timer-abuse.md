---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cron and Timer Abuse

## Definition

Cron and timer abuse occurs when a low-privileged user can influence a scheduled task that runs with higher privileges.

This includes classic cron jobs, systemd timers, writable scripts, writable directories, unsafe PATH values, and root-run maintenance workflows.

## Why it matters

Scheduled jobs are quiet privilege crossings. They often run as root, repeat automatically, and execute scripts that were not reviewed like production code.

For defenders, scheduled execution review catches a large class of preventable local escalation paths.

## How it works

Ask 5 questions:

1. **Who runs it:** root, service account, or user?
2. **What runs:** binary, shell script, interpreter, or command string?
3. **Where from:** absolute path, relative path, wildcard, or writable directory?
4. **What input:** files, directories, environment, glob expansion, config, or logs?
5. **Who can write:** can a low user modify anything in the execution chain?

## Techniques / patterns

- Inspect `/etc/crontab`, `/etc/cron.*`, user crontabs, and systemd timers.
- Check permissions on scripts and parent directories.
- Look for wildcard expansion and relative command paths.
- Identify jobs that process user-writable files.
- Verify scheduled task behavior in a lab without waiting for production cycles.

### Worked example: writable backup chain

```
Schedule: root runs /opt/backup/run.sh every 5 minutes
Script owner: root:backup-ops
Script mode: group-writable
User context: low user belongs to backup-ops
Boundary question: can the low user change root-executed code?
Minimal proof: in lab, write a harmless timestamp marker to /tmp
Fix: root-owned immutable deployment path and separate writable data directory
```

Scheduled-task findings should trace the full chain from schedule to identity to writable component.

## Variants and bypasses

### 1. Writable script

A root cron job executes a script writable by a low-privileged user.

### 2. Writable directory

The script is protected, but its parent directory or included files are writable.

### 3. PATH or relative command

The scheduled job calls a program by name and trusts a PATH value.

### 4. Wildcard expansion

The job processes files from a writable directory in a way that changes command behavior.

### 5. systemd timer chain

A timer triggers a service whose unit file, environment file, or script is writable.

## Impact

- Delayed root command execution.
- Persistent root-level modification.
- Credential theft from backup or maintenance scripts.
- Service tampering through scheduled restart or cleanup workflows.
- Hard-to-debug recurring compromise.

## Detection and defense

- **Use absolute paths in scheduled tasks.** Remove ambiguity from privileged execution.
- **Protect scripts and parent directories.** The whole execution chain must be root-owned or otherwise tightly controlled.
- **Avoid processing attacker-writable directories as root.** Use safe staging, strict ownership, and defensive glob handling.
- **Inventory timers and cron jobs.** Scheduled execution should be part of baseline review.
- **Log scheduled job activity.** Failure and unexpected file changes should be observable.

### What does not work as a primary defense

- **Only checking `/etc/crontab`.** User crontabs, `/etc/cron.*`, systemd timers, and app schedulers also matter.
- **Protecting the script but not the directory.** Parent directory write access can still be dangerous.
- **Assuming infrequent jobs are safe.** A daily root job is still a root boundary.

## Practical labs

Use an owned VM with a deliberately safe test job.

### Enumerate scheduled tasks

```
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.* 2>/dev/null
systemctl list-timers --all 2>/dev/null
```

Record who owns each job and what it executes.

### Check script and directory permissions

```
ls -la /path/to/script
namei -l /path/to/script
```

`namei -l` shows every directory in the path.

### Build an execution-chain table

```
Schedule:
Runs as:
Command:
Script owner:
Directory owners:
User-writable inputs:
Risk:
Fix:
```

This makes the whole chain visible.

### Verify remediation

```
sudo chown root:root /path/to/script
sudo chmod 755 /path/to/script
namei -l /path/to/script
```

In real systems, use change control before modifying scheduled jobs.

## Practical examples

- A root cron job runs `/opt/backup.sh`, and `/opt` is writable by a support group.
- A cleanup script processes files from `/tmp` with unsafe wildcard behavior.
- A systemd timer triggers a service that reads an environment file writable by an app user.
- A script calls `tar` without an absolute path under a modified PATH.
- A backup job exposes credentials in logs readable by low users.

## Related notes

- [[linux-privilege-escalation]]
- [[linux-enumeration]]
- [[path-hijacking]]
- [[suid-sgid-misconfigurations]]
- [[linpeas-workflow]]

### Suggested future atomic notes

- systemd-service-permissions
- cron-wildcard-abuse
- writable-service-files
- scheduled-job-hardening

## References

- **Official Docs:** crontab file format — https://man7.org/linux/man-pages/man5/crontab.5.html
- **Official Docs:** systemd timers — https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- **Official Docs:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
