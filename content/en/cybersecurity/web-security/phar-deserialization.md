---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# PHAR Deserialization

## Definition

PHAR deserialization is a PHP-specific exploitation technique where deserialization is triggered not by an explicit `unserialize()` call, but as a side effect of any filesystem operation performed on a `phar://` stream URI. PHAR (PHP Archive) files contain serialized metadata, and the moment PHP reads a file via the `phar://` wrapper, that metadata is implicitly deserialized — invoking the magic methods of any class encoded inside.

## Why it matters

PHAR deserialization changes the threat model for an entire category of code that defenders previously considered inert.

- **The trigger is not `unserialize`.** A code review searching for `unserialize($_*)` will miss PHAR-driven RCE entirely. The trigger is `file_exists`, `fopen`, `getimagesize`, `is_dir`, `filesize`, `stat`, `md5_file`, `imagecreatefromjpeg` — over fifty PHP functions, plus anything in third-party image / archive libraries that internally calls them.
- **It weaponizes file uploads that are otherwise considered safe.** An "image upload" endpoint that strictly validates extension, MIME type, and even re-encodes through GD becomes a deserialization sink the moment another endpoint touches the file by path through `phar://`.
- **It teaches that stream wrappers are silent execution surfaces.** PHP's stream wrapper architecture is shared by `phar://`, `zip://`, `data://`, `expect://`, `phar://`, and any user-registered wrapper. The same lesson applies: filesystem APIs operate on attacker-influenceable URIs.
- **Sam Thomas's 2018 disclosure changed how many auditors model file-handling code.** It made the Black Hat USA 2018 Top 10 web hacking techniques list and remains the canonical demonstration that "trigger surface" can be much wider than "obvious sink."

## How it works

The mechanism in five steps:

1. **Build a polyglot PHAR.** A PHAR file consists of a stub (PHP code), a manifest (serialized metadata), file contents, and a signature. The stub can be prefixed with arbitrary bytes — including a valid JPG/GIF/PNG/PDF header. The result is a single file that passes as both an image and a working PHAR.
2. **Embed the payload in the manifest.** The manifest stores serialized PHP objects representing the archive's metadata. Attacker replaces this metadata with a serialized object whose class has dangerous magic methods (`__wakeup`, `__destruct`) that kick off a [[gadget-chains|gadget chain]] when called.
3. **Upload via a file-upload endpoint.** Validation typically checks: file extension (.jpg/.png), MIME type sniff, image-dimension parse via `getimagesize()`, sometimes re-encoding through GD or Imagick. A polyglot defeats extension checks (rename `.phar` → `.jpg`), MIME sniffing (image header is real), and dimension parsing (the JPG part is valid).
4. **Trigger any filesystem call through `phar://`.** The attacker now needs to make the application read its own uploaded file via `phar://path/to/upload.jpg` instead of a plain path. Common primitives:
   - A second endpoint that takes a path parameter (thumbnail rendering, file metadata viewer, attachment download).
   - A path-traversal in another feature that accepts `phar://` as a scheme.
   - An LFI that lets the attacker prefix the path with `phar://`.
5. **Magic methods fire.** PHP parses the PHAR manifest, deserializes the embedded object, and calls `__wakeup()` immediately. If the object has a `__destruct()`, that runs when the request finishes. Either way, the gadget chain executes.

The bug is not the upload. The bug is not the deserialization (no `unserialize()` is in the source). The bug is that **filesystem APIs operating on attacker-influenceable URIs are deserialization sinks**.

## Techniques / patterns

What attackers look at and how they probe:

- **Map every code path that takes a path-like parameter** and trace it to PHP functions in the trigger surface (see Variants below). Any concatenation `"$prefix/$user_input"` reaching one of those functions is a candidate.
- **Look for image-handling features** that go beyond dimension parsing — thumbnailing, EXIF extraction, watermarking, format conversion. Image libraries (GD, Imagick) call internal filesystem APIs that all honor stream wrappers.
- **Look for indirect path access** — RSS importers, XML SYSTEM entity resolvers, plugin loaders, file-existence checks before reading. Any of these may accept `phar://` as a scheme.
- **Build the polyglot with `phar.phar` or `phpggc --phar`**. PHPGGC supports `--phar tar` / `--phar zip` / `--phar phar` modes that bundle a chosen gadget chain into a polyglot of the chosen archive type — and tar/zip-mode polyglots evade `phar://` allowlists when the application happens to also support those wrappers.
- **Bypass `phar.readonly`.** This php.ini directive prevents *creation* of PHAR files via PHP code; it does not prevent *reading* attacker-uploaded ones. Defenders frequently misconfigure this hoping it will block the attack.

## Variants and bypasses

### Polyglot file types

The PHAR manifest has flexibility about where it sits in the file. Common polyglots:
- **PHAR + JPG** — JPG header (FFD8FFE0), then PHAR stub, then manifest.
- **PHAR + GIF** — `GIF89a` magic + PHAR.
- **PHAR + PDF** — `%PDF-` header + PHAR.
- **PHAR + ZIP / TAR** — PHP supports `phar://` wrappers over zip- and tar-format archives, which can avoid signature checks specific to the PHAR format.

### Trigger surface (selected high-traffic PHP functions)

Any of these on a `phar://` URI implicitly deserializes the manifest:
- File existence: `file_exists`, `is_file`, `is_dir`, `is_readable`, `is_writable`, `is_executable`.
- File reads: `fopen`, `file_get_contents`, `file`, `readfile`, `fread`, `include`, `require` (also code execution via the stub).
- File metadata: `stat`, `lstat`, `filesize`, `filemtime`, `fileatime`, `filectime`, `fileowner`, `filegroup`.
- Image processing: `getimagesize`, `imagecreatefromjpeg`, `imagecreatefrompng`, `exif_read_data`.
- Hashing: `md5_file`, `sha1_file`, `hash_file`, `crc32_file`.
- Path manipulation: `realpath`, `dirname`, `basename`, `pathinfo` — most of these do not actually deserialize, but they propagate the `phar://` URI to downstream calls that do.

### Indirect triggers via libraries

Image processing libraries (GD, Imagick), archive libraries (`ZipArchive`, `Phar` itself), template engines that resolve include paths, and frameworks that auto-load assets all eventually call functions in the trigger surface. A "thumbnail generator" that accepts a user-controlled path can therefore deserialize without any obvious sink in the application source.

### Auth context elevation

PHAR deserialization runs in the PHP-FPM worker process, which often has higher privilege than the user-facing role suggests — access to `.env` files, database credentials, Redis sockets. The first stage of post-exploit is usually credential harvesting from the worker's filesystem context.

### `phar.readonly` confusion

This php.ini directive prevents PHP code from *writing* PHAR files (e.g., via `Phar::setStub`). It does not affect *reading* PHAR files. Defenders frequently set `phar.readonly=On` and assume the attack is blocked. It is not.

## Impact

- **Remote code execution** via the embedded gadget chain — the default ceiling.
- **Local file read / SSRF** — chain sinks can be narrower than RCE; sometimes the practical primitive is "read `/etc/passwd`" or "make an outbound request to attacker."
- **Authentication context theft** — chain reads server-side credentials from filesystem (`.env`, `auth.json`, AWS instance metadata cache files).
- **Persistence** — chain writes a webshell to the document root, converting one-shot deserialization into long-term access.

The blast radius is amplified by PHAR's stealth: incident responders looking for malicious uploaded files see a JPG. Logs show file_exists() calls. The exploitation surface is invisible without explicit knowledge of the technique.

## Detection and defense

Ordered by effectiveness:

1.
**Disable the `phar://` stream wrapper entirely.**
   `stream_wrapper_unregister('phar')` at application bootstrap is the cleanest fix when no legitimate PHAR usage exists. This is the default posture for any application that does not deliberately distribute itself as a PHAR. The line is one statement in `bootstrap.php` or equivalent.

