# Company OSINT

## Definición

El Company OSINT es el uso de fuentes públicas para entender las marcas, dominios, productos, subsidiarias, vendors, tecnologías, contexto público de personas y huella digital expuesta de una organización. Es el modo OSINT que produce un **mapa de propiedad y superficie defendible** — el artefacto del que dependen la [[scope-validation|validación de scope]] y la [[external-attack-surface|superficie de ataque externa]] downstream.

## Por qué importa

Las empresas rara vez se exponen a través de un único dominio. Las páginas públicas, portales de soporte, publicaciones de trabajo, páginas de status, docs, CNAMEs de vendors, cuentas sociales, certificados e historial de adquisiciones describen la organización real. Tratar "el sitio de marketing principal" como el scope es la razón más común por la que los scopes se pierden exposición real.

El Company OSINT es el equivalente defensivo del reconocimiento del atacante. El mismo mapa que un atacante ensambla de fuentes públicas es el mapa que un defensor necesita para saber qué implica confianza para usuarios, partners y motores de búsqueda. Sin él, el scope es una suposición y la "confianza de terceros" es invisible.

El entregable es un mapa acotado y respaldado por evidencia sobre el que las ramas downstream pueden actuar:
- **La validación de scope** recibe una lista de confianza de propiedad antes de cualquier testing activo.
- **La superficie de ataque externa** recibe un inventario de dominio/vendor vinculado a evidencia de propiedad.
- **La exposición de terceros** recibe la lista de relaciones con vendors con calificaciones de calidad de evidencia.

## Cómo funciona

El Company OSINT extrae de **6 familias de pistas**. Un mapa útil cruza al menos tres de ellas por activo.

1. **Pistas de marca y producto.** Nombres de productos públicos, listados en app stores, dominios orientados al cliente, docs públicos, páginas de status, páginas de términos de servicio.
2. **Pistas legales y de propiedad.** Subsidiarias, adquisiciones, archivos corporativos, divulgaciones regulatorias, campos de entidad legal de términos de servicio, campos de organización "O=" de certificados.
3. **Pistas técnicas.** Stack, cloud provider, APIs, SDKs, nombres de paquetes, entradas de certificate transparency, registros ASN/BGP.
4. **Pistas de vendors.** Proveedores de soporte, identidad, analytics, status, CDN y SaaS — más visibles vía registros CNAME en subdominios y vía scripts de terceros referenciados.
5. **Pistas de personas.** Roles, equipos, contrataciones, maintainers públicos, contactos de seguridad. Usadas solo para contexto organizacional, con [[social-media-osint|reglas de minimización]] aplicadas.
6. **Pistas históricas.** Páginas archivadas, productos legacy, marcas antiguas, docs de soporte obsoletos, certificados vencidos pero publicados.

El bug es **no que exista el contexto público de la empresa**. La habilidad OSINT es **conectar pistas sin exagerar la propiedad** — una página hosted por vendor no es infraestructura del objetivo; un dominio de marca adquirida puede o no pertenecer aún al padre; un SAN de cert no prueba deployment.

Un ejemplo trabajado:

```
Pregunta:    Mapeá la superficie externa de Example Corp para validación de scope.
Pista de marca: sitio principal example.com, producto example.app, portal dev exampledev.com.
Pista legal: ToS lista "Example Corp Inc." como entidad legal; subsidiaria "ExSubsidiary Ltd." en archivos.
Técnica:    certificate transparency devuelve 47 nombres bajo example.com + 12 bajo exampledev.com.
Vendor:     cadena CNAME en support.example.com → zendesk; status.example.com → statuspage.io.
Personas:   LinkedIn muestra empleados de ExSubsidiary con afiliación al grupo "Example Corp" (corroboración).
Histórico:  archive.org revela legacy-brand.example.io aún resuelve a una página activa.
Salida:     mapa de propiedad con 3 dominios primarios verificados, 4 hosted por vendor (confianza de terceros), 1 legacy.
```

Cada entrada en el mapa lleva evidencia y una etiqueta de confianza, no una sola afirmación de fuente.

## Técnicas / patrones

La disciplina es "verificá la propiedad a través de al menos tres familias de pistas antes de promover a verificado".

- **Sitios web oficiales, términos, privacidad, status, páginas de soporte** — ancla para entidad legal y marca primaria.
- **Certificate transparency (`crt.sh`) y registros DNS** — fuente de inventario técnico primario.
- **Publicaciones de trabajo y blogs de ingeniería** — divulgan stack, cloud y estructura de equipo.
- **Repositorios públicos y registros de paquetes** — revelan convenciones de nomenclatura e identidades de maintainers.
- **Dominios personalizados hosted por vendor** — CNAMEs a `*.zendesk.com`, `*.statuspage.io`, `*.cloudfront.net`, `*.elasticbeanstalk.com` indican confianza de terceros.
- **Cuentas sociales y anuncios de productos** — ancla para marca actual y relaciones con vendors.
- **Historial de adquisiciones/marcas y páginas archivadas** — sacan a la superficie activos legacy que aún llevan confianza.

