# ASVS como input del proceso de desarrollo

## Definición

Esta nota trata OWASP ASVS no como una checklist post-hoc, sino como un input del proceso de desarrollo para diseñar, revisar y verificar controles técnicos de seguridad durante la implementación.

## Por qué importa

DevSecOps necesita requisitos, no solo scanners. ASVS da un conjunto estructurado de requisitos de verificación que los equipos pueden usar para dar forma a arquitectura, backlog items, criterios de review y readiness de release.
Esta nota trata sobre convertir requisitos de verificación en inputs de ingeniería. Es más acotada que [[nist-ssdf]] y menos filosófica que [[secure-by-design]].

## Perspectiva del atacante

Los atacantes explotan el gap entre “corremos tools” y “construimos los controles correctos”. Si los equipos no tienen requisitos explícitos de verificación, las vulnerabilidades sobreviven porque nadie fue concretamente responsable por el control.

## Perspectiva del defensor

Los defensores pueden usar ASVS para:
- definir expectativas de seguridad por área de control
- conectar requisitos con tareas de implementación
- mejorar rigor de review
- evitar depender solo de tests o tooling ad hoc

## Ejemplos prácticos

- un equipo tiene SAST y dependency scans pero ningún requisito explícito de verificación para access control o session handling
- security review se vuelve más consistente cuando se mapean secciones ASVS a stories y release gates

## Notas relacionadas

- [[nist-ssdf]]
- [[secure-by-design]]
- [[ci-cd-hardening]]
- [[broken-access-control|Broken Access Control]]

## Referencias

- **Fundamental:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
- **Fundamental:** OWASP ASVS Cheat Sheet Index — https://cheatsheetseries.owasp.org/IndexASVS.html
