---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-28
tags:
  - cybersecurity
  - networking
  - nat
  - private-networks
  - reachability
  - trust-boundary
sources: []
---

# NAT y redes privadas

## Definición
Las redes privadas usan rangos de direcciones IP que **no son ruteables en la Internet pública**, por diseño. NAT (Network Address Translation) permite que los hosts en esos rangos hablen con destinos públicos reescribiendo sus direcciones de origen a la salida, y reescribiendo las direcciones de destino a la vuelta. La combinación es el sustrato de casi todo despliegue moderno: redes hogareñas, LANs corporativas, VPCs de nube, redes de contenedores y redes de pods de Kubernetes usan todas direccionamiento privado más NAT.

El único error de seguridad que este tema entero existe para refutar: **"este rango de direcciones no es ruteable desde Internet, por lo tanto es seguro."** La alcanzabilidad es una propiedad del *camino* de red, no de la dirección. Un servicio de cara al público comprometido tiene el camino; un atacante vía SSRF tiene el camino; un vecino de contenedor mal configurado tiene el camino. El direccionamiento privado es una conveniencia de despliegue, no una frontera de seguridad.

## Por qué importa
La distinción "interno vs externo" es la frontera más sobreestimada en producción:

- **Amplificación del impacto de SSRF.** El server-side request forgery alcanza su mayor impacto cuando la propia VPC de la app contiene servicios solo-internos (bases de datos, APIs de admin, endpoints de metadata) que el atacante no puede alcanzar directamente. Ver [[cybersecurity/web-security/ssrf|SSRF]] y [[metadata-endpoints|Endpoints de metadata]].
- **Movimiento lateral.** Una subred privada plana convierte a un workload comprometido en una plataforma de lanzamiento hacia cada vecino. Los security groups de nube frecuentemente vienen por defecto con egress `0.0.0.0/0` e ingress `10.0.0.0/16` intra-subred.
- **Exposición de credenciales de nube.** Los endpoints de metadata de instancia de nube se sientan en el espacio de direcciones link-local (169.254.0.0/16). Cualquier proceso dentro de la VM que pueda emitir una request HTTP saliente puede leer credenciales IAM de vida corta. Ver [[metadata-endpoints|Endpoints de metadata]].
- **Atajos de confianza-por-IP.** Las allowlists "interno = confiable" colapsan en el momento en que un servicio de cara al público forwardea una request en nombre del atacante, o un workload en la red privada es comprometido.
- **El networking de contenedores y pods difumina la frontera.** Los pods de Kubernetes comparten namespaces de red node-local; un pod mal configurado con `hostNetwork: true` ve las interfaces del nodo directamente.

## Cómo funciona
Los operadores modernos se encuentran repetidamente con **6 bloques de direcciones reservados**. Reconocerlos a primera vista es el punto de entrada para cualquier discusión de alcanzabilidad.

| Rango | RFC | Propósito |
| --- | --- | --- |
| `10.0.0.0/8` | RFC 1918 | Privado (empresa grande / VPC de nube) |
| `172.16.0.0/12` | RFC 1918 | Privado (mediano, también el default de Docker) |
| `192.168.0.0/16` | RFC 1918 | Privado (hogar, oficina chica) |
| `127.0.0.0/8` | RFC 1122 | Loopback (`localhost`) |
| `169.254.0.0/16` | RFC 3927 | Link-local — y el hogar de los servicios de metadata de nube |
| `100.64.0.0/10` | RFC 6598 | NAT de grado carrier (CGNAT) |

Equivalentes en IPv6:
- `fc00::/7` — Unique Local Addresses (ULA), el RFC 1918 de IPv6.
- `fe80::/10` — link-local.
- `::1/128` — loopback.

NAT viene en **3 modos** que tienen propiedades de seguridad significativamente distintas.

