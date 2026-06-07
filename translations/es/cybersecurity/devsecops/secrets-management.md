# Secrets Management

## Definición

Secrets management es el manejo seguro de credenciales, tokens, claves, certificados y otro material sensible a través de desarrollo, build, deployment y runtime.

## Por qué importa

Los secrets frecuentemente cruzan trust boundaries entre source control, CI/CD, infraestructura y producción. Un manejo débil convierte conveniencia local en compromiso sistémico.
Esta nota trata sobre el lifecycle y exposición del material sensible en sí, no sobre todo el entorno CI/CD ni el modelo de release-governance que lo rodea.

## Perspectiva del atacante

Los atacantes buscan:
- secrets en source control
- credenciales en logs de CI
- tokens long-lived en variables de entorno
- secrets overprivileged reutilizados entre sistemas
- secrets viejos que nunca se rotaron

## Perspectiva del defensor

Los defensores deberían:
- minimizar dónde existen secrets
- separar secrets de build-time y runtime
- rotar y scopear secrets intencionalmente
- reducir manejo humano de secrets
- revisar exposición en logs, artifacts y config

## Ejemplos prácticos

- un deploy token se imprime en logs
- la misma credencial long-lived se reutiliza entre entornos
- el historial del repo todavía contiene secrets que los equipos asumen que “ya no están”

## Notas relacionadas

- [[ci-cd-hardening]]
- [[supply-chain-security]]
- [[artifact-integrity]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
