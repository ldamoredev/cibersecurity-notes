---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Bot Detection Signals

## Definition

Bot detection signals are the observable clues a web application or edge service uses to classify traffic as human, benign automation, suspicious automation, or malicious automation.

## Why it matters

Modern abuse often uses valid application features at machine speed: credential stuffing, scraping, account creation, inventory hoarding, card testing, spam, scanning, and metric manipulation. These are not always “vulnerabilities” in the injection sense. They are abuse of normal workflows.

The old mirror project demonstrates a common beginner model: block User-Agents, IP ranges, hostnames, ISPs, proxies, and browser strings. That is useful as a starting vocabulary, but mature bot defense treats each signal as probabilistic and combines network, browser, account, behavior, and business context.

## How it works

Bot classification uses **5 signal families**:

1.
**Network signals**
   Source IP, ASN, hosting provider, VPN/proxy reputation, geolocation, connection history.

2.
**Protocol signals**
   HTTP version, header order, missing headers, TLS/client hints, cookie behavior, redirect handling.

3.
**Client-declared signals**
   User-Agent, Accept-Language, platform hints, automation library fingerprints. These are easy to fake but still useful telemetry.

4.
**Browser/runtime signals**
   JavaScript execution, storage behavior, rendering capabilities, timing, fingerprint stability, challenge handling.

5.
**Behavior and business signals**
   Request rate, path sequence, account targets, failed-login distribution, cart behavior, scraping depth, inventory lock patterns.

Toy classifier:

```
User-Agent contains "curl"      -> +1 automation signal
ASN is cloud hosting            -> +1 hosting signal
No cookies after login redirect -> +1 browser-behavior signal
100 login attempts / minute     -> +5 abuse signal
Many accounts, one password     -> credential spraying pattern
```

The bug is treating one weak signal as a verdict. The mature model asks how multiple signals line up with a specific abuse pattern.

## Techniques / patterns

- Separate **good automation** from bad automation: search crawlers, uptime monitors, API clients, partner integrations, and accessibility tooling may be legitimate.
- Classify by objective: credential stuffing, scraping, scanning, account creation, spam, inventory denial, or token cracking.
- Compare signals across layers: IP reputation plus route sequence plus account behavior is stronger than User-Agent alone.
- Watch for impossible browser behavior: no cookies where cookies are required, no JS where JS is mandatory, inconsistent headers, or state transitions too fast for humans.
- Use rate limits by route, account, credential pair, session, device, ASN, and IP, not just one global IP bucket.
- Build allowlists with ownership and expiry; permanent allowlists become bypass channels.

## Variants and bypasses

Bot detection fails in **6 recurring ways**.

### 1. User-Agent-only blocking

The app blocks `curl`, `python`, `sqlmap`, or crawler strings. Attackers set a browser-like User-Agent. Legitimate tools and monitors may be blocked accidentally.

### 2. Static IP blocklists

The app blocks known ranges or old bad IPs. Cloud IPs rotate, residential proxies exist, and stale blocklists create false positives.

### 3. ASN and hosting reputation overreach

Cloud and hosting ASNs are useful risk signals, but many legitimate users, monitors, partners, and corporate egress paths also come from those networks.

### 4. Reverse-DNS certainty

PTR records can help identify crawlers or vendors, but they can be absent, stale, generic, or misleading. Reverse DNS should support triage, not replace proof.

### 5. Challenge dependence

CAPTCHA or JavaScript challenges reduce some automation but introduce accessibility, UX, privacy, and solver-service issues. They should protect specific abuse points, not become the whole strategy.

### 6. Missing business context

The strongest signal may be domain-specific: cart holds without checkout, many reset emails, repeated gift-card balance checks, or scraping exactly one expensive endpoint.

## Impact

- **Account takeover.** Credential stuffing and password spraying compromise reused passwords.
- **Data scraping.** Content, pricing, listings, user data, or internal terminology is extracted at scale.
- **Fraud and financial abuse.** Carding, coupon abuse, gift-card enumeration, and refund abuse become automated.
- **Resource exhaustion.** Expensive searches, reports, or inventory holds degrade service or create denial-of-wallet.
- **Security noise.** Scanner-like traffic hides real attack chains inside high-volume background automation.
- **User harm.** Lockouts, spam, account creation abuse, and privacy exposure affect real users.

