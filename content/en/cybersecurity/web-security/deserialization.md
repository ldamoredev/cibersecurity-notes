---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

==

# Insecure Deserialization

## Definition

Insecure deserialization is the act of reconstructing a typed object from attacker-controlled bytes, where the reconstruction process itself executes code paths under attacker influence. The bug is not "we accepted bad data" — it is "we instantiated an object graph from data we do not trust, and instantiation has side effects."

## Why it matters

This is the canonical *parser-as-execution-engine* vulnerability class. It matters because:

- It typically yields **remote code execution** without needing memory-corruption skill — just the right gadget chain in the dependency tree.
- The dangerous code runs **during** deserialization, before any application-level validation can fire. Most defensive instincts ("validate after parse") do not apply here.
- It scales across an entire ecosystem: every application using Apache Commons Collections (Java) or vulnerable PHP frameworks shares a single gadget chain. One library, many victims.
- It teaches a transferable lesson: **format complexity is attack surface**. JSON is safer than Java serialization not because JSON is magical but because most JSON parsers don't instantiate typed objects with custom constructors.

## How it works

Three-stage mental model — the *gadget chain*:

1. **Kick-off gadget** — a magic method the language runtime invokes automatically when deserializing (PHP `__wakeup`/`__destruct`, Java `readObject`, Python `__reduce__`).
2. **Intermediate gadgets** — a chain of method calls inside trusted libraries that pass attacker-controlled state from the kick-off point toward a dangerous method.
3. **Sink gadget** — the final method where attacker-controlled state becomes a dangerous operation (`Runtime.exec`, `eval`, file write, reflective invocation).

All three stages are *existing code* in the target application. The attacker contributes only the serialized data that walks the chain.

PHP serialized User object — readable on the wire:

```
O:4:"User":2:{s:4:"name":s:6:"carlos";s:10:"isLoggedIn":b:1;}
```

`O:4:"User"` declares an object of class `User` (4-char name) with 2 attributes. `s:N:"..."` is a string of length N, `i:N` is an integer, `b:0|1` is a boolean, `a:N:{...}` is an array. The format is human-readable, which is why PHP deserialization bugs are often discovered first by simply reading session cookies.

Java serialized streams begin with hex `ac ed 00 05` (base64 `rO0AB`). Any HTTP body, cookie, or hidden field starting with `rO0` is almost certainly a serialized Java object — instantly diagnostic during black-box testing.

The bug is not the gadget chain. The bug is **deserializing user input at all**.

## Techniques / patterns

What attackers look at and how they probe:

- **Identify the format on the wire**: PHP `O:` prefix, Java `rO0`/`ac ed`, Python pickle opcodes (`(c__main__\n...`), .NET BinaryFormatter signatures, Ruby Marshal `\x04\x08`.
- **Find the entry point**: cookies (most common), hidden form fields, HTTP headers, viewstate (.NET), authentication tokens carrying typed data, file uploads consumed via filesystem APIs.
- **Confirm deserialization happens at all**: send a payload that triggers a side channel — DNS lookup (ysoserial `URLDNS` chain), TCP connectback (`JRMPClient`), or a sleep — without needing any specific vulnerable library on the target.
- **Modify attributes first**: flip `isAdmin: false` → `isAdmin: true` in a serialized session before reaching for full RCE. Many "insecure deserialization" findings are actually "trusted-cookie privilege escalation" and never need a gadget chain.
- **Inject arbitrary object types**: deserializers usually do not validate the class. Substituting a different class whose magic methods do something useful is the gateway from data tampering to code execution.

## Variants and bypasses

### Object injection via class substitution

The deserializer instantiates whichever class the bytes name. Attacker swaps the expected `User` for any serializable class whose `__wakeup`/`readObject` does something dangerous on the controlled fields.

### Gadget chain RCE

Pre-built chains in libraries like Apache Commons Collections (Java) or various PHP frameworks. Tools weaponize them:
- **`ysoserial`** — Java payload generator with chains for Commons Collections, Spring, Groovy, Hibernate, etc. Java 16+ requires `--add-opens` flags. Universal probes: `URLDNS` (DNS lookup), `JRMPClient` (TCP connectback) — both trigger before any specific gadget chain is needed.
- **`PHPGGC`** — PHP equivalent with chains for Laravel, Symfony, WordPress, Drupal, etc.

### Type confusion (PHP-specific)

PHP's loose `==` comparison plus attacker-chosen types in deserialized data:

```
$login = unserialize($_COOKIE);
if ($login['password'] == $password) { /* log in */ }
```

Attacker serializes `password` as integer `0`. On PHP 7.x and earlier, `0 == "Example string"` evaluates true (string-to-number conversion stops at non-numeric). PHP 8+ changed this — verify the runtime version before testing.

### PHAR deserialization

PHP Archive (`.phar`) files contain serialized metadata. **Any** filesystem operation on a `phar://` stream implicitly deserializes that metadata, invoking `__wakeup`/`__destruct`. Attack:

1. Build a polyglot PHAR that also passes as a JPG.
2. Upload via file-upload functionality (which may only validate extension or MIME).
3. Trigger any code that runs `file_exists("phar://uploads/avatar.jpg")` or similar.
4. Metadata deserializes, kick-off magic method fires, gadget chain runs.

The trigger is *not* the upload. The trigger is the next code path that touches the file with a `phar://` stream wrapper.

### Polymorphic deserialization in modern formats

JSON/XML libraries that deserialize *into typed objects* with class-name hints reintroduce the same vuln. Jackson's polymorphic typing (`@JsonTypeInfo`), Gson's `RuntimeTypeAdapterFactory`, and XStream are the well-known reincarnations. The data format looks safe; the *binding library* is not.

