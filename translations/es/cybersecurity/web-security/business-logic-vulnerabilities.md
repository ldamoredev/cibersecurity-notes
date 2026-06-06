# Business Logic Vulnerabilities

## Definición

Las vulnerabilidades de lógica de negocio son fallas en el flujo de trabajo previsto, suposiciones, invariantes o diseño de reglas de una aplicación, donde el sistema se comporta como fue codificado pero no de forma segura según la intención.

## Por qué importa

Los bugs de lógica de negocio están entre las fallas de seguridad más realistas y específicas del producto. No dependen de bugs clásicos del parser. Dependen de cómo el producto realmente funciona:
- secuencia
- precios
- aprobaciones
- cuotas
- cupones
- reintentos
- confianza en el flujo aplicado por el cliente

Frecuentemente están subdocumentados, subescaneados y tienen alto impacto.

## Cómo funciona

El mecanismo suele ser:
1. el producto asume un cierto flujo de trabajo, estado o invariante
2. el servidor no aplica esa suposición con suficiente fuerza
3. el atacante interactúa con el flujo de trabajo fuera de orden, demasiadas veces o en condiciones inesperadas
4. el sistema produce un resultado legítimo pero inseguro

## Técnicas / patrones

Los atacantes generalmente testean:
- saltar pasos
- envío repetido de acciones de un solo uso
- race conditions
- interacciones de precio negativo / descuento
- transiciones de estado fuera de orden
- abuso de reembolso parcial / cupón / crédito
- suposiciones ocultas aplicadas solo por la UI

## Variantes y bypasses

### Abuso de orden del flujo de trabajo

El atacante llama a los pasos en un orden no previsto.

### Abuso de un solo uso / replay

Un cupón, token o acción puede reutilizarse.

### Abuso de transición de estado

El servidor permite transiciones que deberían ser imposibles o estar limitadas por rol.

### Abuso de lógica de precios / contabilidad

El problema es el manejo incorrecto de valores, combinaciones o estado.

### Abuso de lógica por race condition

Dos operaciones válidas pueden combinarse concurrentemente para violar un invariante.

### Malentendido de reglas aplicadas por la UI

El frontend previene una ruta, pero el backend nunca la aplica realmente.

## Impacto

Impacto típico:
- abuso financiero
- escalada de privilegios o de flujo de trabajo
- cambios de estado no autorizados
- créditos / recompensas / uso duplicado
- fraude o consumo de recursos más allá de los límites previstos

## Detección y defensa

Ordenado por efectividad:

1.
**Modelar casos de abuso, no solo el happy path**
   Hacer el threat model del flujo de trabajo antes de codificarlo: ¿qué pasa si el usuario llama al paso 3 antes del paso 2, llama al paso 2 dos veces, o llama al paso 4 con estado obsoleto del paso 1? La mayoría de los bugs de lógica de negocio son filas faltantes en esta matriz, no fallas del parser.

2.
**Aplicar los invariantes del lado del servidor**
   Cada invariante del que depende el producto — "un cupón es de un solo uso", "un reembolso no puede exceder el pago original", "un usuario no puede estar en dos roles a la vez" — debe aplicarse en el servidor, en un solo lugar autoritativo, idealmente dentro de una transacción. Las reglas de UI y las verificaciones del lado del cliente no cuentan.

3.
**Usar restricciones de base de datos y transacciones para flujos críticos de estado**
   Las race conditions son la clase de lógica de negocio más explotada. Usar locks a nivel de fila, restricciones únicas y actualizaciones condicionales (`UPDATE ... WHERE status = 'pending'`) para hacer imposible el abuso por replay y acción concurrente en la capa de datos, no solo en la capa de aplicación.

4.
**Testear flujos de trabajo y transiciones de estado intencionalmente**
   Construir tests de máquina de estados que impulsen el flujo de trabajo desde cada estado alcanzable a través de cada transición, incluyendo las inválidas. Los tests basados en propiedades y con estado detectan exactamente la clase "paso fuera de orden" que los tests unitarios pierden.

5.
**Auditar las transiciones de alto valor**
   El movimiento de dinero, los cambios de rol, las transferencias de propiedad y las operaciones irreversibles necesitan escrutinio adicional — revisión separada, control dual o un paso de re-autenticación. El costo de un único bug de lógica de negocio aquí es mucho mayor que en endpoints de menor valor.

6.
**Instrumentar patrones de flujo de trabajo inusuales**
   Registrar cada transición de estado con el llamante, el estado antes/después e identificadores. Alertar sobre patrones que no deberían ocurrir: un solo usuario redimiendo el mismo cupón dos veces en segundos, un reembolso mayor que el total del pedido, un cambio de rol que bypasea la cola de aprobación.

7.
**No confiar en las restricciones de la UI**
   Que el frontend deshabilite un botón, oculte un campo o salte un paso no es un control de seguridad. Cualquier control que importe debe aplicarse en el servidor independientemente de lo que hizo el cliente.

## Ejemplos prácticos

- el cupón puede reutilizarse porque la invalidación ocurre demasiado tarde
- el checkout permite un precio manipulado a través de un mismatch de pasos
- el flujo de aprobación puede dispararse fuera de orden
- la acción de recompensa puede reproducirse concurrentemente para obtener valor extra

## Notas relacionadas

- [[broken-access-control]]
- [[broken-function-level-authorization]]
- [[api-rate-limiting]]

## Referencias

- **Fundamental:** OWASP WSTG business logic testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/
- **Testing / Lab:** PortSwigger business logic vulnerabilities topic — https://portswigger.net/web-security/logic-flaws
- **Investigación / Deep Dive:** PortSwigger, "Smashing the state machine: the true potential of web race conditions" — https://portswigger.net/research/smashing-the-state-machine
