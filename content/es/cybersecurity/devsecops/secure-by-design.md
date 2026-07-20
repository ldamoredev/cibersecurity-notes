# Secure by Design

## Definición

Secure by Design es el principio de que fabricantes de software y equipos de ingeniería deberían hacer que los resultados seguros sean el default del diseño de producto, en vez de trasladar la carga a operadores y usuarios finales.

## Por qué importa

Esta nota importa porque DevSecOps puede volverse demasiado tool-centric. Secure by Design reencuadra el objetivo: reducir condiciones explotables antes del deployment cambiando defaults, arquitectura de producto e incentivos de ingeniería.
Mantené claro el límite: esto es una filosofía de producto e ingeniería, no el framework de proceso de [[nist-ssdf]] ni el rol de catálogo de verificación de [[asvs-as-dev-process-input]].

## Perspectiva del atacante

Los atacantes se benefician cuando los productos:
- shippean defaults inseguros
- requieren que clientes endurezcan todo manualmente
- exponen funcionalidad peligrosa por defecto
- hacen fáciles las configuraciones riesgosas y difíciles las seguras

## Perspectiva del defensor

Los defensores deberían usar Secure by Design para:
- reducir exposición explotable antes de runtime
- simplificar defaults seguros
- eliminar clases de errores a nivel producto
- desplazar responsabilidad de seguridad hacia el productor, no solo hacia el cliente

## Ejemplos prácticos

- interfaces admin default quedan habilitadas
- storage público o features de debug se exponen por defecto
- equipos de producto dependen de docs que dicen a clientes “configuren seguro después”

## Notas relacionadas

- [[nist-ssdf]]
- [[branch-protection-and-release-controls]]
- [[container-security]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Fundamental:** CISA principles and approaches PDF — https://www.cisa.gov/sites/default/files/2023-04/principles_approaches_for_security-by-design-default_508_0.pdf
