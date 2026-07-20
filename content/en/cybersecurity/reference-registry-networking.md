---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Networking

## Purpose

This note is the networking-specific seed for the broader cybersecurity reference registry.

Use it to:
- standardize references for networking notes
- keep source quality consistent
- help Codex assign references without inventing weak source sets
- make future networking notes easier to expand

## Source of truth rule

For networking notes, this registry is the primary source of truth.

Use it together with:
- `<a href="networking/index.html">Networking Index</a>` for study order and branch structure
- `<a href="reference-registry.html">Cybersecurity Reference Registry</a>` for broader cross-branch fallback only when this note does not yet cover a networking topic

When assigning references:
- choose the smallest set of strongest references for the exact note
- do not invent random networking reference sets ad hoc
- if a note is missing here, infer from the closest networking parent topic first and add a registry entry proposal
- keep networking references tied to security implications, not academic abstraction

---

## Reference selection policy

### Source priority

1. official documentation
2. official labs and practical training
3. standards and testing guides
4. high-signal research
5. secondary sources only when they add clear value

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid bloating notes with long lists

### Labeling

Use:
- **Foundational**
- **Testing / Lab**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Networking topic map

## tcp-ip-basics

Preferred references:
- **Foundational:** RFC 9293 (Transmission Control Protocol) — https://datatracker.ietf.org/doc/html/rfc9293
- **Foundational:** RFC 791 (Internet Protocol) — https://datatracker.ietf.org/doc/html/rfc791
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/

Why:
- TCP/IP notes should stay grounded in real network behavior, not abstract theory
- Nmap and Wireshark are the most practical anchors for how communication and reachability are observed

---

## ports-and-services

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/

Why:
- this topic is operational and tied directly to attack surface
- Nmap is the core practical reference

---

## dns-resolution

Preferred references:
- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Foundational:** ICANN DNS Concepts — https://www.icann.org/resources/pages/dns-2012-02-25-en
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers

Why:
- this note should explain how names resolve in practice and why that matters for ownership, exposure, and asset discovery

---

## dns-security

Preferred references:
- **Foundational:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Foundational:** ICANN DNSSEC — https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en
- **Mitigation:** CISA Domain Name System Security Best Practices — https://www.cisa.gov/resources-tools/resources/domain-name-system-dns-security-best-practices
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20

Why:
- DNS matters most here as attack surface, ownership drift, and domain-control hygiene, not just protocol theory

---

## dangling-dns-records

Preferred references:
- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20

Why:
- this note owns the DNS lifecycle and stale-record mechanism that can later become a subdomain-takeover finding in attack-surface mapping

---

## http-overview

Preferred references:
- **Foundational:** MDN HTTP overview — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Foundational:** MDN HTTP request methods — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security

Why:
- MDN provides the practical browser/server behavior anchor; RFC 9110 anchors the formal semantics; PortSwigger is the canonical hands-on lab path for HTTP-rooted vulnerabilities

---

## http-messages

Preferred references:
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 9112 (HTTP/1.1 Message Syntax) — https://datatracker.ietf.org/doc/html/rfc9112
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn

Why:
- HTTP messages are best understood through both protocol shape and security consequences. RFC 9112 anchors the formal HTTP/1.1 wire syntax; the Kettle paper is the strongest research anchor on what happens when two parsers disagree on it

---

## http-headers

Preferred references:
- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Mitigation:** OWASP HTTP Headers Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security

Why:
- header behavior sits at the intersection of protocol semantics, browser behavior, caching, proxy trust, and multiple exploit classes

---

## cookies-and-sessions

Preferred references:
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- **Foundational:** OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- **Testing / Lab:** OWASP WSTG Session Management Testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf

Why:
- this note needs browser semantics plus security testing/mitigation framing

---

## tls-https

Preferred references:
- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** RFC 8446 (TLS 1.3) — https://datatracker.ietf.org/doc/html/rfc8446
- **Foundational:** Mozilla SSL Configuration Generator — https://ssl-config.mozilla.org/
- **Official Tool Docs:** OpenSSL s_client — https://docs.openssl.org/master/man1/openssl-s_client/
- **Testing / Lab:** testssl.sh — https://github.com/drwetter/testssl.sh

