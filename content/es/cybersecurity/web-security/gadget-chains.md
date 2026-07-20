# Gadget Chains

## Definición

Una gadget chain es una secuencia de invocaciones de métodos a través de *código de confianza existente* que recorre datos controlados por el atacante desde un punto de entrada de deserialización hasta un sink peligroso. El atacante no escribe código nuevo en el objetivo — solo elige qué grafo de objetos serializados reconstruye el deserializador, y la cadena es cualquier cosa que ese grafo haga invocar al runtime.

## Por qué importa

El modelo mental de gadget chain es lo que separa un hallazgo casual de deserialización ("manipulé una cookie") de un primitivo RCE productizado. Importa porque:

- Explica por qué "eliminamos la librería vulnerable" es una defensa perdedora. Los árboles de dependencias modernos contienen cientos de clases que pueden convertirse en un eslabón de la cadena; se publican nuevas cadenas cada año. El whack-a-mole con cadenas nunca converge.
- Se transfiere limpiamente a través de clases de ataque. La misma forma kick-off / intermediate / sink aplica a la deserialización polimórfica JSON (Jackson, Newtonsoft), binding XML (XStream), .NET `BinaryFormatter`, pickle de Python, cargadores YAML. Si podés leer la forma de la gadget chain, podés leerlas todas.
- Clarifica el threat model. La aplicación no está "ejecutando el código del atacante" — está llamando a sus propios métodos legítimos en datos que nunca deberían haber podido elegir qué se llama. El bug es la deserialización, no la cadena.
- Enseña una lección de diseño transferible: **la instanciación reflectiva de tipos nombrados por el atacante es ejecución**, incluso cuando el formato de datos parece inerte.

## Cómo funciona

La cadena tiene tres etapas con nombre. Las tres son *código existente* en el objetivo.

1. **Gadget de kick-off** — un método que el runtime del lenguaje invoca automáticamente al reconstruir el grafo de objetos. PHP `__wakeup()` / `__destruct()`, Java `readObject(ObjectInputStream)`, Python `__reduce__`, Ruby `_load`, callbacks .NET `OnDeserialized`. El deserializador llama a esto sin código de aplicación de por medio.
2. **Gadgets intermedios** — métodos invocados desde el kick-off (o desde cada eslabón anterior) que pasan el estado controlado por el atacante hacia adelante. Frecuentemente son helpers de aspecto inocente: un logger que llama `toString()` en el mensaje, un comparador que invoca `equals()`, un transformer que envuelve un `Method.invoke()`. Cada eslabón hace una operación ordinaria; la cadena es la composición.
3. **Gadget sink** — el método final donde el estado controlado por el atacante se convierte en un primitivo peligroso: `Runtime.exec`, `eval`, `ProcessBuilder.start`, `URL.openStream`, `File.write`, invocación reflectiva de método. RCE es el techo típico, pero escritura de archivo, SSRF, o bypass de auth también son sinks válidos.

La demostración canónica es la cadena `InvokerTransformer` de Apache Commons Collections en Java:
- Kick-off: un `HashMap` cuyo `hashCode()` es invocado durante `readObject`.
- Intermedio: las claves son entradas de `LazyMap` cuyo `get()` llama a `ChainedTransformer.transform()`.
- Sink: el `InvokerTransformer` final llama reflectivamente a `Runtime.getRuntime().exec(cmd)`.

La aplicación no contiene código malicioso. Contiene `HashMap`, `LazyMap` e `InvokerTransformer`. Componerlos es el bug.

## Técnicas / patrones

Qué miran los atacantes y cómo sondean:

- **Identificar el formato de deserialización en el wire** antes de buscar cadenas. Java `rO0`/`ac ed`, PHP `O:N:"..."`, opcodes de pickle de Python (`(c__main__\n...`), .NET `AAEAAAD/////` (BinaryFormatter), Ruby Marshal `\x04\x08`, YAML `!!ruby/object:` o `!!python/object:`.
- **Confirmar que la deserialización ocurre** con una sonda *universal* antes de buscar una cadena específica de la aplicación:
  - `URLDNS` (ysoserial) — dispara un lookup DNS hacia el dominio controlado por el atacante. Detectable vía Burp Collaborator. Funciona contra cualquier objetivo Java que llame `readObject`.
  - `JRMPClient` (ysoserial) — fuerza un TCP connectback. Funciona sin gadgets específicos.
  - Para PHP, un payload personalizado que llama `dns_get_record()` en un `__destruct()` de una clase conocida cargada.
- **Enumerar el classpath / librerías cargadas**. Ruta común de bug bounty: los response headers filtran tecnología del servidor (`X-Powered-By: WildFly`), las páginas de error filtran stack traces con nombres de librerías, los source maps filtran dependencias npm. Cruzar la lista de dependencias con los catálogos de cadenas de ysoserial / PHPGGC.
- **Usar primero las herramientas prefabricadas**. Las cadenas hechas a mano raramente son necesarias — empezar con:
  - `ysoserial` — Java, docenas de cadenas para Commons Collections (1–7), Spring 1/2, Groovy, Hibernate, JBoss, Jackson polimórfico, etc.
  - `PHPGGC` — PHP, cadenas para Laravel, Symfony, WordPress, Drupal, Monolog, Guzzle, Doctrine, Slim, etc.
  - `marshalsec` — gadgets JNDI / LDAP / RMI, binders polimórficos JSON/XML/YAML.
