---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - services
  - ports
sources: []
---

# Puertos y servicios

## Definición
Un puerto es un endpoint numerado en un host que usan protocolos de transporte como TCP o UDP. Un servicio es el proceso o aplicación que escucha en ese puerto y habla un protocolo con los clientes.

## Por qué importa
Los puertos son cómo la alcanzabilidad de red se convierte en superficie de ataque de aplicación. Un puerto abierto no es automáticamente una vulnerabilidad, pero todo servicio que escucha necesita una razón para existir, una frontera, un dueño y una historia de parcheo.

Esta nota es dueña de la superficie expuesta que escucha. [[service-enumeration|Enumeración de servicios]] empieza cuando querés identificar qué es realmente el servicio.

## Cómo funciona
Los puertos y servicios se entienden mejor a través de **4 capas**:

1. **Dirección.** Qué host/interfaz recibe el tráfico.
2. **Transporte.** TCP o UDP lleva el tráfico a un puerto numerado.
3. **Listener.** Un proceso se bindea a esa dirección y puerto.
4. **Protocolo/aplicación.** El servicio habla SSH, HTTP, TLS, Postgres, Redis, DNS u otro protocolo.

Ejemplo:

```txt
0.0.0.0:5432/tcp -> postgres process -> PostgreSQL protocol
127.0.0.1:3000/tcp -> node process -> HTTP dev server
203.0.113.10:443/tcp -> nginx -> TLS/HTTP reverse proxy
```

El mismo número de puerto puede significar riesgo distinto según dónde esté bindeado y quién pueda alcanzarlo.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- sockets locales que escuchan con `lsof`, `ss` o `netstat`
- puertos abiertos remotos con Nmap o `nc` dirigido
- exposición TCP vs UDP
- dirección de bind: loopback, privada, pública, todas las interfaces, IPv6
- inventario de servicios esperado vs inesperado
- puertos de admin/dev de número alto
- puertos de base de datos/caché/cola alcanzables fuera de las redes previstas
- puertos de backend directos que saltean reverse proxies o load balancers

## Variantes y bypasses
La superficie que escucha cae en **6 clases de servicio**.

### 1. Puntos de entrada web públicos
Los puertos 80 y 443 normalmente exponen HTTP/HTTPS a través de un reverse proxy, CDN o load balancer. Esperado, pero igual necesita revisión de TLS, headers, ruteo y seguridad de la app.

### 2. Administración remota
SSH, RDP, VPN, consolas de gestión y bastiones son de alto valor porque controlan sistemas en vez de features de la app.

### 3. Almacenes de datos y colas
PostgreSQL, MySQL, Redis, Elasticsearch, RabbitMQ, Kafka y servicios similares casi nunca deberían ser alcanzables directamente desde internet.

### 4. Servicios de desarrollo y debug
Servidores de desarrollo de frameworks, puertos de debug, hot reloaders, notebooks y endpoints de profiling suelen aparecer durante incidentes o experimentos y después quedan dando vueltas.

### 5. Salud, métricas y diagnósticos
Prometheus, actuator, `/metrics`, `/health`, tracing y APIs de admin pueden revelar estado interno o proveer acciones del plano de control.

### 6. Servicios UDP
DNS, NTP, SNMP, VPN y protocolos de descubrimiento se comportan distinto que TCP y suelen estar sub-escaneados.

## Impacto
Ordenado aproximadamente por severidad:

- **Camino de compromiso directo.** Servicios de admin o datos expuestos pueden permitir bypass de auth, ataques de credenciales débiles o explotación de servicios conocidos.
- **Bypass de proxy/control.** Los puertos de backend directos saltean WAF, gateway de auth, rate limits o logging.
- **Exposición de datos.** Bases de datos, cachés y servicios de búsqueda pueden exponer datos sensibles.
- **Reconocimiento interno.** Los banners y combinaciones de puertos revelan el stack y la arquitectura.
- **Movimiento lateral.** Servicios internos alcanzables tras un primer punto de apoyo amplían el radio de explosión.
- **Deriva operativa.** Listeners desconocidos indican un desajuste de deploy/inventario.

## Detección y defensa
Ordenado por efectividad:

1. **Mantené un inventario de servicios esperados.**
   Para cada host o workload, definí qué puertos deberían escuchar, en qué interfaces y desde qué rangos de origen. La detección solo funciona contra un estado esperado.

