---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Tor Browser Security Settings

## Definition

Tor Browser security settings are built-in controls that trade web compatibility for reduced attack surface and stronger anonymity-preserving browser behavior.

## Why it matters

Tor Browser is more than Firefox pointed at Tor. Its value comes from the combination of Tor routing, browser fingerprint resistance, state isolation, safer defaults, and security levels that can disable risky web features.

Changing settings casually can make a user more unique. The goal is not maximum customization; it is staying inside a large, predictable anonymity set while raising security level when the activity justifies the usability cost.

## How it works

Use the 4-control model:

1.
**Security level**
   Standard, Safer, and Safest disable progressively more web features. Higher levels can break pages but reduce exposure to risky browser features.

2.
**Fingerprinting protections**
   Tor Browser tries to make users look similar through defenses such as first-party isolation, user-agent behavior, and window-size protections.

3.
**Identity management**
   New Identity and New Tor Circuit controls help separate activity, though they do not erase account decisions already made on a site.

4.
**Extension and plugin restraint**
   Extensions and plugins can create unique fingerprints or bypass Tor Browser protections.

Simple decision table:

```
Need ordinary browsing compatibility: Standard
Need lower script/media/font attack surface: Safer
Need static/basic site access with maximum browser feature reduction: Safest
Need anonymity from destination: avoid account login and customization
```

The bug is not choosing Standard. The bug is assuming Standard plus unsafe account behavior is anonymity.

## Techniques / patterns

- Use Tor Browser defaults unless a threat model calls for higher security level.
- Prefer security-level changes over random about:config hardening.
- Avoid installing browser extensions.
- Avoid resizing and customizing in ways that make the browser stand out.
- Use New Identity when moving between unlinkable activities.
- Keep account identity separate from browsing identity.

## Variants and bypasses

Use the 5 browser-risk classes:

### 1. Script and active-content risk

JavaScript and rich web features can increase attack surface and fingerprinting surface. Higher security levels reduce these features.

### 2. Font, media, and rendering risk

Fonts, icons, media, math symbols, canvas, and rendering differences can help fingerprint a browser or expose attack surface.

### 3. Extension uniqueness

Extensions can add APIs, alter pages, leak data, or make the browser fingerprint unusual. Tor Browser's protection model assumes minimal customization.

### 4. Identity-state leakage

Cookies, sessions, logins, and site storage can link activity. Browser controls help, but logging into an identifying account still identifies the user to that service.

### 5. External application leakage

Opening downloaded files in external apps can bypass Tor Browser and expose network, metadata, or local-device signals.

## Impact

- Reduced browser exploit and fingerprinting surface at higher security levels.
- Lower usability on dynamic sites when risky features are disabled.
- Better compartmentalization when New Identity is used correctly.
- Deanonymization risk when users customize the browser, install extensions, or log into identifying accounts.
- Boundary-crossing risk from downloaded files and helper applications.

## Detection and defense

Ordered by effectiveness:

1.
**Keep Tor Browser close to defaults**
   Defaults are designed for a shared anonymity set. Unique custom settings can weaken anonymity even if they feel more secure.

2.
**Raise security level based on activity risk**
   Safer and Safest reduce exposed browser features. Use them when the consequence of browser exploitation or fingerprinting outweighs site compatibility.

3.
**Avoid extensions and plugins**
   Extensions are high-risk because they change browser behavior and may create unique fingerprints or leak data.

4.
**Use New Identity for activity separation**
   New Identity helps reset state between unrelated activities. It does not make a logged-in account anonymous.

5.
**Treat downloads as boundary crossings**
   Inspect, isolate, or avoid files that need external applications. External apps may connect outside Tor or reveal metadata.

6.
**Do not chase fingerprint test scores by tweaking**
   Random changes can make the browser more unique. Consistency with the Tor Browser population is usually the point.

### What does not work as a primary defense

- **Custom hardening is not automatically better.** Unique settings can create a distinctive fingerprint.
- **Extensions are not harmless.** Even privacy extensions can alter fingerprint and behavior.
- **New Identity does not anonymize real-name logins.** The service still knows the account.
- **A higher security level does not fix OPSEC mistakes.** Files, accounts, behavior, and endpoint compromise remain.

## Practical labs

### Record security-level decision

```
Activity:
Consequence if browser exploited:
Need JavaScript-heavy sites:
Need media/fonts:
Chosen level: Standard / Safer / Safest
Reason:
Retest after breakage:
```

The result ties settings to risk instead of superstition.

### Compare site behavior across levels

```
Site:
Standard works:
Safer works:
Safest works:
Features broken:
Security benefit worth breakage:
```

Use only sites you are allowed to access. The point is learning the compatibility tradeoff.

### Check extension discipline

```
Installed extensions:
Why each is needed:
Could it alter fingerprint:
Could it read pages:
Could it make network requests:
Decision:
```

Most Tor Browser workflows should have no extra extensions.

### Plan identity separation

```
Activity A:
Activity B:
Same account? yes/no
Same site? yes/no
Need New Identity between them? yes/no
Files downloaded? yes/no
External apps opened? yes/no
```

This distinguishes browser state separation from account separation.

## Practical examples

- A user moves from Standard to Safer for sensitive research that only needs simple pages.
- A site breaks under Safest because scripts are disabled; the user documents the compatibility tradeoff.
- A user installs a password-manager extension and becomes more fingerprintable.
- A user opens a downloaded document in a normal PDF reader, crossing out of Tor Browser's protection model.
- A user uses New Identity between unrelated research tasks but avoids logging into identifying accounts.

## Related notes

- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[content-security-policy|Content Security Policy]]

### Suggested future atomic notes

- [[browser-fingerprinting]]
- tor-download-safety
- tor-identity-management
- javascript-and-anonymity

## References

- **Official Tool Docs:** Tor Browser Security Levels - https://support.torproject.org/tor-browser/features/security-levels/
- **Official Tool Docs:** Tor Browser Fingerprinting Protections - https://support.torproject.org/tor-browser/features/fingerprinting-protections/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
