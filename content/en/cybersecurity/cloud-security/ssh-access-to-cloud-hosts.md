---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# SSH Access to Cloud Hosts

## Definition

SSH access to cloud hosts is the controlled administrative path for reaching Linux virtual machines through keys, identity, network rules, and audit trails.

## Why it matters

SSH is often the first practical cloud lab step and one of the easiest ways to create accidental exposure. A VM with port 22 open to the world, a reused private key, or a privileged default user can become the whole lab's weak point.

The cloud-specific lesson is that SSH security is not just `sshd_config`; it includes key lifecycle, security groups, public IPs, IAM, and logging.

## How it works

Cloud SSH access has **5 gates**:

1. **Instance identity.** The VM exists in a specific account, region, subnet, and security context.
2. **Network reachability.** Security groups, firewalls, routes, and public IPs decide whether SSH is reachable.
3. **Host authentication.** The client verifies the server host key.
4. **User authentication.** The server accepts a key, certificate, or managed session identity.
5. **Privilege boundary.** Sudo, users, and instance roles decide post-login impact.

The bug is rarely "SSH exists." The bug is SSH exposed too broadly with weak identity and excessive post-login privileges.

A worked example, SSH exposure to cloud impact:

```
Host:
  lab-web-01

Inbound:
  TCP/22 from 0.0.0.0/0

Credential:
  shared private key used by multiple labs

Post-login:
  default user has passwordless sudo

Cloud identity:
  attached role can read object storage

Decision:
  SSH exposure is high impact because shell access becomes role credential access and storage reach
```

Cloud SSH triage should always include network path, credential hygiene, local privilege, and attached cloud identity.

## Techniques / patterns

Reviews look at:

- port 22 open to `0.0.0.0/0` or `::/0`
- reused private keys across labs
- default users with broad sudo access
- missing host-key verification
- unmanaged key distribution
- direct SSH where session-manager style access would be safer
- instance roles reachable after login

## Variants and bypasses

SSH cloud risk has **4 common shapes**.

### 1. World-open SSH

The security group allows inbound SSH from anywhere.

### 2. Shared key access

One key grants access to many hosts or many people.

### 3. Privileged default user

Login lands on a user that can immediately become root.

### 4. Metadata-assisted escalation

After SSH login, the user can access workload credentials through metadata.

## Impact

Ordered roughly by severity:

- **Host compromise.** A stolen key or weak access path gives shell access.
- **Credential pivot.** Instance roles and local secrets may expose cloud APIs.
- **Lateral movement.** The host may reach private networks or databases.
- **Persistence.** Attackers can add keys, users, services, or cron jobs.
- **Cost abuse.** Compromised hosts can mine, proxy, or scan.

## Detection and defense

Ordered by effectiveness:

1.
**Restrict SSH reachability.**
   Limit inbound SSH to trusted IPs, VPNs, bastions, or managed session services.

2.
**Use unique, protected keys or managed access.**
   Unique credentials reduce blast radius and make rotation realistic.

3.
**Minimize sudo and instance-role permissions.**
   Shell access should not automatically imply cloud admin access.

4.
**Log SSH and cloud control-plane activity.**
   Host logs plus cloud audit logs show both login and follow-on API behavior.

5.
**Rotate and remove stale access.**
   Keys and users should have owners and expiry.

### What does not work as a primary defense

- **Changing SSH to a nonstandard port.** It reduces noise, not real exposure.
- **Relying on key auth while sharing the same key widely.** Shared secrets are hard to revoke.
- **Assuming a lab VM is uninteresting.** Attackers do not care why the host exists.
- **Blocking password login but leaving admin role credentials accessible.** Post-login impact still matters.

## Practical labs

Use one sandbox VM.

### Review inbound SSH exposure

```
Instance:
Public IP:
Security group/firewall:
Allowed source:
IPv6 allowed:
Business reason:
Expiry:
```

World-open SSH should be temporary and justified, if used at all.

### Validate key hygiene

```
Key name:
Owner:
Used by hosts:
Passphrase:
Stored where:
Rotation date:
```

Private keys are cloud credentials.

### Check post-login cloud reach

```
curl -sS --max-time 2 http://169.254.169.254/ || true
```

Record whether metadata is reachable and which protections apply in the provider.

### Build an SSH exposure exception record

```
host | source allowed | reason | owner | expiry | compensating controls
```

Temporary SSH exceptions need an expiry or they become permanent exposure.

### Compare direct SSH with managed session access

```
Requirement:
Direct SSH needed?:
Managed session option:
Audit trail:
Network exposure removed:
Decision:
```

Managed access can remove public SSH reachability while preserving administration.

## Practical examples

- A lab EC2 instance exposes SSH to the entire internet.
- One private key is reused across every cloud exercise.
- A default user has passwordless sudo.
- A compromised host reads role credentials from metadata.
- A security group remains open after the lab ends.

## Related notes

- [[cloud-lab-infrastructure]]
- [[cloud-network-boundaries]]
- [[cloud-metadata-security]]
- [[cloud-iam-boundaries]]
- [[metadata-endpoints|Metadata Endpoints]]

### Suggested future atomic notes

- cloud-bastion-hosts
- session-manager-access
- ssh-key-rotation
- linux-hardening-for-cloud-hosts

## References

- **Official Docs:** AWS EC2 key pairs and Linux instances — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- **Official Docs:** AWS EC2 security groups — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html
- **Mitigation:** Microsoft guidance for securing privileged access — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
