---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-28
tags:
  - cybersecurity
  - networking
  - cloud
  - ssrf
  - credentials
  - metadata
sources: []
---

# Endpoints de metadata de instancias de nube

## Definición
Los endpoints de metadata de instancia de nube son servicios HTTP hospedados por el proveedor de nube en una **dirección link-local** (típicamente `169.254.169.254`) que cualquier proceso corriendo dentro de la máquina virtual puede consultar sin autenticación. Exponen información sobre la instancia — región, identidad, user-data — y, críticamente, **credenciales IAM de vida corta para el rol adjunto a la instancia**. La misma primitiva existe en cada nube mayor, con diferencias sutiles de protocolo que importan para el tooling del atacante y para los defensores que escriben allowlists de SSRF.

La única oración que explica por qué existe este tema entero: **el endpoint de metadata ata los permisos IAM de la nube a la propiedad de capa de red "cualquier proceso dentro de esta VM"**, que el modelo de seguridad de la aplicación normalmente no.

## Por qué importa
Los servicios de metadata de instancia son el target de SSRF de mayor impacto en la Internet pública, por amplio margen. Una vulnerabilidad en cualquier aplicación que emite requests HTTP salientes en respuesta a input del atacante — fetchers de imágenes, handlers de webhook, previews de URL, lectores de RSS, flujos OpenID/OAuth, fetchers de JWKS, embebedores de iframe del lado del servidor — se vuelve un camino directo a las credenciales IAM de la instancia. Esas credenciales normalmente permiten las operaciones de nube normales de la aplicación: leer buckets de S3, escribir a colas, llamar APIs internas, a veces asumir otros roles.

Esto importa por cuatro razones específicas:

- **El endpoint es alcanzable desde cualquier cosa en la VM.** Contenedores, pods, sidecars y la aplicación misma comparten todos el mismo namespace de red por defecto salvo que el operador hiciera algo deliberado para bloquear esto.
- **Las credenciales son reales.** Son credenciales STS / token-broker con los mismos permisos que usa la aplicación. No son creds de prueba, no están scopeadas, no están gateadas por auth adicional.
- **Las defensas que "se ven bien" a menudo se lo pierden.** Las allowlists de SSRF que bloquean `127.0.0.1` y `localhost` y se olvidan de `169.254.169.254` son extremadamente comunes. También lo son los parsers de URL que permiten `0.0.0.0`, direcciones IPv6 mapeadas o trucos de DNS-rebinding.
- **La detección es rara.** Los fetches de metadata se ven como HTTP saliente ordinario desde dentro de la VM. CloudTrail / los audit logs de GCP ven el *uso* de las credenciales, no el *robo* de ellas.

## Cómo funciona
El servicio de metadata es solo un servidor HTTP en una dirección link-local que devuelve texto o JSON cuando se lo consulta. **4 propiedades** lo hacen peligroso:

1. **Alcanzabilidad link-local.** `169.254.169.254` está en `169.254.0.0/16` (RFC 3927) — no ruteable en la Internet pública, pero alcanzable desde cualquier proceso que pueda emitir una request TCP/HTTP desde dentro de la VM.
2. **Sin autenticación por defecto** (o una "auth" trivialmente débil de solo-header — ver Variantes).
3. **Devuelve credenciales de vida corta** para el rol IAM adjunto a la instancia. La validez del token suele ser de 1–12 horas; refrescar requiere solo re-preguntarle al endpoint.
4. **Bypassea el modelo de seguridad de la aplicación por completo.** El authn/authz de la app, sus rate limits, su allowlist — todos estos son controles de *capa de aplicación*. El endpoint de metadata es una primitiva de *capa de red* que se sienta debajo de todos ellos.

La request de ataque canónica, AWS IMDSv1:

```http
GET /latest/meta-data/iam/security-credentials/ HTTP/1.1
Host: 169.254.169.254
```

Respuesta: una lista de nombres de rol. Después:

```http
GET /latest/meta-data/iam/security-credentials/<role-name> HTTP/1.1
Host: 169.254.169.254
```

Respuesta, JSON, incluyendo:

```json
{
  "Code": "Success",
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "FwoG...",
  "Expiration": "2026-04-28T11:59:00Z"
}
```

Estos tres valores son inmediatamente usables como `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_SESSION_TOKEN` para cualquier API de AWS que el rol permita.

El bug rara vez es "el servicio de metadata existe". El bug es la ausencia de uno de: un modo de metadata endurecido (IMDSv2), un bloqueo de capa de red al egress link-local desde los workloads de cara al público, o una defensa de SSRF a nivel de aplicación que cierre el gate link-local explícitamente.