- **Construir a mano una cadena cuando el conjunto de librerías del objetivo es inusual**. El bucle mental: elegir un punto de entrada magic-method que exista en cualquier clase cargada, recorrer el grafo de llamadas hacia adelante buscando cualquier método que haga *algo con input* (reflexión, `Class.forName`, `eval`, ops de archivo), luego trazar hacia atrás hasta el kick-off.

## Variantes y bypasses

### Java — familia Commons Collections

La original. Versiones 1–7 en ysoserial, cada una adaptada a una versión ligeramente diferente de Commons Collections. El sink es siempre `Runtime.exec` reflectivo. Dispara RCE de Apache Struts2, JBoss, WebSphere, Jenkins, OpenNMS y docenas de productos enterprise.

### Java — cadenas no-Commons

- **Spring 1 / 2** — cadenas `DefaultListableBeanFactory`. Útil cuando Commons Collections no está en el classpath.
- **Groovy** — `MethodClosure` permite que la cadena termine en invocación de método arbitrario.
- **Hibernate** — `TypedValue` + `PojoComponentTuplizer` alcanzan ejecución reflectiva.
- **Cadenas solo-JRE** — entradas más nuevas de ysoserial (`URLDNS`, `JRMPClient`) funcionan en una JRE vanilla sin librerías extras. Sinks limitados (DNS, TCP) pero requieren zero suposiciones de dependencias.

### PHP — familias PHPGGC

Cadenas específicas de framework que explotan las propias clases del framework:
- **Laravel** — la cadena termina en `Symfony\Component\HttpKernel\HttpKernelBrowser` o similar.
- **Monolog** — `__destruct` en un logger alcanza `proc_open` vía un `BufferHandler`.
- **Guzzle** — la cadena alcanza efectos secundarios de HTTP request útiles para SSRF.
- **WordPress / Drupal** — cadenas específicas de aplicación que explotan clases de plugins.

### .NET — `BinaryFormatter` y `LosFormatter`

- `BinaryFormatter` — Microsoft lo ha deprecado oficialmente exactamente por esto; cadenas vía `ObjectDataProvider`, `WindowsIdentity`, `System.Configuration.Install.AssemblyInstaller`.
- `LosFormatter` — usado por ASP.NET ViewState. Las cadenas son idénticas en forma; ysoserial.NET las cubre.
- `Json.NET` con `TypeNameHandling.All` reintroduce la misma superficie de cadena en JSON.

### Python — pickle `__reduce__`

"Cadena" de un solo eslabón: `__reduce__` devuelve `(os.system, ("id",))` y el unpickler obedientemente lo llama. Pickle es único en que el formato en sí es una VM basada en stack — las gadget chains apenas se necesitan. Tratar cualquier `pickle.loads()` en datos no confiables como RCE inmediato.

### Ruby — Marshal + ActiveSupport

`Marshal.load` en bytes controlados por el atacante más una app Rails en el classpath da cadenas vía `ActionDispatch::Cookies::CookieJar` y `ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy`.

### Sondas ciegas universales

Cuando no se puede identificar el conjunto de librerías, las cadenas universales (`URLDNS`, `JRMPClient` para Java; `__wakeup` con callback DNS para PHP) confirman que la deserialización ocurre y dicen que hay que invertir más esfuerzo. Siempre sondear ciegamente primero.

## Impacto

La severidad coincide con la fortaleza del sink, no con la existencia de la cadena:

- **RCE** — el sink alcanza `exec`/`eval`/equivalente. Techo por defecto para cualquier cadena que alcance un primitivo a nivel de OS.
- **SSRF** — el sink alcanza primitivos HTTP/URL (`URLDNS`, cadenas de Guzzle, .NET `WebClient`).
- **Lectura / escritura de archivo** — el sink alcanza APIs del sistema de archivos (`File.write`, `fopen` en modo `w`).
- **Bypass de auth / escalada de privilegios** — la cadena modifica el estado de autorización del lado del servidor.
- **Denegación de servicio** — cadenas degeneradas: grafos de objetos anidados, colisiones de hash estilo billion-laughs en claves de `HashMap`.

## Detección y defensa

Ordenado por efectividad:

1.
**No deserializar input no confiable.**
   Esta es la única defensa que aborda la clase. Si los bytes no confiables nunca llegan a `readObject` / `unserialize` / `pickle.loads`, ninguna cadena puede dispararse. Reemplazar la serialización nativa con formatos solo-datos (JSON sin tipado polimórfico, Protobuf con esquemas explícitos, MessagePack) y reconstruir objetos de dominio con rutas de código explícitas y type-checked. Toda otra defensa es una mitigación.

