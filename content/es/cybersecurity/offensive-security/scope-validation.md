# Scope Validation

## Definición

La scope validation es el proceso de confirmar qué assets descubiertos son propiedad del objetivo, están autorizados para testear y son apropiados para análisis adicional.

## Por qué importa

El recon produce ambigüedad. Sin scope validation, es fácil perder tiempo, testear el objetivo equivocado o confundir infraestructura administrada por vendors con la superficie propia de la organización.

Esta nota se mantiene acotada: es sobre los límites de ownership y testing autorizado, no sobre el descubrimiento amplio ni la validación técnica de servicios.

## Cómo funciona

La scope validation hace **5 preguntas de evidencia**:

1. **Ownership.** ¿Qué evidencia vincula el asset al objetivo?
2. **Autorización.** ¿Está en el scope escrito, el contrato o la aprobación interna?
3. **Entorno.** ¿Producción, staging, vendor, plataforma compartida o desconocido?
4. **Control.** ¿Controla el objetivo el contenido, la auth, el DNS o la infraestructura?
5. **Límites.** ¿Qué tests, tasas, cuentas, datos o técnicas están prohibidos?

El problema no es la incertidumbre. El error operacional es proceder con testing activo antes de resolver la incertidumbre.

Un ejemplo trabajado, asset ambiguo:

```
Asset:
  login-example.vendorcloud.com

Evidence:
  linked from example.test SSO docs; certificate is vendor-owned; page displays Example tenant name

Scope:
  program allows *.example.test but excludes third-party platform testing

Decision:
  test target-owned tenant configuration only if explicitly allowed;
  do not test vendor platform vulnerabilities
```

La scope validation es un control de seguridad, no papeleo.

## Técnicas / patrones

Los operadores validan usando:

- documentos de scope y reglas de bug bounty
- DNS, certificados, redirects y ownership del contenido
- links oficiales desde dominios confiables del objetivo
- pistas de vendor/plataforma
- mapeo legal/entidad y marca
- contacto con los owners del programa cuando hay ambigüedad

## Variantes y bypasses

La ambigüedad de scope aparece en **6 formas**.

### 1. Asset hosteado por vendor

El objetivo usa una plataforma de terceros pero no es dueño de la infraestructura del proveedor.

### 2. Infraestructura compartida

Las IPs de cloud, CDN o hosting sirven a múltiples tenants.

### 3. Marca adquirida o legacy

Los assets históricos pueden o no estar autorizados para testear.

### 4. Subdominio de cliente o tenant

Los nombres parecen relacionados pero pueden pertenecer a clientes o usuarios.

### 5. Superficie pública pero excluida

El asset es propiedad del objetivo pero está explícitamente excluido del testing.

### 6. Límite de control desconocido

Las pistas de DNS, contenido e identidad se contradicen o están incompletas.

## Impacto

Ordenado aproximadamente por severidad:

- **Riesgo legal/ético.** Testear sistemas fuera de scope puede dañar a terceros.
- **Esfuerzo desperdiciado.** El testing del objetivo equivocado produce hallazgos inutilizables.
- **Riesgo real perdido.** Una clasificación demasiado conservadora puede ocultar exposición propia.
- **Mejor reporting.** El scope validado crea evidencia más sólida y paths de remediación.

## Detección y defensa

Ordenado por efectividad:

1. **Validá el scope antes de tests activos o intrusivos.**
   La recolección pasiva puede generar pistas, pero el testing activo necesita claridad de autorización.

2. **Preservá evidencia para las decisiones de ownership.**
   Los reportes deberían mostrar por qué un asset se considera en scope.

3. **Usá niveles de confianza.**
   Los assets desconocidos deberían marcarse como desconocidos, no forzarse en in/out prematuramente.

4. **Escalá la ambigüedad al owner del programa.**
   Una clarificación breve supera a las suposiciones arriesgadas.

5. **Para defensores, publicá scope y contactos de seguridad más claros.**
   Un scope público claro reduce el testing accidental en el objetivo equivocado.

### Qué no funciona como defensa primaria

- **Similitud de nombre sola.** Los dominios similares no son prueba de ownership.
- **Ownership de IP compartida.** Las IPs de cloud y CDN no son assets del objetivo por defecto.
- **Asumir que todas las páginas hosteadas por vendors son testeables.** El scope puede incluir el contenido pero no los ataques a la plataforma.
- **Proceder porque un objetivo es público.** La alcanzabilidad pública no es permiso.

## Labs prácticos

Usá programas autorizados o assets internos.

### Construir una tabla de evidencia de scope

```
asset | evidencia | confianza de ownership | estado de scope | tests permitidos | notas
```

No avancés assets desconocidos a testing activo sin aprobación.

### Verificar linking oficial

```
¿Una página confiable del objetivo linkea a este host?
¿El DNS apunta desde una zona propiedad del objetivo?
¿El certificado incluye nombres controlados por el objetivo?
```

Múltiples señales aumentan la confianza.

### Separar proveedor de tenant

```
dig CNAME app.example.test +short
```

La infraestructura del proveedor puede estar fuera de scope incluso cuando el dominio custom está en scope.

### Escribir una pregunta de ambigüedad para el owner

```
Asset:
Evidencia:
Ambigüedad:
Test propuesto:
Impacto potencial en terceros:
Decisión necesaria:
```

Preguntar bien es más rápido que asumir mal.

### Marcar confianza antes de testear

```
en scope confirmado | probablemente en scope | desconocido | probablemente fuera de scope | excluido
```

Solo assets confirmados o explícitamente aprobados deberían avanzar a testing intrusivo.

## Ejemplos prácticos

- Un subdominio pertenece a una instancia SaaS de terceros en lugar de la infraestructura del objetivo.
- Una IP pública resuelve a una plataforma compartida y necesita confirmación de ownership.
- El dominio de una marca adquirida está activo pero no es parte del scope de testing actual.
- Un nombre de tenant de cliente se parece al objetivo pero está excluido.
- Un portal de soporte está en scope solo para configuración de tenant, no para testing de la plataforma vendor.

## Notas relacionadas

- [[company-mapping|Company Mapping]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[third-party-exposure|Third-Party Exposure]]
- [[external-attack-surface|Superficie de Ataque Externa]]
- [[recon-to-testing-handoff|Recon-to-Testing Handoff]]

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** HackerOne Disclosure Guidelines — https://www.hackerone.com/disclosure-guidelines