## Variantes y bypasses

El Company OSINT se agrupa en **5 clases de ambigüedad**. La mayoría de los errores de mapa son uno de estos.

### 1. Ambigüedad de marca

Los nombres de productos y marcas pueden no coincidir con entidades legales. "Example" la marca, "Example Corp Inc." la empresa, y "ExSubsidiary Ltd." el propietario legal de la mitad de la infraestructura pueden ser todos la misma organización — o no. Resolvé vía campos de entidad legal de términos de servicio, campos "O=" de certificados y archivos corporativos.

### 2. Ambigüedad de vendor

Las superficies hosted por vendors (`support.example.com` → Zendesk) llevan confianza del objetivo sin ser infraestructura propiedad del objetivo. Testear contra el host del vendor, no el objetivo. Evidencia: cadena CNAME, headers de respuesta, SANs de cert TLS específicos del vendor.

### 3. Desplazamiento de adquisición

Los activos y dominios viejos a menudo permanecen después de los cambios de propiedad — a veces durante años. El propietario actual puede no saber que existen. Evidencia: snapshots de archive.org, historial de entidad legal, línea temporal de certificados. El desplazamiento de adquisición es una fuente frecuente de exposición "espera, ¿eso sigue siendo nuestro?".

### 4. Ambigüedad de plataforma compartida

Las plataformas CDN, cloud y SaaS alojan muchos tenants. Una IP `*.cloudfront.net` sirve a miles de clientes; un endpoint de Elasticsearch en un cluster compartido no "pertenece" a un tenant. Resolvé vía comportamiento del Host-header, identificadores de tenant del vendor o confirmación de propiedad out-of-band.

### 5. Ambigüedad de contexto de personas

Los perfiles públicos pueden ser obsoletos, personales o no relacionados con el scope actual. Un perfil de LinkedIn listando "Example Corp" como empleador puede tener 5 años de antigüedad. Usá solo con corroboración; nunca uses como evidencia primaria de scope.

## Impacto

Ordenado aproximadamente por severidad:

- **Clarificación de scope.** La evidencia de propiedad guía el testing seguro en pentests y trabajo de bug bounty; la alternativa son errores de objetivo incorrecto.
- **Descubrimiento de activos públicos.** Las marcas, vendors y adquisiciones revelan dominios y servicios que no están en ningún inventario interno.
- **Mapeo de exposición de terceros.** Los proveedores SaaS e identidad se vuelven visibles como parte de la superficie de confianza.
- **Apuntado de tecnología.** Las publicaciones de trabajo, blogs de ingeniería y repositorios públicos revelan elecciones de stack que impulsan la priorización.
- **Descubrimiento de activos obsoletos.** Las marcas legacy y páginas archivadas revelan sistemas olvidados que llevan confianza actual.

## Detección y defensa

Las defensas se agrupan alrededor de **mantener el propio mapa externo de la empresa** con etiquetas de confianza.

1.
**Mantené un mapa de empresa orientado al exterior.**
   Los defensores deberían saber qué marcas, vendors y dominios implican confianza. El mapa debería coincidir con lo que construiría un atacante, mantenido al día.

2.
**Publicá scope de seguridad y contactos claros.**
   `security.txt`, una página de seguridad y un scope de bug-bounty/divulgación declarado reducen la ambigüedad para investigadores y equipos internos. Ver [[email-and-phone-osint]].

3.
**Limpiá señales públicas obsoletas.**
   Los docs viejos, páginas de soporte deprecated, dominios de productos expirados y entornos de staging archivados siguen expandiendo la superficie percibida mucho después de que el equipo que los construyó se fue.

4.
**Revisá las publicaciones de trabajo y docs en busca de detalles técnicos innecesarios.**
   La contratación pública puede ser útil sin compartir arquitectura sensible en exceso. "Usamos Kubernetes" está bien; "nuestro auth usa el módulo X versión Y en el cluster Z" no lo está.

5.
**Usá niveles de confianza para la propiedad.**
   No tratés una pista como prueba. El mapa debería tener columnas verificado / probable / incierto / hosted-por-vendor con evidencia por fila.

### Qué no funciona como defensa primaria

- **Asumir que el sitio web principal es la empresa.** Las marcas, vendors y adquisiciones expanden el contexto mucho más allá de él.
- **Asumir que la infraestructura compartida prueba propiedad.** Las plataformas compartidas (CDN, cloud, SaaS) alojan muchos tenants; "servido desde cloudfront.net" no es evidencia de propiedad.
- **Ignorar adquisiciones viejas.** Los activos legacy a menudo persisten mucho después de que se completan las adquisiciones; llevan confianza actual hasta que se descomisionen.
- **Tratar perfiles de personas como scope técnico.** Los roles son contexto organizacional, nunca autorización para testear sistemas.
- **Confiar solo en campos de organización WHOIS.** Los servicios de privacidad y las registraciones obsoletas hacen que WHOIS sea poco confiable como fuente de propiedad única.

