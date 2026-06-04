---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - dns
  - dangling-records
sources: []
---

# Registros DNS colgantes

## Definición
Los registros DNS colgantes son entradas de DNS que todavía apuntan a infraestructura, recursos de nube, mapeos de SaaS, buckets de almacenamiento, distribuciones de CDN u objetivos de servicio que ya no existen o ya no están controlados por el dueño previsto.

## Por qué importa
Los registros colgantes son la falla de ciclo de vida que está debajo de muchos hallazgos de subdomain takeover. Un hostname puede parecer legítimo a usuarios, navegadores, cookies, política HSTS, allowlists de redirect de OAuth y documentación interna mientras su objetivo de respaldo está abandonado o es reclamable.

Esta nota de networking es dueña del mecanismo nombre-objetivo obsoleto. [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] es dueña de la condición de exposición confirmada donde un atacante puede reclamar el objetivo.

## Cómo funciona
Una falla de registro colgante tiene **4 partes en movimiento**:

1. **El nombre DNS sigue vivo.** La organización todavía publica `blog.example.com`, `docs.example.com` u otro hostname.
2. **El ciclo de vida del objetivo cambia.** La app de respaldo, bucket, distribución de CDN, tenant de SaaS o load balancer de nube se borra, renombra, expira o mueve.
3. **La limpieza de DNS no ocurre.** El registro obsoleto sigue apuntando al viejo objetivo del proveedor.
4. **El comportamiento del proveedor decide el impacto.** Algunos proveedores devuelven errores inofensivos; otros permiten que un nuevo tenant/recurso reclame el mismo objetivo.

Ejemplo:

```txt
docs.example.com. 300 IN CNAME example-docs.vendor-cdn.net.
```

Si `example-docs` se borra en el vendor pero el DNS queda, un atacante podría registrar `example-docs` y servir contenido como `docs.example.com`.

El bug es el vínculo de ciclo de vida roto entre el DNS y el recurso del proveedor, no la resolución DNS sola.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- registros `CNAME` que apuntan a nombres de SaaS, CDN, app-hosting, almacenamiento y proveedores de nube
- registros `A` / `AAAA` que apuntan a IPs de nube desasignadas o load balancers viejos
- strings de error específicos del proveedor como "no such app", "project not found", "bucket not found" o "unconfigured domain"
- registros TXT de verificación que pueden preservar propiedad vieja del proveedor
- registros DNS de entornos retirados: `staging`, `preview`, `old`, `docs`, `help`, `status`, `campaign`
- logs de CT e historial de DNS para hostnames que ya no aparecen en el inventario actual
- documentación del proveedor sobre si los objetivos de dominio custom son reclamables tras la eliminación

## Variantes y bypasses
Los registros colgantes aparecen en **6 formas comunes**.

### 1. CNAME colgante a SaaS o app hosting
El hostname hace alias a un nombre gestionado por el proveedor, pero el tenant/proyecto/site ya no existe. Esta es la forma clásica de subdomain takeover para sitios de documentación, portales de soporte, páginas de marketing y plataformas de apps.

### 2. Bucket de almacenamiento o sitio estático borrado
El registro DNS apunta a object storage o hosting estático, y el nombre del bucket/site queda disponible para otra cuenta. El impacto depende de las reglas de namespace del proveedor y del matching de región.

### 3. IP de nube o load balancer desasignado
Un registro `A` apunta a una IP o load balancer que fue liberado. Si la dirección o endpoint puede asignarse después a otro cliente, el registro obsoleto puede rutear tráfico al dueño equivocado.

### 4. Distribución de CDN o dominio custom obsoleto
La organización remueve la distribución de CDN o el binding de dominio custom pero deja el DNS. Otra distribución podría reclamar el hostname si la validación de certificado/dominio lo permite.

### 5. Residuo de token de verificación
Los registros TXT de email, SaaS, validación de dominio, search consoles, analytics o proveedores de nube quedan tras retirar la integración. El registro puede no rutear tráfico, pero puede preservar prueba de control.

### 6. Registros colgantes internos/privados
Las zonas hospedadas privadas y el DNS interno también pueden colgar. El impacto suele ser misrouting interno, amplificación de SSRF, suplantación de servicios o confusión en la respuesta a incidentes, más que takeover público.

## Impacto
Ordenado aproximadamente por severidad:

- **Subdomain takeover.** El atacante sirve contenido bajo un hostname confiable tras reclamar el objetivo de respaldo del proveedor.
- **Abuso de credenciales/sesión.** El estatus de subdominio confiable puede influir en cookies, allowlists de redirect de OAuth, CORS, callbacks de SSO o credibilidad de phishing.
- **Intercepción de tráfico.** Usuarios, clientes de API o automatización siguen enviando requests a un nombre cuyo objetivo ya no es tuyo.
- **Abuso de marca y phishing.** El atacante obtiene HTTPS y un hostname de apariencia legítima si la emisión de certificado tiene éxito.
- **Confusión de servicios internos.** Nombres privados obsoletos rutean workloads a servicios equivocados o endpoints muertos.
- **Deriva de inventario.** Los registros colgantes son evidencia de que el ciclo de vida de los activos y el del DNS están desconectados.

## Detección y defensa
Ordenado por efectividad:

1. **Atá los registros DNS a recursos de proveedor propios en el inventario.**
   Cada registro externo debería mapear a un recurso concreto de nube/SaaS/CDN/almacenamiento con un dueño y un estado de ciclo de vida. Si el recurso de respaldo desaparece, el DNS debería alertar o fallar la revisión.

2. **Borrá o estacioná el DNS antes de destruir el objetivo.**
   El deprovisioning debería remover el registro DNS o apuntarlo a un endpoint de parking controlado antes de borrar el recurso del proveedor. Esto evita la ventana reclamable.

3. **Escaneá continuamente fingerprints colgantes específicos del proveedor.**
   Resolvé periódicamente los CNAMEs y pedí el host por HTTP/HTTPS. Los mensajes "not found" del proveedor son de alta señal. Mantené una lista de fingerprints pero verificá manualmente antes de declarar takeover.

4. **Limpiá los registros TXT de verificación obsoletos.**
   Remové los registros de validación de SaaS, email, search y nube cuando terminan las integraciones. Los tokens de verificación se olvidan seguido porque no sirven tráfico directamente.

5. **Preferí configuraciones de proveedor que requieran validación de dominio antes del reclamo.**
   Algunas plataformas previenen el reclamo arbitrario sin un token de DNS fresco o validación de certificado. Elegí proveedores más seguros y habilitá los chequeos de propiedad de dominio donde estén disponibles.

6. **Monitoreá DNS y certificate transparency en busca de nombres abandonados.**
   Los logs de CT pueden mostrar certificados para hosts viejos. El historial de DNS puede mostrar nombres que desaparecieron del inventario pero todavía reciben tráfico o siguen delegados.

7. **Documentá los estados de parking aceptados.**
   Un `CNAME` deliberado a un host de parking controlado o un `A` a una página sink es distinto de un error accidental del proveedor. Hacé visible la diferencia.

### Qué no funciona como defensa primaria

- **Asumir que un 404 del proveedor es inofensivo.** Algunos 404 del proveedor son exactamente la señal de que un objetivo puede reclamarse.
- **Confiar en HSTS o HTTPS.** TLS puede proteger la conexión a un objetivo reclamado por el atacante; no prueba que el objetivo sea tuyo.
- **Borrar primero el recurso de nube.** Eso crea la condición colgante. La limpieza de DNS debe ocurrir antes o junto con la eliminación.
- **Escanear solo el inventario actual.** Los registros colgantes suelen vivir en hosts olvidados encontrados a través de logs de CT, historial de DNS, docs o repos viejos.
- **Tratar todos los fingerprints como takeovers confirmados.** El comportamiento del proveedor cambia. Un fingerprint significa investigar y probar la reclamabilidad de forma segura dentro del alcance autorizado.

## Labs prácticos
Corré solo contra dominios que sean tuyos o que estés autorizado a evaluar.

### Listar objetivos CNAME y fronteras de proveedor

```bash
while read -r name; do
  target=$(dig +short "$name" CNAME | tail -n1)
  [ -n "$target" ] && printf '%-45s -> %s\n' "$name" "$target"
done < subdomains.txt
```

Etiquetá cada objetivo por proveedor y dueño esperado.

### Sondear fingerprints de error de proveedor

```bash
while read -r name; do
  printf '\n== %s ==\n' "$name"
  dig +short "$name" CNAME
  curl -skL --max-time 5 "https://$name" | sed -n '1,12p'
done < subdomains.txt
```

Buscá mensajes de dominio-no-configurado específicos del proveedor, y después verificá contra los docs actuales del proveedor y tus reglas de alcance.

### Comparar DNS con el inventario de activos

```bash
while read -r name; do
  target=$(dig +short "$name" CNAME A AAAA | tr '\n' ' ')
  printf '%s,%s\n' "$name" "$target"
done < subdomains.txt > dns-targets.csv
```

Diffeá `dns-targets.csv` contra los exports de inventario de nube/CDN/SaaS. Los objetivos sin match son candidatos a revisión.

### Chequear registros de verificación obsoletos

```bash
domain=example.com
dig +short "$domain" TXT
for sub in google-site-verification atlassian-domain-verification amazonses; do
  dig +short "$sub.$domain" TXT
done
```

Los tokens inesperados deberían mapear a integraciones activas o ser removidos.

### Revisar Certificate Transparency en busca de nombres olvidados

```bash
domain=example.com
curl -s "https://crt.sh/?q=%25.$domain&output=json" \
  | jq -r '.[].name_value' 2>/dev/null \
  | tr '\n' '\n' \
  | sort -u
```

Los nombres que están en CT pero no en el inventario son buenos candidatos a registro colgante.

### Patrón de confirmación segura

```text
1. Confirmá que el hostname está en el alcance autorizado.
2. Confirmá que el objetivo del proveedor ya no mapea a un recurso propio.
3. Confirmá que los docs del proveedor dicen que el objetivo es reclamable.
4. Usá la prueba menos invasiva permitida por el programa o el dueño.
5. Nunca sirvas contenido engañoso ni recolectes tráfico.
```

## Ejemplos prácticos
- `help.example.com` apunta a un tenant de helpdesk borrado y muestra una página "project not found" del proveedor.
- `static.example.com` apunta a un bucket de almacenamiento removido cuyo nombre puede re-crearse.
- `campaign.example.com` apunta a un dominio custom de SaaS de marketing retirado después de que terminó el contrato.
- `_amazonses.example.com` queda mucho después de que el envío por SES fue migrado a otro lado.
- Un registro de DNS privado todavía apunta `payments.internal` a una IP de servicio vieja ahora usada por otro workload.

## Notas relacionadas
- [[dns-resolution|Resolución DNS]] — cómo resuelve la cadena nombre-objetivo.
- [[dns-security|Seguridad de DNS]] — propiedad, control y proceso de limpieza.
- [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] — hallazgo de exposición cuando el objetivo es reclamable.
- [[cybersecurity/attack-surface-mapping/third-party-exposure|Exposición de terceros]]
- [[cybersecurity/offensive-security/subdomain-enumeration|Enumeración de subdominios]]
- [[tls-https|TLS/HTTPS]] — el comportamiento de HSTS y certificados puede amplificar el impacto del subdominio confiable.

### Notas atómicas futuras sugeridas
- [[provider-takeover-fingerprints|Fingerprints de takeover por proveedor]]
- [[stale-verification-records|Registros de verificación obsoletos]]
- [[cloud-storage-takeover|Takeover de almacenamiento en la nube]]
- [[cdn-custom-domain-takeover|Takeover de dominio custom de CDN]]
- [[dns-inventory-automation|Automatización del inventario de DNS]]
- [[safe-takeover-proof|Prueba segura de takeover]]

## Referencias
- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20
