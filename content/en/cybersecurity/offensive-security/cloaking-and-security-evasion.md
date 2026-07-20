---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloaking and Security Evasion

## Definition

Cloaking is the practice of showing different behavior to different visitors based on signals such as IP, geography, ASN, reverse DNS, User-Agent, browser fingerprint, proxy reputation, or perceived scanner identity.

## Why it matters

Cloaking appears in fraud, phishing, malware delivery, gray-market scraping, and evasive abuse infrastructure. It is also sometimes used legitimately for localization, compliance, or abuse prevention. The security question is not “does content vary?” The question is whether variation hides malicious behavior from defenders, crawlers, scanners, or reviewers.

The old mirror project is a compact example: it allows Argentina, blocks cloud/security/vendor-looking networks, checks proxy reputation, serves `robots.txt`, and redirects or denies traffic based on weak signals.

## How it works

Cloaking has **4 stages**:

1.
**Observe the visitor**
   Collect IP, ASN/org, geolocation, reverse DNS, headers, User-Agent, cookies, JavaScript behavior, and request sequence.

2.
**Classify the visitor**
   Decide whether the visitor looks like a victim, crawler, scanner, security vendor, proxy, researcher, or normal user.

3.
**Fork the response**
   Victim-like traffic receives the real flow. Suspicious traffic receives a redirect, blank page, benign page, error, or robots denial.

4.
**Record and adapt**
   Logs feed future blocklists, allowlists, or targeting rules.

Defensive evidence card:

```
same URL:
  residential browser -> login page
  cloud scanner       -> 403
  security vendor ASN -> news redirect
  curl User-Agent     -> access denied
```

The bug is not content negotiation. The bug is using visitor classification to hide risky behavior from validation.

## Techniques / patterns

- Compare the same URL from different vantage points: residential, cloud, corporate VPN, mobile, and local lab networks.
- Vary User-Agent, language, cookies, JavaScript execution, and proxy headers to see whether content changes.
- Look for benign redirects, fake 404s, blank pages, delayed responses, or “maintenance” pages shown only to scanner-like clients.
- Preserve body hashes, screenshots, headers, TLS certificate details, and redirect chains for each vantage point.
- Separate legitimate regionalization from evasive branching by asking whether the sensitive behavior appears only for selected visitors.
- Treat blocklists of security vendors, cloud providers, and crawler names as strong cloaking indicators when paired with risky content.

## Variants and bypasses

Cloaking has **6 recognizable variants**.

### 1. Geo cloaking

Behavior changes by country or region. Legitimate localization exists, but phishing and fraud often target one region while hiding from foreign scanners.

### 2. ASN / hosting cloaking

Traffic from cloud providers, data centers, VPNs, and security vendors receives harmless content. Residential or mobile traffic sees the real flow.

### 3. User-Agent cloaking

Known crawlers, command-line tools, scanners, or headless browsers are blocked. Browser-like strings receive different content.

### 4. Reverse-DNS cloaking

PTR hostnames containing vendor, cloud, crawler, or security terms are denied. This is fragile but common in older kits.

### 5. Fingerprint cloaking

JavaScript, browser APIs, timing, storage, or rendering behavior distinguishes real browsers from automation.

### 6. Interaction cloaking

The suspicious behavior appears only after clicks, login steps, delays, referrers, email-link parameters, or campaign tokens.

## Impact

- **Security review bypass.** Automated scanners or vendor crawlers see benign content while victims see the real payload.
- **Phishing longevity.** Reporting and takedown pipelines get misleading evidence.
- **Malware delivery control.** Operators reduce exposure to sandboxes and researchers.
- **Fraud targeting.** Campaigns focus on specific regions, devices, or account populations.
- **False defensive confidence.** A clean scan from one vantage point is mistaken for clean behavior everywhere.

## Detection and defense

Ordered by effectiveness:

