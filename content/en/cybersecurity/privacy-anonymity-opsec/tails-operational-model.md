---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Tails Operational Model

## Definition

Tails is a portable operating system designed to route internet activity through Tor and reduce traces on the computer it runs on. Its security model is operational: it helps create a temporary, Tor-centered session, but it is not magic.

## Why it matters

Tails is useful when the operating environment matters as much as the browser. It can reduce traces on a borrowed or shared computer, provide a consistent Tor-oriented toolset, and help avoid using a daily OS for sensitive work.

But Tails does not protect against every threat. It cannot fix unsafe account behavior, file metadata, compromised firmware, malicious hardware, physical surveillance, or a user mixing multiple identities in one session.

## How it works

Use the 5-part Tails model:

1.
**Boot into a separate operating system**
   Tails runs independently from the usual installed OS.

2.
**Use Tor by default**
   Internet applications are designed to use Tor rather than the normal network path.

3.
**Leave less local state**
   Tails is built for temporary sessions. Persistence is optional and must be configured intentionally.

4.
**Bundle privacy tools**
   Tails includes tools for Tor browsing, file handling, encryption, metadata cleaning, and secure deletion workflows.

5.
**Depend on user discipline**
   The session boundary fails if the user logs into identifying accounts, reuses files, or mixes purposes.

Session sketch:

```
usual OS off
Tails booted from USB
network connects
Tor connects
activity happens inside temporary session
shutdown clears non-persistent state
```

The bug is not using persistence or files. The bug is using them without recognizing they become identity links.

## Techniques / patterns

- Use one Tails session for one purpose when unlinkability matters.
- Restart between unrelated identities or activities.
- Clean metadata before sharing files.
- Avoid plugging the Tails USB into a running untrusted OS for file transfer.
- Treat Persistent Storage as sensitive and linkable.
- Verify Tails installation and updates from trusted sources.
- Remember that local observers may still see Tor or Tails use.

## Variants and bypasses

Use the 6 operational boundaries:

### 1. Temporary session boundary

Tails reduces leftover state after shutdown. This helps with local traces but does not erase activity recorded by websites, accounts, networks, or recipients.

### 2. Persistent Storage boundary

Persistence is useful for keys, documents, and settings, but it can link sessions and identities if reused carelessly.

### 3. Tor visibility boundary

Tails routes through Tor, but the local network may see Tor use unless bridges are used. Destination sites may see Tor exit traffic.

### 4. File boundary

Files can carry metadata into or out of Tails. Cleaning and verifying files remains necessary.

### 5. Hardware boundary

Tails cannot reliably protect against compromised firmware, malicious peripherals, hardware implants, or physical observation.

### 6. Activity boundary

Using the same session for multiple identities can link them through circuits, files, timing, accounts, or browser state.

## Impact

- Reduced dependence on a daily OS for sensitive activity.
- Lower local-trace risk after shutdown when persistence is not used.
- Stronger workflow discipline for Tor-centered tasks.
- Risk of false confidence if Tails is treated as complete anonymity.
- Linkage risk through persistence, account login, metadata, and mixed-purpose sessions.

## Detection and defense

Ordered by effectiveness:

1.
**Define the purpose before booting**
   A Tails session should have one operational purpose. Mixing work email, personal accounts, and sensitive research in one session weakens the boundary.

2.
**Restart between unlinkable activities**
   Restarting is a simple, strong separation control. It clears session state that users often forget exists.

3.
**Use Persistent Storage sparingly**
   Persist only what the workflow needs. Treat persistent files, keys, and settings as possible links across sessions.

4.
**Clean and verify files**
   Tails includes metadata-cleaning workflows, but users must still inspect and verify outputs.

5.
**Use bridges when local Tor visibility matters**
   Tails using Tor may be visible to the local network. Bridges address that specific observer.

6.
**Respect hardware limits**
   Use trusted hardware when the adversary could affect firmware, peripherals, or physical observation.

### What does not work as a primary defense

- **Tails is not magic.** It cannot protect against every software, hardware, network, and behavior risk.
- **Persistence is not neutral.** It improves usability while creating linkage and storage risk.
- **Tor routing does not clean files.** Metadata remains unless handled separately.
- **One session for many identities weakens compartmentalization.** Restart or separate media when the identities must stay apart.

## Practical labs

### Plan a Tails session

```
Purpose:
Accounts needed:
Files needed:
Persistent Storage needed:
Bridge needed:
Metadata cleaning needed:
Shutdown criteria:
Do not mix with:
```

The plan prevents a temporary OS from becoming an improvised daily environment.

### Review persistence risk

```
Persistent item:
Why needed:
Could link identities:
Could expose real name:
Backup location:
Deletion plan:
```

Persistence should earn its place.

### Build a file movement record

```
File:
Source device:
Destination:
Metadata inspected:
Metadata cleaned:
Opened outside Tails:
Remaining risk:
```

File movement is a common place where Tails boundaries blur.

### Separate two activities

```
Activity A:
Activity B:
Shared accounts:
Shared files:
Shared persistence:
Need restart between them:
Need separate USB:
```

The result should make identity linkage explicit.

## Practical examples

- A user boots Tails for a single sensitive research task and shuts down afterward.
- A journalist uses Persistent Storage for keys but keeps source identities on separate Tails media.
- A user uploads a document through Tails but forgets to remove author metadata.
- A local network sees Tor use from Tails, prompting bridge use in a higher-risk environment.
- A user logs into personal and pseudonymous accounts in one session, weakening separation.

## Related notes

- [[tor-and-onion-services|Tor and Onion Services]]
- [[tor-bridges-and-pluggable-transports|Tor Bridges and Pluggable Transports]]
- [[file-metadata-removal|File Metadata Removal]]
- [[secure-file-sharing|Secure File Sharing]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

### Suggested future atomic notes

- tails-persistent-storage
- tails-session-separation
- tails-install-verification
- [[secure-deletion-and-storage-wiping]]

## References

- **Official Tool Docs:** Tails documentation - https://tails.net/doc/
- **Official Tool Docs:** Tails warnings - https://tails.net/doc/about/warnings/
- **Official Tool Docs:** Tor Browser User Manual - https://tb-manual.torproject.org/
