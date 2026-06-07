# CI/CD Hardening

## Definición

CI/CD hardening es asegurar el build, test y deployment pipeline para que la automatización se vuelva una ruta de control confiable en vez de un amplificador de ataques.

## Por qué importa

Los pipelines suelen contener acceso a código, secrets, material de firma, privilegios de release y automatización de deployment. Un sistema CI/CD débil puede convertirse en el camino más corto desde compromiso de source hasta compromiso de producción.
Esta nota se mantiene enfocada en ejecución de pipeline y confianza del entorno de build; [[branch-protection-and-release-controls]] cubre governance alrededor de código y promoción, mientras [[secrets-management]] se enfoca en el material sensible en sí.

## Perspectiva del atacante

Los atacantes apuntan a CI/CD para:
- robar secrets
- correr steps maliciosos
- manipular artifacts
- abusar privilegios demasiado amplios de automatización
- pivotear desde el entorno de build hacia infraestructura

## Perspectiva del defensor

Los defensores deberían:
- bloquear permisos del pipeline
- aislar entornos de build
- minimizar exposición de secrets en jobs
- revisar quién puede modificar workflows y lógica de release
- tratar definiciones de pipeline como código sensible

## Ejemplos prácticos

- cualquier contributor puede modificar lógica de workflow en una rama sensible
- logs del pipeline exponen tokens o credenciales
- build runners tienen alcance de red amplio y estado persistente

## Notas relacionadas

- [[secrets-management]]
- [[artifact-integrity]]
- [[branch-protection-and-release-controls]]
- [[nist-ssdf]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
