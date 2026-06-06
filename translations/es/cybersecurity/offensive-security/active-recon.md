# Active Recon

## Definición

El active recon es la recopilación de información que interactúa directamente con la infraestructura, servicios o aplicaciones del objetivo para validar o extender lo descubierto en el passive recon.

## Por qué importa

El passive recon encuentra posibilidades. El active recon las convierte en evidencia: qué hosts responden, qué puertos están abiertos, qué rutas existen, qué servicios se comportan como paneles de administración, y qué pistas son obsoletas.

El active recon debe estar autorizado y en scope. Operacionalmente viene después del [[passive-recon|Passive Recon]] y es más estrecho que el [[enumeration|Enumeration]] general.

## Cómo funciona

El active recon tiene **5 loops de validación**:

1. **Liveness del host.** ¿El host candidato resuelve y responde?
2. **Alcanzabilidad del servicio.** ¿Qué puertos, protocolos y virtual hosts responden?
3. **Comportamiento de la aplicación.** ¿Qué status codes, redirects, headers y contenido aparecen?
4. **Expansión de superficie.** ¿Qué rutas, parámetros, schemas y versiones son descubribles?
5. **Triage.** ¿El hallazgo merece testing más profundo, revisión de ownership o descarte?

El error en el active recon no es una sola request. Es el probing ruidoso y fuera de scope que no produce evidencia útil.

Un ejemplo trabajado, pista pasiva a validación activa:

```
Passive lead:
  preview-api.example.test appears in certificate transparency

Scope check:
  domain is target-owned and wildcard program scope includes *.example.test

Active check:
  DNS resolves, HTTPS returns 401 with "preview-api" header

Decision:
  live in-scope API candidate; move to service validation and API inventory testing
```

El active recon debería responder una pregunta de validación a la vez.

## Técnicas / patrones

Los operadores usan:

- HTTP probes de baja tasa y verificaciones de status codes
- resolución DNS y validación de virtual hosts
- port scanning dentro del scope autorizado
- probing de rutas y endpoints
- tech fingerprinting
- captura de screenshots o títulos de páginas para triage
- comparación contra el inventario de assets

## Variantes y bypasses

El active recon tiene **5 clases de actividad**.

### 1. HTTP probing

Verifica comportamiento web en vivo, redirects, headers, títulos y disponibilidad de rutas.

### 2. Port discovery

Encuentra servicios alcanzables y puertos no estándar.

### 3. Virtual-host probing

Prueba si los hosts y orígenes enrutan diferente según el `Host`.

### 4. Endpoint probing

Verifica rutas conocidas o adivinadas, métodos, schemas y parámetros.

### 5. Controlled fingerprinting

Infiere el stack y el rol del servicio sin intentos de exploit.

## Impacto

Ordenado aproximadamente por severidad:

- **Confirmación de exposición en vivo.** Separa assets reales del ruido pasivo.
- **Descubrimiento de servicios inesperados.** Revela servicios de admin, debug, legacy o de acceso remoto.
- **Descubrimiento de rutas.** Alimenta el testing de APIs y web.
- **Corrección de inventario.** Muestra a los defensores qué pueden validar los de afuera.
- **Priorización de testing.** Evita gastar esfuerzo manual en assets muertos.

## Detección y defensa

Ordenado por efectividad:

1. **Definí scope autorizado y rate limits.**
   El active recon debería ser seguro, repetible y acotado.

2. **Hacé active recon interno antes de que lo hagan los de afuera.**
   El scanning defensivo valida la exposición y el inventario.

3. **Monitoreá patrones de probing.**
   Los 404 repetidos, probes de rutas admin, probes de Host header y port sweeps son señales útiles.

4. **Hacé que los hallazgos inesperados sean accionables.**
   Los assets en vivo desconocidos deberían convertirse en preguntas de ownership, exposición y retiro.

5. **Evitá controles frágiles de oscuridad.**
   El active recon encuentra rápidamente rutas ocultas y puertos inusuales.

### Qué no funciona como defensa primaria

- **Bloquear solo la firma de un scanner.** El recon puede hacerse con clientes HTTP comunes.
- **Esconder servicios en puertos altos.** Los scans activos encuentran puertos alcanzables.
- **Tratar todos los probes como ataques.** Los equipos defensivos también necesitan recon seguro.
- **Ignorar probes de bajo volumen.** El recon hábil suele ser bajo y dirigido.

## Labs prácticos

Usá objetivos propios.

### Verificar candidatos web en vivo

```
while read host; do
  curl -m 3 -ks -o /dev/null -w "%{http_code} %{url_effective}\\n" "https://$host"
done < hosts.txt
```

Separar assets en vivo, redirigidos, denegados y muertos.

### Scanear puertos en scope

```
nmap -sV -Pn --top-ports 100 target.example.test
```

Usar objetivos autorizados y rate limits apropiados.

### Probar el routing de virtual hosts

```
curl -i -H 'Host: admin.example.test' https://203.0.113.10/
```

Solo testear IPs y hostnames propios.

### Registrar tasa y scope del active recon

```
Target list:
Allowed ports/routes:
Max rate:
Start/stop time:
User agent:
Contact/escalation:
```

El active recon seguro está operacionalmente acotado antes de ejecutarse.

### Comparar estado pasivo y activo

```
host | passive source | DNS | HTTPS | status | next action
```

Esto muestra qué pistas públicas se convirtieron en assets en vivo y cuáles eran obsoletas.

### Capturar artefactos reproducibles del probe

```
command | timestamp | target | response summary | saved artifact
```

La evidencia de active recon debería ser repetible sin volver a ejecutar probes ruidosos.

## Ejemplos prácticos

- Un subdominio adivinado se confirma como activo.
- El host discovery encuentra un servicio no registrado en el inventario.
- El probing revela virtual hosts alternativos o rutas legacy.
- Una ruta devuelve `403` en lugar de `404`, sugiriendo una superficie real protegida.
- Un dashboard en un puerto alto responde con un login de vendor.

## Notas relacionadas

- [[recon|Recon]]
- [[passive-recon|Passive Recon]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[service-validation|Validación de Servicios]]
- [[nmap-scanning|Nmap Scanning]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 105 — https://projectdiscovery.io/blog/reconnaissance-series-5-additional-active-reconnaissance
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