2.
**Verificar integridad *antes* de deserializar.**
   Aplicar HMAC a los bytes con una clave solo del servidor; rechazar el payload completamente si la firma no coincide. La verificación debe ejecutarse en los bytes, no en un objeto parseado-y-luego-validado — las verificaciones que se ejecutan después de la deserialización son demasiado tardías, porque el gadget de kick-off ya se disparó. Este es el patrón estándar para "debemos aceptar una cookie tipada."

3.
**Aplicar una allowlist de clases a nivel del deserializador.**
   Java `ObjectInputFilter` (JEP 290), .NET `SerializationBinder`, `BasicPolymorphicTypeValidator` de Jackson, override de `pickle.Unpickler.find_class` de Python. Cada uno restringe qué clases está dispuesto a instanciar el deserializador. Mantener la lista deliberadamente — cada clase añadida es una decisión de superficie de ataque. Las allowlists cierran la inyección de clases arbitrarias incluso si los bytes son manipulados.

4.
**Reemplazar la serialización genérica con métodos específicos por clase.**
   Un `serialize`/`deserialize` hecho a mano para cada clase de dominio permite elegir qué campos cruzan el wire y validar tipos al reconstruir. Previene "el framework deserializó un campo privado que olvidaste que existía."

5.
**Recortar librerías conocidas de gadget chains del árbol de dependencias.**
   Defensa en profundidad, no defensa primaria. Eliminar Commons Collections de un classpath que no lo necesita es buena higiene; no es una estrategia. El conjunto de cadenas crece; el árbol de dependencias deriva; la próxima versión de ysoserial cambia la respuesta.

6.
**Monitorear fingerprints de deserialización en lugares inesperados.**
   El tráfico entrante que lleva `rO0`/`ac ed`/`O:`/PHP-PHAR/opcodes de pickle/`AAEAAAD` donde no debería aparecer es de alta señal. Las reglas WAF para estos prefijos detectan los payloads off-the-shelf incluso cuando la cadena es novedosa.

### Qué no funciona como defensa primaria

- **Eliminar una librería vulnerable a la vez.** El conjunto de cadenas no es una lista fija. Apache Commons Collections fue el ejemplo canónico por años; el ysoserial moderno tiene cadenas en clases JRE planas, en Spring, en Hibernate, en Groovy, en C3P0. Se publican nuevas cadenas más rápido de lo que los equipos de dependencias eliminan las viejas. No presupuestes la defensa en "eliminamos la librería de cadenas."
- **Validar después de la deserialización.** El gadget de kick-off se ejecuta durante `readObject`. Para cuando la aplicación ve el objeto resultante, el sink puede ya haberse ejecutado.
- **Ofuscar o cifrar el formato en el wire.** El cifrado defiende contra la manipulación solo si la clave es del lado del servidor y la verificación de integridad se ejecuta *antes* de la deserialización. Si la clave se filtra o el cifrado es maleable, la cadena vuelve.
- **Solo firmas WAF.** Los WAFs detectan payloads ysoserial codificados en base64 y prefijos PHPGGC conocidos. No detectan cadenas hechas a mano, payloads con codificación personalizada, o cadenas entregadas a través de rutas indirectas (streams PHAR, lookups JNDI).

## Ejemplos prácticos

- Un servicio Java RPC interno que recibe payloads serializados sobre HTTP de llamantes "de confianza" — el atacante alcanza el servicio a través de un ingress mal configurado y ejecuta `ysoserial CommonsCollections5`.
- La cookie de sesión de un foro PHP legacy contiene un `User` serializado — cadena construida con PHPGGC vía la dependencia Monolog incluida alcanza `proc_open`.
- Una app .NET ASP.NET que usa `BinaryFormatter` para ViewState — cadena de ysoserial.NET vía `ObjectDataProvider`. Microsoft ha marcado esto como la razón principal por la que `BinaryFormatter` está deprecado.
- Un servidor de inferencia Python ML que acepta modelos pickleados desde S3 — payload basado en `__reduce__` se ejecuta como una cadena de un solo eslabón. La "cadena" es solo el unpickler que honra `__reduce__`.
- Un loader SnakeYAML detrás de una funcionalidad de importación admin — un payload `!!java.net.URLClassLoader` con una lista URL anidada construye un class loader y dispara la carga de clase remota.

## Notas relacionadas

- [[deserialization]] — el concepto padre; las gadget chains son la mitad de explotación.
- [[phar-deserialization]] — el *trigger* específico de PHP para el kick-off, distinto de la cadena en sí.
- [[file-upload-abuse]] — mecanismo de entrega común, especialmente para PHAR y pickle.
- [[ssrf]] — la familia de cadenas `URLDNS` es efectivamente SSRF-como-detección.

## Referencias

- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Chris Frohoff & Gabriel Lawrence, "Marshalling Pickles" (AppSecCali 2015, original ysoserial talk) — https://frohoff.github.io/appseccali-marshalling-pickles/
- **Docs Oficiales:** ysoserial — https://github.com/frohoff/ysoserial
- **Docs Oficiales:** PHPGGC — https://github.com/ambionics/phpggc
