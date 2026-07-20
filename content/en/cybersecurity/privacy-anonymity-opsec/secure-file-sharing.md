---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Secure File Sharing

## Definition

Secure file sharing is the controlled transfer of files so that contents, metadata, sender/recipient identity, access lifetime, and storage location match the threat model.

## Why it matters

Sharing a file is not only a transport problem. The file may contain metadata. The sharing service may retain a copy. The access link may be forwarded. The recipient may download from an identifying network. The sender may expose their machine if they host the file directly.

Secure sharing means designing the whole chain: file contents, metadata, route, storage, authentication, expiration, recipient handling, and deletion.

## How it works

Use the 6-part sharing model:

1.
**Prepare the file**
   Inspect visible content and hidden metadata.

2.
**Choose transfer path**
   Decide between encrypted messenger, cloud link, OnionShare, physical transfer, or other controlled channel.

3.
**Protect access**
   Use passwords, private keys, recipient identity, expiring links, or one-time access where appropriate.

4.
**Share secrets separately**
   Do not send link, password, and context through the same weak channel when the risk is high.

5.
**Control lifetime**
   Stop sharing, expire the link, remove cloud copies, and record recipient confirmation.

6.
**Handle recipient risk**
   The recipient's device, account, and network become part of the file's exposure path.

Example:

```
file -> metadata inspection -> cleaned copy -> sharing channel -> recipient verification -> access closed -> deletion/retention record
```

The bug is not using a specific file-transfer tool. The bug is leaving the file, link, metadata, and recipient behavior outside the threat model.

## Techniques / patterns

- Clean metadata before sharing.
- Prefer end-to-end encrypted channels for smaller files when recipient identity is known.
- Use OnionShare or onion services when avoiding third-party storage matters.
- Use separate channels for link and password/private key when risk justifies it.
- Set expiration, one-time download, or manual stop conditions.
- Confirm recipient device and account context.
- Preserve originals separately when evidence integrity matters.

## Variants and bypasses

Use the 7 sharing patterns:

### 1. Encrypted messenger transfer

Good for known recipients and smaller files. Metadata, cloud backup, account identity, and device compromise still matter.

### 2. Cloud storage link

Convenient, but the provider may store, scan, log, retain, or receive legal requests for the file and access metadata.

### 3. OnionShare-style direct onion service

The sender hosts a temporary onion service from their machine. This can avoid third-party storage but depends on the sender staying online and sharing the address/key safely.

### 4. Password-protected archive

Adds content protection, but password sharing, weak encryption settings, metadata outside the archive, and archive filenames can leak.

### 5. Physical transfer

Avoids network transfer metadata but introduces physical custody, device, border, loss, and storage risks.

### 6. Anonymous dropbox

Allows sources or recipients to upload without normal account identity, but malware, metadata, and operational handling remain critical.

### 7. Evidence-preserving transfer

When files are evidence, preserve originals and chain of custody before cleaning, converting, or renaming copies.

## Impact

- Reduced exposure of sensitive files to third-party services.
- Lower risk of metadata deanonymization.
- Better control over who can access a file and for how long.
- Clearer recipient-side safety expectations.
- Reduced evidence damage from uncontrolled cleaning or transfer.

## Detection and defense

Ordered by effectiveness:

1.
**Classify the file and recipient risk**
   The right sharing path depends on sensitivity, recipient identity, file size, legal risk, and whether third-party storage is acceptable.

2.
**Inspect and clean metadata before sharing copies**
   Payload privacy matters as much as transport privacy. Share cleaned copies unless preserving metadata is required.

3.
**Choose the channel based on trust and retention**
   Cloud links, messengers, OnionShare, and physical transfer create different storage and metadata trails.

4.
**Separate access material when necessary**
   Link, password, private key, and instructions should not always travel through the same channel.

5.
**Close the sharing window**
   Stop services, expire links, remove temporary copies, and record what remains stored where.

6.
**Give recipient handling instructions**
   A secure transfer can fail if the recipient opens files on a monitored device, syncs them to cloud storage, or forwards the link.

### What does not work as a primary defense

- **A private link is not access control.** Anyone with the link may be able to access it.
- **Encryption in transit does not remove file metadata.** The file can still identify its origin.
- **Cloud deletion does not prove erasure.** Backups, logs, sync clients, and recipients may retain copies.
- **OnionShare does not make unsafe files safe.** It changes hosting and routing, not file contents.
- **Password-protected archives are not enough if the password is sent badly.** The sharing channel matters.

## Practical labs

### Build a file-sharing threat model

```
File:
Sensitivity:
Recipient:
Need anonymity:
Need third-party avoidance:
Need evidence preservation:
Metadata cleaned:
Channel:
Access secret:
Expiration:
Recipient instructions:
```

This should be completed before selecting the tool.

### Inspect before transfer

```
exiftool file.ext
```

Look for author, GPS, timestamps, software, comments, embedded thumbnails, and paths.

### Verify cleaned copy

```
cp file.ext file-clean.ext
exiftool -all= file-clean.ext
exiftool file-clean.ext
```

Use a tool and format appropriate to the file. The final inspection is the evidence.

### Plan link and secret separation

```
Link channel:
Password/private-key channel:
Recipient verification:
Expiration:
Forwarding risk:
Fallback if wrong recipient receives it:
```

Do not improvise secret delivery for high-risk files.

### Record closure

```
Transfer complete:
Recipient confirmed:
Service stopped:
Cloud copy removed:
Local temp copy removed:
Original preserved:
Remaining copies:
```

Closure is part of the sharing workflow.

## Practical examples

- A journalist uses OnionShare for a source to download a file without third-party cloud storage.
- A team shares a password-protected archive but sends the password in the same email thread, weakening the control.
- A user cleans photo metadata before sending it through an encrypted messenger.
- A cloud link is forwarded beyond the intended recipient because it lacks recipient-bound access control.
- An incident responder preserves the original evidence file, then shares a redacted copy.

## Related notes

- [[file-metadata-removal|File Metadata Removal]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[tails-operational-model|Tails Operational Model]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- onionshare-workflows
- anonymous-dropboxes
- document-redaction
- [[secure-deletion-and-storage-wiping]]

## References

- **Official Tool Docs:** OnionShare documentation - https://docs.onionshare.org/
- **Official Tool Docs:** Tails: Removing metadata from files - https://tails.net/doc/sensitive_documents/metadata/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
