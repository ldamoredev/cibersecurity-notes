# Attack Surface Mapping

## Definición

El attack surface mapping es la práctica de identificar qué activos, servicios, rutas, interfaces, dependencias, almacenes de datos, entornos y relaciones de confianza están **realmente expuestos o son alcanzables** desde la perspectiva de un atacante, y comparar esa realidad observable con el diseño previsto por la organización. El entregable es un inventario mantenido con propietario, entorno, nivel de exposición y estado del ciclo de vida por activo.

## Por qué importa

Los equipos de seguridad razonan habitualmente desde diagramas de arquitectura, diseños previstos y supuestos de ownership. Los atacantes razonan desde lo que responde. El attack surface mapping cierra esa brecha partiendo de la realidad observable y tratando cada discrepancia —servicio no documentado, DNS obsoleto, endpoint oculto, API sin documentar, panel admin expuesto, almacenamiento reclamable, superficie conectada a un vendor, entorno abandonado, recurso cloud derivado— como candidato a triaje.

La asimetría es estructural: los atacantes encuentran la superficie gratis usando fuentes públicas y un poco de sondeo; los defensores necesitan trabajo explícito para mantener una vista actualizada. Un equipo que no invierte en mapeo está permanentemente rezagado, y la brecha crece con cada deployment, cambio de vendor, certificado y registro DNS.

Esta es la **nota paraguas** de la rama:
- [[external-attack-surface]] es propietaria de la alcanzabilidad pública (la vista dominante del atacante).
- [[internal-attack-surface]] es propietaria de la alcanzabilidad post-colapso de límite (qué se vuelve alcanzable tras SSRF, foothold o VPN).
- [[recon|Recon]] es propietario del flujo de trabajo operativo que descubre superficie candidata.
- Esta nota es propietaria del **modelo de razonamiento** que los une en un mapa accionable.

## Cómo funciona

El attack surface mapping hace **5 preguntas de inventario** sobre cada activo observado. Saltear cualquiera de ellas produce un mapa que no puede impulsar la remediación.

1. **¿Qué existe?** Dominios, hosts, IPs, puertos, servicios, rutas, APIs, almacenamiento, identidades, vendors, entornos y las relaciones entre ellos. Fuente: reconocimiento externo ([[passive-recon]]) más inventario inside-out (cuentas cloud, gateways, repositorios, certificados, logs de tráfico).
2. **¿Qué es alcanzable?** Internet, red interna, cloud VPC, workload, navegador, red de partner, o solo a través de rutas SSRF/foothold. La alcanzabilidad es una propiedad del camino, no de la dirección ([[nat-and-private-networks]]).
3. **¿Qué está previsto?** Superficie pública del producto, plano de control privado, entorno de staging, compatibilidad legacy, integración de vendor, o desconocido/huérfano. La respuesta "desconocido" es en sí misma un hallazgo.
4. **¿Quién lo tiene?** Equipo, sistema, vendor, entorno, estado del ciclo de vida, ruta de escalación. **"Propietario desconocido" es un hallazgo de seguridad** porque nadie puede de forma segura retirar, parchear o endurecer el activo.
5. **¿Qué cambió?** Nuevos deployments, deriva de versión, DNS obsoleto, servicios abandonados, esquemas filtrados, activos desaprovisionados pero aún alcanzables, nuevas relaciones con vendors. El mapeo es un diff, no una snapshot.

No hay payload aquí. La nota es un **modelo de razonamiento**: comparar la superficie observable con el diseño previsto, tratar cada discrepancia como candidato a triaje, y enrutar cada candidato a validación, remediación, asignación de ownership o retiro.

Un ejemplo trabajado, el diff en acción:

```
Pregunta:  Mapear la superficie externa de example.com y marcar la deriva.
Fuente A (outside-in): cert transparency + DNS + nmap → 47 nombres, 12 servicios activos, 3 hosted por vendor.
Fuente B (inside-out): cuenta cloud + provider DNS + registro de activos → 41 nombres, 11 servicios.
Diff:      6 nombres en A no en B (candidatos a deriva), 0 en B no en A.
Triaje:    3 nombres derivados → propiedad de equipo que se fue (huérfanos), 2 → vendor adquirido obsoleto, 1 → deploy reciente aún no registrado.
Acción:    huérfanos → retirar DNS+cert; obsoletos → baja con vendor; nuevo → registrar en DB de activos.
```

El diff entre outside-in e inside-out es el artefacto clave. El inventario de una sola fuente siempre pierde una dirección.

## Técnicas / patrones

Los profesionales combinan descubrimiento outside-in e inventario inside-out.

- **Outside-in:** dominios raíz, subdominios, certificate transparency (`crt.sh`), registros DNS (historial DNS pasivo), registros ASN/BGP, enumeración IP/puerto, fingerprinting de tecnología web, extracción de rutas desde JavaScript/source-maps, specs públicas de API, introspección de GraphQL, triaje de almacenamiento expuesto.
- **Inside-out:** inventarios de cuenta cloud (AWS Config, GCP Asset Inventory, Azure Resource Graph), zonas del provider DNS, configs de gateway/load-balancer, búsqueda de código en repositorios, logs de tráfico, registros del sistema de orquestación de certificados, registros de propietarios.
- **Comparación diff:** outside-in vs inside-out, snapshot actual vs anterior, observado vs documentado, nombre de activo público vs registro de activos.
- **Integración de ciclo de vida:** el descubrimiento alimenta los pipelines de releases (nuevo activo → DB de activos antes del lanzamiento) y los flujos de descomisionamiento (activo retirado → DNS, cert, ruta, almacenamiento, monitoreo eliminados juntos).

## Variantes y bypasses

La superficie de ataque se agrupa en **6 clases de exposición**. Cada clase tiene un patrón de descubrimiento y un patrón de remediación diferentes.

### 1. Superficie pública del producto

Dominios, hosts, puertos, apps web, APIs, almacenamiento y servicios de acceso remoto alcanzables desde internet público. La vista dominante del atacante; cubierta en profundidad por [[external-attack-surface]]. Descubrimiento: cert transparency + DNS + port scan + web crawl.

### 2. Superficie de aplicación oculta

Rutas, parámetros, campos GraphQL, versiones de API, endpoints de apps móviles y rutas descubiertas por JavaScript no visibles en la UI normal. La aplicación tiene más superficie que lo que sugiere su UI. Descubrimiento: extracción de source-maps, ingeniería inversa de apps móviles, [[api-inventory-management|inventario de API]].

### 3. Superficie admin y de control

Paneles admin, herramientas de soporte, interfaces de debug, sistemas CI/CD, dashboards, consolas de vendor y APIs de gestión. A menudo con mayor privilegio que la superficie del producto, a menudo con autenticación más débil. Cubierta en profundidad por [[admin-interface-discovery]].

### 4. Entornos no productivos

Entornos de staging, preview, beta, legacy, regional, demo y temporales que permanecen alcanzables después de que su propósito terminó. **La exposición temporal se vuelve permanente** si no está vinculada a la automatización del ciclo de vida. Los patrones de nombres de riesgo (`dev.`, `staging.`, `beta.`, `legacy.`) aceleran el triaje.

### 5. Superficie de terceros y vendors

CDNs, almacenamiento de objetos, portales SaaS, proveedores de identidad, APIs externas, endpoints de metadatos cloud, activos hosted por vendors. La confianza se extiende a través de CNAMEs y scopes OAuth; los fallos en cascada cruzan el límite. Cubierta por [[third-party-exposure]].

### 6. Superficie interna post-foothold

Servicios privados que se vuelven alcanzables tras SSRF, ejecución server-side, acceso VPN, workload comprometido o segmentación débil. Cubierta en profundidad por [[internal-attack-surface]]. El descubrimiento ocurre después de un foothold o mediante tests de alcanzabilidad SSRF.

## Impacto

Ordenado aproximadamente por severidad:

- **Ruta de compromiso directo.** Un admin, debug, almacenamiento o servicio vulnerable expuesto se convierte en el punto de entrada más fácil. Un Jenkins olvidado es suficiente.
- **Bypass de control de acceso.** Endpoints ocultos, versiones deprecated de API o entornos de staging saltan los controles presentes en la ruta principal del producto.
- **Exposición de datos.** Almacenamiento, esquemas, logs, source maps, exportaciones y APIs verbosas filtran credenciales, fuente, datos de clientes o terminología interna.
- **Takeover cloud o de vendor.** CNAMEs obsoletos, registros DNS huérfanos y terceros excesivamente confiados se vuelven reclamables. Cubierto por [[subdomain-takeover]].
- **Brechas de parches y monitoreo.** Los activos desconocidos no se parchean, registran, limitan en rate o tienen propietario. El activo se convierte en su propio vector de ataque al ser invisible para los defensores.

## Detección y defensa

Las defensas priorizan **mantener el diff**, no ejecutar escaneos únicos.

1.
**Mantenés un inventario vivo desde múltiples señales.**
   Combiná DNS, cuentas cloud, gateways, repositorios, logs de tráfico, certificados, escáneres y registros de propietarios. Una sola fuente de inventario siempre pierde la deriva; el diff entre fuentes es donde se esconde la deriva.

2.
**Asignás propietario, entorno, exposición y estado del ciclo de vida a cada activo.**
   "Propietario desconocido" y "propósito desconocido" son hallazgos de seguridad. Sin propietarios, ninguna remediación se completa; sin estado del ciclo de vida, el retiro nunca ocurre.

3.
**Comparás continuamente el diseño previsto con la alcanzabilidad observada.**
   El mapeo es un diff, no una snapshot. Programá la comparación outside-in vs inside-out; tratá cada nombre en una vista pero no en la otra como candidato a triaje.

4.
**Priorizás por alcanzabilidad, privilegio, sensibilidad de datos y poder del plano de control.**
   Las superficies de admin e almacenamiento con acceso a internet superan en prioridad a páginas de bajo impacto. Riesgo = (alcanzabilidad) × (privilegio si se compromete) × (sensibilidad de datos).

5.
**Integrás el descubrimiento en los pipelines de release y descomisionamiento.**
   Los nuevos activos entran al inventario antes del lanzamiento; los sistemas retirados pierden DNS, certificados, rutas, credenciales, políticas de almacenamiento y dependencias de monitoreo juntos. La automatización del ciclo de vida previene la deriva más común.

6.
**Usás escaneo seguro y autorizado con rate limits.**
   El descubrimiento debería ser repetible y de bajo ruido en entornos de producción. El escaneo agresivo de tu propia superficie está bien pero genera alertas y carga; presupuestalo.

### Qué no funciona como defensa primaria

- **Diagramas de arquitectura solos.** Describen la intención, no la exposición observada; el diagrama es lo que debería existir, no lo que existe.
- **Eliminar links de la UI para ocultar endpoints.** Las rutas de API ocultas siguen siendo invocables; la oscuridad no es control de acceso.
- **Escaneos únicos.** La superficie de ataque cambia con cada deployment, cambio de vendor, certificado y registro DNS. Un escaneo del trimestre pasado está incorrecto hoy.
- **Listas de activos sin propietarios.** El inventario sin propietarios no produce remediación; la lista crece pero nada sucede.
- **Asumir que "cloud" o "privado" significa inalcanzable.** La alcanzabilidad depende del camino de red, la identidad y el contexto del workload, no del espacio de direcciones.

## Labs prácticos

Usá un dominio propio, un scope autorizado o un entorno de lab.

### Construí un mapa de activos básico

```
activo                 | tipo         | entorno    | alcanzabilidad | propietario | auth        | sensibilidad datos | ciclo de vida
example.com            | web app      | producción | internet       | platform    | OIDC        | media              | activo
api.example.com        | REST API     | producción | internet       | api-team    | OAuth+JWT   | alta               | activo
support.example.com    | vendor (zd)  | producción | internet       | soporte     | vendor SSO  | media              | activo
admin.example.com      | panel admin  | producción | internet       | platform    | basic auth  | alta               | DEPRECAR
staging.example.com    | app staging  | staging    | internet       | desconocido | débil       | alta               | INVESTIGAR
legacy-blog.example.io | sitio legacy | desconocido| internet       | DESCONOCIDO | ninguna     | baja               | RETIRAR
```

Las filas "desconocido" son hallazgos. El mapa es el entregable.

### Ejecutá un diff outside-in vs inside-out

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sort -u > outside.txt

cat dns-zone.txt asset-registry.txt | sort -u > inside.txt

comm -23 outside.txt inside.txt > drift-solo-outside.txt   # observado pero no registrado
comm -13 outside.txt inside.txt > drift-solo-inside.txt    # registrado pero no observado (¿descomisionado?)
```

Los nombres solo en outside son candidatos a deriva; los solo en inside son candidatos a verificación de descomisionamiento.

### Buscá rutas no documentadas en el código

```
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src/ > routes-in-code.txt

yq '.paths | keys' openapi.yaml > routes-in-spec.txt

awk '$7 ~ "/api/" {print $7}' access.log | sort -u > routes-in-traffic.txt
```

Las rutas en código pero no en spec están sin documentar. Las rutas en tráfico pero no en código son problemas de routing obsoleto o de proxy.

### Escaneá servicios activos

```
nmap -sV -Pn -p 22,80,443,3389,5432,6379,8080,8443,9000-9100 --open target.example.test
```

Por cada servicio abierto, clasificá como esperado / inesperado / desconocido / candidato a retiro.

### Checklist de descomisionamiento

```
activo retirado:             api-staging-old.example.com
DNS A/CNAME eliminado:       sí / no
certificado revocado:        sí / no
regla de load-balancer:      sí / no
recurso cloud eliminado:     sí / no
secretos/credenciales:       rotados y eliminados
alertas de monitoreo:        eliminadas (sin falsos positivos en activo retirado)
```

El descomisionamiento es la fuente más común de deriva; el checklist obliga a que todos los pasos de limpieza se completen juntos.

## Ejemplos prácticos

- Un host de staging permanece con acceso a internet meses después del lanzamiento y usa autenticación más débil que producción.
- Un bundle JavaScript expone endpoints de API no documentados que saltan los controles de acceso del nivel de UI.
- Una integración SaaS eliminada deja un CNAME DNS reclamable que apunta a un tenant del vendor desaprovisionado.
- Un bucket de almacenamiento de objetos expone logs, backups o source maps porque la política del bucket nunca fue revisada después del lanzamiento.
- Una versión legacy de la API sigue devolviendo campos sensibles que la versión actual filtra.
- Una nueva relación de vendor agrega un CNAME en `support.example.com` sin pasar por el registro de activos, volviéndose invisible para el inventario.

## Notas relacionadas

- [[external-attack-surface]]
- [[internal-attack-surface]]
- [[exposed-service-triage]]
- [[endpoint-discovery]]
- [[admin-interface-discovery]]
- [[third-party-exposure]]
- [[subdomain-takeover]]
- [[api-inventory-management|API Inventory Management]]
- [[recon|Recon]]
- [[company-osint|Company OSINT]]

### Notas atómicas futuras sugeridas

- staging-environments
- schema-exposure
- asset-ownership-model
- internet-exposure-reduction
- cloud-asset-inventory
- hidden-parameter-discovery
- lifecycle-decommission-automation

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
- **Fundamental:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services
