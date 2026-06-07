# Image Scanning

## Definición

Image scanning es el proceso de inspeccionar container images en busca de vulnerabilidades conocidas, paquetes riesgosos y otros issues antes de promoción o deployment.

## Por qué importa

Image scanning es útil, pero solo cuando está ubicado en el contexto correcto. No reemplaza dependency management, build integrity ni una estrategia segura de base images. Es una señal dentro de un sistema DevSecOps más grande.
Esta nota se mantiene intencionalmente acotada: scanning ayuda a exponer issues conocidos, pero por sí solo no puede probar que un container esté bien diseñado, sea mínimamente privilegiado o se promueva de forma segura.

## Perspectiva del atacante

Los atacantes se benefician cuando los equipos:
- confían ciegamente en el output del scan
- ignoran imágenes no escaneadas y caminos laterales
- usan bases vulnerables porque “el build pasó”
- dependen de scanning sin arreglar ni priorizar

## Perspectiva del defensor

Los defensores deberían:
- tratar scanning como un control entre muchos
- escanear temprano y antes del release
- priorizar por exploitability y exposición, no solo por conteo
- entender blind spots del scanner y riesgos de falsa confianza

## Ejemplos prácticos

- imágenes pasan un scan gate pero todavía contienen tooling riesgoso sin uso y malos defaults
- una ruta side-loaded de imágenes bypass-ea scanning por completo
- los equipos escanean pero no hacen triage ni remediación significativa

## Notas relacionadas

- [[container-security]]
- [[dependency-risk]]
- [[ci-cd-hardening]]
- [[sbom-and-provenance]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