1. **NAT 1:1 (NAT básico)** — una IP privada mapea a una IP pública. Común en despliegues de nube de "elastic IP" / "static NAT". El host privado todavía tiene una identidad pública estable; sus flujos de salida y entrada son simétricos.
2. **NAPT / PAT (Port Address Translation)** — el modo canónico de "muchos hosts privados detrás de una IP pública". El puerto de origen se reescribe para que el tráfico de retorno pueda demultiplexarse. Esto es lo que hacen los routers hogareños y la mayoría de los NAT gateways de nube. Los flujos de salida son stateful; los de entrada están bloqueados salvo que se configure port-forwarding explícito. **La propiedad de privacidad es incidental.** Una conexión iniciada desde adentro abre un agujero por el que cualquier cosa de afuera puede responder, hasta que el estado expira.
3. **CGNAT** — un segundo nivel de NAPT operado por el ISP, usado para el agotamiento de IPv4. Muchos suscriptores comparten una IP pública. Desde la perspectiva de un atacante, "bloqueá esta IP" afecta a muchos usuarios a la vez; desde la del defensor, "confiá en esta IP" confía en muchos usuarios a la vez.

Una request práctica mostrando la traducción en capas:

```
Container (172.17.0.5) → Host (192.168.1.20) → Router hogareño (203.0.113.42) → Internet
       NAPT dentro de Docker         NAPT dentro del router hogareño
```

Para cuando la request pega en la Internet pública, el origen original fue reescrito dos veces. Cada hop de NAT mantiene su propia tabla de estado; la pérdida de estado (reinicio del router, timeout por inactividad) tira el flujo.

El bug rara vez está en NAT mismo. El bug está en la cadena de supuestos de confianza: "esto vino de adentro de mi VPC así que es seguro" — sin verificar si *algo dentro de la VPC* podría estar emitiendo requests en nombre de un atacante.

## Técnicas / patrones
Qué miran atacantes y operadores:

- **Identificá el espacio de direcciones.** `ip addr`, `ipconfig`, `route -n`, consola de nube — ¿qué rangos privados ve el host, y qué rutea hacia dónde? La primera sonda en cualquier investigación de alcanzabilidad interna.
- **Testeá la alcanzabilidad de SSRF contra rangos privados.** Desde una app de cara al público comprometida, ¿puede emitir requests a `10.x`, `192.168.x`, `172.16.x`, `127.0.0.1`, `169.254.169.254`? Cada uno es un gate separado; muchas defensas de SSRF bloquean uno y se olvidan del resto. Ver [[cybersecurity/web-security/ssrf|SSRF]].
- **Sondeá el espacio link-local.** `169.254.169.254`, `fe80::`, direcciones VM-host específicas del vendor (`10.0.2.2` en NAT de VirtualBox, `host.docker.internal` en Docker Desktop). Cada uno es un candidato a "fuga de contenedor a host".
- **Buscá NAT hairpinning.** Un servicio en una subred privada se alcanza a sí mismo a través de su IP pública y es tratado como un cliente externo, a veces con ACLs más laxas que las que aplica el camino interno.
- **Reconocé los defaults de VPC de nube.** La VPC `default` de AWS tiene egress `0.0.0.0/0` y allow intra-VPC `10.0.0.0/16`. Muchos servicios "privados" son alcanzables desde cualquier instancia hermana.
- **Chequeá los namespaces de red de contenedores.** Los pods/contenedores en el mismo nodo se ven entre sí; en el mismo plugin de red ven a los vecinos; con `hostNetwork: true` ven todo el stack de red del nodo.

## Variantes y bypasses
"Interno significa seguro" falla de **4 formas específicas**. Cada una es su propia clase de ataque con su propio techo.

### 1. SSRF aplana la frontera
Una app de cara al público acepta URLs y las fetchea del lado del servidor. El fetcher está *dentro* de la red privada. La request del atacante ahora atraviesa caminos que el firewall se suponía que bloqueaba. El atacante nunca alcanza el servicio privado directamente — la app sí, en nombre del atacante. De mayor impacto cuando esto aterriza en endpoints de metadata (robo de credenciales de nube) o APIs de admin (a menudo sin autenticación porque "internas").

### 2. Movimiento lateral en subredes planas
Un workload comprometido está a un hop de cada vecino en la misma subred. Los security groups por defecto de AWS, los clústeres de Kubernetes sin network-policy y la mayoría de las redes hogareñas son planos. Las imágenes de nube por defecto corren sshd, API de kubelet, sockets de runtime de contenedor y listeners de base de datos sin expectativa de un atacante en el mismo /16.

### 3. Fugas de frontera de contenedor/pod
- `hostNetwork: true` en un pod expone todo el stack de red del nodo al pod, incluyendo la metadata link-local.
- El networking de bridge de Docker sin un `--internal` explícito deja que los contenedores ruteen al host y más allá.
- Plugins CNI mal configurados (Calico/Cilium/Flannel) filtran entre namespaces.
- El socket de runtime de contenedor (`/var/run/docker.sock`, containerd) bind-mounteado en un pod es "container escape con pasos extra".

