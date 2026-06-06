# Host and Port Discovery

## Definición

El host and port discovery es el proceso de encontrar hosts en vivo y los puertos y servicios alcanzables que exponen dentro de un scope autorizado.

## Por qué importa

Una vez que se conocen los dominios y candidatos, el host and port discovery valida qué está realmente escuchando. Es una de las formas más claras de separar la superficie obsoleta de la superficie en vivo e identificar puntos de entrada alternativos.

Mantené el límite claro: esta nota es sobre alcanzabilidad y puertos expuestos, mientras que la [[service-validation|Validación de Servicios]] y el [[service-enumeration|Service Enumeration]] van más profundo en qué significan esas responses.

## Cómo funciona

El host and port discovery tiene **4 capas**:

1. **Resolver.** Convertir nombres a IPs e identificar pistas del proveedor/CDN/origen.
2. **Alcanzar.** Determinar si los hosts responden en absoluto.
3. **Escanear.** Identificar puertos abiertos y protocolos probables dentro del scope.
4. **Priorizar.** Enrutar servicios interesantes a validación y triage de superficie de ataque.

El error no es un puerto abierto por sí solo. El riesgo es un servicio alcanzable que es inesperado, sensible, sin dueño o con controles débiles.

Un ejemplo trabajado, port scan a triage:

```
Host:
  api-preview.example.test

Open ports:
  443/tcp HTTPS
  8443/tcp HTTPS-alt
  22/tcp SSH

Peer comparison:
  other preview hosts expose only 443

Decision:
  8443 and 22 are outliers; route 8443 to service validation and 22 to exposed-service triage
```

El port discovery se vuelve valioso cuando cada outlier recibe una hipótesis de rol y la siguiente validación.

## Técnicas / patrones

Los operadores verifican:

- comportamiento HTTP/HTTPS en vivo
- puertos top y puertos específicos del entorno
- puertos de acceso remoto como SSH, RDP, VPN
- puertos de base de datos/caché/búsqueda/cola
- dashboards de puertos altos y servidores de dev
- diferencias CDN/proxy versus origen directo
- hosts pares con servicios extra inusuales

## Variantes y bypasses

Los resultados del discovery caen en **6 clases**.

### 1. Puertos web públicos esperados

Exposición normal HTTP/HTTPS/API.

### 2. Puertos de acceso remoto

SSH, RDP, VPN, protocolos admin o servicios tipo bastión.

### 3. Puertos de servicios de datos

Bases de datos, cachés, colas, motores de búsqueda y gateways de objetos.

### 4. Puertos admin/dashboard

Grafana, Kibana, Jenkins, servidores debug, métricas y paneles de gestión.

### 5. Split edge/origen

La ruta CDN/proxy difiere de la alcanzabilidad del origen directo.

### 6. Falso positivo o estado filtrado

Los firewalls, edges de CDN, comportamiento tarpit o hosting compartido distorsionan el output del scan.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso inicial.** Servicio de acceso remoto o explotable es alcanzable.
- **Exposición de datos.** Servicios de datos aparecen fuera de las redes previstas.
- **Exposición del plano de control.** Dashboards y servicios admin son alcanzables.
- **Bypass de edge.** Los orígenes directos saltean controles de CDN/WAF.
- **Corrección de inventario.** Los servicios inesperados se convierten en preguntas de ownership.

## Detección y defensa

Ordenado por efectividad:

1. **Definí puertos esperados por rol de asset.**
   Un servidor web, base de datos, herramienta admin y origen CDN deberían tener exposición esperada diferente.

2. **Escaneá continuamente assets públicos propios.**
   Los resultados de scan externo deberían compararse con el inventario.

3. **Restringí puertos de gestión y datos.**
   No deberían ser ampliamente accesibles desde internet.

4. **Validá el aislamiento del origen.**
   Los orígenes directos deberían rechazar tráfico que bypasea edges previstos.

5. **Monitoreá cambios en la postura de puertos.**
   Los puertos nuevos suelen aparecer durante incidentes, migraciones o debugging temporal.

### Qué no funciona como defensa primaria

- **Puertos no estándar.** Los scanners los encuentran.
- **Estado filtrado sin ownership.** Igual necesitás saber por qué un puerto se comporta así.
- **Scanning de una sola vez.** La postura de puertos cambia con los deploys y actualizaciones de firewall.
- **Asumir que CDN significa que el origen está oculto.** Los orígenes se filtran a través de DNS, certs e IPs directas.

## Labs prácticos

Usá objetivos propios.

### Escanear puertos comunes

```
nmap -sV -Pn --top-ports 100 target.example.test
```

Enrutar hallazgos inesperados a validación de servicios.

### Verificar puertos de alto riesgo

```
nmap -sV -Pn -p 22,3389,5432,3306,6379,9200,5601,8080,8443 target.example.test
```

Estos puertos suelen representar exposición admin o de datos.

### Comparar hosts pares

```
nmap -sV -Pn -iL hosts.txt --top-ports 50
```

Los outliers suelen merecer triage primero.

### Construir una tabla de postura de puertos

```
host | port | service guess | expected? | peer outlier? | owner | next validation
```

Esto convierte los scans en decisiones de exposición.

### Verificar exposición IPv4 e IPv6

```
nmap -6 -sV -Pn --top-ports 50 ipv6-host.example.test
```

Los servicios dual-stack pueden exponer puertos no vistos en revisiones solo IPv4.

### Enrutar puertos a validación de servicios

```
port class | examples | next note
remote admin | 22, 3389 | exposed-service-triage
dashboard | 3000, 5601, 9090 | service-validation
data | 5432, 6379, 9200 | internal/exposed-service review
```

El scan solo es útil una vez que los puertos se enrutan a decisiones.

## Ejemplos prácticos

- El scanning revela puertos SSH o de base de datos que no deberían ser públicos.
- Un host expone más servicios que sus pares.
- Un servicio público responde en un puerto no estándar y nunca fue documentado.
- Un origen directo expone HTTP fuera del CDN.
- Un dashboard de métricas responde en `9090`.

## Notas relacionadas

- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[service-validation|Validación de Servicios]]
- [[exposed-service-triage|Exposed Service Triage]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
