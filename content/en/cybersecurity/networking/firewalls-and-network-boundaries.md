---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Firewalls and Network Boundaries

## Definition

Firewalls and network boundaries are controls that decide which traffic may cross between networks, hosts, workloads, and services. In cloud and container environments, the same idea appears as security groups, network ACLs, route tables, private subnets, ingress policies, egress policies, service mesh rules, and Kubernetes NetworkPolicy.

## Why it matters

A service can be well written and still be dangerously reachable. Boundaries are where intended architecture becomes enforceable: public vs private, frontend vs database, workload vs metadata, user vs admin, tenant vs tenant.

The recurring lesson: **a boundary is real only if blocked paths actually fail from the relevant viewpoint**.

## How it works

Network-boundary review asks **5 questions**:

1. **What source is allowed?** Public internet, CDN, VPN, bastion, subnet, service account, pod label, or security group.
2. **What destination is protected?** Host, port, service, subnet, namespace, or cloud resource.
3. **What direction matters?** Inbound, outbound, east-west, or return traffic.
4. **Which layer enforces it?** Firewall, security group, NACL, load balancer, route table, service mesh, or app proxy.
5. **How is it verified?** Nmap, `nc`, logs, flow logs, packet capture, or cloud inventory.

Example intended policy:

```
Internet -> CDN/WAF/load balancer : 443 allowed
CDN/WAF/load balancer -> app       : 443 allowed
Internet -> app origin             : blocked
app -> database                    : 5432 allowed
Internet -> database               : blocked
app -> metadata endpoint           : blocked unless needed
```

The bug is the unexpected allowed path, not merely the existence of a firewall.

## Techniques / patterns

Attackers and defenders inspect:

- public vs private reachability for each service
- direct origin access around CDN/WAF/load balancer controls
- overly broad source ranges such as `0.0.0.0/0` or `::/0`
- database/cache/admin ports exposed outside intended subnets
- east-west movement between internal services
- egress to metadata endpoints, private ranges, and the internet
- VPN/bastion assumptions
- IPv6 policy parity
- cloud security group and route-table drift

## Variants and bypasses

Boundary failures fall into **6 practical classes**.

### 1. Public inbound overexposure

A service accepts internet traffic when it should only accept proxy, VPN, bastion, or internal source traffic.

### 2. Direct-origin bypass

The CDN, WAF, or load balancer is protected, but the backend origin is reachable directly by IP or alternate hostname.

### 3. East-west flatness

Internal workloads can freely reach databases, admin panels, metadata endpoints, and peer services after one foothold.

### 4. Egress gaps

Outbound rules allow user-controlled fetchers, compromised workloads, or CI jobs to reach private ranges, metadata services, or arbitrary internet destinations.

### 5. IPv6 mismatch

IPv4 boundaries are tight while IPv6 allows broader reachability.

### 6. Policy drift and shadow rules

Temporary incident rules, old security groups, duplicated cloud accounts, or manual exceptions remain after the reason disappears.

## Impact

Ordered roughly by severity:

- **Public exposure of sensitive services.** Databases, caches, admin panels, and backends become reachable by attackers.
- **Control bypass.** Direct origin access skips WAF, CDN auth, TLS policy, rate limits, or logging.
- **Lateral movement.** A compromised workload reaches internal services because segmentation is flat.
- **SSRF amplification.** Server-side fetchers can reach private networks or metadata endpoints.
- **Data exfiltration.** Overbroad egress lets compromised workloads send data anywhere.
- **False assurance.** Architecture diagrams claim private boundaries that live rules do not enforce.

## Detection and defense

Ordered by effectiveness:

1.
**Default-deny sensitive paths.**
   Databases, caches, admin services, metadata endpoints, and backends should be unreachable unless a specific source and port is required.

2.
**Constrain source ranges to real upstreams.**
   Backends behind a CDN/load balancer should accept traffic only from that upstream's private/security-group identity or documented IP range, not the whole internet.

3.
**Validate from multiple viewpoints.**
   Public internet, VPN, internal subnet, container, and cloud workload tests should match the intended trust model. A blocked public path is not enough if an SSRF path can reach it.

