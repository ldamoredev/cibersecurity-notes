---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# NAT and Private Networks

## Definition

Private networks use IP address ranges that are **not routable on the public Internet**, by design. NAT (Network Address Translation) lets hosts in those ranges talk to public destinations by rewriting their source addresses on the way out, and rewriting the destination addresses on the way back. The combination is the substrate of nearly every modern deployment: home networks, corporate LANs, cloud VPCs, container networks, and Kubernetes pod networks all use private addressing plus NAT.

The single security mistake this whole topic exists to refute: **"this address range is not routable from the Internet, therefore it is safe."** Reachability is a property of the network *path*, not of the address. A compromised public-facing service has the path; an attacker via SSRF has the path; a misconfigured container neighbor has the path. Private addressing is a deployment convenience, not a security boundary.

## Why it matters

The "internal vs external" distinction is the single most-overestimated boundary in production:

- **SSRF impact amplification.** Server-side request forgery hits its highest impact when the app's own VPC contains internal-only services (databases, admin APIs, metadata endpoints) the attacker cannot reach directly. See [[ssrf|SSRF]] and [[metadata-endpoints]].
- **Lateral movement.** A flat private subnet makes one compromised workload a launchpad to every neighbor. Cloud security groups frequently default to `0.0.0.0/0` egress and `10.0.0.0/16` intra-subnet ingress.
- **Cloud-credential exposure.** Cloud-instance metadata endpoints sit on the link-local address space (169.254.0.0/16). Any process inside the VM that can issue an outbound HTTP request can read short-lived IAM credentials. See [[metadata-endpoints]].
- **Trust-by-IP shortcuts.** "Internal = trusted" allowlists collapse the moment a public-facing service forwards a request on the attacker's behalf, or one workload in the private network is compromised.
- **Container and pod networking blur the boundary.** Kubernetes pods share node-local network namespaces; a misconfigured `hostNetwork: true` pod sees the node's interfaces directly.

## How it works

Modern operators meet **6 reserved address blocks** repeatedly. Recognizing them on sight is the entry point for any reachability discussion.

| Range | RFC | Purpose |
| --- | --- | --- |
| `10.0.0.0/8` | RFC 1918 | Private (large enterprise / cloud VPC) |
| `172.16.0.0/12` | RFC 1918 | Private (mid-size, also Docker default) |
| `192.168.0.0/16` | RFC 1918 | Private (home, small office) |
| `127.0.0.0/8` | RFC 1122 | Loopback (`localhost`) |
| `169.254.0.0/16` | RFC 3927 | Link-local — and the home of cloud metadata services |
| `100.64.0.0/10` | RFC 6598 | Carrier-grade NAT (CGNAT) |

IPv6 equivalents:
- `fc00::/7` — Unique Local Addresses (ULA), the IPv6 RFC 1918.
- `fe80::/10` — link-local.
- `::1/128` — loopback.

NAT comes in **3 modes** that have meaningfully different security properties.

1. **1:1 NAT (basic NAT)** — one private IP maps to one public IP. Common in cloud "elastic IP" / "static NAT" deployments. The private host still has a stable public identity; its outbound and inbound flows are symmetric.
2. **NAPT / PAT (Port Address Translation)** — the canonical "many private hosts behind one public IP" mode. Source port is rewritten so return traffic can be demultiplexed. This is what home routers and most cloud NAT gateways do. Outbound flows are stateful; inbound flows are blocked unless explicit port-forwarding is configured. **The privacy property is incidental.** A connection initiated from inside punches a hole that anything on the outside can answer back through, until the state expires.
3. **CGNAT** — a second tier of NAPT operated by the ISP, used for IPv4 exhaustion. Many subscribers share one public IP. From an attacker perspective, "block this IP" affects many users at once; from a defender perspective, "trust this IP" trusts many users at once.

A practical request showing the layered translation:

```
Container (172.17.0.5) → Host (192.168.1.20) → Home router (203.0.113.42) → Internet
       NAPT inside Docker         NAPT inside the home router
```

By the time the request hits the public Internet, the original source has been rewritten twice. Each NAT hop maintains its own state table; loss of state (router reboot, idle timeout) drops the flow.

The bug is rarely in NAT itself. The bug is in the chain of trust assumptions: "this came from inside my VPC so it's safe" — without verifying whether *anything inside the VPC* might be issuing requests on behalf of an attacker.