## Labs prácticos

Usá una empresa pública que seas dueño, un scope autorizado o un objetivo de entrenamiento benigno.

### Construí un mapa de empresa

```
marca          | dominio              | evidencia                        | confianza de propiedad | activos relacionados  | notas
example.com    | example.com          | entidad legal ToS + cert O=       | verificado             | 47 nombres cert SAN   | primario
exampledev.com | exampledev.com       | referencia ToS + cadena cert     | verificado             | 12 nombres cert SAN   | portal dev
soporte        | support.example.com  | CNAME → zendesk                  | hosted-por-vendor      | n/a                   | confianza de terceros
status         | status.example.com   | CNAME → statuspage.io            | hosted-por-vendor      | n/a                   | confianza de terceros
marca-legacy   | legacy-brand.example.io | archive.org 2018-2024, DNS A actual | probable          | 3 nombres cert SAN    | desplazamiento de adquisición
```

El mapa es el entregable. Las etiquetas de confianza son cargadas.

### Extraé relaciones de vendors de CNAMEs

```
while read host; do
  cname=$(dig CNAME "$host" +short)
  [ -n "$cname" ] && echo "$host -> $cname"
done < subdominios.txt | tee vendor-cnames.txt

# Luego resumir vendors
awk '{print $3}' vendor-cnames.txt | sed 's/\.$//; s/.*\.//' | sort | uniq -c | sort -rn
```

Los mapeos de vendors alimentan la revisión de [[third-party-exposure|third-party exposure]].

### Cross-corroborá la propiedad

```
Fuente 1: campo "O=" del certificado    → "Example Corp, Inc."
Fuente 2: entidad legal de términos de servicio → "Example Corp, Inc."
Fuente 3: snapshot más antiguo de archive.org  → 2014, branding consistente con actual
Fuente 4: organización WHOIS (si visible)→ "Example Corp"
Decisión: propiedad verificada; promover al mapa.
```

Tres fuentes independientes promueven la propiedad de "probable" a "verificado".

### Revisá pistas de tecnología pública sin exagerar

```
fuente                      | pista de tecnología               | confianza | relevancia de seguridad    | próxima acción
publicación de trabajo 2026-03 | "experiencia con Spring Boot"  | media     | sugiere stack Java/Spring  | corroborar vía headers
blog de ingeniería 2025-11  | "corremos en Kubernetes / GCP"    | alta      | cloud + orquestación       | enfocar revisiones GCP
commit público 2026-04      | patrón de email de maintainer     | alta      | patrón email + identidad   | alimentar mapa de patrón email
página de status marca adquirida | lista de vendors (Datadog, Auth0) | alta | inventario de vendors    | alimentar mapa de terceros
```

Las pistas de fuente única no se convierten en "verificado" sin corroboración.

### Auditá el desplazamiento de adquisición

```
adquisición | entidad adquirida | fecha de adquisición | activos conocidos | activos desconocidos-pero-encontrados
2019        | LegacyBrand Inc.  | 2019-Q3              | 2 dominios        | 3 dominios adicionales vía búsqueda de cert
2022        | TinyTool Ltd.     | 2022-Q1              | 1 app SaaS        | 1 dominio de staging aún resolviendo
```

El desplazamiento de adquisición es el hallazgo más común de "no sabíamos que todavía teníamos esto".

## Ejemplos prácticos

- Una página de status revela nombres de servicios, regiones y vendors dependientes que ninguna especificación pública divulga.
- Las publicaciones de trabajo revelan elecciones de cloud y framework que estrechan el scope de testing activo.
- Los CNAMEs de vendors identifican proveedores de soporte e identidad, exponiendo relaciones de confianza de terceros.
- Una marca adquirida sigue teniendo infraestructura activa que la organización padre había olvidado.
- Los repositorios públicos revelan convenciones de nomenclatura de paquetes que coinciden con nombrado interno visible en otro lado.
- Certificate transparency revela un patrón de subdominio de staging no anunciado, sacando a la superficie la superficie pre-lanzamiento.

## Notas relacionadas

- [[osint]]
- [[osint-triage]]
- [[social-media-osint]]
- [[email-and-phone-osint]]
- [[company-mapping|Company Mapping]]
- [[scope-validation|Scope Validation]]
- [[third-party-exposure|Third-Party Exposure]]

### Notas atómicas futuras sugeridas

- brand-domain-inventory
- job-posting-osint
- vendor-relationship-mapping
- acquisition-surface-mapping
- public-repository-osint
- ownership-confidence-grading

## Referencias

- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
