---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN vs Tor

## Definition

VPNs are privacy-routing tools that shift network-path trust to a provider. Tor is an anonymity network designed to distribute trust across relays and reduce linkability between source and destination.

VPNs and Tor overlap, but they are not equivalent.

## Why it matters

The phrase "hide my IP" makes VPNs and Tor sound similar. Their threat models are different.

A VPN usually trusts one provider that can see the user's source IP and traffic metadata. Tor is designed so no single relay should know both who the user is and what destination they are visiting, although Tor has its own performance, blocking, usability, and correlation limits.

Strong sentence: VPNs are privacy tools. Tor is an anonymity network.

## How it works

Use the 4-observer comparison:

1.
**Local network and ISP**
   Both VPN and Tor can reduce direct visibility into final destinations. They still reveal that the user is connecting to a VPN server or Tor entry/bridge unless disguised by other mechanisms.

2.
**Routing provider**
   A VPN provider can usually see the user's source IP and destination metadata. Tor distributes trust across entry, middle, and exit relays so one relay should not see the whole path.

3.
**Destination website**
   A website sees the VPN exit IP or Tor exit IP. It may still identify the user through login, cookies, browser fingerprinting, behavior, or submitted content.

4.
**Global or powerful observer**
   Tor is stronger than a VPN against a single provider observer, but traffic correlation by a powerful observer watching both ends remains a known anonymity limit.

Comparison table:

```
Property                  VPN                           Tor
Primary goal              privacy routing               anonymity network
Trust model               one provider                  distributed relays
Source IP at first hop    VPN provider sees it          entry/bridge sees it
Destination at exit       VPN provider may see it       exit sees destination, not source
Speed                     usually faster                usually slower
Blocking                  less blocked                  more blocked by some services
Browser discipline        still important               essential
Best fit                  hostile Wi-Fi, ISP privacy    anonymity and unlinkability
```

The bug is not choosing the wrong tool universally. The bug is choosing without naming the observer.

## Techniques / patterns

- Use VPNs when the main concern is local network, ISP visibility, hostile Wi-Fi, or corporate/private-network access.
- Use Tor Browser when the main concern is anonymity from destination services and single-provider trust.
- Avoid logging into identifying accounts when anonymity matters.
- Do not customize Tor Browser casually; uniqueness weakens the anonymity set.
- Treat VPN plus Tor as a changed trust model, not automatic improvement.
- Separate speed/convenience goals from anonymity goals.

## Variants and bypasses

Use the 6 comparison dimensions:

### 1. Trust concentration

A VPN concentrates trust in one provider. Tor distributes trust across relays so no single relay should see both source and destination.

### 2. Browser fingerprinting

A VPN changes the network path but leaves the browser mostly unchanged. Tor Browser is designed to reduce fingerprint uniqueness, but user changes and account logins can defeat that.

### 3. Exit reputation

VPN exits may be accepted by more services, depending on provider reputation. Tor exits are often blocked, rate-limited, or challenged because they are public anonymity infrastructure.

### 4. Performance

VPNs are usually faster because traffic takes a shorter path through one provider. Tor is slower because traffic is routed through multiple relays and prioritizes anonymity properties.

### 5. Censorship and blocking

VPNs may bypass some network blocks but can also be blocked. Tor bridges and pluggable transports are designed for censorship resistance, but configuration and local risk matter.

### 6. Legal and organizational context

Corporate VPNs are often monitored access-control infrastructure. Tor use may be suspicious in some environments. Tool choice should consider local rules, safety, and authorization.

## Impact

- Better tool selection for ISP privacy, hostile networks, censorship, anonymity, and corporate access.
- Reduced false confidence from treating VPNs as anonymity tools.
- Better understanding of why Tor Browser behavior matters.
- Avoidance of unnecessary complexity from stacking VPN and Tor without a clear reason.
- Clearer communication in reports, labs, and personal threat models.

## Detection and defense

Ordered by effectiveness:

1.
**Choose based on observer and consequence**
   If the main observer is a hostile local network or ISP, a trustworthy VPN may be enough. If the main problem is unlinkability from destination services or single-provider trust, Tor is usually the more relevant tool.

2.
**Use Tor Browser as designed when anonymity matters**
   Tor's anonymity set depends on users looking similar. Extensions, resizing, custom fonts, unusual settings, and real-name logins can undermine that.

3.
**Use VPNs for routing privacy, not identity erasure**
   A VPN can hide destination metadata from the local network or ISP, but the provider and destination-service signals still matter.

4.
**Avoid account and behavior linkage**
   Neither VPN nor Tor protects anonymity if the user logs into identifying accounts, uploads identifying files, or repeats linkable behavior.

5.
**Document combined-tool choices**
   Tor over VPN and VPN over Tor each change who sees what. Complexity can create operational mistakes, so write the trust model down.

### What does not work as a primary defense

- **VPN is not Tor-lite.** It shifts trust to a provider and does not provide Tor's distributed relay model.
- **Tor is not magic invisibility.** Browser misuse, accounts, files, behavior, and powerful traffic correlation can still matter.
- **Combining VPN and Tor is not automatically stronger.** It may add complexity and new failure modes.
- **Changing IP is not unlinkability.** Cookies, logins, fingerprints, and behavior may still connect sessions.

## Practical labs

### Build an observer table

```
Scenario:
Tool: VPN / Tor / neither

Observer              What they see                         Residual risk
Local Wi-Fi
ISP
VPN provider
Tor entry/bridge
Tor exit
Destination website
Account provider
Device/browser
```

The table makes the trust model visible before tool choice hardens into habit.

### Compare apparent source IP

```
curl -4 https://ifconfig.me
```

Run without VPN, with VPN, and from inside a Tor-capable environment where appropriate. Do not treat source-IP change as anonymity proof.

### Compare browser identity risk

```
Open a fingerprinting test in:
1. daily browser over VPN
2. clean browser profile over VPN
3. Tor Browser

Compare:
- account login state
- timezone/language
- screen size
- extension list
- fingerprint warning or uniqueness result
```

The lesson is that VPN and browser anonymity are different layers.

### Decide between VPN and Tor

```
Goal:
Primary observer:
Consequence if linked:
Need speed:
Need login:
Need anonymity from destination:
Risk if Tor is visible:
Recommended tool:
Reason:
```

This prevents "more tools" from replacing threat-model reasoning.

### Record service compatibility

```
Service:
VPN allowed:
Tor allowed:
Captchas/challenges:
Account lock risk:
Terms or policy issue:
Alternative workflow:
```

Anonymity tools interact with service anti-abuse systems; that operational reality belongs in the plan.

## Practical examples

- A traveler uses a VPN on hotel Wi-Fi to reduce local-network metadata exposure.
- A researcher uses Tor Browser to avoid trusting a single VPN provider with source and destination metadata.
- A user logs into a personal account over Tor, making the session identifiable to the service.
- A company VPN routes all traffic through monitored corporate infrastructure for access control.
- A user stacks VPN and Tor but creates mistakes because they cannot explain who now sees which traffic.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]

### Suggested future atomic notes

- [[tor-and-onion-services]]
- [[tor-browser-security-settings]]
- [[tor-bridges-and-pluggable-transports]]
- [[vpn-with-tor]]
- [[traffic-correlation]]

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Official Tool Docs:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