## Techniques / patterns

What attackers and operators look at:

- **Identify the address space.** `ip addr`, `ipconfig`, `route -n`, cloud console — what private ranges does the host see, and what does it route where? The first probe in any internal-reachability investigation.
- **Test SSRF reachability against private ranges.** From a compromised public-facing app, can it issue requests to `10.x`, `192.168.x`, `172.16.x`, `127.0.0.1`, `169.254.169.254`? Each is a separate gate; many SSRF defenses block one and forget the rest. See [[ssrf|SSRF]].
- **Probe link-local space.** `169.254.169.254`, `fe80::`, vendor-specific VM-host addresses (`10.0.2.2` in VirtualBox NAT, `host.docker.internal` in Docker Desktop). Each is a "leak from container to host" candidate.
- **Look for NAT hairpinning.** A service in a private subnet reaches itself through its public IP and is treated as an external client, sometimes with looser ACLs than the internal path applies.
- **Recognize cloud-VPC defaults.** AWS `default` VPC has `0.0.0.0/0` egress and intra-VPC `10.0.0.0/16` allow. Many "private" services are reachable from any sibling instance.
- **Check container network namespaces.** Pods/containers on the same node see each other; on the same network plugin see neighbors; with `hostNetwork: true` see the node's full network stack.

## Variants and bypasses

"Internal means safe" fails in **4 specific ways**. Each is its own attack class with its own ceiling.

### 1. SSRF flattens the boundary

A public-facing app accepts URLs and fetches them server-side. The fetcher is *inside* the private network. The attacker's request now traverses paths the firewall was supposed to block. The attacker never reaches the private service directly — the app does, on the attacker's behalf. Highest-impact when this lands on metadata endpoints (cloud credential theft) or admin APIs (often unauthenticated because "internal").

### 2. Lateral movement in flat subnets

One compromised workload is one hop from every neighbor on the same subnet. AWS default security groups, Kubernetes network-policy-less clusters, and most home networks are flat. Default cloud images run sshd, kubelet API, container runtime sockets, and database listeners with no expectation of an attacker on the same /16.

### 3. Container/pod boundary leaks

- `hostNetwork: true` on a pod exposes the node's full network stack to the pod, including link-local metadata.
- Docker bridge networking with no explicit `--internal` lets containers route to the host and beyond.
- Misconfigured CNI plugins (Calico/Cilium/Flannel) leak between namespaces.
- The container runtime socket (`/var/run/docker.sock`, containerd) bind-mounted into a pod is "container escape with extra steps."

### 4. NAT hairpinning and trust-by-source-IP

When an internal service reaches its own public IP, the NAT gateway loops the connection back through the public path. The receiving service sees the connection arriving from "outside" but with internal-trust expectations. Combined with public allowlists keyed on the corporate egress IP, this lets an internal attacker masquerade as the corporate edge to an internal API.

## Impact

Ordered roughly by severity:

- **Cloud-credential theft** — SSRF + metadata endpoint reachability → instance IAM credentials → cloud-account compromise. Owns the depth: [[metadata-endpoints]].
- **Internal admin / debug API exposure** — unauthenticated `/admin`, `/metrics`, `/debug`, `/actuator/*`, kubelet API, etcd, Redis, Memcached, Elasticsearch. "Internal" assumption substituted for authentication.
- **Database direct access** — Postgres/MySQL/MongoDB listening on a private IP with weak or default credentials, reachable from any workload in the same subnet.
- **Lateral movement** — one popped container becomes a vantage point for every other workload. Privilege escalation often follows because the next workload runs with broader IAM.
- **Cross-tenant leaks in multi-tenant clusters** — flat networking + shared CNI + shared node = one tenant's compromise reaches another's pod.
- **Trust-by-IP bypass** — a "we only allow corporate egress IP" allowlist collapses when an internal attacker reaches the corporate egress and then loops back.

## Detection and defense

Ordered by effectiveness:

1.
**Treat private networks as untrusted by default (zero trust).**
   The internal/external distinction is a deployment fact, not a security boundary. Every service authenticates every caller — mTLS, signed tokens, hardware keys. Network reachability is a layer of defense-in-depth, not the primary control. This single posture defeats the entire "internal = safe" failure family.