4.
**Segment east-west traffic deliberately.**
   Use subnet rules, security groups, Kubernetes NetworkPolicy, service mesh policy, or host firewalls to limit what workloads can initiate internally.

5.
**Control egress for risky workloads.**
   URL fetchers, renderers, CI runners, and internet-facing apps should not freely reach metadata, loopback, link-local, private ranges, or arbitrary destinations unless needed.

6.
**Continuously diff policy against inventory.**
   Cloud rules drift. Alert on `0.0.0.0/0`, `::/0`, new public IPs, new listener ports, and rules without owners or expiration.

7.
**Log boundary decisions.**
   Flow logs, firewall logs, load-balancer logs, and rejected-connection metrics turn invisible boundary assumptions into evidence.

### What does not work as a primary defense

- **Network names as controls.** `internal.example.com` is not a boundary.
- **NAT alone.** NAT is translation, not authorization.
- **WAF in front, origin exposed behind.** Attackers will look for the origin IP.
- **One-time firewall reviews.** Temporary exceptions become permanent.
- **Inbound-only thinking.** SSRF, malware, and CI abuse often depend on outbound reachability.
- **IPv4-only policy.** IPv6 can create a parallel public path.

## Practical labs

Run only in authorized environments.

### Compare public and internal reachability

```
target=app.example.com
for port in 22 80 443 5432 6379 8080; do
  nc -vz -w 3 "$target" "$port"
done
```

Repeat from public internet, VPN, internal subnet, and a cloud workload.

### Scan for unexpected public services

```
nmap -Pn --top-ports 1000 your-host.example.com
nmap -Pn -p 22,80,443,5432,6379,9200,9300 your-host.example.com
```

Treat unexpected open ports as ownership questions.

### Check direct-origin bypass

```
origin_ip=203.0.113.42
curl -skI "https://$origin_ip/" -H 'Host: app.example.com' --connect-timeout 5
```

Expected: timeout, reset, or explicit denial unless direct origin access is intended.

### Test egress to metadata and private ranges

```
curl -s --max-time 2 http://169.254.169.254/ || true
curl -s --max-time 2 http://10.0.0.1/ || true
```

Run only from workloads you own. Public-facing apps should usually block these paths unless needed.

### Inspect local firewall/listener state

```
lsof -i -P -n | rg 'LISTEN|UDP'
iptables -S 2>/dev/null || true
pfctl -sr 2>/dev/null || true
```

Local host firewalls and bind addresses may differ from cloud boundary rules.

### Review cloud rules for broad exposure

```
# AWS example: review security groups for public ingress.
aws ec2 describe-security-groups \
  --query 'SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,Ingress:IpPermissions}' \
  --output json
```

Look for public source ranges on sensitive ports and rules without owners.

## Practical examples

- A backend accepts traffic from `0.0.0.0/0` even though all intended traffic should arrive through the load balancer.
- A database security group allows the office IP, but a contractor VPN expands that range far beyond the intended team.
- A Kubernetes namespace has no NetworkPolicy, so every pod can reach every other pod.
- An SSRF-prone PDF renderer can reach `169.254.169.254`.
- IPv6 security groups allow SSH globally while IPv4 rules restrict it.

## Related notes

- [[ports-and-services]] — what is listening and exposed.
- [[nmap-scanning]] — validating reachable ports.
- [[nat-and-private-networks]] — private reachability and path assumptions.
- [[metadata-endpoints]] — link-local cloud credential exposure.
- [[load-balancers]] — public entrypoints and backend reachability.
- [[reverse-proxies]] — application-layer trust boundary.
- [[ssrf|SSRF]] — server-side reachability abuse.
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — what boundary traffic actually produces as evidence.
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]] — defender-side interpretation of boundary probing.

### Suggested future atomic notes

- network-segmentation
- egress-control
- direct-origin-bypass
- security-group-review
- kubernetes-networkpolicy
- ipv6-firewall-parity

## References

- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Mitigation:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
