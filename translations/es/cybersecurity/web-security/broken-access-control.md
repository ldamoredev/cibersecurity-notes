---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - access-control
sources: []
---

# Control de acceso roto

## Definición
El control de acceso roto (broken access control) ocurre cuando una aplicación no logra imponer a qué puede acceder o qué puede hacer un llamante.

## Por qué importa
Esta es una de las clases de mayor impacto en aplicaciones reales porque a menudo lleva directamente a:
- acceso no autorizado a datos
- acciones no autorizadas
- escalada de privilegios
- abuso de workflow
- exposición del plano de admin/control

Es más amplia que cualquier subtipo individual. Es el área de riesgo paraguas que incluye:
- fallas a nivel de objeto
- fallas a nivel de función
- fallas a nivel de propiedad
- exposición de funciones ocultas
- enforcement débil de tenant o de propiedad

## Cómo funciona
El mecanismo es:
1. la aplicación autentica a un llamante
2. el sistema expone datos o funcionalidad
3. el servidor no logra verificar si ese llamante tiene permitido acceder a ese recurso o acción en ese contexto

La distinción importante es:
- la autenticación responde quién sos
- la autorización responde qué podés hacer / acceder

## Técnicas / patrones
Los atacantes normalmente testean cambiando:
- identificadores de objeto
- rutas y familias de rutas
- métodos
- parámetros ocultos
- roles y scopes
- etapa / estado del workflow
- superficies específicas del cliente
- valores a nivel de campo que no deberían ser escribibles

## Variantes y bypasses
### Falla de autorización a nivel de objeto
Notas relacionadas: [[idor|IDOR]], [[broken-object-level-authorization|Broken Object-Level Authorization]]

### Falla de autorización a nivel de función
Notas relacionadas: [[broken-function-level-authorization|Broken Function-Level Authorization]]

### Falla de autorización a nivel de propiedad
Notas relacionadas: [[broken-object-property-level-authorization|Broken Object-Property-Level Authorization]], [[mass-assignment|Mass assignment]], [[excessive-data-exposure|Exposición excesiva de datos]]

### Falla de UI oculta
El frontend oculta la capacidad, pero el backend la acepta.

### Deriva cross-versión o cross-cliente
Un cliente o versión impone el acceso correctamente, otro no.

### Falla de frontera de tenant / propiedad
El sistema confía en referencias o estado sin imponer correctamente la propiedad o la separación de tenants.

## Impacto
Impacto típico:
- leer los datos de otro usuario
- modificar los recursos de otro usuario
- invocar acciones solo-de-admin o solo-de-staff
- cambiar el estado de un workflow protegido
- colapso de la frontera multi-tenant
- escalada de privilegios

## Detección y defensa
Ordenado por efectividad:

1. **Tratá la autorización como un sistema del lado del servidor de primera clase**
2. **Imponé autorización en cada camino de acceso**
3. **Separá los chequeos de objeto, función y propiedad**
4. **Negá por defecto**
5. **Testeá múltiples identidades y roles**
6. **Logueá los intentos de acceso negados y sospechosos**
7. **Revisá la deriva entre versiones y clientes**

## Ejemplos prácticos
- un usuario normal lee la factura de otro usuario
- un endpoint mobile permite un bypass de control de acceso no presente en la UI web
- una acción de admin es invocable directamente
- un campo JSON escribible deja a un usuario escalar propiedad o rol
- una ruta legacy preserva reglas de autorización más débiles

## Notas relacionadas
- [[idor|IDOR]]
- [[authorization|Autorización]]
- [[broken-function-level-authorization|Broken Function-Level Authorization]]
- [[cybersecurity/security-playbooks/exploit-idor|Explotar IDOR]]

### Notas atómicas futuras sugeridas
- [[tenant-boundary-failures|Fallas de frontera de tenant]]
- [[authorization-drift-across-clients|Deriva de autorización entre clientes]]

## Referencias
- **Foundational:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control