2.
**Micro-segment the private network.**
   Break the flat subnet into many small zones with explicit ingress/egress rules between them. Cloud: per-service security groups, AWS Network Firewall, GCP firewall rules with target tags, Azure NSGs. Kubernetes: NetworkPolicy resources (deny-all default, then explicit allow). The goal is "compromise of one workload reaches one other workload at most."

3.
**Block egress to private and link-local ranges from public-facing services.**
   The fetcher in your image-thumbnail service has no business connecting to `10.0.0.0/8`, `127.0.0.1`, or `169.254.169.254`. Enforce at the network layer (egress security groups, network policies, application-mesh policy) rather than relying on the app to refuse. This is the SSRF-impact-cap defense; combine with the application-level URL allowlist.

4.
**Configure cloud metadata service hardening.**
   AWS IMDSv2 with `HttpPutResponseHopLimit: 1` (so containers and pods cannot reach it through the host). GCP and Azure require explicit headers (`Metadata-Flavor: Google`, `Metadata: true`) which a naive SSRF cannot supply. See [[metadata-endpoints]] for the long version.

5.
**Disable container host-network and runtime-socket bind-mounts.**
   `hostNetwork: true`, `hostPID: true`, `hostIPC: true`, and bind-mounts of `/var/run/docker.sock` are escape primitives. Block in admission controllers (PSA / Kyverno / OPA Gatekeeper).

6.
**Audit security-group and NetworkPolicy defaults.**
   `0.0.0.0/0` egress is the wrong default. Intra-VPC `allow all` is the wrong default. Ship with `deny-all` and explicit allow-rules; force every new service to declare its egress.

7.
**Watch for NAT hairpinning when designing IP allowlists.**
   Trust-by-source-IP based on the corporate egress IP must account for the case where an internal attacker reaches the corporate egress. Pair every IP allowlist with mutual auth so the IP is one factor of two.

### What does not work as a primary defense

- **"It's in a private subnet."** Any path the application has, an attacker with a server-side request primitive has too. The address range is not the boundary.
- **Blocking `127.0.0.1` only.** RFC 1918 private ranges, link-local, and IPv6 ULA all need to be blocked too. Each is a separate gate the SSRF defense must close.
- **Trusting `Host:` or `X-Forwarded-Host:` for "is this internal?"** Header content is data. The connection's source IP is the only network-layer evidence, and even that is forgeable if NAT hairpinning is in play.
- **Default cloud security groups.** AWS default VPC, GCP default network, Azure default NSG all favor connectivity over isolation. Treat defaults as a starting point, not a finished posture.
- **Kubernetes without NetworkPolicy.** A cluster with no policies allows pod-to-pod traffic in every direction. CNI installation is not policy enforcement; you must write the rules.

## Practical labs

Stock `ip`, `nc`, `curl`, plus `dig` for cloud-DNS investigations.

### Identify the local network landscape

```
# Linux: which addresses does this host see, and how is it routing?
ip addr
ip route
ip -6 route

# macOS variants
ifconfig
netstat -rn

# Cloud: what is the instance's view of itself? (See metadata-endpoints note for safer probes.)
hostname -I
```

### Probe SSRF reach into private space

```
# From a public-facing host you control, simulate an SSRF fetcher's reach.
# Replace 10.0.0.5 with the actual private target.
for target in 127.0.0.1 169.254.169.254 10.0.0.5 192.168.1.1 172.17.0.1; do
  printf '%-20s -> ' "$target"
  curl -s --max-time 3 -o /dev/null -w '%{http_code}\n' "http://$target/" || echo "fail"
done

# Also test IPv6 link-local — many SSRF allowlists forget it
curl -s --max-time 3 -o /dev/null -w '%{http_code}\n' 'http://[fe80::1]/'
```

### Discover internal services on a subnet

```
# Sweep a /24 for live hosts and common admin ports — RUN ONLY AGAINST RANGES YOU OWN
for ip in 10.0.0.{1..254}; do
  (nc -zw1 "$ip" 22 2>/dev/null && echo "$ip ssh") &
  (nc -zw1 "$ip" 6443 2>/dev/null && echo "$ip kube-api") &
  (nc -zw1 "$ip" 2379 2>/dev/null && echo "$ip etcd") &
  (nc -zw1 "$ip" 6379 2>/dev/null && echo "$ip redis") &
done | sort -V
wait

# Or use nmap if available
nmap -sT -Pn -p 22,80,443,2379,6379,6443,8080,9200 10.0.0.0/24
```