### 4. NAT hairpinning y confianza-por-IP-de-origen
Cuando un servicio interno alcanza su propia IP pública, el NAT gateway loopea la conexión de vuelta por el camino público. El servicio que recibe ve la conexión llegando desde "afuera" pero con expectativas de confianza-interna. Combinado con allowlists públicas con clave en la IP de egress corporativa, esto deja que un atacante interno se haga pasar por el edge corporativo ante una API interna.

## Impacto
Ordenado aproximadamente por severidad:

- **Robo de credenciales de nube** — SSRF + alcanzabilidad de endpoint de metadata → credenciales IAM de la instancia → compromiso de la cuenta de nube. Dueña de la profundidad: [[metadata-endpoints|Endpoints de metadata]].
- **Exposición de API de admin / debug interna** — `/admin`, `/metrics`, `/debug`, `/actuator/*`, API de kubelet, etcd, Redis, Memcached, Elasticsearch sin autenticación. Supuesto "interno" sustituido por autenticación.
- **Acceso directo a base de datos** — Postgres/MySQL/MongoDB escuchando en una IP privada con credenciales débiles o por defecto, alcanzable desde cualquier workload en la misma subred.
- **Movimiento lateral** — un contenedor reventado se vuelve un punto de observación para cada otro workload. La escalada de privilegios suele seguir porque el próximo workload corre con IAM más amplio.
- **Fugas cross-tenant en clústeres multi-tenant** — networking plano + CNI compartido + nodo compartido = el compromiso de un tenant alcanza el pod de otro.
- **Bypass de confianza-por-IP** — una allowlist "solo permitimos la IP de egress corporativa" colapsa cuando un atacante interno alcanza el egress corporativo y después loopea de vuelta.

## Detección y defensa
Ordenado por efectividad:

1. **Tratá las redes privadas como no confiables por defecto (zero trust).**
   La distinción interno/externo es un hecho de despliegue, no una frontera de seguridad. Cada servicio autentica a cada llamante — mTLS, tokens firmados, claves de hardware. La alcanzabilidad de red es una capa de defensa en profundidad, no el control primario. Esta única postura derrota toda la familia de fallas "interno = seguro".

2. **Micro-segmentá la red privada.**
   Rompé la subred plana en muchas zonas chicas con reglas explícitas de ingress/egress entre ellas. Nube: security groups por servicio, AWS Network Firewall, reglas de firewall de GCP con target tags, NSGs de Azure. Kubernetes: recursos NetworkPolicy (deny-all por defecto, después allow explícito). El objetivo es "el compromiso de un workload alcanza a lo sumo un otro workload".

3. **Bloqueá el egress a rangos privados y link-local desde los servicios de cara al público.**
   El fetcher de tu servicio de thumbnails de imágenes no tiene nada que hacer conectándose a `10.0.0.0/8`, `127.0.0.1` o `169.254.169.254`. Imponelo en la capa de red (security groups de egress, network policies, política de application-mesh) en vez de confiar en que la app rechace. Esta es la defensa de cap-de-impacto-de-SSRF; combinala con la allowlist de URL a nivel de aplicación.

4. **Configurá el hardening del servicio de metadata de nube.**
   AWS IMDSv2 con `HttpPutResponseHopLimit: 1` (para que contenedores y pods no puedan alcanzarlo a través del host). GCP y Azure requieren headers explícitos (`Metadata-Flavor: Google`, `Metadata: true`) que un SSRF ingenuo no puede proveer. Ver [[metadata-endpoints|Endpoints de metadata]] para la versión larga.

5. **Deshabilitá la host-network de contenedores y los bind-mounts del socket de runtime.**
   `hostNetwork: true`, `hostPID: true`, `hostIPC: true` y los bind-mounts de `/var/run/docker.sock` son primitivas de escape. Bloqueá en admission controllers (PSA / Kyverno / OPA Gatekeeper).

6. **Auditá los defaults de security-group y NetworkPolicy.**
   El egress `0.0.0.0/0` es el default equivocado. El `allow all` intra-VPC es el default equivocado. Salí con `deny-all` y reglas allow explícitas; forzá a que cada servicio nuevo declare su egress.

