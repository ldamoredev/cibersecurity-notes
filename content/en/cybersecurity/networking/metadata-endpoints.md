---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Instance Metadata Endpoints

## Definition

Cloud-instance metadata endpoints are HTTP services hosted by the cloud provider on a **link-local address** (typically `169.254.169.254`) that any process running inside the virtual machine can query without authentication. They expose information about the instance — region, identity, user-data — and, critically, **short-lived IAM credentials for the role attached to the instance**. The same primitive exists across every major cloud, with subtle protocol differences that matter for attacker tooling and for defenders writing SSRF allowlists.

The single sentence that explains why this whole topic exists: **the metadata endpoint binds the cloud's IAM permissions to the network-layer property "any process inside this VM"**, which the application's security model usually does not.

## Why it matters

Instance metadata services are the highest-impact SSRF target on the public Internet, by a wide margin. A vulnerability in any application that issues outbound HTTP requests in response to attacker input — image fetchers, webhook handlers, URL previews, RSS readers, OpenID/OAuth flows, JWKS fetchers, server-side iframe embedders — becomes a direct path to the instance's IAM credentials. Those credentials usually permit the application's normal cloud operations: read S3 buckets, write to queues, call internal APIs, sometimes assume other roles.

This matters for four specific reasons:

- **The endpoint is reachable from anything in the VM.** Containers, pods, sidecars, and the application itself all share the same network namespace by default unless the operator did something deliberate to block this.
- **The credentials are real.** They are STS / token-broker credentials with the same permissions the application uses. Not test creds, not scoped, not gated by additional auth.
- **Defenses that "look right" often miss it.** SSRF allowlists that block `127.0.0.1` and `localhost` and forget `169.254.169.254` are extremely common. So are URL parsers that allow `0.0.0.0`, IPv6 mapped addresses, or DNS-rebinding tricks.
- **Detection is rare.** Metadata fetches look like ordinary outbound HTTP from inside the VM. CloudTrail / GCP audit logs see the *use* of the credentials, not the *theft* of them.

## How it works

The metadata service is just an HTTP server on a link-local address that returns text or JSON when queried. **4 properties** make it dangerous:

1. **Link-local reachability.** `169.254.169.254` is in `169.254.0.0/16` (RFC 3927) — not routable on the public Internet, but reachable from any process that can issue a TCP/HTTP request from inside the VM.
2. **No authentication by default** (or trivially weak header-only "auth" — see Variants).
3. **Returns short-lived credentials** for the IAM role attached to the instance. Token validity is usually 1–12 hours; refreshing requires only re-asking the endpoint.
4. **Bypasses the application's security model entirely.** The app's authn/authz, its rate limits, its allowlist — all of these are *application-layer* controls. The metadata endpoint is a *network-layer* primitive that sits underneath all of them.

The canonical attack request, AWS IMDSv1:

```
GET /latest/meta-data/iam/security-credentials/ HTTP/1.1
Host: 169.254.169.254
```

Response: a list of role names. Then:

```
GET /latest/meta-data/iam/security-credentials/<role-name> HTTP/1.1
Host: 169.254.169.254
```

Response, JSON, including:

```
{
  "Code": "Success",
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "FwoG...",
  "Expiration": "2026-04-28T11:59:00Z"
}
```

These three values are immediately usable as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` for any AWS API the role permits.

The bug is rarely "the metadata service exists." The bug is the absence of one of: a hardened metadata mode (IMDSv2), a network-layer block on link-local egress from public-facing workloads, or an application-layer SSRF defense that closes the link-local gate explicitly.

## Techniques / patterns

What attackers and operators look at:

- **Confirm the cloud first.** `169.254.169.254` answers on AWS, Azure, DigitalOcean, Oracle, Alibaba; GCP responds at `169.254.169.254` *and* `metadata.google.internal`. The exact paths and required headers differ; sending the wrong shape returns 401/403/404 and reveals the cloud.
- **Look for SSRF primitives.** URL fetchers, webhook deliverers, image proxies, OpenID-discovery fetchers, XML/SVG with external entities, OAuth `redirect_uri` validators that follow the URL.
- **Read the role policy.** Once credentials are exfiltrated, `aws sts get-caller-identity` and `aws iam get-account-authorization-details` (or `gcloud auth list`, `az account show`) reveal what the role can do. Most roles are over-scoped.
- **Recognize SSRF allowlist gaps.** Common bypass shapes: `0.0.0.0`, IPv4 in dotted-decimal-as-integer (`http://2852039166/`), IPv6-mapped (`[::ffff:169.254.169.254]`), DNS records pointing at `169.254.169.254`, redirect chains that the app follows blindly, raw `fetch()` calls in JS-side rendering.
- **Check the hop limit.** AWS IMDSv2 lets the operator set a TTL (`HttpPutResponseHopLimit`) on the metadata response; with a hop limit of 1, traffic from inside a Docker container or Kubernetes pod can't reach back. With the default of 1 set correctly, container compromises can't pivot to host credentials. With the default of 64 (or unset), they can.
- **Pivot via assume-role.** If the harvested credentials can `sts:AssumeRole`, the blast radius extends to every role they can chain to — across accounts when trust policies allow it.

