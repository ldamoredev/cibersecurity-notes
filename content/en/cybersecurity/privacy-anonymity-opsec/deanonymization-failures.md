---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Deanonymization Failures

## Definition

Deanonymization failures are the ways a supposedly anonymous workflow becomes linkable again through accounts, metadata, browser state, behavior, network mistakes, or endpoint compromise.

## Why it matters

Users usually do not lose anonymity because one giant control fails. They lose it through a chain of small mistakes that line up: same account, same browser, same file, same schedule, same device, same network leak, same recipient, same recovery email.

## How it works

Use the 6-link failure chain:

1.
**Initial link**
   The user introduces a stable identity signal, such as a login, payment, or username.

2.
**State reuse**
   Cookies, browser state, device state, or filesystem paths persist across activities.

3.
**Metadata spill**
   Files, photos, documents, or messages carry hidden identifiers.

4.
**Behavioral match**
   Timing, writing style, interests, and interaction patterns line up.

5.
**Network mismatch**
   DNS, IPv6, app bypass, or reconnect behavior exposes a normal path.

6.
**Cross-observation**
   A service, provider, or observer connects the dots across sessions or platforms.

The bug is not a single mistake. The bug is a failure chain that no one rechecks end to end.

## Techniques / patterns

- Reconstruct the chain, not just the last leak.
- Ask where the first stable identifier entered.
- Check whether the workflow reuses devices, browsers, accounts, or files.
- Look for invisible spill points such as recovery email, device sync, and cloud backup.
- Identify which observer had enough data to correlate.

## Variants and bypasses

Use the 7 failure classes:

### 1. Login failure

The user logs into a real identity on a site that was supposed to remain pseudonymous.

### 2. File failure

A file, screenshot, PDF, or photo contains identifying metadata or visible context.

### 3. Browser failure

A browser fingerprint, extension set, or cookie jar persists identity.

### 4. Device failure

The device itself carries a stable identity through sync, OS state, or installed software.

### 5. Behavior failure

The user's writing style, timing, or routine points to the same person.

### 6. Provider failure

The service, VPN, email provider, or cloud provider logs enough to correlate users.

### 7. Operational failure

The workflow mixes identities, transfers files badly, or reuses the wrong compartment.

## Impact

- Pseudonymous activity linked to real identity.
- Sensitive research exposed through ordinary mistakes.
- Source, whistleblower, or personal-safety workflows compromised.
- False confidence in privacy tooling.
- Re-identification by a destination service or provider.

## Detection and defense

Ordered by effectiveness:

1.
**Trace the first stable identity signal**
   Find the earliest moment the workflow became linkable.

2.
**Break the chain at multiple points**
   Compartmentalization, metadata cleaning, browser isolation, and account separation all help.

3.
**Retest from the observer's view**
   Do not trust the user's intention; inspect what an observer can actually see.

4.
**Remove unnecessary persistence**
   Cookies, sync, backups, and saved files often create the linkage.

5.
**Use dry-run checklists**
   A preflight checklist catches many errors before publication or transmission.

### What does not work as a primary defense

- **Fixing only the last leak is not enough.**
- **Deleting a post after exposure does not erase logs or copies.**
- **Changing the username alone does not break the chain.**
- **Assuming "nobody noticed" is not evidence.**

## Practical labs

### Build a failure chain

```
Activity:
Identity signal 1:
Identity signal 2:
Metadata spill:
Browser state:
Network leak:
Behavioral clue:
Observer:
Link result:
```

This is the core deanonymization exercise.

### Reconstruct a miss

```
What was supposed to be anonymous:
First link introduced:
What was reused:
What metadata leaked:
What behavior matched:
What observer correlated it:
Where to break earlier next time:
```

The point is to improve the workflow, not blame the last step.

### Preflight anonymity checklist

```
Real-name account? yes/no
Same browser profile? yes/no
Same device? yes/no
Metadata cleaned? yes/no
DNS checked? yes/no
IPv6 checked? yes/no
External apps used? yes/no
Files transferred? yes/no
```

This catches the common failure path.

### Compare intended vs observed identity

```
Intended persona:
Observed signals:
Conflict?
Reason:
Fix:
```

If intended and observed diverge, the workflow is leaky.

## Practical examples

- A pseudonymous account is linked by a reused recovery email.
- A Tor session is deanonymized by a downloaded document with author metadata.
- A VPN user is linked by the same browser fingerprint and writing style.
- A source's identity leaks through a cloud backup and sync account.
- A researcher uses the same browser profile across unrelated personas and gets correlated.

## Related notes

- [[anonymity-threat-models|Anonymity Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[account-correlation|Account Correlation]]
- [[traffic-correlation|Traffic Correlation]]

### Suggested future atomic notes

- opsec-checklists
- failure-chain-analysis
- identity-spill

## References

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Research / Deep Dive:** Tor Project Research - https://research.torproject.org/