## Impact

Ordered roughly by severity:

- **Remote code execution** — sink gadget reaches `exec`/`eval`/equivalent. Default ceiling for any deserialization bug with a viable gadget chain.
- **Authentication bypass / privilege escalation** — attacker tampers with serialized session/auth tokens (the type-confusion path, or simple attribute flip on unsigned cookies).
- **Arbitrary file read / write** — sink gadget reaches filesystem APIs.
- **Server-side request forgery** — sink gadget reaches HTTP/URL primitives. ysoserial's `URLDNS` is a degenerate version of this.
- **Denial of service** — billion-laughs-style nested object graphs or expensive constructors.

Conditions that escalate impact: same process running other tenants' sessions, deserialization in a privileged service (admin queue worker, background job processor), or a JVM/PHP-FPM hosting other apps in shared classpath.

## Detection and defense

Ordered by effectiveness:

1.
**Do not deserialize untrusted input.**
   This is the only defense that addresses the root cause. Replace native serialization with data-only formats (JSON without polymorphic typing, Protobuf, MessagePack) and reconstruct domain objects with explicit, type-checked code. Every other defense is a mitigation.

2.
**If you must accept serialized data, sign it and verify *before* deserializing.**
   HMAC the bytes with a server-only key; reject the payload outright if the signature does not match, and never call `unserialize`/`readObject` on unverified bytes. The signature must be checked on the *bytes*, not on a parsed-then-validated object — checks that run after deserialization are too late, because the dangerous code already executed.

3.
**Use a class allowlist (`ObjectInputFilter` in Java, equivalent in .NET).**
   Restrict the deserializer to a small set of known-safe classes. This shuts down arbitrary-class injection even if the bytes are manipulated. Maintain the list deliberately — every new class added is a new attack-surface decision.

4.
**Replace generic serialization with class-specific methods.**
   Hand-rolled `serialize`/`deserialize` for each domain class lets you choose which fields cross the wire and validate types as you reconstruct. This prevents "framework deserializes private fields you forgot existed."

5.
**Strip dangerous gadget chains from the dependency tree where feasible.**
   Useful as defense-in-depth, but **not a primary defense** — see "what does not work" below. Dependency hygiene shrinks the chain library; it does not eliminate the vulnerability.

6.
**Monitor for deserialization fingerprints in unexpected places.**
   Alerts for `rO0` / `ac ed` / `phar://` / pickle opcodes appearing in inbound HTTP traffic where they should not appear. Catches bugs introduced by a careless library upgrade that suddenly accepts richer payloads.

### What does not work as a primary defense

- **Post-deserialization validation.** The dangerous code runs *during* deserialization. Validating the resulting object is checking the crime scene after the murder.
- **Eliminating known gadget chains.** Modern dependency trees contain hundreds of classes. New chains are discovered yearly. The path of least failure is to not deserialize untrusted input — not to play whack-a-mole with library versions.
- **Obfuscating the format.** Binary doesn't help. `rO0` is as recognizable as plaintext PHP. Attackers identify formats by structure, not by readability.
- **WAF signatures alone.** WAFs catch the common base64-encoded ysoserial payloads; they do not catch novel chains, custom-encoded payloads, or PHAR triggers that look like image uploads.

## Practical examples

- A "remember me" cookie storing a serialized PHP `User` object — attacker flips `isAdmin: false → true`, no gadget chain needed.
- A Java microservice receiving serialized RPC payloads over HTTP from internal callers — attacker reaches the service and lands ysoserial CommonsCollections5 RCE.
- A file-upload feature plus a thumbnail generator that calls `file_exists("phar://uploads/$id")` — PHAR deserialization turns avatar upload into RCE.
- A .NET app using `BinaryFormatter` to deserialize ViewState or session — RCE via known gadget chains, plus Microsoft has officially deprecated `BinaryFormatter` for exactly this reason.
- A modern Spring Boot service using Jackson polymorphic typing on a public endpoint — JSON looks safe; the binder instantiates whatever class the `@type` field names, reintroducing the full vulnerability class.
- An auth flow comparing a deserialized password field with `==` in PHP 7 — type-confusion bypass without ever needing RCE.

## Related notes

- [[gadget-chains]] — the exploitation half: the kick-off / intermediate / sink mental model and the language-by-language chain catalogs.
- [[phar-deserialization]] — PHP-specific kick-off mechanism that triggers from filesystem operations rather than `unserialize`.
- [[polymorphic-deserialization|Polymorphic deserialization]] — same chain shape reintroduced through JSON/YAML/XML binders (Jackson, Newtonsoft, SnakeYAML).
- [[file-upload-abuse]] — PHAR deserialization is the high-impact tail of the upload + filesystem-call combination.
- [[auth-flaws]] — type-confusion bypass and tampered serialized sessions are deserialization-rooted authentication flaws.
- [[business-logic-vulnerabilities]] — many real findings present as "the cookie is trusted," which is a logic flaw whose root cause is unsafe deserialization.
- [[xss]] — both teach the same lesson at different layers: every parser is an execution engine until proven otherwise.
- [[cookies-and-sessions]] — primary delivery channel for serialized payloads.
- [[jwt-attacks|JWT attacks]] — adjacent: structured client-supplied data deserialized into typed claims with library quirks.
- [[mass-assignment|Mass assignment]] — adjacent class: framework instantiates whatever the client sent.

### Suggested future atomic notes

- php-serialization-format
- java-serialization-format
- python-pickle
- type-juggling

## References

- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Insecure deserialization topic — https://portswigger.net/web-security/deserialization
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (PHAR deserialization) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
