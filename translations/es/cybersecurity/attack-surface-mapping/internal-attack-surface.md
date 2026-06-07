# Internal Attack Surface

## Definición

La internal attack surface es el conjunto de servicios, rutas, redes, credenciales, endpoints de metadatos, interfaces admin y rutas de confianza alcanzables desde dentro de un entorno aunque no sean públicos.

## Por qué importa

Muchos incidentes severos provienen de la brecha entre alcanzabilidad pública y alcanzabilidad interna. Una vez que un atacante obtiene SSRF, ejecución server-side, acceso VPN, un workload comprometido o una identidad cloud débilmente aislada, las superficies "solo internas" se convierten en parte de la superficie de ataque real.

Esta nota difiere de [[external-attack-surface]]: la pregunta central es qué se vuelve alcanzable cuando colapsa un límite de confianza.

## Cómo funciona

La internal attack surface tiene **5 posiciones de alcanzabilidad**:

1. **Workload de aplicación.** Lo que el servidor web/API puede alcanzar.
2. **Contenedor o pod.** Lo que un contenedor puede alcanzar en redes overlay, interfaces del host y service accounts.
3. **Instancia cloud o función.** Lo que la identidad cloud y los metadatos hacen alcanzable.
4. **Red de empleado/VPN.** Lo que los usuarios internos autenticados pueden alcanzar.
5. **Ruta de partner o vendor.** Lo que los terceros pueden alcanzar a través de integraciones o links privados.

El error es tratar "no expuesto a internet" como equivalente a "seguro". La alcanzabilidad interna sigue necesitando autenticación, autorización, segmentación, logging y least privilege.

Un ejemplo trabajado, de SSRF a superficie interna:

```
Input externo:
  https://app.example.test/avatar?url=http://10.0.12.34:8080/health

Comportamiento observado:
  200 OK, el cuerpo contiene "management-api"

Posición de alcanzabilidad:
  workload de aplicación

Nuevo hecho de superficie de ataque:
  el servidor de app puede alcanzar 10.0.12.34:8080, aunque el servicio no es público

Pregunta de seguridad:
  ¿ese servicio interno requiere identidad del workload, o la ubicación en la red sola autoriza el acceso?
```

El resultado útil no es "existe SSRF" por sí solo. Es un mapa de qué puede alcanzar la posición de request comprometida y qué controles siguen siendo válidos allí.

## Técnicas / patrones

Los profesionales mapean:

- rangos de IP privados, service discovery, zonas DNS y hostnames internos
- endpoints de metadatos y rutas IAM cloud
- APIs admin, dashboards, colas, bases de datos y servicios HTTP internos
- servicios Kubernetes, tokens de service-account y alcanzabilidad pod-a-pod
- rutas de fetch controladas por SSRF y reglas de egress del proxy
- política de acceso VPN/zero-trust y segmentación east-west

## Variantes y bypasses

La superficie interna aparece en **6 formas**.

### 1. Metadatos e identidad cloud

Metadatos cloud, identidades de workload, tokens de service account y roles IAM.

### 2. Herramientas admin y de control

Dashboards, consolas, APIs, endpoints de debug, CI/CD y herramientas de observabilidad.

### 3. Servicios de datos y de backend

Bases de datos, colas, cachés, almacenes de archivos, APIs internas y service meshes.

### 4. Redes planas internas

Redes privadas donde un workload puede alcanzar muchos servicios no relacionados.

### 5. Rutas SSRF

Los fetches de URL server-side permiten a un atacante externo emitir requests de red internas.

### 6. Rutas de partner y vendor

Las conexiones de partner, endpoints privados e integraciones SaaS amplían la confianza interna.

## Impacto

Ordenado aproximadamente por severidad:

- **Robo de credenciales cloud.** La exposición de metadatos e identidad de workload puede otorgar acceso a APIs cloud.
- **Movimiento lateral.** Las redes planas exponen bases de datos, colas y herramientas admin después de un foothold.
- **Compromiso del plano de control.** Los dashboards internos o sistemas CI/CD alteran producción.
- **Exposición de datos.** Las APIs internas devuelven datos sin autenticación fuerte del llamador.
- **Amplificación del impacto de SSRF.** Un fetch de URL de bajo impacto se convierte en reconocimiento interno o acceso a credenciales.

## Detección y defensa

Ordenado por efectividad:

1.
**Mapeás la alcanzabilidad desde posiciones de workload, no solo diagramas de red.**
   Testéa qué pueden alcanzar realmente los servidores de app, contenedores, funciones y usuarios VPN.

2.
**Requerís autenticación y autorización en servicios internos.**
   La ubicación en la red debería reducir la exposición, no reemplazar la identidad y la política.

3.
**Segmentás servicios de alto valor y bloqueás caminos east-west innecesarios.**
   Las bases de datos, metadatos, herramientas admin, colas y CI/CD necesitan alcanzabilidad estricta.

4.
**Endurecés el acceso a metadatos e identidad de workload.**
   Enforceá IMDSv2 o controles equivalentes, restringí service accounts y bloqueá egress link-local donde sea posible.

5.
**Restringís fetchers y proxies server-side.**
   Las allowlists de URL deben resolver y bloquear destinos privados, loopback, link-local y de redirect.

6.
**Logueás el acceso interno por identidad de workload.**
   Las llamadas a servicios internos deberían ser atribuibles a workload, usuario, token y ruta.

### Qué no funciona como defensa primaria

- **"IP privada significa seguro."** La alcanzabilidad depende del camino, no de la estética de la dirección.
- **Paneles admin internos no autenticados.** SSRF, compromiso de VPN o de workload puede alcanzarlos.
- **Monitoreo solo del perímetro.** El movimiento interno puede nunca cruzar el edge público.
- **Denegar solo `169.254.169.254` como string.** Los bypasses de SSRF incluyen redirecciones, DNS rebinding, IPs en formato entero, formas IPv6 y hosts de metadatos alternativos.

## Labs prácticos

Usá un lab propio o una cuenta cloud.

### Revisá interfaces de red

```
ip route
ip addr
```

Registrá rangos privados, gateways por defecto y rutas link-local.

### Sondeá servicios internos desde un workload

```
for host in 127.0.0.1 169.254.169.254 10.0.0.1 172.16.0.1 192.168.0.1; do
  curl -m 2 -i "http://$host/" | head
done
```

Ejecutá solo en un entorno de lab/propio.

### Revisá la topología del cluster Kubernetes

```
kubectl get svc -A -o wide
kubectl get pods -A -o wide
```

Mapeá qué servicios son cluster-internal, expuestos en el nodo, o balanceados por carga.

### Buscá fetches server-side en el código

```
rg -n "fetch\\(|axios|requests\\.get|http\\.Get|open-uri|curl" src
```

Estos son los lugares donde el input externo puede convertirse en alcanzabilidad interna.

### Construí una matriz de alcanzabilidad de límites

```
Posición fuente | Destino      | Puerto | ¿Esperado? | ¿Auth requerida? | Evidencia | Propietario
web-pod         | metadatos    | 80     | no         | n/a              | bloqueado | platform
web-pod         | redis        | 6379   | no         | sí/no            | timeout   | data
vpn-user        | grafana      | 443    | sí         | SSO+MFA          | 302 SSO   | observabilidad
```

Esto convierte los sondeos dispersos en una revisión de límites en lugar de una lista de hosts.

### Verificá la alcanzabilidad del endpoint de metadatos

```
curl -sS --max-time 2 http://169.254.169.254/ || true
curl -sS --max-time 2 http://[fe80::a9fe:a9fe]/ || true
```

Ejecutá solo desde workloads propios; comparar el comportamiento a nivel host, contenedor y app.

## Ejemplos prácticos

- Un servidor de app puede alcanzar los metadatos cloud y las APIs admin internas.
- Un servicio supuestamente privado está expuesto a todos los workloads en una VPC.
- Los dashboards internos solo dependen de la ubicación en la red.
- SSRF alcanza Redis, Elasticsearch o las APIs de Kubernetes.
- Un link privado de partner otorga mayor alcance del previsto.

## Notas relacionadas

- [[attack-surface-mapping]]
- [[external-attack-surface]]
- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[ssrf|SSRF]]
- [[admin-interface-discovery]]
- [[cloud-iam-boundaries]]

### Notas atómicas futuras sugeridas

- kubernetes-internal-surface
- service-mesh-attack-surface
- ssrf-reachability-mapping
- internal-admin-surface

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP API7:2023 SSRF — https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/
- **Fundamental:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
