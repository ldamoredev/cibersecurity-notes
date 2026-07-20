---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Gadget Chains

## Definition

A gadget chain is a sequence of method invocations through *existing trusted code* that walks attacker-controlled data from a deserialization entry point to a dangerous sink. The attacker writes no new code on the target — they only choose which serialized object graph the deserializer reconstructs, and the chain is whatever methods that graph causes the runtime to invoke.

## Why it matters

The gadget-chain mental model is what separates a casual deserialization finding ("I tampered with a cookie") from a productized RCE primitive. It matters because:

- It explains why "we removed the vulnerable library" is a losing defense. Modern dependency trees contain hundreds of classes that can become a gadget link; new chains are published every year. Whack-a-mole on chains never converges.
- It transfers cleanly across attack classes. The same kick-off / intermediate / sink shape applies to JSON polymorphic deserialization (Jackson, Newtonsoft), XML binding (XStream), .NET `BinaryFormatter`, Python pickle, YAML loaders. If you can read the gadget-chain shape, you can read all of them.
- It clarifies the threat model. The application is not "executing the attacker's code" — it is calling its own legitimate methods on data that should never have been allowed to choose what gets called. The bug is the deserialization, not the chain.
- It teaches a transferable design lesson: **reflective instantiation of attacker-named types is execution**, even when the data format looks inert.

## How it works

The chain has three named stages. All three are *existing code* on the target.

1. **Kick-off gadget** — a method the language runtime invokes automatically when reconstructing the object graph. PHP `__wakeup()` / `__destruct()`, Java `readObject(ObjectInputStream)`, Python `__reduce__`, Ruby `_load`, .NET `OnDeserialized` callbacks. The deserializer calls this with no application code in between.
2. **Intermediate gadgets** — methods invoked from the kick-off (or from each prior link) that pass attacker-controlled state forward. Often these are innocent-looking helpers: a logger that calls `toString()` on the message, a comparator that invokes `equals()`, a transformer that wraps a `Method.invoke()`. Each link does one ordinary operation; the chain is the composition.
3. **Sink gadget** — the final method where attacker-controlled state becomes a dangerous primitive: `Runtime.exec`, `eval`, `ProcessBuilder.start`, `URL.openStream`, `File.write`, reflective method invocation. RCE is the typical ceiling, but file write, SSRF, or auth bypass are also valid sinks.

The canonical demonstration is the Apache Commons Collections `InvokerTransformer` chain in Java:
- Kick-off: a `HashMap` whose `hashCode()` is invoked during `readObject`.
- Intermediate: keys are `LazyMap` entries whose `get()` calls `ChainedTransformer.transform()`.
- Sink: the final `InvokerTransformer` reflectively calls `Runtime.getRuntime().exec(cmd)`.

The application contains no malicious code. It contains `HashMap`, `LazyMap`, and `InvokerTransformer`. Composing them is the bug.

## Techniques / patterns

What attackers look at and how they probe:

- **Identify the deserialization format on the wire** before reaching for chains. Java `rO0`/`ac ed`, PHP `O:N:"..."`, Python pickle opcodes (`(c__main__\n...`), .NET `AAEAAAD/////` (BinaryFormatter), Ruby Marshal `\x04\x08`, YAML `!!ruby/object:` or `!!python/object:`.
- **Confirm deserialization happens at all** with a *universal* probe before searching for an application-specific chain:
- `URLDNS` (ysoserial) — triggers a DNS lookup to attacker-controlled domain. Detectable via Burp Collaborator. Works against any Java target that calls `readObject`.
- `JRMPClient` (ysoserial) — forces a TCP connectback. Works without specific gadgets.
- For PHP, a custom payload that calls `dns_get_record()` in a `__destruct()` of a known-loaded class.
- **Enumerate the classpath / loaded libraries**. Common bug-bounty path: response headers leak server tech (`X-Powered-By: WildFly`), error pages leak stack traces with library names, source maps leak npm dependencies. Match the dependency list against ysoserial / PHPGGC chain catalogs.
- **Use the prebuilt tooling first**. Hand-rolled chains are rarely necessary — start with:
- `ysoserial` — Java, dozens of chains for Commons Collections (1–7), Spring 1/2, Groovy, Hibernate, JBoss, Hibernate, Jackson polymorphic, etc.
- `PHPGGC` — PHP, chains for Laravel, Symfony, WordPress, Drupal, Monolog, Guzzle, Doctrine, Slim, etc.
- `marshalsec` — JNDI / LDAP / RMI gadgets, polymorphic JSON/XML/YAML binders.
- **Hand-build a chain when the target's library set is unusual**. The mental loop: pick a magic-method entry point that exists in any loaded class, walk the call graph forward looking for any method that does *something with input* (reflection, `Class.forName`, `eval`, file ops), then trace backward to the kick-off.

