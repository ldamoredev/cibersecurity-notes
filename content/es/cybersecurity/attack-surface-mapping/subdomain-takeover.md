# Subdomain Takeover

## Definición

El subdomain takeover es una condición de exposición donde un nombre DNS apunta a infraestructura o una relación de servicio de terceros que ya no existe, permitiendo que otra parte reclame el objetivo y sirva contenido bajo el subdominio de confianza.

## Por qué importa

El subdomain takeover es la deriva del ciclo de vida de activos hecha visible. El dominio sigue siendo confiado por usuarios, navegadores, cookies, reglas CORS, redirecciones OAuth, allowlists y expectativas de marca, pero el servicio de respaldo fue eliminado o abandonado.

[[dangling-dns-records|Dangling DNS Records]] es propietario del mecanismo de higiene DNS. Esta nota es propietaria del hallazgo de superficie de ataque: si un mapeo colgante es reclamable y relevante para la seguridad.

## Cómo funciona

El takeover requiere **4 condiciones**:

1. **Existe un subdominio de confianza.** Ejemplo: `help.example.test`.
2. **El DNS apunta a un objetivo externo o desaprovisionado.** Usualmente CNAME, ALIAS o mapeo de servicio cloud-hosted.
3. **El objetivo no está reclamado o es reclamable.** El provider permite que una nueva cuenta cree el recurso faltante.
4. **El subdominio tiene valor de confianza.** Los usuarios, cookies, OAuth, CORS, CSP, links, correo o confianza de marca hacen que el control sea significativo.

El bug no es solo un registro DNS obsoleto. Es un nombre obsoleto más un servicio de respaldo reclamable más confianza adjunta al nombre.

Un ejemplo trabajado, de DNS obsoleto a severidad:

```
Nombre:
  help.example.test

DNS:
  CNAME old-helpdesk.vendor.example

Comportamiento HTTP:
  el provider devuelve "project not found"

Reclamabilidad:
  los docs del provider dicen que el dominio personalizado debe estar vinculado antes de servir tráfico

Amplificación de confianza:
  los emails de restablecimiento de contraseña enlazan a artículos de help.example.test, pero ninguna cookie ni redirect OAuth lo usa

Triaje:
  riesgo probable de takeover de marca/contenido, menor que compromiso de cuenta a menos que se encuentren rutas de confianza
```

La decisión madura no es "takeover sí/no"; es reclamabilidad más amplificación de confianza más prueba segura.

## Técnicas / patrones

Los profesionales buscan:

- CNAMEs a providers SaaS/cloud que devuelven errores "not found" o "no such app"
- apps cloud eliminadas sin limpieza DNS
- subdominios de marketing, docs, soporte, preview y staging
- registros de onboarding de vendor viejos y tokens de verificación
- nombres incluidos en allowlists de redirect OAuth, allowlists CORS, cookies o CSP
- nombres de certificate transparency con CNAMEs específicos del provider

## Variantes y bypasses

El subdomain takeover aparece en **6 formas**.

### 1. Recurso cloud eliminado

El nombre DNS apunta a un recurso Heroku, Azure, Netlify, Vercel, S3/sitio estático o similar eliminado.

### 2. Plataforma SaaS abandonada

Un mapeo de soporte, docs, estado, marketing o ticketing permanece después del offboarding.

### 3. Binding de custom domain huérfano

El provider ya no tiene un binding válido de propietario para el dominio personalizado.

### 4. Artefacto de verificación obsoleto

Los artefactos de verificación TXT o CNAME permanecen y pueden ayudar a reclamar o validar ownership en otro lugar.

### 5. Wildcard DNS o routing compartido del provider

El DNS wildcard o el routing compartido del provider envía muchos nombres a recursos reclamables.

### 6. Amplificación de confianza

El takeover se vuelve más severo porque cookies, CORS, OAuth, CSP, links o confianza del usuario incluyen el subdominio.

## Impacto

Ordenado aproximadamente por severidad:

- **Ruta de compromiso de cuenta.** Los redirects OAuth, links de restablecimiento de contraseña o cookies de confianza interactúan con el subdominio controlado.
- **Phishing y abuso de marca.** El atacante sirve contenido de aspecto confiable en un subdominio real.
- **Robo de datos o tokens.** Las cookies excesivamente amplias, CORS o redirecciones filtran material sensible.
- **Falla de integridad de contenido.** Docs, descargas, scripts o páginas de soporte pueden ser reemplazados.
- **Pivot de reconocimiento.** El takeover confirma la debilidad del ciclo de vida de activos y puede revelar otros mapeos obsoletos.

