---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Browser Fingerprinting

## Definition

Browser fingerprinting is the identification or correlation of a browser through stable characteristics such as user agent, fonts, extensions, rendering behavior, screen size, timezone, language, and feature support.

## Why it matters

Changing the IP address does not change the browser. Sites can still correlate users through application-layer characteristics even when a VPN or Tor changes the network path.

## How it works

Use the 5-signal browser model:

1.
**Declared identity**
   User agent and platform hints.

2.
**Rendering identity**
   Canvas, WebGL, fonts, CSS behavior, and layout quirks.

3.
**Environment identity**
   Screen size, timezone, language, hardware features, and OS behavior.

4.
**State identity**
   Cookies, local storage, history, and login state.

5.
**Behavior identity**
   How the browser is used and which pages or actions appear.

The bug is not that browsers can be identified. The bug is pretending IP masking solves browser uniqueness.

## Techniques / patterns

- Reduce browser customizations when anonymity matters.
- Prefer anti-fingerprinting browsers for sensitive use.
- Keep profiles separate.
- Avoid plugins and extensions that change browser behavior.
- Test fingerprint surfaces after updates.
- Separate browser identity from account identity.

## Variants and bypasses

Use the 6 fingerprint vectors:

### 1. Headers and user agent

Basic browser and OS declarations.

### 2. Rendering surfaces

Canvas, WebGL, fonts, media, CSS, and timing.

### 3. Extension footprint

Installed extensions can be highly identifying.

### 4. Window and device shape

Screen size, DPI, touch support, and hardware hints.

### 5. Storage state

Cookies, local storage, and session state link visits.

### 6. Behavioral patterns

How the browser is used can be as identifying as static properties.

## Impact

- Correlation across sessions and sites.
- Degraded anonymity even when transport privacy is strong.
- Site-side tracking that survives IP changes.
- Higher uniqueness from heavy customization.
- False confidence when using a normal browser through a VPN.

## Detection and defense

Ordered by effectiveness:

1.
**Use anti-fingerprinting browsers for anonymity tasks**
   Tor Browser is designed to reduce uniqueness.

2.
**Keep browsers boring**
   Fewer extensions and fewer custom tweaks generally mean fewer fingerprints.

3.
**Separate identities by browser profile**
   One profile should not hold multiple personas.

4.
**Limit storage state**
   Clear or avoid cookies and site storage when unlinkability matters.

5.
**Retest regularly**
   Browser and OS updates can change the fingerprint.

### What does not work as a primary defense

- **A VPN does not stop browser fingerprinting.**
- **Private mode is not a fingerprinting defense.**
- **More extensions are usually worse, not better.**
- **Random customizations can make the browser more unique.**

## Practical labs

### Inventory fingerprint surfaces

```
Browser:
Profile:
User agent:
Timezone:
Language:
Extensions:
Fonts:
Screen size:
Cookies:
Login state:
```

This shows how much is visible before any network request.

### Compare profiles

```
Daily browser:
Clean profile:
Anti-fingerprinting browser:

Differences:
- extensions
- storage state
- customization
- login state
```

This makes browser uniqueness easier to see.

### Review extension risk

```
Extension:
Needed:
Changes pages:
Reads page content:
Creates unique behavior:
Keep or remove:
```

Extensions are often the fastest way to stand out.

### Check after update

```
Update:
What changed:
Fingerprint site result:
New uniqueness?
```

Post-update retesting should be routine.

## Practical examples

- A Tor Browser user avoids extra extensions to keep the browser in the shared anonymity set.
- A normal browser through a VPN still reveals the same extension set and window size.
- A custom font pack makes a browser easier to identify.
- A site reuses cookies even though the IP address changed.
- A browser profile dedicated to one persona avoids cross-linkage.

## Related notes

- [[vpn-fingerprinting-limitations|VPN Fingerprinting Limitations]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[session-management|Session Management]]

### Suggested future atomic notes

- canvas-fingerprinting
- extension-risk
- browser-state-isolation

## References

- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