## Variants and bypasses

### Java — Commons Collections family

The original. Versions 1–7 in ysoserial, each adapted to a slightly different version of Commons Collections. Sink is always reflective `Runtime.exec`. Triggers Apache Struts2 RCE (CVE-2017-9805 used XStream rather than native Java serialization, but the chain shape is identical), JBoss, WebSphere, Jenkins, OpenNMS, and dozens of enterprise products.

### Java — non-Commons chains

- **Spring 1 / 2** — `DefaultListableBeanFactory` chains. Useful when Commons Collections is not on the classpath.
- **Groovy** — `MethodClosure` lets the chain end at arbitrary method invocation.
- **Hibernate** — `TypedValue` + `PojoComponentTuplizer` reach reflective execution.
- **JRE-only chains** — newer ysoserial entries (`URLDNS`, `JRMPClient`) work on a vanilla JRE with no extra libraries. Limited sinks (DNS, TCP) but require zero dependency assumptions.

### PHP — PHPGGC families

Framework-specific chains that exploit the framework's own classes:
- **Laravel** — chain ends in `Symfony\Component\HttpKernel\HttpKernelBrowser` or similar.
- **Monolog** — `__destruct` on a logger reaches `proc_open` via a `BufferHandler`.
- **Guzzle** — chain reaches HTTP request side-effects useful for SSRF.
- **WordPress / Drupal** — application-specific chains that exploit plugin classes.

### .NET — `BinaryFormatter` and `LosFormatter`

- `BinaryFormatter` — Microsoft has officially deprecated it for exactly this reason; chains via `ObjectDataProvider`, `WindowsIdentity`, `System.Configuration.Install.AssemblyInstaller`.
- `LosFormatter` — used by ASP.NET ViewState. Chains identical in shape; ysoserial.NET covers them.
- `Json.NET` with `TypeNameHandling.All` reintroduces the same chain surface in JSON; see [[polymorphic-deserialization]] for the JSON polymorphic case.

### Python — pickle `__reduce__`

Single-link "chain": `__reduce__` returns `(os.system, ("id",))` and the unpickler obediently calls it. Pickle is unique in that the format itself is a stack-based VM — gadget chains are barely needed. Treat any `pickle.loads()` on untrusted data as immediate RCE.

### Ruby — Marshal + ActiveSupport

`Marshal.load` on attacker-controlled bytes plus a Rails app on the classpath gives chains via `ActionDispatch::Cookies::CookieJar` and `ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy`.

### Universal blind probes

When you cannot identify the library set, the universal chains (`URLDNS`, `JRMPClient` for Java; DNS-callback `__wakeup` for PHP) confirm deserialization happens and tell you to invest more effort. Always probe blind first.

## Impact

Severity matches the strength of the sink, not the existence of the chain:

- **RCE** — sink reaches `exec`/`eval`/equivalent. Default ceiling for any chain reaching an OS-level primitive.
- **SSRF** — sink reaches HTTP/URL primitives (`URLDNS`, Guzzle chains, .NET `WebClient`).
- **File read / write** — sink reaches filesystem APIs (`File.write`, `fopen` in `w` mode).
- **Auth bypass / privilege escalation** — chain modifies server-side authorization state (e.g., flipping `isAdmin` via reflective field write).
- **Denial of service** — degenerate chains: nested object graphs, billion-laughs-style hash collisions in `HashMap` keys.

## Detection and defense

Ordered by effectiveness:

1.
**Don't deserialize untrusted input.**
   This is the only defense that addresses the class. If untrusted bytes never reach `readObject` / `unserialize` / `pickle.loads`, no chain can fire. Replace native serialization with data-only formats (JSON without polymorphic typing, Protobuf with explicit schemas, MessagePack) and reconstruct domain objects with explicit, type-checked code paths. Every other defense is a mitigation.

2.
**Verify integrity *before* deserializing.**
   HMAC the bytes with a server-only key; reject the payload outright if the signature does not match. The check must run on the bytes, not on a parsed-then-validated object — checks that run after deserialization are too late, because the kick-off gadget already fired. This is the standard pattern for "we must accept a typed cookie."