7. **Vigilá el NAT hairpinning al diseñar allowlists de IP.**
   La confianza-por-IP-de-origen basada en la IP de egress corporativa debe tener en cuenta el caso donde un atacante interno alcanza el egress corporativo. Emparejá cada allowlist de IP con auth mutua para que la IP sea un factor de dos.

### Qué no funciona como defensa primaria

- **"Está en una subred privada".** Cualquier camino que tenga la aplicación, un atacante con una primitiva de request del lado del servidor también lo tiene. El rango de direcciones no es la frontera.
- **Bloquear solo `127.0.0.1`.** Los rangos privados RFC 1918, el link-local y el ULA de IPv6 también necesitan bloquearse. Cada uno es un gate separado que la defensa de SSRF debe cerrar.
- **Confiar en `Host:` o `X-Forwarded-Host:` para "¿esto es interno?".** El contenido del header es dato. La IP de origen de la conexión es la única evidencia de capa de red, e incluso esa es forjable si hay NAT hairpinning en juego.
- **Security groups por defecto de la nube.** La VPC default de AWS, la red default de GCP y el NSG default de Azure favorecen todos la conectividad sobre el aislamiento. Tratá los defaults como un punto de partida, no una postura terminada.
- **Kubernetes sin NetworkPolicy.** Un clúster sin políticas permite tráfico pod-a-pod en todas las direcciones. La instalación del CNI no es enforcement de política; tenés que escribir las reglas.

## Labs prácticos
`ip`, `nc`, `curl` estándar, más `dig` para investigaciones de DNS de nube.

### Identificar el paisaje de red local

```bash
# Linux: ¿qué direcciones ve este host, y cómo está ruteando?
ip addr
ip route
ip -6 route

# Variantes de macOS
ifconfig
netstat -rn

# Nube: ¿cuál es la vista que la instancia tiene de sí misma? (Ver la nota metadata-endpoints para sondas más seguras.)
hostname -I
```

### Sondear el alcance de SSRF en el espacio privado

```bash
# Desde un host de cara al público que controlás, simulá el alcance de un fetcher SSRF.
# Reemplazá 10.0.0.5 con el target privado real.
for target in 127.0.0.1 169.254.169.254 10.0.0.5 192.168.1.1 172.17.0.1; do
  printf '%-20s -> ' "$target"
  curl -s --max-time 3 -o /dev/null -w '%{http_code}\n' "http://$target/" || echo "fail"
done

# Testeá también el link-local de IPv6 — muchas allowlists de SSRF se lo olvidan
curl -s --max-time 3 -o /dev/null -w '%{http_code}\n' 'http://[fe80::1]/'
```

### Descubrir servicios internos en una subred

```bash
# Barré un /24 buscando hosts vivos y puertos de admin comunes — CORRÉ SOLO CONTRA RANGOS QUE SEAN TUYOS
for ip in 10.0.0.{1..254}; do
  (nc -zw1 "$ip" 22 2>/dev/null && echo "$ip ssh") &
  (nc -zw1 "$ip" 6443 2>/dev/null && echo "$ip kube-api") &
  (nc -zw1 "$ip" 2379 2>/dev/null && echo "$ip etcd") &
  (nc -zw1 "$ip" 6379 2>/dev/null && echo "$ip redis") &
done | sort -V
wait

# O usá nmap si está disponible
nmap -sT -Pn -p 22,80,443,2379,6379,6443,8080,9200 10.0.0.0/24
```

### Testear el alcance contenedor → host

```bash
# Dentro de un contenedor, ¿podés alcanzar el link-local / metadata del host?
curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' http://169.254.169.254/
curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' http://host.docker.internal/  # solo Docker Desktop

# Dentro de un pod de Kubernetes, ¿qué subred ves?
ip addr
nslookup kubernetes.default.svc.cluster.local
nslookup metadata.google.internal  # si corre en GKE
```

### Sondear el comportamiento de NAT hairpin

```bash
# Desde dentro de la red, pedí la IP/hostname público y mirá si loopea de vuelta.
# Útil al diseñar o auditar controles de allowlist-de-IP.
curl -sI https://example.com/internal-api -H 'X-Forwarded-For: 10.0.0.99'
# Si un endpoint con allowlist-de-IP-pública devuelve 200 desde un host privado haciendo hairpin
# de salida y vuelta por NAT, la allowlist sustituye a la auth peligrosamente.
```

