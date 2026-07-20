---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN with Tor

## Definition

VPN with Tor means combining a VPN and Tor in one workflow, usually as Tor over VPN or VPN over Tor. Combining them changes the trust and visibility model; it does not automatically make a user more anonymous.

## Why it matters

Tool stacking feels comforting, but anonymity systems punish unnecessary complexity. A VPN may hide Tor use from a local network, or it may add a provider that sees the user's source IP. A VPN after Tor may hide Tor exit use from a destination, or it may force the user into fragile custom routing.

The Tor Project generally does not recommend VPN-with-Tor for ordinary users unless they understand the configuration and privacy consequences. The right question is: what observer changes, and what new failure modes appear?

## How it works

Use the 3-route model:

1.
**Tor alone**
   The local network sees Tor use. The entry relay sees the source IP. The destination sees a Tor exit or onion-service path.

2.
**Tor over VPN**
   The user connects to a VPN first, then uses Tor Browser. The local network sees VPN use, the VPN provider sees source IP and Tor entry connection, and Tor sees the VPN exit as the apparent source.

3.
**VPN over Tor**
   The user connects to Tor first, then routes a VPN through Tor. This is harder to configure, often fragile, and can reduce Tor's normal protections if done badly.

Visibility sketch:

```
Tor alone:
  local network -> Tor entry -> Tor network -> destination

Tor over VPN:
  local network -> VPN provider -> Tor entry -> Tor network -> destination

VPN over Tor:
  local network -> Tor entry -> Tor network -> VPN provider -> destination
```

The bug is not combining tools. The bug is combining tools without being able to explain the new observer table.

## Techniques / patterns

- Prefer Tor Browser alone unless the threat model clearly requires hiding Tor use from the local network.
- Use Tor over VPN only when the VPN provider trust tradeoff is understood.
- Treat VPN over Tor as advanced and fragile.
- Avoid account login and browser customization regardless of routing stack.
- Test DNS, IPv6, and app routing when a VPN is involved.
- Write down who sees source IP, Tor use, destination, and account identity.

## Variants and bypasses

Use the 5 composition cases:

### 1. Tor alone

Simplest Tor model. Local network visibility of Tor use may be acceptable in many places. Fewer moving parts means fewer accidental routing mistakes.

### 2. Tor over VPN

Useful when local Tor visibility is a concern or Tor access is blocked but a VPN is allowed. The VPN provider becomes an additional trust point and can see that the user is connecting to Tor.

### 3. VPN over Tor

Sometimes proposed to hide Tor exit use from destinations, but it is difficult and can reduce anonymity if authentication, payment, static exit IP, or routing behavior creates a stable identity.

### 4. VPN plus Tor Browser misuse

The user runs Tor Browser but logs into personal accounts, installs extensions, opens files externally, or uses the same persona. Routing composition cannot fix identity behavior.

### 5. Split-routing confusion

Some traffic uses the VPN, some uses Tor, and some uses the normal network. This can expose activity when the user assumes everything follows one path.

## Impact

- Possible reduction of local-network visibility into Tor use.
- Additional VPN-provider trust and logging surface.
- More complex routing and leak testing requirements.
- Higher chance of OPSEC mistakes from misunderstanding the path.
- Potential service compatibility changes depending on whether destinations see Tor or VPN exits.

## Detection and defense

Ordered by effectiveness:

1.
**Use the simplest model that satisfies the threat model**
   Tor alone is often easier to reason about than a stacked setup. Simplicity is a security control when anonymity depends on behavior.

2.
**Write an observer table before combining**
   List what the local network, ISP, VPN provider, Tor entry, Tor exit, destination, and account provider can see. If the table is unclear, the setup is not ready.

3.
**Avoid identifying accounts and stable payments**
   A VPN account, payment record, or destination login can become the strongest identity signal in the chain.

4.
**Keep Tor Browser protections intact**
   Do not replace Tor Browser with a daily browser through a VPN/Tor route. Browser behavior is part of the anonymity model.

5.
**Test leaks after every routing change**
   DNS, IPv6, app bypass, and reconnect behavior can change when VPNs and Tor are combined.

### What does not work as a primary defense

- **More hops does not mean more anonymity.** The trust model matters more than the count of tools.
- **Tor over VPN does not make the VPN disappear.** The VPN provider still sees the source IP and Tor connection.
- **VPN over Tor is not beginner hardening.** It can create a stable VPN identity after Tor.
- **Stacking tools does not fix account correlation.** The destination still knows a logged-in account.

## Practical labs

### Build a composition observer table

```
Workflow: Tor alone / Tor over VPN / VPN over Tor

Observer             Source IP?      Tor use?      Destination?      Account?
Local network
ISP
VPN provider
Tor entry
Tor exit
Destination service
Account provider
```

If this table cannot be filled out, the setup is too murky for serious use.

### Compare route intent

```
Goal:
Hide Tor use from local network:
Hide source IP from VPN provider:
Hide Tor exit use from destination:
Avoid single-provider trust:
Need speed:
Need account login:
Chosen model:
```

The result should expose tradeoffs, not just pick the most complicated setup.

### Check leak surfaces after adding VPN

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
dig o-o.myaddr.l.google.com TXT @ns1.google.com
```

Use only for your own device and network. This checks visible IP and resolver path, not full anonymity.

### Record failure modes

```
Failure mode                  Expected behavior        Tested?
VPN disconnects
Tor Browser closed
Device sleeps/wakes
Captive portal appears
DNS changes
IPv6 route appears
External app opens file
```

Tool stacking increases failure modes; the table makes them operational.

## Practical examples

- A user in a network that blocks Tor uses a VPN first, then Tor Browser, and accepts VPN-provider visibility.
- A user adds a VPN to Tor but logs into a personal account, making the route irrelevant to the service.
- A custom VPN-over-Tor setup creates a stable VPN account identity visible to destinations.
- A researcher chooses Tor alone because local Tor use is not risky and fewer moving parts are safer.
- A mobile device reconnects VPN and Tor inconsistently after sleep, changing the assumed path.

## Related notes

- [[vpn-vs-tor|VPN vs Tor]]
- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-leakage-risks|VPN Leakage Risks]]

### Suggested future atomic notes

- [[tor-bridges-and-pluggable-transports]]
- [[traffic-correlation]]
- [[vpn-kill-switches]]
- [[account-correlation]]

## References

- **Official Tool Docs:** Tor Project: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
