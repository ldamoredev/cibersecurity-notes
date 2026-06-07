# Cloud Network Boundaries

## Definición

Los cloud network boundaries son los controles de red que deciden la alcanzabilidad de workloads cloud: VPCs, subredes, security groups, firewalls, configuración de servicios, controles de identidad y configuración de workloads.

## Por qué importa

Los entornos cloud tienen controles de red potentes, pero los defaults son frecuentemente más abiertos de lo que los equipos esperan. Un security group, servicio mal configurado, regla de peering o exposición IPv6 puede crear alcanzabilidad desde internet hacia sistemas que se pensaba eran internos.

El modelo mental del cloud es que la "privacidad" no es una propiedad del datacenter sino de decisiones de configuración específicas.

## Cómo funciona

Los límites de red cloud tienen **6 capas de alcanzabilidad**:

1. **Addressing.** ¿El recurso tiene una IP pública o solo privada?
2. **Routing.** ¿Cómo llegan los paquetes al recurso?
3. **Reglas de firewall.** ¿Los security groups o reglas de firewall permiten el tráfico entrante?
4. **Exposición de servicios.** ¿El servicio está detrás de un load balancer, API gateway o expuesto directamente?
5. **Controles de identidad.** ¿El servicio requiere autenticación más allá de la alcanzabilidad de red?
6. **Controles de workload.** ¿Hay restricciones a nivel de OS, aplicación o contenedor?

La exposición real es la intersección de todas las capas. Un host puede parecer privado mientras que un load balancer o endpoint de servicio delante de él es alcanzable públicamente.

Un ejemplo trabajado, ruta de exposición inesperada:

```
Recurso:
  base de datos interna de producción

IP:
  solo privada, dentro de la VPC

Security group:
  acepta 5432 desde 10.0.0.0/8

Sorpresa:
  la subred está en peering con una VPC de lab sin restricción de CIDRs

Ruta de acceso:
  internet → VM de lab → peering → red interna → base de datos

Decisión:
  revisar todos los peeerings de VPC por flujo de tráfico asumido
```

Los límites de red cloud requieren revisión por capa, no solo la regla de security group más visible.

## Técnicas / patrones

Las revisiones analizan:

- security groups con `0.0.0.0/0` o `::/0` para puertos admin
- redes planas donde todos los workloads pueden comunicarse entre sí
- VPC peerings con rutas de transitividad inesperadas
- load balancers o API gateways que exponen backends internos
- endpoints de servicios accesibles públicamente sin autenticación
- exposición IPv6 donde solo IPv4 se pensaba que estaba activo
- reglas de firewall heredadas sin propietario

## Variantes y bypasses

Los límites de red cloud fallan de **5 formas comunes**.

### 1. Puerto admin abierto al mundo

SSH, RDP, bases de datos, paneles admin o debugging son alcanzables desde internet.

### 2. Red privada plana

Todos los workloads dentro de una VPC pueden alcanzarse entre sí sin restricciones.

### 3. Sorpresa de peering

Los VPC peeerings crean conectividad transitiva inesperada.

### 4. Bypass de load balancer

El load balancer expone un servicio público, pero el backend también es directamente alcanzable.

### 5. Exposición IPv6

Los controles de red IPv4 no se aplican al espacio de direcciones IPv6.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso directo admin.** Los puertos SSH, RDP o DB abiertos son el riesgo de exposición más directo.
- **Movimiento lateral.** Las redes planas convierten un workload comprometido en un pivot.
- **Exfiltración de datos.** Los backends no intencionalmente públicos pueden exponer datos de aplicación.
- **Acceso entre cuentas.** Las relaciones de peering pueden cruzar límites de confianza.
- **Evasión de control.** Los patrones de bypass permiten llegar a workloads sin pasar por los controles de identity o WAF.

## Detección y defensa

Ordenado por efectividad:

1.
**Negá por defecto, permitir explícitamente.**
   Los security groups y reglas de firewall deberían empezar con deny-all y abrir solo los puertos y fuentes necesarios.

2.
**Segmentá workloads en subredes y VPCs separadas.**
   La producción, el staging, los labs y los servicios compartidos no deberían compartir una red plana.

3.
**Mantené un inventario de interfaces públicas.**
   Las IPs públicas, load balancers, API gateways y endpoints DNS-a-servicio deberían estar registrados con propietario y fecha de revisión.

4.
**Revisá los peeerings de VPC por acceso transitivo.**
   El peering no es solo conectividad bilateral; puede crear caminos que crucen límites de confianza no intencionados.

5.
**Loguiá los flujos de red.**
   Los VPC flow logs y los network logs muestran la alcanzabilidad real, no solo la configuración de seguridad teórica.

### Qué no funciona como defensa primaria

- **Nombrar una subred "privada".** El nombre no limita el routing.
- **Confiar en solo controls de host para seguridad de red.** La defensa en profundidad requiere ambas capas.
- **Asumir que el peering es seguro porque es entre tus propias cuentas.** El blast radius de cuenta compartida se expande con el peering.
- **Ignorar IPv6.** Los providers frecuentemente asignan direcciones IPv6 incluso cuando no se solicitan.

## Labs prácticos

Usá una cuenta sandbox.

### Revisá los security groups por puertos admin abiertos

```
Puerto | Protocolo | Fuente | Propietario | Motivo | Revisión
22     | TCP       | 0.0.0.0/0 | ?       | ?      | requerida
3306   | TCP       | 10.0.0.0/8| db-team | app    | aceptable
```

Los puertos con fuente `0.0.0.0/0` o `::/0` necesitan justificación explícita.

### Mapeá los peerings de VPC

```
VPC origen | VPC destino | CIDRs permitidos | Motivo | ¿Puede alcanzar producción?
```

Los peerings sin restricción de CIDRs entre VPCs de lab y producción son un riesgo de movimiento lateral.

### Realizá un inventario de endpoints públicos

```
Nombre DNS | IP | Tipo | Servicio backend | Propietario | Autenticación | Revisión
```

Este inventario convierte la arquitectura de red en superficie de ataque concreta.

### Revisá la exposición IPv6

```
Recurso | Dirección IPv6 | Security group IPv6 | Exposición
```

Los recursos con direcciones IPv6 y security groups `deny-all` para IPv4 pueden estar inadvertidamente alcanzables.

### Probá la alcanzabilidad real desde fuera de la VPC

```
# Desde una VM fuera de la VPC objetivo
nmap -Pn -p 22,80,443,3306,5432,8080 <IP_OBJETIVO>
```

Verificá que los puertos se comporten según lo esperado desde diferentes puntos de la red.

## Ejemplos prácticos

- Un security group de una instancia de base de datos permite 5432 desde `0.0.0.0/0`.
- Un peering de VPC de lab crea un camino hacia la producción.
- Un puerto de debugging queda abierto en un host de producción.
- Un load balancer expone servicios de backend mientras el host también tiene una IP pública.
- Los recursos IPv6 están alcanzables a pesar de los controles IPv4 correctos.

## Notas relacionadas

- [[cloud-security-basics]]
- [[cloud-iam-boundaries]]
- [[ssh-access-to-cloud-hosts]]
- [[cloud-logging-and-detection]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Notas atómicas futuras sugeridas

- vpc-design-patterns
- cloud-network-segmentation
- cloud-load-balancer-security
- cloud-private-connectivity

## Referencias

- **Docs Oficiales:** AWS VPC security — https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security.html
- **Docs Oficiales:** Google Cloud VPC firewall rules — https://cloud.google.com/vpc/docs/firewalls
- **Docs Oficiales:** Azure network security groups — https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview
