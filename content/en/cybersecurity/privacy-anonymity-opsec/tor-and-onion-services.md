---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Tor and Onion Services

## Definition

Tor is an anonymity network that routes traffic through multiple relays to reduce linkability between a user and a destination. Onion services are services reachable only through Tor, with cryptographic addresses and hidden network locations.

## Why it matters

Tor is not just a slower VPN. A VPN usually asks the user to trust one provider with source and destination metadata. Tor distributes that trust across relays so a single relay should not know both ends of the connection.

Onion services add another important idea: the service operator can hide the server's network location, and the client can authenticate the service through the `.onion` address itself. This is useful for censorship resistance, source protection, sensitive publishing, internal privacy services, and learning how anonymity systems reshape trust boundaries.

## How it works

Use the 5-part Tor model:

1.
**Client builds a circuit**
   Tor Browser chooses relays and builds an encrypted path through the network.

2.
**Each relay knows only its neighbor**
   The entry relay sees the user's IP but not the final destination. The exit relay sees the destination but not the user's IP for normal web traffic.

3.
**The destination sees the exit**
   For ordinary websites, the site sees the Tor exit relay, not the user's source network.

4.
**Onion services avoid public exits**
   Onion service connections stay inside Tor. The client and service meet through Tor circuits rather than exposing the service's public IP.

5.
**The onion address carries cryptographic meaning**
   Modern onion addresses are long because they encode cryptographic identity, not because they are random branding.

Connection sketch:

```
Normal Tor web browsing:
  user -> entry relay -> middle relay -> exit relay -> website

Onion service:
  user -> Tor circuit -> rendezvous point <- Tor circuit <- onion service
```

The bug is not "Tor hides everything." The bug is forgetting that accounts, browser misuse, downloaded files, behavior, and powerful traffic correlation can still matter.

## Techniques / patterns

- Use Tor Browser rather than routing a daily browser through Tor.
- Treat `.onion` addresses as cryptographic service identifiers that must be copied exactly.
- Prefer onion service versions of sensitive services when available and trustworthy.
- Avoid logging into identifying accounts when anonymity is the goal.
- Avoid opening downloaded files outside the protected context.
- Distinguish normal Tor exit browsing from onion service traffic.

## Variants and bypasses

Use the 5 Tor/onion service distinctions:

### 1. Normal web over Tor

The user reaches an ordinary website through a Tor exit relay. The exit sees destination traffic metadata and can see unencrypted HTTP content, while the website sees the exit relay.

### 2. Onion service access

The user reaches a `.onion` service without a public exit relay to the normal web. The service's location is hidden, and Tor Browser can verify the onion service identity through the address.

### 3. Onion-Location discovery

Some normal websites advertise onion counterparts. This can give users a privacy-preserving path to the same service, but users should still verify that the onion service is expected and legitimate.

### 4. Authenticated onion services

Some onion services require client authorization. This protects access to the service but does not automatically make user behavior anonymous inside the application.

### 5. Relay and traffic-correlation limits

Tor distributes trust, but a powerful observer with visibility near both the user and destination may attempt timing correlation. This is a limit to understand, not a reason to treat Tor as useless.

## Impact

- Reduced linkability between user source IP and destination services.
- Service-location hiding for onion service operators.
- Improved censorship resistance where Tor is reachable or bridges are available.
- Increased service friction, blocking, captchas, and speed tradeoffs.
- Risk of deanonymization through account login, browser changes, file handling, and behavior.

## Detection and defense

Ordered by effectiveness:

1.
**Use Tor Browser as the access boundary**
   Tor Browser combines routing, browser hardening, isolation, and anti-fingerprinting behavior. A daily browser routed through Tor usually lacks those protections.

2.
**Keep identities compartmentalized**
   Do not mix real-name accounts, daily browser profiles, personal files, and anonymous research activity. Tor cannot undo application-layer identity.

3.
**Verify onion addresses and service context**
   Onion addresses are long and typo-sensitive. Use trusted sources, bookmarks, or Onion-Location prompts from expected services.

4.
**Prefer HTTPS for normal web exit traffic**
   Tor hides source IP from the destination, but exit relays are still on the path to ordinary HTTP sites. HTTPS remains important.

5.
**Avoid unsafe downloads and external apps**
   Documents opened outside Tor Browser can make network requests or expose local metadata. Treat downloads as a boundary-crossing event.

6.
**Understand local visibility**
   A local network or ISP may see Tor use unless bridges or transports are used. That visibility can itself matter in some environments.

### What does not work as a primary defense

- **Tor plus real-name login is not anonymity.** The destination knows the account.
- **A daily browser through Tor is not Tor Browser.** Browser fingerprinting and state isolation are different layers.
- **An onion address does not make a service trustworthy.** It authenticates the service location, not the operator's behavior.
- **Tor does not protect against endpoint compromise.** Malware or managed-device monitoring can observe activity before or after Tor.

## Practical labs

### Build a Tor observer table

```
Observer                Normal web over Tor          Onion service
Local network/ISP
Entry relay
Middle relay
Exit relay
Destination website
Onion service operator
Browser/account layer
```

The table should show why onion services and normal Tor browsing have different observer models.

### Verify onion address handling

```
Service:
Source of onion address:
Address length:
Bookmarked:
Tor Browser onion icon state:
Account used:
Files downloaded:
```

This prevents copy/paste mistakes and account-layer confusion.

### Compare normal and onion service routing conceptually

```
Normal site:
  Need exit relay: yes
  Website sees Tor exit: yes
  Server IP public: yes

Onion service:
  Need exit relay: no
  Website sees Tor exit: no
  Server IP public: no
```

The comparison is enough for most defensive notes without running active probes.

### Record a safe download decision

```
Downloaded file:
Source:
Open inside Tor context:
Open outside Tor context:
Network access risk:
Metadata risk:
Decision:
```

Downloaded files are one of the easiest ways to cross an anonymity boundary by accident.

## Practical examples

- A news organization offers an onion service to reduce censorship and protect source access.
- A user visits an ordinary website over Tor but logs into a personal account, removing anonymity from that site.
- An operator hosts a sensitive service as an onion service to avoid exposing its origin IP.
- A user opens a downloaded document in a normal office suite, allowing external resources or metadata to escape the Tor context.
- A local network blocks public Tor relays, pushing the user toward bridges or pluggable transports.

## Related notes

- [[vpn-vs-tor|VPN vs Tor]]
- [[vpn-with-tor|VPN with Tor]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tls-https|TLS / HTTPS]]

### Suggested future atomic notes

- [[tor-bridges-and-pluggable-transports]]
- [[traffic-correlation]]
- onion-service-operations
- tor-download-safety

## References

- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Official Tool Docs:** Tor Browser: Onion Services - https://support.torproject.org/tor-browser/features/onion-services/
- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
