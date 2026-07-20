---
type: concept
status: active
created: 2026-05-01
updated: 2026-05-01
tags:
  - cybersecurity
  - networking
  - express
  - forwarded-headers
  - trust-boundary
sources:
  - "https://expressjs.com/en/guide/behind-proxies.html"
  - "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For"
  - "https://www.rfc-editor.org/rfc/rfc7239"
---

# Confianza en headers en Node Express

## Definición
La confianza en headers en Node/Express es la decisión de si las APIs del framework como `req.ip`, `req.ips`, `req.hostname` y `req.protocol` deberían creerle a headers HTTP provistos por el proxy como `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto` o `Forwarded`.

## Por qué importa
Las aplicaciones Express a menudo se sientan detrás de Nginx, Cloudflare, un load balancer, un CDN o un router de plataforma. En esa forma, el peer TCP es el proxy, mientras que la identidad del cliente original se carga en headers. Si Express confía en esos headers desde el camino de red equivocado, un atacante puede spoofear identidad, bypassear rate limits, envenenar logs, influir en redirects o alcanzar comportamiento con IP-allowlist.

Este es el error común que expuso el ejercicio de aprendizaje Mirror: código de proxy viejo leía `cf-connecting-ip` y `x-forwarded-for` como si fueran hechos, sin probar que la request llegó a través del proxy confiable que debería haberlos escrito.

## Cómo funciona
Express tiene **3 capas de identidad**:

1. **Identidad de socket**
   `req.socket.remoteAddress` es el peer de red conectado al proceso Node. Detrás de un proxy, esta suele ser la IP del proxy, no la del usuario.

2. **Identidad de header forwarded**
   Headers como `X-Forwarded-For`, `X-Real-IP`, `CF-Connecting-IP` y el `Forwarded` de RFC 7239 afirman el cliente original o los hops anteriores. Estos son headers HTTP ordinarios hasta que una frontera de proxy confiable les da significado.

3. **Identidad decidida por el framework**
   `req.ip`, `req.ips`, `req.hostname` y `req.protocol` pueden cambiar según la configuración `trust proxy` de Express. Este valor es conveniente, pero es solo tan correcto como el modelo de confianza del proxy.

Patrón inseguro:

```js
function getClientIp(req) {
  return (
    req.headers["cf-connecting-ip"] ||
    req.headers["x-forwarded-for"] ||
    req.socket.remoteAddress ||
    req.ip
  );
}
```

Forma más segura:

```js
app.set("trust proxy", "loopback, linklocal, uniquelocal");

app.use((req, res, next) => {
  res.locals.clientIp = req.ip;
  res.locals.tcpPeer = req.socket.remoteAddress;
  res.locals.forwardedFor = req.get("x-forwarded-for") || null;
  next();
});
```

El bug no es “usar `X-Forwarded-For`.” El bug es creerle a un header antes de probar qué hop de red lo produjo o normalizó.

## Técnicas / patrones
- Encontrá cada uso de `req.ip`, `req.ips`, `req.hostname`, `req.protocol`, `req.headers["x-forwarded-for"]`, `req.headers["x-real-ip"]`, `CF-Connecting-IP`, `True-Client-IP` y `Forwarded`.
- Identificá la cadena de despliegue real: internet → CDN → load balancer → app proxy → Express.
- Chequeá `app.set("trust proxy", ...)` y si coincide con la cantidad real o el rango CIDR de hops de proxy confiables.
- Compará los headers crudos, `req.socket.remoteAddress` y los valores decididos por Express en un endpoint local `/whoami`.
- Buscá decisiones de seguridad basadas en la IP del cliente: allowlists de admin, geo-blocking, scoring de fraude, rate limiting, throttling de reset de contraseña y logs de auditoría.
- Tratá la alcanzabilidad directa al origin como un test separado: si el origin es alcanzable sin el proxy previsto, la confianza en headers forwarded normalmente colapsa.

## Variantes y bypasses
La confianza en headers en Express falla de **5 formas comunes**.

