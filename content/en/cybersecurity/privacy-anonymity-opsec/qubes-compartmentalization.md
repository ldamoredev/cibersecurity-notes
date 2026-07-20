---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Qubes Compartmentalization

## Definition

Qubes compartmentalization is the practice of separating activities into isolated virtual machines, called qubes, so compromise or leakage in one compartment does not automatically expose every other activity on the computer.

## Why it matters

Many privacy failures are endpoint failures. A browser profile, document editor, chat app, password manager, and personal account all run on the same daily system and silently share files, clipboard, network, credentials, and device context.

Qubes changes the operating model. Instead of trusting one desktop environment, the user designs compartments for work, personal use, risky files, anonymous activity, vault data, and disposable tasks. This is powerful, but it requires planning and discipline.

## How it works

Use the 5-boundary model:

1.
**Separate qubes**
   Each compartment has its own filesystem and process space.

2.
**Templates provide software base**
   Template-based qubes share a managed base while keeping user data separate.

3.
**Network qubes mediate connectivity**
   App qubes can use different network paths, including no network, normal network, VPN, or Tor via Whonix.

4.
**Policy controls interaction**
   Copy, file transfer, devices, and inter-qube services are mediated rather than automatic.

5.
**Dom0 remains special**
   The administrative domain is highly sensitive and should not be used for ordinary work.

Sketch:

```
personal qube    -> normal network
work qube        -> work network
research qube    -> disposable / restricted
vault qube       -> no network
anon qube        -> Whonix/Tor path
dom0             -> administration only
```

The bug is not having many compartments. The bug is moving data between them until the boundaries no longer mean anything.

## Techniques / patterns

- Define compartments by identity and risk, not only by application.
- Use disposable qubes for untrusted documents and one-off browsing.
- Keep secrets in offline or tightly restricted qubes.
- Avoid routine copy/paste between identities.
- Use different network qubes for different trust models.
- Treat USB and device assignment as high-risk.
- Keep dom0 clean and boring.

## Variants and bypasses

Use the 6 compartment patterns:

### 1. Identity compartments

Personal, work, pseudonymous, and anonymous identities should not share browser state, files, or credentials.

### 2. Risk compartments

Untrusted documents, unknown links, and risky research belong in disposable or restricted qubes.

### 3. Network compartments

Some qubes use normal networking, some use VPN, some use Tor/Whonix, and some use no network. The network path is part of the compartment definition.

### 4. Secret compartments

Password databases, keys, signing material, and sensitive documents can live in qubes with limited or no network access.

### 5. Device compartments

USB, camera, microphone, and other devices should be assigned carefully because devices can bridge compartments.

### 6. Human workflow bypass

Users can defeat compartments by copying files, screenshots, text, credentials, or browser links across boundaries without thinking.

## Impact

- Reduced blast radius from malware or browser compromise.
- Better identity separation when compartments are designed and respected.
- Safer handling of untrusted files through disposables.
- Higher complexity and operational burden.
- New failure modes from bad policy, careless file movement, and device assignment.

## Detection and defense

Ordered by effectiveness:

1.
**Design compartments before daily use**
   A compartment model should describe identities, data sensitivity, network path, and allowed transfers. Ad hoc qubes become clutter, not security.

2.
**Use disposables for untrusted input**
   Disposable qubes reduce persistence and make risky documents or links less able to contaminate long-lived identity compartments.

3.
**Limit cross-qube data movement**
   Every copy, paste, file move, and screenshot is a possible boundary crossing. Make transfers intentional.

4.
**Keep secrets offline where practical**
   Networkless qubes are useful for high-value secrets because many attacks require outbound communication.

5.
**Constrain devices**
   USB and peripheral assignment should be explicit. Device compromise can undermine VM isolation assumptions.

6.
**Audit compartment drift**
   Periodically check whether qubes still match their intended identity, risk, and network roles.

### What does not work as a primary defense

- **Many qubes do not guarantee separation.** Bad transfer habits can reconnect everything.
- **Qubes does not fix account correlation.** Logging into the same account from two compartments links them.
- **Network isolation is not file sanitization.** Files still carry metadata and active content risks.
- **Dom0 is not a workspace.** Treating dom0 like a normal desktop undermines the architecture.

## Practical labs

### Draft a compartment map

```
Qube name:
Identity/purpose:
Network path:
Secrets stored:
Allowed inbound files:
Allowed outbound files:
Allowed clipboard:
Disposable needed:
```

This turns compartments into a deliberate architecture.

### Review cross-boundary transfers

```
Transfer:
From qube:
To qube:
Data type:
Metadata risk:
Identity-link risk:
Allowed by policy:
Alternative:
```

The transfer log catches boundary erosion.

### Identify offline secret candidates

```
Secret:
Current location:
Needs internet:
Needs clipboard:
Backup method:
Offline qube candidate:
```

Secrets that do not need internet should not casually live in internet-facing compartments.

### Build a disposable workflow

```
Untrusted input:
Disposable qube used:
Network enabled:
Output needed:
Sanitization step:
Long-lived qube touched:
```

The goal is to handle risky input without contaminating identity compartments.

## Practical examples

- A user opens unknown PDFs in disposable qubes before moving sanitized output elsewhere.
- A work qube and personal qube use separate browsers, files, and network paths.
- A vault qube stores password databases without direct internet access.
- A user copies text from anonymous research into a personal qube, linking contexts.
- A USB device is assigned only to a dedicated qube because peripherals are risky.

## Related notes

- [[whonix-gateway|Whonix Gateway]]
- [[tails-operational-model|Tails Operational Model]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[file-metadata-removal|File Metadata Removal]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- qubes-disposable-qubes
- qubes-usb-security
- qubes-whonix
- split-gpg

## References

- **Official Tool Docs:** Qubes OS documentation - https://doc.qubes-os.org/en/latest/
- **Official Tool Docs:** Qubes OS architecture - https://doc.qubes-os.org/en/latest/developer/system/architecture.html
- **Threat Model:** Qubes OS security design goals - https://doc.qubes-os.org/en/latest/developer/system/security-design-goals.html
