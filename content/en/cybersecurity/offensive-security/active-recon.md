---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Active Recon

## Definition

Active recon is information gathering that directly interacts with target infrastructure, services, or applications to validate or extend what passive recon discovered.

## Why it matters

Passive recon finds possibilities. Active recon turns them into evidence: which hosts answer, which ports are open, which routes exist, which services behave like admin panels, and which leads are stale.

Active recon must be authorized and scoped. It is operationally later than [[passive-recon]] and narrower than general [[enumeration]].

## How it works

Active recon has **5 validation loops**:

1. **Host liveness.** Does the candidate host resolve and respond?
2. **Service reachability.** Which ports, protocols, and virtual hosts answer?
3. **Application behavior.** What status codes, redirects, headers, and content appear?
4. **Surface expansion.** Which routes, parameters, schemas, and versions are discoverable?
5. **Triage.** Does the finding deserve deeper testing, ownership review, or discard?

The bug in active recon is not one request. It is noisy, unscoped probing that fails to produce useful evidence.

A worked example, passive lead to active validation:

```
Passive lead:
  preview-api.example.test appears in certificate transparency

Scope check:
  domain is target-owned and wildcard program scope includes *.example.test

Active check:
  DNS resolves, HTTPS returns 401 with "preview-api" header

Decision:
  live in-scope API candidate; move to service validation and API inventory testing
```

Active recon should answer one validation question at a time.

## Techniques / patterns

Practitioners use:

- low-rate HTTP probes and status-code checks
- DNS resolution and virtual-host validation
- port scanning inside allowed scope
- route and endpoint probing
- technology fingerprinting
- screenshotting or page-title capture for triage
- comparison against asset inventory

## Variants and bypasses

Active recon has **5 activity classes**.

### 1. HTTP probing

Checks live web behavior, redirects, headers, titles, and route availability.

### 2. Port discovery

Finds reachable services and non-standard ports.

### 3. Virtual-host probing

Tests whether hosts and origins route differently based on `Host`.

### 4. Endpoint probing

Checks known or guessed routes, methods, schemas, and parameters.

### 5. Controlled fingerprinting

Infers stack and service role without exploit attempts.

## Impact

Ordered roughly by severity:

- **Live exposure confirmation.** Separates real assets from passive noise.
- **Unexpected service discovery.** Reveals admin, debug, legacy, or remote-access services.
- **Route discovery.** Feeds API and web testing.
- **Inventory correction.** Shows defenders what outsiders can validate.
- **Testing prioritization.** Prevents wasting manual effort on dead assets.

## Detection and defense

Ordered by effectiveness:

1.
**Define authorized scope and rate limits.**
   Active recon should be safe, repeatable, and bounded.

2.
**Run internal active recon before outsiders do.**
   Defensive scanning validates exposure and inventory.

3.
**Monitor for probing patterns.**
   Repeated 404s, admin path probes, host-header probes, and port sweeps are useful signals.

4.
**Make unexpected findings actionable.**
   Unknown live assets should become owner, exposure, and retirement questions.

5.
**Avoid fragile obscurity controls.**
   Active recon quickly finds hidden paths and unusual ports.

### What does not work as a primary defense

- **Blocking only one scanner signature.** Recon can be done with ordinary HTTP clients.
- **Hiding services on high ports.** Active scans find reachable ports.
- **Treating all probes as attacks.** Defensive teams need safe recon too.
- **Ignoring low-volume probes.** Skilled recon often stays low and targeted.

## Practical labs

Use owned targets.

### Check live web candidates

```
while read host; do
  curl -m 3 -ks -o /dev/null -w "%{http_code} %{url_effective}\\n" "https://$host"
done < hosts.txt
```

Separate live, redirected, denied, and dead assets.

### Scan scoped ports

```
nmap -sV -Pn --top-ports 100 target.example.test
```

Use allowed targets and appropriate rate limits.

### Probe virtual-host routing

```
curl -i -H 'Host: admin.example.test' https://203.0.113.10/
```

Only test owned IPs and hostnames.

### Record active recon rate and scope

```
Target list:
Allowed ports/routes:
Max rate:
Start/stop time:
User agent:
Contact/escalation:
```

Safe active recon is operationally bounded before it runs.

### Compare passive and active status

```
host | passive source | DNS | HTTPS | status | next action
```

This shows which public clues became live assets and which were stale.

### Capture reproducible probe artifacts

```
command | timestamp | target | response summary | saved artifact
```

Active recon evidence should be repeatable without re-running noisy probes.

## Practical examples

- A guessed subdomain is confirmed live.
- Host discovery finds a service not recorded in inventory.
- Probing reveals alternate virtual hosts or legacy routes.
- A route returns `403` instead of `404`, suggesting a real protected surface.
- A high-port dashboard responds with a vendor login.

## Related notes

- [[recon]]
- [[passive-recon]]
- [[host-and-port-discovery]]
- [[service-validation]]
- [[nmap-scanning|Nmap Scanning]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Suggested future atomic notes

- safe-active-recon-rules
- virtual-host-discovery
- http-probing
- screenshot-triage
- low-noise-scanning

## References

- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 105 — https://projectdiscovery.io/blog/reconnaissance-series-5-additional-active-reconnaissance
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
