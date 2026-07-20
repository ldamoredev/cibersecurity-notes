---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Playbooks

## Purpose

This note standardizes the references used by the security-playbooks branch.

Use it to:
- keep playbooks anchored to strong sources
- prevent random or low-value references
- make Codex reuse the same high-signal bibliography
- tie procedures to both testing guidance and exploitation labs

## Source of truth rule

For playbooks, this registry is the primary source of truth.

Use it together with:
- `<a href="security-playbooks/index.html">Security Playbooks Index</a>`
- the concept branches those playbooks rely on

---

## Reference selection policy

### Source priority

1. official labs and practical training
2. standards and testing guides
3. cheat sheets / mitigation guides
4. high-signal research
5. secondary sources only when they add clear procedural value

### Per-note target

- minimum 2 references
- ideal 3 references

### Labeling

Use:
- **Testing / Lab**
- **Foundational**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Playbook topic map

## exploit-idor

Preferred references:
- **Testing / Lab:** PortSwigger IDOR page — https://portswigger.net/web-security/access-control/idor
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control
- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/

## inspect-session-handling

Preferred references:
- **Foundational:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

## break-jwt-validation

Preferred references:
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## investigate-ssrf

Preferred references:
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Research / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

## trace-metadata-endpoint-reachability

Preferred references:
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Research / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

## reverse-proxy-misconfig-checklist

Preferred references:
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** PortSwigger Research — https://portswigger.net/research
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages

## test-client-ip-spoofing

Preferred references:
- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## exploit-sqli

Preferred references:
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Foundational:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## test-path-traversal

Preferred references:
- **Testing / Lab:** PortSwigger path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## test-cors-behavior

Preferred references:
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Foundational:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

## inspect-file-upload-surface

Preferred references:
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## run-scan-pipeline

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Masscan README and man page — https://github.com/robertdavidgraham/masscan
- **Official Tool Docs:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Foundational:** Detection Engineering Index — [[index]]

## detect-external-scan-pipeline

Preferred references:
- **Official Tool Docs:** Zeek Logs — https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Suricata EVE JSON Output — https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Foundational:** RFC 7011 IPFIX — https://www.rfc-editor.org/rfc/rfc7011.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents — https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table

## detect-kerberoasting-and-as-rep-roasting

Preferred references:
- **Foundational:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Foundational:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
- **Research / Deep Dive:** Microsoft Threat Intelligence — How attacks abuse Kerberos: detection and mitigations — https://www.microsoft.com/en-us/security/blog/2022/01/26/evolving-kerberos-attack-detection/

## detect-dcsync-and-ntdsdit-access

Preferred references:
- **Foundational:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Foundational:** Microsoft Learn — AD DS replication permissions and audit guidance — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
- **Telemetry Schema:** Microsoft Defender for Identity — DCSync attack detection — https://learn.microsoft.com/en-us/defender-for-identity/credential-access-alerts

---

## Registry usage rules

- choose the smallest set of strongest references for the exact playbook
- prefer labs plus one foundational reference
- attach concept-note links alongside references