### 1. Confianza deshabilitada pero headers crudos leídos a mano
Express puede estar configurado de forma segura con `trust proxy` deshabilitado, pero el código de la aplicación bypassea el framework y lee `req.headers["x-forwarded-for"]` directamente. Esto recrea el bug bajo otro nombre.

### 2. `trust proxy: true` booleano
Un `true` booleano le dice a Express que confíe ampliamente en los headers de proxy. Si la app es alcanzable directamente, el valor de más a la izquierda de `X-Forwarded-For` puede volverse identidad controlada por el atacante.

### 3. Conteo de hops equivocado
`trust proxy: 1` es correcto solo cuando exactamente un proxy confiable se sienta delante de Express. Las cadenas multi-CDN, de service mesh, load balancer y router de plataforma necesitan modelado explícito. El número equivocado elige la IP equivocada.

### 4. Cerebro dividido de nombre de header
El proxy de edge sobrescribe `X-Forwarded-For`, pero la app lee `CF-Connecting-IP`, `True-Client-IP`, `X-Client-IP` o `Forwarded`. Los atacantes buscan el header hermano no saneado.

### 5. Estado interno escondido en headers
Un middleware setea headers de request falsos como `x-is-proxy-header` o `x-country-not-allowed-header`, y después un handler posterior lee esos nombres como estado interno. Funciona hasta que una ruta, proxy o middleware futuro deja que un header controlado por el cliente colisione con ese namespace.

## Impacto
Ordenado aproximadamente por severidad:

- **Bypass de allowlist de IP.** Los paths de admin o el comportamiento solo-interno se vuelven alcanzables spoofeando direcciones loopback, privadas o confiables.
- **Bypass de rate-limit.** Los límites de login, token y API con clave solo en `req.ip` pueden rotarse cambiando headers forwarded.
- **Envenenamiento de log de auditoría.** La respuesta a incidentes sigue una “IP de cliente” forjada en vez del peer TCP observado y el camino del proxy.
- **Bypass de geo-política o bloqueo falso.** Los chequeos de país se vuelven controlados por el atacante o poco confiables.
- **Distorsión del scoring de riesgo.** Los modelos de fraude, bot y abuso ingieren identidad de red spoofeada.
- **Confusión de redirect y host.** Los valores de `X-Forwarded-Proto` y host forwarded pueden afectar la generación de URLs y la lógica de callback cuando se confían demasiado ampliamente.

## Detección y defensa
Ordenado por efectividad:

1. **Modelá la cadena de proxy explícitamente**
   Escribí cada hop confiable y si sobrescribe o agrega headers de forwarding. La configuración de Express debería codificar ese modelo exacto, no un vago supuesto de “detrás de proxy”.

2. **Usá el `trust proxy` de Express de forma angosta**
   Preferí conteos exactos de hops o rangos CIDR para proxies conocidos. El `true` booleano es seguro solo cuando el acceso directo es imposible y el último proxy quita/sobrescribe de forma confiable los headers de forwarding entrantes.

3. **Dejá de leer headers de forwarding crudos para identidad**
   Centralizá la derivación de IP de cliente una sola vez, después de configurar la confianza de proxy de Express. Los headers crudos todavía pueden loguearse como afirmaciones, pero no deberían volverse identidad por sí solos.

4. **Bloqueá la alcanzabilidad directa al origin**
   Si la app solo debería recibir tráfico de un proxy o load balancer, imponelo con reglas de firewall/security-group y rechazo a nivel de aplicación de peers TCP inesperados.

5. **Logueá la identidad observada y la afirmada por separado**
   Guardá `tcp_peer`, `express_client_ip` y `forwarded_for_claim` como campos distintos. Esto preserva la verdad forense sin pretender que todos los valores tienen el mismo nivel de confianza.

6. **Mantené el estado interno fuera de los headers de request**
   Usá `res.locals`, símbolos locales de la request, metadata tipada o subclases de error explícitas. Las señales de control interno no deberían reusar nombres de header HTTP.