Why:
- this note stays practical (transport trust, TLS termination, HSTS, certificate inspection). RFC 8446 anchors the modern TLS spec, Mozilla SSL Configuration Generator is the canonical posture-policy reference, openssl s_client is the standard inspection tool, and testssl.sh is the standard scanner. MDN remains the practical entry point

---

## reverse-proxies

Preferred references:
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn

Why:
- reverse proxies are a trust-boundary note. RFC 7239 and MDN anchor the forwarding-header semantics, the PortSwigger academy is the canonical smuggling lab, and the Kettle paper is the strongest single research anchor for the parser-disagreement class

---

## client-ip-trust

Preferred references:
- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Why:
- this note is about how trust headers affect logging, rate limiting, allowlists, and access controls. RFC 7239 anchors the structured-Forwarded spec; the Kettle paper is the canonical writeup on why unkeyed forwarding headers like XFF and X-Forwarded-Host are dangerous

---

## header-trust-in-node-express

Preferred references:
- **Official Tool Docs:** Express behind proxies — https://expressjs.com/en/guide/behind-proxies.html
- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239

Why:
- this note is the framework-specific bridge from [[client-ip-trust]] into Express. Express documentation owns `trust proxy`; MDN and RFC 7239 anchor the forwarding-header semantics

---

## load-balancers

Preferred references:
- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Why:
- load balancers are entry-point and trust-boundary notes, not just infra notes

---

## firewalls-and-network-boundaries

Preferred references:
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Mitigation:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html

Why:
- this note should connect exposure assumptions to evidence-based discovery

---

## nat-and-private-networks

Preferred references:
- **Foundational:** RFC 1918 (Private Address Allocation) — https://datatracker.ietf.org/doc/html/rfc1918
- **Foundational:** RFC 6598 (CGNAT shared address space) — https://datatracker.ietf.org/doc/html/rfc6598
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html

Why:
- the value of this note is in linking private reachability to SSRF and internal trust boundaries. RFC 1918 + 6598 anchor the formal address-space definitions; the OWASP cheat sheet anchors the SSRF defenses that close the link-local / private-range gates; PortSwigger and Nmap are the practical lab anchors

---

## metadata-endpoints

Preferred references:
- **Foundational:** AWS Instance Metadata Service docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Foundational:** GCP metadata server docs — https://cloud.google.com/compute/docs/metadata/overview
- **Foundational:** Azure Instance Metadata Service docs — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf

Why:
- this note tightly connects internal reachability, SSRF, and cloud-credential exposure risk. The three cloud-vendor docs are the only authoritative sources for protocol shape per platform (AWS IMDSv1/v2, GCP Metadata-Flavor, Azure header-required). OWASP and PortSwigger are the canonical defense and lab anchors

---

## nmap-scanning

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/

Why:
- Nmap should be taught from the official manual first

---

## service-enumeration

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/

Why:
- this note is where discovery becomes actionable understanding of exposed services and protocols

---

## wireshark-workflows

Preferred references:
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark docs portal — https://www.wireshark.org/docs/
- **Official Tool Docs:** Wireshark display filters — https://www.wireshark.org/docs/man-pages/wireshark-filter.html

Why:
- this topic is tool-native and should remain grounded in the official docs

---

## packet-analysis

Preferred references:
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Official Tool Docs:** tcpdump man page — https://www.tcpdump.org/manpages/tcpdump.1.html
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages

Why:
- packet analysis needs both capture tooling and message interpretation

---

## caching-and-security

Preferred references:
- **Foundational:** MDN HTTP caching — https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- **Foundational:** MDN Cache-Control — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
- **Testing / Lab:** PortSwigger Web Cache Poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning

Why:
- caching issues are subtle and often arise from protocol semantics interacting with shared infrastructure

---

# Registry usage rules

- choose the smallest set of strongest references for each exact note
- do not assign generic links blindly
- prefer official documentation and strong labs
- if a future networking note is missing from this registry, map it to the closest parent topic first
- when adding cloud-specific networking notes later, add provider docs only if the note becomes implementation-specific

---

# Suggested next networking registry entries

Add these when the branch expands:
- dns-record-types
- http-status-codes
- http-methods
- caching-keys-and-vary
- content-negotiation
- health-check-endpoints
- network-segmentation
- egress-control
