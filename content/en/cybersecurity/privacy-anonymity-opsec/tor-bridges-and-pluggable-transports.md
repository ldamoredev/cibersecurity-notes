---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Tor Bridges and Pluggable Transports

## Definition

Tor bridges are Tor relays that are not listed in the public relay directory. Pluggable transports transform Tor traffic so it is harder for a censor or network filter to recognize and block.

## Why it matters

Direct Tor use can be visible and blocked. In some networks, the risk is not only that a site sees Tor exit traffic, but that the local ISP, school, employer, or national firewall sees a Tor connection attempt.

Bridges and transports are circumvention tools. They do not make account logins anonymous, remove browser fingerprints, or defeat endpoint compromise. They change the first-hop reachability and detectability problem.

## How it works

Use the 4-stage circumvention model:

1.
**Direct Tor attempt**
   Tor Browser tries to connect to known public Tor relays.

2.
**Blocking or detection**
   A network blocks public relay IPs, detects Tor handshakes, filters known bridges, or interferes with traffic patterns.

3.
**Bridge selection**
   The user obtains a bridge from Tor Browser, bridges.torproject.org, a bot, or a trusted private source.

4.
**Transport camouflage**
   A pluggable transport such as obfs4, Snowflake, meek, or WebTunnel changes how the traffic appears on the local network.

Sketch:

```
Without bridge:
  user -> public Tor relay -> Tor network

With bridge/transport:
  user -> bridge using transport -> Tor network
```

The bug is not needing a bridge. The bug is assuming a bridge solves identity, browser, account, or behavior leakage.

## Techniques / patterns

- Try Tor Browser Connection Assist first.
- Use built-in bridge options before complex manual configuration.
- Match bridge type to local blocking conditions.
- Keep private bridges private; broad sharing makes them easier to block.
- Record which network, country, ISP, and transport were tested.
- Avoid treating circumvention success as anonymity success.

## Variants and bypasses

Use the 5 bridge/transport patterns:

### 1. Built-in bridges

Tor Browser includes bridge options that are easy to try. They are convenient, but public knowledge can make them more blockable in heavily censored networks.

### 2. Requested bridges

BridgeDB, bots, and support channels can provide bridge lines. The distribution channel matters because censors also try to discover bridges.

### 3. obfs4

obfs4 is widely used to make Tor traffic harder to identify. It can still be blocked when censors discover specific bridge endpoints or fingerprint traffic patterns.

### 4. Snowflake

Snowflake uses volunteer proxies to help users reach Tor. It can be useful where static bridge blocking is strong, but reliability can vary.

### 5. WebTunnel and meek-style camouflage

These transports try to make traffic resemble ordinary web traffic or use domain/fronting-like behavior. They can help in some regions but may be slower or more fragile.

## Impact

- Ability to reach Tor where direct Tor is blocked.
- Reduced local visibility of obvious public Tor relay connections.
- New operational dependency on bridge secrecy, availability, and distribution channels.
- Potential increased attention if bridge discovery, support requests, or unusual traffic patterns are monitored.
- False confidence if users treat censorship circumvention as complete anonymity.

## Detection and defense

Ordered by effectiveness:

1.
**Use the simplest working bridge path**
   Prefer the least complex configuration that works in the user's network. Complexity increases support burden and user error.

2.
**Use official bridge acquisition paths**
   Official Tor channels reduce the chance of malicious or stale bridge information.

3.
**Keep private bridge lines private**
   A bridge shared widely becomes easier to enumerate and block. Treat private bridge details as sensitive.

4.
**Document network-specific behavior**
   Censorship varies by ISP, country, time, and device. Record conditions instead of assuming one transport works everywhere.

5.
**Maintain OPSEC beyond connection success**
   Once Tor connects, account, file, browser, and behavior risks still need separate controls.

### What does not work as a primary defense

- **A bridge is not an anonymity upgrade by itself.** It primarily changes reachability and local detectability.
- **Publicly posting private bridges defeats their purpose.** Censors can collect the same bridge information.
- **One successful connection does not prove resilience.** Censorship systems adapt and network conditions change.
- **A transport does not protect against account login.** The destination can still identify the account.

## Practical labs

### Build a circumvention decision card

```
Network:
Country/region:
Direct Tor works:
Connection Assist tried:
Built-in bridge tried:
Requested bridge tried:
Transport:
Error message:
Result:
Risk of visible Tor use:
```

The card keeps troubleshooting tied to the actual network and risk.

### Compare direct and bridge attempts

```
Attempt 1: Direct Tor
Result:
Error:

Attempt 2: Built-in bridge
Transport:
Result:
Error:

Attempt 3: Requested bridge
Source:
Transport:
Result:
Error:
```

Use this only where testing Tor is legal and safe for the user.

### Protect private bridge information

```
Bridge source:
Who received it:
Where stored:
Shared over:
Expiration/rotation:
Leak consequence:
```

Private bridge handling is an OPSEC problem, not just a connection setting.

### Separate circumvention from anonymity

```
Connection problem solved:
Still logged into identifying account:
Browser changed/customized:
Files downloaded/opened:
Files uploaded:
Behavior link risk:
```

This prevents "Tor connected" from becoming "identity protected."

## Practical examples

- A user in a censored region cannot connect directly and uses WebTunnel bridges.
- A school network blocks known Tor relay IPs, but a built-in bridge connects.
- A private bridge stops working after being shared in a public forum.
- A user reaches Tor through Snowflake but logs into a real-name account.
- A support team collects network-specific errors to identify which transports work in a region.

## Related notes

- [[tor-and-onion-services|Tor and Onion Services]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[vpn-with-tor|VPN with Tor]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Suggested future atomic notes

- snowflake
- webtunnel
- obfs4
- censorship-measurement

## References

- **Official Tool Docs:** Tor Browser Censorship Circumvention - https://support.torproject.org/tor-browser/circumvention/
- **Official Tool Docs:** Tor: Using Bridges - https://support.torproject.org/little-t-tor/circumvention/using-bridges/
- **Research / Deep Dive:** Tor Project Anti-censorship - https://community.torproject.org/anti-censorship/
