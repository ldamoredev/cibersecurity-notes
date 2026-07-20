# Supply Chain Security

## Definición

Supply chain security es la práctica de reducir riesgo introducido por código de terceros, build systems, dependencias, artifacts, rutas de firma y procesos de distribución de releases.

## Por qué importa

El software moderno se ensambla desde muchas piezas upstream. DevSecOps está incompleto si asegura solo código first-party mientras ignora dependencias, paquetes transitivos, integridad de build y provenance de release.
Esta nota es el umbrella para el cluster de supply-chain: [[dependency-risk]] cubre exposición upstream de paquetes, [[artifact-integrity]] cubre resistencia a manipulación en outputs y [[sbom-and-provenance]] cubre trazabilidad de componentes y build.

## Perspectiva del atacante

Los atacantes apuntan a supply chains porque un compromiso puede escalar a muchos consumidores downstream. Debilidades en confianza de paquetes, build systems, secrets y artifacts pueden bypass-ear runtime security fuerte por completo.

## Perspectiva del defensor

Los defensores deberían:
- entender de dónde vienen los componentes de software
- reducir confianza innecesaria en upstreams
- asegurar el camino de build y release
- verificar qué se shippea, no solo qué se desarrolla

## Ejemplos prácticos

- un dependency update trae un paquete malicioso o comprometido
- un build artifact es reemplazado después de CI pero antes del release
- los equipos trackean vulnerabilidades pero no provenance ni trust boundaries

## Notas relacionadas

- [[dependency-risk]]
- [[artifact-integrity]]
- [[sbom-and-provenance]]
- [[third-party-exposure|Exposición de terceros]]

## Referencias

- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
