# Artifact Integrity

## Definición

Artifact integrity es la garantía de que outputs de build, paquetes, imágenes y artifacts de release no fueron manipulados y pueden trazarse hasta el proceso de build previsto.

## Por qué importa

Si no podés confiar en lo que se construyó y se shippeó, los checks de seguridad anteriores en el pipeline pierden gran parte de su valor. La integridad trata de preservar confianza desde el source hasta el release.
Esto es distinto de [[dependency-risk]] y [[sbom-and-provenance]]: la pregunta acá es si el artifact shippeado se mantuvo confiable, no solo qué componentes contiene o de dónde vinieron.

## Perspectiva del atacante

Los atacantes apuntan a artifact integrity mediante:
- manipulación de outputs de build
- reemplazo de artifacts después de CI
- abuso de controles débiles de release
- explotación de gaps entre build, storage y deployment

## Perspectiva del defensor

Los defensores deberían:
- limitar quién y qué puede escribir artifacts de release
- trazar artifacts hasta builds y commits específicos
- revisar rutas de storage y promoción
- separar intencionalmente la confianza del build de la confianza del deployment

## Ejemplos prácticos

- un artifact de release en storage es mutable después del build
- deployment consume “latest” en vez de un artifact inmutable controlado
- no hay forma confiable de probar qué source produjo un binario shippeado

## Notas relacionadas

- [[supply-chain-security]]
- [[ci-cd-hardening]]
- [[sbom-and-provenance]]
- [[branch-protection-and-release-controls]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
