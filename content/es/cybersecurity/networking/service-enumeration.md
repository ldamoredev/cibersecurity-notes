---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - enumeration
  - services
sources: []
---

# Enumeración de servicios

## Definición
La enumeración de servicios es el proceso de tomar un puerto o endpoint alcanzable y aprender lo suficiente sobre el servicio que escucha como para entender el protocolo, la familia de software, las pistas de versión, la configuración, la frontera de confianza y el riesgo probable.

## Por qué importa
Un puerto abierto es solo un punto de partida. El valor de seguridad viene de convertir "algo responde en 443" en "esto es un edge de nginx, forwardeando a una app Express, exponiendo `/admin`, con una caché adelante". La enumeración es el puente entre la alcanzabilidad cruda y la comprensión accionable de la superficie de ataque.

Esta nota es dueña de la interpretación de protocolo y servicio. [[ports-and-services|Puertos y servicios]] es dueña de la superficie que escucha; [[nmap-scanning|Escaneo con Nmap]] es dueña de la estrategia de escaneo con Nmap; [[cybersecurity/attack-surface-mapping/exposed-service-triage|Triaje de servicios expuestos]] es dueña de priorizar el hallazgo.

## Cómo funciona
La enumeración de servicios responde **5 preguntas**:

1. **¿Qué protocolo se habla realmente?** Los números de puerto son pistas, no la verdad.
2. **¿Qué software o stack es visible?** Banners, headers, certificados TLS, páginas por defecto y comportamiento revelan pistas de implementación.
3. **¿Qué rol juega el servicio?** App pública, panel de admin, base de datos, proxy, endpoint de health, API de almacenamiento o dependencia interna.
4. **¿Qué frontera de confianza lo protege?** Internet, VPN, subred privada, localhost, service mesh o ninguna.
5. **¿Qué próximo test se justifica?** Sondeo HTTP, revisión de TLS, testeo de auth, chequeo de credenciales por defecto o retiro.

Ejemplo:

```bash
nmap -sV -p 443 app.example.com
curl -skI https://app.example.com/
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null
```

El resultado no es solo una lista de puertos; es un pequeño modelo de qué es el servicio y por qué importa.

## Técnicas / patrones
Atacantes y defensores enumeran a través de:

- detección de servicio de Nmap (`-sV`) y scripts NSE dirigidos
- banner grabs manuales con `nc`, `telnet`, `curl`, `openssl s_client`
- headers HTTP, status codes, redirects, títulos, páginas de error y rutas por defecto
- subject alternative names, issuer, ALPN y comportamiento de SNI del certificado TLS
- clientes específicos de protocolo para SSH, SMTP, Redis, PostgreSQL, SMB, DNS y APIs de Kubernetes
- comparar el comportamiento IP-directa vs hostname
- chequear páginas por defecto, endpoints de health, endpoints de métricas y paths de admin
- cruzar los servicios observados contra el inventario y los diagramas

## Variantes y bypasses
La enumeración de servicios tiene **6 lentes útiles**.

### 1. Servicios con banner visible
Algunos servicios revelan protocolo y versión de inmediato. SSH, SMTP, FTP y muchos servidores HTTP exponen banners obvios. Útil, pero los banners pueden mentir o ser quitados.

### 2. Servicios inferidos por comportamiento
Algunos servicios se revelan a través del timing de respuesta, mensajes de error, comportamiento de TLS, redirects o verbos aceptados en vez de banners explícitos.

### 3. Virtual hosts HTTP
La misma IP y puerto pueden hospedar muchas apps según el `Host` y el SNI. Enumerar solo la IP se pierde el ruteo de virtual-host y las superficies de admin ocultas.

### 4. Servicios detrás de TLS
Los certificados TLS, ALPN, SNI y el comportamiento de ciphers identifican edges, CDNs, load balancers y a veces nombres de servicios internos.

### 5. Servicios de infraestructura no-HTTP
Bases de datos, cachés, colas, protocolos de admin, SMB, RDP, SSH y APIs de Kubernetes a menudo tienen mucho más riesgo que los puertos web normales si están expuestos.

### 6. Servicios de sidecar y diagnóstico
Los puertos de métricas, health, debug, tracing y gestión a menudo se despliegan para operaciones y se olvidan en la revisión de exposición.

## Impacto
Ordenado aproximadamente por severidad:

- **Exposición de servicio de alto riesgo.** Bases de datos, cachés, paneles de admin, APIs de orquestación o servicios de acceso remoto alcanzables por clientes no previstos.
- **Targeting de exploit.** Las pistas de versión guían la investigación de CVE y los chequeos de configuración por defecto.
- **Bypass de frontera de confianza.** La exposición directa del backend o de servicios de diagnóstico puede bypassear controles de proxy, WAF, auth o rate-limit.
- **Fuga de información.** Banners, páginas de error, certificados y headers revelan el stack, el entorno o nombres internos.
- **Superficie mal priorizada.** Sin enumeración, los defensores pueden tratar un servicio crítico expuesto como un puerto desconocido de bajo riesgo.

## Detección y defensa
Ordenado por efectividad:

1. **Mantené un inventario de propiedad de servicios y exposición esperada.**
   Cada servicio expuesto debería tener un dueño, propósito, rangos de origen esperados, protocolo y camino de retiro. Los hallazgos de enumeración se vuelven accionables solo cuando se comparan con ese estado esperado.