## Variants and bypasses

Each cloud's metadata service has its own protocol shape. Treating them as one is a defender mistake; using the wrong one is an attacker mistake. **6 variants** matter in practice.

### 1. AWS IMDSv1

GET against `http://169.254.169.254/latest/meta-data/...`, no auth, no required headers. The default on instances launched before late 2019. Still extremely common in production. Trivially exploitable via any SSRF.

### 2. AWS IMDSv2

Token-based: a `PUT /latest/api/token` request with `X-aws-ec2-metadata-token-ttl-seconds: 21600` returns a session token; subsequent `GET` requests must carry `X-aws-ec2-metadata-token: <token>`. **Two properties make IMDSv2 hard to abuse via SSRF**: the `PUT` method (most SSRF primitives only do GET) and the custom request header (most SSRF primitives can't set arbitrary headers). Also supports `HttpPutResponseHopLimit` to block container reach-through. Switching from IMDSv1 → IMDSv2-required is the single highest-leverage hardening on AWS.

### 3. GCP metadata

`http://metadata.google.internal/computeMetadata/v1/...` (also reachable at `169.254.169.254`). Requires header `Metadata-Flavor: Google` on every request. Header-required posture means most basic SSRF primitives can't reach it. Returns service-account credentials at `/computeMetadata/v1/instance/service-accounts/default/token`.

### 4. Azure IMDS

`http://169.254.169.254/metadata/instance?api-version=2021-02-01`. Requires header `Metadata: true`. Tokens fetched at `/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/`.

### 5. DigitalOcean / Alibaba / Oracle

DigitalOcean: `http://169.254.169.254/metadata/v1/`. Alibaba Cloud and Oracle Cloud each have their own variants. Less commonly targeted but exist; if your application runs there, the same defense pattern applies.

### 6. Kubernetes service account tokens (the metadata-adjacent variant)

Pods get JWTs at `/var/run/secrets/kubernetes.io/serviceaccount/token` (file, not HTTP) which authenticate to the kube-apiserver at `https://kubernetes.default.svc`. Not a metadata endpoint per se, but the same shape: link-local-ish identity primitive that credentials any process in the pod, no application-layer gate. Defense: bind service accounts to least privilege; mount with `automountServiceAccountToken: false` where possible.

## Impact

Ordered by severity:

- **Cloud-account compromise.** Harvested credentials let the attacker exercise every IAM permission the role holds. In poorly scoped accounts, this reaches data exfiltration, privilege escalation via `iam:PassRole` chains, persistence (creating new IAM users / access keys), and pivoting into other accounts when cross-account trust policies allow it.
- **Data exfiltration from cloud storage.** S3, GCS, Azure Blob — most application roles can read at least some buckets the attacker cannot reach directly.
- **Internal API access.** Internal services that authenticate via SigV4 / metadata-derived identity now answer to the attacker.
- **Lateral movement.** Roles with `sts:AssumeRole` or analogous cross-role chains let the attacker pivot to higher-privilege roles. See [[nat-and-private-networks]] for the lateral-movement framing.
- **Persistence.** Credentials issued by the metadata service refresh automatically; an attacker who keeps stealing fresh tokens has indefinite access until the role is revoked or the application stack is rotated.
- **Cost / abuse.** Compromised credentials run cryptominers, send phishing email, or stage further attacks at the victim's expense.

## Detection and defense

Ordered by effectiveness:

1.
**Switch to the hardened metadata mode and require it.**
   AWS: `MetadataOptions.HttpTokens=required` (IMDSv2-only) and `HttpPutResponseHopLimit=1`. GCP: rely on the `Metadata-Flavor` header and review service-account scope. Azure: rely on `Metadata: true`. Set this at the org/account level — Service Control Policies (AWS), Organization Policies (GCP), Azure Policy — so individual workloads cannot opt out. This single change defeats the overwhelming majority of metadata-via-SSRF attacks.

2.
**Block egress to the link-local range from any workload that takes user input.**
   At the network layer, deny `169.254.0.0/16` (and IPv6 link-local `fe80::/10`) outbound from public-facing pods/instances/functions. Cloud security groups, Kubernetes NetworkPolicy, service-mesh egress policies (Istio, Linkerd) all support this. Pair with the application-level allowlist; do not rely on either alone.

3.
**Application-level URL allowlist with explicit private/link-local denial.**
   Every URL-fetching primitive (image fetcher, webhook deliverer, OAuth redirect validator, RSS reader, PDF renderer) must resolve the hostname, check the resolved IP against an explicit deny-list (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`, `fc00::/7`, `fe80::/10`, `0.0.0.0`), and re-check after every redirect. DNS rebinding is real; resolve once and connect to the resolved IP, not the hostname.

4.
**Use VPC service endpoints / Private Google Access / Azure Private Link.**
   Where the workload's job is "talk to S3 / GCS / a few specific cloud APIs," route via private endpoints with explicit IAM scoping. This both reduces egress dependency on the metadata service for IAM and makes credential theft less useful — many private endpoints can be additionally gated on VPC identity.

5.
**Scope the IAM role aggressively.**
   Default role attached to a public-facing web tier should grant only the specific bucket/queue/secret access it needs, with `Condition` clauses where possible (source VPC, request tag, IP). When credentials leak — and assume they will — least privilege is the difference between "annoying" and "RCE-equivalent."

6.
**Detect anomalous metadata access patterns.**
   GuardDuty (`UnauthorizedAccess:EC2/MetadataDNSRebind`, `Discovery:EC2/PortProbeUnprotectedPort`) and similar GCP/Azure detections cover the obvious cases. Custom: alert on STS calls from IPs / regions / user agents the application doesn't normally use.

7.
**Disable Kubernetes pod automount of service-account tokens** unless the pod actually needs to call the API server.
   `automountServiceAccountToken: false` at the pod-spec level. Enforce via admission control. Many workloads ship with the default-mounted token and never use it; that token is just sitting there waiting for a process compromise.

### What does not work as a primary defense

- **Blocking only `127.0.0.1` and `localhost`.** The link-local range, IPv4-as-integer, IPv6-mapped, and `0.0.0.0` are all separate gates. SSRF allowlists that close one and miss the others are the most common metadata-leak path in production.
- **String-matching the URL.** `http://169.254.169.254/`, `http://[::ffff:a9fe:a9fe]/`, `http://2852039166/`, `http://attacker.com/?host=169.254.169.254` (open redirect chained with SSRF), and DNS records pointing at link-local are all the same target. Resolve and check the IP, not the hostname or string.
- **Trusting "the cloud platform handles it."** Cloud defaults often favor compatibility over hardening. IMDSv1 is still allowed by default unless an org policy says otherwise. Default service accounts in GKE and AKS are over-scoped. Defense is your responsibility, not the platform's.
- **WAF rules alone.** WAFs see the application's request; they don't see the application's outbound HTTP. Metadata theft happens on the egress path, which most WAFs don't observe.
- **Long-lived static cloud credentials inside the app.** "We use static credentials so the metadata endpoint doesn't matter." Leaked static credentials are *worse* — they don't expire on their own, and they often have broader scope because operators were too tired to scope them.

## Practical labs

Stock curl. **Run these only against instances you own.** The link-local address is per-VM, but the actions invoke real cloud APIs on credentials that are real money.

### Identify the cloud and try IMDSv1

```
# AWS IMDSv1 (succeeds if not hardened)
curl -s --max-time 2 http://169.254.169.254/latest/meta-data/

# GCP — header required
curl -s --max-time 2 -H 'Metadata-Flavor: Google' \
  http://metadata.google.internal/computeMetadata/v1/

# Azure — header required, query parameter required
curl -s --max-time 2 -H 'Metadata: true' \
  'http://169.254.169.254/metadata/instance?api-version=2021-02-01'

# DigitalOcean
curl -s --max-time 2 http://169.254.169.254/metadata/v1/
```

### Verify AWS IMDSv2 enforcement

```
# IMDSv1 should fail when IMDSv2 is required
curl -s -o /dev/null -w 'imdsv1: %{http_code}\n' --max-time 2 \
  http://169.254.169.254/latest/meta-data/

# IMDSv2 token request
TOKEN=$(curl -s --max-time 2 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)

# Use the token
curl -s --max-time 2 -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/info
```

### Test container reachability (hop-limit verification)

```
# From a Docker container or Kubernetes pod on AWS:
docker run --rm curlimages/curl:latest -s --max-time 2 \
  http://169.254.169.254/latest/meta-data/
# A correctly hop-limited IMDSv2 instance returns timeout / connection refused
# from inside containers; the host still reaches it.
```

### Probe SSRF for metadata reach (lab targets only)

```
# Bypass shapes a hardened SSRF allowlist must defeat
for url in \
  'http://169.254.169.254/' \
  'http://[::ffff:169.254.169.254]/' \
  'http://2852039166/' \
  'http://0177.0.0.1/' \
  'http://0:80/' \
  'http://metadata.google.internal/' ; do
  printf '%-45s -> ' "$url"
  curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' "$url" || echo timeout
done
```

### Use harvested credentials safely (in your own lab)

```
# Pull instance creds, set env, list role's identity — read-only sanity check
TOKEN=$(curl -s -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)
ROLE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/)
CREDS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  "http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE")

export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .Token)

aws sts get-caller-identity
# This is the same shape an attacker exercises after a successful theft.
# In a real audit, this lab confirms your role is over-scoped before the attacker does.
```

### Audit hop-limit and IMDS mode across an account

```
# AWS — list all instances and their metadata-options posture
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table
# Expected: HttpTokens=required, HttpPutResponseHopLimit=1 across the fleet.
```

## Practical examples

- A photo-sharing site lets users provide a remote URL for avatar import. The fetcher runs in EC2 with IMDSv1 enabled. An attacker submits `http://169.254.169.254/latest/meta-data/iam/security-credentials/web-role/`, harvests credentials, and reads every user's profile photo from S3.
- A SaaS webhook system follows redirects on outbound deliveries. Attacker's webhook URL `https://attacker.example/redirect` 302-redirects to `http://169.254.169.254/...`. The webhook system never re-checks the destination after redirect.
- A Kubernetes pod runs an image-OCR microservice that fetches images via URL. The cluster has no NetworkPolicy and runs on EKS with default IMDSv2 hop limit (1). The pod cannot reach the host's metadata directly — but it *can* reach the kubelet API on `127.0.0.1:10250` from inside the pod, which lets it exec into other pods on the same node.
- A GitHub Actions runner runs on a self-hosted EC2 instance with IMDSv1 enabled. A pull request from a fork runs untrusted code. The PR's job script fetches the metadata endpoint and prints the credentials into the public action log.
- A serverless function fetches OAuth provider metadata (`/.well-known/openid-configuration`) via a configurable URL. Misconfigured to use an attacker-controlled provider URL, the fetch hits `169.254.169.254` instead. Lambda execution role compromised.
- A Spring Boot application validates `redirect_uri` parameters against an allowlist, but the allowlist matches by string prefix. Attacker submits `redirect_uri=http://169.254.169.254/...?legitimate.example.com` — prefix matches start of attacker URL after a clever encoding — and metadata is reached.

## Related notes

- [[nat-and-private-networks]] — link-local space, the substrate this whole topic sits on.
- [[firewalls-and-network-boundaries]] — the network-layer egress block that gates metadata reach.
- [[reverse-proxies]] — proxies are common SSRF intermediaries; trust-boundary thinking applies.
- [[client-ip-trust]] — IP-allowlist confusion is a sibling failure mode for cloud-internal trust.
- [[ssrf|SSRF]] — the application-layer primitive that makes this attack possible.
- [[cors-misconfiguration|CORS misconfiguration]] — adjacency: client-side origin trust does not protect server-side fetchers.
- [[file-upload-abuse|File upload abuse]] — SVG/PDF/HTML uploads can become SSRF vectors via headless renderers.
- [[trace-metadata-endpoint-reachability|Trace metadata endpoint reachability]]
- [[secrets-management]] — long-lived static credentials are the worse alternative to instance metadata.

### Suggested future atomic notes

- imdsv2-hop-limit-design
- ssrf-allowlist-design
- gcp-workload-identity
- aws-sts-assume-role-chains
- kubernetes-service-account-tokens
- dns-rebinding
- metadata-detection-with-guardduty

## References

- **Foundational:** AWS Instance Metadata Service docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Foundational:** GCP metadata server docs — https://cloud.google.com/compute/docs/metadata/overview
- **Foundational:** Azure Instance Metadata Service docs — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
