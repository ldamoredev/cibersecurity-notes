# Corporate VPNs vs Consumer VPNs

## Definición

Las VPN corporativas son generalmente infraestructura de control de acceso para alcanzar recursos organizacionales privados. Las VPN de consumidor son generalmente productos de ruteo de privacidad para cambiar la visibilidad de la ruta de red en internet público.

La palabra VPN es la misma, pero el objetivo de seguridad es diferente.

## Por qué importa

Confundir VPN corporativas y de consumidor lleva a expectativas incorrectas. Una VPN corporativa suele ser consciente de la identidad, gestionada por dispositivo, monitoreada y registrada por diseño. Una VPN de consumidor se comercializa como herramienta de privacidad, pero su valor depende de la confianza en el proveedor, el comportamiento de ruteo y los controles de fuga.

Las VPN corporativas generalmente responden a "¿quién puede acceder a este recurso interno?". Las VPN de consumidor generalmente responden a "¿quién puede observar mi ruta de internet pública?".

## Cómo funciona

Usá el modelo de 4 diferencias:

1.
**Objetivo de seguridad**
   VPN corporativa: acceso autenticado a recursos de la empresa. VPN de consumidor: visibilidad reducida de la red local o del ISP y ruta de red de origen aparente cambiada.

2.
**Identidad**
   VPN corporativa: vinculada a la identidad del empleado, postura del dispositivo, MFA, política y monitoreo. VPN de consumidor: vinculada a la cuenta del proveedor, pago, dispositivo o identidad de suscripción.

3.
**Logging**
   VPN corporativa: el logging se espera para operaciones de seguridad, cumplimiento y respuesta a incidentes. VPN de consumidor: el logging es una cuestión de confianza en privacidad.

4.
**Alcance del tráfico**
   VPN corporativa: puede rutear subredes privadas o todo el tráfico a través de la infraestructura de la empresa. VPN de consumidor: generalmente rutea el tráfico de internet pública a través de salidas del proveedor.

Comparación:

```
VPN corporativa:
  propósito: control de acceso
  identidad: empleado/dispositivo
  logging: esperado
  propietario: empleador
  pregunta de confianza: ¿puede este usuario/dispositivo alcanzar este recurso?

VPN de consumidor:
  propósito: ruteo de privacidad
  identidad: suscriptor/cuenta del proveedor
  logging: sensible para la privacidad
  propietario: proveedor
  pregunta de confianza: ¿quién ve mi ruta de red ahora?
```

El bug no es usar una VPN corporativa. El bug es esperar que se comporte como un producto de privacidad del consumidor.

## Técnicas / patrones

- Identificar si la VPN existe para control de acceso o ruteo de privacidad.
- Verificar si todo el tráfico o solo las subredes privadas se rutean.
- Leer los avisos corporativos de uso aceptable y monitoreo.
- Tratar los logs de VPN corporativa como evidencia de seguridad normal, no como una falla de privacidad.
- Evaluar los logs de VPN de consumidor como evidencia de confianza del proveedor.
- Evitar usar VPN o dispositivos gestionados por el empleador para flujos de trabajo de privacidad personal.

## Variantes y bypasses

Usá los 5 patrones de despliegue:

### 1. VPN corporativa de túnel completo

Todo el tráfico rutea por la infraestructura de la empresa. Esto puede soportar monitoreo y protección pero significa que la navegación personal puede ser visible para los sistemas del empleador.

### 2. VPN corporativa de split-tunnel

Solo las rutas corporativas usan la VPN. Esto reduce la carga y preserva las rutas de internet local, pero la política de división debe ser clara y testeada.

### 3. Acceso corporativo con conciencia de identidad

El acceso moderno puede combinar VPN, postura del dispositivo, MFA, SSO, EDR y acceso condicional. El túnel es solo un control en un sistema de acceso más amplio.

### 4. VPN de consumidor de túnel completo

La mayoría del uso de VPN de consumidor rutea el tráfico de internet público a través de salidas del proveedor. El proveedor se convierte en el nuevo punto de confianza de la ruta de red.

### 5. Brecha de marketing de privacidad de consumidor

Las VPN de consumidor pueden prometer demasiado sobre el anonimato. No eliminan la identidad de cuenta, los browser fingerprints, las cookies, el comportamiento o la confianza en el proveedor.

## Impacto

- Mejores expectativas para el monitoreo del empleador y la respuesta a incidentes.
- Reducción del mal uso de VPN corporativas para privacidad personal.
- Evaluación más clara de las afirmaciones de confianza de VPN de consumidor.
- Mejores conversaciones de arquitectura sobre reemplazar el amplio acceso VPN con controles con conciencia de identidad.
- Menos suposiciones falsas sobre lo que "conectado a VPN" prueba.

## Detección y defensa

Ordenado por efectividad:

1.
**Nombrar el objetivo de la VPN**
   Decidir si la VPN es para acceso a recursos privados, privacidad de internet pública, resistencia a la censura o segmentación de red. El objetivo determina qué significa "seguro".

2.
**Documentar la identidad y el logging**
   Las VPN corporativas deberían indicar qué datos de identidad, dispositivo, ruta y actividad se registran. Las VPN de consumidor deberían evaluarse para minimización y evidencia de confianza.

3.
**Preferir el acceso con mínimo privilegio para recursos corporativos**
   El amplio acceso de red debería reducirse donde sea posible a través de segmentación, proxies con conciencia de identidad, acceso por app y patrones de zero trust.

4.
**Testear el alcance de la ruta**
   El túnel completo y el split tunnel tienen diferentes consecuencias de privacidad y seguridad. Verificar las tablas de rutas y el comportamiento del DNS.

5.
**Separar la privacidad personal de los entornos de trabajo gestionados**
   Los dispositivos y VPN gestionados por el empleador generalmente no son apropiados para flujos de trabajo de privacidad personal.

### Qué no funciona como defensa primaria

- **La VPN corporativa no es anonimato personal.** A menudo aumenta la visibilidad del empleador.
- **La VPN de consumidor no es control de acceso corporativo.** No autentica a un usuario ante recursos privados de la empresa por sí sola.
- **El split tunnel no es automáticamente más seguro.** Reduce cierta exposición y crea otra ambigüedad de ruteo.
- **Zero trust no es simplemente "sin VPN".** Es una arquitectura de identidad, dispositivo, política, telemetría y mínimo privilegio.

## Labs prácticos

### Clasificar un despliegue VPN

```
Nombre VPN:
Propietario:
Propósito:
Usuarios:
Recursos alcanzados:
Proveedor de identidad:
¿Requiere postura del dispositivo?:
¿Requiere MFA?:
¿Logging esperado?:
¿Túnel completo o split?:
```

El resultado debería hacer obvio el intento corporativo vs consumidor.

### Inspeccionar el alcance de la ruta

```
netstat -rn | sed -n '1,120p'
```

Ejecutar antes y después de la conexión. Buscar si el tráfico por defecto o solo las subredes privadas usan la VPN.

### Construir una tarjeta de expectativa de monitoreo

```
VPN corporativa:
¿Registra identidad del usuario?:
¿Registra dispositivo?:
¿Registra IP de origen?:
¿Registra destino/recurso interno?:
¿Registra DNS?:
Retención:
Aviso/política:
```

Esto convierte el monitoreo en un hecho de política e ingeniería explícito.

### Comparar afirmaciones de confianza de consumidor

```
Proveedor:
Afirmación de no-log:
Logs de conexión:
Logs de tráfico:
Metadatos de pago:
Auditoría:
Jurisdicción:
Propietario:
Decisión:
```

Usar esto para VPN de consumidor, no para infraestructura de acceso corporativo.

## Ejemplos prácticos

- Un empleado usa VPN corporativa para alcanzar Git interno y la empresa registra identidad, dispositivo y tiempo de acceso.
- Una empresa pasa de amplio acceso VPN a acceso por app con MFA y verificaciones de postura del dispositivo.
- Una VPN de consumidor reduce la visibilidad del ISP en internet doméstica pero no oculta el login de cuenta de los sitios web.
- Una VPN corporativa de split-tunnel envía apps internas por la empresa y la navegación pública por el ISP local.
- Un usuario intenta usar un laptop del trabajo más VPN corporativa para privacidad personal y malentiende la visibilidad del empleador.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[vpn-protocols|VPN Protocols]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[secure-by-design|Secure by Design]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** NIST Zero Trust Architecture SP 800-207 - https://csrc.nist.gov/pubs/sp/800/207/final
- **Fundamental:** CISA Zero Trust Maturity Model - https://www.cisa.gov/zero-trust-maturity-model
