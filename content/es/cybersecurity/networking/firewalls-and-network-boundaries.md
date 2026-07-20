---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - boundaries
  - firewalls
sources: []
---

# Firewalls y fronteras de red

## Definición
Los firewalls y las fronteras de red son controles que deciden qué tráfico puede cruzar entre redes, hosts, workloads y servicios. En entornos de nube y contenedores, la misma idea aparece como security groups, network ACLs, route tables, subredes privadas, políticas de ingress, políticas de egress, reglas de service mesh y NetworkPolicy de Kubernetes.

## Por qué importa
Un servicio puede estar bien escrito y aún así ser peligrosamente alcanzable. Las fronteras son donde la arquitectura prevista se vuelve imponible: público vs privado, frontend vs base de datos, workload vs metadata, usuario vs admin, tenant vs tenant.

La lección recurrente: **una frontera es real solo si los caminos bloqueados realmente fallan desde el punto de vista relevante**.

## Cómo funciona
La revisión de fronteras de red hace **5 preguntas**:

1. **¿Qué origen está permitido?** Internet pública, CDN, VPN, bastión, subred, service account, label de pod o security group.
2. **¿Qué destino está protegido?** Host, puerto, servicio, subred, namespace o recurso de nube.
3. **¿Qué dirección importa?** Inbound, outbound, east-west o tráfico de retorno.
4. **¿Qué capa lo impone?** Firewall, security group, NACL, load balancer, route table, service mesh o app proxy.
5. **¿Cómo se verifica?** Nmap, `nc`, logs, flow logs, captura de paquetes o inventario de nube.

Política prevista de ejemplo:

```txt
Internet -> CDN/WAF/load balancer : 443 permitido
CDN/WAF/load balancer -> app       : 443 permitido
Internet -> app origin             : bloqueado
app -> base de datos               : 5432 permitido
Internet -> base de datos          : bloqueado
app -> endpoint de metadata        : bloqueado salvo que se necesite
```

El bug es el camino permitido inesperado, no meramente la existencia de un firewall.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- alcanzabilidad pública vs privada para cada servicio
- acceso directo al origin esquivando los controles de CDN/WAF/load balancer
- rangos de origen demasiado amplios como `0.0.0.0/0` o `::/0`
- puertos de base de datos/caché/admin expuestos fuera de las subredes previstas
- movimiento east-west entre servicios internos
- egress a endpoints de metadata, rangos privados e internet
- supuestos de VPN/bastión
- paridad de política IPv6
- deriva de security group y route-table de la nube

## Variantes y bypasses
Las fallas de frontera caen en **6 clases prácticas**.

### 1. Sobreexposición de inbound público
Un servicio acepta tráfico de internet cuando solo debería aceptar tráfico de origen proxy, VPN, bastión o interno.

### 2. Bypass directo al origin
El CDN, WAF o load balancer está protegido, pero el origin del backend es alcanzable directamente por IP o hostname alternativo.

### 3. Planitud east-west
Los workloads internos pueden alcanzar libremente bases de datos, paneles de admin, endpoints de metadata y servicios pares tras un primer punto de apoyo.

### 4. Huecos de egress
Las reglas de outbound permiten que fetchers controlados por el usuario, workloads comprometidos o jobs de CI alcancen rangos privados, servicios de metadata o destinos arbitrarios de internet.

### 5. Desajuste de IPv6
Las fronteras de IPv4 son estrictas mientras IPv6 permite alcanzabilidad más amplia.

### 6. Deriva de política y reglas sombra
Reglas temporales de incidente, security groups viejos, cuentas de nube duplicadas o excepciones manuales quedan después de que la razón desaparece.

## Impacto
Ordenado aproximadamente por severidad:

- **Exposición pública de servicios sensibles.** Bases de datos, cachés, paneles de admin y backends se vuelven alcanzables por atacantes.
- **Bypass de control.** El acceso directo al origin saltea WAF, auth de CDN, política de TLS, rate limits o logging.
- **Movimiento lateral.** Un workload comprometido alcanza servicios internos porque la segmentación es plana.
- **Amplificación de SSRF.** Los fetchers del lado del servidor pueden alcanzar redes privadas o endpoints de metadata.
- **Exfiltración de datos.** El egress demasiado amplio deja que workloads comprometidos envíen datos a cualquier lado.
- **Falsa seguridad.** Los diagramas de arquitectura afirman fronteras privadas que las reglas en vivo no imponen.

## Detección y defensa
Ordenado por efectividad:

1. **Default-deny en los paths sensibles.**
   Bases de datos, cachés, servicios de admin, endpoints de metadata y backends deberían ser inalcanzables salvo que se requiera un origen y puerto específicos.

2. **Restringí los rangos de origen a upstreams reales.**
   Los backends detrás de un CDN/load balancer deberían aceptar tráfico solo de la identidad privada/security-group de ese upstream o de su rango de IP documentado, no de todo internet.

3. **Validá desde múltiples puntos de vista.**
   Los tests de internet pública, VPN, subred interna, contenedor y workload de nube deberían coincidir con el modelo de confianza previsto. Un camino público bloqueado no alcanza si un camino de SSRF puede llegarle.