### Test container → host reach

```
# Inside a container, can you reach the host's link-local / metadata?
curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/
curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' http://host.docker.internal/  # Docker Desktop only

# Inside a Kubernetes pod, what subnet do you see?
ip addr
nslookup kubernetes.default.svc.cluster.local
nslookup metadata.google.internal  # if running on GKE
```

### Probe NAT hairpin behavior

```
# From inside the network, request the public IP/hostname and see if it loops back.
# Useful when designing or auditing IP-allowlist controls.
curl -sI https://example.com/internal-api -H 'X-Forwarded-For: 10.0.0.99'
# If a public-IP-allowlisted endpoint returns 200 from a private host hairpinning out
# and back through NAT, the allowlist substitutes for auth dangerously.
```

### Audit Kubernetes pod-network exposure

```
# List pods with hostNetwork or runtime-socket mounts — both are escape primitives
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.hostNetwork == true) | "hostNetwork \(.metadata.namespace)/\(.metadata.name)"'

kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.volumes[]?.hostPath.path | tostring | test("docker.sock|containerd.sock|crio.sock")) | "runtime-socket \(.metadata.namespace)/\(.metadata.name)"'

# Check NetworkPolicy coverage
kubectl get networkpolicy --all-namespaces
```

## Practical examples

- A public Node.js image-thumbnail service accepts a `url` parameter and `fetch()`es it. The service runs in an EC2 instance in a VPC. An attacker submits `http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name` and receives the EC2 instance's IAM credentials.
- A Kubernetes cluster has no NetworkPolicy. A compromised customer-facing pod connects to `10.x.x.x:6379` (cluster Redis), reads cached session tokens, and impersonates other tenants.
- A Java webhook handler accepts URLs and posts to them. The "URL allowlist" blocks `127.0.0.1` and `localhost` but not `0.0.0.0`, `[::]`, or `169.254.169.254`. SSRF reaches metadata.
- A corporate API allowlists the corporate egress IP. An internal employee on the corporate VPN hairpins through NAT and is treated as a trusted external client. Their compromised browser session reaches an internal-only admin path that public clients are denied.
- A Docker Compose dev environment runs `app` and `postgres` containers on the default bridge network with port 5432 published to the host. The developer is on Wi-Fi; a guest on the same Wi-Fi reaches `host-laptop.local:5432` and the app's "I'm in a private network" assumption shatters.
- An HCL module deploys a "private" RDS instance with `publicly_accessible = false`. The security group allows `10.0.0.0/16` (the whole VPC). Every workload — including the public-facing web app's pod — has direct database access without going through the application layer.

## Related notes

- [[tcp-ip-basics]] — addressing fundamentals; private vs public ranges.
- [[firewalls-and-network-boundaries]] — the network-layer enforcement of segmentation.
- [[metadata-endpoints]] — the link-local cloud-credential gateway. Highest-impact SSRF target.
- [[ssrf|SSRF]] — the application-layer primitive that flattens the public/private boundary.
- [[reverse-proxies]] — the trust-translation layer that often sits between public and private.
- [[client-ip-trust]] — IP-allowlist subtleties, NAT hairpinning impact on source-IP trust.
- [[ports-and-services]] — discovering what's listening on a private subnet.
- [[dns-resolution]] / [[dns-security]] — internal DNS and split-horizon are the naming layer of private networks.
- [[internal-attack-surface|Internal attack surface]]
- [[trace-metadata-endpoint-reachability|Trace metadata endpoint reachability]]

### Suggested future atomic notes

- cloud-vpc-defaults
- kubernetes-networkpolicy
- container-escape-primitives
- ssrf-allowlist-design
- ipv6-private-ranges
- nat-hairpinning
- zero-trust-network-architecture

## References

- **Foundational:** RFC 1918 (Private Address Allocation) — https://datatracker.ietf.org/doc/html/rfc1918
- **Foundational:** RFC 6598 (CGNAT shared address space) — https://datatracker.ietf.org/doc/html/rfc6598
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
