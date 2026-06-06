# Company Mapping

## Definición

El company mapping es el proceso de conectar dominios, marcas, subsidiarias, adquisiciones, vendors, identidades públicas, productos y pistas de infraestructura en un modelo coherente de lo que un objetivo realmente opera o en lo que confía.

## Por qué importa

Muchos objetivos no existen como un único namespace prolijo. Las marcas, dominios regionales, empresas adquiridas, portales de soporte, flujos de login hosteados por vendors, proyectos cloud y naming histórico pueden hacer que la superficie real sea más grande de lo que sugiere la página principal oficial.

Esta nota es sobre ownership y forma organizacional, no sobre recolección de assets en bruto o validación de servicios.

## Cómo funciona

El company mapping usa **5 tipos de relaciones**:

1. **Relación legal.** Empresa madre, subsidiaria, adquisición, marca, entidad regional.
2. **Relación de naming.** Dominios, nombres de productos, dominios de email, nombres de apps, nombres de paquetes.
3. **Relación de infraestructura.** DNS, certificados, ASNs, cuentas cloud, hosting compartido, CDNs.
4. **Relación con vendors.** Portales de soporte, docs, identidad, analytics, status, CRM, CI/CD y SaaS.
5. **Relación de personas.** Empleados, roles, ofertas de trabajo, perfiles sociales, contactos de soporte, maintainers públicos.

El error no es saber que una empresa tiene vendors o marcas. El riesgo es clasificar mal el ownership y ya sea perderse superficie real o testear superficie sin relación.

Un ejemplo trabajado, confianza en la relación:

```
Candidate asset:
  support.oldbrand.example

Legal clue:
  oldbrand was acquired by Example Inc. in 2023

Technical clue:
  CNAME points to support SaaS, page uses Example logo

Official clue:
  example.test/help links to support.oldbrand.example

Decision:
  high-confidence related surface; validate scope and vendor boundaries before active tests
```

El company mapping se vuelve confiable cuando la evidencia legal, técnica y de links oficiales coinciden.

## Técnicas / patrones

Los operadores recolectan:

- dominios oficiales, páginas de productos, docs de soporte y páginas legales
- nombres en certificados y relaciones DNS
- ofertas de trabajo y pistas tecnológicas
- repositorios públicos y metadata de paquetes
- dominios custom hosteados por vendors
- pistas de perfiles sociales y profesionales
- historial de adquisiciones y marcas

## Variantes y bypasses

El company mapping tiene **6 clases de ambigüedad**.

### 1. Ambigüedad de subsidiaria y marca

Los assets pueden pertenecer a marcas adquiridas o regionales en lugar del dominio padre obvio.

### 2. Ambigüedad de hosting por vendor

El objetivo puede controlar contenido o auth en un dominio hosteado por un vendor sin ser dueño de la infraestructura del proveedor.

### 3. Ambigüedad de infraestructura compartida

Las IPs de cloud, CDN y hosting compartido pueden alojar muchos tenants sin relación.

### 4. Ambigüedad de ownership histórico

Los assets viejos pueden permanecer de adquisiciones, migraciones o productos abandonados.

### 5. Ambigüedad de empleados y contratistas

Los datos de personas ayudan al contexto pero no deberían tratarse como scope técnico por sí solos.

### 6. Ambigüedad de open-source/proyecto

Los repos y paquetes públicos pueden ser oficiales, personales, forkeados o abandonados.

## Impacto

Ordenado aproximadamente por severidad:

- **Errores de scope.** Testear assets equivocados crea riesgo legal y ético.
- **Exposición omitida.** Las marcas adquiridas y superficies de vendors pueden llevar confianza real.
- **Mejor descubrimiento de takeovers.** Los mappings de marca/vendor obsoletos suelen revelar drift.
- **Mejor modelado social/contextual.** Los datos públicos de personas y procesos explican los sistemas probables.
- **Mejora de inventario.** Los equipos defensivos ven cómo los de afuera infieren el ownership.

## Detección y defensa

Ordenado por efectividad:

1. **Mantené un mapa de ownership público.**
   Las marcas, dominios, vendors y superficies con hosting custom deberían ser trazables hasta sus dueños.

2. **Publicá scope de seguridad claro donde corresponda.**
   Las páginas de bug bounty y contacto de seguridad deberían reducir la ambigüedad.

3. **Limpiá señales obsoletas de marcas y vendors.**
   Los dominios viejos, portales de soporte y docs siguen implicando ownership.

4. **Evitá compartir demasiado sobre la estructura interna en artefactos públicos.**
   Las ofertas de trabajo y docs pueden ser útiles sin filtrar detalles innecesarios.

5. **Validá ownership antes del testing activo.**
   El company mapping alimenta la validación de scope; no la reemplaza.

### Qué no funciona como defensa primaria

- **Asumir que la similitud en el nombre prueba ownership.** Buscá múltiples señales de respaldo.
- **Asumir que una IP compartida significa el mismo objetivo.** Las plataformas compartidas alojan tenants sin relación.
- **Tratar las superficies de vendors como fuera de vista.** Igual pueden llevar confianza del objetivo.
- **Ignorar marcas viejas.** Los assets históricos suelen persistir.

## Labs prácticos

Usá datos públicos y mantente dentro de los límites éticos.

### Construir una tabla de relaciones

```
name | relationship type | evidence | confidence | next validation
```

Requerí evidencia antes de agregar assets al scope de testing.

### Buscar links de dominio oficial

```
site:example.test "privacy" "terms"
site:example.test "support"
site:example.test "status"
```

Las páginas legales/de soporte suelen identificar vendors y marcas.

### Mapear CNAMEs de vendors

```
while read host; do dig CNAME "$host" +short | sed "s|^|$host -> |"; done < subdomains.txt
```

Los mappings de vendors ayudan a identificar relaciones de confianza.

### Construir una escala de confianza de ownership

```
asset | legal evidence | official link | DNS/cert evidence | content evidence | confidence
```

Usá niveles de confianza en lugar de ownership binario cuando la evidencia es incompleta.

### Rastrear el drift de adquisiciones

```
brand | acquired by | old domains | live hosts | redirects | scope status
```

Las marcas adquiridas son una fuente común de superficie olvidada pero real.

## Ejemplos prácticos

- Múltiples dominios de productos mapean a la misma empresa.
- Los portales de soporte y páginas de login hosteadas revelan relaciones con vendors.
- Una marca adquirida sigue apuntando a infraestructura legacy alcanzable.
- Las ofertas de trabajo revelan opciones de proveedor cloud y framework.
- Una organización pública de GitHub expone convenciones de naming de paquetes.

## Notas relacionadas

- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[scope-validation|Validación de Scope]]
- [[passive-recon|Passive Recon]]
- [[third-party-exposure|Exposición de Terceros]]
- [[external-attack-surface|Superficie de Ataque Externa]]

## Referencias

- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
