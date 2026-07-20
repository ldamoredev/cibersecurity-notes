# Insecure Deserialization

## Definición

La deserialización insegura es el acto de reconstruir un objeto tipado a partir de bytes controlados por el atacante, donde el proceso de reconstrucción en sí ejecuta rutas de código bajo la influencia del atacante. El bug no es "aceptamos datos incorrectos" — es "instanciamos un grafo de objetos a partir de datos en los que no confiamos, e instanciar tiene efectos secundarios."

## Por qué importa

Esta es la clase de vulnerabilidad canónica de *parser-como-motor-de-ejecución*. Importa porque:

- Típicamente produce **ejecución remota de código** sin necesitar habilidades de corrupción de memoria — solo la cadena de gadgets correcta en el árbol de dependencias.
- El código peligroso se ejecuta **durante** la deserialización, antes de que pueda dispararse cualquier validación a nivel de aplicación. La mayoría de los instintos defensivos ("validar después de parsear") no aplican aquí.
- Escala a través de un ecosistema entero: cada aplicación que usa Apache Commons Collections (Java) o frameworks PHP vulnerables comparte una única cadena de gadgets. Una librería, muchas víctimas.
- Enseña una lección transferible: **la complejidad del formato es superficie de ataque**. JSON es más seguro que la serialización de Java no porque JSON sea mágico sino porque la mayoría de los parsers JSON no instancian objetos tipados con constructores personalizados.

## Cómo funciona

Modelo mental de tres etapas — la *gadget chain*:

1. **Gadget de kick-off** — un método mágico que el runtime del lenguaje invoca automáticamente al deserializar (PHP `__wakeup`/`__destruct`, Java `readObject`, Python `__reduce__`).
2. **Gadgets intermedios** — una cadena de llamadas a métodos dentro de librerías de confianza que pasan el estado controlado por el atacante desde el punto de kick-off hacia un método peligroso.
3. **Gadget sink** — el método final donde el estado controlado por el atacante se convierte en una operación peligrosa (`Runtime.exec`, `eval`, escritura de archivo, invocación reflectiva).

Las tres etapas son *código existente* en la aplicación objetivo. El atacante solo contribuye los datos serializados que recorren la cadena.

Objeto PHP serializado User — legible en el wire:

```
O:4:"User":2:{s:4:"name":s:6:"carlos";s:10:"isLoggedIn":b:1;}
```

`O:4:"User"` declara un objeto de clase `User` (nombre de 4 caracteres) con 2 atributos. `s:N:"..."` es un string de longitud N, `i:N` es un entero, `b:0|1` es un booleano, `a:N:{...}` es un array. El formato es legible por humanos, razón por la que los bugs de deserialización PHP frecuentemente se descubren primero simplemente leyendo las cookies de sesión.

Los streams serializados de Java comienzan con hex `ac ed 00 05` (base64 `rO0AB`). Cualquier cuerpo HTTP, cookie o campo oculto que comience con `rO0` es casi con certeza un objeto Java serializado — inmediatamente diagnóstico durante testing de caja negra.

El bug no es la gadget chain. El bug es **deserializar input del usuario en absoluto**.

## Técnicas / patrones

Qué miran los atacantes y cómo sondean:

- **Identificar el formato en el wire**: prefijo PHP `O:`, Java `rO0`/`ac ed`, opcodes de pickle de Python (`(c__main__\n...`), firmas de .NET BinaryFormatter, Ruby Marshal `\x04\x08`.
- **Encontrar el punto de entrada**: cookies (el más común), campos de formulario ocultos, HTTP headers, viewstate (.NET), tokens de autenticación que llevan datos tipados, subidas de archivo consumidas vía APIs del sistema de archivos.
- **Confirmar que la deserialización ocurre**: enviar un payload que dispare un canal lateral — lookup DNS (cadena `URLDNS` de ysoserial), TCP connectback (`JRMPClient`), o un sleep — sin necesitar ninguna librería vulnerable específica en el objetivo.
- **Modificar atributos primero**: cambiar `isAdmin: false` → `isAdmin: true` en una sesión serializada antes de ir por RCE completo. Muchos hallazgos de "deserialización insegura" son en realidad "escalada de privilegios de cookie de confianza" y nunca necesitan una gadget chain.
- **Inyectar tipos de objeto arbitrarios**: los deserializadores generalmente no validan la clase. Sustituir una clase diferente cuyos métodos mágicos hacen algo útil es la puerta de entrada desde la manipulación de datos hasta la ejecución de código.

