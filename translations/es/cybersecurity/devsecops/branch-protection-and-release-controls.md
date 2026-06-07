# Protección de ramas y controles de release

## Definición

La protección de ramas y los controles de release son las reglas y mecanismos de governance que determinan quién puede cambiar rutas de código protegidas, aprobar releases y promover artifacts hacia producción.

## Por qué importa

Un build pipeline seguro todavía puede ser socavado si el código y los release gates que lo alimentan son débiles. Este tema conecta code review, aprobación, separación de funciones y disciplina de release.
Mantenelo separado de [[ci-cd-hardening]]: esta nota trata sobre quién puede cambiar o promover rutas sensibles de código, no sobre la postura de seguridad del entorno de automatización en sí.

## Perspectiva del atacante

Los atacantes buscan:
- pushes directos a ramas protegidas
- review gates bypass-eables
- aprobaciones débiles de release
- derechos de maintainer demasiado amplios
- atajos manuales alrededor del flujo formal de release

## Perspectiva del defensor

Los defensores deberían:
- proteger ramas sensibles y release tags
- exigir reviews y status checks apropiados
- restringir poderes de bypass
- definir quién puede aprobar, build-ear y promover

## Ejemplos prácticos

- admins pueden mergear sin checks y lo hacen rutinariamente
- release tags son mutables o están débilmente controlados
- la promoción a producción depende de un atajo manual no documentado

## Notas relacionadas

- [[ci-cd-hardening]]
- [[artifact-integrity]]
- [[secure-by-design]]
- [[supply-chain-security]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