## Detección y defensa

Ordenado por efectividad:

1.
**Vinculás la limpieza DNS al desaprovisionamiento de recursos.**
   Eliminar una app cloud o integración SaaS debería quitar los dominios personalizados y registros DNS en el mismo flujo de trabajo.

2.
**Escaneás continuamente los destinos DNS por estados reclamables específicos del provider.**
   Los registros obsoletos aparecen después de cambios de negocio normales, no solo durante las migraciones.

3.
**Rastreás la propiedad de custom domains de terceros.**
   El inventario debería saber qué provider tiene cada mapeo y cómo se verifica la propiedad.

4.
**Reducís la confianza adjunta a subdominios amplios.**
   Evitá cookies excesivamente amplias, CORS, redirects OAuth y reglas CSP que incluyan muchos subdominios.

5.
**Verificás los takeovers sospechosos de forma segura.**
   En bug bounty o testing interno, seguí los métodos de prueba seguros del provider y evitá servir contenido engañoso.

### Qué no funciona como defensa primaria

- **Eliminar solo el recurso backend.** El DNS puede seguir apuntando al objetivo ahora reclamable.
- **Asumir que todos los registros colgantes son explotables.** La reclamabilidad depende del comportamiento del provider y los chequeos de propiedad.
- **Confianza wildcard.** `*.example.com` en cookies, CORS, CSP u OAuth puede amplificar un solo nombre obsoleto.
- **Revisión DNS manual una vez al año.** Los registros obsoletos aparecen continuamente.

## Labs prácticos

Usá dominios propios o scope explícito de bug bounty.

### Inspeccioná CNAMEs de subdominios

```
dig CNAME help.example.test +short
dig CNAME docs.example.test +short
```

Registrá destinos del provider y propietarios esperados.

### Verificá los mensajes de error del provider

```
curl -i https://help.example.test/
```

Buscá mensajes de no reclamado o proyecto faltante específicos del provider, luego confirmá contra la documentación del provider.

### Verificá rutas de confianza

```
curl -I https://app.example.test/ | rg -i "set-cookie|access-control|content-security-policy"
```

Las cookies, CORS y CSP pueden hacer un takeover más severo.

### Escaneá subdominios a escala

```
while read host; do
  curl -m 5 -ks -I "https://$host" | head -n 1 | sed "s|^|$host |"
done < subdomains.txt
```

Usá bajo volumen y scope propio.

### Construí una tabla de evaluación de takeover

```
host | destino DNS | provider | texto de error | evidencia de reclamabilidad | rutas de confianza | confianza
```

Las páginas de error del provider solas no son suficientes; combinalas con el comportamiento del provider y evidencia de confianza.

### Auditá rutas de confianza de cookies y OAuth

```
Atributos Domain de cookies:
URIs de redirect OAuth:
Orígenes permitidos por CORS:
Fuentes script/connect/frame CSP:
Links de restablecimiento de contraseña:
```

Estos deciden si un subdominio obsoleto es solo riesgo de contenido o una ruta de riesgo de cuenta.

## Ejemplos prácticos

- Un subdominio sigue apuntando a una app cloud eliminada.
- Un hostname de integración SaaS permanece activo en DNS después del offboarding.
- Un hunter de bug bounty reclama un mapeo de servicio obsoleto y sirve contenido de prueba.
- Una allowlist OAuth incluye un subdominio propenso a takeover.
- Un dominio de cookie amplio envía cookies a un subdominio controlado.

## Notas relacionadas

- [[dangling-dns-records|Dangling DNS Records]]
- [[dns-security|DNS Security]]
- [[third-party-exposure]]
- [[external-attack-surface]]
- [[subdomain-enumeration|Subdomain Enumeration]]

### Notas atómicas futuras sugeridas

- provider-specific-takeover-fingerprints
- custom-domain-ownership
- oauth-redirect-subdomain-risk
- wildcard-cookie-risk
- safe-takeover-proof

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery guide to DNS takeovers / subdomain takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
