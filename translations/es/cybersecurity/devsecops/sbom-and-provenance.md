# SBOM and Provenance

## Definición

Un SBOM registra qué componentes de software hay en un producto, mientras que provenance da trazabilidad sobre cómo, dónde y desde qué se construyeron esos artifacts.

## Por qué importa

No podés gobernar bien el riesgo de software si no sabés qué hay dentro de tus artifacts o cómo fueron producidos. SBOM y provenance mejoran incident response, review de dependencias, confianza de release y confianza downstream.
Mantené clara la distinción: SBOM y provenance mejoran visibilidad y trazabilidad, mientras [[artifact-integrity]] se enfoca en si los artifacts se mantuvieron confiables y [[dependency-risk]] se enfoca en exposición de paquetes upstream.

## Perspectiva del atacante

Los atacantes se benefician cuando los equipos no pueden responder:
- ¿qué componentes hay en este release?
- ¿qué build lo produjo?
- ¿qué upstreams estuvieron involucrados?
- ¿qué versiones están deployadas dónde?

## Perspectiva del defensor

Los defensores deberían:
- entender qué se está shippeando
- conectar componentes con builds y releases
- mejorar velocidad de respuesta cuando aparece nuevo riesgo upstream
- usar provenance para reforzar confianza en artifacts

## Ejemplos prácticos

- un equipo no puede identificar rápido dónde está deployado un paquete transitivo vulnerable
- existe un artifact en producción con origen de build poco claro
- los registros de release no capturan suficiente detalle de componentes para triage rápido

## Notas relacionadas

- [[supply-chain-security]]
- [[artifact-integrity]]
- [[dependency-risk]]
- [[api-inventory-management|API Inventory Management]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
