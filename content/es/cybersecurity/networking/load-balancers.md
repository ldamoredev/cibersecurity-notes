---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - load-balancing
  - edge
sources: []
---

# Load balancers

## Definición
Un load balancer es un punto de entrada que distribuye el tráfico entre servicios de backend y a menudo realiza terminación de TLS, health checks, ruteo por host/path, reuso de conexión e inyección de headers.

## Por qué importa
Los load balancers son componentes operativos que se vuelven fronteras de seguridad. Deciden qué backend recibe una request, qué headers se agregan, si TLS termina en el edge, si los endpoints de health son alcanzables y si debería existir acceso directo al backend.

Esta nota es dueña del ruteo del punto de entrada y la alcanzabilidad del backend. [[reverse-proxies|Reverse proxies]] es dueña de la normalización HTTP más profunda y el comportamiento de desacuerdo-de-parser.

## Cómo funciona
Un load balancer aplica **5 funciones relevantes para la seguridad**:

1. **Aceptar tráfico.** Escucha en IPs/puertos públicos o privados.
2. **Terminar o pasar TLS.** Puede descifrar en el edge o forwardear tráfico cifrado.
3. **Elegir un backend.** Rutea por host, path, puerto, protocolo, peso, salud o target group.
4. **Reescribir o agregar metadata.** Agrega `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Port`, `Forwarded` o headers específicos del proveedor.
5. **Realizar health checks.** Sondea paths o puertos del backend y remueve los targets no saludables.

Camino de ejemplo:

```txt
cliente -> CDN/WAF -> load balancer público :443
load balancer -> target group de la app      :8080
load balancer -> /health cada 30s
```

La pregunta de seguridad es si el backend solo confía en el tráfico y la metadata que realmente vinieron por este camino.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- listeners públicos y puertos expuestos
- reglas de ruteo por host/path
- terminación de TLS y cifrado del backend
- alcanzabilidad directa de IP/puerto del backend
- paths de health-check y fuga de diagnósticos
- headers forwarded y propagación de la IP del cliente
- target groups, pools de backend y targets obsoletos
- backends por defecto y rutas catch-all
- sticky sessions y afinidad de ruteo
- desajuste entre los logs del load balancer y los de la app

## Variantes y bypasses
Los problemas de load balancer caen en **6 clases**.

### 1. Bypass directo al backend
El backend es alcanzable directamente por IP, DNS alternativo o regla de security-group pública. Esto bypassea el TLS de edge, el WAF, los gateways de auth, los rate limits y las reglas de sobrescritura de headers.

### 2. Huecos de terminación de TLS
TLS termina en el load balancer, pero el tráfico al backend es texto plano o no autenticado. Esto puede ser aceptable en una red confiable, pero peligroso a través de caminos compartidos o débilmente segmentados.

### 3. Confusión de confianza de headers
El load balancer agrega headers de forwarding, pero el backend también acepta las versiones provistas por el cliente. Esto crea bugs de IP-de-cliente, esquema, host y generación de URLs.

### 4. Errores de reglas de ruteo
Las reglas de host/path/default mandan tráfico al target group equivocado, exponen paths de admin o dejan que valores `Host` hostiles alcancen backends inesperados.

### 5. Exposición de health-check
Los endpoints de health revelan internals, bypassean auth o quedan alcanzables públicamente porque fueron diseñados para el load balancer y después expuestos a todos.

### 6. Target groups obsoletos o mezclados
Versiones viejas, instancias de debug o targets del entorno equivocado quedan registrados detrás del mismo load balancer.

## Impacto
Ordenado aproximadamente por severidad:

- **Bypass de controles de edge.** El acceso directo al backend saltea WAF, CDN, auth, logging o política de TLS.
- **Exposición de credenciales/sesión.** Los hops de backend en texto plano pueden exponer headers sensibles si la red interna no es confiable.
- **Bugs de ruteo de privilegio o tenant.** Los errores de host/path rutean usuarios a apps o superficies de admin equivocadas.
- **Abuso de confianza en IP-de-cliente.** El mal manejo de headers de forwarding rompe rate limits, allowlists, logs y controles de acceso.
- **Fuga de información.** Los health checks y backends por defecto exponen internals.
- **Riesgo de disponibilidad.** Health checks malos o deriva de targets rutean tráfico a servicios no saludables o no previstos.

## Detección y defensa
Ordenado por efectividad:

1. **Bloqueá la alcanzabilidad directa al backend.**
   Los backends deberían aceptar tráfico de inbound solo del load balancer o de una identidad upstream confiable. Este es el control que vuelve al load balancer una frontera real.

2. **Definí la política de TLS para los hops del cliente y del backend.**
   Usá TLS moderno en el edge y decidí explícitamente si se requiere TLS o mTLS al backend. El tráfico sensible a través de redes compartidas debería estar cifrado y autenticado end-to-end.

3. **Sobrescribí los headers de forwarding en el load balancer y confiá en ellos solo desde ese camino.**
   El edge debería setear los headers de origen/proto/host de forma consistente; el backend debería ignorar esos headers desde cualquier otro origen.

