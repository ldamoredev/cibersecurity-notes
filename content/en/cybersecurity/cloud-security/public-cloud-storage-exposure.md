---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Public Cloud Storage Exposure

## Definition

Public cloud storage exposure is unintended or poorly governed public access to object storage, blobs, snapshots, backups, or shared storage resources.

## Why it matters

Cloud object storage is easy to create, easy to share, and easy to forget. A single public bucket or blob container can expose source code, backups, documents, logs, credentials, or customer data.

The key distinction: storage exposure is usually an access-control and lifecycle problem, not a web-server problem.

## How it works

Storage exposure has **5 decision points**:

1. **Resource policy.** Bucket/container policies may allow public or cross-account access.
2. **Object ACLs.** Individual objects may be shared differently from the parent.
3. **Identity permissions.** Users and roles may read or modify storage.
4. **Network and service controls.** Provider settings may block or allow public paths.
5. **Lifecycle and ownership.** Old backups and exports may outlive their purpose.

The bug is not object storage. The bug is data without ownership, classification, and access review.

A worked example, public bucket to impact:

```
Storage:
  public reports bucket

Public access:
  object read allowed, listing disabled

Object found:
  exports/customer-summary-2025.csv

Classification:
  customer data, not intended public content

Root cause:
  export job writes sensitive files into a bucket also used for public static reports

Decision:
  separate public/private buckets, remove object, rotate any exposed credentials, review logs
```

Storage triage depends on content class, access path, lifecycle owner, and read history.

## Techniques / patterns

Reviews look at:

- public access flags and block-public-access settings
- bucket/container policies
- object ACLs and signed URLs
- cross-account or external sharing
- names that imply backups, logs, exports, or secrets
- encryption and retention settings
- stale buckets after service teardown

## Variants and bypasses

Storage exposure has **5 common forms**.

### 1. Public-read bucket/container

Anyone can list or read data.

### 2. Public object inside private storage

Specific objects are exposed even when the container appears private.

### 3. Overbroad cross-account sharing

External principals can read or write more than intended.

### 4. Leaked signed URL

Temporary sharing links escape into tickets, logs, chats, or pages.

### 5. Backup and log exposure

Sensitive data is exposed through derived artifacts rather than primary systems.

## Impact

Ordered roughly by severity:

- **Sensitive data leak.** Backups, documents, logs, or exports become public.
- **Credential compromise.** Exposed config files may contain keys or tokens.
- **Supply-chain impact.** Public write access can modify hosted artifacts.
- **Reconnaissance.** File names and logs reveal systems, users, and paths.
- **Compliance failure.** Data handling promises may be broken.

## Detection and defense

Ordered by effectiveness:

1.
**Block public access by default.**
   Provider-level public-access blocks prevent many accidental exposures before policy review is needed.

2.
**Classify and own storage resources.**
   Buckets with owners, data types, and expiry dates are easier to govern.

3.
**Review resource policies and object ACLs.**
   Effective access can come from multiple layers.

4.
**Monitor public-access changes.**
   Alert on policy changes that make storage public or externally shared.

5.
**Avoid placing secrets in storage artifacts.**
   Backups and logs should not contain credentials that become secondary blast radius.

### What does not work as a primary defense

- **Obscure bucket names.** Names are not access control.
- **Assuming "private by default" stays private.** Policies and ACLs drift.
- **Encrypting data but leaving keys accessible.** Encryption only helps if key access is controlled.
- **Deleting the app but leaving its bucket.** Storage often survives compute teardown.

## Practical labs

Use a sandbox bucket/container with non-sensitive files.

### Storage exposure inventory

```
Name:
Provider:
Public access block:
Resource policy:
Object ACLs:
External sharing:
Owner:
Data type:
Expiry:
```

Review both container and object levels.

### Test with an unauthenticated browser

```
Object URL:
Unauthenticated read:
Directory/listing:
Expected result:
Actual result:
```

Never test with sensitive data.

### Teardown storage

```
Objects deleted:
Versions deleted:
Snapshots/backups deleted:
DNS references removed:
Policy removed:
```

Storage cleanup is separate from VM cleanup.

### Check object-level exceptions

```
bucket/container policy:
public access block:
object ACL exceptions:
signed URLs:
cross-account grants:
```

Container-level privacy does not prove every object is private.

### Review access logs for exposed objects

```
object | public? | first public time | access count | unusual IPs | remediation
```

Exposure response needs both current policy and historical access evidence.

## Practical examples

- A public bucket contains database exports.
- A static website bucket allows unintended object listing.
- A signed URL is pasted into a public issue.
- A backup snapshot remains shared with an old account.
- Public write access lets an attacker replace a hosted file.

## Related notes

- [[cloud-security-basics]]
- [[cloud-iam-boundaries]]
- [[cloud-logging-and-detection]]
- [[exposed-storage|Exposed Storage]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- object-storage-acls
- signed-url-risk
- cloud-backup-exposure
- storage-data-classification

## References

- **Official Docs:** Amazon S3 Block Public Access — https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html
- **Official Docs:** Google Cloud Storage access control — https://cloud.google.com/storage/docs/access-control
- **Official Docs:** Azure Storage security recommendations — https://learn.microsoft.com/en-us/azure/storage/blobs/security-recommendations