2. **Bindeá los servicios a la interfaz y frontera más angostas.**
   Los servicios solo-locales deberían bindear `127.0.0.1` o interfaces privadas, no `0.0.0.0`. Los servicios internos deberían sentarse detrás de networking privado, no DNS público más esperanza.

3. **Reducí la fuga de banners y páginas por defecto sin confiar en la oscuridad.**
   Ocultá strings de versión innecesarios y páginas por defecto, pero no confundas cambios cosméticos con control de acceso o parcheo.

4. **Validá la alcanzabilidad directa al backend.**
   Si se supone que un servicio se alcanza solo a través de un proxy/load balancer, el acceso directo por IP/puerto debería fallar. Este es uno de los chequeos de enumeración de mayor valor.

5. **Usá validación específica de protocolo para los hallazgos importantes.**
   Si un escáner dice "Redis" o "PostgreSQL", validá con el cliente relevante o un handshake seguro. Las etiquetas de servicio son evidencia, no prueba final.

6. **Compará continuamente los escaneos con los cambios de deploy.**
   Aparecen servicios nuevos durante migraciones, incidentes y experimentos. La enumeración debería ser recurrente, no un proyecto único.

### Qué no funciona como defensa primaria

- **Cambiar el número de puerto.** Los puertos no estándar siguen siendo descubribles.
- **Suprimir solo los banners.** Los atacantes pueden inferir servicios desde el comportamiento, TLS, errores y handshakes de protocolo.
- **Asumir "interno" por el naming.** Las labels de DNS no imponen alcanzabilidad.
- **Confiar en el inventario sin observación.** Los diagramas derivan; la enumeración muestra el camino actual.
- **Tratar todos los puertos abiertos por igual.** El puerto 443 sirviendo un sitio de marketing y el puerto 443 sirviendo un dashboard de Kubernetes no son el mismo riesgo.

## Labs prácticos
Corré solo contra sistemas que sean tuyos o que estés autorizado a evaluar.

### Empezar desde los puertos descubiertos

```bash
nmap -Pn -sV -p 22,80,443,8080,8443 app.example.com
```

Registrá las etiquetas de servicio, versiones y confianza.

### Tomar la identidad HTTP manualmente

```bash
curl -skI https://app.example.com/
curl -skL https://app.example.com/ | sed -n '1,20p'
```

Buscá `Server`, redirects, headers de caché, páginas por defecto, errores del framework y rutas ocultas.

### Inspeccionar la identidad TLS

```bash
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```

Los certificados a menudo revelan servicios hermanos, entornos o propiedad del proveedor.

### Comparar el comportamiento IP vs hostname

```bash
ip=$(dig +short app.example.com A | head -n1)
curl -skI "https://$ip/" --connect-timeout 3
curl -skI "https://$ip/" -H 'Host: app.example.com' --connect-timeout 3
```

Las diferencias revelan ruteo de virtual-host y posible bypass del origin.

### Sondear paths de diagnóstico comunes

```bash
for path in /health /status /metrics /debug /admin /actuator/health; do
  printf '%s -> ' "$path"
  curl -sk -o /dev/null -w '%{http_code}\n' "https://app.example.com$path"
done
```

Respuestas inesperadas `200`, `401` o `500` verbosas merecen triaje.

### Validar un servicio no-HTTP de forma segura

```bash
nc -vz app.example.com 22
nmap -Pn -sV -p 22 app.example.com
```

Usá clientes específicos de protocolo solo dentro del alcance y sin adivinar credenciales salvo que estés explícitamente autorizado.

## Ejemplos prácticos
- `443/tcp` responde con un dashboard de Kubernetes por defecto en vez de la app pública esperada.
- `8443/tcp` expone un panel de admin que bypassea el reverse proxy principal.
- Un certificado en una IP pública lista los hostnames `staging`, `internal-api` y `grafana`.
- `-sV` sugiere Redis en un host público; la validación manual confirma que el servicio acepta conexiones sin autenticar.
- Un endpoint de health expone la versión de build, el estado de la base de datos y nombres de dependencias internas.

## Notas relacionadas
- [[ports-and-services|Puertos y servicios]] — superficie que escucha antes de la enumeración más profunda.
- [[nmap-scanning|Escaneo con Nmap]] — estrategia de escaneo y flujo de trabajo con Nmap.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — si el servicio debería ser alcanzable desde este camino.
- [[http-headers|Headers HTTP]] — pistas de identidad y comportamiento HTTP.
- [[tls-https|TLS/HTTPS]] — postura de certificado y TLS.
- [[cybersecurity/attack-surface-mapping/exposed-service-triage|Triaje de servicios expuestos]]
- [[cybersecurity/detection-engineering/zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[cybersecurity/detection-engineering/scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de escaneo y análisis de fingerprint]]

### Notas atómicas futuras sugeridas
- [[banner-grabbing|Banner grabbing]]
- [[http-service-fingerprinting|Fingerprinting de servicios HTTP]]
- [[tls-certificate-enumeration|Enumeración de certificados TLS]]
- [[default-admin-panels|Paneles de admin por defecto]]
- [[health-endpoint-exposure|Exposición de endpoints de health]]
- [[origin-ip-discovery|Descubrimiento de IP de origin]]

## Referencias
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
