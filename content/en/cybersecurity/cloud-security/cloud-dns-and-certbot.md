---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud DNS and Certbot

## Definition

Cloud DNS and Certbot is the operational pattern of pointing cloud-hosted domains at cloud resources and issuing TLS certificates for those services.

## Why it matters

Cloud labs often move quickly from "I launched a VM" to "I exposed a domain with HTTPS." That path touches DNS ownership, public IPs, certificates, firewall rules, web server config, and renewal automation.

The security lesson is that DNS and TLS are not decoration. They are ownership, reachability, and trust controls.

## How it works

Cloud DNS and certificate setup has **6 steps**:

1. **Own or delegate a domain.** Registrar and authoritative DNS decide control.
2. **Create records.** A/AAAA/CNAME records point names at cloud resources.
3. **Expose service ports.** HTTP/HTTPS must be reachable for validation and service.
4. **Prove domain control.** ACME validation uses HTTP or DNS challenges.
5. **Install certificates.** The service presents a valid cert for the name.
6. **Automate renewal.** Short-lived certs require reliable renewal and reload.

The bug is not using Certbot. The bug is weak DNS ownership, stale records, broad exposure, or broken renewal assumptions.

A worked example, certificate setup to exposure drift:

```
Goal:
  expose lab.example.test over HTTPS

DNS:
  A record points to static cloud IP

Validation:
  HTTP-01 challenge required opening TCP/80

After setup:
  HTTPS works, but TCP/80 remains public and redirects to app

Teardown risk:
  VM can be deleted while DNS still points at static IP or future reused address

Decision:
  track DNS record, static IP, firewall rule, certificate renewal, and teardown as one lifecycle unit
```

The security unit is the name-to-service lifecycle, not only the certificate command.

## Techniques / patterns

Reviews look at:

- registrar and DNS account protection
- A/AAAA/CNAME records pointing to current resources
- stale records after teardown
- HTTP validation paths and temporary firewall openings
- certificate name coverage and renewal timers
- TLS config and redirect behavior

## Variants and bypasses

Cloud DNS/TLS risk has **4 common shapes**.

### 1. Stale DNS to deleted resources

Records point at abandoned cloud services or IPs.

### 2. Temporary validation exposure left open

HTTP or admin ports stay reachable after certificate setup.

### 3. Renewal failure

Certificates expire because automation cannot reach the challenge path or reload the service.

### 4. Wildcard or broad certificate scope

One certificate or DNS challenge path covers more names than expected.

## Impact

Ordered roughly by severity:

- **Domain takeover path.** Stale DNS may point at reclaimable cloud resources.
- **Service exposure.** DNS makes lab services discoverable and memorable.
- **TLS trust failure.** Expired or wrong certs train users to ignore warnings.
- **Credential exposure.** Misconfigured HTTPS can leave login flows on HTTP.
- **Operational drift.** Old records survive after the lab is gone.

## Detection and defense

Ordered by effectiveness:

1.
**Treat DNS as inventory.**
   Every record should map to an owner, resource, purpose, and teardown condition.

2.
**Protect registrar and DNS accounts.**
   Domain control is a high-impact administrative boundary.

3.
**Use least exposure for validation.**
   Open only the ports and paths required, then close what is no longer needed.

4.
**Monitor certificate renewal.**
   Renewal failures are predictable and should alert before expiry.

5.
**Clean records during teardown.**
   DNS cleanup is part of cloud resource cleanup.

### What does not work as a primary defense

- **Assuming HTTPS means the host is safe.** TLS proves name binding, not application security.
- **Leaving HTTP open because Certbot needed it once.** Validation requirements do not justify permanent exposure.
- **Deleting a VM but leaving DNS.** Stale records become future attack surface.
- **Ignoring DNS account security.** DNS control can redirect all traffic.

## Practical labs

Use a lab domain or subdomain.

### Map DNS to cloud resources

```
Name:
Record type:
Target:
Cloud resource:
Owner:
Expires:
```

Make DNS cleanup explicit.

### Check certificate posture

```
openssl s_client -connect example.com:443 -servername example.com </dev/null
```

Record issuer, SANs, expiry, and chain status.

### Teardown DNS safely

```
Resource deleted:
DNS record removed:
Certificate renewal disabled:
Firewall rules closed:
Verification date:
```

Avoid leaving names pointed at abandoned infrastructure.

### Check HTTP-to-HTTPS behavior

```
curl -I http://lab.example.test/
curl -I https://lab.example.test/
```

Certificate setup should not leave unexpected plaintext paths or admin redirects.

### Track certificate renewal ownership

```
certificate name | renewal method | service reload | owner | alert before expiry | teardown condition
```

Short-lived certificates need operational ownership, not just initial issuance.

## Practical examples

- A Route 53 record points to a deleted load balancer.
- A lab VM opens HTTP for ACME validation and never closes it.
- A Certbot renewal fails after a firewall change.
- A wildcard cert is reused across unrelated lab services.
- A domain registrar account lacks MFA.

## Related notes

- [[cloud-lab-infrastructure]]
- [[cloud-network-boundaries]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS and HTTPS]]
- [[subdomain-takeover|Subdomain Takeover]]

### Suggested future atomic notes

- cloud-dns-takeover
- acme-dns-challenges
- certificate-renewal-monitoring
- cloud-load-balancer-tls

## References

- **Official Docs:** AWS Route 53 Developer Guide — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Official Docs:** Certbot documentation — https://eff-certbot.readthedocs.io/en/stable/
- **Official Docs:** Let's Encrypt documentation — https://letsencrypt.org/docs/