2. **Bindeá los servicios de forma angosta.**
   Los servicios solo-locales deberían bindear loopback. Los internos deberían bindear interfaces privadas. La exposición pública debería ser intencional y documentada.

3. **Imponé fronteras de red alrededor de servicios no públicos.**
   Bases de datos, cachés, colas, paneles de admin y métricas deberían estar bloqueados desde caminos públicos sin importar la autenticación a nivel de app.

4. **Escaneá desde puntos de vista relevantes.**
   Las vistas pública, VPN, subred interna, contenedor y workload de nube producen conjuntos de puertos alcanzables distintos.

5. **Eliminá o protegé las superficies de diagnóstico.**
   Los endpoints de salud y métricas deberían revelar la mínima información y estar controlados por acceso donde exponen internals.

6. **Revisá IPv6 y UDP explícitamente.**
   Muchas revisiones de exposición cubren accidentalmente solo TCP/IPv4.

### Qué no funciona como defensa primaria

- **Usar puertos no estándar.** Los escáneres encuentran puertos altos.
- **Asumir que localhost en desarrollo equivale a localhost en producción.** Las configuraciones de bind suelen cambiar con los defaults de contenedor o framework.
- **Confiar en "seguridad por oscuridad" para puertos de admin.** Los paths ocultos y puertos inusuales son un problema de descubrimiento, no defensas.
- **Ignorar la semántica closed vs filtered.** Significan cosas distintas para validar fronteras.
- **Dejar que cada servicio bindee `0.0.0.0`.** La conveniencia se vuelve exposición.

## Labs prácticos
Corré solo contra sistemas propios o autorizados.

### Listar servicios locales que escuchan

```bash
lsof -i -P -n | rg 'LISTEN|UDP'
ss -lntup 2>/dev/null || true
```

Buscá procesos inesperados y direcciones de bind.

### Escanear puertos remotos comunes

```bash
nmap -Pn --top-ports 1000 your-host.example.com
```

Esto da una foto rápida de la superficie externa que escucha.

### Escanear todos los puertos TCP

```bash
nmap -Pn -p- --min-rate 1000 your-host.example.com
```

Usalo al buscar servicios de admin/dev en puertos altos.

### Probar un servicio manualmente

```bash
nc -vz your-host.example.com 443
curl -skI https://your-host.example.com/
```

Las pruebas manuales ayudan a validar la salida del escáner.

### Comparar bind en localhost vs público

```bash
curl -sI http://127.0.0.1:3000
hostname -I 2>/dev/null || ipconfig getifaddr en0
```

Después probá desde otro host si está autorizado. El éxito local no implica alcanzabilidad remota.

### Chequear UDP intencionalmente

```bash
nmap -Pn -sU -p 53,123,161 your-host.example.com
```

Mantené los escaneos UDP dirigidos e interpretá el silencio con cuidado.

## Ejemplos prácticos
- Redis en `6379/tcp` queda expuesto públicamente porque un contenedor publicó todos los puertos.
- Una app de backend en `8080/tcp` es alcanzable directamente, salteando el reverse proxy HTTPS.
- SSH se supone que es solo-bastión pero aparece abierto desde internet pública.
- Un servicio de métricas en `9100/tcp` expone hostnames, nombres de proceso y labels internos.
- IPv6 expone `22/tcp` mientras IPv4 lo bloquea.

## Notas relacionadas
- [[tcp-ip-basics|Fundamentos de TCP/IP]] — base de direccionamiento, ruteo y transporte.
- [[service-enumeration|Enumeración de servicios]] — identificar qué escucha en un puerto abierto.
- [[nmap-scanning|Escaneo con Nmap]] — estrategia de escaneo.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — caminos permitidos y bloqueados.
- [[cybersecurity/attack-surface-mapping/exposed-service-triage|Triaje de servicios expuestos]]
- [[load-balancers|Load balancers]] — ruteo de los puntos de entrada públicos.

### Notas atómicas futuras sugeridas
- [[common-service-ports|Puertos de servicios comunes]]
- [[bind-addresses|Direcciones de bind]]
- [[localhost-vs-public-bind|Bind localhost vs público]]
- [[udp-service-exposure|Exposición de servicios UDP]]
- [[admin-port-exposure|Exposición de puertos de admin]]
- [[metrics-endpoint-exposure|Exposición de endpoints de métricas]]

## Referencias
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
