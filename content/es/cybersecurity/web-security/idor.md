---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - access-control
  - idor
sources: []
---

# Insecure Direct Object Reference (IDOR)

## Definición
IDOR es una clase de falla de autorización donde un atacante puede acceder o actuar sobre un objeto manipulando una referencia directa como un ID, nombre de archivo, clave o path.

## Por qué importa
IDOR es una de las clases de bug de mayor valor en aplicaciones reales porque:
- las referencias a objetos están por todos lados
- el camino de explotación suele ser simple
- el impacto suele ser acceso no autorizado real, no solo rarezas teóricas

Se entiende mejor como el encuadre clásico de web/appsec de la falla de autorización a nivel de objeto.

Esta nota debería quedar distinta de la [[broken-object-level-authorization|Broken Object-Level Authorization]] del lado de API, aunque están muy relacionadas.

## Cómo funciona
El mecanismo es:

1. la aplicación expone una referencia a un objeto
2. el servidor usa esa referencia para recuperar o modificar el objeto
3. el servidor no logra verificar que el usuario actual tenga permitido acceder a ese objeto

La vulnerabilidad no es "el ID es adivinable".
La vulnerabilidad es "la autorización no se impone correctamente".

Incluso los UUIDs no resuelven IDOR si faltan los chequeos de propiedad o de acceso.

## Técnicas / patrones
Los atacantes normalmente testean IDOR modificando:

- IDs numéricos en paths
- UUIDs en URLs o JSON
- nombres de archivo y referencias a documentos
- referencias de download/export
- valores de formulario ocultos
- rutas de frontend solo-mobile o alternativas
- referencias indirectas que igual mapean de forma predecible a objetos reales

Flujo de trabajo típico:
- logueate como usuario A
- capturá una request al objeto A
- cambiá solo la referencia al objeto
- reproducila contra el objeto B
- observá diferencias de lectura, escritura o metadata

## Variantes y bypasses

### IDOR de lectura
Lectura no autorizada del objeto de otro usuario.

### IDOR de escritura
Modificación no autorizada del objeto de otro usuario.

### IDOR de borrado / destructivo
Acceso a nivel de objeto más acción destructiva.

### Solapamiento con IDOR de función oculta
A veces el problema no es solo el acceso al objeto, sino también llamar a una ruta que la UI oculta. Eso empieza a solaparse con [[broken-access-control|Control de acceso roto]] o [[broken-function-level-authorization|Broken Function-Level Authorization]].

### IDOR de workflow multi-paso
La referencia al objeto es segura en un paso pero se vuelve explotable más adelante en el flujo.

### Malentendidos sobre referencias indirectas
Las apps a veces usan:
- UUIDs
- tokens opacos
- identificadores envueltos en base64

Estos igual pueden ser explotables si la autorización del lado del servidor es débil.

## Impacto
El impacto suele ser muy directo:
- acceder a los datos de otro usuario
- cambiar la configuración de otro usuario
- descargar los archivos de otro usuario
- escalar a través del acceso al estado de un objeto privilegiado
- destruir o corromper registros

El impacto se vuelve crítico cuando los objetos son:
- financieros
- relacionados con identidad
- de cara al admin
- accesibles en bulk
- fáciles de enumerar

## Detección y defensa
Ordenado por efectividad:

1. **Autorización del lado del servidor en cada acceso a objeto**
   Verificá siempre el derecho del llamante a ese objeto específico.

2. **Separá claramente la recuperación de objeto de la autorización de objeto**
   No asumas "si la ruta está autenticada, el objeto es seguro".

3. **Negá por defecto**
   La propiedad o el acceso deben probarse, no asumirse.

4. **Logueá los intentos de acceso a objetos sospechosos**
   Especialmente patrones de acceso a través de objetos adyacentes o no relacionados.

5. **Usá referencias indirectas solo como fricción secundaria**
   No son un control de autorización primario.

6. **Testeá tanto los caminos de lectura como de escritura**
   Muchos equipos arreglan uno y se pierden el otro.

## Ejemplos prácticos
- cambiar `/invoice/1001` por `/invoice/1002`
- intercambiar un ID de documento en una request de download
- modificar un ticket de soporte u objeto de cuenta no poseído por el usuario actual
- cambiar un ID oculto de proyecto/miembro/recurso en un formulario o llamada de API

## Notas relacionadas
- [[broken-access-control|Control de acceso roto]]
- [[broken-object-level-authorization|Broken Object-Level Authorization]]
- [[authorization|Autorización]]
- [[cybersecurity/security-playbooks/exploit-idor|Explotar IDOR]]

### Notas atómicas futuras sugeridas
- [[object-ownership-check-patterns|Patrones de chequeo de propiedad de objeto]]
- [[indirect-reference-misconceptions|Malentendidos sobre referencias indirectas]]

## Referencias
- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Testing / Lab:** PortSwigger IDOR topic — https://portswigger.net/web-security/access-control/idor