### Auditar la exposición de la red de pods de Kubernetes

```bash
# Listar pods con hostNetwork o mounts del socket de runtime — ambos son primitivas de escape
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.hostNetwork == true) | "hostNetwork \(.metadata.namespace)/\(.metadata.name)"'

kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.volumes[]?.hostPath.path | tostring | test("docker.sock|containerd.sock|crio.sock")) | "runtime-socket \(.metadata.namespace)/\(.metadata.name)"'

# Chequear la cobertura de NetworkPolicy
kubectl get networkpolicy --all-namespaces
```

## Ejemplos prácticos
- Un servicio público de thumbnails de imágenes en Node.js acepta un parámetro `url` y le hace `fetch()`. El servicio corre en una instancia EC2 en una VPC. Un atacante envía `http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name` y recibe las credenciales IAM de la instancia EC2.
- Un clúster de Kubernetes no tiene NetworkPolicy. Un pod de cara al cliente comprometido se conecta a `10.x.x.x:6379` (Redis del clúster), lee tokens de sesión cacheados y se hace pasar por otros tenants.
- Un handler de webhook en Java acepta URLs y postea a ellas. La "allowlist de URL" bloquea `127.0.0.1` y `localhost` pero no `0.0.0.0`, `[::]` ni `169.254.169.254`. El SSRF alcanza la metadata.
- Una API corporativa pone en allowlist la IP de egress corporativa. Un empleado interno en la VPN corporativa hace hairpin por NAT y es tratado como un cliente externo confiable. Su sesión de navegador comprometida alcanza un path de admin solo-interno que a los clientes públicos se les niega.
- Un entorno de desarrollo de Docker Compose corre los contenedores `app` y `postgres` en la red bridge por defecto con el puerto 5432 publicado al host. El desarrollador está en Wi-Fi; un invitado en el mismo Wi-Fi alcanza `host-laptop.local:5432` y el supuesto de la app "estoy en una red privada" se hace pedazos.
- Un módulo HCL despliega una instancia RDS "privada" con `publicly_accessible = false`. El security group permite `10.0.0.0/16` (toda la VPC). Cada workload — incluyendo el pod de la app web de cara al público — tiene acceso directo a la base de datos sin pasar por la capa de aplicación.

## Notas relacionadas
- [[tcp-ip-basics|Fundamentos de TCP/IP]] — fundamentos de direccionamiento; rangos privados vs públicos.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — el enforcement de capa de red de la segmentación.
- [[metadata-endpoints|Endpoints de metadata]] — el gateway link-local de credenciales de nube. El target de SSRF de mayor impacto.
- [[cybersecurity/web-security/ssrf|SSRF]] — la primitiva de capa de aplicación que aplana la frontera público/privado.
- [[reverse-proxies|Reverse proxies]] — la capa de traducción-de-confianza que suele sentarse entre público y privado.
- [[client-ip-trust|Confianza en la IP del cliente]] — sutilezas de allowlist-de-IP, impacto del NAT hairpinning en la confianza de IP-de-origen.
- [[ports-and-services|Puertos y servicios]] — descubrir qué está escuchando en una subred privada.
- [[dns-resolution|Resolución DNS]] / [[dns-security|Seguridad de DNS]] — el DNS interno y el split-horizon son la capa de nombres de las redes privadas.
- [[cybersecurity/attack-surface-mapping/internal-attack-surface|Superficie de ataque interna]]
- [[cybersecurity/security-playbooks/trace-metadata-endpoint-reachability|Trazar la alcanzabilidad del endpoint de metadata]]

### Notas atómicas futuras sugeridas
- [[cloud-vpc-defaults|Defaults de VPC de nube]]
- [[kubernetes-networkpolicy|NetworkPolicy de Kubernetes]]
- [[container-escape-primitives|Primitivas de escape de contenedor]]
- [[ssrf-allowlist-design|Diseño de allowlist de SSRF]]
- [[ipv6-private-ranges|Rangos privados de IPv6]]
- [[nat-hairpinning|NAT hairpinning]]
- [[zero-trust-network-architecture|Arquitectura de red zero trust]]

## Referencias
- **Foundational:** RFC 1918 (Private Address Allocation) — https://datatracker.ietf.org/doc/html/rfc1918
- **Foundational:** RFC 6598 (CGNAT shared address space) — https://datatracker.ietf.org/doc/html/rfc6598
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