4. **Segmentá el tráfico east-west deliberadamente.**
   Usá reglas de subred, security groups, NetworkPolicy de Kubernetes, política de service mesh o firewalls de host para limitar qué pueden iniciar los workloads internamente.

5. **Controlá el egress para workloads riesgosos.**
   Los fetchers de URL, renderers, runners de CI y apps de cara a internet no deberían alcanzar libremente metadata, loopback, link-local, rangos privados o destinos arbitrarios salvo que se necesite.

6. **Diffeá continuamente la política contra el inventario.**
   Las reglas de nube derivan. Alertá ante `0.0.0.0/0`, `::/0`, nuevas IPs públicas, nuevos puertos de listener y reglas sin dueños o expiración.

7. **Logueá las decisiones de frontera.**
   Los flow logs, logs de firewall, logs de load balancer y métricas de conexiones rechazadas convierten los supuestos invisibles de frontera en evidencia.

### Qué no funciona como defensa primaria

- **Nombres de red como controles.** `internal.example.com` no es una frontera.
- **Solo NAT.** NAT es traducción, no autorización.
- **WAF delante, origin expuesto detrás.** Los atacantes van a buscar la IP del origin.
- **Revisiones de firewall únicas.** Las excepciones temporales se vuelven permanentes.
- **Pensamiento solo-inbound.** SSRF, malware y abuso de CI a menudo dependen de la alcanzabilidad de outbound.
- **Política solo-IPv4.** IPv6 puede crear un camino público paralelo.

## Labs prácticos
Corré solo en entornos autorizados.

### Comparar la alcanzabilidad pública e interna

```bash
target=app.example.com
for port in 22 80 443 5432 6379 8080; do
  nc -vz -w 3 "$target" "$port"
done
```

Repetí desde internet pública, VPN, subred interna y un workload de nube.

### Escanear servicios públicos inesperados

```bash
nmap -Pn --top-ports 1000 your-host.example.com
nmap -Pn -p 22,80,443,5432,6379,9200,9300 your-host.example.com
```

Tratá los puertos abiertos inesperados como preguntas de propiedad.

### Chequear el bypass directo al origin

```bash
origin_ip=203.0.113.42
curl -skI "https://$origin_ip/" -H 'Host: app.example.com' --connect-timeout 5
```

Esperado: timeout, reset o denegación explícita salvo que el acceso directo al origin esté previsto.

### Testear el egress a metadata y rangos privados

```bash
curl -s --max-time 2 http://169.254.169.254/ || true
curl -s --max-time 2 http://10.0.0.1/ || true
```

Corré solo desde workloads que sean tuyos. Las apps de cara al público normalmente deberían bloquear estos caminos salvo que se necesite.

### Inspeccionar el estado local de firewall/listeners

```bash
lsof -i -P -n | rg 'LISTEN|UDP'
iptables -S 2>/dev/null || true
pfctl -sr 2>/dev/null || true
```

Los firewalls de host local y las direcciones de bind pueden diferir de las reglas de frontera de la nube.

### Revisar las reglas de nube por exposición amplia

```bash
# Ejemplo AWS: revisar los security groups por ingress público.
aws ec2 describe-security-groups \
  --query 'SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,Ingress:IpPermissions}' \
  --output json
```

Buscá rangos de origen públicos en puertos sensibles y reglas sin dueños.

## Ejemplos prácticos
- Un backend acepta tráfico de `0.0.0.0/0` aunque todo el tráfico previsto debería llegar a través del load balancer.
- Un security group de base de datos permite la IP de la oficina, pero una VPN de un contratista expande ese rango mucho más allá del equipo previsto.
- Un namespace de Kubernetes no tiene NetworkPolicy, así que cada pod puede alcanzar a cada otro pod.
- Un renderer de PDF propenso a SSRF puede alcanzar `169.254.169.254`.
- Los security groups de IPv6 permiten SSH globalmente mientras las reglas de IPv4 lo restringen.

## Notas relacionadas
- [[ports-and-services|Puertos y servicios]] — qué está escuchando y expuesto.
- [[nmap-scanning|Escaneo con Nmap]] — validar los puertos alcanzables.
- [[nat-and-private-networks|NAT y redes privadas]] — alcanzabilidad privada y supuestos de camino.
- [[metadata-endpoints|Endpoints de metadata]] — exposición de credenciales de nube link-local.
- [[load-balancers|Load balancers]] — puntos de entrada públicos y alcanzabilidad del backend.
- [[reverse-proxies|Reverse proxies]] — frontera de confianza de capa de aplicación.
- [[cybersecurity/web-security/ssrf|SSRF]] — abuso de alcanzabilidad del lado del servidor.
- [[cybersecurity/detection-engineering/network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]] — qué produce realmente el tráfico de frontera como evidencia.
- [[cybersecurity/detection-engineering/scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de escaneo y análisis de fingerprint]] — interpretación del lado del defensor del sondeo de fronteras.

### Notas atómicas futuras sugeridas
- [[network-segmentation|Segmentación de red]]
- [[egress-control|Control de egress]]
- [[direct-origin-bypass|Bypass directo al origin]]
- [[security-group-review|Revisión de security groups]]
- [[kubernetes-networkpolicy|NetworkPolicy de Kubernetes]]
- [[ipv6-firewall-parity|Paridad de firewall en IPv6]]

## Referencias
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Mitigation:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