## Variantes y bypasses

### Inyección de objeto vía sustitución de clase

El deserializador instancia cualquier clase que nombren los bytes. El atacante cambia el `User` esperado por cualquier clase serializable cuyo `__wakeup`/`readObject` haga algo peligroso con los campos controlados.

### RCE por gadget chain

Cadenas prefabricadas en librerías como Apache Commons Collections (Java) o varios frameworks PHP. Las herramientas las convierten en armas:
- **`ysoserial`** — generador de payloads Java con cadenas para Commons Collections, Spring, Groovy, Hibernate, etc. Java 16+ requiere flags `--add-opens`. Sondas universales: `URLDNS` (lookup DNS), `JRMPClient` (TCP connectback) — ambas se disparan antes de que se necesite cualquier cadena de gadgets específica.
- **`PHPGGC`** — equivalente PHP con cadenas para Laravel, Symfony, WordPress, Drupal, etc.

### Confusión de tipos (específico de PHP)

La comparación laxa `==` de PHP más tipos elegidos por el atacante en datos deserializados:

```
$login = unserialize($_COOKIE);
if ($login['password'] == $password) { /* log in */ }
```

El atacante serializa `password` como entero `0`. En PHP 7.x y anteriores, `0 == "Example string"` evalúa verdadero (la conversión string-a-número se detiene en el primer carácter no numérico). PHP 8+ cambió esto — verificar la versión del runtime antes de testear.

### Deserialización PHAR

Los archivos PHP Archive (`.phar`) contienen metadatos serializados. **Cualquier** operación del sistema de archivos en un stream `phar://` implícitamente deserializa esos metadatos, invocando `__wakeup`/`__destruct`. Ataque:

1. Construir un PHAR políglotico que también pase como JPG.
2. Subir vía funcionalidad de subida de archivo (que puede solo validar extensión o MIME).
3. Disparar cualquier código que ejecute `file_exists("phar://uploads/avatar.jpg")` o similar.
4. Los metadatos se deserializan, el método mágico de kick-off se dispara, la gadget chain se ejecuta.

El trigger no es la subida. El trigger es la próxima ruta de código que toca el archivo con un wrapper de stream `phar://`.

### Deserialización polimórfica en formatos modernos

Las librerías JSON/XML que deserializan *en objetos tipados* con pistas de nombre de clase reintroducen el mismo bug. El tipado polimórfico de Jackson (`@JsonTypeInfo`), `RuntimeTypeAdapterFactory` de Gson, y XStream son las reencarnaciones conocidas. El formato de datos parece seguro; la *librería de binding* no lo es.

## Impacto

Ordenado aproximadamente por severidad:

- **Ejecución remota de código** — el gadget sink alcanza `exec`/`eval`/equivalente. Techo por defecto para cualquier bug de deserialización con una gadget chain viable.
- **Bypass de autenticación / escalada de privilegios** — el atacante manipula sesiones/tokens de auth serializados (la ruta de confusión de tipos, o un simple flip de atributo en cookies sin firmar).
- **Lectura / escritura arbitraria de archivos** — el gadget sink alcanza APIs del sistema de archivos.
- **Server-Side Request Forgery** — el gadget sink alcanza primitivos HTTP/URL. `URLDNS` de ysoserial es una versión degenerada de esto.
- **Denegación de servicio** — grafos de objetos anidados estilo billion-laughs o constructores costosos.

Condiciones que escalan el impacto: el mismo proceso ejecutando sesiones de otros tenants, deserialización en un servicio privilegiado (worker de cola admin, procesador de trabajos en background), o una JVM/PHP-FPM hospedando otras apps en classpath compartido.

## Detección y defensa

Ordenado por efectividad:

1.
**No deserializar input no confiable.**
   Esta es la única defensa que aborda la causa raíz. Reemplazar la serialización nativa con formatos solo-datos (JSON sin tipado polimórfico, Protobuf, MessagePack) y reconstruir objetos de dominio con código explícito y type-checked. Toda otra defensa es una mitigación.

2.
**Si tenés que aceptar datos serializados, firmalos y verificalos *antes* de deserializar.**
   Aplicar HMAC a los bytes con una clave solo del servidor; rechazar el payload completamente si la firma no coincide, y nunca llamar a `unserialize`/`readObject` en bytes no verificados. La firma debe verificarse en los *bytes*, no en un objeto parseado-y-luego-validado — las verificaciones que se ejecutan después de la deserialización son demasiado tardías, porque el código peligroso ya se ejecutó.

