---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cloud Metadata Security

## Definition

Cloud metadata security is the protection of provider metadata services that expose instance identity, configuration, and temporary credentials to workloads.

## Why it matters

Metadata services are useful because workloads need information and credentials without hardcoded secrets. They are dangerous because any process that can reach metadata may be able to retrieve powerful cloud credentials.

This is the cloud-specific version of the broader [[metadata-endpoints|Metadata Endpoints]] note.

## How it works

Metadata risk has **5 stages**:

1. **Workload runs with an attached identity.** A VM or container has a role/service account.
2. **Metadata endpoint is reachable locally.** The workload can request metadata over a link-local or provider path.
3. **Application bug creates a request primitive.** SSRF, command execution, or proxy misuse can reach the endpoint.
4. **Temporary credentials are returned.** The attacker obtains role-scoped tokens.
5. **Cloud APIs are called.** Impact depends on the attached identity's permissions.

The bug is not metadata existing. The bug is metadata reachability combined with overprivileged workload identity and application request flaws.

A worked example, SSRF to cloud API risk:

```
Application bug:
  /fetch?url= accepts arbitrary URLs

Metadata posture:
  instance metadata reachable from the workload

Attached identity:
  app-role can read storage and list secrets

Exploit path:
  SSRF reaches metadata, retrieves temporary credentials, calls cloud APIs

Decision:
  fix SSRF, require metadata protections, and reduce app-role permissions;
  blocking only one metadata URL string is not enough
```

Metadata findings should always end with the permissions available through the attached identity.

## Techniques / patterns

Reviews look at:

- attached instance roles or service accounts
- IMDSv2/token enforcement and hop limits
- container access to node metadata
- SSRF-capable applications
- metadata access from untrusted workloads
- permissions available to metadata credentials

## Variants and bypasses

Cloud metadata failures have **4 common variants**.

### 1. IMDSv1-style unauthenticated access

Metadata can be queried with a simple HTTP request.

### 2. SSRF to metadata

An application fetches attacker-controlled URLs and reaches metadata.

### 3. Container-to-node metadata

Containers reach the node's metadata service and inherit broader permissions.

### 4. Overprivileged workload identity

Even protected metadata becomes high impact when the attached role is too broad.

## Impact

Ordered roughly by severity:

- **Credential theft.** Temporary cloud credentials are exposed.
- **Data access.** Retrieved credentials can read storage, secrets, databases, or logs.
- **Lateral movement.** Role permissions may allow discovery or role assumption.
- **Persistence.** Some permissions allow new credentials or policy changes.
- **Incident expansion.** One web bug becomes cloud control-plane access.

## Detection and defense

Ordered by effectiveness:

1.
**Minimize workload identity permissions.**
   Metadata credentials should be narrow enough that compromise does not become account compromise.

2.
**Enforce provider metadata protections.**
   IMDSv2, hop limits, and provider-specific controls reduce simple metadata theft paths.

3.
**Block metadata from untrusted runtime contexts.**
   Containers and user-supplied workloads should not reach node metadata unless needed.

4.
**Prevent SSRF and proxy-to-metadata paths.**
   Application-layer controls should deny link-local and provider metadata addresses.

5.
**Monitor metadata credential use.**
   Unusual API calls from workload roles can reveal compromise.

### What does not work as a primary defense

- **Assuming temporary credentials are harmless.** Short-lived credentials still have real permissions.
- **Blocking only the literal metadata IP in app code.** SSRF bypasses can use redirects, DNS tricks, or alternate formats.
- **Giving every instance one broad role.** Metadata exposure then becomes broad API access.
- **Relying on private networking alone.** Metadata is intentionally local to the workload.

## Practical labs

Use only owned sandbox compute.

### Identify metadata posture

```
Provider:
Compute type:
Attached identity:
Metadata protection:
Hop limit:
Role permissions:
```

Understand what a compromised process could reach.

### Test metadata access from the host

```
curl -sS --max-time 2 http://169.254.169.254/ || true
```

Record provider behavior and protections without extracting real secrets into notes.

### Review workload permissions

```
Role/service account:
Needed actions:
Granted actions:
Wildcard permissions:
Safer policy:
```

The main fix is usually identity scope.

### Test metadata from different runtime positions

```
host shell:
container:
application SSRF path:
serverless function:
expected access:
actual access:
```

Metadata reachability can differ between host, container, and app layers.

### Build a metadata blast-radius card

```
workload | metadata reachable? | protection | attached identity | highest-risk permission | next action
```

The severity is the combination of reachability and identity power.

## Practical examples

- An SSRF in a web app retrieves instance role credentials.
- A container can access node metadata in a cluster.
- A VM role can read all storage buckets despite needing only one.
- IMDSv2 is optional rather than required.
- CloudTrail shows unusual API calls from an instance role.

## Related notes

- [[cloud-iam-boundaries]]
- [[cloud-network-boundaries]]
- [[cloud-logging-and-detection]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[ssrf|SSRF]]

### Suggested future atomic notes

- imdsv2-hop-limit-design
- gcp-workload-identity
- kubernetes-service-account-tokens
- metadata-detection-with-guardduty

## References

- **Official Docs:** AWS EC2 Instance Metadata Service — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Official Docs:** Google Cloud VM metadata — https://cloud.google.com/compute/docs/metadata/overview
- **Official Docs:** Azure Instance Metadata Service — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
