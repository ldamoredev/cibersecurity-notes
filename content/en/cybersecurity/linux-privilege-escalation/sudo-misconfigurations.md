---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Sudo Misconfigurations

## Definition

Sudo misconfiguration is an administrative delegation flaw where a user can run a command as another user, often root, in a way that grants more power than intended.

## Why it matters

Sudo is a normal operations tool, so its risk is often hidden inside legitimate maintenance workflows. A single broad rule can turn a minor foothold into full host compromise.

For defenders, sudo review is one of the highest-value Linux hardening activities because it directly describes who may cross privilege boundaries.

## How it works

Ask 5 sudo questions:

1. **Who:** which user or group receives delegation?
2. **As whom:** which target user can they become?
3. **What:** which command, path, and arguments are allowed?
4. **How:** is a password required, is environment preserved, are wildcards used?
5. **Escape:** can the allowed command run a shell, edit files, load plugins, or write root-owned paths?

## Techniques / patterns

- Inspect `sudo -l` before reading assumptions from `/etc/sudoers`.
- Treat command arguments as part of the permission.
- Check GTFOBins for shell escape or file-write behavior.
- Look for `NOPASSWD`, `SETENV`, broad wildcards, interpreters, editors, pagers, archive tools, and package managers.
- Prove with minimal commands in an owned lab.

### Worked example: sudo rule to root cause

```
sudo -l lead: (root) NOPASSWD: /usr/bin/vim /var/log/app.log
Boundary question: can the user use the editor to write outside the intended file?
Minimal lab proof: demonstrate root-owned file write in a disposable path
What not to do: modify real logs or plant persistence
Root cause: shell-capable/editor binary delegated as root
Fix: replace editor sudo with a narrow log-view command or controlled support workflow
```

The report should not stop at "vim can escape." It should explain why the delegated workflow gave the user a general-purpose root editor.

## Variants and bypasses

### 1. Shell-capable binary

The allowed command can spawn a shell or execute another command.

### 2. File write as root

The command can overwrite root-owned files or place content in trusted locations.

### 3. Argument wildcard

A sudo rule restricts the binary but allows attacker-controlled arguments.

### 4. Environment preservation

The rule allows dangerous environment influence through `SETENV`, `env_keep`, or loader variables.

### 5. Relative or writable command path

The rule points to a path that can be replaced or influenced by the user.

## Impact

- Root command execution.
- Root file read or write.
- Persistent service or cron modification.
- Secret extraction from root-readable files.
- Lateral movement through keys, tokens, or configuration.

## Detection and defense

- **Use exact command paths and exact arguments.** Sudo rules should be narrow enough that command behavior is predictable.
- **Avoid shell-capable tools where possible.** Editors, pagers, interpreters, and archive tools often have escape behavior.
- **Require authentication for sensitive paths.** `NOPASSWD` should be rare and justified.
- **Disable dangerous environment preservation.** Avoid `SETENV` and broad `env_keep` rules unless the risk is understood.
- **Review sudo logs.** Sudo execution should be observable and tied to a user.

### What does not work as a primary defense

- **Trusting that a command "is not a shell."** Many tools can execute commands indirectly.
- **Relying on user training.** The policy should prevent accidental overreach.
- **Using wildcards for convenience.** Wildcards often move the security decision from policy to attacker-controlled input.

## Practical labs

Use an owned lab user with a deliberately safe sudo rule.

### Read the user's sudo surface

```
sudo -l
```

Copy the exact command, target user, password state, and options.

### Classify the command

```
Allowed command:
Target user:
Password required:
Can read files:
Can write files:
Can execute commands:
Environment influence:
GTFOBins class:
```

This makes the risky behavior explicit.

### Test argument boundaries safely

```
sudo /allowed/command --help
sudo /allowed/command --version
```

Use documentation and harmless flags before trying impact proof.

### Record a minimal proof decision

```
Finding:
Allowed sudo rule:
Potential escape:
Proof chosen:
Why this proof is minimal:
Fix:
Retest:
```

The report should explain policy failure, not just "got root".

## Practical examples

- A user may run `vim` as root and can edit root-owned files.
- A backup command accepts a destination path that writes into `/etc`.
- A sudo rule allows `/usr/bin/find *`, and argument control changes behavior.
- `SETENV` lets a privileged command load untrusted behavior.
- A rule grants a service restart, but the service file is writable by the user.

## Related notes

- [[linux-privilege-escalation]]
- [[linux-enumeration]]
- [[path-hijacking]]
- [[suid-sgid-misconfigurations]]
- [[linpeas-workflow]]

### Suggested future atomic notes

- sudoers-policy-design
- sudo-environment-risk
- gtfobins-workflow
- writable-service-files

## References

- **Official Docs:** sudoers manual — https://www.sudo.ws/docs/man/sudoers.man/
- **Technique Reference:** GTFOBins: sudo — https://gtfobins.github.io/#+sudo
- **Official Docs:** sudo manual — https://www.sudo.ws/docs/man/sudo.man/
