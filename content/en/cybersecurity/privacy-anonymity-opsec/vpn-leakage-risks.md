---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN Leakage Risks

## Definition

VPN leakage risks are identity, routing, resolver, browser, application, file, and behavior signals that escape or bypass the expected VPN privacy model.

## Why it matters

The VPN tunnel can be working correctly while the user still leaks identity through the browser, operating system, accounts, files, or behavior.

A leak is not always a broken tunnel. Sometimes it is a correct tunnel surrounded by uncontrolled identifiers: a real-name login, browser fingerprint, DNS resolver mismatch, IPv6 path, WebRTC candidate, split-tunnel app, uploaded document metadata, or repeated posting pattern.

## How it works

Use the 7-layer leakage model:

1.
**Route leaks**
   Traffic takes the normal network path instead of the VPN path.

2.
**Resolver leaks**
   DNS lookups leave through an unexpected resolver, often the ISP, local network, or browser-specific DNS path.

3.
**Address-family leaks**
   IPv4 goes through the VPN while IPv6 uses the normal network path.

4.
**Browser leaks**
   Cookies, fingerprints, WebRTC, timezone, language, and extensions identify or correlate the user.

5.
**Application leaks**
   Desktop or mobile apps bypass proxy/VPN expectations, use their own DNS, or reconnect during sleep/wake transitions.

6.
**File leaks**
   Uploaded files carry metadata such as author, GPS, device, software, and timestamps.

7.
**Behavior leaks**
   Accounts, writing style, schedule, contacts, and recurring habits connect the VPN session to a real identity.

Leak chain example:

```
VPN state: connected
Browser IP: VPN exit
DNS: ISP resolver
IPv6: residential address
Account: real-name login
File: PDF author field contains OS username

Result:
  The VPN is connected, but the workflow is not private against the intended observers.
```

The bug is not just the tunnel. The bug is assuming the tunnel defines the whole privacy boundary.

## Techniques / patterns

- Test IPv4, IPv6, and DNS separately.
- Test the exact browser, app, and device used for the workflow.
- Inspect browser fingerprint and account state before sensitive activity.
- Verify split-tunnel rules and app exclusions.
- Check mobile sleep/wake and reconnect behavior.
- Inspect files before uploading or sharing.
- Treat every leak test as a snapshot, not a permanent guarantee.

## Variants and bypasses

Use the 10 leak classes:

### 1. DNS leaks

The browser or OS resolves domains through the ISP, local network, employer resolver, or another unexpected resolver while traffic otherwise uses the VPN.

### 2. IPv6 leaks

The VPN handles IPv4 but leaves IPv6 enabled on the normal interface. Sites that support IPv6 may see the user's real network path.

### 3. WebRTC leaks

Browser APIs can expose local or public candidate addresses depending on browser settings and network state. Modern browsers have improved, but testing remains useful.

### 4. Split-tunnel mistakes

Split tunneling intentionally excludes routes or apps. A mistake in the exclusion list can send sensitive traffic outside the VPN.

### 5. App-level bypass

Some apps use their own networking stack, DNS, proxy settings, or reconnect behavior. The browser passing a leak test does not prove every app is contained.

### 6. Reconnect race conditions

When Wi-Fi changes, the device wakes, or the VPN reconnects, traffic may briefly leave through the normal network unless firewall containment works.

### 7. Browser fingerprinting

The destination can correlate the browser through fonts, extensions, canvas/WebGL, screen size, language, timezone, and other attributes.

### 8. Login correlation

The user logs into an account that directly identifies them or links to prior sessions, making source-IP masking irrelevant.

### 9. File metadata leakage

Images, PDFs, Office documents, and archives can carry identifying metadata after upload.

### 10. Behavioral correlation

Writing style, timing, social graph, and repeated patterns link the VPN session to existing identities.

## Impact