## Técnicas / patrones
Qué miran atacantes y operadores:

- **Confirmá la nube primero.** `169.254.169.254` responde en AWS, Azure, DigitalOcean, Oracle, Alibaba; GCP responde en `169.254.169.254` *y* `metadata.google.internal`. Los paths exactos y los headers requeridos difieren; enviar la forma equivocada devuelve 401/403/404 y revela la nube.
- **Buscá primitivas de SSRF.** Fetchers de URL, entregadores de webhook, proxies de imágenes, fetchers de OpenID-discovery, XML/SVG con entidades externas, validadores de `redirect_uri` de OAuth que siguen la URL.
- **Leé la policy del rol.** Una vez exfiltradas las credenciales, `aws sts get-caller-identity` y `aws iam get-account-authorization-details` (o `gcloud auth list`, `az account show`) revelan qué puede hacer el rol. La mayoría de los roles están sobre-scopeados.
- **Reconocé los huecos de allowlist de SSRF.** Formas de bypass comunes: `0.0.0.0`, IPv4 en decimal-punteado-como-entero (`http://2852039166/`), IPv6-mapeado (`[::ffff:169.254.169.254]`), registros DNS apuntando a `169.254.169.254`, cadenas de redirect que la app sigue a ciegas, llamadas `fetch()` crudas en el renderizado del lado de JS.
- **Chequeá el hop limit.** AWS IMDSv2 deja que el operador setee un TTL (`HttpPutResponseHopLimit`) en la response de metadata; con un hop limit de 1, el tráfico desde dentro de un contenedor Docker o pod de Kubernetes no puede llegar de vuelta. Con el default de 1 seteado correctamente, los compromisos de contenedor no pueden pivotar a credenciales del host. Con el default de 64 (o sin setear), sí pueden.
- **Pivotá vía assume-role.** Si las credenciales cosechadas pueden `sts:AssumeRole`, el radio de explosión se extiende a cada rol al que puedan encadenar — entre cuentas cuando las trust policies lo permiten.

## Variantes y bypasses
El servicio de metadata de cada nube tiene su propia forma de protocolo. Tratarlos como uno es un error del defensor; usar el equivocado es un error del atacante. **6 variantes** importan en la práctica.

### 1. AWS IMDSv1
GET contra `http://169.254.169.254/latest/meta-data/...`, sin auth, sin headers requeridos. El default en instancias lanzadas antes de fines de 2019. Todavía extremadamente común en producción. Trivialmente explotable vía cualquier SSRF.

### 2. AWS IMDSv2
Basado en token: una request `PUT /latest/api/token` con `X-aws-ec2-metadata-token-ttl-seconds: 21600` devuelve un token de sesión; las requests `GET` posteriores deben cargar `X-aws-ec2-metadata-token: <token>`. **Dos propiedades hacen difícil abusar de IMDSv2 vía SSRF**: el método `PUT` (la mayoría de las primitivas de SSRF solo hacen GET) y el header de request custom (la mayoría de las primitivas de SSRF no pueden setear headers arbitrarios). También soporta `HttpPutResponseHopLimit` para bloquear el reach-through de contenedores. Cambiar de IMDSv1 → IMDSv2-requerido es el hardening de mayor palanca en AWS.

### 3. Metadata de GCP
`http://metadata.google.internal/computeMetadata/v1/...` (también alcanzable en `169.254.169.254`). Requiere el header `Metadata-Flavor: Google` en cada request. La postura de header-requerido significa que la mayoría de las primitivas básicas de SSRF no pueden alcanzarlo. Devuelve credenciales de service-account en `/computeMetadata/v1/instance/service-accounts/default/token`.

### 4. Azure IMDS
`http://169.254.169.254/metadata/instance?api-version=2021-02-01`. Requiere el header `Metadata: true`. Los tokens se obtienen en `/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/`.

### 5. DigitalOcean / Alibaba / Oracle
DigitalOcean: `http://169.254.169.254/metadata/v1/`. Alibaba Cloud y Oracle Cloud tienen cada uno sus propias variantes. Menos comúnmente atacados pero existen; si tu aplicación corre ahí, aplica el mismo patrón de defensa.

### 6. Tokens de service account de Kubernetes (la variante adyacente a metadata)
Los pods reciben JWTs en `/var/run/secrets/kubernetes.io/serviceaccount/token` (archivo, no HTTP) que autentican al kube-apiserver en `https://kubernetes.default.svc`. No es un endpoint de metadata per se, pero la misma forma: una primitiva de identidad tipo-link-local que credencializa cualquier proceso en el pod, sin gate de capa de aplicación. Defensa: atá los service accounts al mínimo privilegio; montá con `automountServiceAccountToken: false` donde sea posible.

## Impacto
Ordenado por severidad:

- **Compromiso de la cuenta de nube.** Las credenciales cosechadas dejan que el atacante ejercite cada permiso IAM que el rol tiene. En cuentas mal scopeadas, esto alcanza exfiltración de datos, escalada de privilegios vía cadenas `iam:PassRole`, persistencia (creando nuevos usuarios IAM / access keys) y pivoteo a otras cuentas cuando las trust policies cross-account lo permiten.
- **Exfiltración de datos del almacenamiento de nube.** S3, GCS, Azure Blob — la mayoría de los roles de aplicación pueden leer al menos algunos buckets que el atacante no puede alcanzar directamente.
- **Acceso a API interna.** Los servicios internos que autentican vía SigV4 / identidad derivada de metadata ahora le responden al atacante.
- **Movimiento lateral.** Los roles con `sts:AssumeRole` o cadenas cross-role análogas dejan que el atacante pivote a roles de mayor privilegio. Ver [[nat-and-private-networks|NAT y redes privadas]] para el encuadre del movimiento lateral.
- **Persistencia.** Las credenciales emitidas por el servicio de metadata se refrescan automáticamente; un atacante que sigue robando tokens frescos tiene acceso indefinido hasta que el rol se revoca o el stack de la aplicación se rota.
- **Costo / abuso.** Las credenciales comprometidas corren cryptominers, mandan email de phishing o preparan más ataques a costa de la víctima.

## Detección y defensa
Ordenado por efectividad:

1. **Cambiá al modo de metadata endurecido y requerilo.**
   AWS: `MetadataOptions.HttpTokens=required` (solo-IMDSv2) y `HttpPutResponseHopLimit=1`. GCP: confiá en el header `Metadata-Flavor` y revisá el scope del service-account. Azure: confiá en `Metadata: true`. Seteá esto a nivel de org/cuenta — Service Control Policies (AWS), Organization Policies (GCP), Azure Policy — para que los workloads individuales no puedan optar por salir. Este único cambio derrota la abrumadora mayoría de los ataques de metadata-vía-SSRF.

2. **Bloqueá el egress al rango link-local desde cualquier workload que tome input del usuario.**
   En la capa de red, negá `169.254.0.0/16` (y el link-local de IPv6 `fe80::/10`) en outbound desde los pods/instancias/funciones de cara al público. Los security groups de nube, NetworkPolicy de Kubernetes y las políticas de egress de service-mesh (Istio, Linkerd) soportan todos esto. Emparejá con la allowlist a nivel de aplicación; no confíes en ninguna sola.

3. **Allowlist de URL a nivel de aplicación con denegación explícita de privado/link-local.**
   Cada primitiva de fetch de URL (fetcher de imágenes, entregador de webhook, validador de redirect de OAuth, lector de RSS, renderer de PDF) debe resolver el hostname, chequear la IP resuelta contra una deny-list explícita (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`, `fc00::/7`, `fe80::/10`, `0.0.0.0`) y re-chequear después de cada redirect. El DNS rebinding es real; resolvé una vez y conectate a la IP resuelta, no al hostname.

4. **Usá VPC service endpoints / Private Google Access / Azure Private Link.**
   Donde el trabajo del workload es "hablar con S3 / GCS / unas pocas APIs de nube específicas", ruteá vía endpoints privados con scoping IAM explícito. Esto reduce la dependencia de egress del servicio de metadata para IAM y hace el robo de credenciales menos útil — muchos endpoints privados pueden gatearse adicionalmente por identidad de VPC.

5. **Scopeá el rol IAM agresivamente.**
   El rol por defecto adjunto a un tier web de cara al público debería otorgar solo el acceso específico de bucket/cola/secreto que necesita, con cláusulas `Condition` donde sea posible (source VPC, request tag, IP). Cuando las credenciales se filtren — y asumí que lo harán — el mínimo privilegio es la diferencia entre "molesto" y "equivalente a RCE".

6. **Detectá patrones anómalos de acceso a metadata.**
   GuardDuty (`UnauthorizedAccess:EC2/MetadataDNSRebind`, `Discovery:EC2/PortProbeUnprotectedPort`) y detecciones similares de GCP/Azure cubren los casos obvios. Custom: alertá ante llamadas STS desde IPs / regiones / user agents que la aplicación normalmente no usa.

7. **Deshabilitá el automount de tokens de service-account en los pods de Kubernetes** salvo que el pod realmente necesite llamar al API server.
   `automountServiceAccountToken: false` a nivel de pod-spec. Imponé vía admission control. Muchos workloads salen con el token montado por defecto y nunca lo usan; ese token está ahí esperando un compromiso de proceso.

### Qué no funciona como defensa primaria

- **Bloquear solo `127.0.0.1` y `localhost`.** El rango link-local, IPv4-como-entero, IPv6-mapeado y `0.0.0.0` son todos gates separados. Las allowlists de SSRF que cierran uno y se pierden los otros son el camino de fuga-de-metadata más común en producción.
- **String-matching de la URL.** `http://169.254.169.254/`, `http://[::ffff:a9fe:a9fe]/`, `http://2852039166/`, `http://attacker.com/?host=169.254.169.254` (open redirect encadenado con SSRF) y registros DNS apuntando a link-local son todos el mismo target. Resolvé y chequeá la IP, no el hostname o el string.
- **Confiar en que "la plataforma de nube se encarga".** Los defaults de nube a menudo favorecen la compatibilidad sobre el hardening. IMDSv1 todavía está permitido por defecto salvo que una org policy diga lo contrario. Los service accounts por defecto en GKE y AKS están sobre-scopeados. La defensa es tu responsabilidad, no de la plataforma.
- **Solo reglas de WAF.** Los WAFs ven la request de la aplicación; no ven el HTTP saliente de la aplicación. El robo de metadata ocurre en el camino de egress, que la mayoría de los WAFs no observan.
- **Credenciales de nube estáticas de larga vida dentro de la app.** "Usamos credenciales estáticas así que el endpoint de metadata no importa." Las credenciales estáticas filtradas son *peores* — no expiran solas, y a menudo tienen scope más amplio porque los operadores estaban demasiado cansados para scopearlas.

## Labs prácticos
`curl` estándar. **Corré esto solo contra instancias que sean tuyas.** La dirección link-local es por-VM, pero las acciones invocan APIs de nube reales sobre credenciales que son dinero real.

### Identificar la nube y probar IMDSv1

```bash
# AWS IMDSv1 (tiene éxito si no está endurecido)
curl -s --max-time 2 http://169.254.169.254/latest/meta-data/

# GCP — header requerido
curl -s --max-time 2 -H 'Metadata-Flavor: Google' \
  http://metadata.google.internal/computeMetadata/v1/

# Azure — header requerido, query parameter requerido
curl -s --max-time 2 -H 'Metadata: true' \
  'http://169.254.169.254/metadata/instance?api-version=2021-02-01'

# DigitalOcean
curl -s --max-time 2 http://169.254.169.254/metadata/v1/
```

### Verificar el enforcement de AWS IMDSv2

```bash
# IMDSv1 debería fallar cuando IMDSv2 es requerido
curl -s -o /dev/null -w 'imdsv1: %{http_code}\n' --max-time 2 \
  http://169.254.169.254/latest/meta-data/

# Request de token de IMDSv2
TOKEN=$(curl -s --max-time 2 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)

# Usar el token
curl -s --max-time 2 -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/info
```

### Testear la alcanzabilidad de contenedor (verificación del hop-limit)

```bash
# Desde un contenedor Docker o pod de Kubernetes en AWS:
docker run --rm curlimages/curl:latest -s --max-time 2 \
  http://169.254.169.254/latest/meta-data/
# Una instancia IMDSv2 con hop-limit correcto devuelve timeout / connection refused
# desde dentro de contenedores; el host todavía lo alcanza.
```

### Sondear SSRF buscando alcance de metadata (solo targets de lab)

```bash
# Formas de bypass que una allowlist de SSRF endurecida debe derrotar
for url in \
  'http://169.254.169.254/' \
  'http://[::ffff:169.254.169.254]/' \
  'http://2852039166/' \
  'http://0177.0.0.1/' \
  'http://0:80/' \
  'http://metadata.google.internal/' ; do
  printf '%-45s -> ' "$url"
  curl -s --max-time 2 -o /dev/null -w '%{http_code}\n' "$url" || echo timeout
done
```

### Usar credenciales cosechadas de forma segura (en tu propio lab)

```bash
# Traer las creds de la instancia, setear env, listar la identidad del rol — chequeo de sanidad read-only
TOKEN=$(curl -s -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)
ROLE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/)
CREDS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  "http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE")

export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r .AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r .SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r .Token)

aws sts get-caller-identity
# Esta es la misma forma que un atacante ejercita tras un robo exitoso.
# En una auditoría real, este lab confirma que tu rol está sobre-scopeado antes de que lo haga el atacante.
```

### Auditar el hop-limit y el modo IMDS en toda una cuenta

```bash
# AWS — listar todas las instancias y su postura de metadata-options
aws ec2 describe-instances --query \
  'Reservations[].Instances[].{Id:InstanceId,Tokens:MetadataOptions.HttpTokens,Hop:MetadataOptions.HttpPutResponseHopLimit}' \
  --output table
# Esperado: HttpTokens=required, HttpPutResponseHopLimit=1 en toda la flota.
```

## Ejemplos prácticos
- Un sitio de compartir fotos deja que los usuarios provean una URL remota para importar el avatar. El fetcher corre en EC2 con IMDSv1 habilitado. Un atacante envía `http://169.254.169.254/latest/meta-data/iam/security-credentials/web-role/`, cosecha credenciales y lee la foto de perfil de cada usuario desde S3.
- Un sistema de webhooks SaaS sigue redirects en las entregas salientes. La URL de webhook del atacante `https://attacker.example/redirect` hace un redirect 302 a `http://169.254.169.254/...`. El sistema de webhook nunca re-chequea el destino después del redirect.
- Un pod de Kubernetes corre un microservicio de OCR de imágenes que fetchea imágenes vía URL. El clúster no tiene NetworkPolicy y corre en EKS con el hop limit de IMDSv2 por defecto (1). El pod no puede alcanzar la metadata del host directamente — pero *sí* puede alcanzar la API de kubelet en `127.0.0.1:10250` desde dentro del pod, lo que le deja hacer exec en otros pods del mismo nodo.
- Un runner de GitHub Actions corre en una instancia EC2 self-hosted con IMDSv1 habilitado. Un pull request de un fork corre código no confiable. El script del job del PR fetchea el endpoint de metadata e imprime las credenciales en el log de acción público.
- Una función serverless fetchea metadata del proveedor OAuth (`/.well-known/openid-configuration`) vía una URL configurable. Mal configurada para usar una URL de proveedor controlada por el atacante, el fetch pega en `169.254.169.254` en su lugar. El rol de ejecución de Lambda queda comprometido.
- Una aplicación Spring Boot valida los parámetros `redirect_uri` contra una allowlist, pero la allowlist hace match por prefijo de string. El atacante envía `redirect_uri=http://169.254.169.254/...?legitimate.example.com` — el prefijo coincide con el inicio de la URL del atacante tras una codificación ingeniosa — y se alcanza la metadata.

## Notas relacionadas
- [[nat-and-private-networks|NAT y redes privadas]] — el espacio link-local, el sustrato sobre el que se sienta este tema entero.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — el bloqueo de egress de capa de red que gatea el alcance de la metadata.
- [[reverse-proxies|Reverse proxies]] — los proxies son intermediarios comunes de SSRF; el pensamiento de frontera-de-confianza aplica.
- [[client-ip-trust|Confianza en la IP del cliente]] — la confusión de allowlist-de-IP es un modo de falla hermano para la confianza interna de la nube.
- [[cybersecurity/web-security/ssrf|SSRF]] — la primitiva de capa de aplicación que hace posible este ataque.
- [[cybersecurity/web-security/cors-misconfiguration|Mala configuración de CORS]] — adyacencia: la confianza de origen del lado del cliente no protege a los fetchers del lado del servidor.
- [[cybersecurity/web-security/file-upload-abuse|Abuso de subida de archivos]] — las subidas de SVG/PDF/HTML pueden volverse vectores de SSRF vía renderers headless.
- [[cybersecurity/security-playbooks/trace-metadata-endpoint-reachability|Trazar la alcanzabilidad del endpoint de metadata]]
- [[cybersecurity/devsecops/secrets-management|Gestión de secretos]] — las credenciales estáticas de larga vida son la peor alternativa a la metadata de instancia.

### Notas atómicas futuras sugeridas
- [[imdsv2-hop-limit-design|Diseño del hop-limit de IMDSv2]]
- [[ssrf-allowlist-design|Diseño de allowlist de SSRF]]
- [[gcp-workload-identity|Workload Identity de GCP]]
- [[aws-sts-assume-role-chains|Cadenas de assume-role de AWS STS]]
- [[kubernetes-service-account-tokens|Tokens de service account de Kubernetes]]
- [[dns-rebinding|DNS rebinding]]
- [[metadata-detection-with-guardduty|Detección de metadata con GuardDuty]]

## Referencias
- **Foundational:** AWS Instance Metadata Service docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- **Foundational:** GCP metadata server docs — https://cloud.google.com/compute/docs/metadata/overview
- **Foundational:** Azure Instance Metadata Service docs — https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