2.
**Use PHP 8.0+ where the manifest signature check is enforced.**
   Modern PHP refuses to read PHAR files whose signature does not match. This raises the bar but does not eliminate the attack — attackers control the signature too, since they author the polyglot. Treat this as defense-in-depth, not a primary fix.

3.
**Allowlist stream wrappers your code actually needs.**
   `stream_get_wrappers()` lists the registered wrappers; remove every one your app does not use. PHAR, `data://`, `expect://`, `php://filter` are the dangerous defaults; few applications need them in production. Combine with file-handling code that explicitly rejects URIs containing `://`.

4.
**Validate that path inputs are filesystem paths, not URIs.**
   At the boundary, reject any path containing `://`. Use `realpath()` early and verify the result starts with the expected base directory. Combined with allowlisting, this defeats the entire stream-wrapper-injection vector even if PHAR remains enabled.

5.
**Replace serialized PHAR-style metadata with signed JSON.**
   If the app legitimately distributes itself as a PHAR, the safe pattern is a JSON manifest with an HMAC verified before any deserialization. The serialized-PHP-object manifest is the vulnerable component.

6.
**Treat file uploads as untyped bytes.**
   Re-encode uploaded images through a strict pipeline that produces a normalized output (e.g., `imagecreatefromjpeg` followed by `imagejpeg` to a fresh buffer). Polyglots survive byte-preserving validation; they do not survive lossy re-encoding through a strict format. Combine with random server-chosen filenames so attacker cannot predict the path needed for `phar://` triggers.

### What does not work as a primary defense

- **Blocking `.phar` in upload allowlists.** Polyglots survive any extension check. The file's extension is whatever the attacker says it is.
- **MIME-type sniffing.** A polyglot's leading bytes are a real image header. `mime_content_type` and `finfo` both report `image/jpeg`.
- **`getimagesize()` validation.** Returns valid dimensions for a polyglot — that is the entire point of the polyglot.
- **Setting `phar.readonly=On`.** This blocks PHAR *creation*, not PHAR *reading*. Stops the attacker from generating PHARs server-side; does nothing to stop them uploading one and triggering it.
- **WAF signature blocking on `phar://`.** Trivially bypassed by URL-encoding (`phar%3a%2f%2f`), case variation, or by injection through fields the WAF does not inspect (form-data filenames, SOAP bodies, GraphQL variables).
- **Validating upload content-only.** The bug is on the *trigger* path, not the upload path. The most robust fix lives at the filesystem-API boundary, not at the upload boundary.

## Practical examples

- A forum's avatar upload accepts JPG. A separate "view profile" page calls `getimagesize($avatar_path)` to render dimensions. Attacker uploads polyglot, then visits a profile URL with `?avatar=phar://../uploads/123.jpg` — RCE.
- A CMS's plugin loader checks `file_exists("$plugin_dir/$slug/info.json")`. The slug is user-controlled. Attacker sets slug to `phar://uploads/payload.jpg/`. PHAR deserialization fires from the existence check.
- A document-management system's "preview" feature calls `imagecreatefromjpeg` on user-supplied paths. PHAR deserialization through the GD library's internal filesystem call.
- An RSS feed importer that fetches a URL and stores it locally, then calls `md5_file()` on the cached path. Attacker controls the cache path through a header injection — `phar://` schemes the cache.

## Related notes

- [[deserialization]] — parent concept; PHAR is one trigger mechanism for the kick-off gadget.
- [[gadget-chains]] — the chain still has to exist and reach a sink; PHAR provides only the trigger.
- [[file-upload-abuse]] — primary delivery mechanism; the polyglot is what defeats upload validation.
- [[path-traversal]] — frequent companion vulnerability; LFI plus PHAR is a common chain into RCE.
- [[ssrf]] — `phar://` paired with SSRF lets the attacker make the *server* fetch a remote PHAR via `phar://https://...` in some configurations.

### Suggested future atomic notes

- php-stream-wrappers
- polyglot-files
- sam-thomas-phar-deserialization
- lfi-to-rce-chains

## References

- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
- **Official Tool Docs:** PHPGGC `--phar` mode — https://github.com/ambionics/phpggc#phar-archives
