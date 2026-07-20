---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Linux Capabilities

## Definition

Linux capabilities split root privileges into smaller units that can be assigned to processes or files.

A capability misconfiguration occurs when a binary receives a capability that lets a low-privileged user cross a sensitive boundary.

## Why it matters

Capabilities are often introduced to avoid full root, but they still grant pieces of root. A single dangerous capability can be equivalent to root in practice.

For defenders, capabilities are a precision tool that requires inventory and justification.

## How it works

Use 5 capability-risk questions:

1. **Which capability:** what exact power is granted?
2. **To what:** process, service, or file capability?
3. **Who can execute:** which users can run the binary?
4. **What behavior:** can the binary use the capability to read, write, bind, trace, or change identity?
5. **Can it chain:** does the capability combine with command execution or file write?

## Techniques / patterns

- Enumerate file capabilities with `getcap -r /`.
- Prioritize `cap_setuid`, `cap_setgid`, `cap_dac_read_search`, `cap_dac_override`, `cap_sys_admin`, `cap_net_raw`, and `cap_net_bind_service`.
- Check whether the binary is interpreter-like or shell-capable.
- Compare capability use to the operational need.
- Remove file capabilities that are no longer justified.

### Worked example: capability that outgrows its purpose

```
Lead: /usr/local/bin/net-helper = cap_net_raw+ep
Business purpose: collect packet diagnostics for support
Who can execute: all local users
Boundary question: can any user now perform packet-level activity?
Minimal proof: show capability-bearing execution path without capturing unrelated traffic
Fix: restrict execution to admin group or move diagnostics behind an audited service
```

Capabilities are not automatically bad. The finding appears when capability, executable behavior, and broad execution rights combine.

## Variants and bypasses

### 1. Identity-changing capability

`cap_setuid` or `cap_setgid` may allow user or group transition.

### 2. File-access capability

DAC override/read capabilities can bypass normal file permissions.

### 3. Network capability

Network capabilities can enable packet capture, raw sockets, or privileged port binding.

### 4. Broad system capability

`cap_sys_admin` is notoriously broad and often too close to root.

### 5. Container capability drift

Containers may run with capabilities that make host boundaries weaker than expected.

## Impact

- Privileged file read or write.
- Identity change or root-equivalent execution.
- Packet capture or network manipulation.
- Container escape preconditions.
- Service privilege expansion beyond intended design.

## Detection and defense

- **Inventory file capabilities.** Capabilities are less visible than SUID bits and need their own baseline.
- **Grant the narrowest capability possible.** Avoid broad capabilities such as `cap_sys_admin`.
- **Limit executable access.** A capability-bearing binary should not be executable by users that do not need it.
- **Prefer service-level privilege management.** Avoid scattering file capabilities across custom tools.
- **Monitor `setcap` changes.** Capability assignment is a privilege-boundary change.

### What does not work as a primary defense

- **Saying "it is not SUID."** Capabilities can be equally dangerous.
- **Granting broad capabilities for convenience.** The boundary becomes unclear.
- **Ignoring containers.** Container capabilities can change the meaning of "root inside the container."

## Practical labs

Use an owned VM or disposable container.

### Enumerate file capabilities

```
getcap -r / 2>/dev/null
```

Classify results as expected, unknown, or dangerous.

### Inspect one binary

```
ls -la /path/to/binary
getcap /path/to/binary
file /path/to/binary
```

Capability risk depends on both the capability and binary behavior.

### Build a capability risk table

```
Binary:
Capability:
Who can execute:
Normal purpose:
Dangerous behavior:
Minimal proof:
Safer alternative:
```

This turns capability output into a decision.

### Verify removal in a lab

```
sudo setcap -r /path/to/binary
getcap /path/to/binary
```

Only remove capabilities on owned lab systems or with change approval.

## Practical examples

- Python with `cap_setuid+ep` can become root-equivalent.
- A packet tool with `cap_net_raw` may be justified for a specific admin group, but risky for all users.
- A custom service binary keeps an old capability after the service no longer needs it.
- A container runs with excessive capabilities and weakens host isolation assumptions.
- A backup helper has DAC override when a narrower design would use group permissions.

## Related notes

- [[linux-privilege-escalation]]
- [[linux-enumeration]]
- [[suid-sgid-misconfigurations]]
- [[kernel-exploit-triage]]
- [[cloud-lab-infrastructure|Cloud Lab Infrastructure]]

### Suggested future atomic notes

- container-capabilities
- cap-sys-admin-risk
- linux-file-capability-inventory
- capability-hardening-baseline

## References

- **Official Docs:** Linux capabilities — https://man7.org/linux/man-pages/man7/capabilities.7.html
- **Official Docs:** setcap — https://man7.org/linux/man-pages/man8/setcap.8.html
- **Technique Reference:** GTFOBins: capabilities — https://gtfobins.github.io/#+capabilities