### Qué no funciona como defensa primaria
- **Chequear solo que `X-Forwarded-For` existe.** La existencia no prueba nada sobre quién lo seteó.
- **Confiar en headers estilo Cloudflare sin chequear los rangos de origen de Cloudflare.** Los nombres de header no autentican el camino de red.
- **Usar `req.ip` a ciegas.** `req.ip` es una decisión del framework afectada por `trust proxy`; no es automáticamente la verdad de red.
- **Confiar en una regla de WAF que quita un header.** Los atacantes pueden probar headers hermanos salvo que se normalice todo el namespace de forwarding.
- **Tratar las allowlists de IP como autenticación.** Los chequeos de IP son una capa, no un sustituto de la identidad de usuario, dispositivo o servicio.

## Labs prácticos

### Comparar la identidad cruda y la del framework

```js
app.get("/whoami", (req, res) => {
  res.json({
    socketRemoteAddress: req.socket.remoteAddress,
    expressIp: req.ip,
    expressIps: req.ips,
    xForwardedFor: req.get("x-forwarded-for") || null,
    forwarded: req.get("forwarded") || null,
    cfConnectingIp: req.get("cf-connecting-ip") || null
  });
});
```

El resultado muestra qué valores son hechos de red observados y cuáles son afirmaciones provistas por el cliente.

### Testear el spoofing directo de headers

```bash
curl -s http://localhost:3000/whoami \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "CF-Connecting-IP: 10.0.0.5" | jq
```

Si una decisión de seguridad cambia solo con esto, la app está confiando en headers desde el camino equivocado.

### Comparar modos de `trust proxy`

```js
// Correr la misma ruta /whoami con cada setting.
app.set("trust proxy", false);
app.set("trust proxy", 1);
app.set("trust proxy", "loopback, linklocal, uniquelocal");
```

La diferencia enseña por qué la confianza de proxy de Express es específica del despliegue.

### Buscar confianza en headers crudos en una base de código

```bash
rg -n "x-forwarded-for|x-real-ip|cf-connecting-ip|true-client-ip|forwarded|req\\.ip|trust proxy" src
```

Cada match es derivación de identidad, telemetría o un candidato a bug; clasificalo antes de cambiar comportamiento.

### Guardar las afirmaciones por separado

```text
request_id:
tcp_peer:
express_client_ip:
forwarded_for_claim:
trusted_proxy_config:
security_decision:
```

Esta tarjeta de evidencia evita que los logs aplasten afirmaciones y hechos en un único campo engañoso.

## Ejemplos prácticos
- Un limiter de login de Express usa `req.headers["x-forwarded-for"]` como clave para los intentos; los atacantes rotan ese header y bypassean el límite por-IP.
- Un dashboard chequea `req.ip === "127.0.0.1"` después de `trust proxy: true`; una request directa con `X-Forwarded-For: 127.0.0.1` alcanza comportamiento solo-admin.
- Un origin fronteado por Cloudflare filtra su IP directa; los atacantes se conectan directamente y envían `CF-Connecting-IP` a mano.
- Un middleware de geolocalización bloquea o redirige usuarios según una IP forwarded provista por el atacante.
- Un middleware setea `req.headers["x-blocked-user-agent-header"]` internamente; refactors posteriores hacen poco claro si ese flag es provisto por el cliente o propiedad del servidor.

## Notas relacionadas
- [[cybersecurity/networking/client-ip-trust|Confianza en la IP del cliente]]
- [[cybersecurity/networking/reverse-proxies|Reverse proxies]]
- [[cybersecurity/networking/http-headers|Headers HTTP]]
- [[cybersecurity/api-security/api-rate-limiting|Rate limiting de APIs]]
- [[cybersecurity/security-playbooks/test-client-ip-spoofing|Testear el spoofing de IP de cliente]]

### Notas atómicas futuras sugeridas
- [[trust-proxy-configuration|Configuración de trust proxy]]
- [[forwarded-header-spec|Spec del header Forwarded]]
- [[origin-ip-discovery|Descubrimiento de IP de origin]]
- [[express-security-middleware|Middleware de seguridad de Express]]

## Referencias
- **Official Tool Docs:** Express behind proxies — https://expressjs.com/en/guide/behind-proxies.html
- **Foundational:** MDN `X-Forwarded-For` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239: Forwarded HTTP Extension — https://www.rfc-editor.org/rfc/rfc7239
