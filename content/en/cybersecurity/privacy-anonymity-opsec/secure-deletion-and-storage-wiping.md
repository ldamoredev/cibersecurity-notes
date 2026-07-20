---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Secure Deletion and Storage Wiping

## Definition

Secure deletion and storage wiping are the practices of removing data so that it cannot be easily recovered from logical, filesystem, or storage layers, subject to the limitations of the medium and the threat model.

## Why it matters

Deleting a file usually only removes a pointer, not the underlying data. Backups, snapshots, journals, wear leveling, cloud sync, device caches, and forensic tooling can all preserve copies or traces long after the user thinks the file is gone.

## How it works

Use the 5-layer deletion model:

1.
**Logical deletion**
   The file is removed from the filesystem view.

2.
**Metadata and journal cleanup**
   Filesystem structures, logs, and journals may still retain traces.

3.
**Medium behavior**
   SSDs, flash storage, and copy-on-write systems can preserve blocks in ways normal deletion does not control.

4.
**Copies and backups**
   Sync services, cloud backups, snapshots, and recipient copies may outlive the original.

5.
**Threat-model match**
   The right wipe method depends on whether the media is magnetic, flash-based, encrypted, repurposed, or simply leaving your control.

The bug is not deleting. The bug is assuming deletion means the same thing on every storage medium.

## Techniques / patterns

- Classify the storage medium before deciding how to delete.
- Prefer full-disk encryption so disposal becomes safer than trying to chase every block.
- Delete or expire copies in backups, sync folders, and cloud services.
- Verify whether the device supports secure erase or built-in wipe functions.
- Separate logical cleanup from physical destruction.
- Keep an audit trail when data must be retained for evidence or compliance.

## Variants and bypasses

Use the 6 storage cases:

### 1. Filesystem delete

Works for user-facing cleanup but leaves recovery opportunities depending on medium and system state.

### 2. Secure erase command

Can be effective when supported by the device and executed correctly.

### 3. Encryption key destruction

If the disk is strongly encrypted, destroying keys can be more practical than overwriting every block.

### 4. Snapshot and backup removal

Cloud snapshots and backups need separate deletion workflows.

### 5. SSD and flash media

Wear leveling and controller behavior make simple overwrite assumptions unreliable.

### 6. Physical destruction

Sometimes the only acceptable option for retired media with high sensitivity.

## Impact

- Reduced recoverability of sensitive data.
- Lower risk from disposed devices or shared systems.
- Better control over backup and cloud remnants.
- More realistic disposal decisions for SSDs and flash media.
- Avoidance of false confidence from simple file deletion.

## Detection and defense

Ordered by effectiveness:

1.
**Encrypt first**
   Strong encryption reduces the need to trust overwrite behavior after disposal.

2.
**Use media-appropriate erasure**
   Follow NIST-style sanitization guidance and vendor support where available.

3.
**Delete copies everywhere**
   Backups, sync folders, snapshots, exports, and recipient copies all matter.

4.
**Verify the wipe path**
   Confirm that the intended method actually applies to the medium in use.

5.
**Use physical destruction for the highest sensitivity**
   When the threat model is high enough, destruction may be more reliable than sanitization.

### What does not work as a primary defense

- **Emptying the trash is not secure deletion.**
- **Overwriting once is not universally sufficient.**
- **Deletion from one device does not delete cloud copies.**
- **Encryption without key management does not solve disposal on its own.**

## Practical labs

### Classify the medium

```
Storage:
HDD / SSD / flash / cloud / backup / snapshot:
Encrypted:
Shared with others:
Sensitive data present:
Supported wipe method:
```

The medium determines the deletion strategy.

### Map copies

```
Original:
Local cache:
Backup:
Cloud sync:
Recipient copy:
Export:
Wipe each one? yes/no
```

Deletion must cover all copies.

### Decide the disposal path

```
Sensitivity:
Time available:
Medium type:
Encryption in place:
Need to retain evidence:
Wipe / destroy / retain:
```

This makes disposal a documented decision.

### Verify the result

```
Method used:
Verification method:
Remaining recoverability:
Cloud remnants:
Backups removed:
```

If you cannot verify, you do not know the deletion outcome.

## Practical examples

- A laptop is retired after key destruction on a strongly encrypted disk.
- A cloud folder is emptied, but the backup snapshot still contains the files.
- An SSD is sanitized according to vendor guidance rather than blind overwriting.
- A phone photo is deleted locally but persists in synced backups.
- A sensitive file is destroyed physically because the threat model is high.

## Related notes

- [[file-metadata-removal|File Metadata Removal]]
- [[secure-file-sharing|Secure File Sharing]]
- [[tails-operational-model|Tails Operational Model]]
- [[end-to-end-encryption|End-to-End Encryption]]
- [[artifact-integrity|Artifact Integrity]]

### Suggested future atomic notes

- data-sanitization
- ssd-wipe-methods
- backup-retention

## References

- **Official Tool Docs:** NIST SP 800-88 Rev. 1 - https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final
- **Official Tool Docs:** Tails: Secure Deletion - https://tails.net/doc/encryption_and_privacy/secure_deletion/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