1.
**Test from multiple vantage points**
   One network path is not enough. Compare residential, mobile, corporate, cloud, and controlled scanner paths to reveal response forks.

2.
**Capture full response evidence**
   Record status, headers, redirects, body hash, screenshot, DNS answer, TLS certificate, and timing. Cloaking often hides in small differences.

3.
**Replay with controlled signal changes**
   Change one variable at a time: User-Agent, cookie jar, language, source network, referrer, JavaScript capability, or campaign token.

4.
**Monitor for defensive-vendor blocklists**
   Code or config that names security vendors, crawlers, cloud providers, or threat-intel systems is high-signal evidence of evasion intent.

5.
**Instrument user-reported paths**
   Reports from real users should preserve original URL, referrer, email headers, device/browser, and timestamp. The victim path may be the only path that reveals the content.

6.
**Avoid assuming benign content proves safety**
   Treat benign responses as one observation from one vantage point. The finding is the differential behavior, not only the hidden payload.

### What does not work as a primary defense

- **A single scanner run.** Cloaking exists to make that view incomplete.
- **Only testing from cloud infrastructure.** Many cloaking rules specifically block data centers and security vendors.
- **Trusting robots.txt.** It is not access control and can itself be part of the decoy surface.
- **Ignoring redirects.** The redirect target may be the cloaking decision.
- **Calling all variation malicious.** Localization, A/B tests, and compliance banners vary too; the key is security-relevant concealment.

## Practical labs

### Compare response fingerprints

```
for ua in "curl/8.0" "Mozilla/5.0 Chrome/120 Safari/537.36" "Googlebot/2.1"; do
  curl -sk -A "$ua" -D "/tmp/headers-$ua.txt" -o "/tmp/body-$ua.html" https://example.test/
  shasum "/tmp/body-$ua.html"
done
```

Different body hashes by User-Agent are a prompt for review, not proof by themselves.

### Record a vantage matrix

```
url:
vantage | ip/asn type | user-agent | status | final-url | body-hash | screenshot | notes
home    | residential | browser    |        |           |           |            |
cloud   | hosting     | browser    |        |           |           |            |
mobile  | carrier     | browser    |        |           |           |            |
cloud   | hosting     | curl       |        |           |           |            |
```

The matrix reveals whether the same URL is behaving as one application or several.

### Check redirect cloaking

```
curl -skIL https://example.test/path \
  -A "Mozilla/5.0 Chrome/120 Safari/537.36"
```

Compare final locations across networks; harmless-looking redirects may be the fork.

### Search code for cloaking vocabulary

```
rg -n "bot|crawler|spider|google|virustotal|phishtank|asn|isp|proxy|vpn|reverse|country|geo" .
```

In owned code, these terms identify where classification and response branching should be reviewed.

### Preserve victim-path context

```
reported URL:
timestamp:
source email/referrer:
device/browser:
network type:
redirect chain:
visible content:
comparison vantage:
```

Without the original path, defenders may only see the decoy.

## Practical examples

- A phishing page shows a fake login only to mobile-carrier IPs in one country and redirects cloud scanners to a news site.
- A malicious download link returns a clean PDF to security-vendor ASNs and a payload to residential browsers.
- A scraper ignores `robots.txt` but changes User-Agent and IP range after being blocked.
- A gray-market bot blocks uptime monitors and security scanners while attacking checkout inventory.
- A fraud campaign requires an email-link token before showing the real page.

## Related notes

- [[bot-detection-signals|Bot Detection Signals]]
- [[recon|Recon]]
- [[active-recon|Active Recon]]
- [[http-headers|HTTP Headers]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

### Suggested future atomic notes

- asn-and-hosting-reputation
- reverse-dns-security-signals
- phishing-detection-signals
- multi-vantage-testing
- malware-sandbox-evasion

## References

- **Foundational:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Testing / Lab:** OWASP Web Security Testing Guide — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery reconnaissance deep dive — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
