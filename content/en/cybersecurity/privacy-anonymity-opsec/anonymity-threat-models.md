---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Anonymity Threat Models

## Definition

An anonymity threat model is a structured account of who is trying to link an action to a person, what they can observe, and what privacy controls actually reduce that linkage.

## Why it matters

Anonymity is adversary-specific. A tool can be sufficient against a local network operator, insufficient against a website, and useless against a device compromise. If the observer is not named, tool choice becomes guesswork.

## How it works

Use the 5-question model:

1.
**Who is the observer?**
   Local network, ISP, VPN provider, website, employer, cloud provider, or powerful network adversary.

2.
**What can they see?**
   Content, metadata, account identity, browser fingerprints, device behavior, file metadata, or traffic timing.

3.
**What can they correlate?**
   Logs, IPs, cookies, usernames, schedules, writing style, and repeated behaviors.

4.
**What consequence follows if linkage occurs?**
   Surveillance, harassment, employment impact, legal exposure, source exposure, or simple tracking.

5.
**What control changes that observer's view?**
   Tor, VPN, compartmentalization, metadata cleaning, encrypted messaging, or policy controls.

The bug is not lacking a tool. The bug is not defining the observer and consequence first.

## Techniques / patterns

- Start with the harshest realistic observer, not the easiest one.
- Separate confidentiality from anonymity.
- Treat metadata and behavior as first-class identity signals.
- Write the threat model down before combining tools.
- Re-evaluate whenever the workflow changes.

## Variants and bypasses

Use the 5 common anonymity models:

### 1. Local-network privacy

Goal: hide activity from cafe, hotel, school, or office network operators.

### 2. ISP privacy

Goal: reduce what an ISP can see about destinations and behavior.

### 3. Destination unlinkability

Goal: prevent the website from tying activity to a persistent identity.

### 4. Source protection

Goal: hide the operator's location or network from the destination.

### 5. Multi-observer resistance

Goal: avoid correlation by a provider, service, or powerful observer across multiple vantage points.

## Impact

- Better tool choice for Tor, VPN, messaging, and compartmentalization.
- Fewer overbroad claims like "anonymous" or "private" without context.
- Better separation of local-network privacy from destination unlinkability.
- More realistic expectations about what logs, files, and behavior can reveal.
- Better operational decisions around login, files, and cross-account reuse.

## Detection and defense

Ordered by effectiveness:

1.
**Name the observer and consequence**
   If those two pieces are missing, the rest of the model is probably not grounded.

2.
**Reduce identity-bearing signals**
   Account reuse, metadata, cookies, browser state, and behavior are often more important than transport.

3.
**Choose controls by observer**
   VPN for local-network privacy, Tor for anonymity, compartmentalization for device isolation, metadata cleaning for file leakage.

4.
**Avoid over-stacking tools**
   Complexity can create more leakage paths than it removes.

### What does not work as a primary defense

- **"Private" is not a threat model.**
- **Encryption alone is not anonymity.**
- **Changing IP alone is not unlinkability.**
- **More tools do not guarantee more safety.**

## Practical labs

### Write an observer matrix

```
Observer:
Can see content:
Can see metadata:
Can see identity:
Can correlate across sessions:
Consequence if linked:
Best control:
```

Do this once per sensitive activity.

### Compare anonymity goals

```
Goal:
Hide from local network:
Hide from ISP:
Hide from destination:
Hide source location:
Resist correlation:
```

The goal tells you which control family matters.

### Separate signal classes

```
Content:
Metadata:
Identity:
Behavior:
Device:
Filesystem:
```

The control should address the right class.

### Revisit after workflow change

```
Changed account?
Changed device?
Changed browser?
Changed network?
Changed file type?
Changed recipient?
```

Any yes answer can change the anonymity model.

## Practical examples

- A journalist uses Tor to reduce destination and local-network correlation risk.
- A traveler uses a VPN to reduce ISP and cafe Wi-Fi visibility.
- A source-sharing workflow also strips metadata because anonymity is lost through files, not just IPs.
- A personal-safety workflow separates devices and accounts to avoid linkage.
- A user combines tools without naming the observer and ends up with a false sense of safety.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[qubes-compartmentalization|Qubes Compartmentalization]]

### Suggested future atomic notes

- threat-observer-matrices
- adversary-capability-grading
- source-protection

## References

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
