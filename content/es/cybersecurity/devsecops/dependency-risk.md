# Dependency Risk

## Definición

Dependency risk es el riesgo de seguridad introducido por librerías, frameworks y paquetes de terceros directos y transitivos, y por sus patrones de actualización y confianza.

## Por qué importa

Las dependencias expanden la base de código, la superficie de privilegio y la carga de mantenimiento más allá de lo que el equipo de producto escribe directamente. El riesgo no viene solo de CVEs conocidas, sino de calidad de mantenimiento, version drift, decisiones de confianza y abuso del ecosistema de paquetes.
Mantené el límite ajustado: esta nota trata sobre confianza upstream en paquetes y exposición de mantenimiento, no sobre manipulación de artifacts o trazabilidad de release después del build.

## Perspectiva del atacante

Los atacantes buscan:
- paquetes desactualizados con issues conocidas
- librerías mal mantenidas
- oportunidades de dependency confusion y typosquatting
- paquetes transitivos que nadie está mirando

## Perspectiva del defensor

Los defensores deberían:
- minimizar cantidad de dependencias cuando tenga sentido
- trackear dependencias directas y transitivas
- priorizar según reachability e impacto, no solo conteo bruto
- establecer disciplina de actualización y retiro

## Ejemplos prácticos

- un paquete vulnerable queda porque nadie es dueño de la cadencia de updates
- una dependencia transitiva introduce riesgo que el equipo no sabía que existía
- se asume confianza en un paquete porque “es popular”

## Notas relacionadas

- [[supply-chain-security]]
- [[sbom-and-provenance]]
- [[ci-cd-hardening]]
- [[image-scanning]]

## Referencias

- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