## Detection and defense

Ordered by effectiveness:

1.
**Classify the abuse objective first**
   A credential-stuffing defense is not the same as a scraping defense. Start with the business action being abused, then choose signals that actually discriminate that action.

2.
**Use layered scoring instead of one-bit blocking**
   Combine network, protocol, client, account, and behavior signals. One weak signal should rarely block by itself; several aligned signals can justify throttling, challenge, review, or denial.

3.
**Rate-limit by multiple keys**
   Protect login by account, credential pair, source network, device/session, and route. This prevents easy bypass by rotating only one identifier.

4.
**Preserve good automation paths**
   Verified crawlers, partner clients, uptime monitors, and accessibility tooling need documented allowlists or API paths. Otherwise bot defense becomes self-inflicted downtime.

5.
**Instrument state transitions**
   Log enough to see route order, session continuity, cookie handling, and account-target distribution. Behavior beats labels.

6.
**Tune response actions**
   Use soft friction, throttling, proof-of-work, step-up auth, or delayed responses where possible. Hard blocking is only one response and often the noisiest.

### What does not work as a primary defense

- **User-Agent regexes alone.** They are trivial to change and often overblock.
- **Robots.txt as access control.** It is a convention for cooperative crawlers, not enforcement.
- **One global IP rate limit.** Cloud, mobile, NAT, and proxy behavior make IP both overbroad and easy to rotate.
- **CAPTCHA everywhere.** It harms users and can be outsourced or bypassed.
- **Permanent allowlists without owners.** They become silent bypasses.

## Practical labs

### Build a signal inventory

```
route:
business action:
network signals:
header signals:
browser/runtime signals:
account/session signals:
behavior signals:
possible false positives:
response action:
```

This turns “bot?” into an evidence-based classification problem.

### Test User-Agent weakness

```
for ua in "curl/8.0" "python-requests/2" \
          "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 Chrome/120 Safari/537.36"; do
  printf '%s -> ' "$ua"
  curl -s -o /dev/null -w "%{http_code}\n" -A "$ua" https://example.test/login
done
```

Different behavior based only on this header means the decision is easy to evade.

### Detect credential stuffing shape

```
time window: 10 minutes
same password across many accounts: yes/no
many passwords against one account: yes/no
source IP count:
ASN count:
success after many failures:
MFA challenge triggered:
```

The pattern tells you whether this is stuffing, spraying, brute force, or noisy login failure.

### Separate crawler from scraper

```
client:
identifies itself:
respects robots.txt:
rate:
paths requested:
auth state:
contact/owner:
business impact:
```

Legitimate automation has an owner and predictable boundaries.

### Compare route sequence

```
rg -n "GET /|POST /" access.log \
  | rg "/login|/api/search|/cart|/checkout|/password-reset"
```

Sequence and repetition usually reveal more than the client label.

## Practical examples

- A login endpoint sees one password tried against 5,000 accounts from many ASNs: credential spraying.
- A product site sees high-speed browsing of every SKU page with no cart or session continuity: scraping.
- A checkout flow sees thousands of card validation attempts with tiny baskets: carding.
- A ticketing site sees inventory held but never purchased: denial of inventory.
- A security scanner announces itself in User-Agent; a stealth scraper spoofs Chrome but never accepts cookies.

## Related notes

- [[api-rate-limiting|API Rate Limiting]]
- [[auth-flaws|Auth Flaws]]
- [[http-headers|HTTP Headers]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

### Suggested future atomic notes

- credential-stuffing-defenses
- asn-and-hosting-reputation
- reverse-dns-security-signals
- rate-limit-key-design
- crawler-verification

## References

- **Foundational:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Mitigation:** OWASP Credential Stuffing Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html
- **Foundational:** Cloudflare Learning Center: What is bot management? — https://www.cloudflare.com/learning/bots/what-is-bot-management/