4. **Auditá las reglas de ruteo y los targets por defecto.**
   Cada regla de host/path debería tener un dueño y un target group esperado. Las rutas catch-all por defecto deberían fallar cerrado o servir contenido inofensivo.

5. **Protegé los endpoints de health y diagnóstico.**
   Los endpoints de health deberían revelar el mínimo estado y ser alcanzables solo donde se necesita. Los usuarios públicos no deberían recibir diagnósticos del backend.

6. **Podá continuamente los target groups.**
   Remové instancias obsoletas, deploys viejos, hosts de debug y targets del entorno equivocado. Los pools del load balancer son superficies de inventario.

7. **Correlacioná los logs del load balancer y del backend.**
   Los request IDs, IP de origen, target ID, host, path y status codes deberían dejarte probar qué backend sirvió una request.

### Qué no funciona como defensa primaria

- **Asumir que el load balancer protege los backends mientras los backends son públicos.** Los atacantes pueden bypassear la puerta de entrada.
- **Confiar en `X-Forwarded-*` porque el load balancer lo setea.** Los clientes también pueden setear esos headers salvo que el edge sobrescriba y el backend restrinja la confianza por camino de red.
- **HTTPS solo-en-el-edge como garantía general.** El texto plano del backend todavía puede importar.
- **Oscuridad del endpoint de health.** `/healthz` y `/actuator/health` son fáciles de encontrar.
- **Un backend por defecto para todo.** Las rutas catch-all a menudo filtran apps equivocadas o paneles de admin.

## Labs prácticos
Corré solo contra infraestructura que sea tuya o que estés autorizado a testear.

### Fingerprintear el punto de entrada

```bash
curl -skI https://app.example.com/ | rg -i 'server|via|x-cache|x-amz|cf-ray|x-forwarded|strict-transport-security'
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null | rg -i 'issuer=|subject=|ALPN|Protocol|Cipher'
```

Identificá pistas de CDN/LB, postura de TLS y headers de política.

### Comparar el ruteo por host/path

```bash
curl -skI https://app.example.com/
curl -skI https://app.example.com/health
curl -skI https://app.example.com/admin
curl -skI https://app.example.com/ -H 'Host: unexpected.example.com'
```

Éxitos o redirects inesperados pueden indicar problemas de ruteo/backend-por-defecto.

### Sondear el manejo de headers forwarded

```bash
curl -skI https://app.example.com/ \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Forwarded-Proto: http' \
  -H 'X-Forwarded-Host: evil.example'
```

Buscá status cambiado, redirects, URLs generadas o efectos en logs.

### Testear la alcanzabilidad directa al backend

```bash
origin_ip=203.0.113.42
curl -skI "https://$origin_ip/" -H 'Host: app.example.com' --connect-timeout 5
curl -sI  "http://$origin_ip:8080/" -H 'Host: app.example.com' --connect-timeout 5
```

Esperado: bloqueado salvo que el acceso directo al origin esté permitido intencionalmente.

### Inspeccionar la exposición de health-check

```bash
for path in /health /healthz /status /metrics /actuator/health; do
  printf '%s -> ' "$path"
  curl -sk -o /dev/null -w '%{http_code}\n' "https://app.example.com$path"
done
```

Seguí cualquier diagnóstico verboso o público.

### Comparar los logs del load balancer y del backend

```text
1. Enviá una request con X-Request-ID: lb-lab-001.
2. Encontrala en los logs del load balancer.
3. Encontrala en los logs del backend.
4. Compará IP de origen, host, path, esquema, target y status.
```

Esto prueba cómo la metadata cruza la frontera.

## Ejemplos prácticos
- El load balancer público impone HTTPS, pero el backend es alcanzable directamente por HTTP en `8080`.
- Una regla de host por defecto rutea headers `Host` desconocidos a una app de admin.
- La app confía en `X-Forwarded-Proto: https`, permitiendo que un atacante haga que los links generados o las decisiones de seguridad mientan.
- `/actuator/health` está pensado para el load balancer pero expone el estado de la base de datos y las dependencias públicamente.
- Un target group obsoleto todavía incluye un build de debug con errores verbosos.

## Notas relacionadas
- [[reverse-proxies|Reverse proxies]] — normalización HTTP más profunda y desacuerdo de parser.
- [[client-ip-trust|Confianza en la IP del cliente]] — semántica de la IP de cliente forwarded.
- [[tls-https|TLS/HTTPS]] — postura de TLS en edge y backend.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — bloquear la alcanzabilidad directa al backend.
- [[http-headers|Headers HTTP]] — headers de forwarding y política.
- [[service-enumeration|Enumeración de servicios]] — identificar el comportamiento del load balancer y el backend.

### Notas atómicas futuras sugeridas
- [[direct-origin-bypass|Bypass directo al origin]]
- [[load-balancer-health-checks|Health checks de load balancer]]
- [[target-group-drift|Deriva de target groups]]
- [[edge-vs-origin-tls|TLS en edge vs origin]]
- [[host-based-routing|Ruteo basado en host]]
- [[sticky-sessions|Sticky sessions]]

## Referencias
- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
