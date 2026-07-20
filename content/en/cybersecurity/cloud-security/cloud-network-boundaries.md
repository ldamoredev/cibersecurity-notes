---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Network Boundaries

## Definition

Cloud network boundaries are the VPC, subnet, route, firewall, security group, private endpoint, and exposure controls that decide which cloud resources can talk to each other and to the internet.

## Why it matters

Cloud networking looks familiar, but it is controlled by APIs and defaults that differ from physical networks. Public IPs, route tables, security groups, load balancers, NAT gateways, and private endpoints combine into effective reachability.

The cloud lesson is that reachability is the result of multiple layers, not one firewall checkbox.

## How it works

Cloud reachability has **6 layers**:

1. **Addressing.** Public and private IPs decide possible paths.
2. **Routing.** Route tables, gateways, NAT, and peering decide where packets go.
3. **Firewall rules.** Security groups, NSGs, and firewall policies allow or deny traffic.
4. **Service exposure.** Load balancers, public endpoints, and private endpoints publish services.
5. **Identity controls.** Some cloud services require IAM even when network-reachable.
6. **Workload controls.** Host firewalls and application auth still matter.

The bug is not any one layer. The bug is assuming one layer expresses the whole boundary.

A worked example, public path through multiple layers:

```
Resource:
  app-origin VM

Addressing:
  private IP plus public load balancer

Routing:
  subnet has route to internet gateway through load balancer path

Firewall:
  origin security group allows 443 from 0.0.0.0/0

Service exposure:
  CDN also points to the same origin

Decision:
  intended edge path exists, but origin is directly reachable; restrict origin to CDN/load-balancer sources
```

Cloud network review should trace the path a packet can actually take, not the diagram label.

## Techniques / patterns

Reviews look at:

- public IP inventory
- internet gateways and default routes
- inbound `0.0.0.0/0` or `::/0` rules
- admin ports exposed to the internet
- peering and VPN paths
- security group references and broad internal rules
- private endpoint and service endpoint assumptions

## Variants and bypasses

Cloud boundary failures have **5 common shapes**.

### 1. World-open admin port

SSH, RDP, database, or dashboard ports are reachable from anywhere.

### 2. Flat private network

Private subnets allow broad east-west movement.

### 3. Peering surprise

A trusted connection exposes more routes than intended.

### 4. Load balancer bypass

The origin host remains directly reachable.

### 5. IPv6 exposure

IPv6 rules or addresses expose services missed by IPv4-only reviews.

## Impact

Ordered roughly by severity:

- **Public compromise path.** Exposed admin or database ports invite direct attacks.
- **Lateral movement.** Flat cloud networks let one workload reach many others.
- **Control bypass.** Direct-origin access bypasses WAF, auth, or logging at the edge.
- **Metadata risk.** Network design affects metadata and internal service reachability.
- **Inventory drift.** Public resources appear faster than teams review them.

## Detection and defense

Ordered by effectiveness:

1.
**Inventory public ingress continuously.**
   Public IPs and broad inbound rules should be treated as attack surface.

2.
**Default to least-reachability rules.**
   Only required sources and ports should be allowed.

3.
**Segment environments and trust zones.**
   Dev, prod, admin, data, and lab networks should not share a flat path.

4.
**Protect origins behind load balancers.**
   Backends should accept traffic only from expected front doors.

5.
**Review IPv4 and IPv6 together.**
   Dual-stack environments need dual-stack security review.

### What does not work as a primary defense

- **Calling a subnet private.** Routes, peering, SSRF, and compromised workloads can still reach it.
- **Using security group names as evidence.** Effective rules matter.
- **Reviewing only inbound traffic.** Egress and east-west paths matter for compromise.
- **Assuming load balancers hide origins.** Direct origin reachability must be tested.

## Practical labs

Use a sandbox VPC/VNet only.

### Public ingress table

```
Resource:
Public IP/DNS:
Port:
Allowed source:
Owner:
Reason:
Expiry:
```

This is the cloud equivalent of a service-exposure map.

### Origin bypass check

```
Load balancer DNS:
Origin IP:
Origin accepts direct traffic:
Allowed source rule:
Expected behavior:
```

Backends should not be public by accident.

### Route boundary review

```
Subnet:
Default route:
Internet/NAT gateway:
Peering/VPN:
Private endpoints:
Sensitive destinations:
```

Reachability is route plus rule plus service.

### Compare intended and effective ingress

```
resource | intended source | effective allowed source | port | reason | fix
```

Most cloud boundary findings are differences between intended and effective reachability.

### Review east-west reachability

```
source workload | destination | port | required? | rule enabling it | owner
```

Private network exposure still matters after one workload is compromised.

## Practical examples

- A database port is open to the internet for debugging.
- A private subnet routes through peering to a production network.
- An origin VM accepts traffic directly around a WAF.
- IPv6 allows access that IPv4 security groups blocked.
- A lab security group remains world-open after teardown.

## Related notes

- [[cloud-security-basics]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-metadata-security]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[external-attack-surface|External Attack Surface]]

### Suggested future atomic notes

- cloud-vpc-defaults
- private-endpoints
- cloud-egress-control
- ipv6-cloud-exposure

## References

- **Official Docs:** AWS VPC security groups — https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- **Official Docs:** Google Cloud VPC firewall rules — https://cloud.google.com/firewall/docs/firewalls
- **Official Docs:** Azure network security groups — https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview
