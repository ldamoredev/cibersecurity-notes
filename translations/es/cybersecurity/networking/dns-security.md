---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - dns
  - ownership
sources: []
---

# Seguridad de DNS

## Definición
La seguridad de DNS es la disciplina de mantener confiable la capa de nombres: los dominios y subdominios deberían resolver solo a destinos previstos, estar controlados por dueños previstos, resistir spoofing o takeover, y no exponer más superficie de ataque que la que la organización pretende publicar.

## Por qué importa
DNS es donde la arquitectura se vuelve descubrible. Incluso cuando la aplicación está bien construida, DNS puede revelar sistemas de staging, apuntar esquivando un CDN, delegar confianza a vendors olvidados, debilitar la identidad de email o dejar registros propensos a takeover. Una zona DNS desprolija suele ser un mapa de propiedad de activos desprolija.

Esta nota es dueña de la propiedad y el control de DNS. [[dns-resolution|Resolución DNS]] es dueña de la mecánica del lookup. [[dangling-dns-records|Registros DNS colgantes]] es dueña de los mapeos nombre-objetivo obsoletos. [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] es dueña del hallazgo concreto de exposición.

## Cómo funciona
La seguridad de DNS se controla a través de **5 fronteras de propiedad**:

1. **Propiedad del registrar.** Quién puede renovar, transferir, bloquear o cambiar el registro del dominio.
2. **Propiedad del DNS autoritativo.** Quién controla los nameservers y los registros de la zona.
3. **Propiedad de los registros.** Qué equipo es dueño de cada hostname, tipo de registro, objetivo y ciclo de vida.
4. **Propiedad del proveedor.** A qué proveedor de nube, CDN, SaaS, almacenamiento o mail le delega el registro el tráfico o la prueba de control.
5. **Frontera de confianza del cliente.** Si los clientes y resolvers pueden confiar en que la respuesta que reciben no fue spoofeada, envenenada ni degradada.

Forma de ejemplo de alto riesgo:

```txt
support.example.com. 300 IN CNAME example-support.zendesk.com.
_amazonses.example.com. 300 IN TXT "old-verification-token"
example.com. 300 IN CAA 0 issue ";"
```

Interpretación de seguridad:

- `support.example.com` depende del ciclo de vida de un tenant de terceros.
- los tokens viejos de verificación pueden preservar prueba de control en servicios externos.
- una política CAA restrictiva o rota afecta la emisión de certificados.
- el registro DNS no es solo "un puntero"; es una delegación de confianza.

El bug suele vivir donde la propiedad del DNS sobrevive al sistema o relación con el vendor para el que fue creado.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- el lock del registrar, MFA, propiedad de la cuenta y postura de renovación del dominio
- los proveedores de nameservers autoritativos y las cadenas de delegación
- registros `CNAME`, `A`, `AAAA`, `NS`, `MX` y `TXT` obsoletos
- mapeos de dominio custom de SaaS de terceros y registros de verificación
- fingerprints de takeover en las páginas de error de proveedores
- registros SPF, DKIM y DMARC faltantes o débiles
- registros CAA ausentes o demasiado amplios
- presencia de DNSSEC, estado de delegación y fallas de validación
- registros wildcard que esconden inventario real
- diferencias de DNS split-horizon entre vistas públicas, internas, VPN y de nube

## Variantes y bypasses
Las fallas de seguridad de DNS caen en **7 clases prácticas**.

### 1. Compromiso o mala gestión del registrar
Si la cuenta del registrar es débil, un atacante puede cambiar nameservers, transferir dominios o secuestrar el dominio en la raíz de confianza. El MFA, el registry lock y una propiedad de cuenta estricta importan antes que cualquier configuración de registro individual.

### 2. Deriva del control del DNS autoritativo
Proveedores de DNS viejos, zonas hospedadas olvidadas, zonas en la sombra y delegación inconsistente hacen poco clara la fuente de verdad. Si dos equipos pueden publicar registros en conflicto, la respuesta a incidentes se vuelve adivinanza.

### 3. Registros colgantes y objetivos reclamables
DNS apunta a un objetivo externo que ya no existe o ya no está reclamado. El registro obsoleto puede volverse un [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] si un atacante puede registrar el recurso de respaldo.

### 4. Residuo de verificación de terceros
Los registros TXT de verificación de SaaS, propiedad de dominio, proveedores de mail, herramientas de analytics y servicios de nube a menudo quedan tras el offboarding. Algunos proveedores tratan los tokens viejos como prueba continua de control.

### 5. Mala configuración de identidad de mail
SPF débil, DKIM faltante, DMARC permisivo y registros MX olvidados hacen más fácil el phishing y el spoofing. La seguridad de DNS incluye la identidad de mail porque la confianza del email es la confianza del dominio.

### 6. Huecos de control en la emisión de certificados
Registros CAA faltantes o amplios permiten que más autoridades de certificación emitan para un dominio de lo previsto. Una propiedad de DNS débil también puede habilitar validación de dominio fraudulenta si un atacante controla un subdominio o un camino de registro.

### 7. Fallas de confianza en resolver y caché
El spoofing de DNS, el envenenamiento de caché, los resolvers locales maliciosos y las respuestas sin firmar pueden rutear clientes al destino equivocado. DNSSEC ayuda donde está desplegado correctamente, pero la higiene operativa sigue importando.

## Impacto
Ordenado aproximadamente por severidad:

- **Secuestro de dominio o subdominio.** Fallas del registrar, del DNS autoritativo o de registros colgantes dejan a un atacante servir contenido bajo nombres confiables.
- **Intercepción de tráfico o robo de credenciales.** Respuestas DNS cambiadas pueden rutear usuarios, clientes de API o mail hacia infraestructura controlada por el atacante.
- **Phishing y abuso de marca.** Registros de mail débiles y subdominios propensos a takeover hacen el spoofing más creíble y más difícil de filtrar.
- **Bypass de seguridad de edge.** Registros de origin directos o DNS obsoleto pueden saltear controles de CDN/WAF/reverse-proxy.
- **Abuso de tenants de nube/SaaS.** Registros de verificación viejos o mapeos de dominio custom pueden preservar confianza no deseada en sistemas de terceros.
- **Falla del inventario de activos.** Registros DNS desconocidos esconden sistemas del parcheo, monitoreo y revisión de propiedad.
- **Demora en la respuesta a incidentes.** TTLs largos, autoridad poco clara o múltiples proveedores de DNS ralentizan la contención.

## Detección y defensa
Ordenado por efectividad:

1. **Protegé primero las cuentas del registrar y del DNS autoritativo.**
   Imponé MFA, mínimo privilegio, registry lock donde esté disponible, monitoreo de renovación y dueños nombrados. Si un atacante puede cambiar nameservers o registros de zona, los controles aguas abajo son decoración.

2. **Hacé obligatorio el inventario de propiedad de DNS.**
   Cada registro debería tener un dueño, propósito, objetivo esperado, proveedor, fecha de creación y condición de retiro. La metadata de propiedad convierte la limpieza de arqueología en operaciones normales.

3. **Automatizá la revisión de registros obsoletos y objetivos de terceros.**
   Compará continuamente los registros DNS contra los inventarios de nube/SaaS. Marcá registros que apunten a buckets borrados, load balancers, app services, distribuciones de CDN, tenants de SaaS u objetivos de proveedor no reclamados.

4. **Atá la limpieza de DNS al deprovisioning.**
   El mismo cambio que borra un servicio debería remover o estacionar su DNS. Esto cierra el hueco donde el ciclo de vida de la infraestructura y el del naming se separan.

5. **Endurecé los registros de control de mail y certificados.**
   Usá SPF con includes ajustados, firma DKIM, DMARC con enforcement (`p=quarantine` o `p=reject` tras el monitoreo) y registros CAA que listen las CAs previstas. Estos registros protegen la confianza del dominio más allá del tráfico web.

6. **Usá DNSSEC donde esté soportado operativamente.**
   DNSSEC provee integridad para las respuestas DNS cuando el resolver la valida y la zona está firmada correctamente. Ayuda contra las clases de spoofing/cache-poisoning, pero no previene registros obsoletos, malos objetivos ni mapeos de SaaS propensos a takeover.

7. **Monitoreá el DNS público y la certificate transparency.**
   Alertá ante nuevos subdominios, cambios de nameserver, cambios de MX, cambios de CAA y emisión inesperada de certificados. Los cambios de DNS son eventos de seguridad de alta señal.

### Qué no funciona como defensa primaria

- **"El dominio parece interno".** Los nombres no imponen alcanzabilidad ni autorización. `admin.internal.example.com` es interno solo si el camino de red y la vista de DNS lo hacen así.
- **DNSSEC como arreglo de takeover.** DNSSEC puede probar que el registro obsoleto es auténtico; no prueba que el objetivo siga siendo propio.
- **Revisión manual anual de DNS.** Los registros derivan cada vez que los equipos despliegan, migran, prueban vendors o decomisionan infraestructura. La revisión anual encuentra fósiles.
- **Borrar la infraestructura antes que el DNS.** Esto crea exactamente la ventana colgante que los atacantes quieren. Remové o estacioná el DNS como parte del mismo cambio.
- **Confiar en registros wildcard para simplificar operaciones.** Los wildcards pueden enmascarar inventario faltante, hacer ruidosa la enumeración y rutear nombres inesperados a infraestructura real.
- **Asumir que las páginas de error de proveedores son inofensivas.** Muchos flujos de takeover empiezan desde páginas "not found" específicas del proveedor que revelan un objetivo reclamable.

## Labs prácticos
Corré esto contra dominios que sean tuyos o que tengas permiso para revisar.

### Inventariar el control autoritativo

```bash
domain=example.com
dig +short "$domain" NS
whois "$domain" | rg -i 'registrar|name server|status|expiry|expiration|updated'
```

Buscá lock/status del registrar, nameservers inesperados, proveedores de DNS viejos y riesgo de renovación.

### Barrer tipos de registro de alto riesgo

```bash
domain=example.com
for type in A AAAA CNAME MX TXT NS CAA; do
  printf '\n== %s ==\n' "$type"
  dig +short "$domain" "$type"
done

dig +short "_dmarc.$domain" TXT
dig +short "selector1._domainkey.$domain" TXT
```

Esto da una foto rápida de la postura de web, mail, verificación, delegación y control de certificados.

### Chequear la postura de identidad de mail

```bash
domain=example.com
dig +short "$domain" TXT | rg -i 'v=spf1'
dig +short "_dmarc.$domain" TXT

# Si conocés los selectores DKIM, chequealos explícitamente.
dig +short "default._domainkey.$domain" TXT
dig +short "selector1._domainkey.$domain" TXT
```

Buscá SPF faltante, `~all` o `?all` durante operación madura, DMARC faltante, o `p=none` que nunca graduó a enforcement.

### Detectar mapeos de SaaS y nube obsoletos

```bash
while read -r name; do
  target=$(dig +short "$name" CNAME | tail -n1)
  if [ -n "$target" ]; then
    printf '%-40s -> %s\n' "$name" "$target"
    curl -skI "https://$name" | sed -n '1,8p'
  fi
done < subdomains.txt
```

Los mensajes 404 o "no such app/bucket/site" específicos del proveedor deberían derivar a [[dangling-dns-records|Registros DNS colgantes]] y [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]].

### Chequear CAA y emisión inesperada de certificados

```bash
domain=example.com
dig +short "$domain" CAA

# Certificate Transparency vía la API JSON de crt.sh.
curl -s "https://crt.sh/?q=%25.$domain&output=json" \
  | jq -r '.[].name_value' 2>/dev/null \
  | tr '\n' '\n' \
  | sort -u
```

Compará los nombres y CAs emitidos contra los proveedores esperados. Los certificados inesperados a menudo revelan hosts olvidados o caminos de emisión no autorizados.

### Comparar vistas públicas e internas

```bash
name=admin.example.com
for resolver in 1.1.1.1 8.8.8.8 9.9.9.9; do
  printf '%s public -> ' "$resolver"
  dig @"$resolver" +short "$name" A
done

printf 'local resolver -> '
dig +short "$name" A
```

Corré el test del resolver local desde contextos de VPN, red de oficina, VM de nube y contenedor cuando estén en alcance. Las sorpresas de split-horizon son comunes.

### Verificar el estado de DNSSEC

```bash
domain=example.com
dig +dnssec "$domain" SOA
dig +short DS "$domain"
```

DNSSEC es útil solo si la zona está firmada, la delegación es correcta y los validadores pueden construir una cadena de confianza.

## Ejemplos prácticos
- Una cuenta de registrar no tiene MFA; una cuenta de email comprometida puede transferir el dominio o cambiar nameservers.
- Un microsite de marketing retirado deja `campaign.example.com CNAME vendor.example.net`; el objetivo del vendor se vuelve reclamable.
- `_amazonses.example.com` o registros TXT viejos de SaaS quedan después de que termina la relación con el proveedor.
- DMARC queda en `p=none` durante años, permitiendo que el mail spoofeado pase con mínimo enforcement del receptor.
- Una nueva migración de CDN deja `origin.example.com` resoluble y alcanzable públicamente fuera del WAF.
- Una zona hospedada privada resuelve `api.example.com` a `10.0.0.12`, mientras el DNS público lo resuelve al CDN. Un SSRF dentro de la VPC sigue el camino interno.

## Notas relacionadas
- [[dns-resolution|Resolución DNS]] — mecánica del lookup, alias, puntos de vista del resolver y comportamiento de TTL.
- [[dangling-dns-records|Registros DNS colgantes]] — objetivos DNS obsoletos y fallas de ciclo de vida.
- [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] — hallazgo de exposición cuando un objetivo colgante es reclamable.
- [[cybersecurity/attack-surface-mapping/external-attack-surface|Superficie de ataque externa]] — DNS como capa de descubribilidad pública.
- [[tls-https|TLS/HTTPS]] — registros CAA, emisión de certificados y validación de dominio.
- [[cybersecurity/networking/reverse-proxies|Reverse proxies]] — el DNS a menudo apunta a los usuarios al edge que impone los controles de proxy.
- [[cybersecurity/web-security/ssrf|SSRF]] — el contexto del resolver y el DNS rebinding afectan los riesgos de fetch de URL.

### Notas atómicas futuras sugeridas
- [[registrar-security|Seguridad del registrar]]
- [[dnssec|DNSSEC]]
- [[spf-dkim-dmarc|SPF, DKIM, DMARC]]
- [[caa-records|Registros CAA]]
- [[dns-monitoring|Monitoreo de DNS]]
- [[dns-rebinding|DNS rebinding]]
- [[third-party-domain-verification|Verificación de dominio de terceros]]

## Referencias
- **Foundational:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Foundational:** ICANN DNSSEC — https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en
- **Mitigation:** CISA Domain Name System Security Best Practices — https://www.cisa.gov/resources-tools/resources/domain-name-system-dns-security-best-practices
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20
