---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Trace Metadata Endpoint Reachability

## Goal

Determine whether an application, host, container, or SSRF-capable feature can reach cloud instance metadata endpoints, and turn that result into a safe evidence package for hardening.

The playbook answers one question: **can this workload reach identity-bearing metadata from the place an attacker-controlled request or compromised process would run?**

## Assumptions

- The target is an owned lab, an explicitly authorized environment, or a defensive audit.
- The workload runs in cloud, container, VM, CI runner, or Kubernetes infrastructure where metadata or metadata-adjacent identity may exist.
- Metadata reachability is a blast-radius question, not automatically a credential-theft exercise.
- SSRF primitives may reveal reachability through status, timing, redirect behavior, DNS callbacks, or partial response differences.

## Prerequisites

- Written scope for the host, app, account, cluster, or lab.
- A way to run commands from the relevant vantage point: host shell, container shell, pod shell, CI job, or an owned SSRF test harness.
- Permission to test link-local addresses and cloud metadata service behavior.
- A safe evidence plan that avoids printing, storing, or exfiltrating real cloud credentials unless the engagement explicitly allows it.
- Known cloud/provider context when possible: AWS, GCP, Azure, DigitalOcean, Oracle, Alibaba, Kubernetes, or local lab.

## Recon steps

1. Identify the execution vantage point: app server, container, pod, CI runner, serverless function, webhook worker, image fetcher, PDF renderer, or URL previewer.
2. Identify whether the workload is cloud-hosted and which provider controls metadata behavior.
3. Record network context: private IPs, routes, container namespace, egress policy, service mesh, and security group or NetworkPolicy expectations.
4. Identify user-controlled server-side request paths, including URL fetchers, redirects, XML/SVG parsing, OAuth/OIDC discovery, webhook delivery, and file preview systems.
5. Decide proof level before testing: reachability only, metadata version check, identity path existence, or controlled read-only cloud API call.

## Test steps

### 1. Test direct host reachability

From the host or VM itself:

```
curl -sS --max-time 2 -o /dev/null -w 'aws-imds-root: %{http_code}\n' \
  http://169.254.169.254/

curl -sS --max-time 2 -o /dev/null -w 'aws-imds-path: %{http_code}\n' \
  http://169.254.169.254/latest/meta-data/
```

Interpretation:
- `200` on AWS IMDSv1-style paths means basic metadata reachability exists.
- `401`, `403`, or `405` may mean IMDSv2 or provider header requirements are doing work.
- timeout or connection failure may mean egress filtering, no metadata service, hop-limit behavior, or non-cloud context.

### 2. Test provider-specific hardening

Use safe metadata checks that do not print credentials:

```
# AWS IMDSv2 token availability
TOKEN=$(curl -sS --max-time 2 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)

if [ -n "$TOKEN" ]; then
  curl -sS --max-time 2 -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/iam/info
fi

# GCP metadata root, header required
curl -sS --max-time 2 -H 'Metadata-Flavor: Google' \
  http://metadata.google.internal/computeMetadata/v1/ -o /dev/null -w 'gcp: %{http_code}\n'

# Azure metadata root, header and api-version required
curl -sS --max-time 2 -H 'Metadata: true' \
  'http://169.254.169.254/metadata/instance?api-version=2021-02-01' \
  -o /dev/null -w 'azure: %{http_code}\n'
```

Do not fetch credential paths unless the scope explicitly permits it.

### 3. Test container or pod reachability

Run from the same isolation layer the application uses:

```
# Docker example
docker run --rm curlimages/curl:latest -sS --max-time 2 \
  -o /dev/null -w 'container-imds: %{http_code}\n' \
  http://169.254.169.254/latest/meta-data/

# Kubernetes example
kubectl exec -n <namespace> <pod> -- sh -c \
  "curl -sS --max-time 2 -o /dev/null -w 'pod-imds: %{http_code}\n' http://169.254.169.254/latest/meta-data/"
```

Compare host reachability to container/pod reachability. On AWS, a host may reach IMDS while a correctly hop-limited pod cannot.

### 4. Test SSRF-mediated reachability safely

Use a harmless endpoint or owned callback target first:

```
Feature:
User-controlled URL:
Outbound callback observed:
Redirects followed:
DNS rebinding possible:
Direct IP allowed:
Private/link-local blocked:
```

Then test link-local probes only if authorized:

```
http://169.254.169.254/
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/
http://[::ffff:169.254.169.254]/
http://2852039166/
```

Record differences in status, timing, response length, redirects, and error text. A blind SSRF can still prove reachability through timeouts or out-of-band callbacks.

### 5. Verify cloud control posture

Use provider APIs where available:

```
# AWS: metadata token and hop-limit posture
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table

# Kubernetes: service-account token automount and host networking
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.hostNetwork == true) | "\(.metadata.namespace)/\(.metadata.name) hostNetwork=true"'
```

Control-plane evidence is often cleaner than risky runtime credential proof.

## Validation clues

- A host, pod, container, CI runner, or app feature receives non-timeout responses from `169.254.169.254`.
- Basic GET to AWS metadata succeeds, suggesting IMDSv1 is allowed.
- IMDSv2 token flow works from host and also from container/pod when hop limit should prevent it.
- SSRF feature blocks normal private IPs but permits equivalent encodings, redirects, IPv6-mapped forms, or provider hostnames.
- GCP or Azure header-required metadata blocks naive SSRF, but a richer SSRF primitive can set arbitrary headers.
- Cloud API posture shows `HttpTokens=optional`, high hop limits, broad service-account scopes, missing NetworkPolicy, or default service-account automount.

## Evidence to capture

Use a small table instead of dumping secrets:

```
Vantage point:
Provider:
Probe:
Result:
Credential path requested: no/yes
Credentials stored: no/yes
Control-plane setting:
Impact if reached:
Recommended fix:
Retest:
```

If credential access is explicitly in scope, store only enough to prove identity, such as `aws sts get-caller-identity` output, and redact tokens immediately.

## Mitigation

- Require hardened metadata mode: AWS IMDSv2 required and hop limit `1`; provider-equivalent controls for GCP/Azure.
- Block egress to link-local and private ranges from public-facing workloads unless there is a documented need.
- Implement URL allowlists that resolve hosts, deny private/link-local ranges, and re-check after redirects.
- Restrict service accounts and instance roles to least privilege.
- Disable Kubernetes service-account token automount where the pod does not need the API server.
- Add cloud/account policies so new workloads cannot launch with weak metadata posture.
- Retest from the exact workload vantage point after changes.

## Logging / detection

- Alert on metadata-related cloud detections such as DNS rebinding, unusual STS usage, or API calls from unexpected IPs, regions, or user agents.
- Log outbound requests from URL-fetching services and flag link-local/private destinations.
- Monitor changes to AWS metadata options, Kubernetes `hostNetwork`, service-account automount, and egress NetworkPolicy.
- Correlate SSRF probing against later cloud API use by the same workload role.

## Stop conditions

Stop testing and escalate if:

- credential material appears in a response unexpectedly
- a production workload allows IMDSv1 or pod metadata reachability
- a probe risks modifying cloud resources or generating cost
- a blind SSRF starts hitting sensitive internal services outside scope
- the only remaining proof would require destructive actions, broad credential exfiltration, or cross-account testing

## Related notes

- [[metadata-endpoints|Cloud Instance Metadata Endpoints]]
- [[nat-and-private-networks|NAT and Private Networks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[ssrf|SSRF]]
- [[cloud-metadata-security|Cloud Metadata Security]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[investigate-ssrf|Investigate SSRF]]

## Commands / payloads

### Safe probe set

```
http://169.254.169.254/
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/
http://[::ffff:169.254.169.254]/
http://2852039166/
http://0.0.0.0/
http://127.0.0.1/
```

### Minimal AWS posture command

```
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table
```

### Kubernetes posture checks

```
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.automountServiceAccountToken != false) | "\(.metadata.namespace)/\(.metadata.name) token-auto-mounted"'

kubectl get networkpolicy --all-namespaces
```

## Gotchas

- A timeout is not always safe; it may indicate network filtering, DNS failure, provider mismatch, or a blind SSRF with no visible response.
- IMDSv2 required on the host does not automatically prove containers cannot reach metadata; hop limit and network namespace matter.
- Header-required metadata services reduce basic SSRF risk but do not protect against SSRF primitives that can set arbitrary headers.
- DNS allowlists must be checked after every redirect and should pin resolved IPs to prevent rebinding.
- Never paste real metadata credentials into notes, tickets, or screenshots.

## References

- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Research / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
