---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Command Injection

## Definition

Command injection occurs when an application builds an operating-system command from attacker-controlled input and executes it through a shell or process API without strict separation between data and command syntax.

## Why it matters

Command injection crosses from application logic into the host operating system. Impact can jump from a single web feature to file read, credential theft, lateral movement, cloud metadata access, or remote code execution.

It is the OS-command version of the broader injection lesson: untrusted input must not become interpreter syntax.

## How it works

Command injection has **4 moving parts**:

1. **Input.** User-controlled data reaches a feature such as ping, PDF conversion, image processing, backup, or Git tooling.
2. **Command construction.** The server concatenates input into a shell command.
3. **Interpreter boundary.** The shell interprets metacharacters such as `;`, `&&`, `|`, `$()`, or backticks.
4. **Execution.** The command runs with the application's OS privileges.

Unsafe pattern:

```
exec("ping -c 1 " + req.query.host)
```

Payload-shaped example:

```
host=127.0.0.1; id
```

The bug is not "ping exists." The bug is attacker-controlled data crossing into shell syntax.

## Techniques / patterns

Attackers test:

- network tools: ping, nslookup, curl, traceroute
- file tools: convert, ffmpeg, tar, zip, grep
- deployment/tools: git, docker, kubectl, backup scripts
- separators: `;`, `&&`, `||`, `|`, newline
- command substitution: `$()`, backticks
- blind indicators: time delay, DNS/HTTP callbacks, changed output

## Variants and bypasses

Command injection appears in **5 contexts**.

### 1. Direct output injection

The command output appears in the HTTP response.

### 2. Blind command injection

The response does not show output, so timing or out-of-band callbacks prove execution.

### 3. Argument injection

Input cannot add a new command but can add flags that change the invoked tool's behavior.

### 4. Environment injection

User-controlled environment variables, paths, or filenames influence execution.

### 5. Shell-less process misuse

Even without a shell, unsafe arguments can still trigger tool-level dangerous behavior.

## Impact

Ordered roughly by severity:

- **Remote code execution.** Commands run as the application user.
- **Credential and secret theft.** Environment variables, files, cloud metadata, or service credentials leak.
- **Lateral movement.** Internal network tools become reachable from the server.
- **Data destruction or alteration.** Commands delete, overwrite, or exfiltrate data.
- **Host reconnaissance.** Attackers learn users, paths, processes, and network access.

## Detection and defense

Ordered by effectiveness:

1.
**Avoid shelling out for request-driven work.**
   Use library APIs or safe internal implementations instead of invoking shell commands.

2.
**If a process is required, pass arguments as an array to a non-shell API.**
   Keep executable and arguments structurally separate so metacharacters remain data.

3.
**Allowlist input by expected domain.**
   Validate hostnames, filenames, IDs, or enum choices before they reach any command.

4.
**Run with least privilege and isolation.**
   Containers, sandboxing, low-privilege users, and network egress limits reduce blast radius.

5.
**Log command invocations and reject suspicious metacharacters.**
   Logging helps detection, but filtering is secondary to avoiding shell interpretation.

### What does not work as a primary defense

- **Blacklisting a few characters.** Shell syntax has many separators, encodings, and platform differences.
- **Escaping without understanding the shell.** Escaping rules vary and are easy to misapply.
- **Hiding output.** Blind injection can still use timing or callbacks.
- **WAF signatures.** The dangerous boundary is server-side command construction.

## Practical labs

Use local labs or intentionally vulnerable targets only.

### Find command execution sinks

```
rg -n "exec\\(|spawn\\(|system\\(|popen\\(|Runtime\\.getRuntime|ProcessBuilder|subprocess" src
```

Review whether user input reaches the sink.

### Test benign separator behavior

```
curl -i 'https://app.example.test/ping?host=127.0.0.1%3Bid'
```

Only run against owned labs.

### Test blind timing safely

```
curl -w "%{time_total}\n" -o /dev/null -s 'https://app.example.test/ping?host=127.0.0.1%3Bsleep%205'
```

Timing differences can indicate execution when no output is shown.

## Practical examples

- A network diagnostic page shells out to `ping`.
- A PDF conversion feature passes filenames through a shell.
- A backup endpoint builds `tar` commands from request data.
- An image processor accepts arguments that become command flags.
- A Git webhook invokes shell commands with branch names.

## Related notes

- [[sql-injection]]
- [[ssrf]]
- [[path-traversal]]
- [[file-upload-abuse]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

### Suggested future atomic notes

- blind-command-injection
- argument-injection
- shell-metacharacters
- safe-process-execution
- out-of-band-command-injection

## References

- **Foundational:** OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OS command injection — https://portswigger.net/web-security/os-command-injection
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
