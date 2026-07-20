---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — API Security

## Purpose

This note is the API-security-specific seed for the broader cybersecurity reference registry.

Use it to:
- standardize references for API-security notes
- keep source quality consistent
- help Codex assign references without inventing weak source sets
- make future API-security notes easier to expand

## Source of truth rule

For API-security notes, this registry is the primary source of truth.

Use it together with:
- `<a href="api-security/index.html">API Security Index</a>` for study order and branch structure
- `<a href="reference-registry.html">Cybersecurity Reference Registry</a>` for broader fallback only when this note does not yet cover an API-security topic

---

## Reference selection policy

### Source priority

1. official standards and project documentation
2. official labs and practical training
3. testing guides and cheat sheets
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

# API-security topic map

## api-security-top-10

Preferred references:
- **Foundational:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Foundational:** OWASP REST Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## authorization

Preferred references:
- **Foundational:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## broken-object-level-authorization

Preferred references:
- **Foundational:** OWASP API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-bola/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control / IDOR — https://portswigger.net/web-security/access-control/idor

## broken-function-level-authorization

Preferred references:
- **Foundational:** OWASP API5:2023 Broken Function Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa5-bfla/
- **Foundational:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## broken-authentication

Preferred references:
- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-auth-flaws

Preferred references:
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication

## jwt-attacks

Preferred references:
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt

## token-lifecycle

Preferred references:
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/

## broken-object-property-level-authorization

Preferred references:
- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure

## excessive-data-exposure

Preferred references:
- **Foundational:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## mass-assignment

Preferred references:
- **Foundational:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-rate-limiting

Preferred references:
- **Foundational:** OWASP API4:2023 Unrestricted Resource Consumption — https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-inventory-management

Preferred references:
- **Foundational:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing and OWASP alignment — https://portswigger.net/web-security/api-testing/top-10-api-vulnerabilities

## polymorphic-deserialization

Preferred references:
- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Foundational:** OWASP API8:2023 Security Misconfiguration — https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Moritz Bechler, "Java Unmarshaller Security" (`marshalsec`) — https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf
- **Official Tool Docs:** ysoserial.net — https://github.com/pwntester/ysoserial.net

---

## Registry usage rules

- choose the smallest set of strongest references for each exact note
- do not assign generic links blindly
- prefer official documentation and strong labs
- if a future API-security note is missing from this registry, map it to the closest parent topic first
