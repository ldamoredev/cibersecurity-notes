# Índice de Playbooks de Seguridad

## Propósito

Este índice es el punto de entrada raíz para la rama security-playbooks del atlas de ciberseguridad.

Usalo para:
- navegar workflows ofensivos y defensivos reutilizables
- conectar notas conceptuales con procedimientos repetibles
- convertir teoría en checklists testeables
- crear un manual personal de operador para trabajo de seguridad

Usá [[reference-registry-playbooks|Registro de referencia — Playbooks]] como fuente de verdad para las referencias de esta rama.
Volvé al [[index|Índice de Ciberseguridad]] para navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - La rama conceptual que operacionaliza el playbook (nombrada en las notas relacionadas de cada playbook).

---

## Primeros playbooks

### Control de acceso y auth

1. [[exploit-idor|Exploit IDOR]]
2. [[inspect-session-handling|Inspeccionar manejo de sesiones]]
3. [[break-jwt-validation|Romper validación JWT]]

### Server-side y proxy-aware

1. [[investigate-ssrf|Investigar SSRF]]
2. [[reverse-proxy-misconfig-checklist|Checklist de mala configuración de reverse proxy]]
3. [[test-client-ip-spoofing|Testear spoofing de IP de cliente]]
4. [[trace-metadata-endpoint-reachability|Trazar alcanzabilidad de metadata endpoints]]

### Input y manejo de archivos

1. [[exploit-sqli|Exploit SQL Injection]]
2. [[test-path-traversal|Testear path traversal]]
3. [[test-cors-behavior|Testear comportamiento CORS]]
4. [[inspect-file-upload-surface|Inspeccionar superficie de file upload]]

### Recon e ingeniería de scans

1. [[run-scan-pipeline|Ejecutar pipeline de scan]] — ofensa
2. [[detect-external-scan-pipeline|Detectar pipeline de scan externo]] — defensa

### Active Directory y credenciales

1. [[detect-kerberoasting-and-as-rep-roasting|Detectar Kerberoasting y AS-REP Roasting]]
2. [[detect-dcsync-and-ntdsdit-access|Detectar DCSync y acceso a ntds.dit]]
3. [[detect-bloodhound-collection|Detectar BloodHound collection]]

## Cómo usar playbooks

Un playbook no reemplaza una nota conceptual.
Es el paso "cómo lo ejecuto / verifico / detecto" después de entender el concepto.

Para cada playbook:

1. leé las notas relacionadas
2. verificá scope y autorización
3. prepará evidencia reproducible
4. ejecutá pasos mínimos primero
5. registrá hallazgos, límites y falsos positivos
6. conectá el resultado con mitigación o detección

## Convenciones

Los playbooks deberían ser:

- seguros por default
- repetibles
- orientados a evidencia
- separados entre recon, exploit/test, validación, mitigación y logging
- explícitos sobre supuestos y límites

## Próximos playbooks sugeridos

- inspect-oauth-flow
- test-api-authorization
- test-rate-limiting
- test-open-redirects
- investigate-command-injection
- inspect-business-logic-workflow
- validate-cloud-metadata-exposure
- test-storage-bucket-exposure
- inspect-ci-cd-secrets
- review-container-image-risk

## Notas relacionadas

- [[index|Índice de Ciberseguridad]]
- [[reference-registry-playbooks|Reference Registry — Playbooks]]
- [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor como herramienta de aprendizaje]]
- [[minimum-viable-cybersecurity-literacy|Alfabetización mínima viable en ciberseguridad]]

## Referencias

- **Fundamental:** OWASP Web Security Testing Guide — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Fundamental:** MITRE ATT&CK — https://attack.mitre.org/
