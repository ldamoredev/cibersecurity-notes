# Container Security

## Definición

Container security es la práctica de reducir riesgo en cómo las aplicaciones containerizadas se construyen, configuran, shippean y corren.

## Por qué importa

Los containers facilitan delivery, pero también empaquetan software, dependencias, configuración y supuestos de privilegio en una unidad altamente portable. Imágenes base débiles, privilegios amplios y malos defaults pueden escalar patrones inseguros rápidamente.
Container security es más amplio que [[image-scanning]]: scanning es un control útil, pero el tema completo incluye confianza en base images, diseño de privilegios, build context, postura runtime y disciplina de promoción.

## Perspectiva del atacante

Los atacantes buscan:
- containers demasiado privilegiados
- imágenes base débiles o infladas
- secrets embebidos en imágenes
- tooling admin/debug expuesto
- drift entre lo que contiene la imagen y lo que los equipos creen que contiene

## Perspectiva del defensor

Los defensores deberían:
- reducir complejidad de imágenes
- controlar privilegios y capabilities cuidadosamente
- mantener intencionales el build context y el contenido de imágenes
- separar higiene de build de supuestos runtime
- revisar cómo se obtienen y promueven las imágenes

## Ejemplos prácticos

- un container corre como root sin necesidad
- debug tools y credenciales están embebidas en imágenes de producción
- los equipos heredan una base image sin entender su estado de mantenimiento

## Notas relacionadas

- [[image-scanning]]
- [[supply-chain-security]]
- [[artifact-integrity]]
- [[exposed-storage|Storage expuesto]]

## Referencias

- **Fundamental:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Fundamental:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
