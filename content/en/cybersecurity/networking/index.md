---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Networking Index

## Purpose

This index is the root entry point for the networking branch of the cybersecurity atlas.

Use it to:
- navigate the networking notes
- understand the order of study
- see how networking connects to web security, API security, attack surface mapping, and playbooks
- see where generic networking stops and wireless-specific security begins
- keep the branch coherent as new notes are added

Use [[reference-registry-networking|Reference Registry — Networking]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0) — the mental models every technical branch assumes.

---

## Recommended learning order

### Phase 1 — Core communication and exposure

1. [[tcp-ip-basics]]
2. [[ports-and-services]]
3. [[dns-resolution]]
4. [[dns-security]]
5. [[dangling-dns-records]]

### Phase 2 — Web traffic and state

1. [[http-overview]]
2. [[http-messages]]
3. [[http-headers]]
4. [[cookies-and-sessions]]
5. [[tls-https]]

### Phase 3 — Boundaries, routing, and trust

1. [[reverse-proxies]]
2. [[client-ip-trust]]
3. [[header-trust-in-node-express]]
4. [[load-balancers]]
5. [[firewalls-and-network-boundaries]]
6. [[nat-and-private-networks]]
7. [[metadata-endpoints]]

### Phase 4 — Discovery and observation

1. [[nmap-scanning]]
2. [[service-enumeration]]
3. [[wireshark-workflows]]
4. [[packet-analysis]]

### Phase 5 — Performance layers with security impact

1. [[caching-and-security]]

This order goes from:
- how systems communicate
- to how names and services become reachable
- to how HTTP traffic really behaves
- to how trust boundaries are built and broken
- to how attackers and defenders observe the environment

---

## Core networking cluster

### Foundational communication

- [[tcp-ip-basics]]
- [[ports-and-services]]
- [[dns-resolution]]
- [[dns-security]]
- [[dangling-dns-records]]

### Web and application-layer traffic

- [[http-overview]]
- [[http-messages]]
- [[http-headers]]
- [[cookies-and-sessions]]
- [[tls-https]]

### Exposure, routing, and boundaries

- [[reverse-proxies]]
- [[client-ip-trust]]
- [[header-trust-in-node-express]]
- [[load-balancers]]
- [[firewalls-and-network-boundaries]]
- [[nat-and-private-networks]]
- [[metadata-endpoints]]

### Discovery and observation

- [[nmap-scanning]]
- [[service-enumeration]]
- [[wireshark-workflows]]
- [[packet-analysis]]

### Performance and delivery

- [[caching-and-security]]

---

## Why this branch matters

Networking is not separate from application security.

It is the substrate for:
- web security
- API security
- reverse proxy trust boundaries
- SSRF impact
- admin interface exposure
- attack surface mapping
- cloud reachability assumptions
- caching and delivery behavior

If a service is reachable, routable, forwarded, cached, or translated incorrectly, the security problem may start long before application code is reviewed.

---

## Cross-links to other branches

### Web security

- [[http-overview]] → supports XSS, CSRF, CORS, sessions, request smuggling
- [[http-messages]] → supports header abuse, auth analysis, parser confusion
- [[http-headers]] → supports CORS, CSP, auth, forwarding behavior
- [[cookies-and-sessions]] → supports auth, session management, CSRF
- [[tls-https]] → supports cookie security, HSTS, transport trust
- [[reverse-proxies]] → supports request smuggling and trust-boundary reasoning

### API security

- [[http-overview]] → supports REST semantics and API behavior
- [[http-headers]] → supports auth headers, caching, forwarding, content negotiation
- [[client-ip-trust]] → supports rate limiting, logs, allowlists
- [[header-trust-in-node-express]] → supports Express-specific proxy trust, `req.ip`, and forwarded-header decisions
- [[reverse-proxies]] → supports trust-boundary thinking for APIs
- [[nat-and-private-networks]] → supports SSRF and internal service access
- [[metadata-endpoints]] → supports SSRF-to-credential-risk thinking

### Attack surface mapping

- [[ports-and-services]]
- [[dns-resolution]]
- [[dns-security]]
- [[subdomain-takeover|Subdomain Takeover]]
- [[firewalls-and-network-boundaries]]
- [[nmap-scanning]]
- [[service-enumeration]]
- [[load-balancers]]

### Wireless security

- [[wireless-security|Wireless Security]]
- [[wifi-monitor-mode|Wi-Fi Monitor Mode]]
- [[arp-poisoning|ARP Poisoning]]
- [[mitm-on-local-networks|MITM on Local Networks]]

### Cloud security

- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[cloud-metadata-security|Cloud Metadata Security]]
- [[cloud-dns-and-certbot|Cloud DNS and Certbot]]
- [[ssh-access-to-cloud-hosts|SSH Access to Cloud Hosts]]

### Detection engineering

- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Playbooks

- [[nmap-scanning]]
- [[service-enumeration]]
- [[packet-analysis]]
- [[reverse-proxies]]
- [[cookies-and-sessions]]
- [[client-ip-trust]]
- [[metadata-endpoints]]

---

## Suggested future notes

### Possible next atomic notes

- dns-record-types
- http-status-codes
- http-methods
- caching-keys-and-vary
- content-negotiation
- health-check-endpoints
- network-segmentation
- egress-control
- client-isolation

### Possible playbooks

- enumerate-exposed-services
- inspect-login-traffic
- [[reverse-proxy-misconfig-checklist]]
- map-public-attack-surface
- [[test-client-ip-spoofing]]
- [[trace-metadata-endpoint-reachability]]

---

## Atlas maintenance rules for networking notes

Each networking note should follow the internal 11-section atomic-note shape:
- Definition
- Why it matters
- How it works
- Techniques / patterns
- Variants and bypasses
- Impact
- Detection and defense
- Practical labs or practical examples
- Related notes
- Suggested future atomic notes
- References

Prefer `## Practical labs` when the topic supports runnable commands. Use `## Practical examples` when the topic is primarily conceptual, architectural, or policy-oriented.

Each networking note should stay practical, not overly academic.
Bias toward:
- exposure
- protocol behavior
- packet-level observation
- real service enumeration
- security implications

Keep Wi-Fi-specific radio, frame, handshake, rogue-AP, and local wireless lab topics in [[index|Wireless Security]].
Keep provider-specific VPC, IAM, metadata, storage, DNS, and cloud logging controls in [[index|Cloud Security]].

---

## References

- **Foundational:** MDN HTTP docs — https://developer.mozilla.org/en-US/docs/Web/HTTP
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
