# Trace Metadata Endpoint Reachability

## Objetivo

Determinar si una aplicación, host, container o feature capaz de SSRF puede alcanzar cloud instance metadata endpoints, y convertir ese resultado en un paquete de evidencia seguro para hardening.

El playbook responde una pregunta: **¿puede este workload alcanzar metadata con identidad desde el lugar donde correría una request controlada por atacante o un proceso comprometido?**

## Supuestos

- El objetivo es un lab propio, un entorno explícitamente autorizado o una auditoría defensiva.
- El workload corre en cloud, container, VM, CI runner o infraestructura Kubernetes donde puede existir metadata o identidad adyacente a metadata.
- La alcanzabilidad de metadata es una pregunta de blast radius, no automáticamente un ejercicio de robo de credenciales.
- Las primitivas SSRF pueden revelar alcanzabilidad por status, timing, redirects, callbacks DNS o diferencias parciales de response.

## Prerrequisitos

- Scope escrito para el host, app, cuenta, cluster o lab.
- Una forma de correr comandos desde el vantage point relevante: host shell, container shell, pod shell, CI job o un harness SSRF propio.
- Permiso para testear direcciones link-local y comportamiento de metadata services cloud.
- Plan de evidencia seguro que evite imprimir, almacenar o exfiltrar credenciales cloud reales salvo que el engagement lo permita explícitamente.
- Contexto cloud/provider conocido cuando sea posible: AWS, GCP, Azure, DigitalOcean, Oracle, Alibaba, Kubernetes o lab local.

## Pasos de recon

1. Identificá el vantage point de ejecución: app server, container, pod, CI runner, serverless function, webhook worker, image fetcher, PDF renderer o URL previewer.
2. Identificá si el workload está alojado en cloud y qué provider controla el comportamiento de metadata.
3. Registrá contexto de red: IPs privadas, rutas, namespace de container, egress policy, service mesh y expectativas de security group o NetworkPolicy.
4. Identificá paths de request server-side controlados por usuario, incluyendo URL fetchers, redirects, parsing XML/SVG, OAuth/OIDC discovery, webhook delivery y sistemas de file preview.
5. Decidí nivel de prueba antes de testear: solo alcanzabilidad, metadata version check, existencia de path de identidad o llamada cloud API controlada read-only.

## Pasos de testing

### 1. Testear alcanzabilidad directa desde host

Desde el host o VM:

```
curl -sS --max-time 2 -o /dev/null -w 'aws-imds-root: %{http_code}\n' \
  http://169.254.169.254/

curl -sS --max-time 2 -o /dev/null -w 'aws-imds-path: %{http_code}\n' \
  http://169.254.169.254/latest/meta-data/
```

Interpretación:
- `200` en paths estilo AWS IMDSv1 significa que existe metadata reachability básica.
- `401`, `403` o `405` puede significar que IMDSv2 o requisitos de header del provider están funcionando.
- timeout o falla de conexión puede significar egress filtering, falta de metadata service, comportamiento de hop-limit o contexto no-cloud.

### 2. Testear hardening específico de provider

Usá checks seguros que no impriman credenciales:

```
# AWS IMDSv2 token availability
TOKEN=$(curl -sS --max-time 2 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)

if [ -n "$TOKEN" ]; then
  curl -sS --max-time 2 -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/iam/info
fi

# GCP metadata root, header required
curl -sS --max-time 2 -H 'Metadata-Flavor: Google' \
  http://metadata.google.internal/computeMetadata/v1/ -o /dev/null -w 'gcp: %{http_code}\n'

# Azure metadata root, header and api-version required
curl -sS --max-time 2 -H 'Metadata: true' \
  'http://169.254.169.254/metadata/instance?api-version=2021-02-01' \
  -o /dev/null -w 'azure: %{http_code}\n'
```

No fetchees paths de credenciales salvo que el scope lo permita explícitamente.

### 3. Testear alcanzabilidad desde container o pod

Corré desde la misma capa de aislamiento que usa la aplicación:

```
# Docker example
docker run --rm curlimages/curl:latest -sS --max-time 2 \
  -o /dev/null -w 'container-imds: %{http_code}\n' \
  http://169.254.169.254/latest/meta-data/

# Kubernetes example
kubectl exec -n <namespace> <pod> -- sh -c \
  "curl -sS --max-time 2 -o /dev/null -w 'pod-imds: %{http_code}\n' http://169.254.169.254/latest/meta-data/"
```

Compará alcanzabilidad de host contra container/pod. En AWS, un host puede alcanzar IMDS mientras un pod correctamente hop-limited no.

### 4. Testear alcanzabilidad mediada por SSRF de forma segura

Usá primero un endpoint inofensivo o callback target propio:

```
Feature:
User-controlled URL:
Outbound callback observed:
Redirects followed:
DNS rebinding possible:
Direct IP allowed:
Private/link-local blocked:
```

Después probá probes link-local solo si está autorizado:

```
http://169.254.169.254/
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/
http://[::ffff:169.254.169.254]/
http://2852039166/
```

Registrá diferencias en status, timing, largo de response, redirects y texto de error. Un SSRF blind todavía puede probar reachability por timeouts o callbacks out-of-band.

### 5. Verificar postura de cloud control

Usá APIs del provider donde estén disponibles:

```
# AWS: metadata token and hop-limit posture
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table

# Kubernetes: service-account token automount and host networking
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.hostNetwork == true) | "\(.metadata.namespace)/\(.metadata.name) hostNetwork=true"'
```

La evidencia de control-plane suele ser más limpia que una prueba riesgosa de credenciales en runtime.

## Señales de validación

- Un host, pod, container, CI runner o app feature recibe responses non-timeout de `169.254.169.254`.
- GET básico a metadata AWS funciona, sugiriendo IMDSv1 permitido.
- El flujo de token IMDSv2 funciona desde host y también desde container/pod cuando hop limit debería impedirlo.
- Una feature SSRF bloquea IPs privadas normales pero permite encodings equivalentes, redirects, formas IPv6-mapped o hostnames de provider.
- Metadata GCP o Azure con header requerido bloquea SSRF ingenuo, pero una primitiva SSRF más rica puede setear headers arbitrarios.
- La postura cloud API muestra `HttpTokens=optional`, hop limits altos, scopes amplios de service account, NetworkPolicy faltante o default service-account automount.

## Evidencia a capturar

Usá una tabla chica en vez de dumpear secretos:

```
Vantage point:
Provider:
Probe:
Result:
Credential path requested: no/yes
Credentials stored: no/yes
Control-plane setting:
Impact if reached:
Recommended fix:
Retest:
```

Si el acceso a credenciales está explícitamente en scope, guardá solo lo suficiente para probar identidad, como output de `aws sts get-caller-identity`, y redactá tokens inmediatamente.

## Mitigación

- Requerir modo metadata hardened: AWS IMDSv2 required y hop limit `1`; controles equivalentes de provider para GCP/Azure.
- Bloquear egress a rangos link-local y privados desde workloads public-facing salvo necesidad documentada.
- Implementar URL allowlists que resuelven hosts, deniegan rangos private/link-local y vuelven a chequear después de redirects.
- Restringir service accounts e instance roles a least privilege.
- Deshabilitar Kubernetes service-account token automount cuando el pod no necesita el API server.
- Agregar policies cloud/account para que workloads nuevos no puedan lanzarse con postura metadata débil.
- Retestear desde el vantage point exacto del workload después de cambios.

## Logging / detección

- Alertar sobre detecciones cloud relacionadas con metadata como DNS rebinding, uso STS inusual o llamadas API desde IPs, regiones o user agents inesperados.
- Loguear requests salientes de servicios URL-fetching y marcar destinos link-local/private.
- Monitorear cambios a AWS metadata options, Kubernetes `hostNetwork`, service-account automount y egress NetworkPolicy.
- Correlacionar probing SSRF contra uso posterior de cloud API por el mismo workload role.

## Stop conditions

Frená testing y escalá si:

- aparece material de credenciales inesperadamente en una response
- un workload de producción permite IMDSv1 o reachability de metadata desde pod
- un probe arriesga modificar recursos cloud o generar costo
- un SSRF blind empieza a tocar servicios internos sensibles fuera de scope
- la única prueba restante requeriría acciones destructivas, exfiltración amplia de credenciales o testing cross-account

## Notas relacionadas

- [[metadata-endpoints|Cloud Instance Metadata Endpoints]]
- [[nat-and-private-networks|NAT and Private Networks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[ssrf|SSRF]]
- [[cloud-metadata-security|Cloud Metadata Security]]
- [[cloud-iam-boundaries|Cloud IAM Boundaries]]
- [[investigate-ssrf|Investigar SSRF]]

## Comandos / payloads

### Set seguro de probes

```
http://169.254.169.254/
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/
http://[::ffff:169.254.169.254]/
http://2852039166/
http://0.0.0.0/
http://127.0.0.1/
```

### Comando mínimo de postura AWS

```
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table
```

### Checks de postura Kubernetes

```
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.automountServiceAccountToken != false) | "\(.metadata.namespace)/\(.metadata.name) token-auto-mounted"'

kubectl get networkpolicy --all-namespaces
```

## Gotchas

- Un timeout no siempre es seguro; puede indicar filtering de red, falla DNS, mismatch de provider o SSRF blind sin response visible.
- IMDSv2 requerido en host no prueba automáticamente que containers no puedan alcanzar metadata; hop limit y namespace de red importan.
- Metadata services con header requerido reducen riesgo SSRF básico pero no protegen contra primitivas SSRF que pueden setear headers arbitrarios.
- Las DNS allowlists deben chequearse después de cada redirect y deberían pinear IPs resueltas para prevenir rebinding.
- Nunca pegues credenciales metadata reales en notas, tickets o screenshots.

## Referencias

- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Investigación / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
