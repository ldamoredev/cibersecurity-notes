---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# PATH Hijacking

## Definition

PATH hijacking is privilege escalation through influencing which executable or library a privileged process loads.

The classic case is a privileged script or binary calling `cp`, `tar`, or another helper without an absolute path while the attacker controls the search path or working directory.

## Why it matters

PATH hijacking turns a small coding shortcut into a privilege boundary failure. It is common in custom scripts, SUID helpers, cron jobs, service wrappers, and sudo rules.

For defenders, it is a reminder that privileged code must treat lookup behavior as untrusted input.

## How it works

Use 4 lookup questions:

1. **Caller:** what privileged process executes the helper?
2. **Lookup:** is the helper referenced by absolute path or searched by PATH?
3. **Control:** can the low user influence PATH, working directory, library path, or helper file?
4. **Privilege:** does the helper run as root or another privileged account?

## Techniques / patterns

- Inspect scripts for unqualified helper names.
- Inspect binaries for helper strings, but verify behavior carefully.
- Check sudo rules for `SETENV` or environment preservation.
- Check cron and systemd jobs for PATH definitions.
- Use `namei -l` to verify directory ownership along every path.

### Worked example: helper lookup failure

```
Privileged caller: root cron script
Command in script: tar -czf /backup/app.tgz /srv/app
PATH in job: /opt/app/bin:/usr/bin:/bin
Attacker control: /opt/app/bin is group-writable
Minimal proof: lab-only harmless helper logs its effective user
Fix: /usr/bin/tar plus root-owned PATH directories
```

PATH hijacking is not "PATH is weird." It is attacker-controlled lookup plus privileged execution.

## Variants and bypasses

### 1. Shell PATH hijack

A privileged shell script calls a helper by name.

### 2. Current-directory trust

The process searches or executes from a writable working directory.

### 3. Library path influence

The dynamic loader or program-specific plugin path loads attacker-controlled code.

### 4. Environment variable preservation

Sudo or service configuration preserves variables that influence lookup.

### 5. Relative path in service or cron

A scheduled or service command assumes a working directory that can be changed.

## Impact

- Privileged command execution.
- Root-owned file modification.
- Persistence through modified helper paths.
- Compromise of scheduled tasks or service restarts.
- Confusing behavior because the command name looks legitimate.

## Detection and defense

- **Use absolute paths in privileged scripts.** Search behavior should not decide privileged execution.
- **Set safe PATH explicitly.** Cron, sudo, and service contexts should define trusted paths.
- **Avoid dangerous environment preservation.** Loader and path variables should not cross into privileged contexts.
- **Protect parent directories.** A safe file in a writable directory is not a safe execution chain.
- **Prefer simpler privileged helpers.** Smaller, audited helpers are less likely to perform unsafe lookup.

### What does not work as a primary defense

- **Trusting the current PATH.** The current environment belongs to the caller unless reset.
- **Checking only file permissions.** Directory permissions and lookup order also matter.
- **Relying on script readability.** Compiled helpers can make the same mistake.

## Practical labs

Use an owned lab with a harmless privileged test script.

### Find unqualified commands in scripts

```
grep -R "tar\\|cp\\|mv\\|sh\\|bash" /opt /usr/local/bin 2>/dev/null
```

Manual review is required because grep only finds clues.

### Check the path chain

```
echo "$PATH"
which tar
namei -l "$(which tar)"
```

The executable and every parent directory must be trusted.

### Review sudo environment behavior

```
sudo -l
sudo -V | grep -i "env" | head
```

Look for `SETENV`, `secure_path`, and preserved variables.

### Build a PATH risk card

```
Privileged caller:
Helper command:
Absolute path used:
Attacker-controlled lookup component:
Privilege level:
Minimal proof:
Fix:
```

This keeps the finding concrete.

## Practical examples

- A root cron script calls `tar` without `/usr/bin/tar`.
- A SUID helper calls `service` by name.
- A sudo rule preserves PATH and permits a script that calls common helpers.
- A systemd service reads a writable environment file containing PATH.
- A privileged program loads a plugin from a writable directory.

## Related notes

- [[linux-privilege-escalation]]
- [[cron-and-timer-abuse]]
- [[sudo-misconfigurations]]
- [[suid-sgid-misconfigurations]]
- [[linux-enumeration]]

### Suggested future atomic notes

- ld-preload-abuse
- secure-path-in-sudoers
- privileged-script-hardening
- library-search-path-risk

## References

- **Official Docs:** Bash command search and execution — https://www.gnu.org/software/bash/manual/bash.html#Command-Search-and-Execution
- **Official Docs:** ld.so dynamic linker — https://man7.org/linux/man-pages/man8/ld.so.8.html
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
