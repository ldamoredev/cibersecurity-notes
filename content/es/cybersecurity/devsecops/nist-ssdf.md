# NIST SSDF

## Definición

El Secure Software Development Framework (SSDF) es el framework de NIST para integrar seguridad de software en prácticas de desarrollo a través de la organización, toolchain y proceso de release.

## Por qué importa

SSDF le da a DevSecOps una estructura durable. Convierte “seguridad en el pipeline” de una aspiración vaga en prácticas concretas alrededor de preparar la organización, proteger software, producir software bien asegurado y responder a vulnerabilidades.
Esta nota es el anchor de framework para la rama; [[secure-by-design]] es la filosofía de producto, mientras [[asvs-as-dev-process-input]] es un input concreto de verificación que los equipos pueden alimentar al trabajo de delivery.

## Perspectiva del atacante

Los atacantes se benefician cuando los equipos tratan seguridad como tooling ad hoc en vez de como sistema. Entornos débiles, checks inconsistentes, roles poco claros y prácticas informales de release crean aberturas mucho antes de la explotación runtime.

## Perspectiva del defensor

Los defensores deberían usar SSDF para:
- definir prácticas de desarrollo seguro
- establecer entornos y responsabilidades seguros
- integrar checks en el workflow
- mejorar disciplina de respuesta y remediación

## Ejemplos prácticos

- existe secure code review, pero aprobación de release e integridad de artifacts son informales
- los equipos escanean dependencias pero carecen de un proceso para arreglar o priorizar hallazgos
- developers endurecen código pero el entorno de build está débilmente controlado

## Notas relacionadas

- [[secure-by-design]]
- [[ci-cd-hardening]]
- [[supply-chain-security]]
- [[asvs-as-dev-process-input]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** NIST SSDF project page — https://csrc.nist.gov/Projects/ssdf
