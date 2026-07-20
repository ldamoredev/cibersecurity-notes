---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# LinPEAS Workflow

## Definition

LinPEAS workflow is the disciplined use of the LinPEAS enumeration script as a triage assistant for Linux privilege escalation, followed by manual verification and remediation-focused reporting.

LinPEAS is not the finding. The manually verified boundary failure is the finding.

## Why it matters

Automation helps learners and testers avoid missing common paths, but it can also produce noisy output, false positives, and shallow reports.

A good workflow uses LinPEAS to prioritize where to look, then proves one path clearly.

## How it works

Use 5 phases:

1. **Prepare:** confirm authorization, host role, upload policy, and cleanup expectations.
2. **Run:** execute the script in a controlled way and save output.
3. **Triage:** group findings by sudo, SUID, capabilities, writable paths, credentials, services, and kernel.
4. **Verify:** manually test one candidate with minimal proof.
5. **Report:** explain root cause, impact, fix, and retest evidence.

## Techniques / patterns

- Run tooling after basic manual context collection.
- Save raw output but do not paste it wholesale into notes.
- Treat colors and severity as prompts, not truth.
- Verify commands manually and read relevant files.
- Clean up scripts and outputs according to the lab or engagement rules.

### Worked example: tool output to verified finding

```
LinPEAS highlight: possible writable service file
Manual check: namei -l and systemctl cat confirm writable drop-in
Boundary question: does root/systemd consume this file?
Minimal proof: lab-only service override writes a harmless marker
Finding: low user can influence root service configuration
Fix: root-owned service path, deployment controls, alert on unit changes
```

The value of LinPEAS is prioritization. The value of the operator is turning a highlight into proof or rejecting it.

## Variants and bypasses

### 1. No-upload environment

Policy or technical controls may prohibit uploading scripts; manual enumeration must still work.

### 2. Restricted shell

The session may lack TTY, writable directories, or common interpreters.

### 3. Noisy production host

Running broad scripts may be inappropriate on sensitive systems.

### 4. CTF speed mode

In labs, LinPEAS may quickly point toward the intended path, but learning still requires understanding the path.

### 5. False-positive-heavy output

Many highlighted items are informational or non-exploitable without another condition.

## Impact

- Faster enumeration.
- Better coverage of common Linux privesc categories.
- Risk of noise, accidental data collection, or overclaiming.
- Improved reports when output is converted into verified evidence.

## Detection and defense

- **Assume enumeration scripts are observable.** Execution, file creation, and many local reads may appear in logs or EDR.
- **Restrict script upload and execution where appropriate.** Controls should be policy-driven, not ad hoc.
- **Reduce findings through hardening.** Clean sudo rules, SUID, capabilities, writable paths, and secrets reduce automated signal.
- **Use LinPEAS defensively in labs.** Blue teams can run it against golden images to find drift.
- **Pair automation with baselines.** A known-good host makes output easier to evaluate.

### What does not work as a primary defense

- **Blocking LinPEAS by name.** Enumeration can be done manually or with modified tools.
- **Treating no red output as secure.** Scripts are incomplete and context-dependent.
- **Accepting script output as proof.** Manual verification is required.

## Practical labs

Use an owned VM.

### Run manual context first

```
id
uname -a
sudo -l
```

This gives you anchors before automated output.

### Save LinPEAS output

```
./linpeas.sh | tee linpeas-output.txt
```

Only run downloaded scripts when the lab allows it and you understand the source.

### Triage by category

```
Sudo:
SUID/SGID:
Capabilities:
Writable paths:
Credentials:
Services/timers:
Kernel:
Top manual check:
```

Convert output into a small action list.

### Verify one candidate manually

```
LinPEAS line:
Manual command:
Observed evidence:
Boundary crossed:
Minimal proof:
Fix:
```

This is the step that turns tool output into knowledge.

## Practical examples

- LinPEAS highlights a SUID binary; manual GTFOBins review explains whether it matters.
- LinPEAS reports a writable directory; manual tracing shows no privileged process uses it.
- LinPEAS finds a sudo rule; the real issue is the command's file-write behavior.
- LinPEAS flags kernel versions; vendor patch metadata rejects the path.
- A defensive team runs LinPEAS on a lab image and removes unnecessary capabilities.

## Related notes

- [[linux-privilege-escalation]]
- [[linux-enumeration]]
- [[sudo-misconfigurations]]
- [[suid-sgid-misconfigurations]]
- [[kernel-exploit-triage]]

### Suggested future atomic notes

- linpeas-output-triage
- manual-privesc-verification
- linux-privesc-reporting
- authorized-tool-upload-policy

## References

- **Official Tool Docs:** PEASS-ng / LinPEAS — https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
- **Technique Reference:** GTFOBins — https://gtfobins.github.io/