3.
**Usar una allowlist de clases (`ObjectInputFilter` en Java, equivalente en .NET).**
   Restringir el deserializador a un conjunto pequeño de clases conocidas como seguras. Esto cierra la inyección de clases arbitrarias incluso si los bytes son manipulados. Mantener la lista deliberadamente — cada nueva clase añadida es una nueva decisión de superficie de ataque.

4.
**Reemplazar la serialización genérica con métodos específicos por clase.**
   Un `serialize`/`deserialize` hecho a mano para cada clase de dominio permite elegir qué campos cruzan el wire y validar tipos al reconstruir. Esto previene "el framework deserializó un campo privado que olvidaste que existía."

5.
**Eliminar gadget chains peligrosas conocidas del árbol de dependencias donde sea factible.**
   Útil como defensa en profundidad, pero **no como defensa primaria** — ver "qué no funciona" abajo. La higiene de dependencias reduce la librería de cadenas; no elimina la vulnerabilidad.

6.
**Monitorear fingerprints de deserialización en lugares inesperados.**
   Alertas para `rO0` / `ac ed` / `phar://` / opcodes de pickle apareciendo en tráfico HTTP entrante donde no deberían aparecer. Detecta bugs introducidos por una actualización descuidada de librería que de repente acepta payloads más ricos.

### Qué no funciona como defensa primaria

- **Validación post-deserialización.** El código peligroso se ejecuta *durante* la deserialización. Validar el objeto resultante es revisar la escena del crimen después del hecho.
- **Eliminar gadget chains conocidas.** Los árboles de dependencias modernos contienen cientos de clases. Se descubren nuevas cadenas cada año. El camino de menor falla es no deserializar input no confiable — no jugar al whack-a-mole con versiones de librerías.
- **Ofuscar el formato.** El binario no ayuda. `rO0` es tan reconocible como el texto plano PHP. Los atacantes identifican formatos por estructura, no por legibilidad.
- **Solo firmas WAF.** Los WAF detectan los payloads ysoserial codificados en base64 comunes; no detectan cadenas novedosas, payloads con codificación personalizada, o triggers PHAR que parecen subidas de imágenes.

## Ejemplos prácticos

- Una cookie "recordarme" almacenando un objeto PHP `User` serializado — el atacante cambia `isAdmin: false → true`, sin necesitar gadget chain.
- Un microservicio Java que recibe payloads RPC serializados sobre HTTP de llamantes "internos" — el atacante alcanza el servicio y ejecuta ysoserial CommonsCollections5 RCE.
- Una funcionalidad de subida de archivo más un generador de miniaturas que llama `file_exists("phar://uploads/$id")` — la deserialización PHAR convierte la subida de avatar en RCE.
- Una app .NET que usa `BinaryFormatter` para deserializar ViewState o sesión — RCE vía gadget chains conocidas, y Microsoft ha deprecado oficialmente `BinaryFormatter` exactamente por esto.
- Un servicio Spring Boot moderno que usa tipado polimórfico de Jackson en un endpoint público — el JSON parece seguro; el binder instancia cualquier clase que nombre el campo `@type`, reintroduciendo la clase de vulnerabilidad completa.
- Un flujo de auth que compara un campo de contraseña deserializado con `==` en PHP 7 — bypass por confusión de tipos sin necesitar nunca RCE.

## Notas relacionadas

- [[gadget-chains]] — la mitad de explotación: el modelo mental kick-off / intermediate / sink y los catálogos de cadenas por lenguaje.
- [[phar-deserialization]] — el mecanismo de trigger específico de PHP que se dispara desde operaciones del sistema de archivos en lugar de `unserialize`.
- [[file-upload-abuse]] — la deserialización PHAR es el tail de alto impacto de la combinación subida + llamada al sistema de archivos.
- [[auth-flaws]] — el bypass por confusión de tipos y las sesiones serializadas manipuladas son fallas de autenticación con raíz en deserialización insegura.
- [[cookies-and-sessions]] — canal de entrega primario para payloads serializados.

## Referencias

- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Insecure deserialization topic — https://portswigger.net/web-security/deserialization
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (PHAR deserialization) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