- Exposure of real IP address, DNS resolver, employer network, ISP, location, or device context.
- Website-level correlation despite changed exit IP.
- Accidental deanonymization through accounts or uploaded files.
- False confidence during sensitive research, reporting, or personal-safety workflows.
- Incomplete incident evidence when a team records "VPN enabled" without testing the full path.

## Detection and defense

Ordered by effectiveness:

1.
**Treat leaks as a workflow problem**
   Test network, DNS, browser, app, account, file, and behavior together. VPN state alone is not enough evidence.

2.
**Use full-tunnel routing when privacy depends on containment**
   Full tunnel is easier to reason about than split tunneling. Split tunneling should be explicit, documented, and tested.

3.
**Disable or correctly route IPv6 when unsupported**
   If the VPN does not support IPv6, either route it through the tunnel or disable it for that workflow. Silent IPv6 fallback is a common mismatch.

4.
**Force DNS through the intended resolver path**
   DNS behavior should match the threat model. Browser DNS-over-HTTPS, OS resolvers, and VPN provider DNS can differ.

5.
**Use browser compartmentalization**
   Separate profiles, anti-fingerprinting browsers, and disciplined account behavior are needed when destination correlation matters.

6.
**Use kill switches or firewall containment**
   A kill switch reduces accidental fallback during disconnects and reconnects. System-level controls are stronger than app-only status indicators.

7.
**Inspect files and remove metadata before sharing**
   Metadata removal should be verified after cleaning, not assumed from an export or screenshot workflow.

### What does not work as a primary defense

- **A green VPN icon is not proof of privacy.** It usually says the tunnel is connected, not that all traffic and identifiers are contained.
- **An IP-check website is not a full leak test.** It does not prove DNS, IPv6, apps, files, or browser identity are safe.
- **Private browsing mode is not leak prevention.** It does not hide IP, DNS, browser fingerprint, app traffic, or account identity.
- **Changing exit country does not stop tracking.** Cookies, accounts, and fingerprints can still correlate sessions.

## Practical labs

### Test IPv4 and IPv6 separately

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Run before and after connecting. Record whether both address families follow the expected path.

### Check resolver path

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Compare resolver visibility before and after VPN connection.

### Compare browser and terminal paths

```
1. Check visible IP in browser.
2. Run terminal curl IP checks.
3. Run DNS resolver checks.
4. Repeat in a second browser profile.
5. Record mismatches.
```

Browser and terminal behavior can diverge because of DNS-over-HTTPS, proxy settings, extensions, or app permissions.

### Inspect split-tunnel assumptions

```
App or route       Expected path      Observed path      Notes
Browser            VPN                unknown            test
Messaging app      VPN                unknown            test
Updater            normal/VPN         unknown            test
Private subnet     direct/VPN         unknown            test
DNS                VPN resolver       unknown            test
```

The table makes split tunneling explicit instead of accidental.

### Inspect file metadata before upload

```
exiftool document.pdf
exiftool image.jpg
```

If author, GPS, software, timestamp, or device fields appear, clean and re-check before sharing.

### Build a leakage incident card

```
Expected privacy path:
Observed leak:
Observer who could see it:
Identity signal exposed:
Root cause:
Retest:
Control change:
```

This keeps leak handling concrete and retestable.

## Practical examples

- A VPN routes browser traffic, but DNS queries still go to the ISP resolver.
- IPv4 shows the VPN exit while IPv6 exposes the home network.
- A work chat app reconnects before the VPN after laptop wake.
- A user uploads a photo through the VPN but leaves GPS metadata intact.
- A user changes exit IP but logs into the same personal account with the same browser profile.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[dns-resolution|DNS Resolution]]
- [[cookies-and-sessions|Cookies and Sessions]]

### Suggested future atomic notes

- [[vpn-kill-switches]]
- [[browser-fingerprinting]]
- [[file-metadata-removal]]
- split-tunneling
- webrtc-leaks

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** ExifTool documentation - https://exiftool.org/