3.
**Apply a class allowlist at the deserializer level.**
   Java `ObjectInputFilter` (JEP 290), .NET `SerializationBinder`, Jackson `BasicPolymorphicTypeValidator`, Python `pickle.Unpickler.find_class` override. Each restricts which classes the deserializer is willing to instantiate. Maintain the list deliberately — every class added is an attack-surface decision. Allowlists shut down arbitrary-class injection even if the bytes are tampered with.

4.
**Replace generic serialization with class-specific methods.**
   Hand-rolled `serialize`/`deserialize` for each domain class lets you choose which fields cross the wire and validate types as you reconstruct. Prevents "the framework deserialized a private field you forgot existed."

5.
**Trim known gadget-chain libraries from the dependency tree.**
   Defense-in-depth, not primary defense. Removing Commons Collections from a classpath that does not need it is good hygiene; it is not a strategy. The chain set grows; the dependency tree drifts; the next ysoserial release changes the answer. See "what does not work" below.

6.
**Monitor for deserialization fingerprints in unexpected places.**
   Inbound traffic carrying `rO0`/`ac ed`/`O:`/PHP-PHAR/pickle opcodes/`AAEAAAD` where it should not appear is high-signal. WAF rules for these prefixes catch the off-the-shelf payloads even when the chain is novel.

### What does not work as a primary defense

- **Removing one vulnerable library at a time.** The chain set is not a fixed list. Apache Commons Collections was the canonical example for years; modern ysoserial has chains in plain JRE classes, in Spring, in Hibernate, in Groovy, in C3P0, in Hibernate, in BeanShell. New chains are published faster than dependency teams remove old ones. Do not budget defense around "we removed the chain library."
- **Validating after deserialization.** The kick-off gadget runs during `readObject`. By the time the application sees the resulting object, the sink may have already executed.
- **Obfuscating or encrypting the format on the wire.** Encryption defends against tampering only if the key is server-side and the integrity check runs *before* deserialization. If the key leaks or the cipher is malleable, the chain is back.
- **WAF signatures alone.** WAFs catch base64 ysoserial payloads and known PHPGGC prefixes. They do not catch hand-built chains, custom-encoded payloads, or chains delivered through indirect paths (PHAR streams, JNDI lookups).
- **Java `SecurityManager`.** Deprecated and removed in Java 17+. Even when present, it does not prevent the chain — it only restricts the sink's effect, and most chains reach sinks the SecurityManager does not gate.

## Practical examples

- An internal Java RPC service receiving serialized payloads over HTTP from "trusted" callers — attacker reaches the service through a misconfigured ingress and lands `ysoserial CommonsCollections5`.
- A legacy PHP forum's session cookie holds a serialized `User` — PHPGGC-built chain via the bundled Monolog dependency reaches `proc_open`.
- A .NET ASP.NET application using `BinaryFormatter` for ViewState — ysoserial.NET chain via `ObjectDataProvider`. Microsoft has flagged this as the top reason `BinaryFormatter` is deprecated.
- A Python ML inference server accepting pickled models from S3 — `__reduce__`-based payload runs as a single-link chain. The "chain" is just the unpickler honoring `__reduce__`.
- A SnakeYAML loader behind an admin import feature — a `!!java.net.URLClassLoader` payload with a nested URL list constructs a class loader and triggers remote class load.

## Related notes

- [[deserialization]] — the parent concept; gadget chains are the exploitation half.
- [[phar-deserialization]] — the PHP-specific *trigger* for the kick-off, distinct from the chain itself.
- [[polymorphic-deserialization|Polymorphic deserialization]] — the same chain shape reintroduced through JSON/XML/YAML binders.
- [[file-upload-abuse]] — common delivery mechanism, especially for PHAR and pickle.
- [[ssrf]] — the `URLDNS` family of chains is effectively SSRF-as-detection.

### Suggested future atomic notes

- ysoserial-chains
- phpggc-chains
- jndi-injection
- binaryformatter-chains
- snakeyaml-chains

## References

- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Chris Frohoff & Gabriel Lawrence, "Marshalling Pickles" (AppSecCali 2015, original ysoserial talk) — https://frohoff.github.io/appseccali-marshalling-pickles/
- **Official Tool Docs:** ysoserial — https://github.com/frohoff/ysoserial
- **Official Tool Docs:** PHPGGC — https://github.com/ambionics/phpggc
