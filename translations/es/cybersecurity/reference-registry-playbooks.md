# Reference Registry — Playbooks

## Propósito

Esta nota estandariza las referencias usadas por la rama security-playbooks.

Usala para:
- mantener los playbooks anclados a fuentes fuertes
- prevenir referencias random o de bajo valor
- hacer que Codex reutilice la misma bibliografía de alta señal
- atar procedimientos tanto a guía de testing como a labs de explotación

## Regla de fuente de verdad

Para playbooks, este registry es la fuente de verdad primaria.

Usalo junto con:
- `<a href="security-playbooks/index.html">Security Playbooks Index</a>`
- las ramas conceptuales de las que dependen esos playbooks

---

## Política de selección de referencias

### Prioridad de fuentes

1. labs oficiales y training práctico
2. estándares y guías de testing
3. cheat sheets / guías de mitigación
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor procedural claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias

### Etiquetas

Usar:
- **Testing / Lab**
- **Fundamental**
- **Investigación / Deep Dive**
- **Docs oficiales de herramienta**

---

# Mapa de temas playbook

## exploit-idor

Referencias preferidas:
- **Testing / Lab:** PortSwigger IDOR page — https://portswigger.net/web-security/access-control/idor
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control
- **Fundamental:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/

## inspect-session-handling

Referencias preferidas:
- **Fundamental:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Fundamental:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

## break-jwt-validation

Referencias preferidas:
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## investigate-ssrf

Referencias preferidas:
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Investigación / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

## trace-metadata-endpoint-reachability

Referencias preferidas:
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Investigación / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html

## reverse-proxy-misconfig-checklist

Referencias preferidas:
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** PortSwigger Research — https://portswigger.net/research
- **Fundamental:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages

## test-client-ip-spoofing

Referencias preferidas:
- **Fundamental:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## exploit-sqli

Referencias preferidas:
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Fundamental:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## test-path-traversal

Referencias preferidas:
- **Testing / Lab:** PortSwigger path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## test-cors-behavior

Referencias preferidas:
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Fundamental:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

## inspect-file-upload-surface

Referencias preferidas:
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/

## run-scan-pipeline

Referencias preferidas:
- **Docs oficiales de herramienta:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Docs oficiales de herramienta:** Masscan README and man page — https://github.com/robertdavidgraham/masscan
- **Docs oficiales de herramienta:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Fundamental:** Detection Engineering Index — [[index]]

## detect-external-scan-pipeline

Referencias preferidas:
- **Docs oficiales de herramienta:** Zeek Logs — https://docs.zeek.org/en/current/logs/
- **Docs oficiales de herramienta:** Suricata EVE JSON Output — https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Fundamental:** RFC 7011 IPFIX — https://www.rfc-editor.org/rfc/rfc7011.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents — https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table

## detect-kerberoasting-and-as-rep-roasting

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Fundamental:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
- **Investigación / Deep Dive:** Microsoft Threat Intelligence — How attacks abuse Kerberos: detection and mitigations — https://www.microsoft.com/en-us/security/blog/2022/01/26/evolving-kerberos-attack-detection/

## detect-dcsync-and-ntdsdit-access

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Fundamental:** Microsoft Learn — AD DS replication permissions and audit guidance — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
- **Telemetry Schema:** Microsoft Defender for Identity — DCSync attack detection — https://learn.microsoft.com/en-us/defender-for-identity/credential-access-alerts

---

## Reglas de uso del registry

- elegí el set más chico de referencias fuertes para el playbook exacto
- preferí labs más una referencia fundacional
- adjuntá links a notas conceptuales junto con las referencias
