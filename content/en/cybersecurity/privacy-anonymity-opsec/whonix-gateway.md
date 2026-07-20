---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Whonix Gateway

## Definition

Whonix Gateway is the Tor-routing component of Whonix. It is designed to separate Tor network routing from user applications, so application traffic from the workstation is forced through the gateway's Tor path.

## Why it matters

Many anonymity failures happen because applications leak around the intended proxy or VPN. Whonix addresses this by splitting the environment into a gateway and workstation model: applications run in one VM, while Tor routing happens in another.

This is stronger than asking every application to behave correctly, but it still does not solve account identity, file metadata, browser misuse, host compromise, or user behavior.

## How it works

Use the 4-part Whonix model:

1.
**Gateway VM**
   Whonix Gateway connects to Tor and acts as the network path.

2.
**Workstation VM**
   User applications run in a separate workstation that routes through the gateway.

3.
**Network isolation**
   The workstation should not have direct internet access outside the gateway path.

4.
**Host dependency**
   The host OS or hypervisor still matters. A compromised host can undermine VM-level privacy.

Sketch:

```
application -> Whonix Workstation -> Whonix Gateway -> Tor network -> destination
```

The bug is not using a gateway. The bug is assuming gateway routing fixes application identity and file OPSEC.

## Techniques / patterns

- Keep workstation traffic routed only through the gateway.
- Use Whonix with Qubes when stronger compartmentalization is needed.
- Avoid installing unnecessary software in anonymity workstations.
- Keep browser behavior close to Tor Browser expectations.
- Separate identities into separate workstations where needed.
- Treat the host/hypervisor as part of the threat model.
- Use bridges where local Tor visibility matters.

## Variants and bypasses

Use the 6 Whonix boundary classes:

### 1. Gateway/workstation split

The main design boundary separates routing from applications. This reduces accidental direct connections from applications.

### 2. Host compromise

The host can observe or manipulate VMs if compromised. Whonix is not a defense against all host-level attackers.

### 3. Application-layer identity

Applications can still reveal identity through logins, telemetry, files, and behavior. Routing cannot remove that layer.

### 4. Browser fingerprinting

Using nonstandard browsers or adding extensions can make the user stand out even when traffic routes through Tor.

### 5. Multi-workstation compartmentalization

Separate workstations can isolate identities and tasks, especially with Qubes-Whonix. The separation only works if data movement is controlled.

### 6. Local Tor visibility

The local network may see Tor use unless bridges or transports are configured.

## Impact

- Stronger containment against direct application network leaks.
- Better separation between routing and user applications.
- Useful integration with Qubes compartmentalization.
- Continued risk from host compromise, account login, files, and behavior.
- More operational complexity than Tor Browser alone or Tails.

## Detection and defense

Ordered by effectiveness:

1.
**Preserve the gateway-only route**
   The workstation should not have an alternate direct network path. The architecture matters only if traffic cannot bypass it.

2.
**Separate identities into separate workstations**
   Different identities should not share files, browser state, or application data when unlinkability matters.

3.
**Use Qubes-Whonix for stronger compartments**
   Qubes adds a broader compartment model around Whonix routing, which can reduce blast radius when used carefully.

4.
**Keep host security in scope**
   Patch the host, limit risky host activity, and understand that VM isolation depends on the host and hypervisor.

5.
**Maintain browser and file discipline**
   Use Tor Browser behavior, avoid identifying logins, and inspect files. Gateway routing cannot fix payload-layer leaks.

### What does not work as a primary defense

- **Gateway routing is not identity removal.** Accounts and behavior still identify users.
- **Whonix is not host-compromise protection.** The host remains a critical trust point.
- **Multiple workstations are not separation if files are freely shared.** Transfers can reconnect identities.
- **Tor routing does not clean metadata.** File inspection and cleaning remain separate tasks.

## Practical labs

### Map Whonix boundaries

```
Host OS:
Hypervisor:
Gateway:
Workstation:
Network path:
Direct internet path possible:
Accounts used:
Files moved in/out:
```

This makes the trust boundary explicit.

### Build an identity workstation plan

```
Identity/task:
Workstation:
Gateway:
Shared folders:
Clipboard policy:
Files imported:
Files exported:
Browser changes:
```

The plan prevents all identities from collapsing into one workstation.

### Review bypass assumptions

```
Application:
Needs network:
Can reach only gateway:
Uses system proxy:
Has telemetry:
Stores account data:
File metadata risk:
```

This separates network containment from application behavior.

### Compare Whonix to VPN

```
Question                         VPN              Whonix
Single provider trust:
Tor routing:
App direct leak resistance:
Browser fingerprint solved:
Account login solved:
Host compromise solved:
```

The table keeps Whonix in the right threat-model slot.

## Practical examples

- A user routes a research workstation through Whonix Gateway to prevent direct app connections.
- A Qubes user runs separate Whonix workstations for separate identities.
- A non-browser app sends telemetry through Tor but still includes account identifiers.
- A compromised host observes VM activity despite Whonix routing.
- A user copies files between workstations, linking identities that were otherwise separated.

## Related notes

- [[qubes-compartmentalization|Qubes Compartmentalization]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[tor-bridges-and-pluggable-transports|Tor Bridges and Pluggable Transports]]
- [[file-metadata-removal|File Metadata Removal]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

### Suggested future atomic notes

- qubes-whonix
- whonix-workstation
- tor-gateway-leakage
- host-compromise-limits

## References

- **Official Tool Docs:** Whonix documentation - https://www.whonix.org/wiki/Documentation
- **Official Tool Docs:** Whonix Gateway - https://www.whonix.org/wiki/Whonix-Gateway
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
